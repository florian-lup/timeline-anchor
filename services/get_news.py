"get all the articles from today's date with title and summary from mongodb"

from __future__ import annotations

"""Service for retrieving today's news articles from MongoDB."""

from typing import List, Dict

from clients.mongodb import get_articles_today


def fetch_today_articles() -> List[Dict[str, str]]:
    """Return today's articles (title & summary) from MongoDB."""
    return get_articles_today()