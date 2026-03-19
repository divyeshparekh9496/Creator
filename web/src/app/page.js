"use client";
import { useState, useEffect, useRef } from "react";
import { AnimatePresence } from "framer-motion";
import Header from "@/components/Header";
import LeftSidebar from "@/components/LeftSidebar";
import CenterCanvas from "@/components/CenterCanvas";
import RightPanel from "@/components/RightPanel";
import TimelineEditor from "@/components/TimelineEditor";
import AssetLibrary from "@/components/AssetLibrary";
import ExportPanel from "@/components/ExportPanel";
import ParticleBackground from "@/components/ParticleBackground";
import { useStream, submitFeedback } from "@/hooks/useStream";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

const DEFAULT_SCENES = [
  { id: 1, title: "Waiting for story...", arcStage: 0, trait: "—", shots: 0, rlScore: 0, duration: 0 },
];
const DEFAULT_CHARACTERS = [];
const DEFAULT_RL = {
  episode: 0, policyVersion: "—", totalReward: 0,
  coherence: 0, creativity: 0, consistency: 0, emotional: 0, technical: 0,
};
const DEFAULT_PIPELINE = {
  status: "idle",
  stages: [
    { name: "Story Analysis", status: "queued" },
    { name: "Character Dev", status: "queued" },
    { name: "RL Start", status: "queued" },
    { name: "Storyboard", status: "queued" },
    { name: "Keyframes", status: "queued" },
    { name: "Animation", status: "queued" },
    { name: "Audio", status: "queued" },
    { name: "RL Rewards", status: "queued" },
    { name: "Scene Render", status: "queued" },
    { name: "Assembly", status: "queued" },
  ],
};

