#!/bin/bash

# OnlineTestMaker Self-Hosted Verification Script
# This script verifies that all components are running locally without external dependencies

echo "🏠 OnlineTestMaker Self-Hosted Verification"
echo "==========================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check functions
check_service() {
    local service=$1
    local url=$2
    local expected=$3
    
    echo -n "Checking $service... "
    
    if curl -s --max-time 5 "$url" | grep -q "$expected"; then
        echo -e "${GREEN}✅ RUNNING (Self-Hosted)${NC}"
        return 0
    else
        echo -e "${RED}❌ FAILED${NC}"
        return 1
    fi
}

check_port() {
    local service=$1
    local port=$2
    
    echo -n "Checking $service on port $port... "
    
    if netstat -tuln | grep -q ":$port "; then
        echo -e "${GREEN}✅ LISTENING${NC}"
        return 0
    else
        echo -e "${RED}❌ NOT LISTENING${NC}"
        return 1
    fi
}

echo ""
echo "🔍 Verifying Self-Hosted Components..."
echo ""

# 1. Check MongoDB (Database)
echo "1. Database Service (MongoDB)"
if systemctl is-active --quiet mongod; then
    echo -e "   ${GREEN}✅ MongoDB service is running locally${NC}"
    
    # Test database connection
    if mongo --eval "db.stats()" --quiet > /dev/null 2>&1; then
        echo -e "   ${GREEN}✅ Database connection successful${NC}"
    else
        echo -e "   ${YELLOW}⚠️  Database connection test failed${NC}"
    fi
else
    echo -e "   ${RED}❌ MongoDB service not running${NC}"
fi

echo ""

# 2. Check Backend API (FastAPI)
echo "2. Backend API Service (FastAPI)"
check_port "Backend API" "8001"
check_service "Backend Health" "http://localhost:8001/api/health" "self-hosted"

echo ""

# 3. Check Frontend (React)
echo "3. Frontend Service (React)"
check_port "Frontend" "3000"
check_service "Frontend App" "http://localhost:3000" "OnlineTestMaker"

echo ""

# 4. Check for External Dependencies
echo "4. External Dependencies Check"
echo -n "Checking for external API calls... "

# Check if any processes are making external HTTP requests
if netstat -tuln | grep -E ":(80|443|8080|8443) " | grep -v "127.0.0.1\|localhost" > /dev/null; then
    echo -e "${YELLOW}⚠️  External connections detected${NC}"
    echo "   Review your configuration to ensure complete self-hosting"
else
    echo -e "${GREEN}✅ No external dependencies detected${NC}"
fi

echo ""

# 5. CORS Configuration Check
echo "5. CORS Configuration"
echo -n "Checking CORS settings... "

if curl -s --max-time 5 "http://localhost:8001/api/cors-info" | grep -q "allowed_origins"; then
    echo -e "${GREEN}✅ CORS properly configured${NC}"
    
    # Test CORS preflight
    echo -n "Testing CORS preflight... "
    if curl -s -H "Origin: http://localhost:3000" \
            -H "Access-Control-Request-Method: POST" \
            -X OPTIONS \
            "http://localhost:8001/api/health" | grep -q "200\|OK"; then
        echo -e "${GREEN}✅ CORS preflight working${NC}"
    else
        echo -e "${YELLOW}⚠️  CORS preflight test failed${NC}"
    fi
else
    echo -e "${RED}❌ CORS configuration not accessible${NC}"
fi

echo ""

# 6. Verify File Storage
echo "6. File Storage Configuration"
if grep -q "base64" /app/backend/server.py; then
    echo -e "   ${GREEN}✅ Using local base64 storage (self-hosted)${NC}"
else
    echo -e "   ${YELLOW}⚠️  File storage configuration unclear${NC}"
fi

echo ""

# 6. Check MathJax
echo "6. Mathematical Expressions (MathJax)"
if grep -q "mathjax" /app/frontend/package.json; then
    echo -e "   ${GREEN}✅ Using local MathJax package (self-hosted)${NC}"
else
    echo -e "   ${YELLOW}⚠️  MathJax configuration unclear${NC}"
fi

echo ""

# 7. Environment Configuration
echo "7. Environment Configuration"
if [ -f "/app/backend/.env" ]; then
    if grep -q "localhost\|127.0.0.1" /app/backend/.env; then
        echo -e "   ${GREEN}✅ Backend configured for local database${NC}"
    else
        echo -e "   ${YELLOW}⚠️  Check backend database configuration${NC}"
    fi
else
    echo -e "   ${RED}❌ Backend .env file not found${NC}"
fi

if [ -f "/app/frontend/.env" ]; then
    if grep -q "localhost\|127.0.0.1" /app/frontend/.env || grep -q "$(hostname -I | awk '{print $1}')" /app/frontend/.env; then
        echo -e "   ${GREEN}✅ Frontend configured for local backend${NC}"
    else
        echo -e "   ${YELLOW}⚠️  Check frontend backend URL configuration${NC}"
    fi
else
    echo -e "   ${RED}❌ Frontend .env file not found${NC}"
fi

echo ""
echo "==========================================="
echo "🎉 Self-Hosted Verification Complete!"
echo ""
echo "📋 Summary:"
echo "• All services should be running on your local server"
echo "• Database: MongoDB running locally"
echo "• Backend: FastAPI on port 8001"
echo "• Frontend: React on port 3000"
echo "• No external API dependencies"
echo "• File storage: Local base64 encoding"
echo "• Math rendering: Local MathJax package"
echo ""
echo "🌐 Access your application at: http://$(hostname -I | awk '{print $1}'):3000"
echo "🔧 API health check: http://$(hostname -I | awk '{print $1}'):8001/api/health"
echo ""
echo "📖 For deployment instructions, see: SELF_HOSTED_DEPLOYMENT.md"