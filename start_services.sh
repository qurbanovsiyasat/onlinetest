#!/bin/bash

# OnlineTestMaker Self-Hosted Startup Script
# This script helps initialize and start your OnlineTestMaker instance

set -e  # Exit on any error

echo "🏠 OnlineTestMaker Self-Hosted Startup"
echo "======================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
BACKEND_DIR="./backend"
FRONTEND_DIR="./frontend"
MONGO_PORT=27017
BACKEND_PORT=8001
FRONTEND_PORT=3000

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check if a port is in use
port_in_use() {
    lsof -Pi :$1 -sTCP:LISTEN -t >/dev/null 2>&1
}

# Function to wait for service to be ready
wait_for_service() {
    local service=$1
    local url=$2
    local max_attempts=30
    local attempt=1
    
    echo -n "Waiting for $service to be ready"
    while [ $attempt -le $max_attempts ]; do
        if curl -s "$url" >/dev/null 2>&1; then
            echo -e " ${GREEN}✅ Ready!${NC}"
            return 0
        fi
        echo -n "."
        sleep 2
        attempt=$((attempt + 1))
    done
    echo -e " ${RED}❌ Timeout${NC}"
    return 1
}

# Function to get local IP address
get_local_ip() {
    # Try different methods to get local IP
    if command_exists hostname; then
        hostname -I | awk '{print $1}' 2>/dev/null || echo "127.0.0.1"
    elif command_exists ip; then
        ip route get 1 | awk '{print $7}' 2>/dev/null || echo "127.0.0.1"
    else
        echo "127.0.0.1"
    fi
}

echo ""
echo "🔍 Checking Prerequisites..."
echo ""

# Check for required commands
MISSING_DEPS=()

if ! command_exists node; then
    MISSING_DEPS+=("Node.js")
fi

if ! command_exists npm && ! command_exists yarn; then
    MISSING_DEPS+=("npm or yarn")
fi

if ! command_exists python3; then
    MISSING_DEPS+=("Python 3")
fi

if ! command_exists pip3; then
    MISSING_DEPS+=("pip3")
fi

if ! command_exists mongod; then
    MISSING_DEPS+=("MongoDB")
fi