export default function Home() {
  const [showAssetLibrary, setShowAssetLibrary] = useState(false);
  const [showExport, setShowExport] = useState(false);
  const [selectedScene, setSelectedScene] = useState(null);
  const [timelineCollapsed, setTimelineCollapsed] = useState(false);
  const [theme, setTheme] = useState("dark");
  const [backendUp, setBackendUp] = useState(null);
  const [storyInput, setStoryInput] = useState("");
  const storyInputRef = useRef(null);

  const stream = useStream();

  useEffect(() => {
    fetch(`${API_BASE}/api/health`)
      .then((res) => res.ok && setBackendUp(true))
      .catch(() => setBackendUp(false));
  }, []);

  useEffect(() => {
    const saved = localStorage.getItem("creator-theme") || "dark";
    setTheme(saved);
    document.documentElement.setAttribute("data-theme", saved);
  }, []);


  const rawScenes = stream.result?.scene_rendering?.scenes ?? stream.result?.storyboard?.scenes ?? [];
  const scenes = rawScenes.length > 0
    ? rawScenes.map((s, i) => {
        let imageUrl = null;
        if (s.shots?.[0]?.image_path && s.shots[0].image_path !== "Not generated") {
          const path = s.shots[0].image_path.replace(/^data\/output\//, "output/");
          imageUrl = path.startsWith("http") ? path : `${API_BASE}/${path}`;
        }
        return {
          id: s.scene_id ?? i + 1,
          scene_id: s.scene_id ?? i + 1,
          title: s.title ?? `Scene ${i + 1}`,
          arcStage: s.arc_stage ?? 1,
          trait: s.trait ?? "—",
          shots: s.shots?.length ?? 0,
          rlScore: stream.result?.rl_rewards?.total ?? 0,
          duration: s.shots?.reduce((a, sh) => a + (sh.duration_seconds ?? 3), 0) ?? 0,
          imageUrl,
        };
      })
    : DEFAULT_SCENES;

  const characters = stream.result?.character_data?.character_sheets?.map((c) => ({
    id: c.character_id,
    name: c.name,
    role: c.role,
    arcStage: 1,
    styleLock: c.style_lock || "",
    trait: c.initial_state?.personality?.[0] ?? "—",
  })) ?? DEFAULT_CHARACTERS;

  const storyBeats = stream.result?.story_analysis?.beats ?? stream.result?.story_analysis?.narrative_beats ?? [];

  const rlData = stream.result?.rl_rewards
    ? {
        episode: stream.result.rl_rewards.composite?.episode ?? 1,
        policyVersion: "v1",
        totalReward: stream.result.rl_rewards.total ?? 0,
        coherence: stream.result.rl_rewards.composite?.coherence ?? 0,
        creativity: stream.result.rl_rewards.composite?.creativity ?? 0,
        consistency: stream.result.rl_rewards.composite?.consistency ?? 0,
        emotional: stream.result.rl_rewards.composite?.emotional_impact ?? 0,
        technical: stream.result.rl_rewards.composite?.technical_quality ?? 0,
      }
    : DEFAULT_RL;

  const pipeline = {
    status: stream.status,
    stages: DEFAULT_PIPELINE.stages.map((s) => {
      const live = stream.stages.find((ls) => ls.stage === s.name);
      if (live) return { ...s, status: live.status ?? "done", time: live.time };
      return s;
    }),
  };

  const toggleTheme = () => {
    const next = theme === "dark" ? "light" : "dark";
    setTheme(next);
    document.documentElement.setAttribute("data-theme", next);
    localStorage.setItem("creator-theme", next);
  };

  const handleNewStory = () => {
    stream.stop?.();
    setSelectedScene(null);
    setStoryInput("");
    setTimeout(() => storyInputRef.current?.focus(), 100);
  };

  const focusStoryInput = () => {
    storyInputRef.current?.focus();
  };

  const handleGenerate = (story) => stream.generate?.(story);

  const handleFeedback = async (isPositive) => {
    if (stream.jobId) await submitFeedback(stream.jobId, isPositive ? 5 : 2);
  };

  const coherencePct = Math.round((rlData.coherence ?? 0) * 100);

  return (
    <div style={{ height: "100vh", display: "flex", flexDirection: "column", position: "relative", overflow: "hidden" }}>
      <ParticleBackground />

      {backendUp === false && (
        <div
          style={{
            background: "hsla(0,70%,50%,0.9)",
            color: "white",
            padding: "8px 16px",
            fontSize: 12,
            textAlign: "center",
            zIndex: 100,
          }}
        >
          ⚠️ Backend not running. Start with: <code>python3 server.py</code>
        </div>
      )}

      {stream.status === "generating" && (
        <div
          style={{
            background: "hsla(263,70%,50%,0.9)",
            color: "white",
            padding: "8px 16px",
            fontSize: 12,
            textAlign: "center",
            zIndex: 100,
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            gap: 10,
          }}
        >
          <div
            style={{
              width: 14,
              height: 14,
              borderRadius: "50%",
              border: "2px solid white",
              borderTopColor: "transparent",
              animation: "spin 0.6s linear infinite",
            }}
          />
          {stream.currentStage ?? "Starting pipeline..."} — {stream.progress?.toFixed(0) ?? 0}%
          <style>{`@keyframes spin { to { transform: rotate(360deg) } }`}</style>
        </div>
      )}

      {stream.error && (
        <div
          style={{
            background: "hsla(0,70%,50%,0.9)",
            color: "white",
            padding: "8px 16px",
            fontSize: 12,
            textAlign: "center",
            zIndex: 100,
          }}
        >
          ❌ {stream.error}
        </div>
      )}

      <Header
        theme={theme}
        onToggleTheme={toggleTheme}
        onOpenAssets={() => setShowAssetLibrary(true)}
        onOpenExport={() => setShowExport(true)}
        onNewStory={handleNewStory}
        onOpenLibrary={() => setShowAssetLibrary(true)}
        onFocusStory={focusStoryInput}
        rlData={rlData}
      />

      <div style={{ display: "flex", height: "calc(100vh - var(--header-height))" }}>
        <LeftSidebar pipeline={pipeline} rlData={rlData} characters={characters} storyBeats={storyBeats} onFocusStory={focusStoryInput} />

        <div style={{ flex: 1, display: "flex", flexDirection: "column", height: "100%", overflow: "hidden" }}>
          <div style={{ flex: 1, padding: 24, overflowY: "auto", position: "relative" }}>
            <CenterCanvas
              scenes={scenes}
              rlData={rlData}
              selectedScene={selectedScene ?? scenes[0]}
              onSelectScene={setSelectedScene}
              characters={characters}
            />
          </div>
          <TimelineEditor
            scenes={scenes}
            selectedScene={selectedScene ?? scenes[0]}
            onSelectScene={setSelectedScene}
            collapsed={timelineCollapsed}
            onToggleCollapse={() => setTimelineCollapsed(!timelineCollapsed)}
          />
        </div>

        <RightPanel
          storyInput={storyInput}
          onStoryChange={setStoryInput}
          storyInputRef={storyInputRef}
          rlData={rlData}
          characters={characters}
          selectedScene={selectedScene ?? scenes[0]}
          storybookData={stream.result?.storybook}
          onGenerate={handleGenerate}
          onFeedback={handleFeedback}
          isGenerating={stream.status === "generating"}
        />
      </div>

      <div
        className="status-bar"
        style={{
          position: "fixed",
          bottom: 0,
          left: 0,
          right: 0,
          height: 36,
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          padding: "0 24px",
          fontSize: 11,
          color: "hsl(var(--text-muted))",
          backdropFilter: "blur(12px)",
          zIndex: 90,
        }}
      >
        <div style={{ display: "flex", gap: 24, alignItems: "center" }}>
          <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
            <span style={{ color: "hsl(var(--text-secondary))", fontWeight: 500 }}>Coherence</span>
            <div style={{ width: 100, height: 6, background: "hsla(240, 20%, 18%, 0.8)", borderRadius: 4, overflow: "hidden", border: "1px solid hsla(240, 20%, 25%, 0.5)" }}>
              <div
                style={{
                  width: `${Math.max(coherencePct, 2)}%`,
                  height: "100%",
                  background: coherencePct > 0
                    ? "linear-gradient(90deg, hsl(260, 80%, 55%), hsl(355, 75%, 55%))"
                    : "hsla(240, 20%, 25%, 0.5)",
                  borderRadius: 3,
                  transition: "width 0.4s ease, background 0.3s",
                }}
              />
            </div>
            <span style={{ color: "hsl(160, 84%, 50%)", fontWeight: 600, minWidth: 32 }}>{coherencePct}%</span>
          </div>
          {stream.status === "idle" && coherencePct === 0 && (
            <span style={{ color: "hsl(var(--text-muted))", fontSize: 10 }}>Ready — enter a story and generate</span>
          )}
        </div>
        <div style={{ display: "flex", gap: 20, alignItems: "center" }}>
          {stream.jobId && (
            <span style={{ background: "hsla(263, 50%, 25%, 0.3)", padding: "4px 10px", borderRadius: 6, fontSize: 10 }}>
              Job: {stream.jobId}
            </span>
          )}
          <span>Ep. {rlData.episode} · {rlData.policyVersion}</span>
        </div>
      </div>

      <AnimatePresence>
        {showAssetLibrary && <AssetLibrary onClose={() => setShowAssetLibrary(false)} jobId={stream.jobId} />}
        {showExport && (
          <ExportPanel
            onClose={() => setShowExport(false)}
            pipeline={pipeline}
            jobId={stream.jobId}
            result={stream.result}
          />
        )}
      </AnimatePresence>
    </div>
  );
}
