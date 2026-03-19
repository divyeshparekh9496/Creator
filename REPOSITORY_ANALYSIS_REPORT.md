# Creator — Repository Analysis Report

**Generated:** March 13, 2025  
**Repository:** Creator (Gemini Live Agent Hackathon)  
**Path:** `/Users/divyesh/Desktop/Gemini Live Agent Hackathon/Creator`

---

## 1. Executive Summary

**Creator** is a self-evolving creative-director AI that turns text stories into **anime-style animated sequences** with character arcs, visual effects, and RL-driven self-improvement. It implements an end-to-end pipeline from narrative input to final video, powered by Gemini, Google GenAI SDK, GCS, and a SAGE-inspired reinforcement learning system.

---

## 2. Project Overview

### Purpose

Convert narrative input into a full anime production pipeline:

```
Story → Characters → Storyboard → Keyframes → Animation → Audio → Video Assembly
```

With reinforcement learning to iteratively improve outputs based on composite reward signals and optional user feedback (RLHF).

### Target Audience

- Content creators (indie animators, writers, producers)
- Hackathon and demo use
- Teams exploring AI-driven anime-style production

### Main Value Proposition

| Feature | Description |
|--------|-------------|
| **End-to-end pipeline** | Single run from story text to final video |
| **Character-driven** | Character sheets, arc stages, style consistency |
| **RL self-improvement** | Master RL + 5 Sub-RL agents, composite rewards, RLHF |
| **Modern stack** | Gemini 3.1, Google GenAI SDK, GCS, Next.js web UI, SSE streaming |

---

## 3. Architecture & Structure

### Directory Layout

```
Creator/
├── main.py                 # CLI entry point (--story or --file)
├── server.py               # FastAPI backend (REST + SSE)
├── requirements.txt        # Python dependencies
├── .env.example            # Environment template
├── README.md               # Main documentation
├── src/
│   ├── config.py           # Configuration and env loading
│   ├── pipeline.py         # 10-stage pipeline orchestration
│   ├── agents/             # Pipeline stage agents
│   │   ├── base_agent.py
│   │   ├── story_agent.py
│   │   ├── character_agent.py
│   │   ├── storyboard_agent.py
│   │   ├── image_agent.py
│   │   ├── animation_agent.py
│   │   ├── audio_agent.py
│   │   ├── storybook_agent.py
│   │   ├── scene_renderer.py
│   │   └── editor_agent.py
│   ├── rl/                 # Reinforcement learning system
│   │   ├── master_agent.py
│   │   ├── sub_agents.py
│   │   └── reward_system.py
│   └── utils/
│       ├── genai_client.py
│       ├── gcp_utils.py
│       ├── token_optimizer.py
│       └── cache.py
├── web/                    # Next.js 16 frontend
│   ├── package.json
│   ├── src/
│   │   ├── app/            # App Router (page.js, layout.js, globals.css)
│   │   ├── components/     # UI components
│   │   └── hooks/          # useStream, etc.
│   └── next.config.mjs
└── data/output/            # Generated assets (characters, keyframes, scenes, etc.)
```

### Pipeline Flow

```
User (CLI or Web UI) → main.py / server.py
        ↓
CreatorPipeline (src/pipeline.py)
        ↓
Stage 1:  StoryAgent              → Narrative analysis (beats, characters, setting)
Stage 2:  CharacterDevelopmentAgent → Character sheets + arcs
Stage 3:  MasterRLAgent           → Episode init + policy-based action selection
Stage 4:  StoryboardAgent         → Arc-driven shots, effects, motion hints
Stages 5–7 (parallel):
          ImageAgent, AnimationAgent, AudioAgent, StorybookAgent
Stage 8:  MasterRLAgent           → Composite rewards + Sub-RL evaluation
Stage 9:  SceneRenderer           → RL-augmented interleaved scene output
Stage 10: EditorAgent             → ffmpeg video assembly + GCS upload
```

### Tech Stack

| Layer | Technology |
|-------|------------|
| Backend | Python 3, FastAPI, uvicorn |
| GenAI | google-genai, Gemini 3.1, Gemini 2.5 |
| Cloud | Google Cloud Storage, Vertex AI |
| Caching | Redis (optional) + file fallback |
| Frontend | Next.js 16.1.6, React 19.2.3, Tailwind 4 |
| UI | Framer Motion, Lucide React, react-markdown |
| Video | ffmpeg (EditorAgent) |

---

## 4. Key Components

### Agents (10-Stage Pipeline)

| Agent | Role |
|-------|------|
| **StoryAgent** | Narrative analysis → beats, characters, setting |
| **CharacterDevelopmentAgent** | Character sheets, arcs, `style_lock`, evolution tracking |
| **StoryboardAgent** | Arc-driven shots, effects, motion hints |
| **ImageAgent** | Keyframes with Visual Consistency Protocol |
| **AnimationAgent** | Motion/animation plans |
| **AudioAgent** | SFX and music plans, emotion-synced |
| **StorybookAgent** | Storybook images from scenes |
| **SceneRenderer** | RL-augmented interleaved scene output |
| **EditorAgent** | ffmpeg-based video assembly and GCS upload |

### RL System

- **MasterRLAgent**: Orchestrates sub-RL agents, policy, and episode lifecycle
- **Sub-RL Agents**: CharacterRL, VisualRL, AudioRL, SequenceRL, StorybookRL
- **RewardEvaluator**: Gemini-based scoring on coherence, creativity, consistency, emotional impact, technical quality
- **Composite reward**: `0.3×Coherence + 0.25×Creativity + 0.2×Consistency + 0.15×Emotional + 0.1×Technical`
- **RLHF**: User ratings (1–5) feed as reward bonus/penalty

