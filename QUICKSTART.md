# 🚀 Quick Start Guide

Welcome! This guide will get you up and running with your 50-server local simulation in minutes.

## Prerequisites Check

Before starting, make sure you have:

- ✅ **Docker Desktop** - [Download here](https://www.docker.com/products/docker-desktop)
- ✅ **Python 3.9+** - Check with `python3 --version`
- ✅ **Node.js 18+** - Check with `node --version`
- ✅ **8GB+ RAM available** - Check your system resources

## 🎯 Option 1: Automated Setup (Recommended)

Run the quick start script:

```bash
cd /Users/prateekro/Documents/projects/ai
./quickstart.sh
```

This will:
1. ✅ Check prerequisites
2. 📦 Generate docker-compose.yml
3. 🐳 Build and start 50 Docker containers
4. 📦 Install Python dependencies
5. 📦 Install Node.js dependencies

## 🎯 Option 2: Manual Setup

### Step 1: Generate Docker Compose Configuration

```bash
cd /Users/prateekro/Documents/projects/ai
python3 generate_compose.py 50 8000
```

This creates a `docker-compose.yml` with 50 servers on ports 8001-8050.

### Step 2: Start the Servers

```bash
# Build and start all containers
docker-compose up -d --build

# Check status
docker-compose ps

# View logs
docker-compose logs -f server-1
```

**Note**: First-time build takes 5-10 minutes. Subsequent starts are much faster!

### Step 3: Set Up Control Plane

```bash
cd control-plane

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Start the API
python main.py
```

The Control Plane API will be available at: **http://localhost:8000**

Test it:
```bash
curl http://localhost:8000/api/health
```

### Step 4: Set Up Web Interface

Open a **new terminal**:

```bash
cd /Users/prateekro/Documents/projects/ai/web-interface

# Install dependencies
npm install

# Start development server
npm run dev
```

The Web Interface will be available at: **http://localhost:3000**

## 🎮 Your First Tests

### Test 1: Check Individual Server

```bash
# Test server 1
curl http://localhost:8001/health

# Get metrics
curl http://localhost:8001/metrics | jq

# Test slow endpoint
curl http://localhost:8001/slow-endpoint
```

### Test 2: Check All Servers

```bash
cd /Users/prateekro/Documents/projects/ai

# Run health check
python3 tools/health_check.py

# Expected output:
# ✅ Healthy servers: 50/50 (100.0%)
```

### Test 3: Run Load Test

```bash
# Light load test (100 requests to first 10 servers)
python3 tools/load_test.py --servers 10 --requests 100 --concurrency 10

# Expected output:
# 📊 Total RPS: ~1000+
# ✅ All servers responded successfully!
```

### Test 4: Use the Web Interface

1. Open **http://localhost:3000** in your browser
2. You should see all 50 servers with green "running" badges
3. Click **"🔄 Refresh Now"** to update metrics
4. Click **"⚡ Run Load Test"** to test first 10 servers
5. Watch the CPU and Memory bars update in real-time

### Test 5: Use the Control Plane API

```bash
# Get all server status
curl http://localhost:8000/api/servers | jq

# Get aggregated metrics
curl http://localhost:8000/api/metrics | jq

# Broadcast a request to all servers
curl -X POST http://localhost:8000/api/broadcast?endpoint=/

# Run a load test via API
curl -X POST http://localhost:8000/api/load-test \
  -H "Content-Type: application/json" \
  -d '{
    "target_servers": [1,2,3,4,5],
    "requests": 200,
    "concurrency": 20
  }' | jq
```

## 📊 What You Should See

### Docker Containers
```bash
docker-compose ps
```

You should see 50 containers with status "Up (healthy)"

### Resource Usage
```bash
docker stats --no-stream | head -n 20
```

Expected resource usage per server:
- CPU: 0.5-5% (idle)
- Memory: 50-150 MB

### Control Plane Logs

You should see:
```
🎮 Starting Control Plane API...
   Managing 50 servers
   Port range: 8001 - 8050
   API: http://localhost:8000
   Docs: http://localhost:8000/docs
```

### Web Interface

You should see:
- Total Servers: 50
- Running: 50 (100% uptime)
- Healthy: 50
- All server cards showing green status

## 🔥 Common First-Time Issues

### Issue: "Port already in use"

**Solution**: Check if something is using ports 8000-8050
```bash
lsof -i :8000-8050
```

Kill the process or use different ports:
```bash
python3 generate_compose.py 50 9000  # Use ports 9001-9050
```

### Issue: "Cannot connect to Docker daemon"

**Solution**: Make sure Docker Desktop is running
```bash
# Check Docker status
docker info

# If not running, start Docker Desktop
open /Applications/Docker.app  # macOS
```

### Issue: "Out of memory"

**Solution**: Reduce number of servers
```bash
# Start with 25 servers
docker-compose up -d --scale server=25

# Or use the generator for 25 servers
python3 generate_compose.py 25 8000
docker-compose up -d --build
```

### Issue: Containers unhealthy

**Solution**: Give them more time or check logs
```bash
# Wait 30 seconds after starting
sleep 30

# Check specific server logs
docker-compose logs server-1

# Restart unhealthy server
docker-compose restart server-1
```

### Issue: Control Plane can't connect to Docker

**Solution**: Make sure Docker API is accessible
```bash
# Test Docker API
docker ps

# If that works, your Docker SDK should work too
```

## 🎊 Success Checklist

✅ All 50 containers running and healthy  
✅ Control Plane API responding at port 8000  
✅ Web Interface loading at port 3000  
✅ Health check shows 50/50 healthy  
✅ Individual server responds to `curl localhost:8001/health`  
✅ Load test completes successfully  

## 🎯 Next Steps

Now that everything is running:

1. **Explore the Web Dashboard**
   - Monitor real-time metrics
   - Try different load tests
   - Watch resource usage

2. **Read the API Docs**
   - Visit http://localhost:8000/docs
   - Try the interactive API examples

3. **Run Advanced Tests**
   - See `ADVANCED.md` for complex scenarios
   - Try chaos engineering examples
   - Set up monitoring with Prometheus

4. **Customize Your Setup**
   - Modify server application (`server/app.py`)
   - Add new API endpoints
   - Create custom load tests

## 🛑 Stopping Everything

When you're done:

```bash
# Stop all containers
./stop.sh

# Or manually
docker-compose down

# Stop and remove all data
docker-compose down -v
```

## 📚 Additional Resources

- **Full Documentation**: `README.md`
- **Advanced Usage**: `ADVANCED.md`
- **API Documentation**: http://localhost:8000/docs (when running)
- **Example Config**: `.env.example`

## 🆘 Getting Help

If you encounter issues:

1. Check the logs: `docker-compose logs`
2. Verify Docker is running: `docker info`
3. Check resource usage: `docker stats`
4. Review the troubleshooting section above

## 💡 Quick Tips

- Use `Ctrl+C` to stop the Control Plane or Web Interface
- Use `docker-compose restart server-X` to restart a specific server
- The Web Interface auto-refreshes every 5 seconds
- All servers share the same network, so they can communicate
- Each server has its own isolated file system and process space

---

**Enjoy your local server farm! 🎉**

For questions or contributions, see the main README.md file.
