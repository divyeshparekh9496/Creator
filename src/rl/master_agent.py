"""
Master RL Agent — coordinates Sub-RL agents, manages policy, and drives self-improvement.

Inspired by:
- SAGE RL framework (arXiv:2512.17102): Hierarchical agent coordination
- ElegantRL: PPO-base policy optimization (lightweight DRL)
- Godot RL Agents: Animation/game simulation environments

The Master RL:
1. Aggregates sub-RL rewards into composite scores
2. Selects global actions (parameter tweaks) based on policy
3. Tracks episode history and policy evolution
4. Logs everything to GCS for retraining
"""
import os
import json
import time
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field

from src.rl.reward_system import (
    RewardScore, RLAction, RLEpisode, RewardEvaluator, REWARD_WEIGHTS
)
from src.rl.sub_agents import CharacterRL, VisualRL, AudioRL, SequenceRL
from src.utils.gcp_utils import GCPUtils
from src.utils.genai_client import GenAIClient
from src.config import MODEL_FLASH_TEXT


# ── Default RL Actions the Master can take ──
DEFAULT_ACTIONS = [
    RLAction("increase_drama", "drama_intensity", +0.20, "storyboard",
             "Boost drama for higher emotional impact"),
    RLAction("add_particles", "particle_density", +0.15, "image",
             "More particle effects for visual richness"),
    RLAction("deepen_arc", "arc_stages", +1, "character",
             "Add an extra arc stage for character depth"),
    RLAction("layer_audio", "sfx_layers", +1, "audio",
             "Add extra SFX layer for audio richness"),
    RLAction("smooth_transitions", "transition_type", 0, "animation",
             "Use dissolves/fades instead of hard cuts"),
    RLAction("boost_consistency", "reference_weight", +0.10, "image",
             "Increase character reference image weight"),
    RLAction("slow_build", "pacing", -0.15, "animation",
             "Slow down pacing for dramatic buildup"),
    RLAction("emotional_music", "music_intensity", +0.20, "audio",
             "Intensify background music for emotional peaks"),
]

POLICY_SELECTION_PROMPT = """You are an RL policy agent for anime production quality optimization.
Given the current reward scores and available actions, select the TOP 3 actions
that would most improve the total reward.

Current rewards:
{rewards}

Available actions:
{actions}

Learned patterns from history:
{patterns}

Return JSON:
{{
  "selected_actions": [
    {{"action_index": 0, "reasoning": "Why this action improves quality"}},
    {{"action_index": 1, "reasoning": "..."}},
    {{"action_index": 2, "reasoning": "..."}}
  ],
  "policy_notes": "Overall strategy for this episode"
}}

Return ONLY valid JSON."""


