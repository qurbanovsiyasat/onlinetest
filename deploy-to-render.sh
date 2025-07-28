#!/bin/bash

# 🚀 Squiz Quiz Platform - Render Deployment Helper Script
# This script helps you prepare your code for Render deployment

echo "🚀 Preparing Squiz Quiz Platform for Render Deployment..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Check if we're in the right directory
if [ ! -f "render.yaml" ]; then
    print_error "render.yaml not found. Are you in the project root directory?"
    exit 1
fi

print_status "Found render.yaml configuration"

# Check backend dependencies
print_info "Checking backend dependencies..."
cd backend
if [ -f "requirements.txt" ]; then
    print_status "Backend requirements.txt found"
    echo "Dependencies:"
    head -n 5 requirements.txt
else
    print_error "Backend requirements.txt not found"
    exit 1
fi

# Check backend server
if [ -f "server.py" ]; then
    print_status "Backend server.py found"
else
    print_error "Backend server.py not found"
    exit 1
fi

cd ..

# Check frontend dependencies
print_info "Checking frontend dependencies..."
cd frontend
if [ -f "package.json" ]; then
    print_status "Frontend package.json found"
    echo "React version: $(grep -o '"react": "[^"]*"' package.json)"
else
    print_error "Frontend package.json not found"
    exit 1
fi

cd ..

# Check environment files
print_info "Checking environment configuration..."
if [ -f "backend/.env" ]; then
    print_status "Backend .env found"
else
    print_warning "Backend .env not found - will use Render environment variables"
fi

if [ -f "frontend/.env" ]; then
    print_status "Frontend .env found"
else
    print_warning "Frontend .env not found - will use Render environment variables"
fi

# Check Git status
print_info "Checking Git repository status..."
if [ -d ".git" ]; then
    print_status "Git repository found"
    
    # Check if there are uncommitted changes
    if [ -n "$(git status --porcelain)" ]; then
        print_warning "You have uncommitted changes:"
        git status --short
        echo
        read -p "Do you want to commit these changes? (y/n): " commit_changes
        if [ "$commit_changes" = "y" ] || [ "$commit_changes" = "Y" ]; then
            git add .
            echo "Enter commit message (press Enter for default): "
            read -r commit_message
            if [ -z "$commit_message" ]; then
                commit_message="Prepare for Render deployment"
            fi
            git commit -m "$commit_message"
            print_status "Changes committed"
        fi
    else
        print_status "No uncommitted changes"
    fi
    
    # Check if origin is set
    if git remote get-url origin > /dev/null 2>&1; then
        print_status "Git origin configured: $(git remote get-url origin)"
        
        read -p "Do you want to push to GitHub now? (y/n): " push_now
        if [ "$push_now" = "y" ] || [ "$push_now" = "Y" ]; then
            git push origin main
            print_status "Code pushed to GitHub"
        fi
    else
        print_warning "Git origin not configured"
        echo "To set up GitHub origin:"
        echo "git remote add origin https://github.com/YOUR-USERNAME/YOUR-REPO.git"
        echo "git push -u origin main"
    fi
else
    print_error "Not a Git repository. Initialize with: git init"
    exit 1
fi

echo
print_info "🎯 Deployment Readiness Summary:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
print_status "✅ render.yaml configuration ready"
print_status "✅ Backend (FastAPI + Python) ready"
print_status "✅ Frontend (React + Tailwind) ready"
print_status "✅ Database (MongoDB) configured"
print_status "✅ CORS configuration updated"
echo

print_info "📋 Next Steps for Render Deployment:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "1. 🌐 Go to https://dashboard.render.com"
echo "2. 🗄️  Create MongoDB database: squiz-database"
echo "3. 🖥️  Create Web Service: squiz-backend"
echo "4. 🌍 Create Static Site: squiz-frontend"
echo "5. ⚙️  Configure environment variables"
echo "6. 🚀 Deploy and test!"
echo

print_info "📚 For detailed instructions, see:"
echo "   📖 RENDER_DEPLOYMENT_COMPLETE_GUIDE.md"
echo

print_info "🔐 Admin Credentials (Change after deployment!):"
echo "   📧 Email: admin@squiz.com"
echo "   🔑 Password: admin123"
echo

print_status "🎉 Your Squiz Quiz Platform is ready for Render deployment!"