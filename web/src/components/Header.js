"use client";
import { motion } from "framer-motion";
import { Sparkles, Moon, Sun, FolderOpen, Download, Film, Library, Plus, ChevronDown, Zap } from "lucide-react";
import { useState } from "react";

function RLStatsDropdown({ rlData, onClose }) {
  if (!rlData || rlData.episode === 0) return null;
  return (
    <motion.div
      initial={{ opacity: 0, y: -8 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -8 }}
      className="glass-card-elevated"
      style={{
        position: "absolute", top: "100%", right: 0, marginTop: 8,
        minWidth: 220, padding: 16, zIndex: 100,
      }}
    >
      <div style={{ fontSize: 11, fontWeight: 600, color: "hsl(var(--text-muted))", marginBottom: 12, textTransform: "uppercase", letterSpacing: "0.05em" }}>
        RL Quality Scores
      </div>
      <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
        {[
          { label: "Coherence", value: (rlData.coherence ?? 0) * 100, color: "#8B5CF6" },
          { label: "Creativity", value: (rlData.creativity ?? 0) * 100, color: "#3B82F6" },
          { label: "Consistency", value: (rlData.consistency ?? 0) * 100, color: "#10B981" },
          { label: "Emotional", value: (rlData.emotional ?? 0) * 100, color: "#F59E0B" },
          { label: "Technical", value: (rlData.technical ?? 0) * 100, color: "#EC4899" },
        ].map((m) => (
          <div key={m.label}>
            <div style={{ display: "flex", justifyContent: "space-between", fontSize: 11, marginBottom: 4 }}>
              <span style={{ color: "hsl(var(--text-secondary))" }}>{m.label}</span>
              <span style={{ fontWeight: 600, color: m.color }}>{Math.round(m.value)}%</span>
            </div>
            <div style={{ height: 4, background: "hsl(var(--bg-hover))", borderRadius: 2, overflow: "hidden" }}>
              <div style={{ width: `${Math.min(100, m.value)}%`, height: "100%", background: m.color, borderRadius: 2, transition: "width 0.3s ease" }} />
            </div>
          </div>
        ))}
      </div>
      <div style={{ marginTop: 12, paddingTop: 12, borderTop: "1px solid var(--glass-border)", fontSize: 10, color: "hsl(var(--text-muted))" }}>
        Episode {rlData.episode} · Policy {rlData.policyVersion || "v1"}
      </div>
    </motion.div>
  );
}

export default function Header({ theme, onToggleTheme, onOpenAssets, onOpenExport, rlData, onNewStory, onOpenLibrary, onFocusStory }) {
  const [showRLStats, setShowRLStats] = useState(false);

  const handleNewStory = () => {
    if (onNewStory) onNewStory();
    else window.location.reload();
  };

  const handleMyLibrary = () => {
    if (onOpenLibrary) onOpenLibrary();
    else onOpenAssets?.();
  };

  return (
    <motion.header
      initial={{ y: -20, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      className="header-bar"
      style={{
        height: "var(--header-height)",
        display: "flex", alignItems: "center", justifyContent: "space-between",
        padding: "0 24px",
        backdropFilter: "blur(16px)", WebkitBackdropFilter: "blur(16px)",
        zIndex: 50, position: "relative"
      }}
    >
      <div style={{ display: "flex", alignItems: "center", gap: 32 }}>
        <button
          type="button"
          onClick={() => onFocusStory?.()}
          style={{
            display: "flex", alignItems: "center", gap: 12,
            background: "none", border: "none", cursor: "pointer", padding: 0,
          }}
          aria-label="Creator — focus story input"
        >
          <div style={{
            width: 36, height: 36, borderRadius: 10,
            background: "linear-gradient(135deg, hsl(355, 80%, 55%), hsl(260, 80%, 60%))",
            display: "flex", alignItems: "center", justifyContent: "center",
            boxShadow: "0 0 20px hsla(355, 80%, 55%, 0.4)",
          }}>
            <Film size={18} color="white" />
          </div>
          <div className="header-text" style={{ fontSize: 18, fontWeight: 700, letterSpacing: "-0.03em" }}>
            Creator
          </div>
        </button>

        <div style={{ display: "flex", gap: 8, fontSize: 13, fontWeight: 500 }}>
          <button
            className="btn-ghost"
            style={{ display: "flex", alignItems: "center", gap: 6 }}
            onClick={handleNewStory}
          >
            <Plus size={14} /> New Story
          </button>
          <button
            className="btn-ghost"
            style={{ display: "flex", alignItems: "center", gap: 6 }}
            onClick={handleMyLibrary}
          >
            <Library size={14} /> My Library
          </button>
        </div>
      </div>

      <div style={{ display: "flex", alignItems: "center", gap: 16, position: "relative" }}>
        <button
          className="rl-pulse"
          onClick={() => setShowRLStats(!showRLStats)}
          style={{
            display: "flex", alignItems: "center", gap: 8, fontSize: 12,
            padding: "6px 14px", borderRadius: 8,
            background: "hsla(160,84%,39%,0.12)", color: "hsl(var(--accent))",
            border: "1px solid hsla(160,84%,39%,0.3)",
            cursor: "pointer", transition: "all 0.2s",
          }}
        >
          <Sparkles size={14} />
          Reward: {(rlData?.totalReward ?? 0).toFixed(2)}
          <ChevronDown size={12} style={{ opacity: showRLStats ? 1 : 0.5, transform: showRLStats ? "rotate(180deg)" : "none" }} />
        </button>
        {showRLStats && (
          <>
            <div style={{ position: "fixed", inset: 0, zIndex: 99 }} onClick={() => setShowRLStats(false)} />
            <RLStatsDropdown rlData={rlData} onClose={() => setShowRLStats(false)} />
          </>
        )}
      </div>

      <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
        <button className="btn-ghost" onClick={onOpenAssets}>
          <FolderOpen size={14} /> Assets
        </button>
        <button className="btn-primary" onClick={onOpenExport}>
          <Download size={14} /> Export
        </button>
        <button className="btn-icon" onClick={onToggleTheme} aria-label="Toggle theme">
          {theme === "dark" ? <Sun size={16} /> : <Moon size={16} />}
        </button>
      </div>
    </motion.header>
  );
}
