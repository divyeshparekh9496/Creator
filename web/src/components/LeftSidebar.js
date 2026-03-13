"use client";
import { motion } from "framer-motion";
import { FolderKanban, Bot, GitBranch, Check, Loader2, Clock, User, ChevronDown, ChevronRight } from "lucide-react";
import { useState } from "react";

function PipelineStage({ stage, index }) {
  const icons = { done: <Check size={12} />, processing: <Loader2 size={12} className="animate-spin" />, queued: <Clock size={12} /> };
  const colors = {
    done: "hsl(var(--accent))",
    processing: "hsl(var(--primary))",
    queued: "hsl(var(--text-muted))"
  };
  return (
    <motion.div
      initial={{ opacity: 0, x: -10 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ delay: index * 0.05 }}
      style={{
        display: "flex", alignItems: "center", gap: 8, padding: "4px 0",
        fontSize: 12, color: colors[stage.status],
      }}
    >
      <div style={{ width: 18, display: "flex", justifyContent: "center" }}>{icons[stage.status]}</div>
      <span style={{ flex: 1 }}>{stage.name}</span>
      {stage.time && <span style={{ fontSize: 10, opacity: 0.7 }}>{stage.time}</span>}
      {stage.progress != null && (
        <div style={{ width: 40, height: 3, borderRadius: 2, background: "hsl(var(--bg-hover))" }}>
          <motion.div
            initial={{ width: 0 }}
            animate={{ width: `${stage.progress}%` }}
            style={{ height: "100%", borderRadius: 2, background: "hsl(var(--primary))" }}
          />
        </div>
      )}
    </motion.div>
  );
}

function SidebarSection({ title, icon, children, defaultOpen = true }) {
  const [open, setOpen] = useState(defaultOpen);
  return (
    <div style={{ marginBottom: 4 }}>
      <button
        onClick={() => setOpen(!open)}
        style={{
          width: "100%", display: "flex", alignItems: "center", gap: 8,
          padding: "8px 16px", fontSize: 11, fontWeight: 600,
          textTransform: "uppercase", letterSpacing: "0.05em",
          color: "hsl(var(--text-muted))", background: "none", border: "none",
          cursor: "pointer",
        }}
      >
        {icon}
        <span style={{ flex: 1, textAlign: "left" }}>{title}</span>
        {open ? <ChevronDown size={12} /> : <ChevronRight size={12} />}
      </button>
      {open && <div style={{ padding: "0 16px 8px" }}>{children}</div>}
    </div>
  );
}

export default function LeftSidebar({ pipeline, rlData, characters }) {
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
      {/* Projects */}
      <SidebarSection title="Projects" icon={<FolderKanban size={12} />}>
        {["Samurai Dawn", "Elf Chronicles", "Mecha Uprising"].map((name, i) => (
          <motion.button
            key={name}
            whileHover={{ x: 4, backgroundColor: "hsl(var(--bg-hover))" }}
            style={{
              width: "100%", display: "flex", alignItems: "center", gap: 8,
              padding: "8px 10px", borderRadius: 8, fontSize: 13,
              color: i === 0 ? "hsl(var(--text-primary))" : "hsl(var(--text-secondary))",
              background: i === 0 ? "hsl(var(--bg-tertiary))" : "transparent",
              border: i === 0 ? "1px solid hsl(var(--border-glow))" : "1px solid transparent",
              cursor: "pointer", textAlign: "left",
            }}
          >
            <div style={{
              width: 28, height: 28, borderRadius: 6, flexShrink: 0,
              background: `linear-gradient(135deg, hsl(${200 + i * 30},60%,40%), hsl(${220 + i * 30},60%,30%))`,
            }} />
            <div>
              <div style={{ fontWeight: 500 }}>{name}</div>
              <div style={{ fontSize: 10, color: "hsl(var(--text-muted))" }}>
                {i === 0 ? "Active" : `${3 - i} scenes`}
              </div>
            </div>
          </motion.button>
        ))}
      </SidebarSection>

      {/* Characters */}
      <SidebarSection title="Characters" icon={<User size={12} />}>
        {characters.map((char) => (
          <div key={char.id} style={{
            display: "flex", alignItems: "center", gap: 8,
            padding: "6px 10px", borderRadius: 8, fontSize: 12,
            marginBottom: 4,
          }}>
            <div style={{
              width: 24, height: 24, borderRadius: "50%", flexShrink: 0,
              background: char.role === "protagonist"
                ? "linear-gradient(135deg, hsl(263,70%,50%), hsl(200,70%,50%))"
                : "linear-gradient(135deg, hsl(0,60%,45%), hsl(35,80%,50%))",
              border: "2px solid hsl(var(--border))",
            }} />
            <div style={{ flex: 1 }}>
              <div style={{ fontWeight: 500, color: "hsl(var(--text-primary))" }}>{char.name}</div>
              <div style={{ fontSize: 10, color: "hsl(var(--text-muted))" }}>{char.trait} • Stage {char.arcStage}</div>
            </div>
            <span className="badge badge-primary">Arc {char.arcStage}</span>
          </div>
        ))}
      </SidebarSection>

      {/* RL Policy */}
      <SidebarSection title="RL Policy" icon={<Bot size={12} />}>
        <div className="glass-card" style={{ padding: 10, marginBottom: 8 }}>
          <div style={{ display: "flex", justifyContent: "space-between", fontSize: 12, marginBottom: 6 }}>
            <span>Policy {rlData.policyVersion}</span>
            <span className="badge badge-success">Ep. {rlData.episode}</span>
          </div>
          {rlData.actions.map((a, i) => (
            <div key={i} style={{
              fontSize: 11, color: "hsl(var(--text-secondary))", padding: "3px 0",
              display: "flex", alignItems: "center", gap: 4,
            }}>
              <span style={{ color: "hsl(var(--accent))" }}>→</span>
              {a.type}: {a.param}
            </div>
          ))}
        </div>
        <div style={{ fontSize: 10, color: "hsl(var(--text-muted))", lineHeight: 1.5 }}>
          {rlData.patterns.map((p, i) => <div key={i} style={{ marginBottom: 2 }}>💡 {p}</div>)}
        </div>
      </SidebarSection>

      {/* Pipeline */}
      <SidebarSection title="Pipeline" icon={<GitBranch size={12} />}>
        {pipeline.stages.map((stage, i) => <PipelineStage key={i} stage={stage} index={i} />)}
      </SidebarSection>
    </motion.aside>
  );
}
