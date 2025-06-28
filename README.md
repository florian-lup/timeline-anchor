# Timeline Anchor 🎙️

An AI-powered broadcasting system that fetches recent news articles and converts them to speech

## Features

### 🔍 **News Aggregation**

- Fetches the most recent news articles stored in MongoDB

### 🎵 **Text-to-Speech**

- Generates professional-quality audio using OpenAI's TTS

### ⚡ **Low Latency**

- Streams audio as it's generated, minimizing wait time for end users

### 🌐 **FastAPI HTTP API**

A lightweight `FastAPI` wrapper exposes the entire pipeline as a single HTTP endpoint so any front-end (web, mobile, etc.) can request fresh audio on demand.

| Method | Path                      | Auth               | Response                 |
| ------ | --------------------------| ------------------ | ------------------------ |
| `POST` | `/generate-anchor-stream` | `X-API-Key` header | Streamed `audio/wav`     |

1. **Call sequence**  
   `POST ANCHOR_SERVICE_URL/generate-anchor-stream` with header `X-API-Key: <secret>`.  
   The backend:

   - pulls fresh articles from MongoDB,
   - calls OpenAI TTS and streams the generated audio back to the client in real-time.

2. **Environment variables**:

   | Variable              | Purpose                                      |
   | --------------------- | -------------------------------------------- |
   | `OPENAI_API_KEY`      | Access to OpenAI services                    |
   | `MONGODB_URI`         | Connection string for articles DB            |
   | `ANCHOR_API_KEY`      | Shared secret required in `X-API-Key` header |
   | `ANCHOR_SERVICE_URL`  | The URL of the anchor service                |

## Technologies Used

### **Core Technologies**

- **MongoDB** - Database for storing and retrieving news articles
- **OpenAI API** - AI model integration for text-to-speech generation
- **FastAPI** - HTTP API for the anchor service
