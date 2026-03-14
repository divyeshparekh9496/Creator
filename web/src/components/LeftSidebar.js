"use client";
import { motion } from "framer-motion";
import { FolderKanban, Bot, GitBranch, Check, Loader2, Clock, User, ChevronDown, ChevronRight } from "lucide-react";
import { useState } from "react";

function StoryBeatCard({ index, title, description, isActive }) {
  return (
    <motion.div
      whileHover={{ scale: 1.02 }}
      style={{
        padding: "10px 12px", borderRadius: 8, marginBottom: 8, cursor: "pointer",
        background: isActive ? "hsla(260, 40%, 30%, 0.3)" : "hsla(240, 15%, 16%, 0.5)",
        border: isActive ? "1px solid hsla(260, 60%, 50%, 0.5)" : "1px solid hsla(240, 20%, 30%, 0.3)",
        borderLeft: isActive ? "3px solid hsl(260, 80%, 60%)" : "3px solid transparent",
        display: "flex", gap: 10,
        boxShadow: isActive ? "0 4px 12px hsla(260, 60%, 50%, 0.15)" : "none"
      }}
    >
      <div style={{
        width: 24, height: 24, borderRadius: 6, display: "flex", alignItems: "center", justifyContent: "center",
        background: "hsla(240, 20%, 25%, 0.6)", fontSize: 11, fontWeight: 700, color: "hsl(var(--text-secondary))"
      }}>
        {index}
      </div>
      <div>
        <div style={{ fontSize: 13, fontWeight: 600, color: "hsl(var(--text-primary))", marginBottom: 2 }}>{title}</div>
        <div style={{ fontSize: 11, color: "hsl(var(--text-muted))", lineHeight: 1.4 }}>{description}</div>
      </div>
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
      {/* Characters */}
      <SidebarSection title="Characters" icon={<User size={14} />}>
        <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: 8, marginBottom: 8 }}>
          {characters.map((char, i) => (
            <motion.div
              key={char.id}
              whileHover={{ scale: 1.05 }}
              style={{
                aspectRatio: "1", borderRadius: 8, cursor: "pointer",
                background: char.role === "protagonist"
                  ? "linear-gradient(135deg, hsl(355, 60%, 40%), hsl(260, 60%, 50%))"
                  : `linear-gradient(135deg, hsl(${180 + i * 40}, 50%, 30%), hsl(${220 + i * 30}, 50%, 20%))`,
                border: "1px solid hsla(240, 20%, 30%, 0.5)", position: "relative", overflow: "hidden",
                boxShadow: "inset 0 0 20px hsla(0,0%,0%,0.5)", display: "flex", alignItems: "flex-end", padding: 6
              }}
            >
               <span style={{ fontSize: 9, fontWeight: 700, color: "white", textShadow: "0 1px 4px black", zIndex: 10 }}>
                 {char.name}
               </span>
               <div style={{ position: "absolute", top: "50%", left: "50%", transform: "translate(-50%, -50%)", width: 24, height: 24, borderRadius: "50%", background: "hsla(0,0%,0%,0.4)", display: "flex", alignItems: "center", justifyContent: "center", backdropFilter: "blur(4px)" }}>
                 <div style={{ width: 0, height: 0, borderLeft: "6px solid white", borderTop: "4px solid transparent", borderBottom: "4px solid transparent", marginLeft: 2 }} />
               </div>
            </motion.div>
          ))}
        </div>
      </SidebarSection>

      {/* System Architecture */}
      <SidebarSection title="System Architecture" icon={<Bot size={14} />}>
        <div style={{ padding: "0 4px", display: "flex", flexDirection: "column", gap: 0 }}>
          {pipeline.stages.map((stage, i) => {
             const isDone = stage.status === "done";
             const isActive = stage.status === "processing";
             const isQueued = stage.status === "queued" || stage.status === "idle";
             
             return (
               <div key={i} style={{ display: "flex", gap: 12, opacity: isQueued ? 0.4 : 1 }}>
                 {/* Timeline line & node */}
                 <div style={{ display: "flex", flexDirection: "column", alignItems: "center", width: 16 }}>
                   <div style={{ 
                     width: 14, height: 14, borderRadius: "50%", 
                     background: isDone ? "hsla(160, 80%, 40%, 0.2)" : isActive ? "hsla(260, 80%, 60%, 0.2)" : "transparent",
                     border: "1px solid", borderColor: isDone ? "hsl(160, 80%, 40%)" : isActive ? "hsl(260, 80%, 60%)" : "hsl(var(--text-muted))",
                     display: "flex", alignItems: "center", justifyContent: "center", zIndex: 2,
                     marginTop: 4
                   }}>
                     {isDone && <Check size={8} color="hsl(160, 80%, 50%)" />}
                     {isActive && <Loader2 size={10} color="hsl(260, 80%, 60%)" style={{ animation: "spin 1s linear infinite" }} />}
                   </div>
                   {i < pipeline.stages.length - 1 && <div style={{ width: 1, flex: 1, background: "hsla(240, 20%, 30%, 0.5)", marginTop: 2, marginBottom: -4 }} />}
                 </div>
                 {/* Text content */}
                 <div style={{ flex: 1, paddingBottom: 16, paddingTop: 2 }}>
                   <div style={{ fontSize: 13, fontWeight: isDone || isActive ? 600 : 500, color: isDone || isActive ? "hsl(var(--text-primary))" : "hsl(var(--text-muted))" }}>{stage.name}</div>
                   {isActive && <div style={{ fontSize: 11, color: "hsl(260, 80%, 60%)", marginTop: 2 }}>Processing...</div>}
                   {isDone && stage.time && <div style={{ fontSize: 10, color: "hsl(var(--text-muted))", marginTop: 2 }}>{stage.time}s</div>}
                 </div>
               </div>
             )
          })}
        </div>
      </SidebarSection>
    </motion.aside>
  );
}
