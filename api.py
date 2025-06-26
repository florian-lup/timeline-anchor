from __future__ import annotations

"""FastAPI wrapper exposing the AI News Anchor pipeline as a web API.

Run with:

    uvicorn api:app --host 0.0.0.0 --port 8080

The endpoint `/generate-anchor` triggers the news anchor generation flow and
returns the generated MP3. Clients must supply a valid API key in the
`X-API-Key` header. Set the expected key via the `ANCHOR_API_KEY` environment
variable (e.g. `fly secrets set ANCHOR_API_KEY=your_secret`).
"""

import logging
import os
import uuid
from io import BytesIO

from fastapi import Depends, FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse

from services.get_news import fetch_last_24_hours_articles
from services.write_script import create_anchor_script
from services.generate_speech import generate_anchor_audio_bytes

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

def _run_pipeline(task_id: str) -> bytes:
    """Run the news-anchor pipeline and return MP3 bytes."""

    logger.info("[%s] Fetching articles …", task_id)
    articles = fetch_last_24_hours_articles()

    if not articles:
        raise RuntimeError("No articles found in the last 24 hours.")

    logger.info("[%s] Creating script …", task_id)
    script = create_anchor_script(articles)

    logger.info("[%s] Generating speech …", task_id)
    audio_bytes = generate_anchor_audio_bytes(script)

    return audio_bytes


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------


@app.post("/generate-anchor", dependencies=[Depends(verify_api_key)])  # type: ignore[arg-type]
async def generate_anchor() -> StreamingResponse:  # noqa: D401
    """Trigger generation and stream back the resulting MP3 file."""

    import asyncio

    task_id = uuid.uuid4().hex

    loop = asyncio.get_running_loop()

    try:
        audio_bytes = await loop.run_in_executor(None, _run_pipeline, task_id)
    except Exception as exc:  # pragma: no cover
        logger.exception("[%s] Generation failed", task_id)
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    logger.info("[%s] Completed successfully", task_id)

    buffer = BytesIO(audio_bytes)

    response = StreamingResponse(buffer, media_type="audio/mpeg")
    response.headers["X-Task-ID"] = task_id
    response.headers["Content-Disposition"] = "inline; filename=news_anchor.mp3"
    return response
