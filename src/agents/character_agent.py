"""
CharacterDevelopmentAgent — deep character arc tracking, visual evolution, and emotion state.

Builds evolving characters with backstories, motivations, and visual/emotional changes
across scenes. Outputs character sheets as JSON profiles and reference images.

Open-source inspirations:
- LlamaGenAI/LlamaGen, dtoyoda10/anime-gen: JSON character sheet patterns
- FLUX.1 Kontext: Embedding consistency for visual anchoring
- AnimeGANv2: Style-locked character rendering
"""
import os
import json
import copy
from typing import Dict, Any, List, Optional
from PIL import Image

from src.agents.base_agent import BaseAgent
from src.config import MODEL_PRO_IMAGE, MODEL_FLASH_TEXT, DEFAULT_ASPECT_RATIO, DEFAULT_IMAGE_SIZE


CHARACTER_SYSTEM_PROMPT = """You are an anime character designer and narrative psychologist.
Given a story analysis, create DEEP character profiles with arcs, backstories, and evolution.

Return a JSON object:
{
  "characters": [
    {
      "id": "char_001",
      "name": "Character Name",
      "role": "protagonist/antagonist/supporting",
      "backstory": "2-3 sentence backstory that drives their motivation",
      "motivation": "What they want and why",
      "personality": ["brave but doubtful", "secretly kind"],
      "arc": {
        "stages": ["naive", "doubtful", "determined", "heroic"],
        "current_stage": 0,
        "arc_description": "From innocent youth to reluctant hero"
      },
      "visual_traits": {
        "base": {
          "hair": "blue, shoulder-length, slightly messy",
          "eyes": "amber, wide and expressive",
          "build": "slim, athletic",
          "outfit": "worn traveler's cloak over leather armor",
          "distinguishing_features": ["small scar on left cheek"]
        },
        "evolution": [
          {
            "trigger_scene": 1,
            "changes": "Scar is fresh and red, eyes are bright with innocence"
          },
          {
            "trigger_scene": 3,
            "changes": "Scar deepens, eyes grow sharper, cloak is torn"
          },
          {
            "trigger_scene": 5,
            "changes": "Scar fades to silver, eyes burn with resolve, new armor"
          }
        ]
      },
      "emotional_states": {
        "default": "cautiously optimistic",
        "per_scene": [
          {"scene_id": 1, "emotion": "wonder and fear", "intensity": 0.6},
          {"scene_id": 3, "emotion": "doubt and anger", "intensity": 0.9},
          {"scene_id": 5, "emotion": "resolve and calm power", "intensity": 0.8}
        ]
      },
      "relationships": [
        {"with": "Other Character", "type": "rival-turned-ally", "evolution": "distrust→respect"}
      ],
      "voice_style": "young, earnest, cracks under pressure"
    }
  ],
  "art_style": "AnimeGANv2-style: cel-shaded, high-contrast lighting, vivid colors, detailed linework"
}

Return ONLY valid JSON. Create rich, evolving characters. Max 5 characters."""


VISUAL_EVOLUTION_PROMPT = """You are tracking a character's visual evolution across scenes.
Given the character's current state and scene context, describe EXACTLY how they should
look in this scene, including any changes from their base design.

Return JSON:
{
  "character_id": "char_001",
  "scene_id": 1,
  "visual_state": "Full visual description for this specific scene",
  "emotion_display": "How their current emotion shows physically",
  "effects": ["glow_aura", "wind_hair", "shadow_cast"],
  "consistency_anchors": ["blue hair", "amber eyes", "scar position"]
}

Return ONLY valid JSON."""


