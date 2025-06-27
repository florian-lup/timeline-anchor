"""Randomly choose a voice for TTS from the configured list."""

from __future__ import annotations

import random

from config import settings

__all__ = ["random_voice"]


def random_voice() -> str:
    """Return a random voice from ``settings.voice_options``."""

    if not settings.voice_options:
        raise ValueError("No voice options configured in settings.")

    return random.choice(settings.voice_options) 