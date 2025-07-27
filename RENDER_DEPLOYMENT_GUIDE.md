# 🚀 Render.com Deployment Configuration for Squiz Platform

## Quick Deploy to Render.com

### Step 1: Create Services on Render Dashboard

Go to [https://dashboard.render.com/](https://dashboard.render.com/) and create these services:

#### 1. MongoDB Database
1. Click "New +" → "Database"
2. Select "MongoDB"
3. Name: `squiz-database`
4. Plan: Free tier (or paid as needed)
5. Save the connection string for later

#### 2. Backend Web Service
1. Click "New +" → "Web Service"
2. Connect your GitHub repository
3. Configure:
   - **Name:** `squiz-backend`
   - **Environment:** `Python 3`
   - **Build Command:** `cd backend && pip install -r requirements.txt`
   - **Start Command:** `cd backend && python -m uvicorn server:app --host 0.0.0.0 --port $PORT`
   - **Root Directory:** `./`

#### 3. Frontend Static Site
1. Click "New +" → "Static Site"
2. Connect your GitHub repository
3. Configure:
   - **Name:** `squiz-frontend`
   - **Build Command:** `cd frontend && yarn install && yarn build`
   - **Publish Directory:** `frontend/build`
   - **Root Directory:** `./`

### Step 2: Environment Variables

#### Backend Environment Variables
Add these in Render backend service settings:

```bash
# Database
MONGO_URL=mongodb+srv://your-mongodb-connection-string
DB_NAME=squiz_production

# Security
JWT_SECRET=your-secure-jwt-secret-key-here

# CORS
FRONTEND_URL=https://your-frontend-service.onrender.com
```

#### Frontend Environment Variables
Add these in Render frontend static site settings:

```bash
# Backend API URL
REACT_APP_BACKEND_URL=https://your-backend-service.onrender.com

# Build optimization
GENERATE_SOURCEMAP=false
CI=false
```

### Step 3: Deploy

1. Push your code to GitHub
2. Render will automatically build and deploy
3. Access your admin dashboard at the frontend URL with:
   - Email: `admin@squiz.com`
   - Password: `admin123`

## Deployment Architecture

```
┌─────────────────────┐    ┌─────────────────────┐    ┌─────────────────────┐
│   Frontend          │    │   Backend           │    │   MongoDB           │
│   (Static Site)     │    │   (Web Service)     │    │   (Database)        │
│                     │    │                     │    │                     │
│   React App         │◄──►│   FastAPI           │◄──►│   Quiz Data         │
│   Built Assets      │    │   Python Backend    │    │   User Accounts     │
│   Served by Render  │    │   REST API          │    │   Analytics         │
└─────────────────────┘    └─────────────────────┘    └─────────────────────┘
```

## Important Production Settings

### Security Checklist
- [ ] Change default admin password
- [ ] Set strong JWT secret
- [ ] Configure proper CORS origins
- [ ] Enable HTTPS (automatic with Render)
- [ ] Set up database backups

### Performance Optimization
- [ ] Enable build optimizations
- [ ] Configure CDN (Render handles this)
- [ ] Set up monitoring and logging
- [ ] Optimize database queries

### Maintenance
- [ ] Set up automated backups
- [ ] Monitor service health
- [ ] Plan for scaling if needed
- [ ] Regular security updates

## Troubleshooting

### Common Issues:

1. **Build Fails:**
   - Check build logs in Render dashboard
   - Verify package.json and requirements.txt
   - Ensure correct Node.js/Python versions

2. **Backend Won't Start:**
   - Check environment variables
   - Verify MongoDB connection string
   - Review startup logs

3. **Frontend Can't Connect to Backend:**
   - Verify REACT_APP_BACKEND_URL is correct
   - Check CORS configuration
   - Ensure backend is running

4. **Database Connection Issues:**
   - Verify MongoDB connection string
   - Check network permissions
   - Ensure database is running

## Cost Estimate

- **Frontend (Static Site):** Free
- **Backend (Web Service):** Free tier available, $7/month for paid
- **Database (MongoDB):** Free tier 500MB, $5/month for 2GB

Total estimated cost: **$0-12/month** depending on usage.

---

**Need Help?** Check Render.com documentation or contact support.