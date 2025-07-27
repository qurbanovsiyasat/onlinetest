# 🚀 Render.com Deployment Checklist for Squiz Platform

## ✅ Pre-Deployment Setup

### 1. GitHub Repository Setup
- [ ] Push your code to GitHub repository
- [ ] Ensure all files are in the root directory structure:
  ```
  your-repo/
  ├── backend/
  ├── frontend/
  ├── render.yaml
  ├── build-backend.sh
  ├── build-frontend.sh
  └── RENDER_DEPLOYMENT_GUIDE.md
  ```

### 2. File Permissions
- [ ] Ensure build scripts are executable:
  ```bash
  chmod +x build-backend.sh build-frontend.sh
  ```

## 🏗️ Render.com Service Creation

### Step 1: Create MongoDB Database
1. [ ] Go to [Render Dashboard](https://dashboard.render.com/)
2. [ ] Click "New +" → "Database" → "MongoDB"
3. [ ] Configure:
   - **Name:** `squiz-database`
   - **Plan:** Free tier (or paid for production)
4. [ ] Save the MongoDB connection string (format: `mongodb+srv://...`)

### Step 2: Create Backend Web Service
1. [ ] Click "New +" → "Web Service"
2. [ ] Connect your GitHub repository
3. [ ] Configure:
   - **Name:** `squiz-backend`
   - **Environment:** `Python 3`
   - **Root Directory:** `./` (leave empty for root)
   - **Build Command:** `cd backend && pip install -r requirements.txt`
   - **Start Command:** `cd backend && python -m uvicorn server:app --host 0.0.0.0 --port $PORT`

### Step 3: Configure Backend Environment Variables
Add these environment variables in the backend service settings:

**Required Variables:**
- [ ] `MONGO_URL` = `your-mongodb-connection-string-from-step-1`
- [ ] `DB_NAME` = `squiz_production`
- [ ] `JWT_SECRET` = `your-secure-random-jwt-secret` (generate a strong secret)

**Optional Variables:**
- [ ] `FRONTEND_URL` = `https://your-frontend-service-name.onrender.com`
- [ ] `ALLOWED_ORIGINS` = `https://your-frontend-service-name.onrender.com`

### Step 4: Create Frontend Static Site
1. [ ] Click "New +" → "Static Site"
2. [ ] Connect your GitHub repository
3. [ ] Configure:
   - **Name:** `squiz-frontend`
   - **Root Directory:** `./` (leave empty for root)
   - **Build Command:** `cd frontend && yarn install && yarn build`
   - **Publish Directory:** `frontend/build`

### Step 5: Configure Frontend Environment Variables
Add these environment variables in the frontend static site settings:

**Required Variables:**
- [ ] `REACT_APP_BACKEND_URL` = `https://your-backend-service-name.onrender.com`

**Build Optimization Variables:**
- [ ] `GENERATE_SOURCEMAP` = `false`
- [ ] `CI` = `false`
- [ ] `DISABLE_ESLINT_PLUGIN` = `true`

## 🔧 Deployment Process

### Step 6: Deploy Services
1. [ ] Deploy backend service first (wait for completion)
2. [ ] Deploy frontend service second
3. [ ] Check build logs for any errors

### Step 7: Verify Deployment
1. [ ] Test backend health check:
   ```
   GET https://your-backend-service.onrender.com/api/health
   ```
2. [ ] Access frontend URL:
   ```
   https://your-frontend-service.onrender.com
   ```
3. [ ] Test admin login:
   - Email: `admin@squiz.com`
   - Password: `admin123`

## 🔐 Post-Deployment Security

### Step 8: Security Configuration
- [ ] **CRITICAL:** Change admin password after first login
- [ ] Verify JWT secret is set to a strong random value
- [ ] Test CORS configuration with your domain
- [ ] Enable HTTPS (automatic with Render)

## 🐛 Troubleshooting Common Issues

### Build Failures

**Frontend Build Fails:**
- [ ] Check if `yarn install` completes without errors
- [ ] Verify all dependencies are in package.json
- [ ] Check build logs for specific errors
- [ ] Try building locally first: `cd frontend && yarn build`

**Backend Build Fails:**
- [ ] Check if `pip install -r requirements.txt` completes
- [ ] Verify Python version compatibility
- [ ] Check for missing environment variables

### Runtime Errors

**Backend Won't Start:**
- [ ] Verify MongoDB connection string is correct
- [ ] Check environment variables are set
- [ ] Review backend startup logs
- [ ] Test MongoDB connectivity

**Frontend Can't Connect to Backend:**
- [ ] Verify `REACT_APP_BACKEND_URL` is correct
- [ ] Check CORS configuration in backend
- [ ] Ensure backend is running and healthy
- [ ] Test API endpoints manually

**Database Connection Issues:**
- [ ] Verify MongoDB service is running
- [ ] Check connection string format
- [ ] Ensure database user has proper permissions
- [ ] Test connection from backend logs

## 📊 Monitoring & Maintenance

### Step 9: Set Up Monitoring
- [ ] Enable Render logging and monitoring
- [ ] Set up health check endpoints
- [ ] Configure alerts for service downtime
- [ ] Plan regular database backups

### Step 10: Performance Optimization
- [ ] Monitor service performance metrics
- [ ] Optimize database queries if needed
- [ ] Consider upgrading to paid plans for production
- [ ] Set up CDN for static assets (Render handles this)

## 💰 Cost Considerations

**Free Tier Limits:**
- Static Site (Frontend): Free with custom domain
- Web Service (Backend): Free tier with sleep mode after 15 minutes
- MongoDB: 500MB free storage

**Recommended Production Setup:**
- Backend: Starter plan ($7/month) for always-on service
- Database: Paid plan ($5/month) for 2GB storage and better performance
- Frontend: Free tier is sufficient

**Total Monthly Cost:** $0-12 depending on usage and requirements

## 🎯 Success Criteria

Your deployment is successful when:
- [ ] ✅ Backend health check returns "healthy" status
- [ ] ✅ Frontend loads without errors
- [ ] ✅ Admin can login with provided credentials
- [ ] ✅ Quiz creation and management works
- [ ] ✅ User registration and quiz taking works
- [ ] ✅ Database operations complete successfully

## 📞 Support Resources

- **Render Documentation:** https://render.com/docs
- **MongoDB Atlas Support:** https://support.mongodb.com/
- **Squiz Platform Issues:** Check application logs and backend health endpoints

---

**✨ Congratulations!** Your Squiz platform should now be live and accessible to users worldwide via Render.com!

**Admin Access:** https://your-frontend-service.onrender.com
**Credentials:** admin@squiz.com / admin123 (⚠️ Change password after first login!)