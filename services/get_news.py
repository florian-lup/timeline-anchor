# noqa: D400
"""Service for retrieving the latest news anchor script from MongoDB."""

from __future__ import annotations

from clients.mongodb import get_latest_script


def fetch_latest_script() -> str:
    """Return the most recently created anchor script from MongoDB."""

    return get_latest_script()