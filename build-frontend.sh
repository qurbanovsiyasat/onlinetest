#!/bin/bash

# Build script for Render.com frontend deployment

echo "🚀 Starting Squiz Frontend Build Process..."

# Navigate to frontend directory
cd frontend

echo "📦 Installing Node.js dependencies..."
yarn install --frozen-lockfile

echo "🔧 Setting up environment..."
# Create default .env if it doesn't exist (will be overridden by Render env vars)
if [ ! -f .env ]; then
    echo "Creating default .env file..."
    cat > .env << EOL
REACT_APP_BACKEND_URL=http://localhost:8001
GENERATE_SOURCEMAP=false
CI=false
EOL
fi

echo "🏗️  Building React application..."
yarn build

# Verify build was successful
if [ -d "build" ]; then
    echo "✅ Build folder created successfully!"
    echo "📊 Build statistics:"
    du -sh build/
    echo "📁 Build contents:"
    ls -la build/
else
    echo "❌ Build failed - no build folder found!"
    exit 1
fi

echo "✅ Frontend build completed successfully!"
echo "Frontend is ready for deployment on Render.com"