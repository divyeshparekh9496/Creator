"""
ImageAgent — keyframe generation for each storyboard shot.
Uses Nano Banana Pro with character reference images for consistency.
"""
import os
from typing import Dict, Any, List, Optional
from PIL import Image

from src.agents.base_agent import BaseAgent
from src.config import MODEL_PRO_IMAGE, MODEL_FLASH_IMAGE, DEFAULT_ASPECT_RATIO, DEFAULT_IMAGE_SIZE


class ImageAgent(BaseAgent):
    """
    Agent 4: Frame-level image generation.
    Input:  storyboard (shot list) + character sheets
    Output: keyframe images for each shot, saved locally and to GCS
    """

    def __init__(self, output_dir: str = "data/output/keyframes", **kwargs):
        super().__init__(name="ImageAgent", **kwargs)
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

    def _build_keyframe_prompt(self, shot: Dict, scene: Dict, style: str) -> str:
        """Build a prompt for a single keyframe image."""
        shot_type = shot.get("shot_type", "medium")
        action = shot.get("action", "")
        expression = shot.get("expression", "")
        visual_notes = shot.get("visual_notes", "")
        location = scene.get("location", "")
        time_of_day = scene.get("time_of_day", "day")
        characters = ", ".join(shot.get("characters_present", []))
        dialogue = shot.get("dialogue", "")

        prompt = (
            f"Anime keyframe, {style}. "
            f"{shot_type} shot. Location: {location}, {time_of_day}. "
            f"Characters: {characters}. "
            f"Action: {action}. Expression: {expression}. "
            f"{visual_notes}. "
            f"High quality anime production frame, detailed backgrounds, "
            f"professional animation quality."
        )
        if dialogue:
            prompt += f" The character is saying: '{dialogue}'."
        return prompt

    def _load_character_refs(self, character_sheets: List[Dict]) -> List[Image.Image]:
        """Load character sheet images as references."""
        refs = []
        for sheet in character_sheets:
            path = sheet.get("local_path")
            if path and os.path.exists(path):
                try:
                    refs.append(Image.open(path))
                except Exception:
                    pass
        return refs

    def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        storyboard = input_data.get("storyboard", {})
        character_data = input_data.get("character_data", {})
        style = character_data.get("style", "Shonen-style anime, cel-shaded")

        self.log("Generating keyframes for all shots...")

        # Load character reference images for consistency
        refs = self._load_character_refs(character_data.get("character_sheets", []))
        self.log(f"  Loaded {len(refs)} character reference images")

        keyframes: List[Dict[str, Any]] = []

        for scene in storyboard.get("scenes", []):
            scene_id = scene.get("scene_id", 0)
            for shot in scene.get("shots", []):
                shot_id = shot.get("shot_id", 0)
                self.log(f"  Generating: Scene {scene_id}, Shot {shot_id}")

                prompt = self._build_keyframe_prompt(shot, scene, style)

                try:
                    if refs:
                        image = self.genai.edit_image(
                            prompt=prompt,
                            reference_images=refs[:3],  # Use up to 3 refs
                            model=MODEL_PRO_IMAGE,
                            aspect_ratio=DEFAULT_ASPECT_RATIO,
                            image_size=DEFAULT_IMAGE_SIZE,
                        )
                    else:
                        image = self.genai.generate_image(
                            prompt=prompt,
                            model=MODEL_FLASH_IMAGE,
                            aspect_ratio=DEFAULT_ASPECT_RATIO,
                            image_size=DEFAULT_IMAGE_SIZE,
                        )

                    if image:
                        filename = f"scene{scene_id:02d}_shot{shot_id:02d}.png"
                        local_path = os.path.join(self.output_dir, filename)
                        image.save(local_path)

                        gcs_path = f"keyframes/{filename}"
                        self.gcs.upload_blob(local_path, gcs_path)

                        keyframes.append({
                            "scene_id": scene_id,
                            "shot_id": shot_id,
                            "local_path": local_path,
                            "gcs_path": gcs_path,
                            "duration_seconds": shot.get("duration_seconds", 3),
                        })
                    else:
                        self.log(f"  Warning: No image for S{scene_id}/Shot{shot_id}")
                        keyframes.append({
                            "scene_id": scene_id,
                            "shot_id": shot_id,
                            "local_path": None,
                        })

                except Exception as e:
                    self.log(f"  Error: S{scene_id}/Shot{shot_id}: {e}")
                    keyframes.append({
                        "scene_id": scene_id,
                        "shot_id": shot_id,
                        "error": str(e),
                    })

        self.log(f"Keyframe generation complete — {len(keyframes)} frames")
        return {"keyframes": keyframes, "style": style}
