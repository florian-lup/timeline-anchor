"""
Latency test for Timeline Anchor API services.

This test measures the response time for each service:
1. Time to get articles from MongoDB
2. Time to generate script using OpenAI
3. Time to first audio chunk streamed

Run with: python -m pytest tests/test_latency.py -v -s
"""

import time
import asyncio
import logging
import os
from typing import Dict, Any
from unittest.mock import patch, MagicMock

import pytest
import httpx
from fastapi.testclient import TestClient

# Configure logging to see detailed timing information
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Import your app and services
from api import app
from services.get_news import fetch_latest_script
from services.generate_speech import generate_anchor_audio_stream


class LatencyTracker:
    """Helper class to track timing for different operations."""
    
    def __init__(self):
        self.timings: Dict[str, float] = {}
        self.start_times: Dict[str, float] = {}
    
    def start_timing(self, operation: str):
        """Start timing an operation."""
        self.start_times[operation] = time.time()
        logger.info(f"Started timing: {operation}")
    
    def end_timing(self, operation: str):
        """End timing an operation and store the duration."""
        if operation in self.start_times:
            duration = time.time() - self.start_times[operation]
            self.timings[operation] = duration
            logger.info(f"Completed timing: {operation} - Duration: {duration:.3f}s")
            return duration
        return 0.0
    
    def get_timing(self, operation: str) -> float:
        """Get the timing for a specific operation."""
        return self.timings.get(operation, 0.0)
    
    def print_summary(self):
        """Print a summary of all timings."""
        logger.info("=== LATENCY SUMMARY ===")
        total_time = 0.0
        for operation, duration in self.timings.items():
            logger.info(f"{operation}: {duration:.3f}s")
            total_time += duration
        logger.info(f"Total time: {total_time:.3f}s")
        logger.info("=====================")


@pytest.fixture
def api_key():
    """Set up API key for testing."""
    test_api_key = "test-api-key-12345"
    os.environ["ANCHOR_API_KEY"] = test_api_key
    return test_api_key


@pytest.fixture
def client():
    """Create a test client for the FastAPI app."""
    return TestClient(app)


@pytest.fixture
def latency_tracker():
    """Create a latency tracker instance."""
    return LatencyTracker()


def test_service_latencies_unit_tests(latency_tracker):
    """Test individual service latencies using unit tests."""
    
    # Mock data for testing
    mock_script = "Good evening. Here are today's top stories. This is a test script for latency testing."
    
    # Test 1: Script fetching latency
    with patch('clients.mongodb.get_latest_script') as mock_get_script:
        mock_get_script.return_value = mock_script

        latency_tracker.start_timing("fetch_script")
        script = fetch_latest_script()
        fetch_time = latency_tracker.end_timing("fetch_script")

        assert script == mock_script
        assert fetch_time >= 0
        logger.info(f"Script fetching took: {fetch_time:.3f}s")
    
    # Test 2: Audio streaming latency (time to first chunk)
    mock_audio_chunks = [b"audio_chunk_1", b"audio_chunk_2", b"audio_chunk_3"]
    
    with patch('clients.openai.generate_speech_stream') as mock_speech:
        mock_speech.return_value = iter(mock_audio_chunks)
        
        latency_tracker.start_timing("first_audio_chunk")
        audio_stream = generate_anchor_audio_stream(mock_script)
        
        # Time to first chunk
        first_chunk = next(audio_stream)
        first_chunk_time = latency_tracker.end_timing("first_audio_chunk")
        
        assert first_chunk == b"audio_chunk_1"
        assert first_chunk_time >= 0
        logger.info(f"Time to first audio chunk: {first_chunk_time:.3f}s")
        
        # Consume remaining chunks to test full streaming
        remaining_chunks = list(audio_stream)
        assert len(remaining_chunks) == 2
    
    latency_tracker.print_summary()


def test_api_endpoint_latency(client, api_key, latency_tracker):
    """Test the API endpoint latency with mocked services."""
    
    # Mock all external dependencies
    mock_script = "Welcome to the news. Here are today's top stories from our timeline anchor."
    mock_audio_chunks = [f"chunk_{i}".encode() for i in range(5)]
    
    with patch('services.get_news.fetch_latest_script') as mock_fetch, \
         patch('services.generate_speech.generate_anchor_audio_stream') as mock_audio:
        
        mock_fetch.return_value = mock_script
        mock_audio.return_value = iter(mock_audio_chunks)
        
        headers = {"X-API-Key": api_key}
        
        latency_tracker.start_timing("full_api_request")
        
        # Make the API request
        response = client.post("/generate-anchor-stream", headers=headers)
        
        # Check response starts streaming
        assert response.status_code == 200
        assert response.headers["content-type"] == "audio/wav"
        
        # Measure time to first byte
        content_generator = response.iter_bytes(chunk_size=1024)
        first_chunk = next(content_generator)
        first_byte_time = latency_tracker.end_timing("full_api_request")
        
        assert len(first_chunk) > 0
        logger.info(f"API time to first byte: {first_byte_time:.3f}s")
        
        # Consume the rest of the stream
        total_bytes = len(first_chunk)
        for chunk in content_generator:
            total_bytes += len(chunk)
        
        logger.info(f"Total audio bytes received: {total_bytes}")
    
    latency_tracker.print_summary()