### Utilities & Services

- **GenAIClient**: Retries, circuit breaker, token budget, monitoring
- **GCPUtils**: GCS upload/download, optional mocking when no credentials
- **SceneCache**: Redis + file fallback, input-hash–based keys
- **TokenBudget / token_optimizer**: Prompt compression and token usage control

### Web App Components

- **useStream**: SSE hook for pipeline progress (`POST /api/generate` → `GET /api/status/{job_id}`)
- **Layout**: Header, LeftSidebar, RightPanel, CenterCanvas, TimelineEditor
- **AssetLibrary**: Browse generated assets
- **ExportPanel**: Export options
- **ParticleBackground**: Background visuals

---

## 5. API Endpoints

| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/api/health` | Health check |
| POST | `/api/generate` | Start pipeline (returns `job_id`) |
| GET | `/api/status/{job_id}` | SSE stream of stage-by-stage progress |
| GET | `/api/jobs/{job_id}` | Get completed job results |
| GET | `/api/jobs` | List all jobs |
| POST | `/api/feedback` | Submit RLHF rating (1–5) |
| GET | `/api/assets` | Browse generated assets |
| GET | `/api/monitor` | Global pipeline monitor |
| GET | `/api/monitor/{job_id}` | Per-job monitor |

---

## 6. Dependencies

### Backend (`requirements.txt`)

- **Core**: google-genai, google-cloud-storage, python-dotenv, pillow
- **Server**: fastapi, uvicorn, sse-starlette
- **Testing**: pytest
- **Caching**: redis (optional with file fallback)

### Frontend (`web/package.json`)

- **Runtime**: next 16.1.6, react 19.2.3, framer-motion, lucide-react, react-markdown
- **Dev**: Tailwind 4, ESLint, eslint-config-next

---

## 7. Configuration

### Environment Variables (`.env.example`)

| Variable | Purpose |
|----------|---------|
| `GOOGLE_API_KEY` | GenAI API key (required) |
| `GOOGLE_CLOUD_PROJECT` | GCP project for Vertex/GCS |
| `GOOGLE_CLOUD_LOCATION` | Default: `us-central1` |
| `GCS_BUCKET_NAME` | Default: `creator-anime-assets` |
| `GOOGLE_APPLICATION_CREDENTIALS` | Optional service account JSON path |

### Run Commands

- **CLI**: `python main.py --story "..."` or `python main.py --file story.txt`
- **Server**: `python server.py` → `http://localhost:8000`
- **Web**: `cd web && npm run dev` → `http://localhost:3000`
- **API docs**: `http://localhost:8000/docs`

---

## 8. Strengths

1. **Clear architecture**: 10-stage pipeline, consistent `BaseAgent` pattern, parallel stages where possible.
2. **Resilience**: Circuit breaker, quota checks, Redis + file caching with graceful fallback.
3. **Observability**: APIMonitor, token budget, cache stats, `/api/monitor`.
4. **RL design**: Sub-RL agents, composite rewards, RLHF path, policy evolution.
5. **Character consistency**: Character sheets, arc stages, Visual Consistency Protocol.
6. **UX**: SSE streaming for live progress, Framer Motion, dark cosmic theme.
7. **Documentation**: README describes architecture, pipeline, and quick start.

---

## 9. Areas for Improvement

| Issue | Description |
|-------|-------------|
| **Hardcoded API URL** | `useStream.js` and `page.js` use `http://localhost:8000`; should use `NEXT_PUBLIC_API_URL` for production |
| **Limited tests** | No pytest-based unit tests; only manual `test_story_agent.py`-style usage |
| **No container setup** | No Dockerfile or docker-compose; deployment story is implicit (e.g. Vercel for web) |
| **RLHF wiring** | `POST /api/feedback` stores feedback, but `CreatorPipeline.get_user_feedback` may not be fully connected to RL updates |
| **ffmpeg dependency** | EditorAgent depends on ffmpeg with no version or install docs in README |
| **Redis behavior** | Optional but used for full caching; startup behavior and fallback could be clearer |
| **CORS** | Server allows only `localhost:3000`; production needs configurable origins |

---

## 10. Recommendations

1. **Add `NEXT_PUBLIC_API_URL`** in web app and use it for all API calls.
2. **Add Dockerfile** (and optionally docker-compose) for backend and web.
3. **Add pytest tests** for agents and pipeline stages (story, character, storyboard, etc.).
4. **Wire feedback** from `POST /api/feedback` into `CreatorPipeline` RLHF path.
5. **Document ffmpeg** requirement (version, install) in main README.
6. **Document Redis** usage: optional vs required, fallback behavior.
7. **Add architecture diagram** (e.g. Mermaid) and API docs for stakeholders.
8. **Make CORS origins configurable** via environment variable.

---

## 11. Output Structure

Generated output layout:

```
data/output/
├── {job_id}/
│   ├── characters/          # Character sheets, profiles, arc data
│   ├── keyframes/           # AnimeGANv2-styled frames
│   ├── animation/           # Animation plan + effects
│   ├── audio/               # Audio plan + SFX
│   ├── storybook/           # Storybook images
│   ├── scenes/              # RL-augmented interleaved output
│   ├── rl/                  # Policy, episodes, reward logs
│   ├── pipeline_state.json
│   └── character_evolution_log.json
└── cache/                   # Scene cache (Redis or file)
```

---

*Report generated from analysis of the Creator repository.*
