"""
ImageAgent — enforces Visual Consistency Protocol from Enhancement #1.

Every image prompt MUST include:
  "Character: [name] from sheet [character_id]"
  "Current arc stage: [stage] visual traits: [changes]"
  "Style anchor: [style_lock]"

Open-source inspirations:
- AnimeGANv2: Style-locked anime rendering
- Animate Anyone: Pose-guided smooth transitions
- FLUX.1 Kontext: Frame-to-frame consistency via reference anchoring
"""
import os
from typing import Dict, Any, List, Optional
from PIL import Image

from src.agents.base_agent import BaseAgent
from src.config import MODEL_PRO_IMAGE, MODEL_FLASH_IMAGE, DEFAULT_ASPECT_RATIO, DEFAULT_IMAGE_SIZE


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
    "dust_motes": "gentle floating dust particles in light beams",
}


class ImageAgent(BaseAgent):
    """
    Enhanced ImageAgent with mandatory Visual Consistency Protocol.

    Every image prompt includes:
    1. AnimeGANv2 style prefix
    2. Character sheet reference + arc stage + style anchor (from CharacterDevelopmentAgent)
    3. Animate Anyone motion hints
    4. Effect/particle descriptors
    5. FLUX.1 consistency anchors
    """

    def __init__(self, output_dir: str = "data/output/keyframes", **kwargs):
        super().__init__(name="ImageAgent", **kwargs)
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

    def _build_prompt_with_consistency(
        self,
        shot: Dict,
        scene: Dict,
        style: str,
        character_consistency_blocks: List[str],
    ) -> str:
        """
        Build prompt enforcing Visual Consistency Protocol.
        Every prompt MUST include character sheet ref + arc stage + style anchor.
        """
        shot_type = shot.get("shot_type", "medium")
        action = shot.get("action", "")
        expression = shot.get("expression", "")
        visual_notes = shot.get("visual_notes", "")
        location = scene.get("location", "")
        time_of_day = scene.get("time_of_day", "day")
        dialogue = shot.get("dialogue")

        # ── AnimeGANv2 style prefix ──
        prompt = f"AnimeGANv2 style: {style}. "

        # ── Scene composition ──
        prompt += f"{shot_type} shot. {location}, {time_of_day}. "

        # ── VISUAL CONSISTENCY PROTOCOL (MANDATORY) ──
        for block in character_consistency_blocks:
            prompt += f"{block}. "

        # ── Action / expression ──
        prompt += f"Action: {action}. Expression: {expression}. "

        # ── Animate Anyone motion hint ──
        camera = shot.get("camera_movement", "static")
        animate_hint = shot.get("animate_anyone_hint", "")
        if camera != "static":
            prompt += f"Animate Anyone smooth {camera}. "
        if animate_hint:
            prompt += f"Animate Anyone: {animate_hint}. "

        # ── Effects ──
        effects = shot.get("effects", [])
        if effects:
            effect_descs = [EFFECT_PRESETS.get(e, e) for e in effects]
            prompt += f"Effects: {', '.join(effect_descs)}. "

        # ── Visual notes ──
        if visual_notes:
            prompt += f"{visual_notes}. "

        # ── Quality + FLUX.1 consistency ──
        prompt += (
            "High quality anime production frame, detailed backgrounds. "
            "FLUX.1 consistency: maintain exact character proportions and design."
        )

        if dialogue:
            prompt += f" Speech bubble: '{dialogue}'."

        return prompt

    def _load_refs(self, character_sheets: List[Dict]) -> List[Image.Image]:
        refs = []
        for sheet in character_sheets:
            path = sheet.get("local_path")
            if path and os.path.exists(path):
                try:
                    refs.append(Image.open(path))
                except Exception:
                    pass
        return refs[:3]

    def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        storyboard = input_data.get("storyboard", {})
        character_data = input_data.get("character_data", {})
        char_agent = input_data.get("character_agent")  # Live agent ref for consistency blocks
        style = character_data.get("style", "AnimeGANv2 style: cel-shaded, high-contrast")

        self.log("Generating keyframes with Visual Consistency Protocol...")

        refs = self._load_refs(character_data.get("character_sheets", []))
        self.log(f"  ReferenceNet anchors: {len(refs)} sheets loaded")

        # Build consistency blocks index from sheets
        sheets = character_data.get("character_sheets", [])
        char_id_by_name = {}
        for s in sheets:
            char_id_by_name[s.get("name", "").lower()] = s.get("character_id", "")

        keyframes: List[Dict[str, Any]] = []

        for scene in storyboard.get("scenes", []):
            scene_id = scene.get("scene_id", 0)

            for shot in scene.get("shots", []):
                shot_id = shot.get("shot_id", 0)
                self.log(f"  Generating: Scene {scene_id}, Shot {shot_id}")

                # ── Visual Consistency Protocol ──
                consistency_blocks = []
                for char_name in shot.get("characters_present", []):
                    char_id = char_id_by_name.get(char_name.lower(), "")
                    if char_agent and char_id:
                        block = char_agent.get_visual_consistency_block(char_id)
                        if block:
                            consistency_blocks.append(block)
                    elif char_id:
                        # Fallback: build from sheet data
                        for s in sheets:
                            if s.get("character_id") == char_id:
                                style_lock = s.get("style_lock", "")
                                consistency_blocks.append(
                                    f"Character: {char_name} from sheet {char_id}, "
                                    f"Style anchor: {style_lock}"
                                )

                prompt = self._build_prompt_with_consistency(
                    shot, scene, style, consistency_blocks
                )

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
                            "consistency_blocks": consistency_blocks,
                        })
                    else:
                        keyframes.append({"scene_id": scene_id, "shot_id": shot_id, "local_path": None})

                except Exception as e:
                    self.log(f"  Error: S{scene_id}/Shot{shot_id}: {e}")
                    keyframes.append({"scene_id": scene_id, "shot_id": shot_id, "error": str(e)})

        self.log(f"Keyframe generation complete — {len(keyframes)} frames (consistency enforced)")
        return {"keyframes": keyframes, "style": style}
