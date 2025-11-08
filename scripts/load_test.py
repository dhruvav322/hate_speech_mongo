#!/usr/bin/env python3
"""
Load testing script to verify industry-ready performance.
Tests concurrent requests, response times, and error handling.
"""

import asyncio
import aiohttp
import time
import statistics
from typing import List, Dict
import os

# Configuration
BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")
API_KEY = os.getenv("API_KEY", "test-api-key-123")
NUM_REQUESTS = 100
CONCURRENT_WORKERS = 10

async def analyze_message(session: aiohttp.ClientSession, text: str, request_id: int) -> Dict:
    """Single message analysis request."""
    start_time = time.time()

    try:
        async with session.post(
            f"{BASE_URL}/api/v1/moderation/analyze",
            json={"text": text, "user_id": f"load_test_user_{request_id}"},
            headers={"X-API-Key": API_KEY},
            timeout=aiohttp.ClientTimeout(total=30)
        ) as response:
            response_time = time.time() - start_time

            if response.status == 200:
                data = await response.json()
                return {
                    "request_id": request_id,
                    "status": "success",
                    "response_time": response_time,
                    "message_id": data.get("message_id"),
                    "action": data.get("moderation_action", {}).get("recommended_action")
                }
            else:
                return {
                    "request_id": request_id,
                    "status": "error",
                    "response_time": response_time,
                    "error": f"HTTP {response.status}",
                    "error_detail": await response.text()
                }

    except asyncio.TimeoutError:
        return {
            "request_id": request_id,
            "status": "timeout",
            "response_time": 30.0,
            "error": "Request timeout"
        }
    except Exception as e:
        return {
            "request_id": request_id,
            "status": "error",
            "response_time": time.time() - start_time,
            "error": str(e)
        }

async def run_load_test():
    """Execute load test with concurrent requests."""
    print(f"🚀 Starting load test: {NUM_REQUESTS} requests, {CONCURRENT_WORKERS} workers")
    print(f"🌐 Target: {BASE_URL}")
    print()

    # Test messages with varying complexity
    test_messages = [
        "Hello world!",
        "This is a moderate message with some content",
        "I think this is quite long and might trigger more complex analysis with multiple sentences and different sentiments that need to be processed carefully",
        "You are stupid and ugly",  # Should trigger moderation
        "Have a wonderful day full of joy and happiness!",
        "This message contains potentially problematic content that should be flagged",
        "Simple short text",
        "Another moderate length message for testing purposes"
    ]

    # Create semaphore to limit concurrent requests
    semaphore = asyncio.Semaphore(CONCURRENT_WORKERS)

    async def bounded_analyze(session, text, request_id):
        async with semaphore:
            return await analyze_message(session, text, request_id)

    start_time = time.time()

    # Run requests concurrently
    connector = aiohttp.TCPConnector(limit=CONCURRENT_WORKERS * 2)
    async with aiohttp.ClientSession(connector=connector) as session:
        tasks = []
        for i in range(NUM_REQUESTS):
            message = test_messages[i % len(test_messages)]
            task = bounded_analyze(session, message, i)
            tasks.append(task)

        results = await asyncio.gather(*tasks, return_exceptions=True)

    total_time = time.time() - start_time

    # Analyze results
    successful_requests = [r for r in results if isinstance(r, dict) and r.get("status") == "success"]
    failed_requests = [r for r in results if isinstance(r, dict) and r.get("status") != "success"]

    response_times = [r["response_time"] for r in successful_requests]

    # Industry-ready benchmarks
    print("📊 Load Test Results")
    print("=" * 50)
    print(f"Total requests: {NUM_REQUESTS}")
    print(f"Successful: {len(successful_requests)} ({len(successful_requests)/NUM_REQUESTS*100:.1f}%)")
    print(f"Failed: {len(failed_requests)} ({len(failed_requests)/NUM_REQUESTS*100:.1f}%)")
    print(f"Total time: {total_time:.2f}s")
    print(f"Requests per second: {NUM_REQUESTS/total_time:.2f}")
    print()

    if response_times:
        print("⏱️  Response Time Analysis")
        print("-" * 30)
        print(f"Average: {statistics.mean(response_times)*1000:.0f}ms")
        print(f"Median: {statistics.median(response_times)*1000:.0f}ms")
        print(f"Min: {min(response_times)*1000:.0f}ms")
        print(f"Max: {max(response_times)*1000:.0f}ms")
        print(f"95th percentile: {sorted(response_times)[int(len(response_times)*0.95)]*1000:.0f}ms")
        print()

    # Industry-ready validation
    print("🏆 Industry-Ready Validation")
    print("-" * 30)

    # Success rate check (should be > 99%)
    success_rate = len(successful_requests) / NUM_REQUESTS
    if success_rate >= 0.99:
        print(f"✅ Success rate: {success_rate*100:.1f}% (Excellent)")
    elif success_rate >= 0.95:
        print(f"⚠️  Success rate: {success_rate*100:.1f}% (Good)")
    else:
        print(f"❌ Success rate: {success_rate*100:.1f}% (Needs improvement)")

    # Response time check (should be < 1000ms average)
    if response_times:
        avg_response_time = statistics.mean(response_times) * 1000
        if avg_response_time <= 500:
            print(f"✅ Avg response time: {avg_response_time:.0f}ms (Excellent)")
        elif avg_response_time <= 1000:
            print(f"⚠️  Avg response time: {avg_response_time:.0f}ms (Good)")
        else:
            print(f"❌ Avg response time: {avg_response_time:.0f}ms (Needs optimization)")

    # Throughput check (should handle > 10 req/s)
    throughput = NUM_REQUESTS / total_time
    if throughput >= 50:
        print(f"✅ Throughput: {throughput:.1f} req/s (Excellent)")
    elif throughput >= 20:
        print(f"⚠️  Throughput: {throughput:.1f} req/s (Good)")
    else:
        print(f"❌ Throughput: {throughput:.1f} req/s (Needs optimization)")

    # Error analysis
    if failed_requests:
        print(f"\n❌ Error Analysis:")
        error_types = {}
        for req in failed_requests:
            error = req.get("error", "Unknown")
            error_types[error] = error_types.get(error, 0) + 1

        for error, count in error_types.items():
            print(f"  • {error}: {count} occurrences")

    print("\n🎯 Recommendations:")
    if success_rate < 0.99:
        print("  • Investigate failed requests and improve error handling")
    if response_times and statistics.mean(response_times) > 1.0:
        print("  • Optimize ML model inference or add more workers")
    if throughput < 20:
        print("  • Increase worker count or optimize performance")

    return {
        "success_rate": success_rate,
        "avg_response_time": statistics.mean(response_times) * 1000 if response_times else 0,
        "throughput": throughput,
        "total_requests": NUM_REQUESTS,
        "successful_requests": len(successful_requests)
    }

if __name__ == "__main__":
    print("🔬 Industry-Ready Load Testing")
    print("=" * 50)
    print("⚠️  Make sure your API is running and API_KEY is set")
    print()

    asyncio.run(run_load_test())