"""
SceneRenderer — RL-augmented interleaved character-driven output (Enhancement #2).

New per-scene format:
  SCENE [N] – RL-Enhanced
  RL State: [current params]
  Character Evolution: [arc] (Sub-RL Score: 0.85)
  Narration: [...]
  Image: [prompt + "RL Action: added glow effects for +0.2 reward"]
  Audio: [SFX + "RL Action: layered horns for emotional peak"]
  RL Reward Preview: Coherence=0.9, Total=0.87
  Metadata: {"rl_episode": N, "policy_version": "v3", "suggested_next_action": "..."}
"""
import os
import json
from typing import Dict, Any, List

from src.agents.base_agent import BaseAgent


class SceneRenderer(BaseAgent):
    """Renders RL-augmented interleaved output per scene."""

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
        rl_master = input_data.get("rl_master")
        rl_rewards = input_data.get("rl_rewards", {})

        self.log("Rendering RL-augmented interleaved output...")

        sheets = character_data.get("character_sheets", [])
        char_by_name = {s.get("name", "").lower(): s for s in sheets}

        kf_index = {}
        for kf in keyframes.get("keyframes", []):
            kf_index[(kf.get("scene_id"), kf.get("shot_id"))] = kf

        anim_seqs = {}
        for part in animation_plan.get("parts", []):
            for seq in part.get("sequences", []):
                anim_seqs[(seq.get("scene_id"), seq.get("shot_id"))] = seq

        # RL state
        rl_state = rl_master.get_rl_state() if rl_master else {}
        composite = rl_rewards.get("composite", {})
        sub_rl = rl_rewards.get("sub_rl", {})

        scenes_output = []
        rendered_lines = []

        # Audio emotion hints
        audio_hints = {
            "timid": "timid flutes, soft tremolo strings",
            "determined": "building drums, brass entering, tempo rising",
            "heroic": "epic horns, full orchestra, triumphant swell",
            "fearful": "tremolo strings, heartbeat pulse, low drone",
            "angry": "aggressive percussion, distorted bass, staccato hits",
            "peaceful": "gentle piano, nature ambience, flowing strings",
            "doubtful": "uncertain woodwinds, sparse notes, hollow reverb",
            "resolved": "steady rhythm, warm brass, building confidence",
        }

        for scene in storyboard.get("scenes", []):
            scene_id = scene.get("scene_id", 0)
            location = scene.get("location", "")
            time_of_day = scene.get("time_of_day", "day")

            all_chars = set()
            for shot in scene.get("shots", []):
                for c in shot.get("characters_present", []):
                    all_chars.add(c)

            primary_char = next(iter(all_chars), "Unknown")
            primary_sheet = char_by_name.get(primary_char.lower(), {})
            primary_id = primary_sheet.get("character_id", "")
            current_stage = 1
            if char_agent and primary_id:
                current_stage = char_agent._current_stages.get(primary_id, 1)

            # ── Scene Header (RL-Enhanced) ──
            header = f"\n{'═' * 60}\n"
            header += f"SCENE {scene_id} – RL-Enhanced | {primary_char} Arc Stage {current_stage}\n"
            header += f"Location: {location} ({time_of_day})\n"
            if rl_state:
                header += (
                    f"🤖 RL State: Episode {rl_state.get('rl_episode', '?')}, "
                    f"Policy {rl_state.get('policy_version', '?')}\n"
                )
            header += f"{'═' * 60}\n"

            rendered_lines.append(header)
            scene_shots = []

            for shot in scene.get("shots", []):
                shot_id = shot.get("shot_id", 0)
                key = (scene_id, shot_id)
                duration = shot.get("duration_seconds", 3)

                # ── Character Evolution ──
                evolution_msgs = []
                char_rl_score = sub_rl.get("character", 0.5)
                for char_name in shot.get("characters_present", []):
                    cs = char_by_name.get(char_name.lower(), {})
                    cid = cs.get("character_id", "")
                    arc_stages = cs.get("arc_stages", [])
                    stage_num = char_agent._current_stages.get(cid, 1) if char_agent and cid else 1
                    current_trait, visual_change = "", ""
                    for s in arc_stages:
                        if s.get("stage") == stage_num:
                            current_trait = s.get("trait", "")
                            visual_change = s.get("visual_change", "")
                    evolution_msgs.append(
                        f"{char_name}: stage {stage_num} ({current_trait}), "
                        f"visual: {visual_change} (Sub-RL Score: {char_rl_score:.2f})"
                    )

                # ── Narration ──
                narration = shot.get("narration") or shot.get("dialogue") or ""
                action = shot.get("action", "")

                # ── Image + RL Action ──
                kf = kf_index.get(key, {})
                image_ref = kf.get("local_path", "Not generated")
                image_rl_action = ""
                if rl_master:
                    image_rl_action = rl_master.get_action_description("image")

                # ── Audio + RL Action ──
                expression = shot.get("expression", "neutral").lower()
                audio_desc = audio_hints.get(expression, f"mood: {expression}")
                audio_rl_action = ""
                if rl_master:
                    audio_rl_action = rl_master.get_action_description("audio")

                # ── Motion/Effects ──
                anim = anim_seqs.get(key, {})
                motion = anim.get("motion", {})
                effects = anim.get("effects", {})
                motion_desc = ""
                if isinstance(motion, dict):
                    motion_desc = f"{motion.get('camera', '')} — {motion.get('character_motion', '')}"
                effect_list = []
                if isinstance(effects, dict):
                    for cat in ["particles", "lighting", "special"]:
                        v = effects.get(cat)
                        if v:
                            if isinstance(v, list):
                                effect_list.append(f"{cat}: {', '.join(v)}")
                            else:
                                effect_list.append(f"{cat}: {v}")

                # ── RL Reward Preview ──
                coh = composite.get("coherence", 0.5)
                total_r = rl_rewards.get("total", 0.5)

                # ── Metadata ──
                metadata = {
                    "rl_episode": rl_state.get("rl_episode", 0),
                    "policy_version": rl_state.get("policy_version", "v1"),
                    "char_id": primary_id,
                    "arc_stage": current_stage,
                    "duration": f"{duration}s",
                    "suggested_next_action": (
                        rl_state.get("active_actions", [{}])[0].get("action_type", "none")
                        if rl_state.get("active_actions") else "none"
                    ),
                }

                # ── Build Shot Output ──
                shot_text = f"\n  Shot {shot_id} ({shot.get('shot_type', 'medium')}) — {duration}s\n"
                if evolution_msgs:
                    shot_text += f"  👤 Character Evolution: {'; '.join(evolution_msgs)}\n"
                if narration:
                    shot_text += f"  📖 Narration: \"{narration}\"\n"
                if action:
                    shot_text += f"  🎬 Action: {action}\n"
                shot_text += f"  🖼️  Image: [Nano Banana 2: {image_ref}]"
                if image_rl_action:
                    shot_text += f" + {image_rl_action}"
                shot_text += "\n"
                shot_text += f"  🔊 Audio: [{audio_desc}]"
                if audio_rl_action:
                    shot_text += f" + {audio_rl_action}"
                shot_text += "\n"
                if motion_desc or effect_list:
                    shot_text += f"  ✨ Motion/Effects: {motion_desc}"
                    if effect_list:
                        shot_text += f" + {' + '.join(effect_list)}"
                    shot_text += "\n"
                shot_text += f"  📊 RL Reward Preview: Coherence={coh:.2f}, Total={total_r:.3f}\n"
                shot_text += f"  📋 Metadata: {json.dumps(metadata)}\n"

                rendered_lines.append(shot_text)
                scene_shots.append({
                    "shot_id": shot_id,
                    "character_evolution": evolution_msgs,
                    "narration": narration,
                    "image_path": image_ref,
                    "audio": audio_desc,
                    "rl_reward_preview": {"coherence": coh, "total": total_r},
                    "metadata": metadata,
                })

            scenes_output.append({
                "scene_id": scene_id,
                "primary_character": primary_char,
                "arc_stage": current_stage,
                "rl_enhanced": True,
                "shots": scene_shots,
            })

        # ── Save ──
        full_text = "\n".join(rendered_lines)
        text_path = os.path.join(self.output_dir, "interleaved_output.txt")
        with open(text_path, "w") as f:
            f.write(full_text)

        json_path = os.path.join(self.output_dir, "scenes_data.json")
        with open(json_path, "w") as f:
            json.dump({"scenes": scenes_output, "rl_state": rl_state}, f, indent=2)

        self.gcs.upload_blob(text_path, "scenes/interleaved_output.txt")
        self.gcs.upload_blob(json_path, "scenes/scenes_data.json")

        self.log(f"RL-augmented rendering complete — {len(scenes_output)} scenes")
        print(full_text)

        return {"scenes": scenes_output, "interleaved_text": full_text, "output_path": text_path}
