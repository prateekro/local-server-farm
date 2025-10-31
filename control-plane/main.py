from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import docker
import asyncio
import aiohttp
import uvicorn
from datetime import datetime
import statistics

app = FastAPI(
    title="Server Farm Control Plane",
    description="Centralized control and monitoring for 50 server instances",
    version="1.0.0"
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Docker client - initialize with better error handling
try:
    docker_client = docker.DockerClient(base_url='unix://var/run/docker.sock')
    docker_client.ping()
    print("✅ Connected to Docker daemon")
except Exception as e:
    print(f"⚠️  Warning: Could not connect to Docker daemon: {e}")
    print("   Docker container management features will be limited.")
    docker_client = None

# Configuration
BASE_PORT = 8001
NUM_SERVERS = 50


# Pydantic models
class LoadTestRequest(BaseModel):
    target_servers: Optional[List[int]] = None
    requests: int = 1000
    concurrency: int = 10
    duration: Optional[int] = None


class SimulateLoadRequest(BaseModel):
    server_ids: List[int]
    cpu_duration: float = 2.0
    memory_mb: int = 100


class ServerAction(BaseModel):
    action: str  # start, stop, restart


# Helper functions
def get_server_url(server_id: int) -> str:
    """Get the URL for a specific server"""
    port = BASE_PORT + server_id - 1
    return f"http://localhost:{port}"


def get_container_name(server_id: int) -> str:
    """Get container name for a server ID"""
    return f"server-{server_id}"


async def fetch_url(session: aiohttp.ClientSession, url: str, timeout: int = 5) -> Dict[str, Any]:
    """Fetch URL with timeout and error handling"""
    try:
        async with session.get(url, timeout=aiohttp.ClientTimeout(total=timeout)) as response:
            if response.status == 200:
                return await response.json()
            else:
                return {"error": f"HTTP {response.status}"}
    except asyncio.TimeoutError:
        return {"error": "timeout"}
    except Exception as e:
        return {"error": str(e)}


# API Endpoints
@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "name": "Server Farm Control Plane",
        "version": "1.0.0",
        "servers_managed": NUM_SERVERS,
        "base_port": BASE_PORT,
        "endpoints": {
            "servers": "/api/servers",
            "health": "/api/health",
            "metrics": "/api/metrics",
            "docs": "/docs"
        }
    }


@app.get("/api/servers")
async def list_servers():
    """List all server instances with their status"""
    servers = []
    
    # If Docker is not available, check servers via HTTP only
    if docker_client is None:
        async with aiohttp.ClientSession() as session:
            for i in range(1, NUM_SERVERS + 1):
                url = get_server_url(i)
                try:
                    health = await fetch_url(session, f"{url}/health", timeout=2)
                    if "error" not in health:
                        servers.append({
                            "id": i,
                            "name": get_container_name(i),
                            "status": "running",
                            "url": url,
                            "port": BASE_PORT + i - 1,
                        })
                    else:
                        servers.append({
                            "id": i,
                            "name": get_container_name(i),
                            "status": "unreachable",
                            "url": url,
                            "port": BASE_PORT + i - 1,
                            "error": health.get("error")
                        })
                except Exception as e:
                    servers.append({
                        "id": i,
                        "name": get_container_name(i),
                        "status": "error",
                        "url": url,
                        "port": BASE_PORT + i - 1,
                        "error": str(e)
                    })
    else:
        # Use Docker API for detailed stats
        for i in range(1, NUM_SERVERS + 1):
            container_name = get_container_name(i)
            try:
                container = docker_client.containers.get(container_name)
                status = container.status
                stats = container.stats(stream=False)
                
                # Calculate CPU percentage
                cpu_delta = stats['cpu_stats']['cpu_usage']['total_usage'] - \
                           stats['precpu_stats']['cpu_usage']['total_usage']
                system_delta = stats['cpu_stats']['system_cpu_usage'] - \
                              stats['precpu_stats']['system_cpu_usage']
                cpu_percent = (cpu_delta / system_delta) * 100.0 if system_delta > 0 else 0.0
                
                # Calculate memory usage
                memory_usage = stats['memory_stats'].get('usage', 0)
                memory_limit = stats['memory_stats'].get('limit', 1)
                memory_percent = (memory_usage / memory_limit) * 100.0
                
                servers.append({
                    "id": i,
                    "name": container_name,
                    "status": status,
                    "url": get_server_url(i),
                    "port": BASE_PORT + i - 1,
                    "cpu_percent": round(cpu_percent, 2),
                    "memory_mb": round(memory_usage / (1024 * 1024), 2),
                    "memory_percent": round(memory_percent, 2)
                })
            except docker.errors.NotFound:
                servers.append({
                    "id": i,
                    "name": container_name,
                    "status": "not_found",
                    "url": get_server_url(i),
                    "port": BASE_PORT + i - 1,
                    "error": "Container not found"
                })
            except Exception as e:
                servers.append({
                    "id": i,
                    "name": container_name,
                    "status": "error",
                    "url": get_server_url(i),
                    "port": BASE_PORT + i - 1,
                    "error": str(e)
                })
    
    return {
        "total_servers": NUM_SERVERS,
        "servers": servers,
        "timestamp": datetime.now().isoformat()
    }


