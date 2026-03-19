"use client";
import { motion } from "framer-motion";
import { User, Bot, Check, Loader2, ChevronDown, ChevronRight, BookOpen, Sparkles } from "lucide-react";
import { useState } from "react";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

const PIPELINE_HINTS = {
  "Story Analysis": "Parse narrative, extract beats & cast",
  "Character Dev": "Sheets, arcs, style locks",
  "RL Start": "Episode init, policy selection",
  "Storyboard": "Shots, effects, motion hints",
  "Keyframes": "AnimeGANv2-styled frames",
  "Animation": "Motion & transition plans",
  "Audio": "SFX, BGM, emotion sync",
  "RL Rewards": "Composite scoring, action selection",
  "Scene Render": "RL-augmented interleaved output",
  "Assembly": "Video merge & upload",
};

function SidebarSection({ title, icon, children, defaultOpen = true }) {
  const [open, setOpen] = useState(defaultOpen);
  return (
    <div style={{ marginBottom: 8 }}>
      <button
        onClick={() => setOpen(!open)}
        style={{
          width: "100%", display: "flex", alignItems: "center", gap: 10,
          padding: "12px 16px", fontSize: 11, fontWeight: 600,
          textTransform: "uppercase", letterSpacing: "0.08em",
          color: open ? "hsl(var(--text-primary))" : "hsl(var(--text-muted))",
          background: open ? "hsl(var(--bg-hover) / 0.8)" : "transparent",
          border: "none", borderBottom: open ? "1px solid hsl(var(--border))" : "none",
          cursor: "pointer", transition: "all 0.2s", borderRadius: 8, marginBottom: 4,
        }}
      >
        <span style={{ color: open ? "hsl(var(--primary))" : "hsl(var(--text-muted))" }}>{icon}</span>
        <span style={{ flex: 1, textAlign: "left" }}>{title}</span>
        {open ? <ChevronDown size={12} /> : <ChevronRight size={12} />}
      </button>
      {open && <div style={{ padding: "0 16px 12px" }}>{children}</div>}
    </div>
  );
}

function CharacterCard({ char, isExpanded, onToggle }) {
  const color = char.role === "protagonist" ? "hsl(355, 60%, 50%)" : `hsl(${200 + (char.id?.length || 0) * 20}, 50%, 45%)`;
  return (
    <motion.div
      layout
      whileHover={{ scale: 1.02 }}
      onClick={onToggle}
      style={{
        padding: 10, borderRadius: 10, marginBottom: 8, cursor: "pointer",
        background: isExpanded ? "hsl(var(--bg-hover) / 0.9)" : "hsl(var(--bg-tertiary) / 0.7)",
        border: isExpanded ? "1px solid hsl(var(--primary) / 0.5)" : "1px solid hsl(var(--border))",
        borderLeft: `3px solid ${color}`,
        boxShadow: isExpanded ? "0 4px 12px hsla(260, 60%, 50%, 0.15)" : "none",
      }}
    >
      <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
        <div style={{
          width: 40, height: 40, borderRadius: 10, flexShrink: 0,
          background: `linear-gradient(135deg, ${color}, hsla(260, 60%, 35%, 0.8))`,
          display: "flex", alignItems: "center", justifyContent: "center",
          boxShadow: "inset 0 0 10px hsla(0,0%,0%,0.3)",
        }}>
          <User size={18} color="white" />
        </div>
        <div style={{ flex: 1, minWidth: 0 }}>
          <div style={{ fontSize: 13, fontWeight: 600, color: "hsl(var(--text-primary))", marginBottom: 2 }}>{char.name}</div>
          <div style={{ fontSize: 10, color: "hsl(var(--text-muted))", textTransform: "capitalize" }}>{char.role || "Character"}</div>
        </div>
        {isExpanded ? <ChevronDown size={12} /> : <ChevronRight size={12} />}
      </div>
      {isExpanded && (
        <motion.div
          initial={{ opacity: 0, height: 0 }}
          animate={{ opacity: 1, height: "auto" }}
          exit={{ opacity: 0, height: 0 }}
          style={{ marginTop: 10, paddingTop: 10, borderTop: "1px solid hsl(var(--border))" }}
        >
          <div style={{ fontSize: 11, color: "hsl(var(--text-secondary))", lineHeight: 1.5 }}>
            {char.trait && <div style={{ marginBottom: 4 }}><strong>Trait:</strong> {char.trait}</div>}
            {char.styleLock && <div><strong>Style:</strong> {char.styleLock}</div>}
          </div>
        </motion.div>
      )}
    </motion.div>
  );
}

