"""
EditorAgent — final assembly, transitions, subtitles, and encoding.
Merges keyframes + audio into video parts using ffmpeg.
"""
import os
import json
import subprocess
import shutil
from typing import Dict, Any, List, Optional

from src.agents.base_agent import BaseAgent
from src.config import DEFAULT_OUTPUT_DIR, DEFAULT_PARTS_DIR, DEFAULT_FINAL_DIR


class EditorAgent(BaseAgent):
    """
    Agent 7: Video assembly and final encoding.
    Input:  keyframes + animation plan + audio plan
    Output: rendered video parts and merged final episode
    """

    def __init__(self, output_dir: str = DEFAULT_OUTPUT_DIR, **kwargs):
        super().__init__(name="EditorAgent", **kwargs)
        self.output_dir = output_dir
        self.parts_dir = os.path.join(output_dir, DEFAULT_PARTS_DIR)
        self.final_dir = os.path.join(output_dir, DEFAULT_FINAL_DIR)
        os.makedirs(self.parts_dir, exist_ok=True)
        os.makedirs(self.final_dir, exist_ok=True)

    def _check_ffmpeg(self) -> bool:
        """Check if ffmpeg is available."""
        return shutil.which("ffmpeg") is not None

    def _create_slideshow_part(
        self,
        part: Dict,
        keyframes: List[Dict],
        part_index: int,
    ) -> Optional[str]:
        """
        Create a video part from keyframe images using ffmpeg.
        Each keyframe is shown for its specified duration.
        """
        if not self._check_ffmpeg():
            self.log("  Warning: ffmpeg not found — skipping video render")
            return None

        # Filter keyframes that belong to this part's sequences
        part_keyframes = []
        for seq in part.get("sequences", []):
            kf_idx = seq.get("keyframe_index", -1)
            if 0 <= kf_idx < len(keyframes):
                kf = keyframes[kf_idx]
                if kf.get("local_path") and os.path.exists(kf["local_path"]):
                    part_keyframes.append({
                        "path": kf["local_path"],
                        "duration": seq.get("duration_seconds", 3),
                    })

        if not part_keyframes:
            self.log(f"  No valid keyframes for part {part_index + 1}")
            return None

        # Create ffmpeg concat file
        concat_path = os.path.join(self.parts_dir, f"part{part_index + 1}_concat.txt")
        with open(concat_path, "w") as f:
            for kf in part_keyframes:
                f.write(f"file '{os.path.abspath(kf['path'])}'\n")
                f.write(f"duration {kf['duration']}\n")
            # Repeat last frame to avoid ffmpeg cutting it short
            if part_keyframes:
                f.write(f"file '{os.path.abspath(part_keyframes[-1]['path'])}'\n")

        output_path = os.path.join(self.parts_dir, f"ep01_part{part_index + 1:02d}.mp4")

        cmd = [
            "ffmpeg", "-y",
            "-f", "concat", "-safe", "0",
            "-i", concat_path,
            "-vsync", "vfr",
            "-pix_fmt", "yuv420p",
            "-c:v", "libx264",
            "-crf", "23",
            output_path,
        ]

        try:
            subprocess.run(cmd, capture_output=True, check=True, timeout=120)
            self.log(f"  Rendered: {output_path}")
            return output_path
        except subprocess.CalledProcessError as e:
            self.log(f"  ffmpeg error: {e.stderr.decode()[:200]}")
            return None
        except FileNotFoundError:
            self.log("  ffmpeg not found")
            return None

    def _merge_parts(self, part_paths: List[str]) -> Optional[str]:
        """Concatenate all parts into a single final episode."""
        if not part_paths or not self._check_ffmpeg():
            return None

        concat_path = os.path.join(self.final_dir, "final_concat.txt")
        with open(concat_path, "w") as f:
            for pp in part_paths:
                f.write(f"file '{os.path.abspath(pp)}'\n")

        final_path = os.path.join(self.final_dir, "ep01_full_anime.mp4")

        cmd = [
            "ffmpeg", "-y",
            "-f", "concat", "-safe", "0",
            "-i", concat_path,
            "-c", "copy",
            final_path,
        ]

        try:
            subprocess.run(cmd, capture_output=True, check=True, timeout=120)
            self.log(f"  Final episode: {final_path}")

            # Upload to GCS
            self.gcs.upload_blob(final_path, "final/ep01_full_anime.mp4")
            return final_path
        except Exception as e:
            self.log(f"  Merge error: {e}")
            return None

    def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        animation_plan = input_data.get("animation_plan", {})
        keyframes_data = input_data.get("keyframes", {})
        audio_plan = input_data.get("audio_plan", {})

        self.log("Assembling anime episode...")

        keyframes = keyframes_data.get("keyframes", [])
        parts = animation_plan.get("parts", [])

        # Render each part
        rendered_parts: List[str] = []
        for i, part in enumerate(parts):
            self.log(f"  Rendering Part {i + 1}: {part.get('part_title', '')}")
            path = self._create_slideshow_part(part, keyframes, i)
            if path:
                rendered_parts.append(path)

                # Upload part to GCS
                gcs_path = f"parts/ep01_part{i + 1:02d}.mp4"
                self.gcs.upload_blob(path, gcs_path)

        # Merge all parts
        final_path = None
        if len(rendered_parts) > 1:
            final_path = self._merge_parts(rendered_parts)
        elif len(rendered_parts) == 1:
            # Single part IS the final
            final_path = rendered_parts[0]
            self.gcs.upload_blob(final_path, "final/ep01_full_anime.mp4")

        # Save assembly manifest
        manifest = {
            "rendered_parts": rendered_parts,
            "final_episode": final_path,
            "animation_plan_summary": {
                "total_parts": len(parts),
                "fps": animation_plan.get("fps", 24),
                "total_duration": animation_plan.get("total_duration_seconds", 0),
            },
        }
        manifest_path = os.path.join(self.output_dir, "assembly_manifest.json")
        with open(manifest_path, "w") as f:
            json.dump(manifest, f, indent=2)

        self.log(f"Assembly complete — {len(rendered_parts)} parts, final: {final_path or 'N/A'}")
        return manifest
