"from the script generate TTS"

from __future__ import annotations

"""Service for generating TTS audio from a news anchor script."""

from pathlib import Path

from clients.openai import generate_speech


def generate_anchor_audio(script: str, output_file: str | Path = "news_anchor.mp3") -> Path:
    """Generate an MP3 file containing TTS for the given script."""
    return generate_speech(script, output_path=output_file)