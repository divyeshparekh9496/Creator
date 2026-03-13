"""
ImageAgent — enhanced keyframe generation with AnimeGANv2 style,
Animate Anyone motion hints, and particle/glow effects.

Open-source inspirations:
- AnimeGANv2 (TachibanaYoshino): Style-locked anime rendering
- Animate Anyone (humanaigc): Pose-guided smooth transitions
- FLUX.1 Kontext: Frame-to-frame consistency via reference anchoring
"""
import os
from typing import Dict, Any, List, Optional
from PIL import Image

from src.agents.base_agent import BaseAgent
from src.config import MODEL_PRO_IMAGE, MODEL_FLASH_IMAGE, DEFAULT_ASPECT_RATIO, DEFAULT_IMAGE_SIZE


# Effect presets for visual richness
EFFECT_PRESETS = {
    "particle_rain": "fine rain particles with subtle light refraction",
    "particle_dust": "floating dust motes catching warm light",
    "particle_snow": "gentle snowfall with bokeh depth",
    "particle_fire": "ember sparks trailing upward",
    "inner_glow": "soft inner aura glow emanating from character",
    "glow_aura": "ethereal energy aura surrounding character",
    "lens_flare": "cinematic lens flare from light source",
    "speed_lines": "dynamic speed lines indicating rapid motion",
    "wind_hair": "hair dramatically blown by wind",
    "shadow_cast": "dramatic long shadows with high contrast",
    "fire_trail": "fire trail follows weapon swing",
    "explosion_particles": "debris and light burst from impact",
    "cherry_blossoms": "floating cherry blossom petals",
    "energy_burst": "radiating energy wave from center",
}


class ImageAgent(BaseAgent):
    """
    Enhanced Agent 4: AnimeGANv2-styled keyframes with Animate Anyone
    motion hints and rich visual effects.

    Features:
    - AnimeGANv2 style prefix on all prompts
    - Animate Anyone motion descriptors for pose-guided frames
    - Particle/glow/effect system
    - Character evolution visual state integration
    - FLUX.1-inspired consistency anchoring
    """

    def __init__(self, output_dir: str = "data/output/keyframes", **kwargs):
        super().__init__(name="ImageAgent", **kwargs)
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

    def _build_enhanced_prompt(
        self,
        shot: Dict,
        scene: Dict,
        style: str,
        char_states: List[Dict] = None,
    ) -> str:
        """Build a rich prompt with AnimeGANv2 style + Animate Anyone motion + effects."""
        shot_type = shot.get("shot_type", "medium")
        action = shot.get("action", "")
        expression = shot.get("expression", "")
        visual_notes = shot.get("visual_notes", "")
        location = scene.get("location", "")
        time_of_day = scene.get("time_of_day", "day")
        characters = ", ".join(shot.get("characters_present", []))
        dialogue = shot.get("dialogue")

        # AnimeGANv2 style prefix
        prompt = f"AnimeGANv2 style: {style}. "

        # Scene composition
        prompt += (
            f"{shot_type} shot. {location}, {time_of_day}. "
            f"Characters: {characters}. "
        )

        # Character evolution state
        if char_states:
            for cs in char_states:
                visual = cs.get("visual_state", "")
                emotion = cs.get("emotion_display", "")
                if visual:
                    prompt += f"Character appearance: {visual}. "
                if emotion:
                    prompt += f"Emotional display: {emotion}. "

        # Action and expression
        prompt += f"Action: {action}. Expression: {expression}. "

        # Animate Anyone motion hint
        camera = shot.get("camera_movement", "static")
        if camera != "static":
            prompt += f"Animate Anyone smooth {camera} motion. "

        # Effects
        effects = shot.get("effects", [])
        if effects:
            effect_descs = []
            for eff in effects:
                desc = EFFECT_PRESETS.get(eff, eff)
                effect_descs.append(desc)
            prompt += f"Visual effects: {', '.join(effect_descs)}. "

        # Visual notes and quality
        if visual_notes:
            prompt += f"{visual_notes}. "

        prompt += (
            "High quality anime production frame, detailed backgrounds, "
            "FLUX.1 consistency: maintain character proportions and design exactly."
        )

        if dialogue:
            prompt += f" Speech bubble: '{dialogue}'."

        return prompt

    def _load_character_refs(self, character_sheets: List[Dict]) -> List[Image.Image]:
        """Load character sheet images as ReferenceNet-style anchors."""
        refs = []
        for sheet in character_sheets:
            path = sheet.get("local_path")
            if path and os.path.exists(path):
                try:
                    refs.append(Image.open(path))
                except Exception:
                    pass
        return refs[:3]  # Nano Banana supports up to 14, use 3 for speed

    def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        storyboard = input_data.get("storyboard", {})
        character_data = input_data.get("character_data", {})
        style = character_data.get("style", "AnimeGANv2-style: cel-shaded, high-contrast")

        self.log("Generating enhanced keyframes (AnimeGANv2 + Animate Anyone + effects)...")

        refs = self._load_character_refs(character_data.get("character_sheets", []))
        self.log(f"  ReferenceNet anchors: {len(refs)} character sheets loaded")

        keyframes: List[Dict[str, Any]] = []

        for scene in storyboard.get("scenes", []):
            scene_id = scene.get("scene_id", 0)
            for shot in scene.get("shots", []):
                shot_id = shot.get("shot_id", 0)
                self.log(f"  Generating: Scene {scene_id}, Shot {shot_id}")

                prompt = self._build_enhanced_prompt(shot, scene, style)

                try:
                    if refs:
                        image = self.genai.edit_image(
                            prompt=prompt,
                            reference_images=refs,
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
                            "effects": shot.get("effects", []),
                            "camera_movement": shot.get("camera_movement", "static"),
                        })
                    else:
                        keyframes.append({"scene_id": scene_id, "shot_id": shot_id, "local_path": None})

                except Exception as e:
                    self.log(f"  Error: S{scene_id}/Shot{shot_id}: {e}")
                    keyframes.append({"scene_id": scene_id, "shot_id": shot_id, "error": str(e)})

        self.log(f"Keyframe generation complete — {len(keyframes)} enhanced frames")
        return {"keyframes": keyframes, "style": style}
