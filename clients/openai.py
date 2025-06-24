from __future__ import annotations

"""OpenAI client helpers for chat completions and TTS generation."""

import logging
from pathlib import Path
from typing import List, Dict

from openai import OpenAI

from config import settings

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


def chat_completion(messages: List[Dict[str, str]], max_tokens: int = 2000) -> str:
    """Return the assistant's response text using the configured chat model."""

    client = _get_client()

    response = client.chat.completions.create(
        model=settings.chat_model,
        messages=messages,
        max_tokens=max_tokens,
        temperature=0.5,
    )
    return response.choices[0].message.content.strip()


def generate_speech(
    text: str,
    output_path: str | Path = "news_anchor.mp3",
    *,
    voice: str | None = None,
) -> Path:
    """Generate TTS audio from ``text`` and save to ``output_path``.

    Returns the ``Path`` to the generated file.
    """

    client = _get_client()

    voice = voice or settings.voice

    logger.info("Generating TTS audio using model %s", settings.tts_model)

    response = client.audio.speech.create(
        model=settings.tts_model,
        voice=voice,
        input=text,
        response_format=settings.audio_format,
    )

    output_path = Path(output_path)
    response.stream_to_file(str(output_path))

    logger.info("Audio saved to %s", output_path)
    return output_path
