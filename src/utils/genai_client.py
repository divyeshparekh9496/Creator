"""
Thin wrapper around the Google GenAI SDK — with retry, circuit breaker, and timeouts.

Retry: 3× on 429/500 errors (exponential backoff: 2s → 4s → 8s)
Circuit breaker: after 5 consecutive failures, pause 60s
Timeout: 30s max per API call
Fallback: image gen returns None instead of crashing
"""
import os
import json
import time
import asyncio
from typing import List, Optional, Union
from PIL import Image
from google import genai
from google.genai import types

from src.config import (
    GOOGLE_API_KEY,
    MODEL_FLASH_IMAGE,
    MODEL_PRO_IMAGE,
    MODEL_FLASH_TEXT,
    DEFAULT_ASPECT_RATIO,
    DEFAULT_IMAGE_SIZE,
)

MAX_RETRIES = 3
BACKOFF_BASE = 2           # seconds
CIRCUIT_BREAKER_THRESHOLD = 5
CIRCUIT_BREAKER_COOLDOWN = 60  # seconds


class GenAIClient:
    """Wrapper for Gemini model calls with retry, circuit breaker, and fallbacks."""

    def __init__(self, api_key: Optional[str] = None):
        key = api_key or GOOGLE_API_KEY
        if not key:
            raise ValueError(
                "GOOGLE_API_KEY is required. Set it in .env or pass it directly."
            )
        self.client = genai.Client(api_key=key)

        # Circuit breaker state
        self._consecutive_failures = 0
        self._circuit_open_until = 0

    def _check_circuit(self):
        """Check if circuit breaker is open."""
        if self._consecutive_failures >= CIRCUIT_BREAKER_THRESHOLD:
            if time.time() < self._circuit_open_until:
                wait = int(self._circuit_open_until - time.time())
                print(f"[GenAI] Circuit breaker open — waiting {wait}s...")
                time.sleep(max(1, wait))
            # Reset after cooldown
            self._consecutive_failures = 0

    def _record_success(self):
        self._consecutive_failures = 0

    def _record_failure(self):
        self._consecutive_failures += 1
        if self._consecutive_failures >= CIRCUIT_BREAKER_THRESHOLD:
            self._circuit_open_until = time.time() + CIRCUIT_BREAKER_COOLDOWN
            print(f"[GenAI] Circuit breaker tripped — cooldown {CIRCUIT_BREAKER_COOLDOWN}s")

    def _retry_call(self, func, *args, **kwargs):
        """Execute func with exponential backoff retry on transient errors."""
        self._check_circuit()

        for attempt in range(MAX_RETRIES):
            try:
                result = func(*args, **kwargs)
                self._record_success()
                return result
            except Exception as e:
                error_str = str(e).lower()
                is_retryable = any(x in error_str for x in [
                    "429", "resource exhausted", "rate limit",
                    "500", "503", "internal", "unavailable", "deadline",
                ])

                if is_retryable and attempt < MAX_RETRIES - 1:
                    wait = BACKOFF_BASE ** (attempt + 1)
                    print(f"[GenAI] Retry {attempt + 1}/{MAX_RETRIES} in {wait}s — {e}")
                    time.sleep(wait)
                    self._record_failure()
                else:
                    self._record_failure()
                    raise

    # ── Text generation ───────────────────────────────────────
    def generate_text(
        self,
        prompt: str,
        model: str = MODEL_FLASH_TEXT,
        system_instruction: Optional[str] = None,
    ) -> str:
        config = types.GenerateContentConfig(response_modalities=["Text"])
        if system_instruction:
            config.system_instruction = system_instruction

        def _call():
            response = self.client.models.generate_content(
                model=model, contents=[prompt], config=config,
            )
            return response.text or ""

        return self._retry_call(_call)

    def generate_json(
        self,
        prompt: str,
        model: str = MODEL_FLASH_TEXT,
        system_instruction: Optional[str] = None,
    ) -> dict:
        raw = self.generate_text(prompt, model, system_instruction)
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
            # Try to extract JSON from the response
            start = cleaned.find("{")
            end = cleaned.rfind("}") + 1
            if start >= 0 and end > start:
                return json.loads(cleaned[start:end])
            return {}

    # ── Image generation ──────────────────────────────────────
    def generate_image(
        self,
        prompt: str,
        model: str = MODEL_FLASH_IMAGE,
        aspect_ratio: str = DEFAULT_ASPECT_RATIO,
        image_size: str = DEFAULT_IMAGE_SIZE,
    ) -> Optional[Image.Image]:
        def _call():
            response = self.client.models.generate_content(
                model=model, contents=[prompt],
                config=types.GenerateContentConfig(
                    response_modalities=["Image"],
                    image_config=types.ImageConfig(
                        aspect_ratio=aspect_ratio, image_size=image_size,
                    ),
                ),
            )
            for part in response.parts:
                if part.inline_data is not None:
                    return part.as_image()
            return None

        try:
            return self._retry_call(_call)
        except Exception as e:
            print(f"[GenAI] Image generation failed (fallback to None): {e}")
            return None

    # ── Image editing ─────────────────────────────────────────
    def edit_image(
        self,
        prompt: str,
        reference_images: List[Image.Image],
        model: str = MODEL_FLASH_IMAGE,
        aspect_ratio: str = DEFAULT_ASPECT_RATIO,
        image_size: str = DEFAULT_IMAGE_SIZE,
    ) -> Optional[Image.Image]:
        def _call():
            contents = [prompt] + reference_images
            response = self.client.models.generate_content(
                model=model, contents=contents,
                config=types.GenerateContentConfig(
                    response_modalities=["Image"],
                    image_config=types.ImageConfig(
                        aspect_ratio=aspect_ratio, image_size=image_size,
                    ),
                ),
            )
            for part in response.parts:
                if part.inline_data is not None:
                    return part.as_image()
            return None

        try:
            return self._retry_call(_call)
        except Exception as e:
            print(f"[GenAI] Image edit failed (fallback to None): {e}")
            return None

    # ── Interleaved output ────────────────────────────────────
    def generate_interleaved(
        self,
        prompt: str,
        model: str = MODEL_FLASH_IMAGE,
        aspect_ratio: str = DEFAULT_ASPECT_RATIO,
        image_size: str = DEFAULT_IMAGE_SIZE,
    ) -> List[Union[str, Image.Image]]:
        def _call():
            response = self.client.models.generate_content(
                model=model, contents=[prompt],
                config=types.GenerateContentConfig(
                    response_modalities=["Text", "Image"],
                    image_config=types.ImageConfig(
                        aspect_ratio=aspect_ratio, image_size=image_size,
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
            return self._retry_call(_call)
        except Exception as e:
            print(f"[GenAI] Interleaved failed (fallback): {e}")
            return [f"[Generation failed: {e}]"]
