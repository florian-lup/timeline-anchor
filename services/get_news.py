"get all the articles from today's date with title and summary from mongodb"

from __future__ import annotations

"""Service for retrieving articles from the last 24 hours from MongoDB."""

from typing import List, Dict

from clients.mongodb import get_articles_today


def fetch_today_articles() -> List[Dict[str, str]]:
    """Return articles from the last 24 hours (title & summary) from MongoDB."""
    return get_articles_today()