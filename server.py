"""
Creator FastAPI Server — REST + SSE endpoints connecting frontend ↔ pipeline.

Endpoints:
  POST /api/generate     — Start a new pipeline run (returns job_id)
  GET  /api/status/{id}  — SSE stream of stage-by-stage progress
  GET  /api/jobs/{id}     — Get completed job results
  POST /api/feedback      — Submit RL rating (RLHF)
  GET  /api/assets        — Browse generated assets
  GET  /api/health        — Health check
"""
import os
import sys
import uuid
import json
import time
import asyncio
from threading import Thread
from typing import Dict, Any

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from sse_starlette.sse import EventSourceResponse

# Ensure project root on path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.pipeline import CreatorPipeline
from src.config import DEFAULT_OUTPUT_DIR

app = FastAPI(title="Creator API", version="1.0.0")

# CORS — allow Next.js dev server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve generated output files
os.makedirs(DEFAULT_OUTPUT_DIR, exist_ok=True)
app.mount("/output", StaticFiles(directory=DEFAULT_OUTPUT_DIR), name="output")

# ── Job storage ──
jobs: Dict[str, Dict[str, Any]] = {}
job_events: Dict[str, list] = {}


class GenerateRequest(BaseModel):
    story: str
    output_dir: str = DEFAULT_OUTPUT_DIR


class FeedbackRequest(BaseModel):
    job_id: str
    rating: int  # 1-5


# ── Health ──
@app.get("/api/health")
async def health():
    return {"status": "ok", "version": "1.0.0", "jobs": len(jobs)}


# ── Generate ──
@app.post("/api/generate")
async def generate(req: GenerateRequest):
    job_id = str(uuid.uuid4())[:8]
    output_dir = os.path.join(req.output_dir, job_id)

    jobs[job_id] = {
        "id": job_id,
        "status": "starting",
        "story": req.story[:200],
        "output_dir": output_dir,
        "created_at": time.time(),
        "stages_completed": 0,
        "total_stages": 10,
        "result": None,
        "error": None,
    }
    job_events[job_id] = []

    # Run pipeline in background thread
    def _run():
        try:
            def on_progress(event, data=None):
                entry = {"event": event, "data": data or {}, "ts": time.time()}
                job_events[job_id].append(entry)

                if event == "stage_start":
                    jobs[job_id]["status"] = f"processing: {data.get('stage', '')}"
                elif event == "stage_done":
                    jobs[job_id]["stages_completed"] = data.get("index", 0)
                elif event == "pipeline_complete":
                    jobs[job_id]["status"] = "done"

            pipeline = CreatorPipeline(
                output_dir=output_dir,
                on_progress=on_progress,
            )
            result = pipeline.run_full(req.story)

            # Sanitize result for JSON
            sanitized = {}
            for k, v in result.items():
                try:
                    json.dumps(v)
                    sanitized[k] = v
                except TypeError:
                    sanitized[k] = str(v)

            jobs[job_id]["result"] = sanitized
            jobs[job_id]["status"] = "done"

        except Exception as e:
            jobs[job_id]["status"] = "error"
            jobs[job_id]["error"] = str(e)
            job_events[job_id].append({
                "event": "error", "data": {"message": str(e)}, "ts": time.time()
            })

    thread = Thread(target=_run, daemon=True)
    thread.start()

    return {"job_id": job_id, "status": "started"}


# ── SSE Status stream ──
@app.get("/api/status/{job_id}")
async def status_stream(job_id: str):
    if job_id not in jobs:
        raise HTTPException(404, "Job not found")

    async def event_generator():
        sent = 0
        while True:
            events = job_events.get(job_id, [])
            for evt in events[sent:]:
                yield {
                    "event": evt["event"],
                    "data": json.dumps(evt["data"]),
                }
                sent = len(events)

            status = jobs[job_id]["status"]
            if status in ("done", "error"):
                yield {
                    "event": "done" if status == "done" else "error",
                    "data": json.dumps({
                        "status": status,
                        "result": jobs[job_id].get("result"),
                        "error": jobs[job_id].get("error"),
                    }),
                }
                break

            await asyncio.sleep(0.5)

    return EventSourceResponse(event_generator())


# ── Get job results ──
@app.get("/api/jobs/{job_id}")
async def get_job(job_id: str):
    job = jobs.get(job_id)
    if not job:
        raise HTTPException(404, "Job not found")
    return job


# ── List all jobs ──
@app.get("/api/jobs")
async def list_jobs():
    return {"jobs": list(jobs.values())}


# ── RL Feedback ──
@app.post("/api/feedback")
async def submit_feedback(req: FeedbackRequest):
    job = jobs.get(req.job_id)
    if not job:
        raise HTTPException(404, "Job not found")
    if req.rating < 1 or req.rating > 5:
        raise HTTPException(400, "Rating must be 1-5")

    # Store feedback
    job.setdefault("feedback", []).append({
        "rating": req.rating, "ts": time.time(),
    })

    return {"status": "ok", "rating": req.rating, "job_id": req.job_id}


# ── Browse assets ──
@app.get("/api/assets")
async def list_assets(job_id: str = None):
    base = DEFAULT_OUTPUT_DIR
    if job_id:
        base = os.path.join(base, job_id)
    if not os.path.exists(base):
        return {"assets": []}

    assets = []
    for root, dirs, files in os.walk(base):
        for f in files:
            if f.startswith("."):
                continue
            path = os.path.join(root, f)
            rel = os.path.relpath(path, DEFAULT_OUTPUT_DIR)
            assets.append({
                "name": f,
                "path": f"/output/{rel}",
                "size": os.path.getsize(path),
                "type": f.split(".")[-1],
            })
    return {"assets": assets}


if __name__ == "__main__":
    import uvicorn
    print("\n🎬 Creator API Server starting...")
    print("   Docs: http://localhost:8000/docs")
    print("   Health: http://localhost:8000/api/health\n")
    uvicorn.run(app, host="0.0.0.0", port=8000)
