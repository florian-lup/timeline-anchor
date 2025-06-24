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
    """Return today's articles using the ObjectId-embedded timestamp.

    MongoDB's default ObjectId contains the document's creation time in its
    first 4 bytes. By generating start/end ObjectIds for the UTC boundaries of
    today, we can retrieve all documents inserted today without relying on a
    separate ``date`` field. This keeps the query simple and index-friendly.
    """

    start_of_day = datetime.now(tz=settings.timezone).replace(
        hour=0, minute=0, second=0, microsecond=0
    )
    end_of_day = start_of_day + timedelta(days=1)

    with _get_client() as client:
        collection = client[settings.mongodb_db][settings.mongodb_collection]

        start_oid = ObjectId.from_datetime(start_of_day)
        end_oid = ObjectId.from_datetime(end_of_day)

        cursor = collection.find(
            {"_id": {"$gte": start_oid, "$lt": end_oid}},
            {"_id": 0, "title": 1, "summary": 1},
        )
        return list(cursor)