if [ ${#MISSING_DEPS[@]} -gt 0 ]; then
    echo -e "${RED}❌ Missing required dependencies:${NC}"
    for dep in "${MISSING_DEPS[@]}"; do
        echo "   - $dep"
    done
    echo ""
    echo "Please install the missing dependencies and run this script again."
    exit 1
fi

echo -e "${GREEN}✅ All prerequisites found${NC}"
echo ""

# Check if MongoDB is running
echo "🗄️  Checking MongoDB..."
if port_in_use $MONGO_PORT; then
    echo -e "${GREEN}✅ MongoDB is running on port $MONGO_PORT${NC}"
else
    echo -e "${YELLOW}⚠️  MongoDB not running, attempting to start...${NC}"
    
    # Try to start MongoDB
    if command_exists systemctl; then
        sudo systemctl start mongod
        sleep 3
        if port_in_use $MONGO_PORT; then
            echo -e "${GREEN}✅ MongoDB started successfully${NC}"
        else
            echo -e "${RED}❌ Failed to start MongoDB via systemctl${NC}"
            exit 1
        fi
    elif command_exists brew; then
        brew services start mongodb/brew/mongodb-community
        sleep 3
        if port_in_use $MONGO_PORT; then
            echo -e "${GREEN}✅ MongoDB started successfully${NC}"
        else
            echo -e "${RED}❌ Failed to start MongoDB via brew${NC}"
            exit 1
        fi
    else
        echo -e "${RED}❌ Please start MongoDB manually${NC}"
        exit 1
    fi
fi

echo ""

# Setup backend
echo "🔧 Setting up Backend..."
if [ ! -d "$BACKEND_DIR" ]; then
    echo -e "${RED}❌ Backend directory not found: $BACKEND_DIR${NC}"
    exit 1
fi

cd "$BACKEND_DIR"

# Check if .env exists, if not copy from template
if [ ! -f ".env" ]; then
    if [ -f ".env.template" ]; then
        echo -e "${YELLOW}⚠️  .env not found, copying from template...${NC}"
        cp .env.template .env
        echo -e "${GREEN}✅ .env created from template${NC}"
        echo -e "${YELLOW}📝 Please edit .env file to configure your settings${NC}"
    else
        echo -e "${YELLOW}⚠️  Creating basic .env file...${NC}"
        cat > .env << EOF
MONGO_URL="mongodb://localhost:27017"
DB_NAME="onlinetestmaker_db"
JWT_SECRET="OnlineTestMaker_Self_Hosted_Secret_2025_CHANGE_THIS"
ALLOWED_ORIGINS="http://localhost:3000,http://127.0.0.1:3000"
HOST="0.0.0.0"
PORT="8001"
SELF_HOSTED="true"
EOF
        echo -e "${GREEN}✅ Basic .env created${NC}"
    fi
fi

# Install Python dependencies
if [ -f "requirements.txt" ]; then
    echo "📦 Installing Python dependencies..."
    pip3 install -r requirements.txt
    echo -e "${GREEN}✅ Python dependencies installed${NC}"
else
    echo -e "${YELLOW}⚠️  requirements.txt not found${NC}"
fi

# Start backend server
echo "🚀 Starting Backend Server..."
if port_in_use $BACKEND_PORT; then
    echo -e "${YELLOW}⚠️  Port $BACKEND_PORT is already in use${NC}"
    echo "   Attempting to stop existing process..."
    pkill -f "uvicorn.*server:app" || true
    sleep 2
fi

# Start backend in background
nohup python3 -m uvicorn server:app --host 0.0.0.0 --port $BACKEND_PORT --reload > ../backend.log 2>&1 &
BACKEND_PID=$!
echo "Backend started with PID: $BACKEND_PID"

# Wait for backend to be ready
if wait_for_service "Backend API" "http://localhost:$BACKEND_PORT/api/health"; then
    echo -e "${GREEN}✅ Backend server is running${NC}"
else
    echo -e "${RED}❌ Backend server failed to start${NC}"
    echo "Check backend.log for details"
    exit 1
fi

cd ..

# Setup frontend
echo ""
echo "🎨 Setting up Frontend..."
if [ ! -d "$FRONTEND_DIR" ]; then
    echo -e "${RED}❌ Frontend directory not found: $FRONTEND_DIR${NC}"
    exit 1
fi

cd "$FRONTEND_DIR"

# Check if .env exists, if not copy from template
if [ ! -f ".env" ]; then
    LOCAL_IP=$(get_local_ip)
    if [ -f ".env.template" ]; then
        echo -e "${YELLOW}⚠️  .env not found, copying from template...${NC}"
        cp .env.template .env
        # Update backend URL to use local IP
        sed -i.bak "s|http://localhost:8001|http://$LOCAL_IP:8001|g" .env
        echo -e "${GREEN}✅ .env created and configured for local IP: $LOCAL_IP${NC}"
    else
        echo -e "${YELLOW}⚠️  Creating basic .env file...${NC}"
        cat > .env << EOF
REACT_APP_BACKEND_URL=http://localhost:8001
GENERATE_SOURCEMAP=false
BROWSER=none
EOF
        echo -e "${GREEN}✅ Basic .env created${NC}"
    fi
fi

# Install Node.js dependencies
if [ -f "package.json" ]; then
    echo "📦 Installing Node.js dependencies..."
    if command_exists yarn; then
        yarn install
    else
        npm install
    fi
    echo -e "${GREEN}✅ Node.js dependencies installed${NC}"
else
    echo -e "${RED}❌ package.json not found${NC}"
    exit 1
fi

# Start frontend server
echo "🚀 Starting Frontend Server..."
if port_in_use $FRONTEND_PORT; then
    echo -e "${YELLOW}⚠️  Port $FRONTEND_PORT is already in use${NC}"
    echo "   Attempting to stop existing process..."
    pkill -f "react-scripts start\|craco start" || true
    sleep 2
fi

# Start frontend in background
if command_exists yarn; then
    nohup yarn start > ../frontend.log 2>&1 &
else
    nohup npm start > ../frontend.log 2>&1 &
fi
FRONTEND_PID=$!
echo "Frontend started with PID: $FRONTEND_PID"

# Wait for frontend to be ready
if wait_for_service "Frontend App" "http://localhost:$FRONTEND_PORT"; then
    echo -e "${GREEN}✅ Frontend server is running${NC}"
else
    echo -e "${RED}❌ Frontend server failed to start${NC}"
    echo "Check frontend.log for details"
    exit 1
fi

cd ..

# Initialize admin user
echo ""
echo "👤 Initializing Admin User..."
ADMIN_RESPONSE=$(curl -s -X POST "http://localhost:$BACKEND_PORT/api/init-admin" -H "Content-Type: application/json")

if echo "$ADMIN_RESPONSE" | grep -q "Admin already exists"; then
    echo -e "${YELLOW}⚠️  Admin user already exists${NC}"
elif echo "$ADMIN_RESPONSE" | grep -q "created successfully"; then
    echo -e "${GREEN}✅ Admin user created successfully${NC}"
    echo ""
    echo "📧 Admin Login Credentials:"
    echo "   Email: admin@onlinetestmaker.com"
    echo "   Password: admin123"
    echo -e "${YELLOW}   ⚠️  Please change the password after first login!${NC}"
else
    echo -e "${YELLOW}⚠️  Could not initialize admin user automatically${NC}"
    echo "   You can do this manually by visiting: http://localhost:$BACKEND_PORT/api/init-admin"
fi

# Save PIDs for cleanup
echo "$BACKEND_PID" > backend.pid
echo "$FRONTEND_PID" > frontend.pid

# Get network information
LOCAL_IP=$(get_local_ip)

echo ""
echo "=========================================="
echo -e "${GREEN}🎉 OnlineTestMaker Started Successfully!${NC}"
echo "=========================================="
echo ""
echo "📍 Access URLs:"
echo "   🌐 Frontend (Web App): http://localhost:$FRONTEND_PORT"
echo "   🔧 Backend API: http://localhost:$BACKEND_PORT"
echo "   📚 API Documentation: http://localhost:$BACKEND_PORT/docs"
echo ""
if [ "$LOCAL_IP" != "127.0.0.1" ]; then
    echo "📡 Network Access (Local Network):"
    echo "   🌐 Frontend: http://$LOCAL_IP:$FRONTEND_PORT"
    echo "   🔧 Backend: http://$LOCAL_IP:$BACKEND_PORT"
    echo ""
fi
echo "👤 Admin Credentials:"
echo "   📧 Email: admin@onlinetestmaker.com"
echo "   🔑 Password: admin123"
echo ""
echo "📋 Features Available:"
echo "   ✅ Subject folder organization"
echo "   ✅ Multiple question types (MC, Open-ended)"
echo "   ✅ File uploads (Images, PDFs)"
echo "   ✅ Mathematical expressions (MathJax)"
echo "   ✅ Mobile responsive design"
echo "   ✅ Advanced grading system"
echo "   ✅ Analytics dashboard"
echo "   ✅ User access control"
echo ""
echo "🔒 Security:"
echo "   ✅ Fully self-hosted - no external dependencies"
echo "   ✅ Local MongoDB database"
echo "   ✅ JWT-based authentication"
echo "   ✅ Base64 file storage (no cloud services)"
echo ""
echo "📝 Log Files:"
echo "   Backend: backend.log"
echo "   Frontend: frontend.log"
echo ""
echo "🛑 To stop the services:"
echo "   ./stop_services.sh"
echo ""
echo -e "${BLUE}Happy quiz making! 🚀${NC}"

# Create stop script
cat > stop_services.sh << 'EOF'
#!/bin/bash

echo "🛑 Stopping OnlineTestMaker services..."

# Read PIDs
if [ -f "backend.pid" ]; then
    BACKEND_PID=$(cat backend.pid)
    if kill -0 $BACKEND_PID 2>/dev/null; then
        echo "Stopping backend (PID: $BACKEND_PID)..."
        kill $BACKEND_PID
        rm -f backend.pid
    fi
fi

if [ -f "frontend.pid" ]; then
    FRONTEND_PID=$(cat frontend.pid)
    if kill -0 $FRONTEND_PID 2>/dev/null; then
        echo "Stopping frontend (PID: $FRONTEND_PID)..."
        kill $FRONTEND_PID
        rm -f frontend.pid
    fi
fi

# Clean up any remaining processes
pkill -f "uvicorn.*server:app" || true
pkill -f "react-scripts start\|craco start" || true

echo "✅ Services stopped"
EOF

chmod +x stop_services.sh

echo "Created stop_services.sh script for easy shutdown"