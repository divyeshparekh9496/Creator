"use client";
import { motion } from "framer-motion";
import { ChevronUp, ChevronDown, GripVertical } from "lucide-react";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

function getImageUrl(url) {
  if (!url) return null;
  if (url.startsWith("http")) return url;
  if (url.startsWith("/output/")) return `${API_BASE}${url}`;
  if (url.startsWith("data/output/")) return `${API_BASE}/output/${url.replace("data/output/", "")}`;
  return url;
}

export default function TimelineEditor({ scenes, selectedScene, onSelectScene, collapsed, onToggleCollapse }) {
  const sceneList = scenes || [];
  const totalDuration = sceneList.reduce((acc, s) => acc + (s.duration || 3), 0);
  const pixelsPerSecond = Math.max(20, 400 / totalDuration);

  return (
    <motion.div
      initial={{ y: 200 }}
      animate={{ y: 0, height: collapsed ? 44 : "var(--timeline-height)" }}
      transition={{ duration: 0.4, ease: [0.16, 1, 0.3, 1] }}
      style={{
        background: "var(--glass-bg)", backdropFilter: "blur(20px)",
        borderTop: "1px solid var(--glass-border)",
        zIndex: 20, position: "relative", overflow: "hidden",
        display: "flex", flexDirection: "column",
      }}
    >
      <div
        className="panel-controls"
        style={{
          display: "flex", alignItems: "center", justifyContent: "space-between",
          padding: "0 16px", height: 44,
          borderBottom: collapsed ? "none" : "1px solid hsl(var(--border))",
        }}
      >
        <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
          <button className="btn-icon" onClick={onToggleCollapse} style={{ width: 32, height: 32 }}>
            {collapsed ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
          </button>
          <span style={{ fontSize: 13, fontWeight: 600, color: "hsl(var(--text-primary))" }}>Timeline</span>
          <span style={{ fontSize: 11, color: "hsl(var(--text-muted))" }}>{sceneList.length} scenes · ~{totalDuration}s</span>
        </div>
        <div style={{ display: "flex", alignItems: "center", gap: 8, fontSize: 11, color: "hsl(var(--text-muted))" }}>
          <span>Drag to reorder</span>
        </div>
      </div>

      {!collapsed && (
        <div style={{ flex: 1, display: "flex", overflow: "hidden" }}>
          <div style={{ width: 50, borderRight: "1px solid hsl(var(--border))", display: "flex", flexDirection: "column", padding: "24px 0" }}>
            <div style={{ height: 50, display: "flex", alignItems: "center", justifyContent: "center" }}>
              <div style={{
                width: 28, height: 28, borderRadius: 6,
                background: "hsl(var(--primary) / 0.2)",
                border: "1px solid hsl(var(--primary) / 0.4)",
                display: "flex", alignItems: "center", justifyContent: "center",
                fontSize: 12,
              }}>🎬</div>
            </div>
            <div style={{ height: 36, display: "flex", alignItems: "center", justifyContent: "center" }}>
              <div style={{
                width: 28, height: 28, borderRadius: 6,
                background: "hsl(var(--accent) / 0.2)",
                border: "1px solid hsl(var(--accent) / 0.4)",
                display: "flex", alignItems: "center", justifyContent: "center",
                fontSize: 12,
              }}>🔊</div>
            </div>
          </div>

          <div style={{ flex: 1, overflowX: "auto", overflowY: "hidden", position: "relative" }}>
            <div style={{ minWidth: Math.max(500, totalDuration * pixelsPerSecond), padding: "12px 16px", display: "flex", flexDirection: "column", gap: 8 }}>
              <div style={{ height: 18, display: "flex", fontSize: 10, color: "hsl(var(--text-muted))" }}>
                {Array.from({ length: Math.ceil(totalDuration / 5) + 1 }, (_, i) => (
                  <div key={i} style={{ width: pixelsPerSecond * 5, flexShrink: 0, paddingLeft: 4 }}>
                    {i * 5}s
                  </div>
                ))}
              </div>

              <div style={{ height: 52, display: "flex", alignItems: "center", gap: 4 }}>
                {sceneList.length > 0 ? (
                  sceneList.map((scene, i) => {
                    const isSelected = selectedScene && (selectedScene.id ?? selectedScene.scene_id) === (scene.id ?? scene.scene_id);
                    const w = (scene.duration || 3) * pixelsPerSecond;
                    const thumbUrl = getImageUrl(scene.imageUrl);
                    return (
                      <motion.button
                        key={scene.id ?? scene.scene_id ?? i}
                        whileHover={{ scale: 1.02 }}
                        onClick={() => onSelectScene?.(scene)}
                        title="Click to select scene"
                        aria-label={`Select scene ${scene.id ?? i + 1}`}
                        style={{
                          flexShrink: 0, width: Math.max(w, 60), height: "100%", borderRadius: 8,
                          position: "relative",
                          background: isSelected ? "hsl(var(--primary) / 0.35)" : "hsl(var(--primary) / 0.2)",
                          border: isSelected ? "2px solid hsl(var(--primary))" : "1px solid hsl(var(--border))",
                          overflow: "hidden", cursor: "pointer", padding: 0, display: "flex",
                        }}
                      >
                        {thumbUrl ? (
                          <img src={thumbUrl} alt="" style={{ width: "100%", height: "100%", objectFit: "cover", opacity: 0.9 }} />
                        ) : (
                          <div style={{
                            width: "100%", height: "100%",
                            background: "hsl(var(--bg-tertiary))",
                            display: "flex", alignItems: "center", justifyContent: "center",
                            fontSize: 11, color: "hsl(var(--text-muted))",
                          }}>
                            S{scene.id ?? i + 1}
                          </div>
                        )}
                        <div style={{
                          position: "absolute", bottom: 2, left: 4, right: 4,
                          fontSize: 9, color: "white", textShadow: "0 1px 2px black",
                          overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap",
                        }}>
                          {scene.title || `Scene ${i + 1}`}
                        </div>
                      </motion.button>
                    );
                  })
                ) : (
                  <div style={{
                    flex: 1, height: "100%", borderRadius: 8,
                    background: "hsl(var(--bg-tertiary) / 0.6)",
                    border: "1px dashed hsl(var(--border))",
                    display: "flex", alignItems: "center", justifyContent: "center",
                    fontSize: 12, color: "hsl(var(--text-muted))",
                  }}>
                    Generate a story to build the timeline
                  </div>
                )}
              </div>

              <div style={{ height: 36, display: "flex", alignItems: "center", gap: 4 }}>
                {sceneList.map((scene, i) => {
                  const w = (scene.duration || 3) * pixelsPerSecond;
                  return (
                    <div
                      key={`audio-${scene.id ?? i}`}
                      style={{
                        flexShrink: 0, width: Math.max(w, 60), height: 28, borderRadius: 6,
                        background: "hsl(var(--accent) / 0.12)",
                        border: "1px solid hsl(var(--accent) / 0.3)",
                        display: "flex", alignItems: "center", padding: "0 8px",
                        fontSize: 10, color: "hsl(160, 70%, 55%)",
                      }}
                    >
                      🔊 AI
                    </div>
                  );
                })}
                {sceneList.length === 0 && (
                  <div style={{ flex: 1, height: 28, borderRadius: 6, background: "hsl(var(--bg-tertiary) / 0.5)", border: "1px dashed hsl(var(--border))" }} />
                )}
              </div>
            </div>
          </div>
        </div>
      )}
    </motion.div>
  );
}
