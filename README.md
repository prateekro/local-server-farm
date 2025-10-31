# 🖥️ Local Server Farm Simulator

A sophisticated local development environment that simulates **50 independent servers** using Docker containers, complete with a beautiful web-based control panel for monitoring, testing, and benchmarking.

![Project Status](https://img.shields.io/badge/status-ready-brightgreen)
![Docker](https://img.shields.io/badge/docker-required-blue)
![Python](https://img.shields.io/badge/python-3.9+-blue)
![License](https://img.shields.io/badge/license-MIT-green)

**📚 [Complete Documentation Index](DOCUMENTATION.md) | 🚀 [Quick Start Guide](QUICKSTART.md) | 🧪 [Testing Guide](TESTING.md) | 💻 [Command Reference](COMMANDS.md)**

## 🌟 Features

- **50 Containerized Servers**: Each running an isolated FastAPI application
- **Real-time Monitoring**: Track CPU, memory, and request metrics for all servers
- **Central Control Panel**: Beautiful React-based dashboard
- **Load Testing**: Built-in tools to simulate traffic and measure performance
- **Health Checks**: Automatic monitoring of server health
- **Scalable Architecture**: Easy to scale from 10 to 100+ servers
- **API-First Design**: RESTful APIs for all operations

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Control Panel (React)                 │
│            http://localhost:3000                         │
└─────────────────┬───────────────────────────────────────┘
                  │
┌─────────────────▼───────────────────────────────────────┐
│              Control Plane API (FastAPI)                 │
│            http://localhost:8000                         │
│  - Orchestrates containers                               │
│  - Collects metrics                                      │
│  - Manages load tests                                    │
└─────────────────┬───────────────────────────────────────┘
                  │
    ┌─────────────┴─────────────┐
    │                           │
┌───▼────┐  ┌────────┐     ┌────────┐
│Server 1│  │Server 2│ ... │Server50│
│:8001   │  │:8002   │     │:8050   │
└────────┘  └────────┘     └────────┘
   Each running FastAPI with:
   - Health endpoints
   - Metrics collection
   - Simulated workload
   - Resource monitoring
```

## 🚀 Quick Start

### Prerequisites

- Docker Desktop installed and running
- Python 3.9+ (for control plane)
- Node.js 18+ (for web interface)

### 1. Clone and Setup

```bash
# Navigate to project directory
cd /Users/prateekro/Documents/projects/ai

# Install Python dependencies for control plane
cd control-plane
pip install -r requirements.txt
cd ..
```

### 2. Start All 50 Servers

```bash
# Build and start all containers (this may take a few minutes first time)
docker-compose up -d --build

# Check all containers are running
docker-compose ps
```

### 3. Start Control Plane API

```bash
cd control-plane
python main.py
```

The Control Plane API will be available at: `http://localhost:8000`

### 4. Start Web Interface

```bash
cd web-interface
npm install
npm run dev
```

The Web Interface will be available at: `http://localhost:3000`

## 📊 Using the System

### Web Dashboard

Visit `http://localhost:3000` to access the control panel where you can:

- View all 50 servers and their status
- Monitor real-time metrics (CPU, memory, requests)
- Start/stop individual servers or groups
- Run load tests across all servers
- View aggregate statistics

### API Endpoints

The Control Plane API (`http://localhost:8000`) provides:

#### Server Management
- `GET /api/servers` - List all servers
- `GET /api/servers/{id}` - Get specific server details
- `POST /api/servers/{id}/restart` - Restart a server
- `POST /api/servers/start-all` - Start all servers
- `POST /api/servers/stop-all` - Stop all servers

#### Metrics & Monitoring
- `GET /api/metrics` - Get aggregated metrics
- `GET /api/metrics/{id}` - Get metrics for specific server
- `GET /api/health` - Check health of all servers

#### Load Testing
- `POST /api/load-test` - Run load test
- `GET /api/load-test/results` - Get latest test results

### Individual Server API

Each server (`http://localhost:8001-8050`) exposes:

- `GET /` - Basic info
- `GET /health` - Health check
- `GET /metrics` - Server metrics
- `POST /simulate-load` - Simulate CPU/memory load
- `GET /slow-endpoint` - Simulate slow response (for testing)

## 🧪 Testing Scenarios

### Scenario 1: Health Check All Servers

```bash
curl http://localhost:8000/api/health
```

### Scenario 2: Load Test Specific Server

```bash
# Using ApacheBench
ab -n 1000 -c 10 http://localhost:8001/

# Using the control plane
curl -X POST http://localhost:8000/api/load-test \
  -H "Content-Type: application/json" \
  -d '{"target_servers": [1,2,3], "requests": 1000, "concurrency": 10}'
```

### Scenario 3: Simulate Server Failure

```bash
# Stop a specific server
docker-compose stop server-25

# Check how the system detects it
curl http://localhost:8000/api/servers/25
```

### Scenario 4: Scale Up/Down

```bash
# Scale to 100 servers
docker-compose up -d --scale server=100

# Scale back to 50
docker-compose up -d --scale server=50
```

## 🔧 Configuration

### Adjusting Number of Servers

Edit `docker-compose.yml`:

```yaml
# Change the number of replicas
services:
  server:
    deploy:
      replicas: 50  # Change this number
```

### Server Resource Limits

Each server has configurable resource limits in `docker-compose.yml`:

```yaml
deploy:
  resources:
    limits:
      cpus: '0.5'
      memory: 512M
```

### Environment Variables

Create `.env` file:

```env
# Control Plane
CONTROL_PLANE_PORT=8000
LOG_LEVEL=INFO

# Servers
SERVER_BASE_PORT=8001
SERVER_COUNT=50
```

## 📈 Performance Testing

### Built-in Load Testing

The system includes built-in load testing capabilities:

```python
# From Python
import requests

response = requests.post('http://localhost:8000/api/load-test', json={
    'target_servers': list(range(1, 51)),  # All servers
    'requests': 10000,
    'concurrency': 100,
    'duration': 60  # seconds
})

print(response.json())
```

### External Tools

Recommended tools for advanced testing:

- **wrk**: `wrk -t12 -c400 -d30s http://localhost:8001`
- **Apache Bench**: `ab -n 10000 -c 100 http://localhost:8001/`
- **Locust**: For complex user behavior simulation

## 🛠️ Development

### Project Structure

```
.
├── control-plane/          # Control plane API
│   ├── main.py            # FastAPI application
│   ├── docker_manager.py  # Docker SDK integration
│   ├── metrics_collector.py
│   └── requirements.txt
│
├── server/                 # Individual server application
│   ├── app.py             # FastAPI server
│   ├── Dockerfile
│   └── requirements.txt
│
├── web-interface/          # React dashboard
│   ├── src/
│   │   ├── components/
│   │   ├── App.jsx
│   │   └── main.jsx
│   ├── package.json
│   └── vite.config.js
│
├── docker-compose.yml      # Orchestration
└── README.md
```

### Adding New Features

1. **New Server Endpoint**: Edit `server/app.py`
2. **New Control API**: Edit `control-plane/main.py`
3. **New UI Component**: Add to `web-interface/src/components/`

## 🐛 Troubleshooting

### Containers won't start

```bash
# Check Docker is running
docker info

# Check logs
docker-compose logs server-1

# Rebuild from scratch
docker-compose down -v
docker-compose up -d --build
```

### Port conflicts

```bash
# Check what's using ports
lsof -i :8000-8050

# Change base port in docker-compose.yml
```

### High resource usage

```bash
# Reduce number of servers
docker-compose up -d --scale server=10

# Increase resource limits in docker-compose.yml
```

## 🎯 Use Cases

1. **Load Balancer Testing**: Deploy nginx/traefik and test load distribution
2. **Microservices Simulation**: Test service discovery, circuit breakers
3. **Chaos Engineering**: Randomly kill servers, simulate network issues
4. **Monitoring Stack**: Integrate Prometheus + Grafana
5. **CI/CD Pipeline**: Test deployment strategies (blue-green, canary)
6. **Database Connection Pooling**: Test connection limits with 50 clients

## 🤝 Contributing

Feel free to extend this project! Some ideas:

- Add Prometheus metrics export
- Implement WebSocket for real-time updates
- Add authentication/authorization
- Create Kubernetes manifests (for cloud deployment)
- Add more realistic workload simulations

## 📝 License

MIT License - Feel free to use this for learning and testing!

## 🙏 Credits

Built with modern tools: Docker, FastAPI, React, and ❤️
