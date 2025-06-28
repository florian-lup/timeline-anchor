# Timeline Anchor Latency Tests

This directory contains latency tests for the Timeline Anchor API to measure response times for each service in the pipeline.

## Test File

### `test_latency.py` - Real API Tests

- Tests against a running API instance
- Measures actual end-to-end latency
- Logs detailed timing information
- Creates latency_test.log file

**Run with:**

```bash
# Create a .env file in the project root with your variables:
# ANCHOR_SERVICE_URL=https://your-api-service.com
# ANCHOR_API_KEY=your-api-key
# OPENAI_API_KEY=your-openai-api-key
# MONGODB_URI=your-mongodb-uri

# Then run the test (it will automatically load from .env)
python tests/test_latency.py
```

## What Gets Measured

### Key Metrics:

1. **Time to Get Articles**: How long it takes to fetch articles from MongoDB
2. **Time to First Audio Chunk**: How long before audio streaming begins
3. **Total End-to-End Time**: Complete request processing time

### Logs

Integration tests create a `latency_test.log` file with detailed timing information.
