"use client";
import { motion } from "framer-motion";
import { ThumbsUp, ThumbsDown, Send, Sliders, Sparkles } from "lucide-react";
import { useState } from "react";

const PRESETS = [
  { id: "cinematic", label: "Cinematic 4K", desc: "Film-like composition" },
  { id: "pixar", label: "Pixar Dream", desc: "3D animated style" },
  { id: "anime", label: "Anime Epic", desc: "Dramatic anime" },
  { id: "cyberpunk", label: "Dark Cyberpunk", desc: "Neon noir" },
];

function SliderControl({ label, value, onChange }) {
  return (
    <div className="panel-card-subtle" style={{
      marginBottom: 16,
      padding: "12px 14px",
      borderRadius: 10,
      backdropFilter: "blur(12px)",
    }}>
      <div style={{ display: "flex", justifyContent: "space-between", fontSize: 11, marginBottom: 8 }}>
        <span style={{ color: "hsl(var(--text-secondary))", fontWeight: 500 }}>{label}</span>
        <span style={{ color: "hsl(var(--text-primary))", fontWeight: 600 }}>{Math.round(value * 100)}%</span>
      </div>
      <input
        type="range"
        min={0}
        max={100}
        value={value * 100}
        onChange={(e) => onChange(Number(e.target.value) / 100)}
        style={{
          width: "100%", height: 6, borderRadius: 3,
          cursor: "pointer",
          background: "hsl(var(--border))",
        }}
        className="slider-industrial"
      />
    </div>
  );
}

