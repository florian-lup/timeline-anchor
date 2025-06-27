from __future__ import annotations

"""MongoDB client helpers."""

from pymongo import MongoClient

from config import settings

# Reuse a single MongoClient instance across requests to avoid the connection
# establishment overhead (≈200-300 ms). MongoClient is thread-safe and
# maintains its own internal connection pool, so a singleton pattern is safe.
_client: MongoClient | None = None


def _get_client() -> MongoClient:
    """Return a cached MongoClient instance (create it on first use)."""

    global _client
    if _client is None:
        _client = MongoClient(settings.mongodb_uri)
    return _client


# ---------------------------------------------------------------------------
# Public helpers
# ---------------------------------------------------------------------------

def get_latest_script() -> str:
    """Return the most recently inserted script from the ``scripts`` collection.

    The collection is sorted by the default ``_id`` ObjectId which contains
    a creation timestamp. Sorting by ``_id`` descending and limiting to one
    document gives us the latest entry without requiring an additional
    timestamp index.

    The document is expected to have an ``anchor`` field containing the
    text that should be narrated by the news anchor.
    """

    client = _get_client()
    collection = client[settings.mongodb_db]["scripts"]

    doc = collection.find_one({}, {"_id": 0, "anchor": 1}, sort=[("_id", -1)])

    if not doc or "anchor" not in doc:
        raise RuntimeError("No scripts found in the 'scripts' collection or missing 'anchor' field.")

    return doc["anchor"]
