"use client";
import { motion } from "framer-motion";
import { Sparkles, Image, Volume2, Wand2, Eye, Sliders } from "lucide-react";

function SceneCard({ scene, isSelected, characters }) {
  const arcColors = { timid: "#6366F1", determined: "#F59E0B", brave: "#EF4444", heroic: "#10B981" };
  const color = arcColors[scene.trait] || "#8B5CF6";

  return (
    <motion.div
      layout
      whileHover={{ scale: 1.02, y: -4, boxShadow: "0 12px 30px hsla(263,70%,50%,0.2)" }}
      style={{
        background: isSelected ? "hsla(263,70%,50%,0.08)" : "hsla(240, 15%, 15%, 0.4)",
        backdropFilter: "blur(16px)",
        border: isSelected ? "1px solid hsla(263,70%,60%,0.5)" : "1px solid hsla(240, 20%, 30%, 0.3)",
        boxShadow: isSelected ? "0 0 20px hsla(263,70%,50%,0.15), inset 0 1px 0 hsla(255,255%,255%,0.05)" : "inset 0 1px 0 hsla(255,255%,255%,0.05), 0 4px 12px hsla(0,0%,0%,0.2)",
        borderRadius: 16, padding: 16, cursor: "pointer",
        transition: "all 0.3s cubic-bezier(0.16,1,0.3,1)",
      }}
    >
      {/* Keyframe outline */}
      <div style={{
        width: "100%", aspectRatio: "16/9", borderRadius: 10, marginBottom: 12,
        background: scene.imageUrl ? "black" : `linear-gradient(135deg, hsl(${240 + scene.id * 15},30%,15%), hsl(${260 + scene.id * 10},40%,20%))`,
        display: "flex", alignItems: "center", justifyContent: "center",
        border: "1px solid hsl(var(--border))",
        position: "relative", overflow: "hidden",
      }}>
        {!scene.imageUrl && (
          <>
            <div style={{
              position: "absolute", top: 0, left: 0, right: 0, bottom: 0,
              background: `radial-gradient(circle at 30% 40%, ${color}22, transparent 60%)`,
            }} />
            <Image size={28} style={{ color: "hsl(var(--text-muted))", opacity: 0.4 }} />
          </>
        )}
        {scene.imageUrl && (
          <img 
            src={scene.imageUrl} 
            alt={scene.title}
            style={{ width: "100%", height: "100%", objectFit: "cover", opacity: 0.9 }} 
          />
        )}
        {/* RL Score badge */}
        <div className="badge-pill-pulse" style={{
          position: "absolute", top: 8, right: 8,
          fontSize: 10, fontWeight: 700,
          backdropFilter: "blur(12px)",
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

export default function CenterCanvas({ rlData, selectedScene }) {
  if (!selectedScene) return null;

  return (
    <motion.main
      initial={{ opacity: 0, scale: 0.98 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.6, ease: [0.16, 1, 0.3, 1] }}
      style={{
        flex: 1, height: "100%", display: "flex", flexDirection: "column",
        alignItems: "center", justifyContent: "center", position: "relative", zIndex: 1,
      }}
    >
      {/* 16:9 Cinematic Frame */}
      <div style={{
        width: "100%", maxWidth: 1000, aspectRatio: "16/9", position: "relative",
        background: "var(--bg-primary)", borderRadius: 16, border: "1px solid hsla(240, 20%, 30%, 0.4)",
        boxShadow: "0 20px 50px hsla(0,0%,0%,0.5)", overflow: "hidden", display: "flex", flexDirection: "column"
      }}>
        {/* Main Image Area */}
        <div style={{ flex: 1, position: "relative", background: "black" }}>
          <img 
            src={selectedScene.imageUrl || "/api/placeholder/1600/900"} 
            alt="Current Scene" 
            style={{ width: "100%", height: "100%", objectFit: "cover", filter: "contrast(1.1) brightness(0.9)" }} 
          />

          {/* Director HUD Overlays */}
          <div style={{ position: "absolute", top: 0, left: 0, right: 0, bottom: 0, pointerEvents: "none" }}>
             {/* Center Reticle */}
             <div style={{
               position: "absolute", top: "50%", left: "50%", transform: "translate(-50%, -50%)",
               width: 300, height: 300, border: "1px solid hsla(255,255%,255%,0.15)", borderRadius: "50%",
               boxShadow: "0 0 40px hsla(255,255%,255%,0.05)"
             }} />
             <div style={{
               position: "absolute", top: "50%", left: "50%", transform: "translate(-50%, -50%)",
               width: 400, height: 400, border: "1px solid hsla(255,255%,255%,0.05)", borderRadius: "50%"
             }} />

             {/* Crosshairs */}
             <div style={{ position: "absolute", top: "48%", left: "50%", width: 1, height: 8, background: "hsla(255,255%,255%,0.5)" }} />
             <div style={{ position: "absolute", bottom: "48%", left: "50%", width: 1, height: 8, background: "hsla(255,255%,255%,0.5)" }} />
             <div style={{ position: "absolute", left: "48%", top: "50%", width: 8, height: 1, background: "hsla(255,255%,255%,0.5)" }} />
             <div style={{ position: "absolute", right: "48%", top: "50%", width: 8, height: 1, background: "hsla(255,255%,255%,0.5)" }} />

             {/* AI Suggest Tags */}
             <motion.div animate={{ y: [0, -5, 0] }} transition={{ repeat: Infinity, duration: 4 }} style={{
               position: "absolute", top: "20%", right: "25%",
               background: "hsla(240, 15%, 15%, 0.8)", backdropFilter: "blur(8px)",
               border: "1px solid hsla(240, 20%, 30%, 0.5)", color: "white", fontSize: 11, fontWeight: 600,
               padding: "6px 12px", borderRadius: 20, display: "flex", gap: 6, alignItems: "center"
             }}>
               <Sparkles size={12} style={{ color: "hsl(var(--primary))" }} /> AI Suggest
             </motion.div>
             
             <motion.div animate={{ y: [0, 5, 0] }} transition={{ repeat: Infinity, duration: 5 }} style={{
               position: "absolute", bottom: "30%", left: "20%",
               background: "hsla(240, 15%, 15%, 0.8)", backdropFilter: "blur(8px)",
               border: "1px solid hsla(240, 20%, 30%, 0.5)", color: "white", fontSize: 11, fontWeight: 600,
               padding: "6px 12px", borderRadius: 20, display: "flex", gap: 6, alignItems: "center"
             }}>
               <Wand2 size={12} style={{ color: "hsl(var(--accent))" }} /> Enhance Lighting
             </motion.div>

             {/* Tracking markers */}
             <div style={{ position: "absolute", top: "45%", left: "15%", fontSize: 10, color: "hsla(255,255%,255%,0.5)", letterSpacing: 2 }}>40</div>
             <div style={{ position: "absolute", top: "45%", right: "15%", fontSize: 10, color: "hsla(255,255%,255%,0.5)", letterSpacing: 2 }}>0</div>
          </div>
        </div>

        {/* Player Controls Bar */}
        <div style={{
          height: 48, background: "hsla(240, 15%, 8%, 0.9)", backdropFilter: "blur(10px)",
          borderTop: "1px solid hsla(240, 20%, 30%, 0.4)", display: "flex", alignItems: "center", padding: "0 16px", gap: 16
        }}>
           <div style={{ fontSize: 12, fontWeight: 500, fontFamily: "monospace", color: "hsl(var(--text-secondary))" }}>16:00 / 5:30</div>
           
           {/* Playback Scrubber */}
           <div style={{ flex: 1, height: 4, background: "hsla(240, 20%, 30%, 0.5)", borderRadius: 2, position: "relative", cursor: "pointer" }}>
             <div style={{ position: "absolute", left: 0, top: 0, bottom: 0, width: "35%", background: "hsl(355, 80%, 55%)", borderRadius: 2 }} />
             <div style={{ position: "absolute", left: "35%", top: -4, width: 12, height: 12, borderRadius: "50%", background: "white", border: "2px solid hsl(355, 80%, 55%)", boxShadow: "0 0 10px hsla(355,80%,55%,0.5)" }} />
           </div>

           {/* Play Controls */}
           <div style={{ display: "flex", alignItems: "center", gap: 12, color: "hsl(var(--text-primary))" }}>
             <button className="btn-icon"><svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><polygon points="19 20 9 12 19 4 19 20"></polygon><line x1="5" y1="19" x2="5" y2="5"></line></svg></button>
             <button className="btn-icon" style={{ color: "white" }}><svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><polygon points="5 3 19 12 5 21 5 3"></polygon></svg></button>
             <button className="btn-icon"><svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><polygon points="5 4 15 12 5 20 5 4"></polygon><line x1="19" y1="5" x2="19" y2="19"></line></svg></button>
           </div>
           
           <div style={{ width: 1, height: 16, background: "hsla(240, 20%, 30%, 0.5)" }} />
           
           {/* Settings/Volume */}
           <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
             <button className="btn-icon"><Volume2 size={14} /></button>
             <button className="btn-icon"><Sliders size={14} /></button>
           </div>
        </div>
      </div>
    </motion.main>
  );
}