@app.get("/api/servers/{server_id}")
async def get_server(server_id: int):
    """Get detailed information about a specific server"""
    if server_id < 1 or server_id > NUM_SERVERS:
        raise HTTPException(status_code=404, detail="Server not found")
    
    container_name = get_container_name(server_id)
    url = get_server_url(server_id)
    
    # Get metrics from the server itself
    async with aiohttp.ClientSession() as session:
        metrics = await fetch_url(session, f"{url}/metrics")
    
    if docker_client is None:
        # Without Docker, just return HTTP metrics
        return {
            "server_id": server_id,
            "container_name": container_name,
            "status": "running" if "error" not in metrics else "error",
            "url": url,
            "port": BASE_PORT + server_id - 1,
            "metrics": metrics,
            "timestamp": datetime.now().isoformat()
        }
    
    try:
        container = docker_client.containers.get(container_name)
        
        return {
            "server_id": server_id,
            "container_name": container_name,
            "status": container.status,
            "url": url,
            "port": BASE_PORT + server_id - 1,
            "metrics": metrics,
            "timestamp": datetime.now().isoformat()
        }
    except docker.errors.NotFound:
        raise HTTPException(status_code=404, detail="Container not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/servers/{server_id}/action")
async def server_action(server_id: int, action: ServerAction):
    """Perform an action on a specific server (start, stop, restart)"""
    if server_id < 1 or server_id > NUM_SERVERS:
        raise HTTPException(status_code=404, detail="Server not found")
    
    if docker_client is None:
        raise HTTPException(
            status_code=503, 
            detail="Docker client not available. Use 'docker-compose' commands directly."
        )
    
    container_name = get_container_name(server_id)
    
    try:
        container = docker_client.containers.get(container_name)
        
        if action.action == "start":
            container.start()
        elif action.action == "stop":
            container.stop()
        elif action.action == "restart":
            container.restart()
        else:
            raise HTTPException(status_code=400, detail="Invalid action")
        
        return {
            "server_id": server_id,
            "action": action.action,
            "status": "success",
            "timestamp": datetime.now().isoformat()
        }
    except docker.errors.NotFound:
        raise HTTPException(status_code=404, detail="Container not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/health")
async def health_check_all():
    """Check health status of all servers"""
    async with aiohttp.ClientSession() as session:
        tasks = []
        for i in range(1, NUM_SERVERS + 1):
            url = f"{get_server_url(i)}/health"
            tasks.append(fetch_url(session, url))
        
        results = await asyncio.gather(*tasks)
    
    healthy_count = sum(1 for r in results if r.get("status") == "healthy")
    degraded_count = sum(1 for r in results if r.get("status") == "degraded")
    unhealthy_count = sum(1 for r in results if "error" in r)
    
    health_data = []
    for i, result in enumerate(results, 1):
        health_data.append({
            "server_id": i,
            "status": result.get("status", "error"),
            "error": result.get("error")
        })
    
    return {
        "total_servers": NUM_SERVERS,
        "healthy": healthy_count,
        "degraded": degraded_count,
        "unhealthy": unhealthy_count,
        "servers": health_data,
        "timestamp": datetime.now().isoformat()
    }


@app.get("/api/metrics")
async def get_all_metrics():
    """Get aggregated metrics from all servers"""
    async with aiohttp.ClientSession() as session:
        tasks = []
        for i in range(1, NUM_SERVERS + 1):
            url = f"{get_server_url(i)}/metrics"
            tasks.append(fetch_url(session, url, timeout=10))
        
        results = await asyncio.gather(*tasks)
    
    # Filter successful results
    valid_metrics = [r for r in results if "error" not in r]
    
    if not valid_metrics:
        return {
            "error": "No servers responded",
            "timestamp": datetime.now().isoformat()
        }
    
    # Aggregate metrics
    total_requests = sum(m.get("requests", {}).get("total", 0) for m in valid_metrics)
    cpu_values = [m.get("cpu", {}).get("percent", 0) for m in valid_metrics if m.get("cpu")]
    memory_values = [m.get("memory", {}).get("percent", 0) for m in valid_metrics if m.get("memory")]
    
    return {
        "total_servers": NUM_SERVERS,
        "responding_servers": len(valid_metrics),
        "aggregated_metrics": {
            "total_requests": total_requests,
            "cpu": {
                "average": round(statistics.mean(cpu_values), 2) if cpu_values else 0,
                "max": round(max(cpu_values), 2) if cpu_values else 0,
                "min": round(min(cpu_values), 2) if cpu_values else 0,
            },
            "memory": {
                "average": round(statistics.mean(memory_values), 2) if memory_values else 0,
                "max": round(max(memory_values), 2) if memory_values else 0,
                "min": round(min(memory_values), 2) if memory_values else 0,
            }
        },
        "timestamp": datetime.now().isoformat()
    }


