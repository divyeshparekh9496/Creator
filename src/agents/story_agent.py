"""
StoryAgent — narrative understanding, cleansing, and structuring.
Converts raw story input into structured beats via Gemini.
"""
import json
from typing import Dict, Any

from src.agents.base_agent import BaseAgent
from src.config import MODEL_FLASH_TEXT

STORY_SYSTEM_PROMPT = """You are a professional anime story analyst. Given a story or text input,
you must return a JSON object with the following structure:

{
  "title": "Suggested anime title",
  "beats": [
    {"id": 1, "description": "Beat description", "mood": "Mood keyword"}
  ],
  "characters": [
    {"name": "Character name", "role": "protagonist/antagonist/supporting",
     "description": "Visual and personality description",
     "key_traits": ["trait1", "trait2"]}
  ],
  "setting": {
    "world": "World description",
    "time_period": "Time period",
    "locations": ["Location 1", "Location 2"]
  },
  "mood": "Overall mood",
  "genre": "Genre classification (e.g., action, romance, sci-fi)",
  "episode_structure": {
    "format": "TV series / OVA / Movie",
    "episode_count": 3,
    "episodes": [
      {"number": 1, "title": "Episode title", "summary": "Episode summary",
       "beats": [1, 2]}
    ]
  }
}

Return ONLY valid JSON. No markdown, no explanation. Keep beats to 3-5 items.
Keep characters to the main cast (max 5). Be creative with the title."""


class StoryAgent(BaseAgent):
    """
    Agent 1: Narrative understanding and structuring.
    Input:  raw story text (str)
    Output: structured beats, characters, setting, mood, genre, episode structure
    """

    def __init__(self, **kwargs):
        super().__init__(name="StoryAgent", **kwargs)

    def run(self, story_text: str) -> Dict[str, Any]:
        self.log(f"Analyzing story ({len(story_text)} chars)...")

        prompt = f"Analyze this story and return structured JSON:\n\n{story_text}"

        result = self.genai.generate_json(
            prompt=prompt,
            model=MODEL_FLASH_TEXT,
            system_instruction=STORY_SYSTEM_PROMPT,
        )

        self.log(f"Story analysis complete — title: {result.get('title', 'Untitled')}")
        return result
