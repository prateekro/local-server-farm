#!/bin/bash

# Server Farm Quick Start Script
# This script sets up and starts the entire server farm environment

set -e

echo "🚀 Server Farm Quick Start"
echo "=========================="
echo ""

# Check prerequisites
echo "📋 Checking prerequisites..."

if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker Desktop first."
    exit 1
fi

if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed."
    exit 1
fi

if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed."
    exit 1
fi

echo "✅ All prerequisites met!"
echo ""

# Generate docker-compose.yml
echo "🔧 Generating docker-compose.yml for 50 servers..."
python3 generate_compose.py 50 8000
echo ""

# Build and start containers
echo "🐳 Building and starting Docker containers..."
echo "   (This may take several minutes on first run)"
docker-compose up -d --build

echo ""
echo "⏳ Waiting for containers to be healthy..."
sleep 10

echo ""
echo "📊 Container status:"
docker-compose ps

echo ""
echo "🎮 Control Plane Setup"
echo "====================="
echo ""

# Install control plane dependencies
echo "📦 Installing control plane dependencies..."
cd control-plane
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi
source venv/bin/activate
pip install -q -r requirements.txt
cd ..

echo ""
echo "🌐 Web Interface Setup"
echo "====================="
echo ""

# Install web interface dependencies
echo "📦 Installing web interface dependencies..."
cd web-interface
npm install
cd ..

echo ""
echo "✅ Setup Complete!"
echo "=================="
echo ""
echo "🎯 Next Steps:"
echo ""
echo "1. Start Control Plane API:"
echo "   cd control-plane"
echo "   source venv/bin/activate"
echo "   python main.py"
echo "   → http://localhost:8000"
echo ""
echo "2. Start Web Interface (in new terminal):"
echo "   cd web-interface"
echo "   npm run dev"
echo "   → http://localhost:3000"
echo ""
echo "3. Test a server directly:"
echo "   curl http://localhost:8001/health"
echo ""
echo "📚 Full documentation: README.md"
echo ""
