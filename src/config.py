"""
Creator configuration — loads from .env and exposes constants.
"""
import os
from dotenv import load_dotenv

load_dotenv()

# ── API & Cloud ──────────────────────────────────────────────
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")
GOOGLE_CLOUD_PROJECT = os.getenv("GOOGLE_CLOUD_PROJECT", "")
GOOGLE_CLOUD_LOCATION = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")
GCS_BUCKET_NAME = os.getenv("GCS_BUCKET_NAME", "creator-anime-assets")

# ── Model names (documented Gemini family) ───────────────────
# Nano Banana 2 — fast, cost-efficient, all-round image gen
MODEL_FLASH_IMAGE = "gemini-3.1-flash-image-preview"
# Nano Banana Pro — professional quality, thinking mode, up to 4K
MODEL_PRO_IMAGE = "gemini-3-pro-image-preview"
# Text-only reasoning backbone
MODEL_FLASH_TEXT = "gemini-2.0-flash"

# ── Defaults ─────────────────────────────────────────────────
DEFAULT_ASPECT_RATIO = "16:9"
DEFAULT_IMAGE_SIZE = "2K"          # 1K | 2K | 4K (Pro only)
DEFAULT_OUTPUT_DIR = "data/output"
DEFAULT_PARTS_DIR = "parts"
DEFAULT_FINAL_DIR = "final"
