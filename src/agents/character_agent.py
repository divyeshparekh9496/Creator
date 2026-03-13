"""
CharacterDevelopmentAgent — Enhancement #1: Character Development Engine.

Dedicated sub-agent that activates BEFORE storyboard generation and persists
ACROSS all scenes. Produces and tracks character sheets with arc stages,
visual evolution, style locks, and zero-hallucination safeguards.

Open-source references:
- LlamaGenAI/LlamaGen, dtoyoda10/anime-gen: JSON character sheet format
- Animate Anyone (humanaigc): Pose-guided visual consistency
- AnimeGANv2 (TachibanaYoshino): Style anchors in every prompt
- FLUX.1 Kontext: Embedding consistency for visual locking
"""
import os
import json
from typing import Dict, Any, List, Optional
from PIL import Image

from src.agents.base_agent import BaseAgent
from src.config import MODEL_PRO_IMAGE, MODEL_FLASH_TEXT, DEFAULT_ASPECT_RATIO, DEFAULT_IMAGE_SIZE


CHARACTER_SHEET_SYSTEM_PROMPT = """You are an anime character development specialist.
For EVERY named character in the story, create a production-ready character sheet.

ZERO HALLUCINATION RULE:
- Base ALL character details on the explicit story input.
- If character details are missing, set "incomplete_fields" with what you need.
- Never invent arcs not supported by the story beats.
- Track EVERY change in JSON metadata.

Return a JSON object with this EXACT structure:
{
  "characters": [
    {
      "character_id": "unique_snake_case_id",
      "name": "Character Name",
      "role": "protagonist/antagonist/sidekick/supporting",
      "initial_state": {
        "personality": ["trait1", "trait2", "trait3"],
        "visual_traits": ["slender build", "wide eyes", "specific features"],
        "skills": ["skill1 (level)", "skill2"],
        "motivations": ["primary goal", "secondary goal"],
        "flaws": ["flaw1", "flaw2"]
      },
      "backstory": "2-3 sentence backstory grounded in the story",
      "arc_stages": [
        {"stage": 1, "trait": "initial_trait", "visual_change": "specific visual for this stage"},
        {"stage": 2, "trait": "mid_trait", "visual_change": "what changes visually"},
        {"stage": 3, "trait": "final_trait", "visual_change": "final visual state"}
      ],
      "style_lock": "anime_[type]: [hair], [eyes], [distinctive visual anchors]",
      "voice_style": "tone description for audio agent",
      "emotional_range": {
        "default": "baseline emotion",
        "per_scene": [
          {"scene_id": 1, "emotion": "emotion_name", "intensity": 0.7}
        ]
      },
      "relationships": [
        {"with": "Other Character", "type": "relationship_type", "evolution": "start→end"}
      ],
      "incomplete_fields": []
    }
  ],
  "art_style": "AnimeGANv2 style: [specific style description]",
  "consistency_notes": "Key visual anchors that must persist across ALL frames"
}

Return ONLY valid JSON. Create sheets for ALL named characters (max 5).
If any character lacks sufficient story detail, list missing fields in "incomplete_fields"."""


