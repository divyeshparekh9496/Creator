"use client";
import { motion } from "framer-motion";
import { X, Download, FileJson, Film, Box, Copy, ExternalLink, Check } from "lucide-react";
import { useState } from "react";

const EXPORT_FORMATS = [
  { id: "mp4", label: "MP4 Sequences", icon: <Film size={16} />, desc: "Rendered video parts + merged episode", ext: ".mp4" },
  { id: "json", label: "Lottie JSON", icon: <FileJson size={16} />, desc: "Animation data for web players", ext: ".json" },
  { id: "glb", label: "GLB Characters", icon: <Box size={16} />, desc: "3D character models from sheets", ext: ".glb" },
  { id: "manifest", label: "Pipeline Manifest", icon: <FileJson size={16} />, desc: "GCS paths, FFmpeg script, metadata", ext: ".json" },
];

export default function ExportPanel({ onClose, pipeline }) {
  const [selected, setSelected] = useState(["mp4", "manifest"]);
  const [copied, setCopied] = useState(false);

  const toggle = (id) => {
    setSelected(prev => prev.includes(id) ? prev.filter(x => x !== id) : [...prev, id]);
  };

  const copyManifest = () => {
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      style={{
        position: "fixed", inset: 0, background: "hsla(0,0%,0%,0.5)",
        backdropFilter: "blur(6px)", zIndex: 100,
        display: "flex", justifyContent: "flex-end",
      }}
      onClick={onClose}
    >
      <motion.div
        initial={{ x: 400 }}
        animate={{ x: 0 }}
        exit={{ x: 400 }}
        transition={{ type: "spring", damping: 30, stiffness: 300 }}
        onClick={(e) => e.stopPropagation()}
        style={{
          width: "min(400px, 90vw)", height: "100%",
          background: "var(--glass-bg)", backdropFilter: "blur(20px)",
          borderLeft: "1px solid var(--glass-border)",
          display: "flex", flexDirection: "column",
        }}
      >
        {/* Header */}
        <div style={{
          display: "flex", alignItems: "center", justifyContent: "space-between",
          padding: "16px 20px", borderBottom: "1px solid var(--glass-border)",
        }}>
          <h2 style={{ fontSize: 16, fontWeight: 700 }}>Export</h2>
          <button className="btn-icon" onClick={onClose}><X size={18} /></button>
        </div>

        {/* Content */}
        <div style={{ flex: 1, overflow: "auto", padding: 20 }}>
          {/* Format selection */}
          <div style={{ fontSize: 12, fontWeight: 600, marginBottom: 12, color: "hsl(var(--text-primary))" }}>
            Export Formats
          </div>

          {EXPORT_FORMATS.map((fmt) => {
            const isSelected = selected.includes(fmt.id);
            return (
              <motion.button
                key={fmt.id}
                whileHover={{ scale: 1.01 }}
                onClick={() => toggle(fmt.id)}
                style={{
                  width: "100%", display: "flex", alignItems: "center", gap: 12,
                  padding: 14, borderRadius: 10, marginBottom: 8,
                  background: isSelected ? "hsla(263,70%,50%,0.1)" : "hsl(var(--bg-secondary))",
                  border: isSelected ? "1px solid hsla(263,70%,50%,0.3)" : "1px solid hsl(var(--border))",
                  cursor: "pointer", textAlign: "left",
                }}
              >
                <div style={{
                  width: 36, height: 36, borderRadius: 8, flexShrink: 0,
                  background: isSelected ? "hsl(var(--primary))" : "hsl(var(--bg-tertiary))",
                  display: "flex", alignItems: "center", justifyContent: "center",
                  color: isSelected ? "white" : "hsl(var(--text-muted))",
                }}>
                  {fmt.icon}
                </div>
                <div style={{ flex: 1 }}>
                  <div style={{ fontSize: 13, fontWeight: 500, color: "hsl(var(--text-primary))" }}>
                    {fmt.label}
                  </div>
                  <div style={{ fontSize: 11, color: "hsl(var(--text-muted))" }}>{fmt.desc}</div>
                </div>
                <div style={{
                  width: 20, height: 20, borderRadius: 6,
                  border: isSelected ? "none" : "2px solid hsl(var(--border))",
                  background: isSelected ? "hsl(var(--primary))" : "transparent",
                  display: "flex", alignItems: "center", justifyContent: "center",
                }}>
                  {isSelected && <Check size={12} color="white" />}
                </div>
              </motion.button>
            );
          })}

          {/* GCS Preview */}
          <div style={{ fontSize: 12, fontWeight: 600, marginTop: 20, marginBottom: 12, color: "hsl(var(--text-primary))" }}>
            Cloud Storage Paths
          </div>

          <div className="glass-card" style={{ padding: 12, fontFamily: "monospace", fontSize: 11, lineHeight: 1.8 }}>
            <div style={{ color: "hsl(var(--text-muted))" }}>gs://creator-anime-assets/</div>
            <div style={{ paddingLeft: 12 }}>
              <div><span style={{ color: "hsl(var(--primary))" }}>├─</span> characters/profiles.json</div>
              <div><span style={{ color: "hsl(var(--primary))" }}>├─</span> keyframes/*.png</div>
              <div><span style={{ color: "hsl(var(--primary))" }}>├─</span> animation/plan.json</div>
              <div><span style={{ color: "hsl(var(--primary))" }}>├─</span> audio/plan.json</div>
              <div><span style={{ color: "hsl(var(--primary))" }}>├─</span> scenes/interleaved_output.txt</div>
              <div><span style={{ color: "hsl(var(--accent))" }}>├─</span> rl/policy_v2.json</div>
              <div><span style={{ color: "hsl(var(--accent))" }}>└─</span> rl/episodes/*.json</div>
            </div>
          </div>

          {/* Pipeline status */}
          <div style={{ fontSize: 12, fontWeight: 600, marginTop: 20, marginBottom: 12, color: "hsl(var(--text-primary))" }}>
            Pipeline Status
          </div>

          <div className="glass-card" style={{ padding: 12 }}>
            {pipeline.stages.map((stage, i) => (
              <div key={i} style={{
                display: "flex", alignItems: "center", justifyContent: "space-between",
                padding: "4px 0", fontSize: 12,
                color: stage.status === "done" ? "hsl(var(--accent))"
                     : stage.status === "processing" ? "hsl(var(--primary))"
                     : "hsl(var(--text-muted))",
              }}>
                <span>{stage.name}</span>
                <span style={{ fontSize: 10, textTransform: "uppercase", fontWeight: 600 }}>{stage.status}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Footer */}
        <div style={{
          padding: "16px 20px", borderTop: "1px solid var(--glass-border)",
          display: "flex", gap: 8,
        }}>
          <button className="btn-ghost" onClick={copyManifest} style={{ flex: 1, justifyContent: "center" }}>
            {copied ? <Check size={14} /> : <Copy size={14} />}
            {copied ? "Copied!" : "Copy Manifest"}
          </button>
          <button className="btn-primary" style={{ flex: 1, justifyContent: "center" }}>
            <Download size={14} /> Export
          </button>
        </div>
      </motion.div>
    </motion.div>
  );
}
