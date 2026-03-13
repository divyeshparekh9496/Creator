"use client";
import { useState } from "react";
import { AnimatePresence } from "framer-motion";
import Header from "@/components/Header";
import LeftSidebar from "@/components/LeftSidebar";
import CenterCanvas from "@/components/CenterCanvas";
import RightPanel from "@/components/RightPanel";
import TimelineEditor from "@/components/TimelineEditor";
import AssetLibrary from "@/components/AssetLibrary";
import ExportPanel from "@/components/ExportPanel";
import ParticleBackground from "@/components/ParticleBackground";

// ── Demo/mock data ──
const MOCK_SCENES = [
  { id: 1, title: "The Awakening", arcStage: 1, trait: "timid", shots: 3, rlScore: 0.82, duration: 12, image: null },
  { id: 2, title: "Doubt Turns to Resolve", arcStage: 2, trait: "determined", shots: 4, rlScore: 0.87, duration: 16, image: null },
  { id: 3, title: "Trial by Fire", arcStage: 2, trait: "brave", shots: 3, rlScore: 0.91, duration: 14, image: null },
  { id: 4, title: "The Warrior Rises", arcStage: 3, trait: "heroic", shots: 5, rlScore: 0.94, duration: 20, image: null },
];

const MOCK_CHARACTERS = [
  { id: "elara_001", name: "Elara", role: "protagonist", arcStage: 2, styleLock: "anime_elf: silver hair, emerald eyes", trait: "determined" },
  { id: "kai_002", name: "Kai", role: "rival", arcStage: 1, styleLock: "anime_warrior: dark hair, crimson eyes", trait: "hostile" },
];

const MOCK_RL = {
  episode: 3, policyVersion: "v2", totalReward: 0.87,
  coherence: 0.90, creativity: 0.82, consistency: 0.91, emotional: 0.85, technical: 0.78,
  actions: [
    { type: "add_particles", param: "density +15%", agent: "image" },
    { type: "emotional_music", param: "intensity +20%", agent: "audio" },
  ],
  patterns: ["Slow-build arcs + particle glows → +15% reward", "Layered SFX + emotion sync → +12%"],
};

const MOCK_PIPELINE = {
  status: "processing",
  stages: [
    { name: "Story Analysis", status: "done", time: "2.1s" },
    { name: "Character Dev", status: "done", time: "5.3s" },
    { name: "Storyboard", status: "done", time: "3.8s" },
    { name: "Keyframes", status: "processing", time: "12s", progress: 65 },
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
  const [selectedScene, setSelectedScene] = useState(MOCK_SCENES[0]);
  const [timelineCollapsed, setTimelineCollapsed] = useState(false);
  const [theme, setTheme] = useState("dark");

  const toggleTheme = () => {
    const next = theme === "dark" ? "light" : "dark";
    setTheme(next);
    document.documentElement.setAttribute("data-theme", next);
  };

  return (
    <div style={{ height: "100vh", display: "flex", flexDirection: "column", position: "relative", overflow: "hidden" }}>
      <ParticleBackground />

      {/* Header */}
      <Header
        theme={theme}
        onToggleTheme={toggleTheme}
        onOpenAssets={() => setShowAssetLibrary(true)}
        onOpenExport={() => setShowExport(true)}
        rlData={MOCK_RL}
      />

      {/* Main Layout: Sidebar | Canvas | Right Panel */}
      <div style={{ display: "flex", flex: 1, overflow: "hidden" }}>
        <LeftSidebar
          pipeline={MOCK_PIPELINE}
          rlData={MOCK_RL}
          characters={MOCK_CHARACTERS}
        />

        <CenterCanvas
          scenes={MOCK_SCENES}
          selectedScene={selectedScene}
          rlData={MOCK_RL}
          characters={MOCK_CHARACTERS}
        />

        <RightPanel
          rlData={MOCK_RL}
          characters={MOCK_CHARACTERS}
          selectedScene={selectedScene}
        />
      </div>

      {/* Timeline Editor — bottom dock */}
      <TimelineEditor
        scenes={MOCK_SCENES}
        selectedScene={selectedScene}
        onSelectScene={setSelectedScene}
        collapsed={timelineCollapsed}
        onToggleCollapse={() => setTimelineCollapsed(!timelineCollapsed)}
      />

      {/* Modal Overlays */}
      <AnimatePresence>
        {showAssetLibrary && <AssetLibrary onClose={() => setShowAssetLibrary(false)} />}
        {showExport && <ExportPanel onClose={() => setShowExport(false)} pipeline={MOCK_PIPELINE} />}
      </AnimatePresence>
    </div>
  );
}