export default function RightPanel({ storyInput: controlledStory, onStoryChange, storyInputRef, rlData, characters, selectedScene, storybookData, onGenerate, onFeedback, isGenerating }) {
  const [internalStory, setInternalStory] = useState("");
  const storyInput = controlledStory !== undefined ? controlledStory : internalStory;
  const setStoryInput = onStoryChange || setInternalStory;

  const [activePreset, setActivePreset] = useState("anime");
  const [sliders, setSliders] = useState({
    duration: 0.6,
    intensity: 0.8,
    particleDensity: 0.3,
    cameraSpeed: 0.5,
  });
  const [feedbackSent, setFeedbackSent] = useState(null);

  const updateSlider = (key, value) => {
    setSliders((prev) => ({ ...prev, [key]: value }));
  };

  const handleFeedback = async (positive) => {
    if (!onFeedback) return;
    setFeedbackSent(positive ? "up" : "down");
    await onFeedback(positive);
    setTimeout(() => setFeedbackSent(null), 2000);
  };

  return (
    <motion.aside
      initial={{ x: 320, opacity: 0 }}
      animate={{ x: 0, opacity: 1 }}
      transition={{ duration: 0.5, ease: [0.16, 1, 0.3, 1] }}
      style={{
        width: "var(--right-panel-width)", minWidth: "var(--right-panel-width)",
        height: "100%", overflow: "auto",
        background: "var(--glass-bg)",
        backdropFilter: "blur(24px)", WebkitBackdropFilter: "blur(24px)",
        borderLeft: "1px solid hsl(var(--border))",
        boxShadow: "var(--shadow-md)",
        display: "flex", flexDirection: "column", zIndex: 10, position: "relative",
      }}
    >
      <div style={{ padding: 20, display: "flex", flexDirection: "column", gap: 24, flex: 1 }}>
        {/* Prompt */}
        <div>
          <div className="section-label" style={{ marginBottom: 10 }}>Story Prompt</div>
          <div className="glow-focus panel-card-subtle" style={{
            borderRadius: 12, padding: 2,
            boxShadow: "var(--shadow-sm)",
            backdropFilter: "blur(16px)", WebkitBackdropFilter: "blur(16px)",
          }}>
            <textarea
              ref={storyInputRef}
              value={storyInput}
              onChange={(e) => setStoryInput(e.target.value)}
              placeholder="Write your story... e.g. A lone samurai walks through a cherry blossom forest at dusk, reflecting on past battles."
              aria-label="Story prompt"
              style={{
                width: "100%", height: 120, padding: 14, fontSize: 13, lineHeight: 1.6,
                background: "transparent", border: "none", color: "hsl(var(--text-primary))",
                resize: "none", outline: "none",
              }}
            />
          </div>
        </div>

        {/* Style Presets */}
        <div>
          <div className="section-label" style={{ marginBottom: 10 }}>Style Preset</div>
          <div style={{ display: "flex", flexWrap: "wrap", gap: 8 }}>
            {PRESETS.map((p) => (
              <button
                key={p.id}
                onClick={() => setActivePreset(p.id)}
                style={{
                  padding: "8px 14px", borderRadius: 10, fontSize: 12, fontWeight: 500, cursor: "pointer",
                  background: activePreset === p.id
                    ? "hsl(var(--primary) / 0.2)"
                    : "hsl(var(--bg-tertiary) / 0.8)",
                  color: activePreset === p.id ? "hsl(var(--primary))" : "hsl(var(--text-secondary))",
                  border: activePreset === p.id
                    ? "1px solid hsl(var(--primary) / 0.5)"
                    : "1px solid hsl(var(--border))",
                  backdropFilter: "blur(12px)", WebkitBackdropFilter: "blur(12px)",
                  boxShadow: activePreset === p.id ? "0 0 20px hsl(var(--primary) / 0.15)" : "none",
                  transition: "all 0.2s",
                }}
              >
                {p.label}
              </button>
            ))}
          </div>
        </div>

        {/* Sliders */}
        <div className="panel-card-subtle" style={{
          padding: 16, borderRadius: 12,
          backdropFilter: "blur(16px)", WebkitBackdropFilter: "blur(16px)",
          boxShadow: "var(--shadow-sm)",
        }}>
          <div className="section-label" style={{ marginBottom: 14 }}>Generation Controls</div>
          <SliderControl label="Duration" value={sliders.duration} onChange={(v) => updateSlider("duration", v)} />
          <SliderControl label="Intensity" value={sliders.intensity} onChange={(v) => updateSlider("intensity", v)} />
          <SliderControl label="Particle Density" value={sliders.particleDensity} onChange={(v) => updateSlider("particleDensity", v)} />
          <SliderControl label="Camera Speed" value={sliders.cameraSpeed} onChange={(v) => updateSlider("cameraSpeed", v)} />
        </div>

        {/* RL Feedback */}
        {rlData && rlData.episode > 0 && (
          <div>
            <div className="section-label" style={{ marginBottom: 10 }}>Rate Output (RLHF)</div>
            <div style={{ display: "flex", gap: 8 }}>
              <button
                className="btn-ghost"
                style={{
                  flex: 1, justifyContent: "center", padding: 12,
                  background: feedbackSent === "up" ? "hsla(160, 84%, 39%, 0.2)" : "hsl(var(--bg-tertiary) / 0.7)",
                  borderColor: feedbackSent === "up" ? "hsl(160, 84%, 45%)" : undefined,
                }}
                onClick={() => handleFeedback(true)}
              >
                <ThumbsUp size={16} /> Like
              </button>
              <button
                className="btn-ghost"
                style={{
                  flex: 1, justifyContent: "center", padding: 12,
                  background: feedbackSent === "down" ? "hsla(0, 70%, 50%, 0.2)" : "hsl(var(--bg-tertiary) / 0.7)",
                  borderColor: feedbackSent === "down" ? "hsl(0, 70%, 55%)" : undefined,
                }}
                onClick={() => handleFeedback(false)}
              >
                <ThumbsDown size={16} /> Dislike
              </button>
            </div>
          </div>
        )}

        <div style={{ flex: 1 }} />

        {/* Generate Button */}
        <button
          onClick={() => storyInput.trim() && onGenerate?.(storyInput)}
          disabled={isGenerating || !storyInput.trim()}
          style={{
            width: "100%", padding: 18, borderRadius: 12, fontSize: 15, fontWeight: 600,
            letterSpacing: "0.05em",
            display: "flex", alignItems: "center", justifyContent: "center", gap: 10,
            opacity: isGenerating || !storyInput.trim() ? 0.6 : 1,
            cursor: isGenerating || !storyInput.trim() ? "not-allowed" : "pointer",
            background: "linear-gradient(135deg, hsl(355, 80%, 55%), hsl(260, 80%, 60%))",
            color: "white",
            border: "1px solid hsla(355, 80%, 65%, 0.5)",
            boxShadow: "0 0 20px hsla(355, 80%, 55%, 0.4), inset 0 1px 0 hsla(0,0%,100%,0.2)",
            backdropFilter: "blur(20px)", WebkitBackdropFilter: "blur(20px)",
            transition: "all 0.2s",
          }}
        >
          {isGenerating ? (
            <>
              <div style={{ width: 18, height: 18, borderRadius: "50%", border: "2px solid white", borderTopColor: "transparent", animation: "spin 0.6s linear infinite" }} />
              Generating...
            </>
          ) : (
            <>
              <Sparkles size={18} /> Generate
            </>
          )}
        </button>
      </div>
    </motion.aside>
  );
}
