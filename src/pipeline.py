"""
CreatorPipeline — orchestrates all agents in sequence to produce anime.
"""
import os
import json
from typing import Dict, Any, Optional

from src.utils.genai_client import GenAIClient
from src.utils.gcp_utils import GCPUtils
from src.agents.story_agent import StoryAgent
from src.agents.storyboard_agent import StoryboardAgent
from src.agents.character_agent import CharacterAgent
from src.agents.image_agent import ImageAgent
from src.agents.animation_agent import AnimationAgent
from src.agents.audio_agent import AudioAgent
from src.agents.editor_agent import EditorAgent
from src.config import DEFAULT_OUTPUT_DIR


class CreatorPipeline:
    """
    Main orchestrator that chains all Creator agents.

    Pipeline stages:
      1. Story Analysis    →  structured beats, characters, setting
      2. Storyboarding     →  shot list per scene
      3. Character Design  →  character sheet images
      4. Keyframe Gen      →  anime keyframe images per shot
      5. Animation Plan    →  timing, transitions, parts
      6. Audio Plan        →  dialogue, music, SFX cues
      7. Final Assembly    →  rendered video parts + merged episode
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        output_dir: str = DEFAULT_OUTPUT_DIR,
    ):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

        # Shared dependencies
        self.genai = GenAIClient(api_key=api_key)
        self.gcs = GCPUtils()

        # Initialize all agents with shared deps
        agent_kwargs = {"genai_client": self.genai, "gcs": self.gcs}

        self.story_agent = StoryAgent(**agent_kwargs)
        self.storyboard_agent = StoryboardAgent(**agent_kwargs)
        self.character_agent = CharacterAgent(
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
        self.editor_agent = EditorAgent(
            output_dir=output_dir, **agent_kwargs
        )

        # Pipeline state
        self.state: Dict[str, Any] = {}

    def _save_state(self, stage: str, data: Any):
        """Persist pipeline state to disk after each stage."""
        self.state[stage] = data
        state_path = os.path.join(self.output_dir, "pipeline_state.json")

        # Convert non-serializable objects
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
        """Run the complete pipeline from story to final anime."""
        print("\n" + "=" * 60)
        print("  🎬  CREATOR PIPELINE — Full Run")
        print("=" * 60 + "\n")

        # Stage 1: Story Analysis
        print("━" * 40)
        story = self.story_agent.run(story_text)
        self._save_state("story_analysis", story)

        # Stage 2: Storyboard
        print("━" * 40)
        storyboard = self.storyboard_agent.run(story)
        self._save_state("storyboard", storyboard)

        # Stage 3: Character Design
        print("━" * 40)
        characters = self.character_agent.run(story)
        self._save_state("character_data", characters)

        # Stage 4: Keyframe Generation
        print("━" * 40)
        keyframes = self.image_agent.run({
            "storyboard": storyboard,
            "character_data": characters,
        })
        self._save_state("keyframes", keyframes)

        # Stage 5: Animation Planning
        print("━" * 40)
        animation = self.animation_agent.run({
            "keyframes": keyframes,
            "storyboard": storyboard,
        })
        self._save_state("animation_plan", animation)

        # Stage 6: Audio Planning
        print("━" * 40)
        audio = self.audio_agent.run({
            "animation_plan": animation,
            "storyboard": storyboard,
        })
        self._save_state("audio_plan", audio)

        # Stage 7: Final Assembly
        print("━" * 40)
        final = self.editor_agent.run({
            "keyframes": keyframes,
            "animation_plan": animation,
            "audio_plan": audio,
        })
        self._save_state("final_assembly", final)

        print("\n" + "=" * 60)
        print("  ✅  PIPELINE COMPLETE")
        print("=" * 60 + "\n")

        return self.state

    def run_stage(self, stage_name: str, input_data: Any = None) -> Any:
        """Run a single pipeline stage (for debugging or partial runs)."""
        stages = {
            "story": self.story_agent,
            "storyboard": self.storyboard_agent,
            "character": self.character_agent,
            "image": self.image_agent,
            "animation": self.animation_agent,
            "audio": self.audio_agent,
            "editor": self.editor_agent,
        }
        agent = stages.get(stage_name)
        if not agent:
            raise ValueError(f"Unknown stage: {stage_name}. Options: {list(stages.keys())}")

        result = agent.run(input_data)
        self._save_state(stage_name, result)
        return result
