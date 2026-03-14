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
        borderTop: "1px solid var(--glass-border)", borderRight: "1px solid hsla(240, 20%, 30%, 0.3)",
        zIndex: 20, position: "relative", overflow: "hidden", display: "flex", flexDirection: "column"
      }}
    >
      {/* Header bar */}
      <div style={{
        display: "flex", alignItems: "center", justifyContent: "space-between",
        padding: "0 16px", height: 40, background: "hsla(240, 15%, 12%, 0.8)",
        borderBottom: collapsed ? "none" : "1px solid var(--glass-border)",
      }}>
        <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
          <button className="btn-icon" onClick={onToggleCollapse}>
            {collapsed ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
          </button>
          <span style={{ fontSize: 13, fontWeight: 600, color: "hsl(var(--text-primary))", letterSpacing: "0.02em" }}>Timeline</span>
        </div>
        
        <div style={{ display: "flex", gap: 16, alignItems: "center" }}>
          <div style={{ display: "flex", alignItems: "center", gap: 6, fontSize: 11, color: "hsl(var(--text-secondary))", background: "hsla(240,15%,15%,0.6)", padding: "4px 10px", borderRadius: 4, border: "1px solid hsla(240,20%,30%,0.3)" }}>
            <span style={{ color: "hsl(var(--text-muted))" }}>→</span> Drag timelines
          </div>
          <div style={{ display: "flex", alignItems: "center", gap: 6, fontSize: 11, color: "hsl(var(--text-secondary))", background: "hsla(240,15%,15%,0.6)", padding: "4px 10px", borderRadius: 4, border: "1px solid hsla(240,20%,30%,0.3)" }}>
            <span style={{ color: "hsl(var(--accent))" }}>↑</span> Auto-snap keyframes
          </div>
        </div>
      </div>

      {/* Timeline Editor Area */}
      {!collapsed && (
        <div style={{ flex: 1, display: "flex", position: "relative" }}>
          
          {/* Left Track Headers (Video / Audio Track Icons) */}
          <div style={{ width: 60, borderRight: "1px solid hsla(240, 20%, 30%, 0.4)", display: "flex", flexDirection: "column", padding: "30px 0" }}>
            <div style={{ height: 60, display: "flex", alignItems: "center", justifyContent: "center" }}>
              <div style={{ width: 32, height: 32, background: "hsla(240, 15%, 20%, 0.6)", borderRadius: 6, display: "flex", alignItems: "center", justifyContent: "center", border: "1px solid hsla(240,20%,30%,0.5)" }}>
                <span style={{ fontSize: 14 }}>🎬</span>
              </div>
            </div>
            <div style={{ height: 40, display: "flex", alignItems: "center", justifyContent: "center" }}>
              <div style={{ width: 32, height: 32, background: "hsla(240, 15%, 20%, 0.6)", borderRadius: 6, display: "flex", alignItems: "center", justifyContent: "center", border: "1px solid hsla(240,20%,30%,0.5)" }}>
                <span style={{ fontSize: 14 }}>🎵</span>
              </div>
            </div>
          </div>

          {/* Timeline Tracks Grid */}
          <div style={{ flex: 1, position: "relative", overflowX: "auto", overflowY: "hidden", display: "flex", flexDirection: "column" }}>
            
            {/* Time Ruler */}
            <div style={{ height: 20, borderBottom: "1px solid hsla(240,20%,30%,0.3)", display: "flex", fontSize: 10, color: "hsla(255,255%,255%,0.3)" }}>
              {Array(10).fill(0).map((_, i) => (
                <div key={i} style={{ flexShrink: 0, width: 120, borderLeft: "1px solid hsla(255,255%,255%,0.1)", paddingLeft: 4 }}>
                  0{i}:00
                </div>
              ))}
            </div>

            {/* Red Playhead Line */}
            <div style={{ position: "absolute", top: 0, bottom: 0, left: 240, width: 2, background: "hsl(355, 80%, 55%)", zIndex: 10 }}>
              <div style={{ position: "absolute", top: 16, left: -4, width: 10, height: 10, borderRadius: "50%", background: "hsl(355, 80%, 55%)" }} />
            </div>

            {/* Video Track */}
            <div style={{ height: 60, marginTop: 10, display: "flex", paddingLeft: 10, position: "relative", gap: 4 }}>
               {scenes.map((scene, i) => {
                 const isSelected = selectedScene?.id === scene.id;
                 return (
                   <div key={scene.id} onClick={() => onSelectScene(scene)} style={{
                     width: scene.duration * 10, height: "100%", borderRadius: 6, cursor: "pointer",
                     background: isSelected ? "hsla(210, 80%, 30%, 0.6)" : "hsla(263, 60%, 40%, 0.4)",
                     border: isSelected ? "2px solid hsl(210, 80%, 60%)" : "1px solid hsla(263, 60%, 60%, 0.5)",
                     display: "flex", overflow: "hidden"
                   }}>
                     <img src={scene.imageUrl || "/api/placeholder/160/90"} alt="" style={{ height: "100%", opacity: 0.6 }} />
                     {i === 1 && <img src="/api/placeholder/160/90" alt="" style={{ height: "100%", opacity: 0.6 }} />}
                   </div>
                 );
               })}

               {/* Floating Action Buttons */}
               <div style={{ position: "absolute", top: 60, left: 260, display: "flex", gap: 8, zIndex: 20 }}>
                 <button className="btn-ghost" style={{ fontSize: 11, padding: "4px 12px", background: "hsla(240,15%,12%,0.9)", border: "1px solid hsl(var(--border))" }} onClick={() => alert("Extend Scene clicked!")}>
                    [ ] Extend Scene
                 </button>
                 <button className="btn-ghost" style={{ fontSize: 11, padding: "4px 12px", background: "hsla(240,15%,12%,0.9)", border: "1px solid hsl(var(--border))" }} onClick={() => alert("AI Rewrite Dialogue clicked!")}>
                    ✨ AI Rewrite Dialogue
                 </button>
               </div>
            </div>

            {/* Audio Track */}
            <div style={{ height: 40, marginTop: 4, display: "flex", paddingLeft: 10, position: "relative", gap: 4 }}>
               {scenes.map((scene) => (
                   <div key={`audio-${scene.id}`} style={{
                     width: scene.duration * 10, height: 28, borderRadius: 4,
                     background: "hsla(160, 84%, 39%, 0.2)",
                     border: "1px solid hsla(160, 84%, 39%, 0.4)",
                     display: "flex", alignItems: "center", padding: "0 8px", fontSize: 10, color: "hsl(160,84%,60%)"
                   }}>
                     🔊 AI-generated clip
                   </div>
               ))}
            </div>

          </div>
        </div>
      )}
    </motion.div>
  );
}
