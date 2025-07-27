# 🌐 CORS Configuration Guide for Self-Hosted OnlineTestMaker

## Understanding CORS in Self-Hosted Environments

**CORS (Cross-Origin Resource Sharing)** is a browser security feature that restricts web applications running on one origin (domain/port) from requesting resources from another origin unless explicitly allowed by the server.

---

## 🎯 **Common CORS Scenarios in Self-Hosted Deployments**

### **Scenario 1: Development (Different Ports)**
- Frontend: `http://localhost:3000`
- Backend: `http://localhost:8001`
- **Issue**: Browser blocks requests between different ports
- **Status**: ✅ **CONFIGURED** - Automatically handled

### **Scenario 2: Production (Same Server, Different Ports)**
- Frontend: `http://192.168.1.100:3000`
- Backend: `http://192.168.1.100:8001`
- **Issue**: Need to add server IP to allowed origins
- **Status**: ✅ **CONFIGURED** - Auto-detects server IP

### **Scenario 3: Production (Domain + Reverse Proxy)**
- Frontend: `https://yourdomain.com`
- Backend: `https://yourdomain.com/api`
- **Issue**: Need to configure domain in CORS
- **Status**: ✅ **CONFIGURABLE** - Update environment

---

## 🔧 **CORS Configuration**

### **Automatic Configuration**
The OnlineTestMaker backend automatically includes these origins:
- `http://localhost:3000` (development)
- `http://127.0.0.1:3000` (local testing)
- `http://[SERVER_IP]:3000` (production)
- `https://[SERVER_IP]:3000` (HTTPS production)

### **Manual Configuration**
Add custom origins via environment variable:

```bash
# In /app/backend/.env
ALLOWED_ORIGINS="https://yourdomain.com,https://www.yourdomain.com,http://192.168.1.100:3000"
```

---

## 🚨 **Troubleshooting CORS Issues**

### **1. Check CORS Configuration**
```bash
# Test CORS info endpoint
curl http://localhost:8001/api/cors-info
```

### **2. Browser Console Errors**
Look for these error messages:
```
Access to fetch at 'http://localhost:8001/api/...' from origin 'http://localhost:3000' 
has been blocked by CORS policy: No 'Access-Control-Allow-Origin' header is present
```

### **3. Common Solutions**

#### **Solution A: Add Your Domain/IP**
```bash
# Add your server IP or domain to .env
echo "ALLOWED_ORIGINS=http://YOUR_SERVER_IP:3000,https://yourdomain.com" >> /app/backend/.env
sudo supervisorctl restart onlinetestmaker_backend
```

#### **Solution B: Check Network Configuration**
```bash
# Verify frontend can reach backend
curl -I http://localhost:8001/api/health

# Check from frontend server
curl -I http://BACKEND_IP:8001/api/health
```

#### **Solution C: Browser Testing**
```bash
# Test with curl (bypasses CORS)
curl -X POST http://localhost:8001/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@onlinetestmaker.com","password":"admin123"}'
```

---

## 📊 **CORS Headers Explained**

### **Request Headers (Browser → Backend)**
- `Origin`: Where the request is coming from
- `Access-Control-Request-Method`: HTTP method for preflight
- `Access-Control-Request-Headers`: Headers for preflight

### **Response Headers (Backend → Browser)**
- `Access-Control-Allow-Origin`: Allowed origins
- `Access-Control-Allow-Methods`: Allowed HTTP methods
- `Access-Control-Allow-Headers`: Allowed request headers
- `Access-Control-Allow-Credentials`: Allow cookies/auth

---

## 🔍 **Debugging Commands**

### **1. Test CORS Headers**
```bash
# Check CORS response headers
curl -H "Origin: http://localhost:3000" \
     -H "Access-Control-Request-Method: POST" \
     -H "Access-Control-Request-Headers: Content-Type,Authorization" \
     -X OPTIONS \
     http://localhost:8001/api/auth/login -v
```

### **2. Test from Browser Console**
```javascript
// Test API call from browser
fetch('http://localhost:8001/api/health')
  .then(response => response.json())
  .then(data => console.log(data))
  .catch(error => console.error('CORS Error:', error));
```

### **3. Check Network Tab**
1. Open browser DevTools (F12)
2. Go to Network tab
3. Make a request
4. Check response headers for `Access-Control-*`

---

## 🏗️ **Production Deployment Patterns**

### **Pattern 1: Reverse Proxy (Recommended)**
```nginx
# /etc/nginx/sites-available/onlinetestmaker
server {
    listen 80;
    server_name yourdomain.com;
    
    location / {
        proxy_pass http://localhost:3000;
    }
    
    location /api/ {
        proxy_pass http://localhost:8001;
    }
}
```
**CORS**: Not needed (same origin)

### **Pattern 2: Different Ports**
- Frontend: `http://yourdomain.com:3000`
- Backend: `http://yourdomain.com:8001`
- **CORS**: Required (different ports = different origins)

### **Pattern 3: Subdomain**
- Frontend: `https://app.yourdomain.com`
- Backend: `https://api.yourdomain.com`
- **CORS**: Required (different subdomains = different origins)

---

## ✅ **Quick CORS Fixes**

### **Fix 1: Permissive (Development Only)**
```bash
# WARNING: Only for development!
echo "ALLOWED_ORIGINS=*" >> /app/backend/.env
sudo supervisorctl restart onlinetestmaker_backend
```

### **Fix 2: Specific Origins (Production)**
```bash
# Add your specific domains
echo "ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com" >> /app/backend/.env
sudo supervisorctl restart onlinetestmaker_backend
```

### **Fix 3: Local Network**
```bash
# For local network deployment
SERVER_IP=$(hostname -I | awk '{print $1}')
echo "ALLOWED_ORIGINS=http://$SERVER_IP:3000,https://$SERVER_IP:3000" >> /app/backend/.env
sudo supervisorctl restart onlinetestmaker_backend
```

---

## 🔒 **Security Best Practices**

### **✅ Do:**
- Use specific domains instead of `*`
- Use HTTPS in production
- Validate origins server-side
- Set appropriate cache times
- Use Content Security Policy (CSP)

### **❌ Don't:**
- Use `allow_origins=["*"]` in production
- Allow `null` origin
- Expose sensitive headers
- Set overly long cache times
- Ignore preflight requests

---

## 🛠️ **Testing Your CORS Setup**

```bash
# Run the CORS verification script
./verify_self_hosted.sh

# Check CORS endpoints
curl http://localhost:8001/api/cors-info
curl http://localhost:8001/api/health

# Test from your frontend URL
curl -H "Origin: http://YOUR_FRONTEND_URL" \
     http://localhost:8001/api/health
```

---

## 📞 **Still Having Issues?**

1. **Check browser console** for specific CORS errors
2. **Verify network connectivity** between frontend and backend
3. **Test with curl** to isolate CORS from other issues
4. **Check server logs** in `/var/log/onlinetestmaker_backend.log`
5. **Ensure services are running** with `supervisorctl status`

Your OnlineTestMaker platform is configured with secure CORS defaults that work for most self-hosted scenarios! 🚀