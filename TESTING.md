# 🧪 Testing Guide

Comprehensive guide to testing your server farm in various scenarios.

## Table of Contents
1. [Basic Health Tests](#basic-health-tests)
2. [Load Testing](#load-testing)
3. [Stress Testing](#stress-testing)
4. [Chaos Engineering](#chaos-engineering)
5. [Performance Benchmarking](#performance-benchmarking)
6. [Integration Testing](#integration-testing)

---

## Basic Health Tests

### Test 1: Individual Server Health

```bash
# Test first server
curl http://localhost:8001/health

# Expected response:
{
  "status": "healthy",
  "server_id": "server-1",
  "timestamp": "2025-10-30T12:00:00"
}

# Test all servers sequentially
for i in {8001..8050}; do
  echo "Testing localhost:$i"
  curl -s http://localhost:$i/health | jq .status
done
```

### Test 2: Control Plane Health Check

```bash
# Check all servers via control plane
curl http://localhost:8000/api/health | jq

# Expected: 50 healthy servers
python3 tools/health_check.py
```

### Test 3: Metrics Collection

```bash
# Get metrics from one server
curl http://localhost:8001/metrics | jq

# Get aggregated metrics
curl http://localhost:8000/api/metrics | jq

# Check specific metrics
curl http://localhost:8000/api/metrics | jq '.aggregated_metrics.cpu'
```

---

## Load Testing

### Test 4: Light Load (100 requests)

```bash
# Test 10 servers with light load
python3 tools/load_test.py \
  --servers 10 \
  --requests 100 \
  --concurrency 5

# Expected:
# - 1000 total requests
# - 100% success rate
# - <100ms average response time
```

### Test 5: Medium Load (1000 requests)

```bash
# Test 25 servers with medium load
python3 tools/load_test.py \
  --servers 25 \
  --requests 1000 \
  --concurrency 20

# Expected:
# - 25,000 total requests
# - >99% success rate
# - <200ms average response time
```

### Test 6: Heavy Load (10,000 requests)

```bash
# Test all 50 servers with heavy load
python3 tools/load_test.py \
  --servers 50 \
  --requests 10000 \
  --concurrency 100

# Expected:
# - 500,000 total requests
# - >95% success rate
# - Response times vary with load
```

### Test 7: Sustained Load

```bash
# Run continuous load for 60 seconds
for i in {1..60}; do
  curl -s http://localhost:8001/ > /dev/null &
  sleep 1
done

# Monitor during load
watch -n 1 'curl -s http://localhost:8001/metrics | jq .cpu.percent'
```

---

## Stress Testing

### Test 8: CPU Stress

```bash
# Simulate CPU load on first 5 servers
curl -X POST http://localhost:8000/api/simulate-load \
  -H "Content-Type: application/json" \
  -d '{
    "server_ids": [1,2,3,4,5],
    "cpu_duration": 10.0,
    "memory_mb": 50
  }'

# Monitor CPU usage
docker stats --no-stream | grep server
```

### Test 9: Memory Stress

```bash
# Allocate 200MB memory on servers
curl -X POST http://localhost:8000/api/simulate-load \
  -H "Content-Type: application/json" \
  -d '{
    "server_ids": [1,2,3,4,5],
    "cpu_duration": 1.0,
    "memory_mb": 200
  }'

# Check memory usage
docker stats --no-stream | grep server | awk '{print $1, $7}'
```

### Test 10: Concurrent Stress

```bash
# Stress all servers simultaneously
for i in {1..50}; do
  curl -X POST "http://localhost:$((8000+i))/simulate-load?cpu_duration=5&memory_mb=100" &
done
wait

# Check overall impact
curl http://localhost:8000/api/metrics | jq '.aggregated_metrics'
```

---

## Chaos Engineering

### Test 11: Random Server Failures

```bash
# Kill 5 random servers
for i in {1..5}; do
  server=$((RANDOM % 50 + 1))
  echo "Stopping server-$server"
  docker-compose stop server-$server
  sleep 2
done

# Check system resilience
python3 tools/health_check.py

# Restart failed servers
for i in {1..5}; do
  server=$((RANDOM % 50 + 1))
  echo "Starting server-$server"
  docker-compose start server-$server
done
```

### Test 12: Network Partition Simulation

```bash
# Disconnect a server from network
docker network disconnect ai_server-network server-10

# Test system behavior
curl http://localhost:8000/api/health | jq

# Reconnect
docker network connect ai_server-network server-10
```

### Test 13: Cascade Failure Simulation

```bash
# Stop servers in sequence to simulate cascade
for i in {1..10}; do
  echo "Stopping server-$i"
  docker-compose stop server-$i
  sleep 1
  
  # Check remaining servers
  python3 tools/health_check.py
done

# Restart all
docker-compose start
```

### Test 14: Resource Exhaustion

```bash
# Fill up disk space (be careful!)
docker exec server-1 dd if=/dev/zero of=/tmp/testfile bs=1M count=100

# Watch for OOM (Out of Memory)
for i in {1..50}; do
  curl -X POST "http://localhost:$((8000+i))/simulate-load?memory_mb=250" &
done
```

---

## Performance Benchmarking

### Test 15: ApacheBench Comparison

```bash
# Benchmark single server
ab -n 10000 -c 100 http://localhost:8001/

# Benchmark multiple servers (with load balancer)
# First, set up nginx or similar, then:
ab -n 100000 -c 500 http://localhost/
```

### Test 16: wrk Benchmarking

```bash
# Install wrk first: brew install wrk (macOS)

# Test single server
wrk -t12 -c400 -d30s http://localhost:8001/

# Test with custom Lua script
wrk -t12 -c400 -d30s -s script.lua http://localhost:8001/
```

### Test 17: Response Time Distribution

```bash
# Test different endpoints
curl -w "@curl-format.txt" -o /dev/null -s http://localhost:8001/
curl -w "@curl-format.txt" -o /dev/null -s http://localhost:8001/metrics
curl -w "@curl-format.txt" -o /dev/null -s http://localhost:8001/slow-endpoint

# curl-format.txt content:
# time_namelookup:  %{time_namelookup}\n
# time_connect:     %{time_connect}\n
# time_total:       %{time_total}\n
```

### Test 18: Throughput Testing

```bash
# Measure requests per second
echo "Testing RPS..."
start=$(date +%s)
for i in {1..10000}; do
  curl -s http://localhost:8001/ > /dev/null
done
end=$(date +%s)
duration=$((end - start))
rps=$((10000 / duration))
echo "RPS: $rps"
```

---

## Integration Testing

### Test 19: Broadcast Testing

```bash
# Broadcast to all servers
curl -X POST "http://localhost:8000/api/broadcast?endpoint=/"

# Verify all responses
curl -X POST "http://localhost:8000/api/broadcast?endpoint=/health" | \
  jq '.successful_responses'
```

### Test 20: Load Balancer Testing

Create `nginx.conf`:
```nginx
upstream backend {
    least_conn;
    server localhost:8001;
    server localhost:8002;
    server localhost:8003;
}

server {
    listen 9090;
    location / {
        proxy_pass http://backend;
    }
}
```

Test:
```bash
# Start nginx
nginx -c /path/to/nginx.conf

# Test load distribution
for i in {1..100}; do
  curl -s http://localhost:9090/
done | jq .server_id | sort | uniq -c
```

### Test 21: Database Connection Pool Testing

```python
# test_db_pool.py
import asyncio
import aiohttp

async def test_connections():
    async with aiohttp.ClientSession() as session:
        tasks = []
        for i in range(1, 51):
            url = f"http://localhost:{8000+i}/"
            tasks.append(session.get(url))
        
        responses = await asyncio.gather(*tasks)
        print(f"Concurrent connections: {len(responses)}")

asyncio.run(test_connections())
```

### Test 22: Service Discovery Testing

```bash
# Test DNS resolution
for i in {1..50}; do
  docker exec server-$i nslookup server-1
done

# Test inter-container communication
docker exec server-1 curl http://server-2:8000/health
```

---

## Automated Test Suite

### Complete Test Runner

```bash
#!/bin/bash
# run_all_tests.sh

echo "🧪 Running Complete Test Suite"
echo "==============================="

# Health checks
echo "1. Health Check..."
python3 tools/health_check.py || exit 1

# Basic load
echo "2. Light Load Test..."
python3 tools/load_test.py --servers 10 --requests 100 --concurrency 10 || exit 1

# Stress test
echo "3. Stress Test..."
curl -X POST http://localhost:8000/api/simulate-load \
  -H "Content-Type: application/json" \
  -d '{"server_ids": [1,2,3], "cpu_duration": 2.0, "memory_mb": 50}'

# Chaos test
echo "4. Chaos Test (killing server-25)..."
docker-compose stop server-25
sleep 5
python3 tools/health_check.py
docker-compose start server-25

# Final health check
echo "5. Final Health Check..."
python3 tools/health_check.py || exit 1

echo "✅ All tests passed!"
```

Make it executable:
```bash
chmod +x run_all_tests.sh
./run_all_tests.sh
```

---

## Test Metrics to Track

### Key Performance Indicators

1. **Availability**: % of servers responding
2. **Latency**: Average/p95/p99 response times
3. **Throughput**: Requests per second
4. **Error Rate**: % of failed requests
5. **Resource Usage**: CPU, Memory, Disk
6. **Recovery Time**: Time to heal after failure

### Example Test Report

```
📊 Test Report: Heavy Load Test
================================
Date: 2025-10-30 12:00:00
Duration: 60 seconds

Metrics:
- Total Requests: 100,000
- Successful: 99,547 (99.55%)
- Failed: 453 (0.45%)
- Avg Latency: 45ms
- P95 Latency: 120ms
- P99 Latency: 250ms
- Throughput: 1,666 req/s
- Avg CPU: 45%
- Avg Memory: 65%
- Server Uptime: 100%

Status: ✅ PASSED
```

---

## Continuous Testing

### Cron Job for Monitoring

```bash
# Add to crontab: crontab -e
*/5 * * * * cd /path/to/project && python3 tools/health_check.py >> logs/health.log 2>&1
0 * * * * cd /path/to/project && python3 tools/load_test.py --servers 50 --requests 100 >> logs/load.log 2>&1
```

### GitHub Actions CI

```yaml
name: Server Farm Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
      - name: Generate compose
        run: python3 generate_compose.py 10 8000
      - name: Start servers
        run: docker-compose up -d
      - name: Wait for healthy
        run: sleep 30
      - name: Run tests
        run: python3 tools/health_check.py
```

---

## Tips for Effective Testing

1. **Start Small**: Begin with 10 servers, then scale up
2. **Monitor Resources**: Watch `docker stats` during tests
3. **Test Incrementally**: Increase load gradually
4. **Document Results**: Keep a log of test outcomes
5. **Automate**: Create scripts for repeated tests
6. **Vary Scenarios**: Test different failure modes
7. **Measure Consistently**: Use same metrics across tests
8. **Test Limits**: Find breaking points
9. **Recovery Testing**: Ensure system can heal
10. **Real-World Simulation**: Mix different request types

---

**Happy Testing! 🚀**
