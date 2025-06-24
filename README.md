# AI News Anchor

This project automatically turns the day's news articles from your MongoDB database into a spoken news bulletin.

## Features

1. **MongoDB integration** – Reads today's `title` and `summary` fields from the `events.articles` collection.
2. **Script writing** – Uses OpenAI GPT-4o-mini to craft a broadcast-ready script (≤ 2000 tokens).
3. **Text-to-speech** – Converts the script into speech with the **gpt-4o-mini-tts** model and saves an MP3.

## Project layout

```
clients/        # External service wrappers (MongoDB, OpenAI)
services/       # Domain logic (fetch news, write script, generate speech)
main.py         # End-to-end pipeline entrypoint
config.py       # Environment-driven configuration
```

## Quick start

1. Install dependencies (create a virtual environment first if desired):

```bash
pip install -r requirements.txt
```

2. Set the required environment variables:

```bash
export OPENAI_API_KEY="sk-…"
export MONGODB_URI="mongodb://localhost:27017"   # or your Atlas URI
```

Optional overrides:

```bash
export CHAT_MODEL="gpt-4o-mini"
export TTS_MODEL="gpt-4o-mini-tts"
export ANCHOR_VOICE="alloy"          # voice name supported by the TTS model
```

3. Run the pipeline:

```bash
python main.py
```

The script will be saved to `anchor_script.txt` and the audio to `news_anchor.mp3`.

## Notes

- The MongoDB documents are expected to contain a `date` field with timezone-aware UTC `datetime` values. Adjust the query in `clients/mongodb.py` if your schema differs.
- Token usage depends on article length; if you routinely exceed the 2000-token limit, filter or summarise input before calling the model.
