"use client";
import { motion } from "framer-motion";
import { Sparkles, Image, Volume2, Wand2, Eye } from "lucide-react";

function SceneCard({ scene, isSelected, characters }) {
  const arcColors = { timid: "#6366F1", determined: "#F59E0B", brave: "#EF4444", heroic: "#10B981" };
  const color = arcColors[scene.trait] || "#8B5CF6";

  return (
    <motion.div
      layout
      whileHover={{ scale: 1.02, y: -2 }}
      style={{
        background: isSelected ? "hsla(263,70%,50%,0.08)" : "var(--glass-bg)",
        backdropFilter: "blur(12px)",
        border: isSelected ? "1px solid hsla(263,70%,50%,0.4)" : "1px solid var(--glass-border)",
        borderRadius: 14, padding: 16, cursor: "pointer",
        boxShadow: isSelected ? "0 0 20px hsla(263,70%,50%,0.15)" : "var(--shadow-sm)",
        transition: "all 0.25s cubic-bezier(0.16,1,0.3,1)",
      }}
    >
      {/* Keyframe placeholder */}
      <div style={{
        width: "100%", aspectRatio: "16/9", borderRadius: 10, marginBottom: 12,
        background: `linear-gradient(135deg, hsl(${240 + scene.id * 15},30%,15%), hsl(${260 + scene.id * 10},40%,20%))`,
        display: "flex", alignItems: "center", justifyContent: "center",
        border: "1px solid hsl(var(--border))",
        position: "relative", overflow: "hidden",
      }}>
        <div style={{
          position: "absolute", top: 0, left: 0, right: 0, bottom: 0,
          background: `radial-gradient(circle at 30% 40%, ${color}22, transparent 60%)`,
        }} />
        <Image size={28} style={{ color: "hsl(var(--text-muted))", opacity: 0.4 }} />
        {/* RL Score badge */}
        <div style={{
          position: "absolute", top: 8, right: 8,
          fontSize: 10, fontWeight: 700, padding: "2px 6px", borderRadius: 4,
          background: "hsla(160,84%,39%,0.2)", color: "hsl(var(--accent))",
          backdropFilter: "blur(8px)",
        }}>
          RL: {scene.rlScore.toFixed(2)}
        </div>
        {/* Arc stage */}
        <div style={{
          position: "absolute", bottom: 8, left: 8,
          fontSize: 10, fontWeight: 600, padding: "2px 8px", borderRadius: 4,
          background: `${color}30`, color: color,
        }}>
          Stage {scene.arcStage}: {scene.trait}
        </div>
      </div>

      {/* Scene info */}
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
        <div>
          <div style={{ fontSize: 14, fontWeight: 600, marginBottom: 2, color: "hsl(var(--text-primary))" }}>
            Scene {scene.id}
          </div>
          <div style={{ fontSize: 12, color: "hsl(var(--text-secondary))", fontStyle: "italic" }}>
            {scene.title}
          </div>
        </div>
        <div style={{ textAlign: "right" }}>
          <div style={{ fontSize: 11, color: "hsl(var(--text-muted))" }}>{scene.shots} shots</div>
          <div style={{ fontSize: 11, color: "hsl(var(--text-muted))" }}>{scene.duration}s</div>
        </div>
      </div>

      {/* Interleaved preview markers */}
      <div style={{ display: "flex", gap: 4, marginTop: 10 }}>
        {[
          { icon: <Eye size={10} />, label: "Narration" },
          { icon: <Image size={10} />, label: "Image" },
          { icon: <Volume2 size={10} />, label: "Audio" },
          { icon: <Sparkles size={10} />, label: "Effects" },
        ].map((item, i) => (
          <div key={i} style={{
            flex: 1, display: "flex", alignItems: "center", justifyContent: "center", gap: 3,
            fontSize: 9, padding: "3px 0", borderRadius: 4,
            background: "hsl(var(--bg-tertiary))", color: "hsl(var(--text-muted))",
          }}>
            {item.icon} {item.label}
          </div>
        ))}
      </div>
    </motion.div>
  );
}

export default function CenterCanvas({ scenes, selectedScene, rlData, characters }) {
  return (
    <motion.main
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6, delay: 0.2 }}
      style={{
        flex: 1, overflow: "auto", padding: 24, position: "relative", zIndex: 1,
      }}
    >
      {/* Canvas header */}
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 20 }}>
        <div>
          <h1 style={{ fontSize: 20, fontWeight: 700, marginBottom: 4 }}>Storyboard Canvas</h1>
          <p style={{ fontSize: 13, color: "hsl(var(--text-secondary))" }}>
            {scenes.length} scenes • {scenes.reduce((a, s) => a + s.shots, 0)} shots •
            <span style={{ color: "hsl(var(--accent))", marginLeft: 4 }}>
              RL Score: {rlData.totalReward.toFixed(2)}
            </span>
          </p>
        </div>

        <div style={{ display: "flex", gap: 8 }}>
          <button className="btn-ghost"><Eye size={14} /> Preview</button>
          <button className="btn-primary">
            <Wand2 size={14} /> RL Enhance
          </button>
        </div>
      </div>

      {/* Reward bars */}
      <div className="glass-card" style={{ padding: 14, marginBottom: 20, display: "flex", gap: 12 }}>
        {[
          { label: "Coherence", value: rlData.coherence, color: "#8B5CF6" },
          { label: "Creativity", value: rlData.creativity, color: "#3B82F6" },
          { label: "Consistency", value: rlData.consistency, color: "#10B981" },
          { label: "Emotional", value: rlData.emotional, color: "#F59E0B" },
          { label: "Technical", value: rlData.technical, color: "#EF4444" },
        ].map((dim) => (
          <div key={dim.label} style={{ flex: 1, minWidth: 0 }}>
            <div style={{ display: "flex", justifyContent: "space-between", fontSize: 10, marginBottom: 4, color: "hsl(var(--text-muted))" }}>
              <span>{dim.label}</span>
              <span style={{ color: dim.color, fontWeight: 600 }}>{(dim.value * 100).toFixed(0)}%</span>
            </div>
            <div style={{ height: 4, borderRadius: 2, background: "hsl(var(--bg-hover))" }}>
              <motion.div
                initial={{ width: 0 }}
                animate={{ width: `${dim.value * 100}%` }}
                transition={{ duration: 1, delay: 0.5 }}
                style={{ height: "100%", borderRadius: 2, background: dim.color }}
              />
            </div>
          </div>
        ))}
      </div>

      {/* Scene Grid */}
      <div style={{
        display: "grid",
        gridTemplateColumns: "repeat(auto-fill, minmax(280px, 1fr))",
        gap: 16,
      }}>
        {scenes.map((scene) => (
          <SceneCard
            key={scene.id}
            scene={scene}
            isSelected={selectedScene?.id === scene.id}
            characters={characters}
          />
        ))}
      </div>
    </motion.main>
  );
}
