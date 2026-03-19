"use client";
import { motion } from "framer-motion";
import { X, Search, Image, User, History, Loader2, FolderOpen } from "lucide-react";
import { useState, useEffect } from "react";
import { fetchAssets } from "@/hooks/useStream";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

const TABS = [
  { id: "all", label: "All Assets", icon: <Image size={14} /> },
  { id: "images", label: "Images", icon: <Image size={14} /> },
  { id: "json", label: "Data", icon: <History size={14} /> },
];

function getAssetUrl(path) {
  if (!path) return null;
  if (path.startsWith("http")) return path;
  return `${API_BASE}${path.startsWith("/") ? "" : "/"}${path}`;
}

export default function AssetLibrary({ onClose, jobId }) {
  const [activeTab, setActiveTab] = useState("all");
  const [search, setSearch] = useState("");
  const [assets, setAssets] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    fetchAssets(jobId)
      .then((res) => {
        if (!cancelled) setAssets(res.assets || []);
      })
      .catch(() => {
        if (!cancelled) setAssets([]);
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });
    return () => { cancelled = true; };
  }, [jobId]);

  const imageTypes = ["png", "jpg", "jpeg", "webp", "gif"];
  const dataTypes = ["json", "txt"];

  const filtered = assets.filter((a) => {
    const matchTab =
      activeTab === "all" ||
      (activeTab === "images" && imageTypes.includes((a.type || "").toLowerCase())) ||
      (activeTab === "json" && dataTypes.includes((a.type || "").toLowerCase()));
    const matchSearch = !search || a.name?.toLowerCase().includes(search.toLowerCase());
    return matchTab && matchSearch;
  });

  const images = filtered.filter((a) => imageTypes.includes((a.type || "").toLowerCase()));
  const data = filtered.filter((a) => dataTypes.includes((a.type || "").toLowerCase()));

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      style={{
        position: "fixed", inset: 0, background: "hsla(0,0%,0%,0.6)",
        backdropFilter: "blur(8px)", zIndex: 100,
        display: "flex", alignItems: "center", justifyContent: "center",
      }}
      onClick={onClose}
    >
      <motion.div
        initial={{ scale: 0.9, opacity: 0, y: 20 }}
        animate={{ scale: 1, opacity: 1, y: 0 }}
        exit={{ scale: 0.9, opacity: 0, y: 20 }}
        transition={{ type: "spring", damping: 25, stiffness: 300 }}
        onClick={(e) => e.stopPropagation()}
        className="glass-card-elevated"
        style={{
          width: "min(90vw, 900px)", height: "min(85vh, 650px)",
          display: "flex", flexDirection: "column", overflow: "hidden",
        }}
      >
        <div style={{
          display: "flex", alignItems: "center", justifyContent: "space-between",
          padding: "16px 20px", borderBottom: "1px solid var(--glass-border)",
        }}>
          <h2 style={{ fontSize: 17, fontWeight: 700 }}>Asset Library</h2>
          {jobId && <span style={{ fontSize: 11, color: "hsl(var(--text-muted))" }}>Job: {jobId}</span>}
          <button className="btn-icon" onClick={onClose}><X size={18} /></button>
        </div>

        <div style={{
          display: "flex", alignItems: "center", padding: "12px 20px",
          gap: 12, borderBottom: "1px solid var(--glass-border)",
        }}>
          {TABS.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              style={{
                display: "flex", alignItems: "center", gap: 6,
                padding: "8px 14px", borderRadius: 8, fontSize: 12, fontWeight: 500,
                background: activeTab === tab.id ? "hsl(var(--primary))" : "transparent",
                color: activeTab === tab.id ? "white" : "hsl(var(--text-secondary))",
                border: activeTab === tab.id ? "none" : "1px solid hsl(var(--border))",
                cursor: "pointer", transition: "all 0.2s",
              }}
            >
              {tab.icon} {tab.label}
            </button>
          ))}
          <div style={{ flex: 1 }} />
          <div style={{
            display: "flex", alignItems: "center", gap: 8,
            padding: "8px 12px", borderRadius: 8,
            background: "hsl(var(--bg-secondary))", border: "1px solid hsl(var(--border))",
          }}>
            <Search size={14} style={{ color: "hsl(var(--text-muted))" }} />
            <input
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Search..."
              style={{
                background: "transparent", border: "none", outline: "none",
                fontSize: 12, color: "hsl(var(--text-primary))", width: 140,
              }}
            />
          </div>
        </div>

        <div style={{ flex: 1, overflow: "auto", padding: 20 }}>
          {loading ? (
            <div style={{ display: "flex", alignItems: "center", justifyContent: "center", height: 200, gap: 12 }}>
              <Loader2 size={24} style={{ animation: "spin 1s linear infinite", color: "hsl(var(--primary))" }} />
              <span style={{ color: "hsl(var(--text-muted))" }}>Loading assets...</span>
            </div>
          ) : filtered.length === 0 ? (
            <div style={{
              display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center",
              height: 200, color: "hsl(var(--text-muted))", fontSize: 14, gap: 12,
            }}>
              <FolderOpen size={40} style={{ opacity: 0.4 }} />
              <span>No assets yet. Generate a story first.</span>
            </div>
          ) : (
            <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(140px, 1fr))", gap: 14 }}>
              {filtered.map((asset, i) => {
                const isImage = imageTypes.includes((asset.type || "").toLowerCase());
                const url = getAssetUrl(asset.path);
                return (
                  <motion.a
                    key={`${asset.path}-${i}`}
                    href={url}
                    target="_blank"
                    rel="noopener noreferrer"
                    whileHover={{ scale: 1.03, y: -2 }}
                    className="glass-card glow-hover"
                    style={{
                      padding: 10, cursor: "pointer", textDecoration: "none", color: "inherit",
                      display: "block", borderRadius: 10,
                    }}
                  >
                    <div style={{
                      width: "100%", aspectRatio: isImage ? "16/9" : "1",
                      borderRadius: 8, marginBottom: 8, overflow: "hidden",
                      background: isImage ? "black" : "hsl(var(--bg-tertiary))",
                      display: "flex", alignItems: "center", justifyContent: "center",
                    }}>
                      {isImage && url ? (
                        <img src={url} alt={asset.name} style={{ width: "100%", height: "100%", objectFit: "cover" }} />
                      ) : (
                        <User size={24} style={{ color: "hsl(var(--text-muted))", opacity: 0.5 }} />
                      )}
                    </div>
                    <div style={{ fontSize: 11, fontWeight: 500, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>
                      {asset.name}
                    </div>
                    <div style={{ fontSize: 10, color: "hsl(var(--text-muted))", marginTop: 2 }}>
                      {(asset.size / 1024).toFixed(1)} KB
                    </div>
                  </motion.a>
                );
              })}
            </div>
          )}
        </div>
      </motion.div>
    </motion.div>
  );
}
