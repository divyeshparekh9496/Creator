"""
SceneRenderer — per-scene interleaved output combining all agent outputs.

Produces the final interleaved stream: narration + character update + image + audio + effects + JSON metadata.
This is the core Creative Director output format.
"""
import os
import json
from typing import Dict, Any, List, Optional

from src.agents.base_agent import BaseAgent
from src.config import MODEL_FLASH_IMAGE


class SceneRenderer(BaseAgent):
    """
    Renders per-scene interleaved output combining all pipeline data.

    For each scene, produces:
    - Narration text
    - Character arc update (what changed)
    - Keyframe image reference
    - Audio/SFX description
    - Motion/effects description
    - JSON metadata

    This is the format described in the enhanced Creator prompt:
    ```
    Scene 2 – Character Growth: Doubt Turns to Resolve
    - Narration: "For the first time, Akira felt the weight of her choice..."
    - Character Update: Scar deepens (arc: vulnerability peak); eyes sharpen.
    - Image: [Nano Banana 2: AnimeGANv2 style, ...]
    - Audio: Tense strings build (LMMS-style: low synth drone + heartbeat SFX).
    - Motion/Effects: Slow zoom-in, particle rain + inner glow flare.
    - Metadata: {"scene":2, "char_arc":"doubt_resolve", "duration":8s}
    ```
    """

    def __init__(self, output_dir: str = "data/output/scenes", **kwargs):
        super().__init__(name="SceneRenderer", **kwargs)
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

    def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        storyboard = input_data.get("storyboard", {})
        character_data = input_data.get("character_data", {})
        keyframes = input_data.get("keyframes", {})
        animation_plan = input_data.get("animation_plan", {})
        audio_plan = input_data.get("audio_plan", {})
        story_analysis = input_data.get("story_analysis", {})

        self.log("Rendering interleaved scene output...")

        scenes_output: List[Dict[str, Any]] = []
        rendered_text_parts: List[str] = []

        # Index keyframes by scene/shot
        kf_index = {}
        for kf in keyframes.get("keyframes", []):
            key = (kf.get("scene_id"), kf.get("shot_id"))
            kf_index[key] = kf

        # Index animation sequences
        anim_sequences = {}
        for part in animation_plan.get("parts", []):
            for seq in part.get("sequences", []):
                key = (seq.get("scene_id"), seq.get("shot_id"))
                anim_sequences[key] = seq

        # Index audio elements by part
        audio_tracks = {t.get("part_id"): t for t in audio_plan.get("tracks", [])}

        # Character sheets for arc summary
        chars = character_data.get("character_sheets", [])

        for scene in storyboard.get("scenes", []):
            scene_id = scene.get("scene_id", 0)
            location = scene.get("location", "Unknown")
            time_of_day = scene.get("time_of_day", "day")

            scene_text = f"\n{'═' * 60}\n"
            scene_text += f"Scene {scene_id} — {location} ({time_of_day})\n"
            scene_text += f"{'═' * 60}\n"

            scene_shots = []

            for shot in scene.get("shots", []):
                shot_id = shot.get("shot_id", 0)
                key = (scene_id, shot_id)

                # Narration
                narration = shot.get("narration") or shot.get("dialogue") or ""
                action = shot.get("action", "")

                # Character update
                char_updates = []
                for char in chars:
                    char_name = char.get("name", "")
                    if char_name in shot.get("characters_present", []):
                        arc = char.get("arc", {})
                        emotions = char.get("emotional_states", {})
                        scene_emotions = [
                            e for e in emotions.get("per_scene", [])
                            if e.get("scene_id") == scene_id
                        ]
                        evolution = char.get("visual_traits", {}).get("evolution", [])
                        scene_evo = [
                            e for e in evolution
                            if e.get("trigger_scene") == scene_id
                        ]

                        update = f"{char_name}"
                        if scene_emotions:
                            update += f" — emotion: {scene_emotions[0].get('emotion', 'neutral')}"
                        if scene_evo:
                            update += f" — visual: {scene_evo[0].get('changes', '')}"
                        if arc.get("arc_description"):
                            update += f" (arc: {arc['arc_description']})"
                        char_updates.append(update)

                # Keyframe reference
                kf = kf_index.get(key, {})
                image_path = kf.get("local_path", "Not generated")

                # Animation/effects
                anim = anim_sequences.get(key, {})
                motion = anim.get("motion", {})
                effects = anim.get("effects", {})
                motion_desc = motion.get("character_motion", "") if isinstance(motion, dict) else str(motion)
                camera_desc = motion.get("camera", "") if isinstance(motion, dict) else ""
                particles = effects.get("particles", []) if isinstance(effects, dict) else []
                lighting = effects.get("lighting", "") if isinstance(effects, dict) else ""
                special = effects.get("special", "") if isinstance(effects, dict) else ""

                # Audio
                duration = shot.get("duration_seconds", 3)

                # Build interleaved text
                shot_text = f"\n  Shot {shot_id} ({shot.get('shot_type', 'medium')}) — {duration}s\n"
                if narration:
                    shot_text += f"  📖 Narration: \"{narration}\"\n"
                if action:
                    shot_text += f"  🎬 Action: {action}\n"
                if char_updates:
                    shot_text += f"  👤 Character Update: {'; '.join(char_updates)}\n"
                shot_text += f"  🖼️  Image: {image_path}\n"
                if motion_desc or camera_desc:
                    shot_text += f"  🎥 Motion: {camera_desc} — {motion_desc}\n"
                if particles or lighting or special:
                    effect_parts = []
                    if particles:
                        effect_parts.append(f"particles: {', '.join(particles)}")
                    if lighting:
                        effect_parts.append(f"lighting: {lighting}")
                    if special:
                        effect_parts.append(f"special: {special}")
                    shot_text += f"  ✨ Effects: {' + '.join(effect_parts)}\n"
                shot_text += f"  🔊 Audio sync: emotion={shot.get('expression', 'neutral')}\n"

                # JSON metadata
                metadata = {
                    "scene": scene_id,
                    "shot": shot_id,
                    "duration": duration,
                    "char_arc": char_updates[0] if char_updates else "none",
                    "effects_count": len(particles),
                    "has_dialogue": bool(shot.get("dialogue")),
                }
                shot_text += f"  📋 Metadata: {json.dumps(metadata)}\n"

                scene_text += shot_text
                scene_shots.append({
                    "shot_id": shot_id,
                    "narration": narration,
                    "action": action,
                    "character_updates": char_updates,
                    "image_path": image_path,
                    "motion": motion_desc,
                    "effects": {"particles": particles, "lighting": lighting, "special": special},
                    "metadata": metadata,
                })

            scenes_output.append({
                "scene_id": scene_id,
                "location": location,
                "shots": scene_shots,
            })
            rendered_text_parts.append(scene_text)

        # Save full interleaved output
        full_text = "\n".join(rendered_text_parts)
        text_path = os.path.join(self.output_dir, "interleaved_output.txt")
        with open(text_path, "w") as f:
            f.write(full_text)

        # Save structured JSON
        json_path = os.path.join(self.output_dir, "scenes_data.json")
        with open(json_path, "w") as f:
            json.dump({"scenes": scenes_output}, f, indent=2)

        # Upload to GCS
        self.gcs.upload_blob(text_path, "scenes/interleaved_output.txt")
        self.gcs.upload_blob(json_path, "scenes/scenes_data.json")

        self.log(f"Scene rendering complete — {len(scenes_output)} scenes interleaved")
        print(full_text)  # Display the interleaved output

        return {
            "scenes": scenes_output,
            "interleaved_text": full_text,
            "output_path": text_path,
        }
