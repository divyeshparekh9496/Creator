"""
AudioAgent — voice, music, and SFX planning.
Generates audio track descriptions and hooks for TTS / music generation.
"""
import os
import json
from typing import Dict, Any, List

from src.agents.base_agent import BaseAgent
from src.config import MODEL_FLASH_TEXT


AUDIO_SYSTEM_PROMPT = """You are a professional anime sound director.
Given an animation plan with dialogue and narration, create an audio production plan.

Return a JSON object:
{
  "tracks": [
    {
      "part_id": 1,
      "audio_elements": [
        {
          "type": "dialogue/narration/music/sfx",
          "start_seconds": 0,
          "duration_seconds": 3,
          "content": "The actual text to speak, or description of music/sfx",
          "character": "Character name (for dialogue) or null",
          "voice_style": "calm/excited/whispered/heroic",
          "volume": 1.0
        }
      ],
      "background_music": {
        "genre": "orchestral/electronic/traditional-japanese",
        "mood": "epic/peaceful/tense",
        "tempo": "slow/medium/fast",
        "description": "Detailed description of the background music"
      }
    }
  ],
  "total_audio_duration_seconds": 120
}

Return ONLY valid JSON. Include BGM descriptions for each part."""


class AudioAgent(BaseAgent):
    """
    Agent 6: Audio track planning.
    Input:  animation plan + storyboard (for dialogue)
    Output: audio production plan with dialogue, music, SFX cues
    """

    def __init__(self, output_dir: str = "data/output/audio", **kwargs):
        super().__init__(name="AudioAgent", **kwargs)
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

    def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        animation_plan = input_data.get("animation_plan", {})
        storyboard = input_data.get("storyboard", {})

        self.log("Creating audio production plan...")

        prompt = (
            "Create an audio production plan for this anime:\n\n"
            f"Animation plan: {json.dumps(animation_plan, indent=2)}\n\n"
            f"Storyboard: {json.dumps(storyboard, indent=2)}"
        )

        result = self.genai.generate_json(
            prompt=prompt,
            model=MODEL_FLASH_TEXT,
            system_instruction=AUDIO_SYSTEM_PROMPT,
        )

        # Save audio plan
        plan_path = os.path.join(self.output_dir, "audio_plan.json")
        with open(plan_path, "w") as f:
            json.dump(result, f, indent=2)
        self.log(f"Audio plan saved to {plan_path}")

        num_tracks = len(result.get("tracks", []))
        self.log(f"Audio planning complete — {num_tracks} tracks")
        return result
