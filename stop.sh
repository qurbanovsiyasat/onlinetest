#!/bin/bash

# Squiz Platform Stop Script
echo "🛑 Stopping Squiz Platform..."

# Stop all services
docker-compose down

echo "✅ All services stopped successfully!"
echo ""
echo "💡 To start again: ./start.sh"
echo "🗑️  To remove all data: docker-compose down -v"
