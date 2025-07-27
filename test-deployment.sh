#!/bin/bash

# Test script to verify deployment readiness

echo "🧪 Testing Squiz Platform Deployment Readiness..."
echo "=================================================="

# Test backend dependencies
echo "📦 Testing Backend Dependencies..."
cd backend
if pip install -r requirements.txt --dry-run > /dev/null 2>&1; then
    echo "✅ Backend dependencies are valid"
else
    echo "❌ Backend dependencies have issues"
    exit 1
fi

# Test backend startup (quick test)
echo "🚀 Testing Backend Startup..."
python -c "
import sys
sys.path.append('.')
try:
    from server import app
    print('✅ Backend imports successfully')
except Exception as e:
    print(f'❌ Backend import failed: {e}')
    sys.exit(1)
"

cd ..

# Test frontend dependencies
echo "📦 Testing Frontend Dependencies..."
cd frontend
if yarn install --check-files > /dev/null 2>&1; then
    echo "✅ Frontend dependencies are valid"
else
    echo "❌ Frontend dependencies have issues"
    exit 1
fi

# Test frontend build
echo "🏗️  Testing Frontend Build..."
if yarn build > /dev/null 2>&1; then
    echo "✅ Frontend builds successfully"
    if [ -d "build" ]; then
        BUILD_SIZE=$(du -sh build | cut -f1)
        echo "📊 Build size: $BUILD_SIZE"
        echo "📁 Build files:"
        ls -la build/ | head -10
    fi
else
    echo "❌ Frontend build failed"
    exit 1
fi

cd ..

# Check required files
echo "📋 Checking Deployment Files..."
REQUIRED_FILES=(
    "ADMIN_CREDENTIALS.md"
    "RENDER_DEPLOYMENT_GUIDE.md"
    "DEPLOYMENT_CHECKLIST.md"
    "render.yaml"
    "build-backend.sh"
    "build-frontend.sh"
)

for file in "${REQUIRED_FILES[@]}"; do
    if [ -f "$file" ]; then
        echo "✅ $file exists"
    else
        echo "❌ $file missing"
        exit 1
    fi
done

echo ""
echo "🎉 DEPLOYMENT READINESS CHECK COMPLETE!"
echo "=================================================="
echo "✅ All tests passed - Ready for Render.com deployment"
echo ""
echo "📚 Next Steps:"
echo "1. Push code to GitHub"
echo "2. Follow DEPLOYMENT_CHECKLIST.md"
echo "3. Create services on Render.com"
echo "4. Configure environment variables"
echo "5. Deploy and test!"
echo ""
echo "🔐 Admin Credentials (change after deployment):"
echo "   Email: admin@squiz.com"
echo "   Password: admin123"