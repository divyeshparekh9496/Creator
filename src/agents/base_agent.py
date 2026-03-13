"""
Base class for all Creator agents.
"""
from abc import ABC, abstractmethod
import os
from typing import Dict, Any, Optional

from src.utils.genai_client import GenAIClient
from src.utils.gcp_utils import GCPUtils
from src.config import MODEL_FLASH_TEXT


class BaseAgent(ABC):
    """Abstract base for every agent in the Creator pipeline."""

    def __init__(
        self,
        name: str,
        genai_client: Optional[GenAIClient] = None,
        gcs: Optional[GCPUtils] = None,
        model_name: str = MODEL_FLASH_TEXT,
    ):
        self.name = name
        self.model_name = model_name
        self.genai = genai_client or GenAIClient()
        self.gcs = gcs or GCPUtils()

    @abstractmethod
    def run(self, input_data: Any) -> Dict[str, Any]:
        """Execute the agent's core logic and return structured output."""
        pass

    def log(self, message: str):
        print(f"[{self.name}] {message}")
