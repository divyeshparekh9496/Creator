"use client";
import { useState, useRef, useCallback } from "react";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

/**
 * Hook for real-time pipeline progress via SSE.
 * Events: stage_start, stage_done, stage_cached, pipeline_complete, done, error
 */
export function useStream() {
  const [status, setStatus] = useState("idle"); // idle | generating | done | error
  const [stages, setStages] = useState([]);
  const [currentStage, setCurrentStage] = useState(null);
  const [progress, setProgress] = useState(0);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [jobId, setJobId] = useState(null);
  const eventSourceRef = useRef(null);

  const generate = useCallback(async (story) => {
    setStatus("generating");
    setStages([]);
    setCurrentStage(null);
    setProgress(0);
    setResult(null);
    setError(null);

    try {
      // Start pipeline
      const res = await fetch(`${API_BASE}/api/generate`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ story }),
      });

      if (!res.ok) throw new Error(`API error: ${res.status}`);
      const { job_id } = await res.json();
      setJobId(job_id);

      // Connect SSE stream
      const sse = new EventSource(`${API_BASE}/api/status/${job_id}`);
      eventSourceRef.current = sse;

      sse.addEventListener("stage_start", (e) => {
        const data = JSON.parse(e.data);
        setCurrentStage(data.stage);
        setProgress(((data.index || 0) / 10) * 100);
        setStages((prev) => [...prev, { ...data, status: "processing", time: null }]);
      });

      sse.addEventListener("stage_done", (e) => {
        const data = JSON.parse(e.data);
        setStages((prev) =>
          prev.map((s) =>
            s.stage === data.stage ? { ...s, status: "done", data: data.data } : s
          )
        );
        setProgress(((data.index || 0) / 10) * 100);
      });

      sse.addEventListener("stage_cached", (e) => {
        const data = JSON.parse(e.data);
        setStages((prev) => [...prev, { ...data, status: "cached" }]);
      });

      sse.addEventListener("pipeline_complete", (e) => {
        const data = JSON.parse(e.data);
        setStatus("done");
        setProgress(100);
        if (data.result) setResult(data.result);
      });

      sse.addEventListener("done", async (e) => {
        const data = JSON.parse(e.data);
        setResult(data.result ?? null);
        setStatus("done");
        setProgress(100);
        if (!data?.result && job_id) {
          try {
            const jobRes = await fetch(`${API_BASE}/api/jobs/${job_id}`);
            const jobData = await jobRes.json();
            if (jobData?.result) setResult(jobData.result);
          } catch (_) {}
        }
        sse.close();
      });

      sse.addEventListener("error", (e) => {
        try {
          const data = JSON.parse(e.data);
          setError(data.message || "Pipeline error");
        } catch {
          setError("Connection lost");
        }
        setStatus("error");
        sse.close();
      });

      sse.onerror = () => {
        if (sse.readyState === EventSource.CLOSED) return;
        setError("Connection lost — retrying...");
      };
    } catch (err) {
      setError(err.message);
      setStatus("error");
    }
  }, []);

  const stop = useCallback(() => {
    if (eventSourceRef.current) {
      eventSourceRef.current.close();
      eventSourceRef.current = null;
    }
    setStatus("idle");
  }, []);

  return { status, stages, currentStage, progress, result, error, jobId, generate, stop };
}

/**
 * Submit RL feedback for a job.
 */
export async function submitFeedback(jobId, rating) {
  const res = await fetch(`${API_BASE}/api/feedback`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ job_id: jobId, rating }),
  });
  return res.json();
}

/**
 * Fetch job results.
 */
export async function fetchJob(jobId) {
  const res = await fetch(`${API_BASE}/api/jobs/${jobId}`);
  return res.json();
}

/**
 * List generated assets.
 */
export async function fetchAssets(jobId) {
  const url = jobId
    ? `${API_BASE}/api/assets?job_id=${jobId}`
    : `${API_BASE}/api/assets`;
  const res = await fetch(url);
  return res.json();
}
