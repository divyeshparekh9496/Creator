"""
CharacterAgent — character sheet generation and consistency management.
Generates visual character designs using Nano Banana Pro.
"""
import os
from typing import Dict, Any, List, Optional
from PIL import Image

from src.agents.base_agent import BaseAgent
from src.config import MODEL_PRO_IMAGE, DEFAULT_ASPECT_RATIO, DEFAULT_IMAGE_SIZE


class CharacterAgent(BaseAgent):
    """
    Agent 3: Character design and consistency.
    Input:  story analysis dict (characters list + art style)
    Output: character sheets (images saved locally & to GCS)
    """

    def __init__(self, output_dir: str = "data/output/characters", **kwargs):
        super().__init__(name="CharacterAgent", **kwargs)
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

    def _build_character_prompt(self, character: Dict, style: str) -> str:
        """Build an image-generation prompt for a character sheet."""
        name = character.get("name", "Unknown")
        desc = character.get("description", "")
        traits = ", ".join(character.get("key_traits", []))
        role = character.get("role", "character")

        return (
            f"Anime character sheet for '{name}', a {role}. "
            f"Description: {desc}. Key traits: {traits}. "
            f"Art style: {style}. "
            f"Show the character in three poses: front view, side view, and action pose. "
            f"Include color palette swatches. Professional anime production quality. "
            f"Clean white background, detailed linework."
        )

    def run(self, story_analysis: Dict[str, Any]) -> Dict[str, Any]:
        self.log("Generating character sheets...")

        characters = story_analysis.get("characters", [])
        style = story_analysis.get("metadata", {}).get(
            "suggested_style",
            "Shonen-style anime, 2D, cel-shaded, high-contrast lighting"
        )

        sheets: List[Dict[str, Any]] = []

        for char in characters:
            name = char.get("name", "Unknown")
            self.log(f"  Designing: {name}")

            prompt = self._build_character_prompt(char, style)

            try:
                image = self.genai.generate_image(
                    prompt=prompt,
                    model=MODEL_PRO_IMAGE,
                    aspect_ratio=DEFAULT_ASPECT_RATIO,
                    image_size=DEFAULT_IMAGE_SIZE,
                )

                if image:
                    safe_name = name.lower().replace(" ", "_")
                    local_path = os.path.join(self.output_dir, f"{safe_name}_sheet.png")
                    image.save(local_path)
                    self.log(f"  Saved: {local_path}")

                    # Upload to GCS
                    gcs_path = f"characters/{safe_name}_sheet.png"
                    self.gcs.upload_blob(local_path, gcs_path)

                    sheets.append({
                        "name": name,
                        "local_path": local_path,
                        "gcs_path": gcs_path,
                        "prompt_used": prompt,
                    })
                else:
                    self.log(f"  Warning: No image generated for {name}")
                    sheets.append({"name": name, "local_path": None, "gcs_path": None})

            except Exception as e:
                self.log(f"  Error generating {name}: {e}")
                sheets.append({"name": name, "local_path": None, "error": str(e)})

        self.log(f"Character design complete — {len(sheets)} sheets generated")
        return {"character_sheets": sheets, "style": style}
