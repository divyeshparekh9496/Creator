# Creator 🎬

A **self-evolving creative-director AI** that converts stories into **anime-style animated sequences** with deep character development, rich effects, and RL-driven self-improvement.

Built with **Gemini 3.1**, **Nano Banana 2**, **Google GenAI SDK**, **Google Cloud Storage**, and **SAGE-inspired RL**.

## Architecture

```
User Story → StoryAgent → CharacterDevelopmentAgent → [RL Episode Start]
                                     ↓
StoryboardAgent → ImageAgent → AnimationAgent → AudioAgent
                                     ↓
               [RL Reward Computation] → SceneRenderer → EditorAgent
                                     ↓
                           [RL Policy Update] → Final Anime
```

### Pipeline (10 Stages)

| # | Stage | Agent/Component | Purpose |
|---|-------|----------------|---------|
| 1 | Story | `StoryAgent` | Narrative → beats, characters, setting |
| 2 | Characters | `CharacterDevelopmentAgent` | Deep arcs, style locks, evolution |
| 3 | RL Start | `MasterRLAgent` | Episode init + policy-based action selection |
| 4 | Storyboard | `StoryboardAgent` | Arc-driven shots + effects + motion hints |
| 5 | Keyframes | `ImageAgent` | AnimeGANv2 + Visual Consistency Protocol |
| 6 | Animation | `AnimationAgent` | Animate Anyone motion + particles |
| 7 | Audio | `AudioAgent` | Layered SFX + emotion-synced music |
| 8 | RL Rewards | `MasterRLAgent` | Composite scoring + Sub-RL evaluation |
| 9 | Scenes | `SceneRenderer` | RL-augmented interleaved output |
| 10 | Assembly | `EditorAgent` | Video merge + GCS upload |

### Enhancement #1: Character Development Engine
- **Character sheets**: `initial_state`, `arc_stages`, `style_lock`
- **Visual Consistency Protocol**: Every image prompt includes sheet ref + arc stage + style anchor
- **Zero-hallucination**: Flags `incomplete_fields` instead of inventing data

### Enhancement #2: RL Self-Improvement Agent (SAGE-Inspired)
- **Master RL**: Coordinates 4 Sub-RL agents, selects parameter tweaks, evolves policy
- **Composite Reward**: `0.3×Coherence + 0.25×Creativity + 0.2×Consistency + 0.15×Emotional + 0.1×Technical`
- **Sub-RL Agents**: Character RL, Visual RL, Audio RL, Sequence RL
- **RLHF**: User ratings (1-5) feed as reward bonus/penalty
- **Policy Evolution**: Learns high-reward patterns, auto-evolves policy version

### Open-Source Inspirations

| Feature | Reference |
|---------|-----------|
| RL Framework | SAGE (arXiv:2512.17102), ElegantRL |
| Animation | Animate Anyone (humanaigc) |
| Style | AnimeGANv2 (TachibanaYoshino) |
| Consistency | FLUX.1 Kontext |
| Audio | Audacity/LMMS patterns |

## Quick Start

```bash
git clone https://github.com/divyeshparekh9496/Creator.git
cd Creator
pip install -r requirements.txt
cp .env.example .env  # Set GOOGLE_API_KEY
python main.py --story "A lone samurai walks through a cherry blossom forest"
```

## Output

```
data/output/
├── characters/          # Sheets + profiles + arc data
├── keyframes/           # AnimeGANv2-styled frames
├── animation/           # Animation plan + effects
├── audio/               # Audio plan + SFX
├── scenes/              # RL-augmented interleaved output
├── rl/                  # Policy, episodes, reward logs
├── pipeline_state.json
└── character_evolution_log.json
```

## RL-Augmented Output Format

```
SCENE 2 – RL-Enhanced | Akira Arc Stage 2
🤖 RL State: Episode 3, Policy v2
  👤 Character Evolution: Akira: stage 2 (determined), visual: raised chin (Sub-RL: 0.85)
  📖 Narration: "For the first time, she felt the weight of her choice..."
  🖼️  Image: [Nano Banana 2: ...] + RL Action: add_particles (+0.15)
  🔊 Audio: [building drums, brass entering] + RL Action: emotional_music (+0.20)
  📊 RL Reward Preview: Coherence=0.90, Total=0.87
  📋 Metadata: {"rl_episode": 3, "policy_version": "v2", ...}
```

## License

MIT