class CharacterDevelopmentAgent(BaseAgent):
    """
    Enhanced Character Agent with deep arc tracking and visual evolution.

    Features:
    - Backstory and motivation generation
    - Arc stages tracked across scenes
    - Visual trait evolution (e.g., "scar deepens post-battle")
    - Emotional state per scene → feeds into Audio and Image agents
    - Consistency anchors for visual locking (FLUX.1 / ReferenceNet inspired)
    """

    def __init__(self, output_dir: str = "data/output/characters", **kwargs):
        super().__init__(name="CharacterDevelopmentAgent", **kwargs)
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        # Evolution state persists across scenes
        self._evolution_state: Dict[str, Any] = {}

    def run(self, story_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Phase 1: Generate deep character profiles from story analysis.
        Returns character sheets with arcs, visual evolution plans, and reference images.
        """
        self.log("Building Character Development Engine...")

        prompt = (
            "Create deep character profiles with arcs and visual evolution for:\n\n"
            f"{json.dumps(story_analysis, indent=2)}"
        )

        profiles = self.genai.generate_json(
            prompt=prompt,
            model=MODEL_FLASH_TEXT,
            system_instruction=CHARACTER_SYSTEM_PROMPT,
        )

        characters = profiles.get("characters", [])
        style = profiles.get("art_style", "AnimeGANv2-style: cel-shaded, high-contrast")

        # Generate reference sheet for each character
        sheets = []
        for char in characters:
            name = char.get("name", "Unknown")
            char_id = char.get("id", name.lower().replace(" ", "_"))
            self.log(f"  Designing: {name} (arc: {char.get('arc', {}).get('arc_description', 'N/A')})")

            sheet_prompt = self._build_sheet_prompt(char, style)

            try:
                image = self.genai.generate_image(
                    prompt=sheet_prompt,
                    model=MODEL_PRO_IMAGE,
                    aspect_ratio=DEFAULT_ASPECT_RATIO,
                    image_size=DEFAULT_IMAGE_SIZE,
                )

                local_path = None
                gcs_path = None
                if image:
                    safe_name = char_id
                    local_path = os.path.join(self.output_dir, f"{safe_name}_sheet.png")
                    image.save(local_path)
                    gcs_path = f"characters/{safe_name}/sheet.png"
                    self.gcs.upload_blob(local_path, gcs_path)
                    self.log(f"  Sheet saved: {local_path}")

                sheets.append({
                    **char,
                    "local_path": local_path,
                    "gcs_path": gcs_path,
                    "sheet_prompt": sheet_prompt,
                })

            except Exception as e:
                self.log(f"  Error generating {name}: {e}")
                sheets.append({**char, "local_path": None, "error": str(e)})

            # Initialize evolution state
            self._evolution_state[char_id] = {
                "current_arc_stage": 0,
                "visual_changes_applied": [],
                "emotion_history": [],
            }

        # Save character profiles JSON
        profiles_path = os.path.join(self.output_dir, "character_profiles.json")
        serializable_sheets = []
        for s in sheets:
            s_copy = {k: v for k, v in s.items() if k != "local_path" or v is None or isinstance(v, str)}
            serializable_sheets.append(s_copy)
        with open(profiles_path, "w") as f:
            json.dump({"characters": serializable_sheets, "art_style": style}, f, indent=2)

        # Upload arc data to GCS
        self.gcs.upload_blob(profiles_path, "characters/profiles.json")

        self.log(f"Character Development complete — {len(sheets)} characters with arcs")
        return {
            "character_sheets": sheets,
            "style": style,
            "evolution_state": self._evolution_state,
        }

    def get_scene_state(
        self, char_id: str, scene_id: int, scene_context: str
    ) -> Dict[str, Any]:
        """
        Get a character's visual and emotional state for a specific scene.
        Updates the evolution state and returns scene-specific rendering instructions.
        """
        char_data = None
        for sheet in self._evolution_state.get("_sheets", []):
            if sheet.get("id") == char_id:
                char_data = sheet
                break

        if not char_data:
            return {"character_id": char_id, "scene_id": scene_id, "visual_state": "default"}

        prompt = (
            f"Character: {json.dumps(char_data, indent=2)}\n"
            f"Scene {scene_id} context: {scene_context}\n"
            f"Previous changes: {json.dumps(self._evolution_state.get(char_id, {}))}\n"
            f"Describe their exact visual state for this scene."
        )

        try:
            result = self.genai.generate_json(
                prompt=prompt,
                model=MODEL_FLASH_TEXT,
                system_instruction=VISUAL_EVOLUTION_PROMPT,
            )

            # Update evolution state
            state = self._evolution_state.setdefault(char_id, {})
            state.setdefault("visual_changes_applied", []).append({
                "scene_id": scene_id,
                "changes": result.get("visual_state", ""),
            })
            state.setdefault("emotion_history", []).append({
                "scene_id": scene_id,
                "emotion": result.get("emotion_display", ""),
            })

            return result

        except Exception as e:
            self.log(f"  Evolution query error for {char_id}: {e}")
            return {"character_id": char_id, "scene_id": scene_id, "visual_state": "default"}

    def advance_arc(self, char_id: str) -> int:
        """Advance a character to the next arc stage."""
        state = self._evolution_state.get(char_id, {})
        current = state.get("current_arc_stage", 0)
        state["current_arc_stage"] = current + 1
        return state["current_arc_stage"]

    def _build_sheet_prompt(self, char: Dict, style: str) -> str:
        name = char.get("name", "Unknown")
        role = char.get("role", "character")
        backstory = char.get("backstory", "")
        personality = ", ".join(char.get("personality", []))
        visual = char.get("visual_traits", {}).get("base", {})

        hair = visual.get("hair", "")
        eyes = visual.get("eyes", "")
        build = visual.get("build", "")
        outfit = visual.get("outfit", "")
        features = ", ".join(visual.get("distinguishing_features", []))

        return (
            f"AnimeGANv2 style character sheet for '{name}', a {role}. "
            f"Backstory: {backstory}. Personality: {personality}. "
            f"Hair: {hair}. Eyes: {eyes}. Build: {build}. Outfit: {outfit}. "
            f"Distinguishing features: {features}. "
            f"Art style: {style}. "
            f"Show THREE poses: front view (neutral), side view (determined), "
            f"and action pose (signature move). Include color palette swatches. "
            f"Anime production quality, clean white background, detailed linework. "
            f"FLUX.1 consistency: maintain exact proportions across all three poses."
        )
