"""
Sub-RL Agents — specialized reward evaluators per pipeline process.

Each sub-agent computes domain-specific rewards that feed into the Master RL.
Inspired by: SAGE hierarchical RL, ElegantRL (PPO sub-policies).
"""
from typing import Dict, Any


class SubRLAgent:
    """Base class for sub-RL agents."""

    def __init__(self, name: str, domain: str):
        self.name = name
        self.domain = domain
        self.reward_history: list = []

    def compute_reward(self, data: Dict[str, Any]) -> float:
        raise NotImplementedError

    def log_reward(self, scene_id: int, reward: float, details: str = ""):
        self.reward_history.append({
            "scene_id": scene_id,
            "reward": reward,
            "details": details,
        })


class CharacterRL(SubRLAgent):
    """
    Sub-RL for character development quality.
    Rewards: arc depth, multi-stage evolution, backstory coherence.
    """

    def __init__(self):
        super().__init__("CharacterRL", "character")

    def compute_reward(self, data: Dict[str, Any]) -> float:
        reward = 0.0
        sheets = data.get("character_sheets", [])

        for char in sheets:
            arc_stages = char.get("arc_stages", [])
            # Reward multi-stage arcs
            if len(arc_stages) >= 3:
                reward += 0.3
            elif len(arc_stages) >= 2:
                reward += 0.15

            # Reward backstory presence
            if char.get("backstory"):
                reward += 0.2

            # Reward style lock
            if char.get("style_lock"):
                reward += 0.1

            # Reward emotional range
            emotions = char.get("emotional_range", {})
            if len(emotions.get("per_scene", [])) >= 2:
                reward += 0.2

            # Penalize incomplete fields
            incomplete = char.get("incomplete_fields", [])
            reward -= len(incomplete) * 0.1

        # Normalize to 0-1
        num_chars = max(len(sheets), 1)
        score = min(1.0, max(0.0, reward / num_chars))

        self.log_reward(0, score, f"{num_chars} characters evaluated")
        return score


class VisualRL(SubRLAgent):
    """
    Sub-RL for visual/animation quality.
    Rewards: Animate Anyone motion, particle effects, consistency protocol usage.
    """

    def __init__(self):
        super().__init__("VisualRL", "visual")

    def compute_reward(self, data: Dict[str, Any]) -> float:
        reward = 0.0
        keyframes = data.get("keyframes", [])
        animation = data.get("animation_plan", {})

        # Reward keyframe generation success
        generated = sum(1 for kf in keyframes if kf.get("local_path"))
        total = max(len(keyframes), 1)
        reward += 0.3 * (generated / total)

        # Reward effects usage
        for kf in keyframes:
            effects = kf.get("effects", [])
            if effects:
                reward += 0.05 * min(len(effects), 3)

        # Reward animation richness
        parts = animation.get("parts", [])
        for part in parts:
            for seq in part.get("sequences", []):
                motion = seq.get("motion", {})
                if isinstance(motion, dict) and motion.get("character_motion"):
                    reward += 0.05
                effects = seq.get("effects", {})
                if isinstance(effects, dict):
                    if effects.get("particles"):
                        reward += 0.05
                    if effects.get("lighting"):
                        reward += 0.03

        # Reward consistency protocol
        for kf in keyframes:
            if kf.get("consistency_blocks"):
                reward += 0.05

        score = min(1.0, max(0.0, reward))
        self.log_reward(0, score, f"{generated}/{total} keyframes")
        return score


class AudioRL(SubRLAgent):
    """
    Sub-RL for audio quality.
    Rewards: layered SFX, emotion sync, dynamic changes, instrument detail.
    """

    def __init__(self):
        super().__init__("AudioRL", "audio")

    def compute_reward(self, data: Dict[str, Any]) -> float:
        reward = 0.0
        audio_plan = data.get("audio_plan", {})
        tracks = audio_plan.get("tracks", [])

        for track in tracks:
            elements = track.get("audio_elements", [])
            for elem in elements:
                # Reward layered audio
                layers = elem.get("layers", [])
                reward += 0.05 * min(len(layers), 3)

                # Reward emotion sync
                if elem.get("emotion_sync"):
                    reward += 0.05

            # Reward detailed BGM
            bgm = track.get("background_music", {})
            if bgm.get("instruments"):
                reward += 0.1
            if bgm.get("dynamic_changes"):
                reward += 0.1 * min(len(bgm["dynamic_changes"]), 3)

            # Reward emotion map
            if track.get("emotion_map"):
                reward += 0.1

        score = min(1.0, max(0.0, reward))
        self.log_reward(0, score, f"{len(tracks)} tracks evaluated")
        return score


class SequenceRL(SubRLAgent):
    """
    Sub-RL for sequence/mergeability quality.
    Rewards: transition smoothness, part structure, duration balance.
    """

    def __init__(self):
        super().__init__("SequenceRL", "sequence")

    def compute_reward(self, data: Dict[str, Any]) -> float:
        reward = 0.0
        animation = data.get("animation_plan", {})
        parts = animation.get("parts", [])

        # Reward having multiple parts
        if len(parts) >= 2:
            reward += 0.2
        if len(parts) >= 3:
            reward += 0.1

        # Reward smooth transitions
        for part in parts:
            for seq in part.get("sequences", []):
                t_in = seq.get("transition_in", "cut")
                t_out = seq.get("transition_out", "cut")
                smooth_transitions = {"dissolve", "fade-in", "fade-out", "crossfade", "zoom-blur"}
                if t_in in smooth_transitions:
                    reward += 0.05
                if t_out in smooth_transitions:
                    reward += 0.05

        # Reward duration balance
        durations = []
        for part in parts:
            part_dur = sum(
                s.get("duration_seconds", 3) for s in part.get("sequences", [])
            )
            durations.append(part_dur)

        if durations:
            avg = sum(durations) / len(durations)
            variance = sum((d - avg) ** 2 for d in durations) / len(durations)
            if variance < 50:  # Balanced parts
                reward += 0.2

        score = min(1.0, max(0.0, reward))
        self.log_reward(0, score, f"{len(parts)} parts evaluated")
        return score
