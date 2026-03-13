"""
StoryboardAgent — enhanced scene breakdown with character arc integration.
Produces arc-driven scenes with effects and motion hints per shot.
"""
import json
from typing import Dict, Any

from src.agents.base_agent import BaseAgent
from src.config import MODEL_FLASH_TEXT

STORYBOARD_SYSTEM_PROMPT = """You are a professional anime storyboard artist and creative director.
Given a story analysis WITH character arc data, produce an arc-driven storyboard.

Each scene must reflect character arcs (e.g., "Scene 1: Doubt → Scene 5: Triumph").
Each shot must include effects and motion hints for the animation pipeline.

Return a JSON object:
{
  "scenes": [
    {
      "scene_id": 1,
      "beat_id": 1,
      "title": "Scene title reflecting arc beat",
      "location": "Where this scene takes place",
      "time_of_day": "dawn/day/dusk/night",
      "arc_context": "What character development happens here",
      "shots": [
        {
          "shot_id": 1,
          "shot_type": "wide/medium/close-up/extreme-close-up/over-shoulder",
          "camera_movement": "static/pan-left/pan-right/tilt-up/zoom-in/tracking/whip-pan",
          "duration_seconds": 3,
          "characters_present": ["Character Name"],
          "action": "What happens in this shot",
          "expression": "Character emotional state for this moment",
          "dialogue": "Spoken words or null",
          "narration": "Voiceover narration or null",
          "visual_notes": "Lighting, atmosphere, special visual details",
          "effects": ["particle_rain", "inner_glow", "speed_lines", "cherry_blossoms"],
          "animate_anyone_hint": "smooth head-turn / breathing / hair-flow"
        }
      ]
    }
  ],
  "total_estimated_duration_seconds": 120
}

Return ONLY valid JSON. Create 2-4 shots per scene. Be cinematic.
Include at least one effect per shot. Use Animate Anyone motion hints."""


class StoryboardAgent(BaseAgent):
    """
    Enhanced Agent 2: Arc-driven scene breakdown with effects and motion hints.
    """

    def __init__(self, **kwargs):
        super().__init__(name="StoryboardAgent", **kwargs)

    def run(self, story_analysis: Dict[str, Any]) -> Dict[str, Any]:
        self.log("Generating arc-driven storyboard with effects and motion hints...")

        prompt = (
            "Create an arc-driven anime storyboard with effects and "
            "Animate Anyone motion hints for each shot:\n\n"
            f"{json.dumps(story_analysis, indent=2)}"
        )

        result = self.genai.generate_json(
            prompt=prompt,
            model=MODEL_FLASH_TEXT,
            system_instruction=STORYBOARD_SYSTEM_PROMPT,
        )

        total_shots = sum(len(s.get("shots", [])) for s in result.get("scenes", []))
        self.log(f"Storyboard complete — {len(result.get('scenes', []))} scenes, {total_shots} shots (with effects)")
        return result
