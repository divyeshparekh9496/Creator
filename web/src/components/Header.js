"use client";
import { motion } from "framer-motion";
import { Sparkles, Moon, Sun, FolderOpen, Download, Zap, Film } from "lucide-react";

export default function Header({ theme, onToggleTheme, onOpenAssets, onOpenExport, rlData }) {
  return (
    <motion.header
      initial={{ y: -56, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      transition={{ duration: 0.5, ease: [0.16, 1, 0.3, 1] }}
      style={{
        height: "var(--header-height)", display: "flex", alignItems: "center",
        justifyContent: "space-between", padding: "0 20px",
        background: "var(--glass-bg)", backdropFilter: "blur(16px)",
        borderBottom: "1px solid var(--glass-border)", zIndex: 50,
        position: "relative",
      }}
    >
      {/* Left: Logo */}
      <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
        <div style={{
          width: 32, height: 32, borderRadius: 8,
          background: "linear-gradient(135deg, hsl(263,70%,50%), hsl(220,70%,50%))",
          display: "flex", alignItems: "center", justifyContent: "center",
          boxShadow: "0 0 16px hsla(263,70%,50%,0.4)",
        }}>
          <Film size={18} color="white" />
        </div>
        <span style={{ fontWeight: 700, fontSize: 16, letterSpacing: "-0.02em" }}>
          Creator
        </span>
        <span style={{
          fontSize: 10, fontWeight: 600, padding: "2px 6px", borderRadius: 4,
          background: "hsla(263,70%,50%,0.15)", color: "hsl(263,70%,65%)",
        }}>
          v1.0
        </span>
      </div>

      {/* Center: Pipeline status */}
      <div style={{ display: "flex", alignItems: "center", gap: 16 }}>
        <motion.div
          animate={{ opacity: [0.5, 1, 0.5] }}
          transition={{ duration: 2, repeat: Infinity }}
          style={{ display: "flex", alignItems: "center", gap: 6, fontSize: 12, color: "hsl(var(--accent))" }}
        >
          <Zap size={14} />
          <span>RL Policy {rlData?.policyVersion} • Episode {rlData?.episode}</span>
        </motion.div>

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
