"""
GenAI client with NO-LOOP retry policy, token optimization, and monitoring.

NO-LOOP POLICY:
- Max 2 retries (not 3) — fail fast, don't burn quota
- Daily quota exhausted → STOP IMMEDIATELY, try fallback model if available
- Transient 429 (rate limit) → retry with RetryInfo delay or exponential backoff
- Circuit breaker: 3 consecutive failures → 60s cooldown

MONITORING:
- Tracks every API call: model, tokens, latency, success/failure
"""
import json
import re
import time
from typing import List, Optional, Union
from PIL import Image
from google import genai
from google.genai import types

from src.config import (
    GOOGLE_API_KEY,
    MODEL_FLASH_IMAGE,
    MODEL_PRO_IMAGE,
    MODEL_FLASH_TEXT,
    MODEL_FLASH_TEXT_FALLBACKS,
    DEFAULT_ASPECT_RATIO,
    DEFAULT_IMAGE_SIZE,
)
from src.utils.token_optimizer import (
    compress_prompt,
    estimate_tokens,
    get_route,
    TokenBudget,
)

MAX_RETRIES = 2                    # Max retries per model
BACKOFF_BASE = 3                   # Exponential backoff: 3s, 9s
CIRCUIT_BREAKER_THRESHOLD = 3      # 3 failures → cooldown
CIRCUIT_BREAKER_COOLDOWN = 60
MAX_RETRY_DELAY = 120              # Cap wait at 2 min


class APIMonitor:
    """Track every API call for monitoring dashboard."""

    def __init__(self):
        self.calls = []
        self.total_input_tokens = 0
        self.total_output_tokens = 0
        self.total_latency = 0
        self.successes = 0
        self.failures = 0
        self.retries = 0
        self.quota_stops = 0

    def record(self, model: str, stage: str, input_tokens: int,
               output_tokens: int, latency: float, success: bool, error: str = None):
        self.calls.append({
            "model": model, "stage": stage,
            "input_tokens": input_tokens, "output_tokens": output_tokens,
            "latency_ms": round(latency * 1000),
            "success": success, "error": error,
            "ts": time.time(),
        })
        self.total_input_tokens += input_tokens
        self.total_output_tokens += output_tokens
        self.total_latency += latency
        if success:
            self.successes += 1
        else:
            self.failures += 1

    def get_report(self) -> dict:
        total = self.successes + self.failures
        return {
            "total_calls": total,
            "successes": self.successes,
            "failures": self.failures,
            "retries": self.retries,
            "quota_stops": self.quota_stops,
            "success_rate": f"{(self.successes / max(1, total)) * 100:.1f}%",
            "total_input_tokens": self.total_input_tokens,
            "total_output_tokens": self.total_output_tokens,
            "avg_latency_ms": round(self.total_latency / max(1, total) * 1000),
            "estimated_cost_usd": f"${self._estimate_cost():.4f}",
            "recent_calls": self.calls[-10:],  # Last 10
        }

    def _estimate_cost(self) -> float:
        text_in = (self.total_input_tokens / 1_000_000) * 0.10
        text_out = (self.total_output_tokens / 1_000_000) * 0.40
        imgs = sum(1 for c in self.calls if "image" in c.get("model", "").lower())
        return text_in + text_out + (imgs * 0.0315)


