#!/bin/bash
# Startup Helper Script - Checks prerequisites and provides guidance

echo "🔍 Server Farm Startup Check"
echo "============================"
echo ""

# Check 1: Docker Desktop
echo "1. Checking Docker Desktop..."
if pgrep -q "Docker Desktop"; then
    echo "   ✅ Docker Desktop is running"
else
    echo "   ❌ Docker Desktop is NOT running"
    echo ""
    echo "   🔧 To fix: Start Docker Desktop"
    echo "      - Open Docker Desktop from Applications"
    echo "      - Wait for it to fully start (Docker icon in menu bar)"
    echo ""
fi

# Check 2: Docker CLI
echo ""
echo "2. Checking Docker CLI..."
if command -v docker &> /dev/null; then
    echo "   ✅ Docker CLI is available"
    docker --version
else
    echo "   ❌ Docker CLI not found"
    echo "   Docker Desktop may not be running"
fi

# Check 3: Docker daemon connection
echo ""
echo "3. Checking Docker daemon..."
if docker info &> /dev/null; then
    echo "   ✅ Docker daemon is accessible"
else
    echo "   ❌ Cannot connect to Docker daemon"
    echo ""
    echo "   🔧 To fix:"
    echo "      1. Make sure Docker Desktop is running"
    echo "      2. Wait 30 seconds for it to fully start"
    echo "      3. Run this script again"
    echo ""
    exit 1
fi

# Check 4: Docker containers
echo ""
echo "4. Checking Docker containers..."
RUNNING=$(docker ps --filter "name=server-" --format "{{.Names}}" | wc -l | tr -d ' ')
TOTAL=$(docker ps -a --filter "name=server-" --format "{{.Names}}" | wc -l | tr -d ' ')

if [ "$TOTAL" -eq 0 ]; then
    echo "   ⚠️  No server containers found"
    echo ""
    echo "   🔧 To fix: Build and start containers"
    echo "      cd /Users/prateekro/Documents/projects/ai"
    echo "      docker-compose up -d --build"
    echo ""
elif [ "$RUNNING" -eq 0 ]; then
    echo "   ⚠️  Found $TOTAL containers, but none are running"
    echo ""
    echo "   🔧 To fix: Start containers"
    echo "      cd /Users/prateekro/Documents/projects/ai"
    echo "      docker-compose start"
    echo ""
else
    echo "   ✅ Found $RUNNING running containers (out of $TOTAL total)"
fi

# Check 5: Python environment
echo ""
echo "5. Checking Python..."
if command -v python3 &> /dev/null; then
    echo "   ✅ Python 3 is available"
    python3 --version
else
    echo "   ❌ Python 3 not found"
fi

# Check 6: Node.js
echo ""
echo "6. Checking Node.js..."
if command -v node &> /dev/null; then
    echo "   ✅ Node.js is available"
    node --version
else
    echo "   ❌ Node.js not found"
    echo "   (Only needed for web interface)"
fi

# Check 7: Control Plane dependencies
echo ""
echo "7. Checking Control Plane dependencies..."
if python3 -c "import fastapi, docker, aiohttp" 2>/dev/null; then
    echo "   ✅ Control Plane dependencies installed"
else
    echo "   ⚠️  Some Control Plane dependencies missing"
    echo ""
    echo "   🔧 To fix:"
    echo "      cd /Users/prateekro/Documents/projects/ai/control-plane"
    echo "      pip3 install -r requirements.txt"
    echo ""
fi

# Summary
echo ""
echo "======================================"
echo "📊 Summary"
echo "======================================"

ALL_GOOD=true

if ! pgrep -q "Docker Desktop"; then
    echo "❌ Start Docker Desktop"
    ALL_GOOD=false
fi

if ! docker info &> /dev/null; then
    echo "❌ Docker daemon not accessible"
    ALL_GOOD=false
fi

if [ "$RUNNING" -eq 0 ]; then
    echo "⚠️  Start server containers"
    ALL_GOOD=false
fi

if $ALL_GOOD && [ "$RUNNING" -gt 0 ]; then
    echo "✅ All systems ready!"
    echo ""
    echo "🚀 Next steps:"
    echo ""
    echo "   Terminal 1: Start Control Plane"
    echo "   cd /Users/prateekro/Documents/projects/ai/control-plane"
    echo "   python3 main.py"
    echo ""
    echo "   Terminal 2: Start Web Interface"
    echo "   cd /Users/prateekro/Documents/projects/ai/web-interface"
    echo "   npm run dev"
    echo ""
    echo "   Then open: http://localhost:3000"
    echo ""
else
    echo ""
    echo "🔧 Follow the fix instructions above, then run:"
    echo "   ./check_startup.sh"
    echo ""
fi
