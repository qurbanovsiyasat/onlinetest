#!/bin/bash

# Squiz Platform Startup Script
echo "🚀 Starting Squiz Platform..."

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Create necessary directories
mkdir -p logs
mkdir -p data/mongodb
mkdir -p data/redis

# Set permissions
chmod +x start.sh
chmod +x stop.sh

# Copy environment files if they don't exist
if [ ! -f backend/.env ]; then
    echo "📝 Creating backend environment file..."
    cp backend/.env.example backend/.env
fi

if [ ! -f frontend/.env ]; then
    echo "📝 Creating frontend environment file..."
    cp frontend/.env.example frontend/.env
fi

# Start services
echo "🐳 Starting Docker containers..."
docker-compose up -d

# Wait for services to be ready
echo "⏳ Waiting for services to start..."
sleep 10

# Check service health
echo "🔍 Checking service health..."

# Check MongoDB
if docker-compose exec -T mongodb mongosh --eval "db.adminCommand('ping')" > /dev/null 2>&1; then
    echo "✅ MongoDB is running"
else
    echo "❌ MongoDB failed to start"
fi

# Check Backend
if curl -f http://localhost:8001/api/health > /dev/null 2>&1; then
    echo "✅ Backend API is running"
else
    echo "❌ Backend API failed to start"
fi

# Check Frontend
if curl -f http://localhost:3000 > /dev/null 2>&1; then
    echo "✅ Frontend is running"
else
    echo "❌ Frontend failed to start"
fi

echo ""
echo "🎉 Squiz Platform is ready!"
echo ""
echo "📱 Frontend: http://localhost:3000"
echo "🔧 Backend API: http://localhost:8001"
echo "📊 API Docs: http://localhost:8001/docs"
echo "🗄️  MongoDB: localhost:27017"
echo ""
echo "👤 Default Admin Login:"
echo "   Email: admin@squiz.com"
echo "   Password: admin123"
echo ""
echo "📝 To stop the platform: ./stop.sh"
echo "📋 To view logs: docker-compose logs -f"
