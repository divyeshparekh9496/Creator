# Creator 🎬

A creative-director-style AI system that converts stories into **anime-style animated sequences** using **Gemini 3** and **Google Cloud**.

## Architecture

```
User Story → StoryAgent → StoryboardAgent → CharacterAgent → ImageAgent
                                                                  ↓
                          EditorAgent ← AudioAgent ← AnimationAgent
                               ↓
                        Final Anime Episode
```

### Agents

| Agent | Model | Purpose |
|-------|-------|---------|
| **StoryAgent** | `gemini-2.0-flash` | Narrative analysis → structured beats |
| **StoryboardAgent** | `gemini-2.0-flash` | Shot list with camera, action, dialogue |
| **CharacterAgent** | `gemini-3-pro-image-preview` | Character sheet generation (Nano Banana Pro) |
| **ImageAgent** | `gemini-3.1-flash-image-preview` | Keyframe images per shot (Nano Banana 2) |
| **AnimationAgent** | `gemini-2.0-flash` | Motion planning, transitions, timing |
| **AudioAgent** | `gemini-2.0-flash` | Dialogue, music, SFX cues |
| **EditorAgent** | `ffmpeg` | Video assembly + final merge |

## Quick Start

```bash
# 1. Clone and setup
git clone https://github.com/divyeshparekh9496/Creator.git
cd Creator

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure
cp .env.example .env
# Edit .env with your GOOGLE_API_KEY

# 4. Run
python main.py --story "A lone samurai walks through a cherry blossom forest at dawn"
```

## Usage

```bash
# From text
python main.py --story "Your story here"

# From file
python main.py --file story.txt

# Custom output directory
python main.py --story "..." --output data/my_anime

# With explicit API key
python main.py --story "..." --api-key YOUR_KEY
```

## Output Structure

```
data/output/
├── characters/          # Character sheet images
├── keyframes/           # Keyframe images per shot
├── animation/           # Animation plan JSON
├── audio/               # Audio plan JSON
├── parts/               # Rendered video parts
├── final/               # Merged final episode
├── pipeline_state.json  # Full pipeline state
└── assembly_manifest.json
```

## Tech Stack

- **Gemini 3** (Nano Banana 2 / Nano Banana Pro) — Image generation
- **Google GenAI SDK** — Model calls and interleaved output
- **Google Cloud Storage** — Asset storage
- **ffmpeg** — Video assembly
- **Python 3.10+**

## License

MIT
