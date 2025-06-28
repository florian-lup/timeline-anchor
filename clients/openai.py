from __future__ import annotations

"""OpenAI client helper for streaming text-to-speech generation."""

import logging
from typing import Iterator

from openai import OpenAI

from config import settings
from utils.voice import random_voice

logger = logging.getLogger(__name__)


_client: OpenAI | None = None


def _get_client() -> OpenAI:
    global _client
    if _client is None:
        if not settings.openai_api_key:
            raise EnvironmentError(
                "OPENAI_API_KEY environment variable is required but not set."
            )
        _client = OpenAI(api_key=settings.openai_api_key)
    return _client


def generate_speech_stream(
    text: str,
    *,
    voice: str | None = None,
) -> Iterator[bytes]:
    """Generate TTS audio from ``text`` and yield chunks as they arrive.
    
    This enables true streaming where audio chunks are yielded immediately
    as they're received from OpenAI, allowing clients to start playing
    audio before the entire generation is complete.
    """

    client = _get_client()

    voice = voice or random_voice()

    logger.info("Starting streaming TTS audio generation using model %s", settings.tts_model)

    with client.audio.speech.with_streaming_response.create(
        model=settings.tts_model,
        voice=voice,
        input=text,
        response_format=settings.audio_format,
    ) as response:
        # Yield chunks as they arrive from OpenAI
        # Use 4096-byte chunks to reduce time to first audio byte; OpenAI streams
        # quickly enough that the smaller chunk size does not significantly
        # increase overhead but can shave ~50 ms from perceived latency.
        for chunk in response.iter_bytes(chunk_size=4096):
            yield chunk

    logger.info("Completed streaming TTS audio generation")