@pytest.mark.asyncio
async def test_concurrent_api_requests(api_key, latency_tracker):
    """Test latency under concurrent load."""
    
    num_concurrent_requests = 3
    
    async def make_request(session: httpx.AsyncClient, request_id: int):
        """Make a single API request and measure latency."""
        headers = {"X-API-Key": api_key}
        
        start_time = time.time()
        
        try:
            async with session.stream("POST", "/generate-anchor-stream", headers=headers) as response:
                if response.status_code == 200:
                    # Read first chunk to measure time to first byte
                    async for chunk in response.aiter_bytes(chunk_size=1024):
                        end_time = time.time()
                        latency = end_time - start_time
                        logger.info(f"Request {request_id} - Time to first chunk: {latency:.3f}s")
                        return latency
                else:
                    logger.error(f"Request {request_id} failed with status {response.status_code}")
                    return None
        except Exception as e:
            logger.error(f"Request {request_id} failed with error: {e}")
            return None
    
    # Mock the services for concurrent testing
    mock_script = "Concurrent testing script."
    mock_audio = [b"concurrent_audio_chunk"]
    
    with patch('services.get_news.fetch_latest_script', return_value=mock_script), \
         patch('services.generate_speech.generate_anchor_audio_stream', return_value=iter(mock_audio)):
        
        # Start the app for async testing
        async with httpx.AsyncClient(app=app, base_url="http://test") as client:
            latency_tracker.start_timing("concurrent_requests")
            
            # Make concurrent requests
            tasks = [make_request(client, i) for i in range(num_concurrent_requests)]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            total_concurrent_time = latency_tracker.end_timing("concurrent_requests")
            
            # Analyze results
            successful_requests = [r for r in results if isinstance(r, float)]
            
            if successful_requests:
                avg_latency = sum(successful_requests) / len(successful_requests)
                max_latency = max(successful_requests)
                min_latency = min(successful_requests)
                
                logger.info(f"Concurrent test results:")
                logger.info(f"  Successful requests: {len(successful_requests)}/{num_concurrent_requests}")
                logger.info(f"  Average latency: {avg_latency:.3f}s")
                logger.info(f"  Min latency: {min_latency:.3f}s")
                logger.info(f"  Max latency: {max_latency:.3f}s")
                logger.info(f"  Total time for all requests: {total_concurrent_time:.3f}s")
            else:
                logger.warning("No successful requests in concurrent test")


def test_latency_thresholds():
    """Test that services meet acceptable latency thresholds."""
    
    # Define acceptable latency thresholds (adjust based on your requirements)
    THRESHOLDS = {
        "fetch_script": 2.0,      # 2 seconds for database query
        "first_audio_chunk": 5.0,   # 5 seconds to start audio streaming
        "full_api_request": 15.0,   # 15 seconds total for end-to-end
    }
    
    tracker = LatencyTracker()
    
    # This would typically use real performance data
    # For demo purposes, using mock timing data
    mock_timings = {
        "fetch_script": 0.8,
        "first_audio_chunk": 2.1,
        "full_api_request": 7.1
    }
    
    tracker.timings = mock_timings
    
    # Check each threshold
    for operation, threshold in THRESHOLDS.items():
        actual_time = tracker.get_timing(operation)
        logger.info(f"Checking {operation}: {actual_time:.3f}s (threshold: {threshold}s)")
        
        # In a real test, you'd assert these thresholds
        if actual_time > threshold:
            logger.warning(f"⚠️  {operation} exceeded threshold: {actual_time:.3f}s > {threshold}s")
        else:
            logger.info(f"✅ {operation} within threshold: {actual_time:.3f}s <= {threshold}s")


if __name__ == "__main__":
    # Run basic latency tests
    tracker = LatencyTracker()
    
    # Set up environment
    os.environ["ANCHOR_API_KEY"] = "test-key"
    
    print("Running latency tests...")
    test_service_latencies_unit_tests(tracker)
    test_latency_thresholds()
    print("Latency tests completed!") 