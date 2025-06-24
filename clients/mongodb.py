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


def get_articles_today() -> List[Dict[str, str]]:
    """Return articles created in the **last 24 hours** using ObjectId timestamps.

    MongoDB ObjectIds encode creation time (UTC) in their first 4 bytes. By
    generating ObjectIds for *now* and *24 hours ago* we can efficiently query
    recent documents with the built-in index on ``_id``.
    """

    now = datetime.now(tz=settings.timezone)
    start_time = now - timedelta(hours=24)

    with _get_client() as client:
        collection = client[settings.mongodb_db][settings.mongodb_collection]

        start_oid = ObjectId.from_datetime(start_time)
        end_oid = ObjectId.from_datetime(now)

        cursor = collection.find(
            {"_id": {"$gte": start_oid, "$lt": end_oid}},
            {"_id": 0, "title": 1, "summary": 1},
        )
        return list(cursor)
