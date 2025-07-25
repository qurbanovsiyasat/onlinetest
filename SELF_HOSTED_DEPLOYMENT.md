# 🏠 Complete Self-Hosted Deployment Guide

## OnlineTestMaker - Fully Self-Hosted Setup

This guide ensures **ALL** backend services, APIs, database connections, and media handling run entirely on your server infrastructure without any external dependencies.

---

## 🛠️ **Server Requirements**

### Minimum Hardware:
- **CPU**: 2 cores (4 recommended)
- **RAM**: 4GB (8GB recommended)
- **Storage**: 20GB available space
- **Network**: Internet connection for initial setup only

### Software Requirements:
- **OS**: Ubuntu 20.04+ / CentOS 8+ / RHEL 8+
- **Node.js**: v16+ 
- **Python**: 3.8+
- **MongoDB**: 4.4+

---

## 📦 **Complete Installation**

### 1. Install System Dependencies
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install -y nodejs npm python3 python3-pip mongodb supervisor nginx

# CentOS/RHEL
sudo dnf install -y nodejs npm python3 python3-pip mongodb-server supervisor nginx
```

### 2. Install Application Dependencies
```bash
# Backend Dependencies
cd /app/backend
pip3 install -r requirements.txt

# Frontend Dependencies  
cd /app/frontend
npm install -g yarn
yarn install
```

### 3. Build Frontend for Production
```bash
cd /app/frontend
yarn build
```

---

## 🗄️ **Database Setup (Self-Hosted MongoDB)**

### 1. Configure MongoDB
```bash
# Start MongoDB service
sudo systemctl start mongod
sudo systemctl enable mongod

# Verify MongoDB is running
sudo systemctl status mongod
```

### 2. Create Database and Admin User
```bash
# Connect to MongoDB
mongo

# Create admin user (run in mongo shell)
use admin
db.createUser({
  user: "onlinetestmaker_admin",
  pwd: "your_secure_password_here",
  roles: ["readWriteAnyDatabase", "dbAdminAnyDatabase"]
})

# Create application database
use onlinetestmaker_db
```

### 3. Update Environment Variables
```bash
# Backend environment
cat > /app/backend/.env << EOF
MONGO_URL="mongodb://onlinetestmaker_admin:your_secure_password_here@localhost:27017/onlinetestmaker_db"
DB_NAME="onlinetestmaker_db"
JWT_SECRET="your_jwt_secret_key_here"
EOF

# Frontend environment  
cat > /app/frontend/.env << EOF
REACT_APP_BACKEND_URL=http://your-server-ip:8001
EOF
```

---

## 🚀 **Application Deployment**

### 1. Configure Supervisor (Process Management)
```bash
# Create supervisor configuration
cat > /etc/supervisor/conf.d/onlinetestmaker.conf << EOF
[program:onlinetestmaker_backend]
command=python3 -m uvicorn server:app --host 0.0.0.0 --port 8001
directory=/app/backend
user=root
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/onlinetestmaker_backend.log

[program:onlinetestmaker_frontend]
command=npx serve -s build -l 3000
directory=/app/frontend
user=root
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/onlinetestmaker_frontend.log
EOF
```

### 2. Configure Nginx (Reverse Proxy)
```bash
# Create nginx configuration
cat > /etc/nginx/sites-available/onlinetestmaker << EOF
server {
    listen 80;
    server_name your-domain.com your-server-ip;

    # Frontend
    location / {
        proxy_pass http://localhost:3000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }

    # Backend API
    location /api/ {
        proxy_pass http://localhost:8001;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }

    # File upload limits
    client_max_body_size 10M;
}
EOF

# Enable the site
ln -s /etc/nginx/sites-available/onlinetestmaker /etc/nginx/sites-enabled/
nginx -t
systemctl reload nginx
```

### 3. Start All Services
```bash
# Reload supervisor configuration
supervisorctl reread
supervisorctl update

# Start applications
supervisorctl start onlinetestmaker_backend
supervisorctl start onlinetestmaker_frontend

# Verify services are running
supervisorctl status
```

---

## 🔐 **Security Configuration**

### 1. Firewall Setup
```bash
# Ubuntu UFW
ufw allow 22
ufw allow 80
ufw allow 443
ufw enable

# CentOS Firewalld
firewall-cmd --permanent --add-port=22/tcp
firewall-cmd --permanent --add-port=80/tcp
firewall-cmd --permanent --add-port=443/tcp
firewall-cmd --reload
```

### 2. SSL Certificate (Optional)
```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx

# Get SSL certificate
certbot --nginx -d your-domain.com
```

---

## 📁 **File Storage Configuration**

### Current Setup (Base64 - Suitable for MVP):
- Images and PDFs stored as base64 in MongoDB
- No external file storage dependencies
- Automatic cleanup when items are deleted

### Production Upgrade (Local File Storage):
```python
# Optional: Update backend/server.py for local file storage
UPLOAD_DIR = "/app/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Create upload directory
mkdir -p /app/uploads
chown -R www-data:www-data /app/uploads
```

---

## 🔧 **Self-Hosted Features Verified**

### ✅ **Complete Self-Hosting Checklist:**
- [x] **FastAPI Backend**: Runs on your server (port 8001)
- [x] **React Frontend**: Built and served locally (port 3000)  
- [x] **MongoDB Database**: Local instance with authentication
- [x] **File Uploads**: Base64 storage (no external services)
- [x] **Mathematical Expressions**: Local MathJax (no CDN)
- [x] **Authentication**: Local JWT with your secret keys
- [x] **Image Processing**: Local react-image-crop library
- [x] **All APIs**: Self-hosted FastAPI endpoints
- [x] **Media Handling**: Local base64 encoding/decoding
- [x] **No External Dependencies**: Everything runs on your infrastructure

---

## 🚨 **Important Notes**

### 1. **No External Calls**
- All API calls go to your local backend
- No third-party API dependencies  
- No external authentication services
- No cloud storage requirements

### 2. **Data Privacy**
- All user data stays on your server
- No data transmitted to external services
- Complete control over data retention and backup

### 3. **Scalability**
- Can be deployed on multiple servers
- Database can be clustered if needed
- Load balancing can be added with nginx

---

## 🔍 **Monitoring & Maintenance**

### Log Files:
- Backend: `/var/log/onlinetestmaker_backend.log`
- Frontend: `/var/log/onlinetestmaker_frontend.log`
- Nginx: `/var/log/nginx/access.log`, `/var/log/nginx/error.log`
- MongoDB: `/var/log/mongodb/mongod.log`

### Service Management:
```bash
# Check service status
supervisorctl status

# Restart services
supervisorctl restart onlinetestmaker_backend
supervisorctl restart onlinetestmaker_frontend

# View logs
tail -f /var/log/onlinetestmaker_backend.log
```

---

## ✅ **Deployment Verification**

1. **Backend API**: `curl http://your-server-ip:8001/api/health`
2. **Frontend**: Open `http://your-server-ip` in browser
3. **Database**: `mongo --eval "db.stats()"`
4. **File Uploads**: Test image upload in quiz creation
5. **Mathematical Expressions**: Test $x^2$ rendering

---

**🎉 Your OnlineTestMaker platform is now completely self-hosted!**

All backend services, APIs, database connections, and media handling run entirely on your server infrastructure with zero external dependencies.