class CharacterDevelopmentAgent(BaseAgent):
    """
    Enhancement #1: Character Development Engine.

    Activates BEFORE storyboard generation. Persists ACROSS all scenes.

    Core features:
    - Character sheet generation with exact JSON format
    - Arc stage tracking with visual evolution per scene
    - Style lock anchors for visual consistency protocol
    - Zero-hallucination safeguards (flags incomplete data)
    - Evolution output: "Character [name] evolution: [trait] → [next], visual: [change]"
    """

    def __init__(self, output_dir: str = "data/output/characters", **kwargs):
        super().__init__(name="CharacterDevelopmentAgent", **kwargs)
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

        # Persistent state across scenes
        self._sheets: Dict[str, Dict] = {}       # character_id → sheet
        self._current_stages: Dict[str, int] = {} # character_id → current arc stage
        self._evolution_log: List[Dict] = []       # chronological evolution entries

    @property
    def sheets(self) -> Dict[str, Dict]:
        return self._sheets

    def run(self, story_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Phase 1: Generate character sheets from story analysis.
        Runs BEFORE storyboard generation.
        """
        self.log("═══ Character Development Engine: Generating Sheets ═══")

        prompt = (
            "Create production-ready character sheets for ALL named characters:\n\n"
            f"{json.dumps(story_analysis, indent=2)}"
        )

        profiles = self.genai.generate_json(
            prompt=prompt,
            model=MODEL_FLASH_TEXT,
            system_instruction=CHARACTER_SHEET_SYSTEM_PROMPT,
        )

        characters = profiles.get("characters", [])
        style = profiles.get("art_style", "AnimeGANv2 style: cel-shaded, high-contrast")

        # Zero-hallucination check
        incomplete_chars = []
        for char in characters:
            missing = char.get("incomplete_fields", [])
            if missing:
                incomplete_chars.append(
                    f"Character '{char.get('name')}' sheet incomplete. "
                    f"Need: {', '.join(missing)}"
                )
        if incomplete_chars:
            self.log("⚠️  INCOMPLETE CHARACTER DATA:")
            for msg in incomplete_chars:
                self.log(f"   {msg}")

        # Store sheets and initialize tracking
        sheets_output = []
        for char in characters:
            char_id = char.get("character_id", char.get("name", "unknown").lower().replace(" ", "_"))
            char["character_id"] = char_id
            self._sheets[char_id] = char
            self._current_stages[char_id] = 1  # Start at stage 1

            name = char.get("name", "Unknown")
            arc_stages = char.get("arc_stages", [])
            style_lock = char.get("style_lock", "")

            self.log(f"  📋 Sheet created: {name} ({char_id})")
            self.log(f"     Role: {char.get('role')}")
            self.log(f"     Arc: {' → '.join(s.get('trait', '') for s in arc_stages)}")
            self.log(f"     Style lock: {style_lock}")

            # Generate reference image
            sheet_prompt = self._build_sheet_prompt(char, style)
            local_path, gcs_path = None, None

            try:
                image = self.genai.generate_image(
                    prompt=sheet_prompt,
                    model=MODEL_PRO_IMAGE,
                    aspect_ratio=DEFAULT_ASPECT_RATIO,
                    image_size=DEFAULT_IMAGE_SIZE,
                )
                if image:
                    local_path = os.path.join(self.output_dir, f"{char_id}_sheet.png")
                    image.save(local_path)
                    gcs_path = f"characters/{char_id}/sheet.png"
                    self.gcs.upload_blob(local_path, gcs_path)
                    self.log(f"     Image saved: {local_path}")
            except Exception as e:
                self.log(f"     Image error: {e}")

            sheets_output.append({
                **char,
                "local_path": local_path,
                "gcs_path": gcs_path,
            })

        # Save all sheets to JSON
        profiles_path = os.path.join(self.output_dir, "character_profiles.json")
        with open(profiles_path, "w") as f:
            json.dump({
                "characters": characters,
                "art_style": style,
                "consistency_notes": profiles.get("consistency_notes", ""),
            }, f, indent=2)
        self.gcs.upload_blob(profiles_path, "characters/profiles.json")

        self.log(f"═══ Character Development complete — {len(sheets_output)} sheets ═══")
        return {
            "character_sheets": sheets_output,
            "style": style,
            "consistency_notes": profiles.get("consistency_notes", ""),
            "incomplete_warnings": incomplete_chars,
        }

    def get_visual_consistency_block(self, char_id: str) -> str:
        """
        Visual Consistency Protocol — returns the mandatory prompt block
        that MUST be included in every image generation call.

        Format:
          "Character: [name] from sheet [character_id]"
          "Current arc stage: [stage] visual traits: [changes]"
          "Style anchor: [style_lock]"
        """
        sheet = self._sheets.get(char_id)
        if not sheet:
            return ""

        name = sheet.get("name", "Unknown")
        stage_num = self._current_stages.get(char_id, 1)
        style_lock = sheet.get("style_lock", "")

        # Get current stage visual traits
        arc_stages = sheet.get("arc_stages", [])
        visual_traits = ""
        trait = ""
        for s in arc_stages:
            if s.get("stage") == stage_num:
                visual_traits = s.get("visual_change", "")
                trait = s.get("trait", "")
                break

        return (
            f"Character: {name} from sheet {char_id}, "
            f"Current arc stage: {stage_num} ({trait}) "
            f"visual traits: {visual_traits}, "
            f"Style anchor: {style_lock}"
        )

    def evolve_character(self, char_id: str, scene_id: int) -> str:
        """
        Advance character to next arc stage and return evolution description.
        Output format: "Character [name] evolution: [trait] → [next], visual: [change]"
        """
        sheet = self._sheets.get(char_id)
        if not sheet:
            return ""

        name = sheet.get("name", "Unknown")
        current_stage = self._current_stages.get(char_id, 1)
        arc_stages = sheet.get("arc_stages", [])

        # Find current and next
        current_trait, current_visual = "", ""
        next_trait, next_visual = "", ""

        for s in arc_stages:
            if s.get("stage") == current_stage:
                current_trait = s.get("trait", "")
                current_visual = s.get("visual_change", "")
            if s.get("stage") == current_stage + 1:
                next_trait = s.get("trait", "")
                next_visual = s.get("visual_change", "")

        if next_trait:
            self._current_stages[char_id] = current_stage + 1
            evolution_msg = (
                f"Character {name} evolution: {current_trait} → {next_trait}, "
                f"visual: {next_visual}"
            )
        else:
            evolution_msg = f"Character {name}: at final arc stage ({current_trait})"

        # Log evolution
        self._evolution_log.append({
            "character_id": char_id,
            "scene_id": scene_id,
            "from_stage": current_stage,
            "to_stage": self._current_stages.get(char_id, current_stage),
            "evolution": evolution_msg,
        })

        self.log(f"  🔄 {evolution_msg}")
        return evolution_msg

    def get_scene_emotion(self, char_id: str, scene_id: int) -> Dict[str, Any]:
        """Get character's emotional state for a specific scene."""
        sheet = self._sheets.get(char_id)
        if not sheet:
            return {"emotion": "neutral", "intensity": 0.5}

        emotions = sheet.get("emotional_range", {})
        for e in emotions.get("per_scene", []):
            if e.get("scene_id") == scene_id:
                return e
        return {"emotion": emotions.get("default", "neutral"), "intensity": 0.5}

    def get_evolution_log(self) -> List[Dict]:
        """Return full chronological evolution log."""
        return self._evolution_log

    def _build_sheet_prompt(self, char: Dict, style: str) -> str:
        name = char.get("name", "Unknown")
        role = char.get("role", "character")
        backstory = char.get("backstory", "")
        personality = ", ".join(char.get("initial_state", {}).get("personality", []))
        visual_traits = ", ".join(char.get("initial_state", {}).get("visual_traits", []))
        style_lock = char.get("style_lock", "")

        # Arc stages visual progression
        arc_visuals = []
        for s in char.get("arc_stages", []):
            arc_visuals.append(f"Stage {s.get('stage')}: {s.get('visual_change', '')}")

        return (
            f"AnimeGANv2 style character sheet. "
            f"Character: {name} from sheet {char.get('character_id')}. "
            f"Role: {role}. Backstory: {backstory}. "
            f"Personality: {personality}. Visual: {visual_traits}. "
            f"Style anchor: {style_lock}. "
            f"Art style: {style}. "
            f"Show THREE poses reflecting arc progression: "
            f"{'; '.join(arc_visuals)}. "
            f"Include color palette swatches. "
            f"FLUX.1 consistency: exact proportions across all poses. "
            f"Professional anime production quality, clean white background."
        )
