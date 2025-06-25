"from all the articles write a script suitable for a news anchor, max 2000 tokens"

from __future__ import annotations

"""Service for generating a news anchor script from article data."""

import json
from typing import List, Dict

from clients.openai import chat_completion
from config import settings

PROMPT_TEMPLATE = """
Using the list of news provided below, select the three most impactful stories (if more than three are provided) and craft a concise, engaging analytical commentary suitable for a text-to-speech engine to read aloud.

Open with a time-neutral greeting and a brief introduction to the news.

For each story, provide not just a summary, but also thoughtful analysis: discuss the context, possible causes and implications. Offer insights or perspectives that help the audience understand the significance of each story.

Use smooth, conversational transitions between stories so the narration flows naturally. Separate each story with a blank line for natural breathing pauses.

End with a sign-off that thanks the audience for listening and encourages them to reflect or stay informed.

IMPORTANT: Provide ONLY the words that should be spoken. Do NOT include numbers, bullet points, stage directions, sound-effect cues, speaker labels, or any text inside brackets, parentheses, asterisks, or markdown formatting.

Do NOT exceed {max_tokens} tokens.

News articles (JSON):
{articles}

Analytical Commentary:
"""


def create_anchor_script(articles: List[Dict[str, str]]) -> str:
    """Generate a news anchor script covering the provided articles."""

    if not articles:
        raise ValueError("No articles provided to generate script.")

    user_content = PROMPT_TEMPLATE.format(
        articles=json.dumps(articles, ensure_ascii=False, indent=2),
        max_tokens=settings.chat_max_tokens,
    )

    messages = [
        {"role": "system", "content": "You are an award-winning broadcast news script writer. Your job is to craft clear, engaging scripts in conversational broadcast style for a professional news anchor."},
        {"role": "user", "content": user_content},
    ]

    return chat_completion(messages)