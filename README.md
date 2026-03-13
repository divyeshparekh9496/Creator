# Creator 🎬

A **creative-director-style AI system** that converts stories into **anime-style animated sequences** with **deep character development**, rich animations, dynamic sounds, and special effects.

Built with **Gemini 3.1**, **Nano Banana 2** (image gen), **Google GenAI SDK**, and **Google Cloud Storage**.

## Architecture

```
User Story → StoryAgent → CharacterDevelopmentAgent → StoryboardAgent
                                     ↓
            EditorAgent ← SceneRenderer ← AudioAgent ← AnimationAgent ← ImageAgent
                 ↓
          Final Anime Episode
```

### Agent Pipeline (8 Stages)

| # | Agent | Model | Purpose |
|---|-------|-------|---------|
| 1 | **StoryAgent** | `gemini-2.0-flash` | Narrative → beats, characters, setting |
| 2 | **CharacterDevelopmentAgent** | `gemini-3-pro-image-preview` | Deep arcs, visual evolution, emotion state |
| 3 | **StoryboardAgent** | `gemini-2.0-flash` | Arc-driven shots + effects + motion hints |
| 4 | **ImageAgent** | `gemini-3.1-flash-image-preview` | AnimeGANv2-styled keyframes + particles |
| 5 | **AnimationAgent** | `gemini-2.0-flash` | Animate Anyone motion + effects metadata |
| 6 | **AudioAgent** | `gemini-2.0-flash` | Layered SFX + emotion-synced music |
| 7 | **SceneRenderer** | — | Interleaved output per scene |
| 8 | **EditorAgent** | `ffmpeg` | Video assembly + final merge |

### Key Features

- **Character Development Engine** — Backstories, arc stages, visual evolution per scene
- **AnimeGANv2 Style** — Consistent anime style across all generated frames
- **Animate Anyone Motion** — Pose-guided smooth transitions and motion hints
- **FLUX.1 Consistency** — Visual anchoring across frames via reference images
- **Rich Audio** — Layered SFX (Audacity/LMMS patterns) synced to character emotions
- **Interleaved Output** — Per-scene stream of narration + image + audio + effects + metadata

### Open-Source Inspirations

| Feature | Reference | Integration |
|---------|-----------|-------------|
| Character Sheets | LlamaGenAI, dtoyoda10/anime-gen | JSON profiles for prompts |
| Animation | humanaigc/animate-anyone | Pose/motion guidance |
| Style Transfer | TachibanaYoshino/AnimeGANv2 | Style prefix on prompts |
| Consistency | FLUX.1 Kontext | Reference image anchoring |
| Audio/SFX | Audacity/LMMS patterns | Procedural descriptions |

## Quick Start

```bash
# 1. Clone and install
git clone https://github.com/divyeshparekh9496/Creator.git
cd Creator
pip install -r requirements.txt

# 2. Configure API key
cp .env.example .env
# Edit .env → set GOOGLE_API_KEY

# 3. Run
python main.py --story "A lone samurai walks through a cherry blossom forest at dawn"
```

## Output Structure

```
data/output/
├── characters/          # Character sheets + profiles JSON + arc data
├── keyframes/           # AnimeGANv2-styled keyframe images
├── animation/           # Animation plan with effects metadata
├── audio/               # Audio plan with layered SFX
├── scenes/              # Per-scene interleaved output
│   ├── interleaved_output.txt
│   └── scenes_data.json
├── parts/               # Rendered video parts
├── final/               # Merged final episode
└── pipeline_state.json
```

## Interleaved Output Format

Each scene produces:
```
Scene 2 — Forest Clearing (dusk)
  Shot 1 (close-up) — 5s
  📖 Narration: "For the first time, Akira felt the weight of her choice..."
  🎬 Action: Akira looks at the setting sun
  👤 Character Update: Akira — emotion: doubt and resolve — visual: scar deepens
  🖼️  Image: data/output/keyframes/scene02_shot01.png
  🎥 Motion: slow zoom-in — subtle breathing + wind-blown hair
  ✨ Effects: particles: cherry_blossoms + lighting: golden hour rim light
  🔊 Audio sync: emotion=contemplative
  📋 Metadata: {"scene":2, "shot":1, "duration":5, "char_arc":"doubt_resolve"}
```

## Tech Stack

- **Gemini 3.1** (Nano Banana 2 / Pro) — Image generation
- **Google GenAI SDK** — Model calls & interleaved output
- **Google Cloud Storage** — Asset storage
- **ffmpeg** — Video assembly
- **Python 3.10+**

## License

MIT
