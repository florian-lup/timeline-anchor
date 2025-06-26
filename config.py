from __future__ import annotations

"""Central configuration settings for the AI News Anchor project.

All sensitive information should be provided via environment variables so that
no secrets are hard-coded into the repository.
"""

import os
from dataclasses import dataclass
from datetime import timezone
from dotenv import load_dotenv

load_dotenv()

@dataclass(frozen=True)
class Settings:
    """Runtime settings loaded from the environment."""

    # MongoDB
    mongodb_uri: str = os.getenv("MONGODB_URI")
    mongodb_db: str = os.getenv("MONGODB_DB", "events")
    mongodb_collection: str = os.getenv("MONGODB_COLLECTION", "articles")

    # OpenAI
    openai_api_key: str | None = os.getenv("OPENAI_API_KEY")
    chat_model: str = os.getenv("CHAT_MODEL", "gpt-4.1-mini-2025-04-14")
    chat_max_tokens: int = int(os.getenv("CHAT_MAX_TOKENS", 500))
    chat_temperature: float = float(os.getenv("CHAT_TEMPERATURE", 0.5))
    tts_model: str = os.getenv("TTS_MODEL", "gpt-4o-mini-tts")

    # Speech generation options
    voice: str = os.getenv("ANCHOR_VOICE", "alloy")
    audio_format: str = os.getenv("AUDIO_FORMAT", "wav")

    # General
    timezone: timezone = timezone.utc

settings = Settings()