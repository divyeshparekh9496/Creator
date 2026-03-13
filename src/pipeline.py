"""
CreatorPipeline — enhanced with RL Self-Improvement Agent (Enhancement #2).

The Master RL Agent:
- Starts an episode per pipeline run
- Selects parameter tweaks via policy
- Computes composite rewards from Sub-RL agents
- Persists learning to GCS
- Augments interleaved output with RL metadata
"""
import os
import json
from typing import Dict, Any, Optional

from src.utils.genai_client import GenAIClient
from src.utils.gcp_utils import GCPUtils
from src.agents.story_agent import StoryAgent
from src.agents.storyboard_agent import StoryboardAgent
from src.agents.character_agent import CharacterDevelopmentAgent
from src.agents.image_agent import ImageAgent
from src.agents.animation_agent import AnimationAgent
from src.agents.audio_agent import AudioAgent
from src.agents.scene_renderer import SceneRenderer
from src.agents.editor_agent import EditorAgent
from src.rl.master_agent import MasterRLAgent
from src.config import DEFAULT_OUTPUT_DIR


class CreatorPipeline:
    """
    Full Creator pipeline with:
    - Enhancement #1: Character Development Engine
    - Enhancement #2: RL Self-Improvement Agent

    Pipeline (10 stages):
    1. Story Analysis
    2. Character Development (sheets, arcs, style locks)
    3. RL Episode Start + Action Selection
    4. Arc-Driven Storyboard
    5. Keyframe Gen (Visual Consistency Protocol)
    6. Animation + Effects
    7. Rich Audio (emotion-synced)
    8. Interleaved Scene Rendering (RL-augmented)
    9. RL Reward Computation + Policy Update
    10. Final Assembly
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        output_dir: str = DEFAULT_OUTPUT_DIR,
    ):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

        self.genai = GenAIClient(api_key=api_key)
        self.gcs = GCPUtils()

        agent_kwargs = {"genai_client": self.genai, "gcs": self.gcs}

        # Core agents
        self.story_agent = StoryAgent(**agent_kwargs)
        self.character_agent = CharacterDevelopmentAgent(
            output_dir=os.path.join(output_dir, "characters"), **agent_kwargs
        )
        self.storyboard_agent = StoryboardAgent(**agent_kwargs)
        self.image_agent = ImageAgent(
            output_dir=os.path.join(output_dir, "keyframes"), **agent_kwargs
        )
        self.animation_agent = AnimationAgent(
            output_dir=os.path.join(output_dir, "animation"), **agent_kwargs
        )
        self.audio_agent = AudioAgent(
            output_dir=os.path.join(output_dir, "audio"), **agent_kwargs
        )
        self.scene_renderer = SceneRenderer(
            output_dir=os.path.join(output_dir, "scenes"), **agent_kwargs
        )
        self.editor_agent = EditorAgent(
            output_dir=output_dir, **agent_kwargs
        )

        # RL Master Agent
        self.rl_master = MasterRLAgent(
            genai_client=self.genai,
            gcs=self.gcs,
            output_dir=os.path.join(output_dir, "rl"),
        )

        self.state: Dict[str, Any] = {}

    def _save_state(self, stage: str, data: Any):
        self.state[stage] = data
        state_path = os.path.join(self.output_dir, "pipeline_state.json")
        serializable = {}
        for k, v in self.state.items():
            try:
                json.dumps(v)
                serializable[k] = v
            except TypeError:
                serializable[k] = str(v)
        with open(state_path, "w") as f:
            json.dump(serializable, f, indent=2)

    def run_full(self, story_text: str) -> Dict[str, Any]:
        """Run the full RL-enhanced pipeline."""
        print("\n" + "═" * 60)
        print("  🎬  CREATOR PIPELINE — RL Self-Improvement Engine")
        print("═" * 60 + "\n")

        # ── Stage 1: Story Analysis ──
        print("━" * 50 + " Stage 1: Story Analysis")
        story = self.story_agent.run(story_text)
        self._save_state("story_analysis", story)

        # ── Stage 2: Character Development Engine ──
        print("━" * 50 + " Stage 2: Character Development")
        characters = self.character_agent.run(story)
        self._save_state("character_data", characters)

        warnings = characters.get("incomplete_warnings", [])
        if warnings:
            print("\n⚠️  CHARACTER DATA WARNINGS:")
            for w in warnings:
                print(f"   {w}")

        # ── Stage 3: RL Episode Start ──
        print("━" * 50 + " Stage 3: RL Episode Start")
        episode = self.rl_master.start_episode()
        episode.states.append({"stage": "init", "story_title": story.get("title", "")})

        # ── Stage 4: Arc-Driven Storyboard ──
        print("━" * 50 + " Stage 4: Storyboarding")
        storyboard_input = {
            **story,
            "character_arcs": characters.get("character_sheets", []),
            "consistency_notes": characters.get("consistency_notes", ""),
        }
        storyboard = self.storyboard_agent.run(storyboard_input)
        self._save_state("storyboard", storyboard)

        # ── Stage 5: Keyframes (Visual Consistency Protocol) ──
        print("━" * 50 + " Stage 5: Keyframe Generation")
        keyframes = self.image_agent.run({
            "storyboard": storyboard,
            "character_data": characters,
            "character_agent": self.character_agent,
        })
        self._save_state("keyframes", keyframes)

        # ── Stage 6: Animation + Effects ──
        print("━" * 50 + " Stage 6: Animation Planning")
        animation = self.animation_agent.run({
            "keyframes": keyframes,
            "storyboard": storyboard,
        })
        self._save_state("animation_plan", animation)

        # ── Stage 7: Rich Audio ──
        print("━" * 50 + " Stage 7: Audio Planning")
        audio = self.audio_agent.run({
            "animation_plan": animation,
            "storyboard": storyboard,
            "character_data": characters,
        })
        self._save_state("audio_plan", audio)

        # ── Stage 8: RL Reward Computation ──
        print("━" * 50 + " Stage 8: RL Reward Computation")
        rewards = self.rl_master.compute_rewards(self.state)
        self._save_state("rl_rewards", rewards)
        episode.rewards.append(rewards)

        # Select actions for next iteration
        rl_actions = self.rl_master.select_actions(rewards)
        episode.actions.extend([a.to_dict() for a in rl_actions])

        # ── Stage 9: Interleaved Scene Rendering (RL-augmented) ──
        print("━" * 50 + " Stage 9: Scene Rendering (RL-Augmented)")
        scenes = self.scene_renderer.run({
            "storyboard": storyboard,
            "character_data": characters,
            "keyframes": keyframes,
            "animation_plan": animation,
            "audio_plan": audio,
            "story_analysis": story,
            "character_agent": self.character_agent,
            "rl_master": self.rl_master,
            "rl_rewards": rewards,
        })
        self._save_state("scene_rendering", {
            "scenes": scenes.get("scenes", []),
            "output_path": scenes.get("output_path", ""),
        })

        # ── Stage 10: Final Assembly ──
        print("━" * 50 + " Stage 10: Final Assembly")
        final = self.editor_agent.run({
            "keyframes": keyframes,
            "animation_plan": animation,
            "audio_plan": audio,
        })
        self._save_state("final_assembly", final)

        # ── RL Episode End ──
        print("━" * 50 + " RL: Episode Complete")
        self.rl_master.end_episode(episode)

        # Save evolution log
        evo_log = self.character_agent.get_evolution_log()
        if evo_log:
            evo_path = os.path.join(self.output_dir, "character_evolution_log.json")
            with open(evo_path, "w") as f:
                json.dump(evo_log, f, indent=2)

        print("\n" + "═" * 60)
        print(f"  ✅  PIPELINE COMPLETE — RL Reward: {rewards.get('total', 0):.3f}")
        print(f"  📈  Policy: {self.rl_master.policy_version} | Episode: {self.rl_master.episode_count}")
        print("═" * 60 + "\n")

        return self.state

    def run_stage(self, stage_name: str, input_data: Any = None) -> Any:
        stages = {
            "story": self.story_agent,
            "character": self.character_agent,
            "storyboard": self.storyboard_agent,
            "image": self.image_agent,
            "animation": self.animation_agent,
            "audio": self.audio_agent,
            "scene": self.scene_renderer,
            "editor": self.editor_agent,
        }
        agent = stages.get(stage_name)
        if not agent:
            raise ValueError(f"Unknown stage: {stage_name}. Options: {list(stages.keys())}")
        result = agent.run(input_data)
        self._save_state(stage_name, result)
        return result

    def get_user_feedback(self, rating: int):
        """Accept user feedback (1-5) to feed into RLHF."""
        if self.rl_master.episodes:
            episode = self.rl_master.episodes[-1]
            if episode.rewards:
                from src.rl.reward_system import RewardScore
                last_reward = episode.rewards[-1]
                score = RewardScore(**{
                    k: v for k, v in last_reward.get("composite", {}).items()
                    if k in ["coherence", "creativity", "consistency", "emotional_impact", "technical_quality"]
                })
                score = self.rl_master.reward_evaluator.apply_user_feedback(score, rating)
                print(f"[RLHF] User rating: {rating}/5 → bonus: {score.user_bonus}")
