"""
Integration latency test for Timeline Anchor API.

This test makes real API calls to measure actual latency without mocking.
Use this to test against a running instance of your API.

Run with: python tests/test_latency.py

Set these environment variables:
- ANCHOR_SERVICE_URL: Full URL of your running API service
- ANCHOR_API_KEY: Your API key for authentication
"""

import time
import asyncio
import logging
import os
import sys
from typing import Optional

import httpx
from dotenv import load_dotenv

# Add parent directory to Python path to find services
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import services directly for individual testing
from services.get_news import fetch_latest_script
from services.generate_speech import generate_anchor_audio_stream

# Configure logging (avoid emojis for Windows compatibility)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('latency_test.log', encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)


class APILatencyTester:
    """Test latency of the Timeline Anchor API."""
    
    def __init__(self, base_url: str, api_key: str):
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.results = {}
    
    async def test_streaming_endpoint_latency(self) -> dict:
        """Test the streaming endpoint and measure various latency metrics."""
        
        endpoint = f"{self.base_url}/generate-anchor-stream"
        headers = {"X-API-Key": self.api_key}
        
        logger.info(f"Testing endpoint: {endpoint}")
        
        async with httpx.AsyncClient(timeout=60.0) as client:
            try:
                # Start timing the request
                request_start = time.time()
                
                async with client.stream("POST", endpoint, headers=headers) as response:
                    # Check if request was successful
                    if response.status_code != 200:
                        logger.error(f"Request failed with status {response.status_code}: {response.text}")
                        return {"error": f"HTTP {response.status_code}"}
                    
                    # Measure time to first byte (TTFB)
                    first_byte_received = False
                    first_byte_time = None
                    total_bytes = 0
                    chunk_count = 0
                    chunk_times = []
                    
                    try:
                        async for chunk in response.aiter_bytes(chunk_size=1024):
                            current_time = time.time()
                            
                            if not first_byte_received:
                                first_byte_time = current_time - request_start
                                first_byte_received = True
                                logger.info(f"Time to first chunk streamed: {first_byte_time:.3f}s")
                                
                                # Record this first chunk and stop immediately
                                total_bytes = len(chunk)
                                chunk_count = 1
                                chunk_times.append(current_time - request_start)
                                
                                logger.info(f"First chunk received: {len(chunk)} bytes - stopping test")
                                break
                    except Exception as stream_error:
                        logger.error(f"Error during streaming: {stream_error}")
                        # If streaming failed but we got a response, use the time to response as TTFB
                        if first_byte_time is None:
                            first_byte_time = time.time() - request_start
                            logger.info(f"Using response time as TTFB: {first_byte_time:.3f}s")
                
                total_time = time.time() - request_start
                
                # Ensure we have a valid first_byte_time
                if first_byte_time is None:
                    first_byte_time = total_time
                    logger.warning(f"No chunks received, using total time as TTFB: {first_byte_time:.3f}s")
                
                # Calculate metrics
                results = {
                    "success": True,
                    "time_to_first_byte": first_byte_time,
                    "total_time": total_time,
                    "chunks_received": chunk_count,
                    "total_bytes": total_bytes,
                    "average_chunk_time": sum(chunk_times) / len(chunk_times) if chunk_times else first_byte_time,
                    "task_id": response.headers.get("X-Task-ID", "unknown")
                }
                
                logger.info("Request completed successfully")
                return results
                
            except httpx.TimeoutException:
                logger.error("Request timed out")
                return {"error": "timeout"}
            except Exception as e:
                logger.error(f"Request failed: {e}")
                return {"error": str(e)}
    
    async def test_multiple_concurrent_requests(self, num_requests: int = 3) -> dict:
        """Test latency under concurrent load."""
        
        logger.info(f"Testing {num_requests} concurrent requests")
        
        async def single_request(request_id: int):
            """Make a single request and return timing data."""
            endpoint = f"{self.base_url}/generate-anchor-stream"
            headers = {"X-API-Key": self.api_key}
            
            start_time = time.time()
            
            try:
                async with httpx.AsyncClient(timeout=60.0) as client:
                    async with client.stream("POST", endpoint, headers=headers) as response:
                        if response.status_code == 200:
                            # Read just the first chunk to measure streaming start time
                            async for chunk in response.aiter_bytes(chunk_size=1024):
                                ttfb = time.time() - start_time
                                logger.info(f"Request {request_id}: Time to first chunk = {ttfb:.3f}s")
                                return {
                                    "request_id": request_id,
                                    "success": True,
                                    "ttfb": ttfb,
                                    "task_id": response.headers.get("X-Task-ID")
                                }
                                # Break immediately after first chunk
                        else:
                            return {
                                "request_id": request_id,
                                "success": False,
                                "error": f"HTTP {response.status_code}"
                            }
            except Exception as e:
                return {
                    "request_id": request_id,
                    "success": False,
                    "error": str(e)
                }
        
        # Execute concurrent requests
        start_time = time.time()
        tasks = [single_request(i) for i in range(num_requests)]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        total_time = time.time() - start_time
        
        # Analyze results
        successful = [r for r in results if isinstance(r, dict) and r.get("success")]
        failed = [r for r in results if isinstance(r, dict) and not r.get("success")]
        
        if successful:
            ttfbs = [r["ttfb"] for r in successful]
            concurrent_results = {
                "total_requests": num_requests,
                "successful_requests": len(successful),
                "failed_requests": len(failed),
                "total_time": total_time,
                "average_ttfb": sum(ttfbs) / len(ttfbs),
                "min_ttfb": min(ttfbs),
                "max_ttfb": max(ttfbs),
                "results": results
            }
        else:
            concurrent_results = {
                "total_requests": num_requests,
                "successful_requests": 0,
                "failed_requests": len(failed),
                "total_time": total_time,
                "error": "No successful requests"
            }
        
        logger.info(f"Concurrent test completed: {len(successful)}/{num_requests} successful")
        return concurrent_results
    
    async def test_individual_services_latency(self) -> dict:
        """Test each service individually to measure their specific latencies."""
        
        logger.info("Testing individual services latency")
        service_timings = {}
        
        try:
            # Test 1: Script fetching from MongoDB
            logger.info("Step 1: Fetching latest script from database...")
            start_time = time.time()
            script = fetch_latest_script()
            fetch_time = time.time() - start_time
            service_timings["fetch_script"] = fetch_time
            logger.info(f"Script fetched in {fetch_time:.3f}s")
            
            if not script:
                return {"error": "No script found", "timings": service_timings}
            
            # Test 2: Time to first audio chunk (streaming start)
            logger.info("Step 2: Measuring time until audio streaming begins...")
            start_time = time.time()
            audio_stream = generate_anchor_audio_stream(script)
            
            # Get just the first chunk to measure streaming start time
            first_chunk = next(audio_stream)
            first_chunk_time = time.time() - start_time
            service_timings["first_audio_chunk"] = first_chunk_time
            logger.info(f"Audio streaming started: {len(first_chunk)} bytes in {first_chunk_time:.3f}s (stopping here)")
            
            # Calculate total time
            total_time = service_timings["fetch_script"] + service_timings["first_audio_chunk"]
            service_timings["total_sequential"] = total_time
            
            return {
                "success": True,
                "timings": service_timings,
                "script_length": len(script),
                "first_chunk_size": len(first_chunk)
            }
            
        except Exception as e:
            logger.error(f"Service test failed: {e}")
            return {"error": str(e), "timings": service_timings}
    
    def print_latency_report(self, results: dict):
        """Print a formatted latency report."""
        
        print("\n" + "="*60)
        print("TIMELINE ANCHOR API LATENCY REPORT")
        print("="*60)
        
        if results.get("success"):
            print(f"Status: SUCCESS")
            
            # Safely get values with defaults
            ttfb = results.get('time_to_first_byte', 0) or 0
            total_time = results.get('total_time', 0) or 0
            chunks = results.get('chunks_received', 0) or 0
            total_bytes = results.get('total_bytes', 0) or 0
            avg_chunk_time = results.get('average_chunk_time', 0) or 0
            task_id = results.get('task_id', 'unknown') or 'unknown'
            
            print(f"Time to First Chunk Streamed: {ttfb:.3f}s")
            print(f"Total Response Time: {total_time:.3f}s")
            print(f"First Chunk Size: {total_bytes:,} bytes")
            print(f"Task ID: {task_id}")
            
            # Performance assessment
            if ttfb < 5.0:
                print(f"Performance: EXCELLENT (< 5s to start streaming)")
            elif ttfb < 10.0:
                print(f"Performance: GOOD (< 10s to start streaming)")
            elif ttfb < 20.0:
                print(f"Performance: ACCEPTABLE (< 20s to start streaming)")
            else:
                print(f"Performance: NEEDS IMPROVEMENT (> 20s to start streaming)")
        else:
            print(f"Status: FAILED")
            print(f"Error: {results.get('error', 'Unknown error')}")
        
        print("="*60)
    
    def print_service_breakdown_report(self, results: dict):
        """Print a detailed breakdown of individual service latencies."""
        
        print("\n" + "="*60)
        print("SERVICE LATENCY BREAKDOWN")
        print("="*60)
        
        if results.get("success"):
            timings = results["timings"]
            
            print(f"Status: SUCCESS")
            print(f"Script Length: {results['script_length']} characters")
            print(f"First Chunk Size: {results['first_chunk_size']} bytes")
            print()
            print("Individual Service Timings:")
            print(f"1. Database Query (Script):  {timings['fetch_script']:.3f}s")
            print(f"2. Audio Streaming Start:      {timings['first_audio_chunk']:.3f}s")
            print(f"   Total Sequential Time:      {timings['total_sequential']:.3f}s")
            
            # Find the bottleneck
            service_times = {k: v for k, v in timings.items() if k != 'total_sequential'}
            slowest_service = max(service_times.items(), key=lambda x: x[1])
            print()
            print(f"Slowest Service: {slowest_service[0]} ({slowest_service[1]:.3f}s)")
            
            # Performance breakdown
            print()
            print("Performance Analysis:")
            for service, time_taken in service_times.items():
                percentage = (time_taken / timings['total_sequential']) * 100
                print(f"  {service}: {percentage:.1f}% of total time")
            
        else:
            print(f"Status: FAILED")
            print(f"Error: {results.get('error', 'Unknown error')}")
            if results.get("timings"):
                print("Partial timings collected:")
                for service, time_taken in results["timings"].items():
                    print(f"  {service}: {time_taken:.3f}s")
        
        print("="*60)


