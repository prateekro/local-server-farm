#!/bin/bash
# Helper script to run commands with Docker in PATH

export PATH="/usr/local/bin:$PATH"

echo "🐳 Docker PATH Helper"
echo "====================="
echo ""
echo "Docker is now in PATH for this session."
echo ""

# Check if any arguments were provided
if [ $# -eq 0 ]; then
    echo "Usage examples:"
    echo "  ./docker-env.sh docker ps"
    echo "  ./docker-env.sh docker-compose up -d"
    echo "  ./docker-env.sh python3 tools/health_check.py"
    echo ""
    echo "Or source this script to add Docker to your current shell:"
    echo "  source ./docker-env.sh"
else
    # Execute the provided command
    "$@"
fi
