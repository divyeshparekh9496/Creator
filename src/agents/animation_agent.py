"""
AnimationAgent — motion planning and frame sequencing.
Takes keyframes and plans transitions, timing, and intermediate frames.
"""
import os
import json
from typing import Dict, Any, List

from src.agents.base_agent import BaseAgent
from src.config import MODEL_FLASH_TEXT


ANIMATION_SYSTEM_PROMPT = """You are a professional anime animation director.
Given a list of keyframes with their scene/shot metadata, plan the animation sequence.

Return a JSON object:
{
  "parts": [
    {
      "part_id": 1,
      "part_title": "Act 1 - Introduction",
      "sequences": [
        {
          "keyframe_index": 0,
          "scene_id": 1,
          "shot_id": 1,
          "duration_seconds": 3,
          "transition_in": "fade-in/cut/dissolve/wipe",
          "transition_out": "cut/dissolve/fade-out",
          "motion_notes": "Slow pan across the landscape, camera settles on character",
          "timing": "slow/normal/fast",
          "effects": ["particle_dust", "lens_flare"]
        }
      ]
    }
  ],
  "total_duration_seconds": 120,
  "fps": 24
}

Group sequences into 2-3 parts (acts). Return ONLY valid JSON."""


class AnimationAgent(BaseAgent):
    """
    Agent 5: Motion, timing, and transition planning.
    Input:  keyframes data + storyboard
    Output: animation sequence plan with parts, transitions, timing
    """

    def __init__(self, output_dir: str = "data/output/animation", **kwargs):
        super().__init__(name="AnimationAgent", **kwargs)
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

    def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        keyframes = input_data.get("keyframes", {})
        storyboard = input_data.get("storyboard", {})

        self.log("Planning animation sequences and transitions...")

        prompt = (
            "Plan the animation sequence for this anime. "
            "Here are the keyframes and storyboard:\n\n"
            f"Keyframes: {json.dumps(keyframes.get('keyframes', []), indent=2)}\n\n"
            f"Storyboard: {json.dumps(storyboard, indent=2)}"
        )

        result = self.genai.generate_json(
            prompt=prompt,
            model=MODEL_FLASH_TEXT,
            system_instruction=ANIMATION_SYSTEM_PROMPT,
        )

        # Save animation plan
        plan_path = os.path.join(self.output_dir, "animation_plan.json")
        with open(plan_path, "w") as f:
            json.dump(result, f, indent=2)
        self.log(f"Animation plan saved to {plan_path}")

        num_parts = len(result.get("parts", []))
        self.log(f"Animation planning complete — {num_parts} parts")
        return result
