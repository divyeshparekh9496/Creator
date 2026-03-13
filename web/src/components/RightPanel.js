"use client";
import { motion } from "framer-motion";
import { Upload, FileText, ImageIcon, Mic, ThumbsUp, ThumbsDown, Sliders, Send, Sparkles } from "lucide-react";
import { useState } from "react";

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

export default function RightPanel({ rlData, characters, selectedScene, onGenerate, onFeedback, isGenerating }) {
  const [storyInput, setStoryInput] = useState("");
  const [showFeedback, setShowFeedback] = useState(false);

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
      {/* Multimodal Input */}
      <div style={{ padding: 16, borderBottom: "1px solid var(--glass-border)" }}>
        <div style={{ fontSize: 12, fontWeight: 600, marginBottom: 10, color: "hsl(var(--text-primary))" }}>
          Story Input
        </div>

        {/* Upload buttons */}
        <div style={{ display: "flex", gap: 6, marginBottom: 10 }}>
          {[
            { icon: <FileText size={13} />, label: "Text" },
            { icon: <ImageIcon size={13} />, label: "Image" },
            { icon: <Mic size={13} />, label: "Voice" },
            { icon: <Upload size={13} />, label: "File" },
          ].map((btn) => (
            <motion.button
              key={btn.label}
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              className="btn-ghost"
              style={{ flex: 1, justifyContent: "center", padding: "6px 4px", fontSize: 11 }}
            >
              {btn.icon}
              <span style={{ display: "none" }}>{btn.label}</span>
            </motion.button>
          ))}
        </div>

        {/* Text input */}
        <div className="glow-focus" style={{
          borderRadius: 10, border: "1px solid hsl(var(--border))",
          background: "hsl(var(--bg-secondary))",
          overflow: "hidden",
        }}>
          <textarea
            value={storyInput}
            onChange={(e) => setStoryInput(e.target.value)}
            placeholder="Paste your story, describe a scene, or upload media..."
            style={{
              width: "100%", height: 100, padding: 10, fontSize: 12, lineHeight: 1.6,
              background: "transparent", border: "none", color: "hsl(var(--text-primary))",
              resize: "none", outline: "none",
            }}
          />
          <div style={{ display: "flex", justifyContent: "flex-end", padding: "6px 8px" }}>
            <motion.button
              className="btn-primary"
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              style={{ fontSize: 12, padding: "5px 12px", opacity: isGenerating ? 0.6 : 1 }}
              onClick={() => storyInput.trim() && onGenerate && onGenerate(storyInput)}
              disabled={isGenerating || !storyInput.trim()}
            >
              {isGenerating ? (
                <><div style={{ width: 12, height: 12, borderRadius: "50%", border: "2px solid white", borderTopColor: "transparent", animation: "spin 0.6s linear infinite" }} /> Generating...</>
              ) : (
                <><Send size={12} /> Generate</>
              )}
            </motion.button>
          </div>
        </div>
      </div>

      {/* RL Feedback */}
      <div style={{ padding: 16, borderBottom: "1px solid var(--glass-border)" }}>
        <div style={{
          display: "flex", justifyContent: "space-between", alignItems: "center",
          marginBottom: 12,
        }}>
          <div style={{ fontSize: 12, fontWeight: 600, display: "flex", alignItems: "center", gap: 6 }}>
            <Sparkles size={14} style={{ color: "hsl(var(--accent))" }} />
            RL Feedback
          </div>
          <button
            className="btn-ghost"
            onClick={() => setShowFeedback(!showFeedback)}
            style={{ fontSize: 10, padding: "3px 8px" }}
          >
            <Sliders size={10} /> {showFeedback ? "Hide" : "Show"} Sliders
          </button>
        </div>

        {/* Quick thumbs */}
        <div style={{ display: "flex", gap: 8, marginBottom: 12 }}>
          <motion.button
            whileHover={{ scale: 1.1 }}
            whileTap={{ scale: 0.9, rotate: 10 }}
            onClick={() => onFeedback && onFeedback(true)}
            style={{
              flex: 1, display: "flex", alignItems: "center", justifyContent: "center", gap: 6,
              padding: "10px 0", borderRadius: 10, fontSize: 13, fontWeight: 500,
              background: "hsla(160,84%,39%,0.1)", color: "hsl(var(--accent))",
              border: "1px solid hsla(160,84%,39%,0.2)", cursor: "pointer",
            }}
          >
            <ThumbsUp size={16} /> Great
          </motion.button>
          <motion.button
            whileHover={{ scale: 1.1 }}
            whileTap={{ scale: 0.9, rotate: -10 }}
            onClick={() => onFeedback && onFeedback(false)}
            style={{
              flex: 1, display: "flex", alignItems: "center", justifyContent: "center", gap: 6,
              padding: "10px 0", borderRadius: 10, fontSize: 13, fontWeight: 500,
              background: "hsla(0,70%,50%,0.1)", color: "hsl(0,70%,65%)",
              border: "1px solid hsla(0,70%,50%,0.2)", cursor: "pointer",
            }}
          >
            <ThumbsDown size={16} /> Improve
          </motion.button>
        </div>

        {/* Dimension sliders */}
        {showFeedback && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: "auto", opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
          >
            <FeedbackSlider label="Coherence" value={rlData.coherence} color="#8B5CF6" />
            <FeedbackSlider label="Creativity" value={rlData.creativity} color="#3B82F6" />
            <FeedbackSlider label="Consistency" value={rlData.consistency} color="#10B981" />
            <FeedbackSlider label="Emotional Impact" value={rlData.emotional} color="#F59E0B" />
            <FeedbackSlider label="Technical Quality" value={rlData.technical} color="#EF4444" />
          </motion.div>
        )}
      </div>

      {/* Selected Scene Detail */}
      <div style={{ padding: 16, flex: 1, overflow: "auto" }}>
        <div style={{ fontSize: 12, fontWeight: 600, marginBottom: 10, color: "hsl(var(--text-primary))" }}>
          Scene Detail
        </div>

        {selectedScene && (
          <div className="glass-card" style={{ padding: 12 }}>
            <div style={{ fontSize: 14, fontWeight: 600, marginBottom: 4 }}>
              Scene {selectedScene.id}: {selectedScene.title}
            </div>
            <div style={{ fontSize: 11, color: "hsl(var(--text-secondary))", marginBottom: 8 }}>
              Arc: {selectedScene.trait} (Stage {selectedScene.arcStage})
            </div>

            <div style={{ fontSize: 11, color: "hsl(var(--text-muted))", lineHeight: 1.6 }}>
              <div>📖 <strong>Narration:</strong> "The weight of destiny settled on her shoulders..."</div>
              <div style={{ marginTop: 4 }}>🎬 <strong>Action:</strong> Character faces the storm</div>
              <div style={{ marginTop: 4 }}>🖼️ <strong>Image:</strong> AnimeGANv2 style, Animate Anyone smooth turn</div>
              <div style={{ marginTop: 4 }}>🔊 <strong>Audio:</strong> {selectedScene.trait === "heroic" ? "Epic horns, full orchestra" : "Tense strings, heartbeat SFX"}</div>
              <div style={{ marginTop: 4 }}>✨ <strong>Effects:</strong> particle_rain + inner_glow</div>
              <div style={{ marginTop: 6, fontSize: 10, color: "hsl(var(--accent))" }}>
                📊 RL: {selectedScene.rlScore.toFixed(2)} | Policy: {rlData.policyVersion}
              </div>
            </div>

            <div style={{ display: "flex", gap: 6, marginTop: 10 }}>
              <button className="btn-primary" style={{ flex: 1, justifyContent: "center", fontSize: 11 }}>
                <Sparkles size={12} /> RL Enhance
              </button>
              <button className="btn-ghost" style={{ flex: 1, justifyContent: "center", fontSize: 11 }}>
                Regen Prompt
              </button>
            </div>
          </div>
        )}
      </div>
    </motion.aside>
  );
}
