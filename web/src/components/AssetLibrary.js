"use client";
import { motion } from "framer-motion";
import { X, Search, Image, User, History, Wand2 } from "lucide-react";
import { useState } from "react";

const TABS = [
  { id: "frames", label: "Keyframes", icon: <Image size={14} /> },
  { id: "characters", label: "Characters", icon: <User size={14} /> },
  { id: "rl", label: "RL Episodes", icon: <History size={14} /> },
];

const MOCK_ASSETS = {
  frames: Array(8).fill(0).map((_, i) => ({
    id: `kf_${i + 1}`, name: `S${Math.floor(i / 2) + 1}_Shot${(i % 2) + 1}.png`,
    scene: Math.floor(i / 2) + 1, shot: (i % 2) + 1,
  })),
  characters: [
    { id: "elara_sheet", name: "Elara — Character Sheet", type: "sheet" },
    { id: "kai_sheet", name: "Kai — Character Sheet", type: "sheet" },
  ],
  rl: Array(3).fill(0).map((_, i) => ({
    id: `ep_${i + 1}`, name: `Episode ${i + 1}`,
    reward: (0.75 + i * 0.06).toFixed(2), policy: `v${i + 1}`,
  })),
};

export default function AssetLibrary({ onClose }) {
  const [activeTab, setActiveTab] = useState("frames");
  const [search, setSearch] = useState("");

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      style={{
        position: "fixed", inset: 0, background: "hsla(0,0%,0%,0.6)",
        backdropFilter: "blur(8px)", zIndex: 100,
        display: "flex", alignItems: "center", justifyContent: "center",
      }}
      onClick={onClose}
    >
      <motion.div
        initial={{ scale: 0.9, opacity: 0, y: 20 }}
        animate={{ scale: 1, opacity: 1, y: 0 }}
        exit={{ scale: 0.9, opacity: 0, y: 20 }}
        transition={{ type: "spring", damping: 25, stiffness: 300 }}
        onClick={(e) => e.stopPropagation()}
        className="glass-card-elevated"
        style={{
          width: "min(90vw, 800px)", height: "min(80vh, 600px)",
          display: "flex", flexDirection: "column", overflow: "hidden",
        }}
      >
        {/* Header */}
        <div style={{
          display: "flex", alignItems: "center", justifyContent: "space-between",
          padding: "16px 20px", borderBottom: "1px solid var(--glass-border)",
        }}>
          <h2 style={{ fontSize: 16, fontWeight: 700 }}>Asset Library</h2>
          <button className="btn-icon" onClick={onClose}><X size={18} /></button>
        </div>

        {/* Tabs + Search */}
        <div style={{
          display: "flex", alignItems: "center", padding: "10px 20px",
          gap: 8, borderBottom: "1px solid var(--glass-border)",
        }}>
          {TABS.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              style={{
                display: "flex", alignItems: "center", gap: 6,
                padding: "6px 12px", borderRadius: 6, fontSize: 12, fontWeight: 500,
                background: activeTab === tab.id ? "hsl(var(--primary))" : "transparent",
                color: activeTab === tab.id ? "white" : "hsl(var(--text-secondary))",
                border: activeTab === tab.id ? "none" : "1px solid hsl(var(--border))",
                cursor: "pointer", transition: "all 0.2s ease",
              }}
            >
              {tab.icon} {tab.label}
            </button>
          ))}
          <div style={{ flex: 1 }} />
          <div style={{
            display: "flex", alignItems: "center", gap: 6,
            padding: "6px 10px", borderRadius: 6,
            background: "hsl(var(--bg-secondary))", border: "1px solid hsl(var(--border))",
          }}>
            <Search size={12} style={{ color: "hsl(var(--text-muted))" }} />
            <input
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Search assets..."
              style={{
                background: "transparent", border: "none", outline: "none",
                fontSize: 12, color: "hsl(var(--text-primary))", width: 120,
              }}
            />
          </div>
        </div>

        {/* Grid */}
        <div style={{ flex: 1, overflow: "auto", padding: 20 }}>
          {activeTab === "frames" && (
            <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(160px, 1fr))", gap: 12 }}>
              {MOCK_ASSETS.frames.map((asset) => (
                <motion.div
                  key={asset.id}
                  whileHover={{ scale: 1.03, y: -2 }}
                  className="glass-card glow-hover"
                  style={{ padding: 8, cursor: "pointer" }}
                >
                  <div style={{
                    width: "100%", aspectRatio: "16/9", borderRadius: 8, marginBottom: 8,
                    background: `linear-gradient(135deg, hsl(${240 + asset.scene * 20},30%,18%), hsl(${260 + asset.scene * 15},40%,22%))`,
                    display: "flex", alignItems: "center", justifyContent: "center",
                  }}>
                    <Image size={20} style={{ color: "hsl(var(--text-muted))", opacity: 0.4 }} />
                  </div>
                  <div style={{ fontSize: 11, fontWeight: 500 }}>{asset.name}</div>
                  <div style={{ fontSize: 10, color: "hsl(var(--text-muted))", display: "flex", justifyContent: "space-between", marginTop: 4 }}>
                    <span>Scene {asset.scene}, Shot {asset.shot}</span>
                    <button style={{
                      background: "none", border: "none", cursor: "pointer", display: "flex",
                      alignItems: "center", gap: 2, fontSize: 10, color: "hsl(var(--primary))",
                    }}>
                      <Wand2 size={10} /> Regen
                    </button>
                  </div>
                </motion.div>
              ))}
            </div>
          )}

          {activeTab === "characters" && (
            <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(200px, 1fr))", gap: 12 }}>
              {MOCK_ASSETS.characters.map((asset) => (
                <motion.div
                  key={asset.id}
                  whileHover={{ scale: 1.03 }}
                  className="glass-card glow-hover"
                  style={{ padding: 12, cursor: "pointer", display: "flex", alignItems: "center", gap: 12 }}
                >
                  <div style={{
                    width: 48, height: 48, borderRadius: 8, flexShrink: 0,
                    background: "linear-gradient(135deg, hsl(263,60%,40%), hsl(200,60%,40%))",
                    display: "flex", alignItems: "center", justifyContent: "center",
                  }}>
                    <User size={20} color="white" />
                  </div>
                  <div>
                    <div style={{ fontSize: 13, fontWeight: 500 }}>{asset.name}</div>
                    <div style={{ fontSize: 10, color: "hsl(var(--text-muted))" }}>Character Sheet</div>
                  </div>
                </motion.div>
              ))}
            </div>
          )}

          {activeTab === "rl" && (
            <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
              {MOCK_ASSETS.rl.map((ep) => (
                <motion.div
                  key={ep.id}
                  whileHover={{ x: 4 }}
                  className="glass-card"
                  style={{
                    padding: 12, cursor: "pointer",
                    display: "flex", alignItems: "center", justifyContent: "space-between",
                  }}
                >
                  <div>
                    <div style={{ fontSize: 13, fontWeight: 500 }}>{ep.name}</div>
                    <div style={{ fontSize: 11, color: "hsl(var(--text-muted))" }}>Policy {ep.policy}</div>
                  </div>
                  <div style={{ textAlign: "right" }}>
                    <span className="badge badge-success">Reward: {ep.reward}</span>
                  </div>
                </motion.div>
              ))}
            </div>
          )}
        </div>
      </motion.div>
    </motion.div>
  );
}
