"from the script generate TTS"

from __future__ import annotations

"""Service for generating TTS audio from a news anchor script."""

from pathlib import Path

from clients.openai import generate_speech, generate_speech_bytes


def generate_anchor_audio(script: str, output_file: str | Path = "news_anchor.mp3") -> Path:
    """Generate an MP3 file containing TTS for the given script."""
    return generate_speech(script, output_path=output_file)


# New helper for API use: returns raw bytes instead of writing a file
def generate_anchor_audio_bytes(script: str) -> bytes:
    """Generate TTS audio from ``script`` and return as bytes."""

    return generate_speech_bytes(script)