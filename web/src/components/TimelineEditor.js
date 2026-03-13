"use client";
import { motion } from "framer-motion";
import { ChevronUp, ChevronDown, Play, GripVertical, RotateCcw } from "lucide-react";

export default function TimelineEditor({ scenes, selectedScene, onSelectScene, collapsed, onToggleCollapse }) {
  return (
    <motion.div
      initial={{ y: 200 }}
      animate={{ y: 0, height: collapsed ? 40 : "var(--timeline-height)" }}
      transition={{ duration: 0.4, ease: [0.16, 1, 0.3, 1] }}
      style={{
        background: "var(--glass-bg)", backdropFilter: "blur(20px)",
        borderTop: "1px solid var(--glass-border)",
        zIndex: 20, position: "relative", overflow: "hidden",
      }}
    >
      {/* Header bar */}
      <div style={{
        display: "flex", alignItems: "center", justifyContent: "space-between",
        padding: "0 16px", height: 40,
        borderBottom: collapsed ? "none" : "1px solid var(--glass-border)",
      }}>
        <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
          <button className="btn-icon" onClick={onToggleCollapse}>
            {collapsed ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
          </button>
          <span style={{ fontSize: 12, fontWeight: 600, color: "hsl(var(--text-primary))" }}>Timeline</span>
          <span style={{ fontSize: 11, color: "hsl(var(--text-muted))" }}>
            {scenes.length} scenes • {scenes.reduce((a, s) => a + s.duration, 0)}s total
          </span>
        </div>
        <div style={{ display: "flex", gap: 6 }}>
          <button className="btn-ghost" style={{ fontSize: 11, padding: "4px 10px" }}>
            <RotateCcw size={12} /> Re-run Pipeline
          </button>
          <button className="btn-primary" style={{ fontSize: 11, padding: "4px 10px" }}>
            <Play size={12} /> Preview
          </button>
        </div>
      </div>

      {/* Timeline strips */}
      {!collapsed && (
        <div style={{
          display: "flex", gap: 8, padding: "12px 16px",
          overflowX: "auto", overflowY: "hidden", height: "calc(100% - 40px)",
        }}>
          {scenes.map((scene) => {
            const isSelected = selectedScene?.id === scene.id;
            const arcColors = { timid: "#6366F1", determined: "#F59E0B", brave: "#EF4444", heroic: "#10B981" };
            const color = arcColors[scene.trait] || "#8B5CF6";

            return (
              <motion.div
                key={scene.id}
                layout
                whileHover={{ scale: 1.02, y: -2 }}
                onClick={() => onSelectScene(scene)}
                style={{
                  minWidth: `${Math.max(scene.duration * 8, 120)}px`,
                  height: "100%", borderRadius: 10, cursor: "pointer",
                  background: isSelected ? "hsla(263,70%,50%,0.12)" : "hsl(var(--bg-tertiary))",
                  border: isSelected ? `2px solid ${color}` : "1px solid hsl(var(--border))",
                  padding: 10, display: "flex", flexDirection: "column",
                  position: "relative", overflow: "hidden",
                  transition: "all 0.2s ease",
                }}
              >
                {/* Drag handle */}
                <GripVertical size={12} style={{
                  position: "absolute", top: 4, left: 4,
                  color: "hsl(var(--text-muted))", opacity: 0.4,
                }} />

                {/* Arc gradient bar */}
                <div style={{
                  width: "100%", height: 3, borderRadius: 2, marginBottom: 6,
                  background: `linear-gradient(90deg, ${color}60, ${color})`,
                }} />

                {/* Scene info */}
                <div style={{ fontSize: 11, fontWeight: 600, marginBottom: 2, color: "hsl(var(--text-primary))" }}>
                  S{scene.id}
                </div>
                <div style={{ fontSize: 10, color: "hsl(var(--text-secondary))", flex: 1, overflow: "hidden", textOverflow: "ellipsis" }}>
                  {scene.title}
                </div>

                {/* Bottom row: badges */}
                <div style={{ display: "flex", gap: 4, marginTop: 6, flexWrap: "wrap" }}>
                  <span className="badge" style={{ background: `${color}25`, color }}>
                    {scene.trait}
                  </span>
                  <span className="badge badge-success">
                    RL: {scene.rlScore.toFixed(2)}
                  </span>
                </div>

                {/* Shot markers */}
                <div style={{ display: "flex", gap: 3, marginTop: 6 }}>
                  {Array(scene.shots).fill(0).map((_, i) => (
                    <div
                      key={i}
                      style={{
                        flex: 1, height: 4, borderRadius: 2,
                        background: i < 2 ? color : "hsl(var(--bg-hover))",
                      }}
                    />
                  ))}
                </div>
              </motion.div>
            );
          })}
        </div>
      )}
    </motion.div>
  );
}
