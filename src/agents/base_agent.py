from abc import ABC, abstractmethod
import os
from typing import Dict, Any, List

class BaseAgent(ABC):
      """Base class for all Creator agents."""

    def __init__(self, name: str, model_name: str = "gemini-2.0-flash"):
              self.name = name
              self.model_name = model_name
              self.project_id = os.getenv("GOOGLE_CLOUD_PROJECT")
              self.location = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")

    @abstractmethod
    def run(self, input_data: Any) -> Dict[str, Any]:
              """Execute the agent's core logic."""
              pass

    def log(self, message: str):
              print(f"[{self.name}] {message}")
      