export default function LeftSidebar({ pipeline, rlData, characters, storyBeats, onFocusStory }) {
  const [expandedChar, setExpandedChar] = useState(null);

  return (
    <motion.aside
      initial={{ x: -280, opacity: 0 }}
      animate={{ x: 0, opacity: 1 }}
      transition={{ duration: 0.5, ease: [0.16, 1, 0.3, 1] }}
      style={{
        width: "var(--sidebar-width)", minWidth: "var(--sidebar-width)",
        height: "100%", overflow: "auto",
        background: "var(--glass-bg)", backdropFilter: "blur(16px)",
        borderRight: "1px solid var(--glass-border)", zIndex: 10,
        position: "relative",
      }}
    >
      {/* Story Beats */}
      {storyBeats && storyBeats.length > 0 && (
        <SidebarSection title="Story Beats" icon={<BookOpen size={14} />}>
          <div style={{ display: "flex", flexDirection: "column", gap: 6 }}>
            {storyBeats.map((beat, i) => (
              <motion.div
                key={i}
                whileHover={{ x: 4 }}
                style={{
                  padding: "8px 12px", borderRadius: 8,
                  background: "hsl(var(--bg-tertiary) / 0.8)",
                  border: "1px solid hsl(var(--border))",
                  borderLeft: "3px solid hsl(var(--primary))",
                }}
              >
                <div style={{ fontSize: 12, fontWeight: 600, color: "hsl(var(--text-primary))", marginBottom: 4 }}>
                  Beat {i + 1}
                </div>
                <div style={{ fontSize: 11, color: "hsl(var(--text-muted))", lineHeight: 1.4 }}>
                  {typeof beat === "string" ? beat : beat?.description ?? beat?.summary ?? beat?.title ?? (beat && JSON.stringify(beat).slice(0, 100))}
                </div>
              </motion.div>
            ))}
          </div>
        </SidebarSection>
      )}

      {/* Characters */}
      <SidebarSection title="Characters" icon={<User size={14} />}>
        {characters.length > 0 ? (
          characters.map((char) => (
            <CharacterCard
              key={char.id || char.name}
              char={char}
              isExpanded={expandedChar === (char.id || char.name)}
              onToggle={() => setExpandedChar(expandedChar === (char.id || char.name) ? null : (char.id || char.name))}
            />
          ))
        ) : (
          <motion.div
            initial={{ opacity: 0.8 }}
            animate={{ opacity: 1 }}
            style={{
              padding: 24, textAlign: "center",
              background: "hsl(var(--bg-tertiary) / 0.9)",
              borderRadius: 12, border: "1px dashed hsl(var(--border))",
              position: "relative", overflow: "hidden",
            }}
          >
            <div style={{
              width: 48, height: 48, margin: "0 auto 12px",
              borderRadius: 12, background: "hsl(var(--bg-hover) / 0.8)",
              border: "1px solid hsl(var(--border))",
              display: "flex", alignItems: "center", justifyContent: "center",
            }}>
              <User size={22} style={{ color: "hsl(var(--text-muted))" }} />
            </div>
            <div style={{ fontSize: 12, fontWeight: 500, color: "hsl(var(--text-secondary))", marginBottom: 4 }}>
              No characters yet
            </div>
            <div style={{ fontSize: 11, color: "hsl(var(--text-muted))", lineHeight: 1.4 }}>
              Enter a story in the right panel and click <strong style={{ color: "hsl(var(--primary))" }}>Generate</strong> to create character sheets with arcs
            </div>
            {onFocusStory && (
              <button
                type="button"
                onClick={onFocusStory}
                className="btn-ghost"
                style={{
                  marginTop: 12, padding: "8px 14px", borderRadius: 8, fontSize: 11, fontWeight: 500,
                }}
              >
                Focus story input →
              </button>
            )}
          </motion.div>
        )}
      </SidebarSection>

      {/* Pipeline Stages */}
      <SidebarSection title="Pipeline" icon={<Bot size={14} />}>
        <div style={{ display: "flex", flexDirection: "column", gap: 0 }}>
          {pipeline.stages.map((stage, i) => {
            const isDone = stage.status === "done" || stage.status === "cached";
            const isActive = stage.status === "processing";
            const isQueued = stage.status === "queued" || stage.status === "idle";

            const hint = PIPELINE_HINTS[stage.name];
            return (
              <motion.div
                key={i}
                initial={false}
                animate={{ opacity: isQueued ? 0.75 : 1 }}
                whileHover={isQueued ? { x: 4 } : {}}
                title={isQueued && hint ? hint : undefined}
                style={{
                  display: "flex", gap: 12, marginBottom: 2,
                  padding: "6px 8px", borderRadius: 8,
                  background: isActive ? "hsl(var(--bg-hover) / 0.6)" : "transparent",
                  borderLeft: isActive ? "2px solid hsl(var(--primary))" : "2px solid transparent",
                }}
              >
                <div style={{ display: "flex", flexDirection: "column", alignItems: "center", width: 20 }}>
                  <div style={{
                    width: 18, height: 18, borderRadius: "50%",
                    background: isDone ? "hsl(160, 80%, 40%, 0.3)" : isActive ? "hsl(var(--primary) / 0.25)" : "hsl(var(--bg-tertiary) / 0.8)",
                    border: "2px solid",
                    borderColor: isDone ? "hsl(160, 80%, 50%)" : isActive ? "hsl(var(--primary))" : "hsl(var(--border))",
                    display: "flex", alignItems: "center", justifyContent: "center",
                    flexShrink: 0,
                  }}>
                    {isDone && <Check size={10} color="hsl(160, 80%, 60%)" strokeWidth={3} />}
                    {isActive && <Loader2 size={11} color="hsl(260, 80%, 70%)" style={{ animation: "spin 1s linear infinite" }} />}
                    {isQueued && <span style={{ fontSize: 9, fontWeight: 700, color: "hsl(var(--text-secondary))" }}>{i + 1}</span>}
                  </div>
                  {i < pipeline.stages.length - 1 && (
                    <div style={{ width: 2, flex: 1, minHeight: 10, background: isDone ? "hsl(160, 60%, 45%, 0.3)" : "hsl(var(--border))", marginTop: 4, borderRadius: 1 }} />
                  )}
                </div>
                <div style={{ flex: 1, paddingBottom: 12, paddingTop: 1 }}>
                  <div style={{
                    fontSize: 12, fontWeight: isDone || isActive ? 600 : 500,
                    color: isDone ? "hsl(160, 75%, 55%)" : isActive ? "hsl(var(--text-primary))" : "hsl(var(--text-secondary))",
                  }}>
                    {stage.name}
                  </div>
                  {isQueued && hint && (
                    <div style={{ fontSize: 10, color: "hsl(var(--text-muted))", marginTop: 2, lineHeight: 1.3 }}>{hint}</div>
                  )}
                  {isActive && (
                    <div style={{ fontSize: 10, color: "hsl(260, 80%, 70%)", marginTop: 2, display: "flex", alignItems: "center", gap: 4 }}>
                      <Sparkles size={10} /> Processing...
                    </div>
                  )}
                  {isDone && stage.time != null && (
                    <div style={{ fontSize: 10, color: "hsl(160, 60%, 55%)", marginTop: 2 }}>✓ {stage.time}s</div>
                  )}
                </div>
              </motion.div>
            );
          })}
        </div>
      </SidebarSection>
    </motion.aside>
  );
}
