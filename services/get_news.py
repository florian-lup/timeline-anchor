"get all the articles from the last 24 hours with title and summary from mongodb"

from __future__ import annotations

"""Service for retrieving news articles from the last 24 hours from MongoDB."""

from typing import List, Dict

from clients.mongodb import get_articles_last_24_hours


def fetch_last_24_hours_articles() -> List[Dict[str, str]]:
    """Return articles from the last 24 hours (title & summary) from MongoDB."""
    return get_articles_last_24_hours()