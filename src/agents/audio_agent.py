"""
AudioAgent — rich SFX, music, and voice planning with procedural descriptions.

Generates emotion-synced audio cues with layered sound design.

Open-source inspirations:
- Audacity/LMMS patterns for procedural audio description
- Freesound.org-style library references
"""
import os
import json
from typing import Dict, Any, List

from src.agents.base_agent import BaseAgent
from src.config import MODEL_FLASH_TEXT


AUDIO_SYSTEM_PROMPT = """You are a professional anime sound director and composer.
Create rich, emotion-synced audio plans with layered SFX, music, and voice.

Use procedural audio descriptions inspired by Audacity/LMMS patterns:
- Layer multiple elements: "low synth drone + heartbeat pulse + distant thunder"
- Describe processing: "reverb on footsteps, compression on impacts"
- Sync to emotion: "swell during triumph, thin out during isolation"

Return JSON:
{
  "tracks": [
    {
      "part_id": 1,
      "part_title": "Act 1 Audio",
      "audio_elements": [
        {
          "type": "dialogue/narration/music/sfx/ambience",
          "start_seconds": 0,
          "duration_seconds": 3,
          "content": "Exact text or detailed sound description",
          "character": "Character name or null",
          "voice_style": "calm/excited/whispered/heroic/cracking",
          "layers": [
            {"element": "voice", "description": "young male, earnest tone, slight echo"},
            {"element": "ambience", "description": "wind through grass, distant birds"},
            {"element": "sfx", "description": "soft footsteps on gravel, fabric rustle"}
          ],
          "processing": "light reverb, gentle compression",
          "volume": 1.0,
          "fade": "none/fade-in/fade-out/crossfade",
          "emotion_sync": "wonder"
        }
      ],
      "background_music": {
        "genre": "orchestral/electronic/traditional-japanese/hybrid",
        "mood": "epic/peaceful/tense/melancholy/triumphant",
        "tempo_bpm": 90,
        "key": "D minor",
        "instruments": ["strings", "taiko drums", "bamboo flute"],
        "description": "LMMS-style: pad synth sustain in D minor, layered with pizzicato strings, building to brass crescendo",
        "dynamic_changes": [
          {"at_seconds": 0, "change": "soft intro, strings only"},
          {"at_seconds": 15, "change": "drums enter, tempo rises"},
          {"at_seconds": 30, "change": "full orchestra, triumphant swell"}
        ]
      },
      "emotion_map": {
        "overall": "tension building to release",
        "character_emotions": [
          {"character": "Name", "emotion": "doubt→resolve", "audio_response": "thin texture → full orchestra"}
        ]
      }
    }
  ],
  "global_mix": {
    "master_reverb": "medium hall",
    "stereo_width": "wide for ambience, center for dialogue",
    "loudness_target_lufs": -14
  },
  "total_audio_duration_seconds": 120
}

Return ONLY valid JSON. Be extremely detailed with layered sound design."""


class AudioAgent(BaseAgent):
    """
    Enhanced Agent 6: Rich SFX/music with procedural descriptions and emotion sync.

    Features:
    - Layered audio elements (voice + ambience + SFX per cue)
    - Procedural descriptions (Audacity/LMMS-style)
    - Emotion-synced dynamics (character emotion → audio response)
    - Background music with dynamic changes and instrument details
    - Global mix settings
    """

    def __init__(self, output_dir: str = "data/output/audio", **kwargs):
        super().__init__(name="AudioAgent", **kwargs)
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

    def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        animation_plan = input_data.get("animation_plan", {})
        storyboard = input_data.get("storyboard", {})
        character_data = input_data.get("character_data", {})

        self.log("Creating rich audio plan (layered SFX + emotion-synced music)...")

        # Extract character emotion data for audio sync
        char_emotions = []
        for sheet in character_data.get("character_sheets", []):
            emotions = sheet.get("emotional_states", {})
            if emotions:
                char_emotions.append({
                    "name": sheet.get("name"),
                    "voice_style": sheet.get("voice_style", "neutral"),
                    "emotions": emotions,
                })

        prompt = (
            "Create a rich, layered audio production plan synced to character emotions.\n\n"
            f"Animation plan: {json.dumps(animation_plan, indent=2)}\n\n"
            f"Storyboard: {json.dumps(storyboard, indent=2)}\n\n"
            f"Character emotions: {json.dumps(char_emotions, indent=2)}"
        )

        result = self.genai.generate_json(
            prompt=prompt,
            model=MODEL_FLASH_TEXT,
            system_instruction=AUDIO_SYSTEM_PROMPT,
        )

        plan_path = os.path.join(self.output_dir, "audio_plan.json")
        with open(plan_path, "w") as f:
            json.dump(result, f, indent=2)
        self.log(f"Audio plan saved: {plan_path}")

        num_tracks = len(result.get("tracks", []))
        total_elements = sum(
            len(t.get("audio_elements", [])) for t in result.get("tracks", [])
        )
        self.log(f"Audio planning complete — {num_tracks} tracks, {total_elements} elements")
        return result
