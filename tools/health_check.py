#!/usr/bin/env python3
"""
Health check script - verify all servers are responding
"""

import asyncio
import aiohttp
import sys
from datetime import datetime


async def check_server(session: aiohttp.ClientSession, server_id: int) -> dict:
    """Check health of a single server"""
    url = f"http://localhost:{8000 + server_id}/health"
    
    try:
        async with session.get(url, timeout=aiohttp.ClientTimeout(total=5)) as response:
            if response.status == 200:
                data = await response.json()
                return {
                    "server_id": server_id,
                    "status": "healthy",
                    "health_status": data.get("status"),
                    "response_code": response.status
                }
            else:
                return {
                    "server_id": server_id,
                    "status": "unhealthy",
                    "response_code": response.status
                }
    except asyncio.TimeoutError:
        return {
            "server_id": server_id,
            "status": "timeout",
            "error": "Request timed out"
        }
    except Exception as e:
        return {
            "server_id": server_id,
            "status": "error",
            "error": str(e)
        }


async def check_all_servers(num_servers: int = 50):
    """Check health of all servers"""
    print(f"🏥 Health Check - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"   Checking {num_servers} servers...")
    print("=" * 60)
    
    async with aiohttp.ClientSession() as session:
        tasks = [check_server(session, i) for i in range(1, num_servers + 1)]
        results = await asyncio.gather(*tasks)
    
    healthy = [r for r in results if r["status"] == "healthy"]
    unhealthy = [r for r in results if r["status"] != "healthy"]
    
    print()
    print("✅ Healthy servers:")
    for r in healthy:
        print(f"   Server-{r['server_id']}: {r['health_status']} (HTTP {r['response_code']})")
    
    if unhealthy:
        print()
        print("❌ Unhealthy servers:")
        for r in unhealthy:
            error_msg = r.get('error', f"HTTP {r.get('response_code', 'N/A')}")
            print(f"   Server-{r['server_id']}: {r['status']} - {error_msg}")
    
    print()
    print("=" * 60)
    print(f"Summary: {len(healthy)}/{num_servers} healthy ({len(healthy)/num_servers*100:.1f}%)")
    print("=" * 60)
    
    return len(unhealthy) == 0


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Health check all servers")
    parser.add_argument("--servers", type=int, default=50, help="Number of servers")
    
    args = parser.parse_args()
    
    all_healthy = asyncio.run(check_all_servers(args.servers))
    
    sys.exit(0 if all_healthy else 1)


if __name__ == "__main__":
    main()
