"use client";
import { motion } from "framer-motion";
import { Upload, FileText, ImageIcon, Mic, ThumbsUp, ThumbsDown, Sliders, Send, Sparkles, BookOpen } from "lucide-react";
import { useState, useEffect } from "react";
import ReactMarkdown from "react-markdown";

function FeedbackSlider({ label, value, color }) {
  return (
    <div style={{ marginBottom: 10 }}>
      <div style={{ display: "flex", justifyContent: "space-between", fontSize: 11, marginBottom: 4 }}>
        <span style={{ color: "hsl(var(--text-secondary))" }}>{label}</span>
        <span style={{ color, fontWeight: 600 }}>{(value * 100).toFixed(0)}%</span>
      </div>
      <div style={{ position: "relative", height: 6, borderRadius: 3, background: "hsl(var(--bg-hover))" }}>
        <div style={{
          width: `${value * 100}%`, height: "100%", borderRadius: 3, background: color,
          transition: "width 0.3s ease",
        }} />
        <div style={{
          position: "absolute", top: -3, left: `calc(${value * 100}% - 6px)`,
          width: 12, height: 12, borderRadius: "50%", background: color,
          border: "2px solid hsl(var(--bg-primary))",
          cursor: "pointer",
        }} />
      </div>
    </div>
  );
}

export default function RightPanel({ rlData, characters, selectedScene, storybookData, onGenerate, onFeedback, isGenerating }) {
  const [storyInput, setStoryInput] = useState("");
  const [activePreset, setActivePreset] = useState("Cinematic 4K");

  const presets = ["Cinematic 4K", "Pixar Dream", "Anime Epic", "Dark Cyberpunk"];

  return (
    <motion.aside
      initial={{ x: 320, opacity: 0 }}
      animate={{ x: 0, opacity: 1 }}
      transition={{ duration: 0.5, ease: [0.16, 1, 0.3, 1] }}
      style={{
        width: "var(--right-panel-width)", minWidth: "var(--right-panel-width)",
        height: "100%", overflow: "auto",
        background: "var(--glass-bg)", backdropFilter: "blur(16px)",
        borderLeft: "1px solid var(--glass-border)",
        display: "flex", flexDirection: "column", zIndex: 10, position: "relative",
      }}
    >
      <div style={{ padding: 20, display: "flex", flexDirection: "column", gap: 24, flex: 1 }}>
        
        {/* Prompt Section */}
        <div>
          <div className="section-label" style={{ marginBottom: 12 }}>Prompt</div>
          <div className="glow-focus" style={{
            borderRadius: 12, border: "1px solid hsla(240, 20%, 30%, 0.5)",
            background: "hsla(240, 15%, 15%, 0.6)", padding: 2,
            boxShadow: "inset 0 2px 10px hsla(0,0%,0%,0.2)"
          }}>
            <textarea
              value={storyInput}
              onChange={(e) => setStoryInput(e.target.value)}
              placeholder="Direct the storyteller... describe next scene, camera move, emotion, music cue"
              style={{
                width: "100%", height: 120, padding: 12, fontSize: 13, lineHeight: 1.6,
                background: "transparent", border: "none", color: "hsl(var(--text-primary))",
                resize: "none", outline: "none",
              }}
            />
          </div>
        </div>

        {/* Style Presets */}
        <div>
          <div className="section-label" style={{ marginBottom: 12 }}>Style preset</div>
          <div style={{ display: "flex", flexWrap: "wrap", gap: 8 }}>
            {presets.map(p => (
              <button
                key={p}
                onClick={() => setActivePreset(p)}
                style={{
                  padding: "6px 14px", borderRadius: 20, fontSize: 12, fontWeight: 500, cursor: "pointer",
                  background: activePreset === p ? "hsla(260, 80%, 60%, 0.2)" : "transparent",
                  color: activePreset === p ? "hsl(260, 80%, 75%)" : "hsl(var(--text-secondary))",
                  border: activePreset === p ? "1px solid hsl(260, 80%, 60%)" : "1px solid hsla(240, 20%, 30%, 0.4)",
                  transition: "all 0.2s"
                }}
              >
                {p}
              </button>
            ))}
          </div>
        </div>

        {/* Sliders */}
        <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
          <FeedbackSlider label="Duration" value={0.6} color="#8B5CF6" />
          <FeedbackSlider label="Intensity" value={0.8} color="#3B82F6" />
          <FeedbackSlider label="Particle Density" value={0.3} color="#10B981" />
          <FeedbackSlider label="Camera Speed" value={0.5} color="#F59E0B" />
        </div>

        <div style={{ flex: 1 }} />

        {/* Massive Generate Button */}
        <button
          className="btn-primary"
          onClick={() => storyInput.trim() && onGenerate && onGenerate(storyInput)}
          disabled={isGenerating || !storyInput.trim()}
          style={{
            width: "100%", padding: "16px", borderRadius: 12, fontSize: 16, fontWeight: 700,
            textTransform: "uppercase", letterSpacing: "0.05em",
            display: "flex", alignItems: "center", justifyContent: "center", gap: 8,
            opacity: isGenerating || !storyInput.trim() ? 0.6 : 1,
            background: "linear-gradient(135deg, hsl(355, 80%, 55%), hsl(260, 80%, 60%))",
            boxShadow: "0 0 30px hsla(355, 80%, 55%, 0.4)", border: "1px solid hsla(355, 80%, 65%, 0.5)"
          }}
        >
          {isGenerating ? (
            <><div style={{ width: 16, height: 16, borderRadius: "50%", border: "2px solid white", borderTopColor: "transparent", animation: "spin 0.6s linear infinite" }} /> Generating...</>
          ) : (
            <>DIRECT & GENERATE <Send size={18} style={{ transform: "rotate(-45deg) translateY(-2px)" }} /></>
          )}
        </button>

      </div>
    </motion.aside>
  );
}
