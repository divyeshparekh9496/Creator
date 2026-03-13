"use client";
import { useState, useEffect } from "react";
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

// ── Fallback data (shown before first generation) ──
const DEFAULT_SCENES = [
  { id: 1, title: "Waiting for story...", arcStage: 0, trait: "—", shots: 0, rlScore: 0, duration: 0 },
];
const DEFAULT_CHARACTERS = [];
const DEFAULT_RL = {
  episode: 0, policyVersion: "—", totalReward: 0,
  coherence: 0, creativity: 0, consistency: 0, emotional: 0, technical: 0,
  actions: [], patterns: [],
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

  // Real-time pipeline stream
  const stream = useStream();

  // Check backend health on mount
  useEffect(() => {
    fetch("http://localhost:8000/api/health")
      .then((res) => res.ok && setBackendUp(true))
      .catch(() => setBackendUp(false));
  }, []);

  // ── Derive live data from stream or fallback ──
  const scenes = stream.result?.storyboard?.scenes?.map((s, i) => ({
    id: s.scene_id || i + 1,
    title: s.title || `Scene ${i + 1}`,
    arcStage: s.arc_stage || 1,
    trait: s.trait || "—",
    shots: s.shots?.length || 0,
    rlScore: stream.result?.rl_rewards?.total || 0,
    duration: s.shots?.reduce((a, sh) => a + (sh.duration_seconds || 3), 0) || 0,
  })) || DEFAULT_SCENES;

  const characters = stream.result?.character_data?.character_sheets?.map((c) => ({
    id: c.character_id,
    name: c.name,
    role: c.role,
    arcStage: 1,
    styleLock: c.style_lock || "",
    trait: c.initial_state?.personality?.[0] || "—",
  })) || DEFAULT_CHARACTERS;

  const rlData = stream.result?.rl_rewards ? {
    episode: stream.result.rl_rewards.composite?.episode || 1,
    policyVersion: "v1",
    totalReward: stream.result.rl_rewards.total || 0,
    coherence: stream.result.rl_rewards.composite?.coherence || 0,
    creativity: stream.result.rl_rewards.composite?.creativity || 0,
    consistency: stream.result.rl_rewards.composite?.consistency || 0,
    emotional: stream.result.rl_rewards.composite?.emotional_impact || 0,
    technical: stream.result.rl_rewards.composite?.technical_quality || 0,
    actions: [], patterns: [],
  } : DEFAULT_RL;

  // Build pipeline from stream stages
  const pipeline = {
    status: stream.status,
    stages: DEFAULT_PIPELINE.stages.map((s) => {
      const live = stream.stages.find((ls) => ls.stage === s.name);
      if (live) return { ...s, status: live.status || "done", time: live.time };
      return s;
    }),
  };

  const toggleTheme = () => {
    const next = theme === "dark" ? "light" : "dark";
    setTheme(next);
    document.documentElement.setAttribute("data-theme", next);
  };

  const handleGenerate = (story) => {
    stream.generate(story);
  };

  const handleFeedback = async (isPositive) => {
    if (stream.jobId) {
      await submitFeedback(stream.jobId, isPositive ? 5 : 2);
    }
  };

  return (
    <div style={{ height: "100vh", display: "flex", flexDirection: "column", position: "relative", overflow: "hidden" }}>
      <ParticleBackground />

      {/* Backend status banner */}
      {backendUp === false && (
        <div style={{
          background: "hsla(0,70%,50%,0.9)", color: "white",
          padding: "6px 16px", fontSize: 12, textAlign: "center", zIndex: 100,
        }}>
          ⚠️ Backend not running. Start with: <code>python server.py</code>
        </div>
      )}

      {/* Generation progress banner */}
      {stream.status === "generating" && (
        <div style={{
          background: "hsla(263,70%,50%,0.9)", color: "white",
          padding: "6px 16px", fontSize: 12, textAlign: "center", zIndex: 100,
          display: "flex", alignItems: "center", justifyContent: "center", gap: 8,
        }}>
          <div style={{
            width: 12, height: 12, borderRadius: "50%",
            border: "2px solid white", borderTopColor: "transparent",
            animation: "spin 0.6s linear infinite",
          }} />
          {stream.currentStage || "Starting pipeline..."} — {stream.progress.toFixed(0)}%
          <style>{`@keyframes spin { to { transform: rotate(360deg) } }`}</style>
        </div>
      )}

      {stream.error && (
        <div style={{
          background: "hsla(0,70%,50%,0.9)", color: "white",
          padding: "6px 16px", fontSize: 12, textAlign: "center", zIndex: 100,
        }}>
          ❌ {stream.error}
        </div>
      )}

      <Header
        theme={theme}
        onToggleTheme={toggleTheme}
        onOpenAssets={() => setShowAssetLibrary(true)}
        onOpenExport={() => setShowExport(true)}
        rlData={rlData}
      />

      <div style={{ display: "flex", flex: 1, overflow: "hidden" }}>
        <LeftSidebar pipeline={pipeline} rlData={rlData} characters={characters} />
        <CenterCanvas scenes={scenes} selectedScene={selectedScene || scenes[0]} rlData={rlData} characters={characters} />
        <RightPanel
          rlData={rlData}
          characters={characters}
          selectedScene={selectedScene || scenes[0]}
          onGenerate={handleGenerate}
          onFeedback={handleFeedback}
          isGenerating={stream.status === "generating"}
        />
      </div>

      <TimelineEditor
        scenes={scenes}
        selectedScene={selectedScene || scenes[0]}
        onSelectScene={setSelectedScene}
        collapsed={timelineCollapsed}
        onToggleCollapse={() => setTimelineCollapsed(!timelineCollapsed)}
      />

      <AnimatePresence>
        {showAssetLibrary && <AssetLibrary onClose={() => setShowAssetLibrary(false)} jobId={stream.jobId} />}
        {showExport && <ExportPanel onClose={() => setShowExport(false)} pipeline={pipeline} />}
      </AnimatePresence>
    </div>
  );
}
