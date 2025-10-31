# 🎯 Complete Command Reference

Quick reference for all commands in the Server Farm project.

## Table of Contents
- [Setup Commands](#setup-commands)
- [Docker Commands](#docker-commands)
- [Testing Commands](#testing-commands)
- [Monitoring Commands](#monitoring-commands)
- [Make Commands](#make-commands)
- [API Commands](#api-commands)
- [Troubleshooting Commands](#troubleshooting-commands)

---

## Setup Commands

### Initial Setup
```bash
# Complete automated setup
./quickstart.sh

# Or manual setup
python3 generate_compose.py 50 8000
docker-compose up -d --build
```

### Install Dependencies
```bash
# Root dependencies
pip3 install -r requirements.txt

# Control plane dependencies
cd control-plane
pip3 install -r requirements.txt

# Tools dependencies
cd tools
pip3 install -r requirements.txt

# Web interface dependencies
cd web-interface
npm install
```

### Using Make (Recommended)
```bash
# Complete setup
make setup

# Install all dependencies
make install-deps

# Quick start everything
make quick-start
```

---

## Docker Commands

### Starting Services
```bash
# Start all 50 servers
docker-compose up -d

# Start with rebuild
docker-compose up -d --build

# Start specific server
docker-compose up -d server-1

# View startup logs
docker-compose up

# Start with scale (fewer servers)
docker-compose up -d --scale server=25
```

### Stopping Services
```bash
# Stop all servers
docker-compose down

# Stop specific server
docker-compose stop server-1

# Stop and remove volumes
docker-compose down -v

# Stop and remove images
docker-compose down --rmi all

# Force stop all
docker-compose kill
```

### Container Management
```bash
# List all containers
docker-compose ps

# List with IDs
docker-compose ps -q

# Restart all servers
docker-compose restart

# Restart specific server
docker-compose restart server-1

# Pause/unpause
docker-compose pause
docker-compose unpause

# Remove stopped containers
docker-compose rm
```

### Logs and Debugging
```bash
# View all logs
docker-compose logs

# Follow logs
docker-compose logs -f

# Logs for specific server
docker-compose logs server-1

# Last 50 lines
docker-compose logs --tail=50

# Logs since timestamp
docker-compose logs --since 2025-10-30T12:00:00

# Execute command in container
docker-compose exec server-1 /bin/bash
docker exec -it server-1 sh
```

### Resource Monitoring
```bash
# Real-time stats
docker stats

# Stats for all servers
docker stats $(docker-compose ps -q)

# One-time stats snapshot
docker stats --no-stream

# Format output
docker stats --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}"
```

### Cleanup
```bash
# Remove unused containers
docker container prune

# Remove unused images
docker image prune

# Remove unused volumes
docker volume prune

# Remove everything unused
docker system prune -a

# Check disk usage
docker system df
```

---

## Testing Commands

### Health Checks
```bash
# Check all servers
python3 tools/health_check.py

# Check specific number
python3 tools/health_check.py --servers 25

# Quick check via curl
curl http://localhost:8001/health
curl http://localhost:8000/api/health
```

### Load Testing
```bash
# Light load (10 servers, 100 requests)
python3 tools/load_test.py --servers 10 --requests 100 --concurrency 10

# Medium load (25 servers, 1000 requests)
python3 tools/load_test.py --servers 25 --requests 1000 --concurrency 20

# Heavy load (all servers, 10k requests)
python3 tools/load_test.py --servers 50 --requests 10000 --concurrency 100

# Custom load test
python3 tools/load_test.py --servers 5 --requests 500 --concurrency 50
```

### Stress Testing
```bash
# CPU stress test
curl -X POST http://localhost:8000/api/simulate-load \
  -H "Content-Type: application/json" \
  -d '{"server_ids": [1,2,3], "cpu_duration": 5.0, "memory_mb": 100}'

# Stress single server
curl -X POST "http://localhost:8001/simulate-load?cpu_duration=5&memory_mb=100"

# Stress all servers
for i in {8001..8050}; do
  curl -X POST "http://localhost:$i/simulate-load?cpu_duration=3&memory_mb=50" &
done
wait
```

### Chaos Testing
```bash
# Stop random server
docker-compose stop server-$((RANDOM % 50 + 1))

# Kill 5 random servers
for i in {1..5}; do
  docker-compose stop server-$((RANDOM % 50 + 1))
done

# Restart all stopped
docker-compose start

# Network partition
docker network disconnect ai_server-network server-10
docker network connect ai_server-network server-10
```

---

## Monitoring Commands

### Real-Time Monitoring
```bash
# Watch container status
watch -n 2 docker-compose ps

# Watch health status
watch -n 5 'python3 tools/health_check.py'

# Watch metrics
watch -n 1 'curl -s http://localhost:8001/metrics | jq .cpu.percent'

# Watch aggregated metrics
watch -n 2 'curl -s http://localhost:8000/api/metrics | jq .aggregated_metrics'

# Monitor docker stats
watch -n 1 'docker stats --no-stream | head -n 20'
```

### Log Monitoring
```bash
# Follow all logs
docker-compose logs -f

# Follow specific servers
docker-compose logs -f server-1 server-2 server-3

# Grep logs for errors
docker-compose logs | grep ERROR

# Count log entries
docker-compose logs | wc -l
```

### Resource Monitoring
```bash
# CPU usage
docker stats --format "table {{.Name}}\t{{.CPUPerc}}" --no-stream

# Memory usage
docker stats --format "table {{.Name}}\t{{.MemUsage}}" --no-stream

# Network I/O
docker stats --format "table {{.Name}}\t{{.NetIO}}" --no-stream

# Block I/O
docker stats --format "table {{.Name}}\t{{.BlockIO}}" --no-stream
```

---

## Make Commands

```bash
# Show all available commands
make help

# Setup
make setup              # Complete setup
make install-deps       # Install dependencies

# Container management
make start              # Start all servers
make stop               # Stop all servers
make restart            # Restart all servers
make build              # Rebuild containers
make clean              # Clean up everything

# Monitoring
make status             # Show status
make health             # Run health check
make logs               # Show logs
make stats              # Show resource usage

# Testing
make test               # Run basic tests
make load-test          # Run load test
make test-server        # Test first server

# Development
make control-plane      # Start control plane
make web                # Start web interface

# Utility
make count-running      # Count running containers
make restart-one        # Restart first server
make scale-down         # Scale to 25 servers
make scale-up           # Scale to 100 servers
```

---

## API Commands

### Control Plane API (localhost:8000)

#### Server Management
```bash
# List all servers
curl http://localhost:8000/api/servers | jq

# Get specific server
curl http://localhost:8000/api/servers/1 | jq

# Start server
curl -X POST http://localhost:8000/api/servers/1/action \
  -H "Content-Type: application/json" \
  -d '{"action": "start"}'

# Stop server
curl -X POST http://localhost:8000/api/servers/1/action \
  -H "Content-Type: application/json" \
  -d '{"action": "stop"}'

# Restart server
curl -X POST http://localhost:8000/api/servers/1/action \
  -H "Content-Type: application/json" \
  -d '{"action": "restart"}'
```

#### Health and Metrics
```bash
# Health check all servers
curl http://localhost:8000/api/health | jq

# Get aggregated metrics
curl http://localhost:8000/api/metrics | jq

# Pretty print specific metric
curl http://localhost:8000/api/metrics | jq '.aggregated_metrics.cpu'
```

#### Load Testing
```bash
# Basic load test
curl -X POST http://localhost:8000/api/load-test \
  -H "Content-Type: application/json" \
  -d '{
    "target_servers": [1,2,3,4,5],
    "requests": 100,
    "concurrency": 10
  }' | jq

# Load test all servers
curl -X POST http://localhost:8000/api/load-test \
  -H "Content-Type: application/json" \
  -d '{
    "requests": 1000,
    "concurrency": 50
  }' | jq
```

#### Broadcast
```bash
# Broadcast to all servers
curl -X POST "http://localhost:8000/api/broadcast?endpoint=/" | jq

# Broadcast health check
curl -X POST "http://localhost:8000/api/broadcast?endpoint=/health" | jq
```

### Individual Server API (localhost:8001-8050)

```bash
# Server info
curl http://localhost:8001/ | jq

# Health check
curl http://localhost:8001/health | jq

# Detailed metrics
curl http://localhost:8001/metrics | jq

# Slow endpoint (1-5 second delay)
curl http://localhost:8001/slow-endpoint | jq

# Simulate load
curl -X POST "http://localhost:8001/simulate-load?cpu_duration=3&memory_mb=100" | jq

# Test error handling
curl http://localhost:8001/error/500

# Generate large response
curl http://localhost:8001/data/1024  # 1MB
```

---

## Troubleshooting Commands

### Diagnosis
```bash
# Check Docker status
docker info
docker version

# Check if ports are available
lsof -i :8000-8050
netstat -an | grep 800

# Check container health
docker inspect server-1 | jq '.[0].State.Health'

# Check container logs for errors
docker-compose logs server-1 | grep -i error

# Validate docker-compose file
docker-compose config

# Check resource limits
docker inspect server-1 | jq '.[0].HostConfig.Memory'
```

### Fixing Issues
```bash
# Remove and recreate container
docker-compose rm -f server-1
docker-compose up -d server-1

# Rebuild from scratch
docker-compose down
docker-compose build --no-cache
docker-compose up -d

# Reset Docker (use carefully!)
docker system prune -a
docker volume prune

# Restart Docker daemon (macOS)
osascript -e 'quit app "Docker"'
open -a Docker
```

### Performance Issues
```bash
# Check if host is overloaded
top
htop  # if installed

# Check disk space
df -h

# Check Docker disk usage
docker system df -v

# Reduce number of servers
python3 generate_compose.py 25 8000
docker-compose up -d

# Increase Docker resources
# Docker Desktop -> Settings -> Resources
```

### Network Issues
```bash
# List Docker networks
docker network ls

# Inspect network
docker network inspect ai_server-network

# Test container connectivity
docker exec server-1 ping server-2

# Test DNS resolution
docker exec server-1 nslookup server-2

# Recreate network
docker-compose down
docker network rm ai_server-network
docker-compose up -d
```

---

## Development Commands

### Control Plane Development
```bash
# Start with auto-reload
cd control-plane
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Run in background
cd control-plane
python main.py &

# Stop background process
pkill -f "python main.py"
```

### Web Interface Development
```bash
# Start dev server
cd web-interface
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview

# Install new package
npm install <package-name>
```

### Code Changes
```bash
# Modify server app
vim server/app.py
docker-compose build server
docker-compose up -d

# Modify control plane
vim control-plane/main.py
pkill -f "python main.py"
python control-plane/main.py

# Modify web interface
vim web-interface/src/App.jsx
# Auto-reloads if dev server is running
```

---

## Useful One-Liners

```bash
# Count healthy servers
curl -s http://localhost:8000/api/health | jq '.healthy'

# Get all server IDs
docker-compose ps | grep server | awk '{print $1}'

# Restart all stopped servers
docker-compose ps -q | xargs docker start

# Get average CPU across all servers
curl -s http://localhost:8000/api/metrics | jq '.aggregated_metrics.cpu.average'

# Test all servers in parallel
for i in {8001..8050}; do curl -s http://localhost:$i/health & done | jq .

# Count running containers
docker-compose ps | grep -c Up

# Get total memory usage
docker stats --no-stream --format "{{.MemUsage}}" | awk '{sum+=$1} END {print sum}'

# Find slowest server
for i in {8001..8050}; do
  time=$(curl -o /dev/null -s -w '%{time_total}\n' http://localhost:$i/)
  echo "Server $((i-8000)): $time"
done | sort -t: -k2 -n | tail -1
```

---

## Shell Aliases (Optional)

Add to your `~/.zshrc` or `~/.bashrc`:

```bash
# Server Farm aliases
alias sf-start='cd /path/to/project && docker-compose up -d'
alias sf-stop='cd /path/to/project && docker-compose down'
alias sf-status='cd /path/to/project && docker-compose ps'
alias sf-health='cd /path/to/project && python3 tools/health_check.py'
alias sf-test='cd /path/to/project && python3 tools/load_test.py --servers 10 --requests 100'
alias sf-logs='cd /path/to/project && docker-compose logs -f'
alias sf-stats='docker stats --no-stream'
```

---

## Cheat Sheet Summary

```bash
# Quick Reference
Setup:        ./quickstart.sh  OR  make setup
Start:        docker-compose up -d  OR  make start
Stop:         docker-compose down  OR  make stop
Status:       docker-compose ps  OR  make status
Health:       python3 tools/health_check.py  OR  make health
Test:         python3 tools/load_test.py  OR  make load-test
Logs:         docker-compose logs -f  OR  make logs
Monitor:      docker stats  OR  make stats
API Docs:     http://localhost:8000/docs
Dashboard:    http://localhost:3000
```

---

**Bookmark this page for quick reference! 📚**
