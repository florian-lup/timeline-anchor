"from all the articles write a script suitable for a news anchor, max 2000 tokens"

from __future__ import annotations

"""Service for generating a news anchor script from article data."""

import json
from typing import List, Dict

from clients.openai import chat_completion
from config import settings

PROMPT_TEMPLATE = (
    "You are a professional news anchor. Using the list of news articles provided "
    "below, select the five most impactful stories (if more than five are provided) and craft a concise, engaging script that can be read aloud verbatim. "
    "Open with a brief, time-neutral greeting such as 'Hello' or 'Good day.' "
    "Use smooth, conversational transitions between stories so the narration flows naturally. "
    "IMPORTANT: The script will be passed directly to a text-to-speech engine. "
    "Therefore, provide ONLY the words that should be spoken. "
    "Do NOT include stage directions, sound-effect cues, speaker labels, or any text "
    "inside brackets, parentheses, or asterisks. Do NOT wrap the script in Markdown. "
    "Separate each story with a blank line for natural breathing pauses. "
    "End with a concise sign-off that thanks the audience for listening. "
    "Do NOT exceed {max_tokens} tokens.\n\n"
    "News articles (JSON):\n{articles}\n\n"
    "Script:\n"
)


def create_anchor_script(articles: List[Dict[str, str]]) -> str:
    """Generate a news anchor script covering the provided articles."""

    if not articles:
        raise ValueError("No articles provided to generate script.")

    user_content = PROMPT_TEMPLATE.format(
        articles=json.dumps(articles, ensure_ascii=False, indent=2),
        max_tokens=settings.chat_max_tokens,
    )

    messages = [
        {"role": "system", "content": "You are an award-winning broadcast news script writer. Your job is to craft clear, engaging scripts in conversational broadcast style for a professional news anchor. Maintain a neutral, objective tone and avoid editorializing. Provide ONLY the words to be spoken—no headings, labels, stage directions, or formatting."},
        {"role": "user", "content": user_content},
    ]

    return chat_completion(messages)