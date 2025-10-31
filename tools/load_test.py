#!/usr/bin/env python3
"""
Simple load testing script for the server farm
"""

import asyncio
import aiohttp
import time
from typing import List, Dict
import statistics


async def make_request(session: aiohttp.ClientSession, url: str) -> Dict:
    """Make a single request and measure response time"""
    start = time.time()
    try:
        async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as response:
            await response.text()
            duration = time.time() - start
            return {
                "success": True,
                "status": response.status,
                "duration": duration
            }
    except Exception as e:
        duration = time.time() - start
        return {
            "success": False,
            "error": str(e),
            "duration": duration
        }


async def load_test_server(server_id: int, num_requests: int, concurrency: int) -> Dict:
    """Run load test against a single server"""
    url = f"http://localhost:{8000 + server_id}/"
    
    print(f"🎯 Testing server-{server_id} ({url})")
    print(f"   Requests: {num_requests}, Concurrency: {concurrency}")
    
    async with aiohttp.ClientSession() as session:
        tasks = []
        for _ in range(num_requests):
            tasks.append(make_request(session, url))
        
        start_time = time.time()
        results = await asyncio.gather(*tasks)
        total_time = time.time() - start_time
    
    successful = [r for r in results if r["success"]]
    failed = [r for r in results if not r["success"]]
    
    durations = [r["duration"] for r in successful]
    
    return {
        "server_id": server_id,
        "total_requests": num_requests,
        "successful": len(successful),
        "failed": len(failed),
        "total_time": total_time,
        "requests_per_second": num_requests / total_time if total_time > 0 else 0,
        "avg_response_time": statistics.mean(durations) if durations else 0,
        "min_response_time": min(durations) if durations else 0,
        "max_response_time": max(durations) if durations else 0,
        "median_response_time": statistics.median(durations) if durations else 0,
    }


async def load_test_all(num_servers: int, requests_per_server: int, concurrency: int):
    """Run load test across all servers"""
    print(f"🚀 Starting load test across {num_servers} servers")
    print(f"   {requests_per_server} requests per server")
    print(f"   Concurrency: {concurrency}")
    print("=" * 60)
    print()
    
    tasks = []
    for i in range(1, num_servers + 1):
        tasks.append(load_test_server(i, requests_per_server, concurrency))
    
    results = await asyncio.gather(*tasks)
    
    print()
    print("=" * 60)
    print("📊 RESULTS")
    print("=" * 60)
    print()
    
    total_requests = sum(r["total_requests"] for r in results)
    total_successful = sum(r["successful"] for r in results)
    total_failed = sum(r["failed"] for r in results)
    avg_rps = statistics.mean([r["requests_per_second"] for r in results])
    
    print(f"Total Requests:     {total_requests:,}")
    print(f"Successful:         {total_successful:,} ({(total_successful/total_requests*100):.1f}%)")
    print(f"Failed:             {total_failed:,}")
    print(f"Avg RPS per server: {avg_rps:.2f}")
    print(f"Total RPS:          {(total_successful / results[0]['total_time']):.2f}")
    print()
    
    # Top 5 fastest servers
    print("⚡ Top 5 Fastest Servers:")
    sorted_by_speed = sorted(results, key=lambda x: x["avg_response_time"])
    for i, r in enumerate(sorted_by_speed[:5], 1):
        print(f"   {i}. Server-{r['server_id']}: {r['avg_response_time']*1000:.2f}ms avg")
    
    print()
    
    # Top 5 slowest servers
    print("🐌 Top 5 Slowest Servers:")
    for i, r in enumerate(reversed(sorted_by_speed[-5:]), 1):
        print(f"   {i}. Server-{r['server_id']}: {r['avg_response_time']*1000:.2f}ms avg")
    
    print()
    
    # Servers with failures
    failed_servers = [r for r in results if r["failed"] > 0]
    if failed_servers:
        print(f"⚠️  {len(failed_servers)} servers had failures:")
        for r in failed_servers:
            print(f"   Server-{r['server_id']}: {r['failed']} failed")
    else:
        print("✅ All servers responded successfully!")
    
    print()


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Load test the server farm")
    parser.add_argument("--servers", type=int, default=50, help="Number of servers to test")
    parser.add_argument("--requests", type=int, default=100, help="Requests per server")
    parser.add_argument("--concurrency", type=int, default=10, help="Concurrent requests")
    
    args = parser.parse_args()
    
    asyncio.run(load_test_all(args.servers, args.requests, args.concurrency))


if __name__ == "__main__":
    main()
