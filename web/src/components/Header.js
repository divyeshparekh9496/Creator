"use client";
import { motion } from "framer-motion";
import { Sparkles, Moon, Sun, FolderOpen, Download, Zap, Film, Rocket, Plus, Library, Share, Play } from "lucide-react";

export default function Header({ theme, onToggleTheme, onOpenAssets, onOpenExport, rlData }) {
  return (
    <motion.header
      initial={{ y: -20, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      style={{
        height: "var(--header-height)",
        borderBottom: "1px solid hsla(240, 20%, 30%, 0.3)",
        display: "flex", alignItems: "center", justifyContent: "space-between",
        padding: "0 24px", background: "hsla(240, 15%, 10%, 0.6)",
        backdropFilter: "blur(16px)", zIndex: 50, position: "relative"
      }}
    >
      <div style={{ display: "flex", alignItems: "center", gap: 32 }}>
        <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
          <Rocket size={20} style={{ color: "hsl(var(--primary))" }} />
          <div style={{ fontSize: 18, fontWeight: 700, letterSpacing: "-0.03em", color: "white" }}>
            Creator
          </div>
        </div>

        {/* Center Nav Links */}
        <div style={{ display: "flex", gap: 24, fontSize: 13, fontWeight: 500, color: "hsl(var(--text-secondary))" }}>
          <div style={{ display: "flex", alignItems: "center", gap: 6, cursor: "pointer", color: "white" }} onClick={() => window.location.reload()}><Plus size={14} /> New Story</div>
          <div style={{ display: "flex", alignItems: "center", gap: 6, cursor: "pointer" }} onClick={() => alert("Opening My Library...")}><Library size={14} /> My Library</div>
          <div style={{ display: "flex", alignItems: "center", gap: 6, cursor: "pointer" }} onClick={() => alert("Entering Director Mode...")}><Film size={14} /> Director Mode</div>
        </div>
      </div>

      <div style={{ display: "flex", alignItems: "center", gap: 16 }}>
        <div
          className="rl-pulse"
          style={{
            display: "flex", alignItems: "center", gap: 6, fontSize: 12,
            padding: "4px 10px", borderRadius: 6,
            background: "hsla(160,84%,39%,0.1)", color: "hsl(var(--accent))",
          }}
        >
          <Sparkles size={14} />
          Reward: {rlData?.totalReward?.toFixed(2)}
        </div>
      </div>

      {/* Right: Actions */}
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
