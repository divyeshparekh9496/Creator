"""
CreatorPipeline — optimized with parallel execution, caching, and SSE progress callbacks.

Pipeline flow (parallel where possible):
  Story → Character → Storyboard ──┬──→ Image     ──┐
                                    ├──→ Animation  ──┤──→ RL → Scene → Assembly
                                    └──→ Audio     ──┘
"""
import os
import json
import asyncio
import concurrent.futures
from typing import Dict, Any, Optional, Callable

from src.utils.genai_client import GenAIClient
from src.utils.gcp_utils import GCPUtils
from src.utils.cache import SceneCache
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
    Optimized pipeline with:
    - Parallel execution of independent stages (Image/Animation/Audio)
    - Scene-level caching (skip unchanged stages)
    - Progress callbacks for SSE streaming
    - Retry/circuit breaker via GenAIClient
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        output_dir: str = DEFAULT_OUTPUT_DIR,
        on_progress: Optional[Callable] = None,
    ):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        self.on_progress = on_progress or (lambda *a, **kw: None)

        self.genai = GenAIClient(api_key=api_key)
        self.gcs = GCPUtils()
        self.cache = SceneCache(os.path.join(output_dir, "cache"))

        agent_kwargs = {"genai_client": self.genai, "gcs": self.gcs}

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
        self.rl_master = MasterRLAgent(
            genai_client=self.genai, gcs=self.gcs,
            output_dir=os.path.join(output_dir, "rl"),
        )

        self.state: Dict[str, Any] = {}
        self._executor = concurrent.futures.ThreadPoolExecutor(max_workers=3)

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

    def _emit(self, event: str, data: Any = None):
        """Send progress event to SSE stream."""
        self.on_progress(event, data)

    def _run_cached(self, stage: str, agent, input_data: Any) -> Dict:
        """Run agent with cache — skip if inputs unchanged."""
        cached = self.cache.get(stage, input_data)
        if cached:
            self._emit("stage_cached", {"stage": stage})
            return cached

        result = agent.run(input_data)
        self.cache.set(stage, input_data, result)
        return result

    def run_full(self, story_text: str) -> Dict[str, Any]:
        """Run the full pipeline with parallel stages and progress streaming."""
        self._emit("pipeline_start", {"stages": 10})

        # Stage 1: Story Analysis
        self._emit("stage_start", {"stage": "Story Analysis", "index": 1})
        story = self._run_cached("story", self.story_agent, story_text)
        self._save_state("story_analysis", story)
        self._emit("stage_done", {"stage": "Story Analysis", "index": 1, "data": story})

        # Stage 2: Character Development
        self._emit("stage_start", {"stage": "Character Dev", "index": 2})
        characters = self._run_cached("character", self.character_agent, story)
        self._save_state("character_data", characters)
        self._emit("stage_done", {"stage": "Character Dev", "index": 2, "data": {
            "count": len(characters.get("character_sheets", [])),
            "warnings": characters.get("incomplete_warnings", []),
        }})

        # Stage 3: RL Episode Start
        self._emit("stage_start", {"stage": "RL Start", "index": 3})
        episode = self.rl_master.start_episode()
        self._emit("stage_done", {"stage": "RL Start", "index": 3, "data": {
            "episode": episode.episode_id, "policy": self.rl_master.policy_version,
        }})

        # Stage 4: Storyboard
        self._emit("stage_start", {"stage": "Storyboard", "index": 4})
        storyboard_input = {
            **story,
            "character_arcs": characters.get("character_sheets", []),
            "consistency_notes": characters.get("consistency_notes", ""),
        }
        storyboard = self._run_cached("storyboard", self.storyboard_agent, storyboard_input)
        self._save_state("storyboard", storyboard)
        self._emit("stage_done", {"stage": "Storyboard", "index": 4, "data": {
            "scenes": len(storyboard.get("scenes", [])),
        }})

        # ── Stages 5/6/7: PARALLEL (Image + Animation + Audio) ──
        self._emit("stage_start", {"stage": "Keyframes + Animation + Audio (parallel)", "index": 5})

        image_input = {
            "storyboard": storyboard,
            "character_data": characters,
            "character_agent": self.character_agent,
        }
        anim_input = {"keyframes": {"keyframes": []}, "storyboard": storyboard}
        audio_input = {
            "animation_plan": {}, "storyboard": storyboard,
            "character_data": characters,
        }

        # Run in parallel threads
        future_image = self._executor.submit(self._run_cached, "image", self.image_agent, image_input)
        future_anim = self._executor.submit(self._run_cached, "animation", self.animation_agent, anim_input)
        future_audio = self._executor.submit(self._run_cached, "audio", self.audio_agent, audio_input)

        # Collect results
        keyframes = future_image.result()
        animation = future_anim.result()
        audio = future_audio.result()

        self._save_state("keyframes", keyframes)
        self._save_state("animation_plan", animation)
        self._save_state("audio_plan", audio)
        self._emit("stage_done", {"stage": "Parallel stages complete", "index": 7, "data": {
            "keyframes": len(keyframes.get("keyframes", [])),
        }})

        # Stage 8: RL Rewards
        self._emit("stage_start", {"stage": "RL Rewards", "index": 8})
        rewards = self.rl_master.compute_rewards(self.state)
        self._save_state("rl_rewards", rewards)
        episode.rewards.append(rewards)
        rl_actions = self.rl_master.select_actions(rewards)
        episode.actions.extend([a.to_dict() for a in rl_actions])
        self._emit("stage_done", {"stage": "RL Rewards", "index": 8, "data": rewards})

        # Stage 9: Scene Rendering
        self._emit("stage_start", {"stage": "Scene Render", "index": 9})
        scenes = self.scene_renderer.run({
            "storyboard": storyboard, "character_data": characters,
            "keyframes": keyframes, "animation_plan": animation,
            "audio_plan": audio, "story_analysis": story,
            "character_agent": self.character_agent,
            "rl_master": self.rl_master, "rl_rewards": rewards,
        })
        self._save_state("scene_rendering", {
            "scenes": scenes.get("scenes", []),
            "output_path": scenes.get("output_path", ""),
        })
        self._emit("stage_done", {"stage": "Scene Render", "index": 9})

        # Stage 10: Assembly
        self._emit("stage_start", {"stage": "Assembly", "index": 10})
        final = self.editor_agent.run({
            "keyframes": keyframes, "animation_plan": animation,
            "audio_plan": audio,
        })
        self._save_state("final_assembly", final)
        self._emit("stage_done", {"stage": "Assembly", "index": 10})

        # End RL episode
        self.rl_master.end_episode(episode)

        # Save evolution log
        evo_log = self.character_agent.get_evolution_log()
        if evo_log:
            evo_path = os.path.join(self.output_dir, "character_evolution_log.json")
            with open(evo_path, "w") as f:
                json.dump(evo_log, f, indent=2)

        self._emit("pipeline_complete", {
            "reward": rewards.get("total", 0),
            "policy": self.rl_master.policy_version,
            "episode": self.rl_master.episode_count,
        })

        return self.state

    def run_stage(self, stage_name: str, input_data: Any = None) -> Any:
        stages = {
            "story": self.story_agent, "character": self.character_agent,
            "storyboard": self.storyboard_agent, "image": self.image_agent,
            "animation": self.animation_agent, "audio": self.audio_agent,
            "scene": self.scene_renderer, "editor": self.editor_agent,
        }
        agent = stages.get(stage_name)
        if not agent:
            raise ValueError(f"Unknown stage: {stage_name}")
        result = agent.run(input_data)
        self._save_state(stage_name, result)
        return result

    def get_user_feedback(self, rating: int):
        if self.rl_master.episodes:
            episode = self.rl_master.episodes[-1]
            if episode.rewards:
                from src.rl.reward_system import RewardScore
                last_reward = episode.rewards[-1]
                composite = last_reward.get("composite", {})
                score = RewardScore(**{
                    k: v for k, v in composite.items()
                    if k in ["coherence", "creativity", "consistency", "emotional_impact", "technical_quality"]
                })
                score = self.rl_master.reward_evaluator.apply_user_feedback(score, rating)
                print(f"[RLHF] User rating: {rating}/5 → bonus: {score.user_bonus}")
