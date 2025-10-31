# Makefile for Server Farm Management
# Makes common tasks easier to execute

.PHONY: help setup start stop restart status health test load-test clean install-deps build logs

# Default target
help:
	@echo "🖥️  Server Farm Management Commands"
	@echo "==================================="
	@echo ""
	@echo "Setup & Installation:"
	@echo "  make setup          - Complete setup (install deps, generate compose)"
	@echo "  make install-deps   - Install all dependencies"
	@echo ""
	@echo "Container Management:"
	@echo "  make start          - Start all 50 servers"
	@echo "  make stop           - Stop all servers"
	@echo "  make restart        - Restart all servers"
	@echo "  make build          - Rebuild all containers"
	@echo "  make clean          - Remove all containers and volumes"
	@echo ""
	@echo "Monitoring:"
	@echo "  make status         - Show container status"
	@echo "  make health         - Run health check on all servers"
	@echo "  make logs           - Show logs from all containers"
	@echo "  make stats          - Show resource usage"
	@echo ""
	@echo "Testing:"
	@echo "  make test           - Run basic tests"
	@echo "  make load-test      - Run load test"
	@echo "  make test-server    - Test first server"
	@echo ""
	@echo "Development:"
	@echo "  make control-plane  - Start control plane API"
	@echo "  make web            - Start web interface"
	@echo "  make dev            - Start control plane and web (parallel)"
	@echo ""

# Setup
setup: install-deps
	@echo "🔧 Generating docker-compose.yml..."
	python3 generate_compose.py 50 8000
	@echo "✅ Setup complete!"
	@echo ""
	@echo "Next steps:"
	@echo "  1. make start"
	@echo "  2. make control-plane  (in another terminal)"
	@echo "  3. make web  (in another terminal)"

install-deps:
	@echo "📦 Installing dependencies..."
	pip3 install -r requirements.txt
	cd control-plane && pip3 install -r requirements.txt
	cd tools && pip3 install -r requirements.txt
	cd web-interface && npm install
	@echo "✅ Dependencies installed!"

# Container management
start:
	@echo "🚀 Starting all servers..."
	docker-compose up -d --build
	@echo "⏳ Waiting for containers to be healthy..."
	sleep 15
	@make status

stop:
	@echo "🛑 Stopping all servers..."
	docker-compose down
	@echo "✅ Stopped!"

restart:
	@echo "🔄 Restarting all servers..."
	docker-compose restart
	@echo "✅ Restarted!"

build:
	@echo "🔨 Building containers..."
	docker-compose build --no-cache
	@echo "✅ Build complete!"

clean:
	@echo "🧹 Cleaning up..."
	docker-compose down -v --rmi local
	@echo "✅ Cleanup complete!"

# Monitoring
status:
	@echo "📊 Container Status:"
	@docker-compose ps

health:
	@echo "🏥 Running health check..."
	@python3 tools/health_check.py

logs:
	@echo "📜 Container Logs:"
	@docker-compose logs --tail=50 -f

stats:
	@echo "📈 Resource Usage:"
	@docker stats --no-stream $$(docker-compose ps -q) | head -n 20

# Testing
test: health test-server
	@echo "✅ Basic tests passed!"

test-server:
	@echo "🧪 Testing server-1..."
	@curl -s http://localhost:8001/health | jq
	@curl -s http://localhost:8001/metrics | jq .requests

load-test:
	@echo "⚡ Running load test..."
	@python3 tools/load_test.py --servers 10 --requests 100 --concurrency 10

# Development
control-plane:
	@echo "🎮 Starting Control Plane..."
	@cd control-plane && python3 main.py

web:
	@echo "🌐 Starting Web Interface..."
	@cd web-interface && npm run dev

# Quick commands
quick-start: setup start
	@echo "🎉 Everything is set up and running!"
	@echo ""
	@echo "Access points:"
	@echo "  Web Dashboard: http://localhost:3000"
	@echo "  Control API:   http://localhost:8000"
	@echo "  API Docs:      http://localhost:8000/docs"
	@echo ""
	@echo "Next: Run 'make control-plane' and 'make web' in separate terminals"

# Utility targets
count-running:
	@echo "Running containers: $$(docker-compose ps | grep -c 'Up')"

restart-one:
	@echo "Restarting server-1..."
	@docker-compose restart server-1

scale-down:
	@echo "Scaling to 25 servers..."
	@python3 generate_compose.py 25 8000
	@docker-compose up -d

scale-up:
	@echo "Scaling to 100 servers..."
	@python3 generate_compose.py 100 8000
	@docker-compose up -d