class GenAIClient:
    """Wrapper with no-loop retry, token optimization, and monitoring."""

    def __init__(self, api_key: Optional[str] = None):
        key = api_key or GOOGLE_API_KEY
        if not key:
            raise ValueError("GOOGLE_API_KEY is required.")
        self.client = genai.Client(api_key=key)

        # Circuit breaker
        self._consecutive_failures = 0
        self._circuit_open_until = 0

        # Monitoring
        self.monitor = APIMonitor()
        self.token_budget = TokenBudget()

    def _is_quota_exhausted(self, error_str: str) -> bool:
        """Detect daily/per-project quota exhaustion — do not retry same model."""
        s = error_str.lower().replace("_", "").replace("-", "")
        return (
            "limit: 0" in error_str
            or "quotaperday" in s
            or ("quota exceeded" in s and ("free" in s or "freetier" in s or "limit:" in error_str))
            or "resource_exhausted" in s
        )

    def _parse_retry_delay(self, error_str: str) -> Optional[float]:
        """Extract 'Please retry in X.Ys' or RetryInfo delay from 429 error."""
        m = re.search(r"retry in (\d+(?:\.\d+)?)\s*s", error_str, re.I)
        if m:
            return min(float(m.group(1)), MAX_RETRY_DELAY)
        return None

    def _check_circuit(self):
        if self._consecutive_failures >= CIRCUIT_BREAKER_THRESHOLD:
            if time.time() < self._circuit_open_until:
                wait = int(self._circuit_open_until - time.time())
                print(f"[GenAI] ⛔ Circuit breaker OPEN — {wait}s remaining")
                raise RuntimeError(f"Circuit breaker open — waiting {wait}s. No API calls allowed.")
            self._consecutive_failures = 0
            print("[GenAI] Circuit breaker RESET")

    def _record_success(self):
        self._consecutive_failures = 0

    def _record_failure(self, error_str: str):
        self._consecutive_failures += 1
        if self._consecutive_failures >= CIRCUIT_BREAKER_THRESHOLD:
            self._circuit_open_until = time.time() + CIRCUIT_BREAKER_COOLDOWN
            print(f"[GenAI] ⛔ Circuit breaker TRIPPED — {CIRCUIT_BREAKER_COOLDOWN}s cooldown")

    def _format_quota_error(self, error_str: str, model: str) -> str:
        """Build a clear, actionable message for quota errors."""
        if "429" in error_str or "resource exhausted" in error_str.lower():
            return (
                f"Gemini API quota exceeded for {model}. "
                "Free tier: 20 requests/day per model. "
                "Options: (1) Wait for daily reset, (2) Enable billing at https://aistudio.google.com/apikey, "
                "(3) Use a different API key. See https://ai.google.dev/gemini-api/docs/rate-limits"
            )
        return error_str

    def _retry_call(self, func, stage: str = "unknown", model: str = "unknown"):
        """Retry with backoff. On daily quota exhaustion, raise clear error (caller may try fallback)."""
        self._check_circuit()

        warning = self.token_budget.check_and_warn(stage)
        if warning and self.token_budget.is_over_budget:
            print(f"[GenAI] {warning}")
            raise RuntimeError(warning)

        for attempt in range(MAX_RETRIES + 1):
            start = time.time()
            try:
                result = func()
                latency = time.time() - start
                self.monitor.record(model, stage, 0, 0, latency, True)
                self._record_success()
                return result

            except Exception as e:
                latency = time.time() - start
                error_str = str(e)
                err_lower = error_str.lower()

                if self._is_quota_exhausted(error_str):
                    self.monitor.quota_stops += 1
                    self.monitor.record(model, stage, 0, 0, latency, False, "QUOTA_EXHAUSTED")
                    self._record_failure(error_str)
                    msg = self._format_quota_error(error_str, model)
                    print(f"[GenAI] 🛑 Quota exceeded for {model}")
                    raise RuntimeError(msg) from e

                is_retryable = any(x in err_lower for x in [
                    "429", "resource exhausted", "rate limit",
                    "500", "503", "internal", "unavailable",
                ])

                if is_retryable and attempt < MAX_RETRIES:
                    delay = self._parse_retry_delay(error_str) or (BACKOFF_BASE ** (attempt + 1))
                    delay = min(delay, MAX_RETRY_DELAY)
                    self.monitor.retries += 1
                    print(f"[GenAI] ⏳ Retry {attempt + 1}/{MAX_RETRIES} in {delay:.0f}s — {type(e).__name__} (model: {model})")
                    self.monitor.record(model, stage, 0, 0, latency, False, f"retry_{attempt + 1}")
                    self._record_failure(error_str)
                    time.sleep(delay)
                else:
                    self.monitor.record(model, stage, 0, 0, latency, False, error_str[:200])
                    self._record_failure(error_str)
                    raise

    # ── Text generation (with compression + fallback models) ───
    def generate_text(
        self, prompt: str, model: str = MODEL_FLASH_TEXT,
        system_instruction: Optional[str] = None, stage: str = "text",
    ) -> str:
        route = get_route(stage)
        compressed = compress_prompt(prompt, route.max_input_tokens)
        primary = route.model if model == MODEL_FLASH_TEXT else model
        models_to_try = [primary] + [m for m in MODEL_FLASH_TEXT_FALLBACKS if m != primary]

        config = types.GenerateContentConfig(response_modalities=["Text"])
        if system_instruction:
            config.system_instruction = compress_prompt(system_instruction, 1000)

        last_error = None
        for actual_model in models_to_try:
            def _call(use_model=actual_model):
                response = self.client.models.generate_content(
                    model=use_model, contents=[compressed], config=config,
                )
                text = response.text or ""
                self.token_budget.record(stage, compressed, text, False)
                return text

            try:
                return self._retry_call(_call, stage, actual_model)
            except RuntimeError as e:
                last_error = e
                if "quota" in str(e).lower() and actual_model != models_to_try[-1]:
                    print(f"[GenAI] ⚡ Trying fallback model: {models_to_try[models_to_try.index(actual_model) + 1]}")
                else:
                    raise

        raise last_error or RuntimeError("No model succeeded")

    def generate_json(
        self, prompt: str, model: str = MODEL_FLASH_TEXT,
        system_instruction: Optional[str] = None, stage: str = "json",
    ) -> dict:
        raw = self.generate_text(prompt, model, system_instruction, stage)
        cleaned = raw.strip()
        if cleaned.startswith("```"):
            lines = cleaned.split("\n")
            lines = lines[1:]
            if lines and lines[-1].strip() == "```":
                lines = lines[:-1]
            cleaned = "\n".join(lines)
        try:
            return json.loads(cleaned)
        except json.JSONDecodeError:
            start = cleaned.find("{")
            end = cleaned.rfind("}") + 1
            if start >= 0 and end > start:
                try:
                    return json.loads(cleaned[start:end])
                except json.JSONDecodeError:
                    pass
            return {}

    # ── Image generation ──────────────────────────────────────
    def generate_image(
        self, prompt: str, model: str = MODEL_FLASH_IMAGE,
        aspect_ratio: str = DEFAULT_ASPECT_RATIO,
        image_size: str = DEFAULT_IMAGE_SIZE, stage: str = "keyframe",
    ) -> Optional[Image.Image]:
        compressed = compress_prompt(prompt, 800)

        def _call():
            response = self.client.models.generate_content(
                model=model, contents=[compressed],
                config=types.GenerateContentConfig(
                    response_modalities=["Image"],
                    image_config=types.ImageConfig(
                        aspect_ratio=aspect_ratio,
                    ),
                ),
            )
            for part in response.parts:
                if part.inline_data is not None:
                    self.token_budget.record(stage, compressed, "", True)
                    return part.as_image()
            return None

        try:
            return self._retry_call(_call, stage, model)
        except Exception as e:
            print(f"[GenAI] Image gen skipped (fallback): {type(e).__name__} - {str(e)}")
            return None

    # ── Image editing ─────────────────────────────────────────
    def edit_image(
        self, prompt: str, reference_images: List[Image.Image],
        model: str = MODEL_FLASH_IMAGE,
        aspect_ratio: str = DEFAULT_ASPECT_RATIO,
        image_size: str = DEFAULT_IMAGE_SIZE,
    ) -> Optional[Image.Image]:
        compressed = compress_prompt(prompt, 800)

        def _call():
            contents = [compressed] + reference_images
            response = self.client.models.generate_content(
                model=model, contents=contents,
                config=types.GenerateContentConfig(
                    response_modalities=["Image"],
                    image_config=types.ImageConfig(
                        aspect_ratio=aspect_ratio,
                    ),
                ),
            )
            for part in response.parts:
                if part.inline_data is not None:
                    return part.as_image()
            return None

        try:
            return self._retry_call(_call, "edit_image", model)
        except Exception:
            return None

    # ── Interleaved output ────────────────────────────────────
    def generate_interleaved(
        self, prompt: str, model: str = MODEL_FLASH_IMAGE,
        aspect_ratio: str = DEFAULT_ASPECT_RATIO,
        image_size: str = DEFAULT_IMAGE_SIZE,
    ) -> List[Union[str, Image.Image]]:
        compressed = compress_prompt(prompt, 2000)

        def _call():
            response = self.client.models.generate_content(
                model=model, contents=[compressed],
                config=types.GenerateContentConfig(
                    response_modalities=["Text", "Image"],
                    image_config=types.ImageConfig(
                        aspect_ratio=aspect_ratio,
                    ),
                ),
            )
            results = []
            for part in response.parts:
                if part.text is not None:
                    results.append(part.text)
                elif part.inline_data is not None:
                    results.append(part.as_image())
            return results

        try:
            return self._retry_call(_call, "interleaved", model)
        except Exception as e:
            return [f"[Generation failed: {type(e).__name__}]"]