async def main():
    """Main function to run the latency tests."""
    
    # Load environment variables from .env file
    load_dotenv()
    
    # Get configuration from environment
    base_url = os.getenv("ANCHOR_SERVICE_URL")
    api_key = os.getenv("ANCHOR_API_KEY")
    
    if not base_url:
        logger.error("ERROR: ANCHOR_SERVICE_URL environment variable is required")
        logger.error("Please set it with: export ANCHOR_SERVICE_URL=\"https://your-api-service.com\"")
        sys.exit(1)
    
    if not api_key:
        logger.error("ERROR: ANCHOR_API_KEY environment variable is required")
        logger.error("Please set it with: export ANCHOR_API_KEY=\"your-api-key\"")
        sys.exit(1)
    
    logger.info(f"Testing API at: {base_url}")
    logger.info(f"Using API key: {api_key[:8]}...")
    
    tester = APILatencyTester(base_url, api_key)
    
    # Test 1: Single streaming request
    logger.info("\n" + "="*50)
    logger.info("TEST 1: Single Streaming Request Latency")
    logger.info("="*50)
    
    single_result = await tester.test_streaming_endpoint_latency()
    tester.print_latency_report(single_result)
    
    # Test 2: Concurrent requests
    logger.info("\n" + "="*50)
    logger.info("TEST 2: Concurrent Request Latency")
    logger.info("="*50)
    
    concurrent_result = await tester.test_multiple_concurrent_requests(num_requests=3)
    
    if concurrent_result.get("successful_requests", 0) > 0:
        print(f"\nCONCURRENT TEST RESULTS:")
        print(f"Successful: {concurrent_result['successful_requests']}/{concurrent_result['total_requests']}")
        print(f"Average Time to Stream: {concurrent_result['average_ttfb']:.3f}s")
        print(f"Fastest Time to Stream: {concurrent_result['min_ttfb']:.3f}s")
        print(f"Slowest Time to Stream: {concurrent_result['max_ttfb']:.3f}s")
        print(f"Total Test Time: {concurrent_result['total_time']:.3f}s")
    else:
        print(f"\nCONCURRENT TEST FAILED: {concurrent_result.get('error')}")
    
    # Test 3: Individual services breakdown
    logger.info("\n" + "="*50)
    logger.info("TEST 3: Individual Services Latency Breakdown")
    logger.info("="*50)
    
    services_result = await tester.test_individual_services_latency()
    tester.print_service_breakdown_report(services_result)
    
    logger.info("All tests completed!")


if __name__ == "__main__":
    asyncio.run(main()) 