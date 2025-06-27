# Timeline Anchor Latency Tests

This directory contains latency tests for the Timeline Anchor API to measure response times for each service in the pipeline.

## Test Files

### 1. `test_latency.py` - Unit/Mock Tests

- Tests individual service latencies using mocked dependencies
- Measures time for: article fetching, script generation, and audio streaming
- Includes concurrent request testing
- Fast execution, good for CI/CD

**Run with:**

```bash
pytest tests/test_latency.py -v -s
```

### 2. `test_latency_integration.py` - Real API Tests

- Tests against a running API instance
- Measures actual end-to-end latency
- Logs detailed timing information
- Creates latency_test.log file

**Run with:**

```bash
# Create a .env file in the project root with your variables:
# ANCHOR_SERVICE_URL=https://your-api-service.com
# ANCHOR_API_KEY=your-api-key

# Then run the test (it will automatically load from .env)
python tests/test_latency_integration.py
```

## What Gets Measured

### Key Metrics:

1. **Time to Get Articles**: How long it takes to fetch articles from MongoDB
2. **Script Generation Time**: How long OpenAI takes to generate the news script
3. **Time to First Audio Chunk**: How long before audio streaming begins
4. **Total End-to-End Time**: Complete request processing time

### Performance Benchmarks:

- **Excellent**: Time to First Byte < 5 seconds
- **Good**: Time to First Byte < 10 seconds
- **Acceptable**: Time to First Byte < 20 seconds
- **Needs Improvement**: Time to First Byte > 20 seconds

## Prerequisites

Install test dependencies:

```bash
pip install -r requirements.txt
```

## Running Your API for Integration Tests

1. Create a `.env` file in your project root:

```bash
# .env file contents
ANCHOR_SERVICE_URL=https://your-api-service.com
ANCHOR_API_KEY=your-secret-key
```

2. Run the integration tests:

```bash
python tests/test_latency_integration.py
```

## Sample Output

```
Testing API at: https://your-api-service.com
Using API key: your-key...

==================================================
TEST 1: Single Streaming Request Latency
==================================================
Testing endpoint: https://your-api-service.com/generate-anchor-stream
Time to first byte: 8.234s
Received 10 chunks, 15360 bytes
Request completed successfully

============================================================
TIMELINE ANCHOR API LATENCY REPORT
============================================================
Status: SUCCESS
Time to First Byte: 8.234s
Total Time: 12.456s
Chunks Received: 20
Total Bytes: 30,720
Average Chunk Time: 9.845s
Task ID: abc123def456
Performance: GOOD (TTFB < 10s)
============================================================
```

## Customizing Tests

### Adjusting Concurrent Load

Edit the `num_requests` parameter in the integration test:

```python
concurrent_result = await tester.test_multiple_concurrent_requests(num_requests=5)
```

### Changing Performance Thresholds

Modify the thresholds in `test_latency.py`:

```python
THRESHOLDS = {
    "fetch_articles": 2.0,      # 2 seconds for database query
    "generate_script": 15.0,    # 15 seconds for AI script generation
    "first_audio_chunk": 8.0,   # 8 seconds to start audio streaming
    "full_api_request": 25.0,   # 25 seconds total for end-to-end
}
```

### Testing Against Different Environments

Update your `.env` file with different service URLs:

```bash
# For staging environment
ANCHOR_SERVICE_URL=https://staging.yourapp.com
ANCHOR_API_KEY=your-staging-api-key

# For production environment
ANCHOR_SERVICE_URL=https://api.yourapp.com
ANCHOR_API_KEY=your-production-api-key
```

## Troubleshooting

### Common Issues:

1. **401 Unauthorized**: Check your ANCHOR_API_KEY environment variable
2. **Connection Refused**: Ensure your API server is running
3. **Timeout Errors**: API might be overloaded or services slow
4. **Import Errors**: Install missing dependencies with `pip install -r requirements.txt`

### Logs

Integration tests create a `latency_test.log` file with detailed timing information.
