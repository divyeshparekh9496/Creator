"""
AnimationAgent — enhanced motion planning with Animate Anyone patterns,
particle systems, and rich effects metadata.

Open-source inspirations:
- Animate Anyone (humanaigc): Pose guider for smooth character transitions
- ReferenceNet: Appearance consistency across frames
"""
import os
import json
from typing import Dict, Any, List

from src.agents.base_agent import BaseAgent
from src.config import MODEL_FLASH_TEXT


ANIMATION_SYSTEM_PROMPT = """You are a professional anime animation director with expertise in
Animate Anyone-style pose-guided animation and particle effects.

Given keyframes and storyboard, create a rich animation plan with motion, effects, and transitions.

Return JSON:
{
  "parts": [
    {
      "part_id": 1,
      "part_title": "Act 1 - Title",
      "sequences": [
        {
          "keyframe_index": 0,
          "scene_id": 1,
          "shot_id": 1,
          "duration_seconds": 3,
          "transition_in": "fade-in/cut/dissolve/wipe/zoom-blur",
          "transition_out": "cut/dissolve/fade-out/whip-pan",
          "motion": {
            "type": "Animate Anyone smooth",
            "camera": "slow pan-right",
            "character_motion": "subtle breathing + wind-blown hair",
            "interpolation_frames": 12
          },
          "effects": {
            "particles": ["cherry_blossoms", "dust_motes"],
            "lighting": "golden hour rim light with lens flare",
            "post_processing": ["film_grain", "bloom"],
            "special": "inner glow aura on character during power-up"
          },
          "timing": "slow",
          "sync_emotion": "wonder"
        }
      ]
    }
  ],
  "total_duration_seconds": 120,
  "fps": 24,
  "global_effects": {
    "color_grading": "warm amber tones, desaturated shadows",
    "film_style": "cinematic 2.39:1 letterbox"
  }
}

Return ONLY valid JSON. Be cinematic. Use Animate Anyone motion descriptions."""


class AnimationAgent(BaseAgent):
    """
    Enhanced Agent 5: Motion + effects planning with Animate Anyone patterns.

    Features:
    - Animate Anyone-style pose/motion descriptions
    - Rich particle system metadata per sequence
    - Lighting and post-processing effects
    - Emotion-synced timing
    - Global color grading and film style
    """

    def __init__(self, output_dir: str = "data/output/animation", **kwargs):
        super().__init__(name="AnimationAgent", **kwargs)
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

    def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        keyframes = input_data.get("keyframes", {})
        storyboard = input_data.get("storyboard", {})

        self.log("Planning animation with Animate Anyone motion + particle effects...")

        prompt = (
            "Plan rich animation sequences with Animate Anyone-style motion, "
            "particle effects, lighting, and post-processing. "
            "Here are the keyframes and storyboard:\n\n"
            f"Keyframes: {json.dumps(keyframes.get('keyframes', []), indent=2)}\n\n"
            f"Storyboard: {json.dumps(storyboard, indent=2)}"
        )

        result = self.genai.generate_json(
            prompt=prompt,
            model=MODEL_FLASH_TEXT,
            system_instruction=ANIMATION_SYSTEM_PROMPT,
        )

        plan_path = os.path.join(self.output_dir, "animation_plan.json")
        with open(plan_path, "w") as f:
            json.dump(result, f, indent=2)
        self.log(f"Animation plan saved: {plan_path}")

        num_parts = len(result.get("parts", []))
        total_seqs = sum(len(p.get("sequences", [])) for p in result.get("parts", []))
        self.log(f"Animation planning complete — {num_parts} parts, {total_seqs} sequences")
        return result
