"""
RL Reward System — composite scoring for Creator quality assessment.

Reward = 0.3*Coherence + 0.25*Creativity + 0.2*Consistency + 0.15*EmotionalImpact + 0.1*TechnicalQuality

Inspired by:
- SAGE RL framework (arXiv:2512.17102)
- AWS DeepRacer composite reward
- RLHF patterns (SuperAnnotate)
"""
import json
import os
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field, asdict

from src.agents.base_agent import BaseAgent
from src.config import MODEL_FLASH_TEXT


# ── Reward weights ──
REWARD_WEIGHTS = {
    "coherence": 0.30,
    "creativity": 0.25,
    "consistency": 0.20,
    "emotional_impact": 0.15,
    "technical_quality": 0.10,
}

REWARD_EVAL_PROMPT = """You are a quality evaluator for anime production.
Given the scene data, rate each dimension 0.0-1.0.

Dimensions:
- coherence: Does the narrative flow naturally? (0=disjointed, 1=Pixar-level)
- creativity: Novel effects, arcs, visual choices? (0=cliché, 1=innovative)
- consistency: Do visuals/audio match character sheets? (AnimeGANv2/Animate Anyone score)
- emotional_impact: Does the character arc evoke feeling? (timid→warrior payoff)
- technical_quality: Richness — particles, SFX layers, motion smoothness?

Return ONLY valid JSON:
{
  "coherence": 0.85,
  "creativity": 0.70,
  "consistency": 0.90,
  "emotional_impact": 0.75,
  "technical_quality": 0.80,
  "reasoning": {
    "coherence": "Strong narrative flow between beats",
    "creativity": "Good arc but effects are standard",
    "consistency": "Character visuals match sheets well",
    "emotional_impact": "Arc payoff feels earned",
    "technical_quality": "Good particle use, motion smooth"
  }
}"""


@dataclass
class RewardScore:
    """Composite reward score for a scene or episode."""
    coherence: float = 0.0
    creativity: float = 0.0
    consistency: float = 0.0
    emotional_impact: float = 0.0
    technical_quality: float = 0.0
    user_bonus: float = 0.0  # +1 for thumbs up, -0.5 for critique
    reasoning: Dict[str, str] = field(default_factory=dict)

    @property
    def total(self) -> float:
        base = (
            REWARD_WEIGHTS["coherence"] * self.coherence
            + REWARD_WEIGHTS["creativity"] * self.creativity
            + REWARD_WEIGHTS["consistency"] * self.consistency
            + REWARD_WEIGHTS["emotional_impact"] * self.emotional_impact
            + REWARD_WEIGHTS["technical_quality"] * self.technical_quality
        )
        return min(1.0, max(0.0, base + self.user_bonus * 0.1))

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["total"] = self.total
        return d


@dataclass
class RLAction:
    """An RL action = a parameter tweak for generation."""
    action_type: str          # e.g., "increase_drama", "add_particles"
    parameter: str            # What is tweaked
    magnitude: float          # How much (+/- %)
    target_agent: str         # Which sub-agent this applies to
    reasoning: str = ""       # Why this action was chosen

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class RLEpisode:
    """One episode = one project/story run through the pipeline."""
    episode_id: int
    policy_version: str
    states: List[Dict] = field(default_factory=list)
    actions: List[Dict] = field(default_factory=list)
    rewards: List[Dict] = field(default_factory=list)
    total_reward: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class RewardEvaluator(BaseAgent):
    """
    Computes composite rewards for scenes and episodes.
    Uses Gemini for auto-evaluation + accepts user feedback.
    """

    def __init__(self, **kwargs):
        super().__init__(name="RewardEvaluator", **kwargs)

    def evaluate_scene(self, scene_data: Dict[str, Any]) -> RewardScore:
        """Auto-evaluate a scene using Gemini."""
        self.log(f"  Evaluating scene {scene_data.get('scene_id', '?')}...")

        prompt = (
            "Evaluate this anime scene on all quality dimensions:\n\n"
            f"{json.dumps(scene_data, indent=2, default=str)}"
        )

        try:
            result = self.genai.generate_json(
                prompt=prompt,
                model=MODEL_FLASH_TEXT,
                system_instruction=REWARD_EVAL_PROMPT,
            )
            return RewardScore(
                coherence=float(result.get("coherence", 0.5)),
                creativity=float(result.get("creativity", 0.5)),
                consistency=float(result.get("consistency", 0.5)),
                emotional_impact=float(result.get("emotional_impact", 0.5)),
                technical_quality=float(result.get("technical_quality", 0.5)),
                reasoning=result.get("reasoning", {}),
            )
        except Exception as e:
            self.log(f"  Eval error: {e}")
            return RewardScore(coherence=0.5, creativity=0.5, consistency=0.5,
                             emotional_impact=0.5, technical_quality=0.5)

    def apply_user_feedback(self, score: RewardScore, rating: int) -> RewardScore:
        """Apply user rating (1-5) as RLHF bonus/penalty."""
        if rating >= 4:
            score.user_bonus = 1.0
        elif rating == 3:
            score.user_bonus = 0.0
        else:
            score.user_bonus = -0.5
        return score

    def run(self, input_data: Any) -> Dict[str, Any]:
        """Evaluate all scenes in a rendering."""
        scenes = input_data.get("scenes", [])
        scores = []
        for scene in scenes:
            score = self.evaluate_scene(scene)
            scores.append(score.to_dict())
        avg_total = sum(s["total"] for s in scores) / max(len(scores), 1)
        return {"scene_scores": scores, "episode_avg_reward": avg_total}
