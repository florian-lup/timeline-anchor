"from all the articles write a script suitable for a news anchor, max 2000 tokens"

from __future__ import annotations

"""Service for generating a news anchor script from article data."""

import json
from typing import List, Dict

from clients.openai import chat_completion

PROMPT_TEMPLATE = (
    "You are a professional news anchor. Using the list of news articles provided "
    "below, craft a concise script that you will read on air. The script should "
    "be engaging, clear, and flow naturally from one story to the next. "
    "Aim for a balanced tone—informative yet conversational. "
    "Do NOT exceed 2000 tokens.\n\n"
    "News articles (JSON):\n{articles}\n\n"
    "Script:" 
)


def create_anchor_script(articles: List[Dict[str, str]]) -> str:
    """Generate a news anchor script covering the provided articles."""

    if not articles:
        raise ValueError("No articles provided to generate script.")

    user_content = PROMPT_TEMPLATE.format(articles=json.dumps(articles, ensure_ascii=False, indent=2))

    messages = [
        {"role": "system", "content": "You are ChatGPT, an AI that writes professional news anchor scripts."},
        {"role": "user", "content": user_content},
    ]

    return chat_completion(messages, max_tokens=2000)