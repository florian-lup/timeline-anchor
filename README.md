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
