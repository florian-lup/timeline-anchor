from __future__ import annotations

"""FastAPI wrapper exposing the AI News Anchor pipeline as a web API.

Run with:

    uvicorn api:app --host 0.0.0.0 --port 8080

The endpoint `/generate-anchor-stream` triggers the news anchor generation flow and
streams the generated Opus audio. Clients must supply a valid API key in the
`X-API-Key` header. Set the expected key via the `ANCHOR_API_KEY` environment
variable (e.g. ANCHOR_API_KEY=your_secret`).
"""

import logging
import os
import uuid
from typing import Iterator

from fastapi import Depends, FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse

from services.get_news import fetch_last_24_hours_articles
from services.write_script import create_anchor_script
from services.generate_speech import generate_anchor_audio_stream

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# API-key authentication dependency
# ---------------------------------------------------------------------------
API_KEY = os.getenv("ANCHOR_API_KEY")

if not API_KEY:
    logger.warning(
        "ANCHOR_API_KEY environment variable not set. All requests will be rejected."
    )


def verify_api_key(x_api_key: str = Header(..., description="API key for authentication")) -> None:  # noqa: D401
    """Raise 401 if the provided key does not match the expected one."""

    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid or missing API key")


# ---------------------------------------------------------------------------
# FastAPI application setup
# ---------------------------------------------------------------------------
app = FastAPI(title="Timeline Anchor API", version="1.0.0")

# Allow requests from anywhere (adjust for production as needed)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["POST"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Helper that encapsulates the three-step pipeline
# ---------------------------------------------------------------------------

def _run_streaming_pipeline(task_id: str) -> Iterator[bytes]:
    """Run the news-anchor pipeline and stream Opus chunks as they're generated."""

    logger.info("[%s] Fetching articles …", task_id)
    articles = fetch_last_24_hours_articles()

    if not articles:
        raise RuntimeError("No articles found in the last 24 hours.")

    logger.info("[%s] Creating script …", task_id)
    script = create_anchor_script(articles)

    logger.info("[%s] Starting streaming speech generation …", task_id)
    # Stream audio chunks as they're generated
    for chunk in generate_anchor_audio_stream(script):
        yield chunk

    logger.info("[%s] Completed streaming pipeline", task_id)


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.post("/generate-anchor-stream", dependencies=[Depends(verify_api_key)])  # type: ignore[arg-type]
async def generate_anchor_stream() -> StreamingResponse:  # noqa: D401
    """Trigger generation and stream back Opus chunks as they're generated.
    
    This endpoint provides true streaming where audio chunks are sent to the client
    as soon as they're generated, allowing playback to start much sooner.
    """

    task_id = uuid.uuid4().hex
    logger.info("[%s] Starting streaming generation", task_id)

    def stream_generator():
        """Generator that yields audio chunks as they're produced."""
        try:
            for chunk in _run_streaming_pipeline(task_id):
                yield chunk
        except Exception as exc:
            logger.exception("[%s] Streaming generation failed", task_id)
            raise

    response = StreamingResponse(stream_generator(), media_type="audio/opus")
    response.headers["X-Task-ID"] = task_id
    response.headers["Content-Disposition"] = "inline; filename=news_anchor.opus"
    response.headers["Transfer-Encoding"] = "chunked"
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    response.headers["Connection"] = "keep-alive"
    return response
