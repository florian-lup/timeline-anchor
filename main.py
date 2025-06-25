from __future__ import annotations

"""Entrypoint for the AI News Anchor flow."""

import logging
from pathlib import Path

from services.get_news import fetch_last_24_hours_articles
from services.write_script import create_anchor_script
from services.generate_speech import generate_anchor_audio

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


def main() -> None:
    logger.info("Fetching news articles from the last 24 hours …")
    articles = fetch_last_24_hours_articles()
    logger.info("Found %d articles", len(articles))

    if not articles:
        logger.warning("No articles found for the last 24 hours. Aborting.")
        return

    # Create artefacts directory if it doesn't exist
    artefacts_dir = Path("artefacts")
    artefacts_dir.mkdir(exist_ok=True)

    # Clear old artefacts before generating new ones
    if artefacts_dir.exists():
        for file in artefacts_dir.glob("*"):
            file.unlink()

    logger.info("Generating anchor script …")
    script = create_anchor_script(articles)

    script_path = artefacts_dir / "anchor_script.txt"
    script_path.write_text(script, encoding="utf-8")
    logger.info("Script saved to %s", script_path)

    logger.info("Generating TTS audio …")
    audio_path = generate_anchor_audio(script, output_file=artefacts_dir / "news_anchor.mp3")

    logger.info("All done! Audio available at %s", audio_path)


if __name__ == "__main__":
    main()
