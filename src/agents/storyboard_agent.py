"""
StoryboardAgent — scene breakdown and shot list generation.
Takes story beats and produces a detailed shot-by-shot plan.
"""
import json
from typing import Dict, Any, List

from src.agents.base_agent import BaseAgent
from src.config import MODEL_FLASH_TEXT

STORYBOARD_SYSTEM_PROMPT = """You are a professional anime storyboard artist.
Given a story analysis (beats, characters, setting), produce a JSON storyboard.

Return a JSON object:
{
  "scenes": [
    {
      "scene_id": 1,
      "beat_id": 1,
      "location": "Where this scene takes place",
      "time_of_day": "dawn/day/dusk/night",
      "shots": [
        {
          "shot_id": 1,
          "shot_type": "wide/medium/close-up/extreme-close-up/over-shoulder",
          "camera_movement": "static/pan-left/pan-right/tilt-up/tilt-down/zoom-in/zoom-out/tracking",
          "duration_seconds": 3,
          "characters_present": ["Character Name"],
          "action": "What happens in this shot",
          "expression": "Character emotional state",
          "dialogue": "Any spoken dialogue or null",
          "narration": "Any voiceover narration or null",
          "visual_notes": "Lighting, atmosphere, special effects"
        }
      ]
    }
  ],
  "total_estimated_duration_seconds": 120
}

Return ONLY valid JSON. Create 2-4 shots per scene. Be cinematic and detailed."""


class StoryboardAgent(BaseAgent):
    """
    Agent 2: Scene breakdown and shot planning.
    Input:  story analysis dict (from StoryAgent)
    Output: detailed shot list with camera, action, dialogue per shot
    """

    def __init__(self, **kwargs):
        super().__init__(name="StoryboardAgent", **kwargs)

    def run(self, story_analysis: Dict[str, Any]) -> Dict[str, Any]:
        self.log("Generating storyboard from story beats...")

        prompt = (
            "Create a detailed anime storyboard from this story analysis:\n\n"
            f"{json.dumps(story_analysis, indent=2)}"
        )

        result = self.genai.generate_json(
            prompt=prompt,
            model=MODEL_FLASH_TEXT,
            system_instruction=STORYBOARD_SYSTEM_PROMPT,
        )

        total_shots = sum(len(s.get("shots", [])) for s in result.get("scenes", []))
        self.log(f"Storyboard complete — {len(result.get('scenes', []))} scenes, {total_shots} shots")
        return result
