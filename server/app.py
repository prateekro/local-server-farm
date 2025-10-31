from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import psutil
import os
import socket
from datetime import datetime
from typing import Dict
import asyncio
import random

app = FastAPI(title="Server Instance", description="Simulated Server Instance")

# Enable CORS for control panel
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Server identity
SERVER_ID = os.getenv("SERVER_ID", "unknown")
SERVER_PORT = int(os.getenv("SERVER_PORT", "8000"))
HOSTNAME = socket.gethostname()

# Metrics storage
request_count = 0
start_time = datetime.now()


@app.get("/")
async def root():
    """Basic server information"""
    global request_count
    request_count += 1
    
    return {
        "server_id": SERVER_ID,
        "hostname": HOSTNAME,
        "port": SERVER_PORT,
        "status": "running",
        "uptime_seconds": (datetime.now() - start_time).total_seconds(),
        "total_requests": request_count,
        "timestamp": datetime.now().isoformat()
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    cpu_percent = psutil.cpu_percent(interval=0.1)
    memory = psutil.virtual_memory()
    
    health_status = "healthy"
    if cpu_percent > 80 or memory.percent > 80:
        health_status = "degraded"
    
    return {
        "status": health_status,
        "server_id": SERVER_ID,
        "timestamp": datetime.now().isoformat()
    }


@app.get("/metrics")
async def get_metrics():
    """Detailed metrics endpoint"""
    global request_count
    
    cpu_percent = psutil.cpu_percent(interval=0.1)
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    
    # Network I/O
    net_io = psutil.net_io_counters()
    
    uptime = (datetime.now() - start_time).total_seconds()
    
    return {
        "server_id": SERVER_ID,
        "hostname": HOSTNAME,
        "port": SERVER_PORT,
        "timestamp": datetime.now().isoformat(),
        "uptime_seconds": uptime,
        "requests": {
            "total": request_count,
            "rate_per_minute": (request_count / uptime * 60) if uptime > 0 else 0
        },
        "cpu": {
            "percent": cpu_percent,
            "count": psutil.cpu_count()
        },
        "memory": {
            "total_mb": memory.total / (1024 * 1024),
            "available_mb": memory.available / (1024 * 1024),
            "used_mb": memory.used / (1024 * 1024),
            "percent": memory.percent
        },
        "disk": {
            "total_gb": disk.total / (1024 * 1024 * 1024),
            "used_gb": disk.used / (1024 * 1024 * 1024),
            "free_gb": disk.free / (1024 * 1024 * 1024),
            "percent": disk.percent
        },
        "network": {
            "bytes_sent": net_io.bytes_sent,
            "bytes_recv": net_io.bytes_recv,
            "packets_sent": net_io.packets_sent,
            "packets_recv": net_io.packets_recv
        }
    }


@app.get("/slow-endpoint")
async def slow_endpoint():
    """Simulate a slow endpoint (for testing timeouts, etc.)"""
    global request_count
    request_count += 1
    
    # Random delay between 1-5 seconds
    delay = random.uniform(1, 5)
    await asyncio.sleep(delay)
    
    return {
        "server_id": SERVER_ID,
        "message": "This was a slow response",
        "delay_seconds": delay,
        "timestamp": datetime.now().isoformat()
    }


@app.post("/simulate-load")
async def simulate_load(cpu_duration: float = 2.0, memory_mb: int = 100):
    """
    Simulate CPU and memory load for testing
    
    Args:
        cpu_duration: How long to use CPU (seconds)
        memory_mb: How much memory to allocate (MB)
    """
    global request_count
    request_count += 1
    
    # Simulate CPU load
    start = datetime.now()
    result = 0
    while (datetime.now() - start).total_seconds() < cpu_duration:
        result += sum(range(1000))
    
    # Simulate memory load
    memory_hog = bytearray(memory_mb * 1024 * 1024)
    
    return {
        "server_id": SERVER_ID,
        "message": "Load simulation completed",
        "cpu_duration": cpu_duration,
        "memory_allocated_mb": memory_mb,
        "timestamp": datetime.now().isoformat()
    }


@app.get("/error/{error_code}")
async def simulate_error(error_code: int):
    """Simulate various HTTP errors for testing"""
    global request_count
    request_count += 1
    
    error_messages = {
        400: "Bad Request",
        401: "Unauthorized",
        403: "Forbidden",
        404: "Not Found",
        500: "Internal Server Error",
        503: "Service Unavailable"
    }
    
    message = error_messages.get(error_code, "Unknown Error")
    raise HTTPException(status_code=error_code, detail=message)


@app.get("/data/{size_kb}")
async def generate_data(size_kb: int):
    """Generate response of specific size (for bandwidth testing)"""
    global request_count
    request_count += 1
    
    if size_kb > 10240:  # Limit to 10MB
        raise HTTPException(status_code=400, detail="Size too large (max 10MB)")
    
    # Generate random data
    data = "x" * (size_kb * 1024)
    
    return {
        "server_id": SERVER_ID,
        "size_kb": size_kb,
        "data": data[:100] + "...",  # Only show first 100 chars
        "timestamp": datetime.now().isoformat()
    }


@app.on_event("startup")
async def startup_event():
    """Log startup information"""
    print(f"🚀 Server {SERVER_ID} starting on {HOSTNAME}:{SERVER_PORT}")
    print(f"   CPU cores: {psutil.cpu_count()}")
    print(f"   Memory: {psutil.virtual_memory().total / (1024**3):.2f} GB")


@app.on_event("shutdown")
async def shutdown_event():
    """Log shutdown information"""
    uptime = (datetime.now() - start_time).total_seconds()
    print(f"🛑 Server {SERVER_ID} shutting down")
    print(f"   Uptime: {uptime:.2f} seconds")
    print(f"   Total requests: {request_count}")


if __name__ == "__main__":
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=SERVER_PORT,
        log_level="info"
    )
