"""
LLM Configuration Module
"""

import os
from dataclasses import dataclass

@dataclass
class LLMConfig:
    """Configuration for LLM generation."""
    
    # Model settings
    model_name: str = "models/gemini-1.5-flash"  # Explicit prefix
    temperature: float = 0.3              # Lower for factual accuracy
    max_output_tokens: int = 1024
    top_p: float = 0.95
    top_k: int = 40
    
    # API Settings
    api_key: str = os.getenv("GOOGLE_API_KEY", "")
    
    # RAG Settings
    max_context_chunks: int = 5           # Number of chunks to retrieve
    
    @classmethod
    def from_env(cls):
        """Load configuration from environment variables."""
        return cls(
            api_key=os.getenv("GOOGLE_API_KEY", ""),
            model_name=os.getenv("LLM_MODEL", "models/gemini-1.5-flash")
        )
