#!/bin/bash

# Stop all running containers and clean up

echo "🛑 Stopping Server Farm..."
echo ""

echo "Stopping all containers..."
docker-compose down

echo ""
echo "✅ All containers stopped!"
echo ""
echo "To remove all data:"
echo "  docker-compose down -v"
echo ""
echo "To remove images:"
echo "  docker-compose down --rmi all"
echo ""