class MasterRLAgent:
    """
    Central RL Master Agent — oversees all sub-agents and drives self-improvement.

    Environment:
    - State: Current scene JSON (character arc, assets, user input)
    - Action Space: Parameter tweaks (drama +20%, particle density, arc depth, etc.)
    - Observation: Generated assets + metadata
    - Reward: Composite score from Sub-RL agents + user feedback

    Self-Learning Loop:
    1. Generate sequence → 2. Compute auto-rewards → 3. Solicit user rating
    4. Update policy → 5. Persist to GCS
    """

    def __init__(
        self,
        genai_client: Optional[GenAIClient] = None,
        gcs: Optional[GCPUtils] = None,
        output_dir: str = "data/output/rl",
    ):
        self.genai = genai_client or GenAIClient()
        self.gcs = gcs or GCPUtils()
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

        # Sub-RL agents
        self.character_rl = CharacterRL()
        self.visual_rl = VisualRL()
        self.audio_rl = AudioRL()
        self.sequence_rl = SequenceRL()

        # Reward evaluator
        self.reward_evaluator = RewardEvaluator(genai_client=self.genai, gcs=self.gcs)

        # Policy state
        self.policy_version = "v1"
        self.episode_count = 0
        self.episodes: List[RLEpisode] = []
        self.learned_patterns: List[str] = []
        self.active_actions: List[RLAction] = []

        # Load existing policy if available
        self._load_policy()

    def _log(self, msg: str):
        print(f"[MasterRL] {msg}")

    # ── Policy Management ──

    def _load_policy(self):
        """Load policy from disk if it exists."""
        policy_path = os.path.join(self.output_dir, "policy.json")
        if os.path.exists(policy_path):
            try:
                with open(policy_path, "r") as f:
                    data = json.load(f)
                self.policy_version = data.get("policy_version", "v1")
                self.episode_count = data.get("episode_count", 0)
                self.learned_patterns = data.get("learned_patterns", [])
                self._log(f"Policy loaded: {self.policy_version}, {self.episode_count} episodes")
            except Exception:
                pass

    def _save_policy(self):
        """Persist policy to disk and GCS."""
        policy_data = {
            "policy_version": self.policy_version,
            "episode_count": self.episode_count,
            "learned_patterns": self.learned_patterns,
            "reward_weights": REWARD_WEIGHTS,
            "last_updated": time.strftime("%Y-%m-%d %H:%M:%S"),
        }

        policy_path = os.path.join(self.output_dir, "policy.json")
        with open(policy_path, "w") as f:
            json.dump(policy_data, f, indent=2)

        self.gcs.upload_blob(policy_path, f"rl/policy_{self.policy_version}.json")
        self._log(f"Policy saved: {self.policy_version}")

    # ── Episode Management ──

    def start_episode(self) -> RLEpisode:
        """Start a new RL episode (one full pipeline run)."""
        self.episode_count += 1
        episode = RLEpisode(
            episode_id=self.episode_count,
            policy_version=self.policy_version,
        )
        self.episodes.append(episode)
        self._log(f"═══ RL Episode {episode.episode_id} started (policy {self.policy_version}) ═══")
        return episode

    def end_episode(self, episode: RLEpisode):
        """Close episode, compute final reward, update policy."""
        avg_reward = sum(r.get("total", 0) for r in episode.rewards) / max(len(episode.rewards), 1)
        episode.total_reward = avg_reward

        self._log(f"═══ Episode {episode.episode_id} complete — reward: {avg_reward:.3f} ═══")

        # Save episode log
        episode_path = os.path.join(
            self.output_dir,
            f"episode_{episode.episode_id:04d}.json"
        )
        with open(episode_path, "w") as f:
            json.dump(episode.to_dict(), f, indent=2)

        # Upload to GCS
        gcs_path = f"rl/episodes/episode_{episode.episode_id:04d}.json"
        self.gcs.upload_blob(episode_path, gcs_path)

        # Update policy
        self._update_policy(episode)
        self._save_policy()

    # ── Reward Computation ──

    def compute_rewards(self, pipeline_state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Compute comprehensive rewards from all sub-RL agents + auto-eval.
        Returns composite score with per-dimension breakdown.
        """
        self._log("Computing composite rewards...")

        # Sub-RL rewards
        char_data = pipeline_state.get("character_data", {})
        keyframes = pipeline_state.get("keyframes", {})
        animation = pipeline_state.get("animation_plan", {})
        audio = pipeline_state.get("audio_plan", {})

        char_reward = self.character_rl.compute_reward(char_data)
        visual_reward = self.visual_rl.compute_reward({
            "keyframes": keyframes.get("keyframes", []),
            "animation_plan": animation,
        })
        audio_reward = self.audio_rl.compute_reward({"audio_plan": audio})
        seq_reward = self.sequence_rl.compute_reward({"animation_plan": animation})

        # Auto-eval via Gemini (scene-level)
        scene_data = pipeline_state.get("scene_rendering", {})
        scenes = scene_data.get("scenes", [])
        auto_scores = []
        for scene in scenes[:3]:  # Limit to 3 scenes for cost
            score = self.reward_evaluator.evaluate_scene(scene)
            auto_scores.append(score)

        # Aggregate
        if auto_scores:
            avg_auto = RewardScore(
                coherence=sum(s.coherence for s in auto_scores) / len(auto_scores),
                creativity=sum(s.creativity for s in auto_scores) / len(auto_scores),
                consistency=sum(s.consistency for s in auto_scores) / len(auto_scores),
                emotional_impact=sum(s.emotional_impact for s in auto_scores) / len(auto_scores),
                technical_quality=sum(s.technical_quality for s in auto_scores) / len(auto_scores),
            )
        else:
            # Fallback: use sub-RL scores
            avg_auto = RewardScore(
                coherence=char_reward * 0.5 + seq_reward * 0.5,
                creativity=visual_reward * 0.6 + audio_reward * 0.4,
                consistency=visual_reward,
                emotional_impact=char_reward * 0.7 + audio_reward * 0.3,
                technical_quality=visual_reward * 0.5 + audio_reward * 0.5,
            )

        result = {
            "composite": avg_auto.to_dict(),
            "sub_rl": {
                "character": char_reward,
                "visual": visual_reward,
                "audio": audio_reward,
                "sequence": seq_reward,
            },
            "total": avg_auto.total,
        }

        self._log(f"  Composite reward: {avg_auto.total:.3f}")
        self._log(f"  Sub-RL: char={char_reward:.2f} vis={visual_reward:.2f} "
                   f"aud={audio_reward:.2f} seq={seq_reward:.2f}")

        return result

    # ── Action Selection ──

    def select_actions(self, rewards: Dict[str, Any]) -> List[RLAction]:
        """Use policy to select parameter tweaks based on current rewards."""
        self._log("Selecting RL actions based on policy...")

        actions_desc = "\n".join(
            f"  [{i}] {a.action_type}: {a.parameter} ({'+' if a.magnitude > 0 else ''}{a.magnitude}) "
            f"→ {a.target_agent} — {a.reasoning}"
            for i, a in enumerate(DEFAULT_ACTIONS)
        )

        patterns = "\n".join(self.learned_patterns[-5:]) if self.learned_patterns else "No history yet."

        prompt = POLICY_SELECTION_PROMPT.format(
            rewards=json.dumps(rewards, indent=2),
            actions=actions_desc,
            patterns=patterns,
        )

        try:
            result = self.genai.generate_json(
                prompt=prompt,
                model=MODEL_FLASH_TEXT,
            )

            selected = []
            for sel in result.get("selected_actions", []):
                idx = sel.get("action_index", 0)
                if 0 <= idx < len(DEFAULT_ACTIONS):
                    action = DEFAULT_ACTIONS[idx]
                    action.reasoning = sel.get("reasoning", action.reasoning)
                    selected.append(action)

            self.active_actions = selected
            for a in selected:
                self._log(f"  → Action: {a.action_type} ({a.parameter} {'+' if a.magnitude > 0 else ''}{a.magnitude})")

            return selected

        except Exception as e:
            self._log(f"  Action selection error: {e}")
            return DEFAULT_ACTIONS[:2]

    # ── Policy Update ──

    def _update_policy(self, episode: RLEpisode):
        """Update policy based on episode results (PPO-inspired simple update)."""
        reward = episode.total_reward

        # Learn high-reward patterns
        if reward > 0.7:
            actions_taken = [a.get("action_type", "") for a in episode.actions]
            pattern = (
                f"Episode {episode.episode_id}: High reward ({reward:.2f}) with actions: "
                f"{', '.join(actions_taken) if actions_taken else 'baseline'}"
            )
            self.learned_patterns.append(pattern)
            self._log(f"  📈 Learned pattern: {pattern}")

        # Increment policy version every 3 episodes
        if self.episode_count % 3 == 0:
            version_num = int(self.policy_version.replace("v", ""))
            self.policy_version = f"v{version_num + 1}"
            self._log(f"  🔄 Policy evolved to {self.policy_version}")

    # ── RL State for Interleaved Output ──

    def get_rl_state(self) -> Dict[str, Any]:
        """Get current RL state for interleaved output metadata."""
        return {
            "rl_episode": self.episode_count,
            "policy_version": self.policy_version,
            "active_actions": [a.to_dict() for a in self.active_actions],
            "learned_patterns_count": len(self.learned_patterns),
        }

    def get_action_description(self, agent_name: str) -> str:
        """Get RL action description for a specific agent (for interleaved output)."""
        for action in self.active_actions:
            if action.target_agent == agent_name:
                return (
                    f"RL Action: {action.action_type} "
                    f"({action.parameter} {'+' if action.magnitude > 0 else ''}{action.magnitude})"
                )
        return ""
