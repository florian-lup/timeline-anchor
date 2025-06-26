# Timeline Anchor 🎙️

An AI-powered broadcasting system that fetches recent news articles, generates professional scripts, and converts them to speech.

- Fetches news articles from the last 24 hours stored in MongoDB
- Uses AI to analyze and craft engaging news scripts from multiple articles
- Generates professional-quality text-to-speech audio for broadcast.

## Features

### 🔍 **Intelligent News Aggregation**

- Automatically retrieves news articles from the last 24 hours
- Filters and processes article titles and summaries from MongoDB database
- Smart article selection for optimal news coverage

### 📝 **AI-Powered Script Generation**

- Uses OpenAI's GPT models to analyze and synthesize news content
- Selects the three most impactful stories from available articles
- Generates professional, broadcast-ready scripts with:
  - Engaging analytical commentary
  - Contextual analysis and implications
  - Smooth conversational transitions
  - Natural breathing pauses
  - Professional opening and closing segments

### 🎵 **High-Quality Text-to-Speech**

- Converts scripts to professional audio using OpenAI's TTS technology
- Customizable voice options (default: "alloy")
- Generates MP3 audio files ready for broadcast
- Optimized for natural speech patterns and pacing

### 🌐 **FastAPI HTTP API**

A lightweight `FastAPI` wrapper exposes the entire pipeline as a single HTTP endpoint so any front-end (web, mobile, etc.) can request fresh audio on demand.

| Method | Path               | Auth               | Response                    |
| ------ | ------------------ | ------------------ | --------------------------- |
| `POST` | `/generate-anchor` | `X-API-Key` header | Streamed `audio/mpeg` (MP3) |

1. **Call sequence**  
   `POST https://timeline-anchor/generate-anchor` with header `X-API-Key: <secret>`.  
   The backend:

   - pulls fresh articles from MongoDB,
   - asks GPT to craft the anchor script,
   - calls OpenAI TTS and streams the generated MP3 back to the client in real-time.

2. **Environment variables**:

   | Variable         | Purpose                                      |
   | ---------------- | -------------------------------------------- |
   | `OPENAI_API_KEY` | Access to OpenAI services                    |
   | `MONGODB_URI`    | Connection string for articles DB            |
   | `ANCHOR_API_KEY` | Shared secret required in `X-API-Key` header |

3. **Client example (Next.js / TS)**

   ```ts
   const res = await fetch("https://timeline-anchor/generate-anchor", {
     method: "POST",
     headers: { "X-API-Key": process.env.NEXT_PUBLIC_ANCHOR_API_KEY! },
   });
   const blob = await res.blob();
   const url = URL.createObjectURL(blob);
   new Audio(url).play();
   ```

## Technologies Used

### **Core Technologies**

- **Python 3.x** - Main programming language
- **MongoDB** - Database for storing and retrieving news articles
- **OpenAI API** - AI model integration for script generation and TTS

### **AI Models**

- **GPT-4.1-mini** - Default chat model for script generation (configurable)
- **TTS (Text-to-Speech)** - OpenAI's speech synthesis for audio generation
- **Voice: Alloy** - Default voice option (customizable)

### **Architecture**

- **Modular Design** - Separated services for news retrieval, script writing, and speech generation
- **Configuration Management** - Centralized settings with environment variable support
- **Client Abstraction** - Dedicated clients for MongoDB and OpenAI integrations

### 🚀 **Deploying (Docker container)**

The project ships with a ready-to-use `Dockerfile`. Any container-based PaaS (Runway, Render, Railway, Fly, etc.) can build it without code changes.

```bash
# build & run locally
export OPENAI_API_KEY=your_openai_api_key
export MONGODB_URI="your_mongodb_uri"
export ANCHOR_API_KEY=your_anchor_api_key

docker build -t timeline-anchor .
docker run -p 8080:8080 \
  -e OPENAI_API_KEY \
  -e MONGODB_URI \
  -e ANCHOR_API_KEY \
  timeline-anchor
```

On **Runway.com** simply:

1. Create a new **Docker** service.
2. Add the three environment variables above in the dashboard.
3. Ensure the service's **internal port** matches the `$PORT` env-var Runway sets (the Dockerfile command already uses `$PORT`).

The resulting endpoint will look like `https://<service-subdomain>.runway.com/generate-anchor`.
