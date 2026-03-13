"""
Token optimization — prompt compression, model routing, and usage monitoring.

Strategies:
1. Prompt compression: strip redundant whitespace, truncate long inputs
2. Smart model routing: use cheapest model capable of each task
3. Token budget: track usage per run, warn on overspend
4. Response capping: set max_output_tokens per stage
"""
import re
import json
import time
from typing import Optional
from dataclasses import dataclass, field
from src.config import MODEL_FLASH_TEXT, MODEL_FLASH_IMAGE, MODEL_PRO_IMAGE


# ── Token estimation (rough: 1 token ≈ 4 chars for English) ──
def estimate_tokens(text: str) -> int:
    return max(1, len(text) // 4)


# ── Prompt compression ──
def compress_prompt(prompt: str, max_tokens: int = 4000) -> str:
    """
    Compress prompt to reduce token usage:
    1. Collapse multiple whitespace/newlines
    2. Remove markdown formatting noise
    3. Truncate to max_tokens if needed
    """
    # Collapse whitespace
    text = re.sub(r'\n{3,}', '\n\n', prompt)
    text = re.sub(r'[ \t]{2,}', ' ', text)
    text = re.sub(r'^\s+', '', text, flags=re.MULTILINE)

    # Remove verbose markdown
    text = re.sub(r'#{3,}\s*', '### ', text)
    text = re.sub(r'\*{2,}(.+?)\*{2,}', r'\1', text)  # Remove bold markers

    # Truncate if over budget
    est = estimate_tokens(text)
    if est > max_tokens:
        char_limit = max_tokens * 4
        text = text[:char_limit] + "\n[TRUNCATED]"

    return text.strip()


# ── Model routing ──
@dataclass
class ModelRoute:
    """Maps each pipeline stage to the cheapest capable model + token limits."""
    stage: str
    model: str
    max_input_tokens: int
    max_output_tokens: int
    needs_image: bool = False


# Route table: cheapest model per stage
MODEL_ROUTES = {
    "story":        ModelRoute("story",        MODEL_FLASH_TEXT,  2000,  1500, False),
    "character":    ModelRoute("character",    MODEL_FLASH_TEXT,  3000,  2000, False),
    "character_img":ModelRoute("character_img",MODEL_FLASH_IMAGE, 1000,  500,  True),
    "storyboard":   ModelRoute("storyboard",   MODEL_FLASH_TEXT,  3000,  2000, False),
    "keyframe":     ModelRoute("keyframe",     MODEL_FLASH_IMAGE, 800,   500,  True),
    "animation":    ModelRoute("animation",    MODEL_FLASH_TEXT,  2000,  1500, False),
    "audio":        ModelRoute("audio",        MODEL_FLASH_TEXT,  2000,  1500, False),
    "scene":        ModelRoute("scene",        MODEL_FLASH_TEXT,  3000,  2000, False),
    "rl_eval":      ModelRoute("rl_eval",      MODEL_FLASH_TEXT,  1500,  800,  False),
}


def get_route(stage: str) -> ModelRoute:
    return MODEL_ROUTES.get(stage, ModelRoute(stage, MODEL_FLASH_TEXT, 3000, 2000, False))


# ── Token budget tracker ──
@dataclass
class TokenBudget:
    """Track token usage per pipeline run and warn on overspend."""
    max_input_tokens: int = 30000    # Total budget per run
    max_output_tokens: int = 20000
    max_cost_usd: float = 0.50       # Hard cost cap per run

    # Running totals
    input_tokens_used: int = 0
    output_tokens_used: int = 0
    image_count: int = 0
    api_calls: int = 0
    stages: list = field(default_factory=list)
    start_time: float = field(default_factory=time.time)

    def record(self, stage: str, input_text: str, output_text: str = "", is_image: bool = False):
        """Record token usage for a stage."""
        input_est = estimate_tokens(input_text)
        output_est = estimate_tokens(output_text) if output_text else 0

        self.input_tokens_used += input_est
        self.output_tokens_used += output_est
        self.api_calls += 1
        if is_image:
            self.image_count += 1

        self.stages.append({
            "stage": stage,
            "input_tokens": input_est,
            "output_tokens": output_est,
            "is_image": is_image,
            "ts": time.time(),
        })

    @property
    def estimated_cost(self) -> float:
        """Estimate cost in USD based on Gemini pricing."""
        text_input_cost = (self.input_tokens_used / 1_000_000) * 0.10
        text_output_cost = (self.output_tokens_used / 1_000_000) * 0.40
        image_cost = self.image_count * 0.0315
        return text_input_cost + text_output_cost + image_cost

    @property
    def is_over_budget(self) -> bool:
        return (
            self.input_tokens_used > self.max_input_tokens
            or self.output_tokens_used > self.max_output_tokens
            or self.estimated_cost > self.max_cost_usd
        )

    @property
    def budget_remaining_pct(self) -> float:
        input_pct = 1 - (self.input_tokens_used / self.max_input_tokens)
        output_pct = 1 - (self.output_tokens_used / self.max_output_tokens)
        cost_pct = 1 - (self.estimated_cost / self.max_cost_usd)
        return max(0, min(input_pct, output_pct, cost_pct)) * 100

    def get_report(self) -> dict:
        return {
            "input_tokens": self.input_tokens_used,
            "output_tokens": self.output_tokens_used,
            "image_count": self.image_count,
            "api_calls": self.api_calls,
            "estimated_cost_usd": f"${self.estimated_cost:.4f}",
            "budget_remaining": f"{self.budget_remaining_pct:.0f}%",
            "over_budget": self.is_over_budget,
            "duration_s": f"{time.time() - self.start_time:.1f}",
            "per_stage": self.stages,
        }

    def check_and_warn(self, stage: str) -> Optional[str]:
        """Return warning string if approaching budget, None if OK."""
        if self.estimated_cost > self.max_cost_usd:
            return f"⚠️ COST LIMIT: ${self.estimated_cost:.4f} > ${self.max_cost_usd} cap — skipping {stage}"
        if self.input_tokens_used > self.max_input_tokens * 0.9:
            return f"⚠️ INPUT TOKEN BUDGET 90%+ used ({self.input_tokens_used}/{self.max_input_tokens})"
        return None
