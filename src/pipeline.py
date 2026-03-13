"""
CreatorPipeline — enhanced orchestrator with character evolution state
and per-scene interleaved rendering.
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
from src.config import DEFAULT_OUTPUT_DIR


class CreatorPipeline:
    """
    Enhanced orchestrator — chains all Creator agents with character
    evolution state flowing across the entire pipeline.

    Pipeline:
      1. Story Analysis    →  beats, characters, setting
      2. Character Dev     →  deep arcs, visual evolution, emotion states
      3. Storyboarding     →  arc-driven shots with effects + motion hints
      4. Keyframe Gen      →  AnimeGANv2-styled frames with Animate Anyone motion
      5. Animation Plan    →  particle systems, effects, transitions
      6. Audio Plan        →  layered SFX, emotion-synced music
      7. Scene Rendering   →  per-scene interleaved output (NEW)
      8. Final Assembly    →  video parts + merged episode
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

        self.story_agent = StoryAgent(**agent_kwargs)
        self.storyboard_agent = StoryboardAgent(**agent_kwargs)
        self.character_agent = CharacterDevelopmentAgent(
            output_dir=os.path.join(output_dir, "characters"), **agent_kwargs
        )
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
        """Run the complete enhanced pipeline from story to final anime."""
        print("\n" + "═" * 60)
        print("  🎬  CREATOR PIPELINE — Enhanced with Character Development")
        print("═" * 60 + "\n")

        # Stage 1: Story Analysis
        print("━" * 50 + " Stage 1: Story Analysis")
        story = self.story_agent.run(story_text)
        self._save_state("story_analysis", story)

        # Stage 2: Character Development Engine
        print("━" * 50 + " Stage 2: Character Development")
        characters = self.character_agent.run(story)
        self._save_state("character_data", characters)

        # Stage 3: Arc-Driven Storyboard
        print("━" * 50 + " Stage 3: Storyboarding")
        # Merge story + character data for arc-driven scenes
        storyboard_input = {**story, "character_arcs": characters.get("character_sheets", [])}
        storyboard = self.storyboard_agent.run(storyboard_input)
        self._save_state("storyboard", storyboard)

        # Stage 4: Enhanced Keyframes
        print("━" * 50 + " Stage 4: Keyframe Generation")
        keyframes = self.image_agent.run({
            "storyboard": storyboard,
            "character_data": characters,
        })
        self._save_state("keyframes", keyframes)

        # Stage 5: Animation + Effects
        print("━" * 50 + " Stage 5: Animation Planning")
        animation = self.animation_agent.run({
            "keyframes": keyframes,
            "storyboard": storyboard,
        })
        self._save_state("animation_plan", animation)

        # Stage 6: Rich Audio
        print("━" * 50 + " Stage 6: Audio Planning")
        audio = self.audio_agent.run({
            "animation_plan": animation,
            "storyboard": storyboard,
            "character_data": characters,
        })
        self._save_state("audio_plan", audio)

        # Stage 7: Interleaved Scene Rendering (NEW)
        print("━" * 50 + " Stage 7: Scene Rendering")
        scenes = self.scene_renderer.run({
            "storyboard": storyboard,
            "character_data": characters,
            "keyframes": keyframes,
            "animation_plan": animation,
            "audio_plan": audio,
            "story_analysis": story,
        })
        self._save_state("scene_rendering", {
            "scenes": scenes.get("scenes", []),
            "output_path": scenes.get("output_path", ""),
        })

        # Stage 8: Final Assembly
        print("━" * 50 + " Stage 8: Final Assembly")
        final = self.editor_agent.run({
            "keyframes": keyframes,
            "animation_plan": animation,
            "audio_plan": audio,
        })
        self._save_state("final_assembly", final)

        print("\n" + "═" * 60)
        print("  ✅  ENHANCED PIPELINE COMPLETE")
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