@app.post("/api/load-test")
async def run_load_test(request: LoadTestRequest):
    """Run a load test against specified servers"""
    target_servers = request.target_servers or list(range(1, NUM_SERVERS + 1))
    
    # Validate server IDs
    invalid_servers = [s for s in target_servers if s < 1 or s > NUM_SERVERS]
    if invalid_servers:
        raise HTTPException(status_code=400, detail=f"Invalid server IDs: {invalid_servers}")
    
    results = []
    
    async with aiohttp.ClientSession() as session:
        for server_id in target_servers:
            url = get_server_url(server_id)
            start_time = datetime.now()
            
            # Simple load test: make multiple concurrent requests
            tasks = []
            for _ in range(request.requests):
                tasks.append(fetch_url(session, url, timeout=30))
            
            responses = await asyncio.gather(*tasks)
            end_time = datetime.now()
            
            duration = (end_time - start_time).total_seconds()
            successful = sum(1 for r in responses if "error" not in r)
            failed = len(responses) - successful
            
            results.append({
                "server_id": server_id,
                "requests": request.requests,
                "successful": successful,
                "failed": failed,
                "duration_seconds": round(duration, 2),
                "requests_per_second": round(request.requests / duration, 2) if duration > 0 else 0
            })
    
    return {
        "load_test_results": results,
        "total_requests": sum(r["requests"] for r in results),
        "total_successful": sum(r["successful"] for r in results),
        "total_failed": sum(r["failed"] for r in results),
        "timestamp": datetime.now().isoformat()
    }


@app.post("/api/simulate-load")
async def simulate_load(request: SimulateLoadRequest):
    """Trigger load simulation on specific servers"""
    results = []
    
    async with aiohttp.ClientSession() as session:
        for server_id in request.server_ids:
            if server_id < 1 or server_id > NUM_SERVERS:
                results.append({
                    "server_id": server_id,
                    "status": "error",
                    "message": "Invalid server ID"
                })
                continue
            
            url = f"{get_server_url(server_id)}/simulate-load"
            params = {
                "cpu_duration": request.cpu_duration,
                "memory_mb": request.memory_mb
            }
            
            try:
                async with session.post(url, params=params, timeout=aiohttp.ClientTimeout(total=30)) as response:
                    if response.status == 200:
                        data = await response.json()
                        results.append({
                            "server_id": server_id,
                            "status": "success",
                            "data": data
                        })
                    else:
                        results.append({
                            "server_id": server_id,
                            "status": "error",
                            "message": f"HTTP {response.status}"
                        })
            except Exception as e:
                results.append({
                    "server_id": server_id,
                    "status": "error",
                    "message": str(e)
                })
    
    return {
        "results": results,
        "timestamp": datetime.now().isoformat()
    }


@app.post("/api/broadcast")
async def broadcast_request(endpoint: str = "/"):
    """Broadcast a GET request to all servers"""
    async with aiohttp.ClientSession() as session:
        tasks = []
        for i in range(1, NUM_SERVERS + 1):
            url = f"{get_server_url(i)}{endpoint}"
            tasks.append(fetch_url(session, url))
        
        results = await asyncio.gather(*tasks)
    
    successful = sum(1 for r in results if "error" not in r)
    
    return {
        "endpoint": endpoint,
        "total_servers": NUM_SERVERS,
        "successful_responses": successful,
        "failed_responses": NUM_SERVERS - successful,
        "results": results,
        "timestamp": datetime.now().isoformat()
    }


if __name__ == "__main__":
    print("🎮 Starting Control Plane API...")
    print(f"   Managing {NUM_SERVERS} servers")
    print(f"   Port range: {BASE_PORT} - {BASE_PORT + NUM_SERVERS - 1}")
    print(f"   API: http://localhost:8000")
    print(f"   Docs: http://localhost:8000/docs")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )
