"""
Thin wrapper around the Google GenAI SDK.

All calls use documented patterns from:
https://ai.google.dev/gemini-api/docs/image-generation
"""
import os
import json
from typing import List, Optional, Union
from PIL import Image
from google import genai
from google.genai import types

from src.config import (
    GOOGLE_API_KEY,
    MODEL_FLASH_IMAGE,
    MODEL_PRO_IMAGE,
    MODEL_FLASH_TEXT,
    DEFAULT_ASPECT_RATIO,
    DEFAULT_IMAGE_SIZE,
)


class GenAIClient:
    """Wrapper for Gemini model calls — text, image, and interleaved."""

    def __init__(self, api_key: Optional[str] = None):
        key = api_key or GOOGLE_API_KEY
        if not key:
            raise ValueError(
                "GOOGLE_API_KEY is required. Set it in .env or pass it directly."
            )
        self.client = genai.Client(api_key=key)

    # ── Text-only generation ─────────────────────────────────
    def generate_text(
        self,
        prompt: str,
        model: str = MODEL_FLASH_TEXT,
        system_instruction: Optional[str] = None,
    ) -> str:
        """Return plain text from the model."""
        config = types.GenerateContentConfig(
            response_modalities=["Text"],
        )
        if system_instruction:
            config.system_instruction = system_instruction

        response = self.client.models.generate_content(
            model=model,
            contents=[prompt],
            config=config,
        )
        return response.text or ""

    def generate_json(
        self,
        prompt: str,
        model: str = MODEL_FLASH_TEXT,
        system_instruction: Optional[str] = None,
    ) -> dict:
        """Generate text and parse it as JSON."""
        raw = self.generate_text(prompt, model, system_instruction)
        # Strip markdown code fences if present
        cleaned = raw.strip()
        if cleaned.startswith("```"):
            lines = cleaned.split("\n")
            lines = lines[1:]  # remove opening fence
            if lines and lines[-1].strip() == "```":
                lines = lines[:-1]
            cleaned = "\n".join(lines)
        return json.loads(cleaned)

    # ── Image generation ─────────────────────────────────────
    def generate_image(
        self,
        prompt: str,
        model: str = MODEL_FLASH_IMAGE,
        aspect_ratio: str = DEFAULT_ASPECT_RATIO,
        image_size: str = DEFAULT_IMAGE_SIZE,
    ) -> Optional[Image.Image]:
        """Generate a single image from a text prompt."""
        response = self.client.models.generate_content(
            model=model,
            contents=[prompt],
            config=types.GenerateContentConfig(
                response_modalities=["Image"],
                image_config=types.ImageConfig(
                    aspect_ratio=aspect_ratio,
                    image_size=image_size,
                ),
            ),
        )
        for part in response.parts:
            if part.inline_data is not None:
                return part.as_image()
        return None

    # ── Image editing (with reference images) ────────────────
    def edit_image(
        self,
        prompt: str,
        reference_images: List[Image.Image],
        model: str = MODEL_FLASH_IMAGE,
        aspect_ratio: str = DEFAULT_ASPECT_RATIO,
        image_size: str = DEFAULT_IMAGE_SIZE,
    ) -> Optional[Image.Image]:
        """Edit or compose images using text + reference images."""
        contents: list = [prompt] + reference_images
        response = self.client.models.generate_content(
            model=model,
            contents=contents,
            config=types.GenerateContentConfig(
                response_modalities=["Image"],
                image_config=types.ImageConfig(
                    aspect_ratio=aspect_ratio,
                    image_size=image_size,
                ),
            ),
        )
        for part in response.parts:
            if part.inline_data is not None:
                return part.as_image()
        return None

    # ── Interleaved text + image generation ───────────────────
    def generate_interleaved(
        self,
        prompt: str,
        model: str = MODEL_FLASH_IMAGE,
        aspect_ratio: str = DEFAULT_ASPECT_RATIO,
        image_size: str = DEFAULT_IMAGE_SIZE,
    ) -> List[Union[str, Image.Image]]:
        """Return a list of text/image parts (interleaved output)."""
        response = self.client.models.generate_content(
            model=model,
            contents=[prompt],
            config=types.GenerateContentConfig(
                response_modalities=["Text", "Image"],
                image_config=types.ImageConfig(
                    aspect_ratio=aspect_ratio,
                    image_size=image_size,
                ),
            ),
        )
        results: List[Union[str, Image.Image]] = []
        for part in response.parts:
            if part.text is not None:
                results.append(part.text)
            elif part.inline_data is not None:
                results.append(part.as_image())
        return results
