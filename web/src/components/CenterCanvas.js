"use client";
import { motion, AnimatePresence } from "framer-motion";
import { ChevronLeft, ChevronRight, Play, Pause, SkipBack, SkipForward, Volume2, VolumeX, Maximize2, Minimize2 } from "lucide-react";
import { useState, useCallback, useEffect, useRef } from "react";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

function getImageUrl(url) {
  if (!url) return null;
  if (url.startsWith("http")) return url;
  if (url.startsWith("/output/")) return `${API_BASE}${url}`;
  if (url.startsWith("data/output/")) return `${API_BASE}/output/${url.replace("data/output/", "")}`;
  return url;
}

export default function CenterCanvas({ scenes, rlData, selectedScene, onSelectScene, characters }) {
  const [isPlaying, setIsPlaying] = useState(false);
  const [volumeMuted, setVolumeMuted] = useState(false);
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [currentIndex, setCurrentIndex] = useState(0);
  const viewerRef = useRef(null);

  const sceneList = scenes?.length > 0 ? scenes : [];
  const activeScene = selectedScene || sceneList[currentIndex] || sceneList[0];

  const goPrev = useCallback(() => {
    const idx = sceneList.findIndex((s) => (s.id || s.scene_id) === (activeScene?.id ?? activeScene?.scene_id));
    if (idx > 0) {
      const next = sceneList[idx - 1];
      setCurrentIndex(idx - 1);
      onSelectScene?.(next);
    }
  }, [sceneList, activeScene, onSelectScene]);

  const goNext = useCallback(() => {
    const idx = sceneList.findIndex((s) => (s.id || s.scene_id) === (activeScene?.id ?? activeScene?.scene_id));
    if (idx >= 0 && idx < sceneList.length - 1) {
      const next = sceneList[idx + 1];
      setCurrentIndex(idx + 1);
      onSelectScene?.(next);
    }
  }, [sceneList, activeScene, onSelectScene]);

  const totalDuration = sceneList.reduce((acc, s) => acc + (s.duration || 3), 0);
  const imageUrl = getImageUrl(activeScene?.imageUrl) || null;

  const advanceSlide = useCallback(() => {
    if (sceneList.length <= 1) return;
    setCurrentIndex((i) => {
      const next = i + 1;
      if (next >= sceneList.length) {
        onSelectScene?.(sceneList[0]);
        return 0;
      }
      onSelectScene?.(sceneList[next]);
      return next;
    });
  }, [sceneList, onSelectScene]);

  useEffect(() => {
    if (!isPlaying || sceneList.length <= 1) return;
    const t = setInterval(advanceSlide, 3000);
    return () => clearInterval(t);
  }, [isPlaying, sceneList.length, advanceSlide]);

  useEffect(() => {
    const onFullscreenChange = () => setIsFullscreen(!!document.fullscreenElement);
    document.addEventListener("fullscreenchange", onFullscreenChange);
    return () => document.removeEventListener("fullscreenchange", onFullscreenChange);
  }, []);

  const toggleFullscreen = useCallback(() => {
    if (!viewerRef.current) return;
    if (!document.fullscreenElement) {
      viewerRef.current.requestFullscreen?.().then(() => setIsFullscreen(true)).catch(() => {});
    } else {
      document.exitFullscreen?.().then(() => setIsFullscreen(false)).catch(() => {});
    }
  }, []);

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.98 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.5, ease: [0.16, 1, 0.3, 1] }}
      style={{
        flex: 1, height: "100%", display: "flex", flexDirection: "column",
        alignItems: "center", justifyContent: "center", position: "relative", zIndex: 1,
      }}
    >
      {/* Scene Carousel */}
      <div style={{ width: "100%", maxWidth: 1100, display: "flex", alignItems: "center", gap: 16 }}>
        <button
          className="btn-icon"
          onClick={goPrev}
          disabled={!sceneList.length || currentIndex <= 0}
          style={{
            width: 44, height: 44, borderRadius: 12,
            background: "hsl(var(--bg-tertiary) / 0.9)",
            opacity: sceneList.length && currentIndex > 0 ? 1 : 0.4,
            flexShrink: 0,
          }}
        >
          <ChevronLeft size={24} />
        </button>

        {/* Main Viewer */}
        <div
          ref={viewerRef}
          style={{
            flex: 1, aspectRatio: "16/9", position: "relative",
            background: "hsl(var(--bg-primary))", borderRadius: 16,
            border: "1px solid hsl(var(--border))",
            boxShadow: "var(--shadow-lg)",
            overflow: "hidden",
          }}
        >
          <AnimatePresence mode="wait">
            <motion.div
              key={activeScene?.id ?? activeScene?.scene_id ?? "empty"}
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              transition={{ duration: 0.3 }}
              style={{
                width: "100%", height: "100%",
                background: imageUrl ? "black" : "hsl(var(--bg-primary))",
                display: "flex", alignItems: "center", justifyContent: "center",
              }}
            >
              {imageUrl ? (
                <img
                  src={imageUrl}
                  alt={activeScene?.title || "Scene"}
                  style={{ width: "100%", height: "100%", objectFit: "cover" }}
                />
              ) : (
                <div style={{
                  textAlign: "center", color: "hsl(var(--text-muted))", fontSize: 14,
                  display: "flex", flexDirection: "column", alignItems: "center", gap: 8,
                }}>
                  <div style={{ width: 48, height: 48, borderRadius: 12, background: "hsl(var(--bg-tertiary) / 0.8)", display: "flex", alignItems: "center", justifyContent: "center" }}>
                    <Play size={24} style={{ opacity: 0.5 }} />
                  </div>
                  {sceneList.length > 0 ? "Loading scene..." : "Generate a story to see scenes"}
                </div>
              )}

              {/* Overlays */}
              <div style={{ position: "absolute", top: 12, left: 12, right: 12, display: "flex", justifyContent: "space-between", pointerEvents: "none" }}>
                <div style={{
                  padding: "6px 12px", borderRadius: 8,
                  background: "hsla(0,0%,0%,0.6)", backdropFilter: "blur(8px)",
                  fontSize: 12, fontWeight: 600, color: "white",
                }}>
                  Scene {activeScene?.id ?? activeScene?.scene_id ?? "—"} · {activeScene?.title || "—"}
                </div>
                {rlData?.totalReward > 0 && (
                  <div style={{
                    padding: "6px 12px", borderRadius: 8,
                    background: "hsla(160, 84%, 39%, 0.2)", border: "1px solid hsla(160, 84%, 45%, 0.4)",
                    fontSize: 11, fontWeight: 600, color: "hsl(160, 84%, 65%)",
                  }}>
                    RL: {(activeScene?.rlScore ?? rlData.totalReward).toFixed(2)}
                  </div>
                )}
              </div>
              {activeScene?.trait && (
                <div style={{
                  position: "absolute", bottom: 60, left: 12,
                  padding: "4px 10px", borderRadius: 6,
                  background: "hsla(0,0%,0%,0.5)", fontSize: 11, color: "hsla(255,255,255,0.9)",
                }}>
                  Arc: {activeScene.trait}
                </div>
              )}
            </motion.div>
          </AnimatePresence>
        </div>

        <button
          className="btn-icon"
          onClick={goNext}
          disabled={!sceneList.length || currentIndex >= sceneList.length - 1}
          style={{
            width: 44, height: 44, borderRadius: 12,
            background: "hsl(var(--bg-tertiary) / 0.9)",
            opacity: sceneList.length && currentIndex < sceneList.length - 1 ? 1 : 0.4,
            flexShrink: 0,
          }}
        >
          <ChevronRight size={24} />
        </button>
      </div>

      {/* Player Controls */}
      <div
        className="panel-controls glass-card"
        style={{
          marginTop: 16, width: "100%", maxWidth: 1100,
          padding: 14, display: "flex", alignItems: "center", gap: 16,
        }}
      >
        <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
          <button className="btn-icon" style={{ width: 36, height: 36 }} onClick={() => { setCurrentIndex(0); sceneList[0] && onSelectScene?.(sceneList[0]); }}>
            <SkipBack size={16} />
          </button>
          <button
            className="btn-icon"
            style={{ width: 40, height: 40, background: "hsl(var(--primary))", color: "white" }}
            onClick={() => setIsPlaying(!isPlaying)}
          >
            {isPlaying ? <Pause size={18} /> : <Play size={18} style={{ marginLeft: 2 }} />}
          </button>
          <button className="btn-icon" style={{ width: 36, height: 36 }} onClick={() => { const last = sceneList.length - 1; setCurrentIndex(last); sceneList[last] && onSelectScene?.(sceneList[last]); }}>
            <SkipForward size={16} />
          </button>
        </div>
        <div style={{ flex: 1, fontSize: 11, fontFamily: "monospace", color: "hsl(var(--text-secondary))" }}>
          {currentIndex + 1} / {sceneList.length || 1} · ~{totalDuration}s total
        </div>
        <div style={{ display: "flex", alignItems: "center", gap: 4 }}>
          <button
            className="btn-icon"
            onClick={() => setVolumeMuted((m) => !m)}
            title={volumeMuted ? "Unmute" : "Mute"}
            aria-label={volumeMuted ? "Unmute" : "Mute"}
          >
            {volumeMuted ? <VolumeX size={16} /> : <Volume2 size={16} />}
          </button>
          <button
            className="btn-icon"
            onClick={toggleFullscreen}
            title={isFullscreen ? "Exit fullscreen" : "Fullscreen"}
            aria-label={isFullscreen ? "Exit fullscreen" : "Fullscreen"}
          >
            {isFullscreen ? <Minimize2 size={16} /> : <Maximize2 size={16} />}
          </button>
        </div>
      </div>

      {/* Scene Thumbnails Strip */}
      {sceneList.length > 1 && (
        <div style={{
          marginTop: 12, width: "100%", maxWidth: 1100,
          display: "flex", gap: 8, overflowX: "auto", paddingBottom: 4,
        }}>
          {sceneList.map((s, i) => {
            const isActive = (s.id ?? s.scene_id) === (activeScene?.id ?? activeScene?.scene_id);
            const thumbUrl = getImageUrl(s.imageUrl);
            return (
              <button
                key={s.id ?? s.scene_id ?? i}
                onClick={() => { setCurrentIndex(i); onSelectScene?.(s); }}
                style={{
                  flexShrink: 0, width: 80, height: 45, borderRadius: 8, overflow: "hidden",
                  border: isActive ? "2px solid hsl(var(--primary))" : "1px solid hsl(var(--border))",
                  background: thumbUrl ? "black" : "hsl(var(--bg-tertiary))",
                  cursor: "pointer", padding: 0,
                }}
              >
                {thumbUrl ? (
                  <img src={thumbUrl} alt="" style={{ width: "100%", height: "100%", objectFit: "cover" }} />
                ) : (
                  <div style={{ width: "100%", height: "100%", display: "flex", alignItems: "center", justifyContent: "center", fontSize: 10, color: "hsl(var(--text-muted))" }}>
                    {i + 1}
                  </div>
                )}
              </button>
            );
          })}
        </div>
      )}
    </motion.div>
  );
}
