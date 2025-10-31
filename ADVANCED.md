# Advanced Usage Examples

## Testing Scenarios

### 1. Chaos Engineering - Random Server Failures

```bash
# Kill random servers
for i in {1..5}; do
    server=$((RANDOM % 50 + 1))
    docker-compose stop server-$server
    echo "Stopped server-$server"
done

# Watch the system recover
watch -n 2 'docker-compose ps | grep server'
```

### 2. Progressive Load Testing

```bash
# Start with light load
python tools/load_test.py --servers 50 --requests 50 --concurrency 5

# Medium load
python tools/load_test.py --servers 50 --requests 200 --concurrency 20

# Heavy load
python tools/load_test.py --servers 50 --requests 1000 --concurrency 100
```

### 3. Monitoring Individual Servers

```bash
# Watch server metrics in real-time
watch -n 1 'curl -s http://localhost:8001/metrics | jq'

# Monitor all server health
watch -n 5 'python tools/health_check.py'
```

### 4. Test Specific Endpoints

```bash
# Test slow endpoints
for i in {8001..8050}; do
    curl "http://localhost:$i/slow-endpoint" &
done

# Generate large responses
curl "http://localhost:8001/data/1024"  # 1MB response

# Simulate errors
curl "http://localhost:8001/error/500"
```

### 5. Docker Resource Monitoring

```bash
# Watch Docker stats
docker stats $(docker ps --format '{{.Names}}' | grep server)

# Check resource usage
docker-compose ps -q | xargs docker stats --no-stream
```

### 6. Network Simulation

```bash
# Add network latency to simulate real-world conditions
# (requires tc command - Linux/macOS with network tools)

# Add 100ms latency
sudo tc qdisc add dev lo root netem delay 100ms

# Remove latency
sudo tc qdisc del dev lo root
```

### 7. Load Balancer Testing

Create an nginx configuration:

```nginx
upstream backend {
    least_conn;
    server localhost:8001;
    server localhost:8002;
    server localhost:8003;
    # ... add all 50 servers
}

server {
    listen 80;
    location / {
        proxy_pass http://backend;
    }
}
```

Then test load distribution:

```bash
ab -n 10000 -c 100 http://localhost/
```

### 8. Prometheus Integration

Example prometheus.yml:

```yaml
scrape_configs:
  - job_name: 'servers'
    static_configs:
      - targets: ['localhost:8001', 'localhost:8002', ...]
```

### 9. Custom Scenarios via API

```python
import requests

# Simulate a server failure scenario
for server_id in [5, 10, 15]:
    requests.post(f'http://localhost:8000/api/servers/{server_id}/action', 
                  json={'action': 'stop'})

# Simulate recovery
time.sleep(30)
for server_id in [5, 10, 15]:
    requests.post(f'http://localhost:8000/api/servers/{server_id}/action', 
                  json={'action': 'start'})
```

### 10. Database Connection Pool Testing

```python
# Simulate 50 clients connecting to a database
import psycopg2
from concurrent.futures import ThreadPoolExecutor

def connect_from_server(server_id):
    conn = psycopg2.connect(
        host="db_host",
        database="test_db",
        user=f"server_{server_id}",
        password="password"
    )
    # Perform operations
    conn.close()

with ThreadPoolExecutor(max_workers=50) as executor:
    executor.map(connect_from_server, range(1, 51))
```

## Performance Benchmarks

### Expected Performance (on modern laptop)

- **Startup Time**: 30-60 seconds (first time with build)
- **Memory Usage**: ~5-10 GB total (50 servers × ~100-200 MB each)
- **CPU Usage**: Varies with load, ~10-20% idle
- **Request Latency**: <10ms average for simple endpoints
- **Throughput**: >50,000 requests/second across all servers

### Scaling Guidelines

| Servers | RAM Required | CPU Cores | Notes |
|---------|-------------|-----------|-------|
| 10      | 2 GB        | 2         | Light testing |
| 25      | 4 GB        | 4         | Development |
| 50      | 8 GB        | 4-8       | Full simulation |
| 100     | 16 GB       | 8+        | Stress testing |

## Troubleshooting

### Issue: Containers won't start

```bash
# Check Docker resources
docker system df

# Clean up unused resources
docker system prune -a

# Check logs
docker-compose logs server-1
```

### Issue: Port conflicts

```bash
# Find what's using ports
lsof -i :8001-8050

# Use different port range
python generate_compose.py 50 9000
```

### Issue: High CPU usage

```bash
# Reduce number of servers
docker-compose up -d --scale server=25

# Or increase resource limits in docker-compose.yml
```

### Issue: Out of memory

```bash
# Check current usage
docker stats

# Reduce memory limits per container
# Edit docker-compose.yml memory limits to 128M
```

## Integration Examples

### CI/CD Pipeline Testing

```yaml
# .github/workflows/test.yml
name: Load Test
on: [push]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Start servers
        run: |
          python generate_compose.py 10 8000
          docker-compose up -d
      - name: Run tests
        run: python tools/load_test.py --servers 10 --requests 100
```

### Grafana Dashboard

```json
{
  "dashboard": {
    "title": "Server Farm Metrics",
    "panels": [
      {
        "title": "CPU Usage",
        "targets": [
          {
            "expr": "container_cpu_usage_seconds_total{name=~\"server-.*\"}"
          }
        ]
      }
    ]
  }
}
```
