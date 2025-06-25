from __future__ import annotations

"""MongoDB client helpers."""

import contextlib
from datetime import datetime, timedelta
from typing import Iterator, List, Dict

from pymongo import MongoClient
from bson.objectid import ObjectId

from config import settings


@contextlib.contextmanager
def _get_client() -> Iterator[MongoClient]:
    """Yield a MongoDB client and make sure it is closed afterwards."""
    client = MongoClient(settings.mongodb_uri)
    try:
        yield client
    finally:
        client.close()


def get_articles_last_24_hours() -> List[Dict[str, str]]:
    """Return articles from the last 24 hours using the ObjectId-embedded timestamp.

    MongoDB's default ObjectId contains the document's creation time in its
    first 4 bytes. By generating start/end ObjectIds for the last 24 hours,
    we can retrieve all documents inserted in that timeframe without relying on a
    separate ``date`` field. This keeps the query simple and index-friendly.
    """

    now = datetime.now(tz=settings.timezone)
    start_time = now - timedelta(hours=24)
    end_time = now

    with _get_client() as client:
        collection = client[settings.mongodb_db][settings.mongodb_collection]

        start_oid = ObjectId.from_datetime(start_time)
        end_oid = ObjectId.from_datetime(end_time)

        cursor = collection.find(
            {"_id": {"$gte": start_oid, "$lt": end_oid}},
            {"_id": 0, "title": 1, "summary": 1},
        )
        return list(cursor)
