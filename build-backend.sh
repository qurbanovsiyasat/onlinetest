#!/bin/bash

# Build script for Render.com backend deployment

echo "🚀 Starting Squiz Backend Build Process..."

# Navigate to backend directory
cd backend

echo "📦 Installing Python dependencies..."
pip install -r requirements.txt

echo "🔧 Setting up environment..."
# Create default .env if it doesn't exist (will be overridden by Render env vars)
if [ ! -f .env ]; then
    echo "Creating default .env file..."
    cat > .env << EOL
MONGO_URL=mongodb://localhost:27017
DB_NAME=squiz_production
JWT_SECRET=default-secret-change-in-production
EOL
fi

echo "✅ Backend build completed successfully!"
echo "Backend is ready for deployment on Render.com"