
from __future__ import annotations

"""Service for generating TTS audio from a news anchor script."""

from typing import Iterator

from clients.openai import generate_speech_stream


def generate_anchor_audio_stream(script: str) -> Iterator[bytes]:
    """Generate TTS audio from ``script`` and yield chunks as they arrive.
    
    This enables true streaming where audio chunks are yielded immediately
    as they're received, allowing clients to start playing audio before 
    the entire generation is complete.
    """
    
    return generate_speech_stream(script)