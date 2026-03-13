"""
SceneRenderer — interleaved character-driven output format from Enhancement #1.

Per-scene output:
  SCENE [N] – [Character Name] Arc Stage [X]
  Character Evolution: [previous] → [current], Visual: [changes]
  Narration: "[voiceover]"
  Image: [prompt with character sheet reference]
  Audio: "[music/SFX matching emotional state]"
  Metadata: {"char_id": "[id]", "arc_stage": X, "duration": "8s"}
"""
import os
import json
from typing import Dict, Any, List

from src.agents.base_agent import BaseAgent


class SceneRenderer(BaseAgent):
    """
    Renders per-scene interleaved output with character evolution tracking.
    Uses the exact format from Enhancement #1.
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
        char_agent = input_data.get("character_agent")

        self.log("Rendering interleaved character-driven scene output...")

        sheets = character_data.get("character_sheets", [])
        char_by_name = {s.get("name", "").lower(): s for s in sheets}

        # Index keyframes
        kf_index = {}
        for kf in keyframes.get("keyframes", []):
            kf_index[(kf.get("scene_id"), kf.get("shot_id"))] = kf

        # Index animation
        anim_seqs = {}
        for part in animation_plan.get("parts", []):
            for seq in part.get("sequences", []):
                anim_seqs[(seq.get("scene_id"), seq.get("shot_id"))] = seq

        scenes_output = []
        rendered_lines = []

        for scene in storyboard.get("scenes", []):
            scene_id = scene.get("scene_id", 0)
            location = scene.get("location", "")
            time_of_day = scene.get("time_of_day", "day")
            arc_context = scene.get("arc_context", "")

            # Find primary character for scene header
            all_chars_in_scene = set()
            for shot in scene.get("shots", []):
                for c in shot.get("characters_present", []):
                    all_chars_in_scene.add(c)

            primary_char = next(iter(all_chars_in_scene), "Unknown")
            primary_sheet = char_by_name.get(primary_char.lower(), {})
            primary_id = primary_sheet.get("character_id", "")
            current_stage = 1
            if char_agent and primary_id:
                current_stage = char_agent._current_stages.get(primary_id, 1)

            # ── Scene Header ──
            header = (
                f"\n{'═' * 60}\n"
                f"SCENE {scene_id} – {primary_char} Arc Stage {current_stage}\n"
                f"Location: {location} ({time_of_day})\n"
            )
            if arc_context:
                header += f"Arc Context: {arc_context}\n"
            header += f"{'═' * 60}\n"

            rendered_lines.append(header)
            scene_shots = []

            for shot in scene.get("shots", []):
                shot_id = shot.get("shot_id", 0)
                key = (scene_id, shot_id)
                duration = shot.get("duration_seconds", 3)

                # ── Character Evolution ──
                evolution_msgs = []
                for char_name in shot.get("characters_present", []):
                    char_sheet = char_by_name.get(char_name.lower(), {})
                    char_id = char_sheet.get("character_id", "")

                    if char_agent and char_id:
                        # Get current stage info
                        arc_stages = char_sheet.get("arc_stages", [])
                        stage_num = char_agent._current_stages.get(char_id, 1)
                        current_trait = ""
                        visual_change = ""
                        for s in arc_stages:
                            if s.get("stage") == stage_num:
                                current_trait = s.get("trait", "")
                                visual_change = s.get("visual_change", "")
                        evolution_msgs.append(
                            f"{char_name}: stage {stage_num} ({current_trait}), "
                            f"visual: {visual_change}"
                        )

                # ── Narration ──
                narration = shot.get("narration") or shot.get("dialogue") or ""
                action = shot.get("action", "")

                # ── Image ──
                kf = kf_index.get(key, {})
                image_ref = kf.get("local_path", "Not generated")

                # ── Motion/Effects ──
                anim = anim_seqs.get(key, {})
                motion = anim.get("motion", {})
                effects = anim.get("effects", {})
                motion_desc = ""
                if isinstance(motion, dict):
                    motion_desc = f"{motion.get('camera', '')} — {motion.get('character_motion', '')}"
                effect_parts = []
                if isinstance(effects, dict):
                    if effects.get("particles"):
                        effect_parts.append(f"particles: {', '.join(effects['particles'])}")
                    if effects.get("lighting"):
                        effect_parts.append(f"lighting: {effects['lighting']}")
                    if effects.get("special"):
                        effect_parts.append(f"special: {effects['special']}")

                # ── Audio ──
                expression = shot.get("expression", "neutral")
                # Map expression to audio hint
                audio_hints = {
                    "timid": "timid flutes, soft strings",
                    "determined": "building drums, brass entering",
                    "heroic": "epic horns, full orchestra",
                    "fearful": "tremolo strings, heartbeat pulse",
                    "angry": "aggressive percussion, distorted bass",
                    "peaceful": "gentle piano, nature ambience",
                }
                audio_desc = audio_hints.get(expression.lower(), f"mood: {expression}")

                # ── Metadata ──
                metadata = {
                    "char_id": primary_id,
                    "arc_stage": current_stage,
                    "duration": f"{duration}s",
                    "scene": scene_id,
                    "shot": shot_id,
                }

                # ── Build interleaved output ──
                shot_text = f"\n  Shot {shot_id} ({shot.get('shot_type', 'medium')}) — {duration}s\n"
                if evolution_msgs:
                    shot_text += f"  👤 Character Evolution: {'; '.join(evolution_msgs)}\n"
                if narration:
                    shot_text += f"  📖 Narration: \"{narration}\"\n"
                if action:
                    shot_text += f"  🎬 Action: {action}\n"
                shot_text += f"  🖼️  Image: [Nano Banana 2: {image_ref}]\n"
                shot_text += f"  🔊 Audio: [{audio_desc}]\n"
                if motion_desc:
                    shot_text += f"  🎥 Motion/Effects: {motion_desc}"
                    if effect_parts:
                        shot_text += f" + {' + '.join(effect_parts)}"
                    shot_text += "\n"
                shot_text += f"  📋 Metadata: {json.dumps(metadata)}\n"

                rendered_lines.append(shot_text)
                scene_shots.append({
                    "shot_id": shot_id,
                    "character_evolution": evolution_msgs,
                    "narration": narration,
                    "action": action,
                    "image_path": image_ref,
                    "audio": audio_desc,
                    "motion_effects": motion_desc,
                    "metadata": metadata,
                })

            scenes_output.append({
                "scene_id": scene_id,
                "primary_character": primary_char,
                "arc_stage": current_stage,
                "shots": scene_shots,
            })

        # ── Save outputs ──
        full_text = "\n".join(rendered_lines)
        text_path = os.path.join(self.output_dir, "interleaved_output.txt")
        with open(text_path, "w") as f:
            f.write(full_text)

        json_path = os.path.join(self.output_dir, "scenes_data.json")
        with open(json_path, "w") as f:
            json.dump({"scenes": scenes_output}, f, indent=2)

        self.gcs.upload_blob(text_path, "scenes/interleaved_output.txt")
        self.gcs.upload_blob(json_path, "scenes/scenes_data.json")

        self.log(f"Scene rendering complete — {len(scenes_output)} scenes")
        print(full_text)

        return {
            "scenes": scenes_output,
            "interleaved_text": full_text,
            "output_path": text_path,
        }
