# 🚀 Complete Step-by-Step Guide: Deploy Squiz Quiz Platform to Render

## **What You're Deploying**
A comprehensive quiz platform with:
- **Admin Dashboard**: Create/manage quizzes, users, analytics
- **User Interface**: Take quizzes, view results, hierarchical navigation
- **Features**: Real-time sessions, timer functionality, file uploads, mathematical expressions
- **Architecture**: FastAPI backend + React frontend + MongoDB database

## **Prerequisites Checklist**
✅ GitHub account  
✅ Render.com account (free)  
✅ Your code pushed to GitHub repository  
✅ MongoDB Atlas database (already configured)  

---

## **STEP 1: Push Your Code to GitHub**

1. **Initialize Git Repository** (if not already done):
   ```bash
   git init
   git add .
   git commit -m "Initial commit - Squiz Quiz Platform"
   ```

2. **Create GitHub Repository**:
   - Go to [GitHub](https://github.com)
   - Click "New Repository"
   - Name: `squiz-quiz-platform` (or your preferred name)
   - Make it Public or Private (your choice)
   - Don't initialize with README (you already have one)

3. **Push to GitHub**:
   ```bash
   git remote add origin https://github.com/YOUR-USERNAME/squiz-quiz-platform.git
   git branch -M main
   git push -u origin main
   ```

---

## **STEP 2: Create Render Account & Services**

### A. Sign Up for Render
1. Go to [https://render.com](https://render.com)
2. Click "Get Started" and sign up (free)
3. Connect your GitHub account
4. Go to Dashboard: [https://dashboard.render.com](https://dashboard.render.com)

### B. Create MongoDB Database
1. Click "New +" → "Database"
2. Select "MongoDB"
3. Configure:
   - **Name**: `squiz-database`
   - **Database Name**: `squiz_production`
   - **User**: Leave default
   - **Region**: Choose closest to your users
   - **Plan**: Free (500MB) or Starter ($5/month for 2GB)
4. Click "Create Database"
5. **IMPORTANT**: Save the connection string - you'll see it in the database overview

### C. Create Backend Web Service
1. Click "New +" → "Web Service"
2. Click "Build and deploy from a Git repository"
3. Connect your GitHub repository
4. Configure:
   - **Name**: `squiz-backend`
   - **Root Directory**: `.` (leave blank)
   - **Environment**: `Python 3`
   - **Region**: Same as your database
   - **Branch**: `main`
   - **Build Command**: `cd backend && pip install -r requirements.txt`
   - **Start Command**: `cd backend && python -m uvicorn server:app --host 0.0.0.0 --port $PORT`
   - **Plan**: Free tier

5. **Environment Variables** - Add these:
   ```
   MONGO_URL = [Paste your MongoDB connection string from step B]
   DB_NAME = squiz_production
   JWT_SECRET = [Generate a random 32-character string]
   ```

6. Click "Create Web Service"

### D. Create Frontend Static Site
1. Click "New +" → "Static Site"
2. Connect the same GitHub repository
3. Configure:
   - **Name**: `squiz-frontend`
   - **Root Directory**: `.` (leave blank)
   - **Branch**: `main`
   - **Build Command**: `cd frontend && yarn install && yarn build:production`
   - **Publish Directory**: `frontend/build`
   - **Plan**: Free

4. **Environment Variables** - Add these:
   ```
   REACT_APP_BACKEND_URL = https://squiz-backend.onrender.com
   GENERATE_SOURCEMAP = false
   CI = false
   ```
   
   **Note**: Replace `squiz-backend` with your actual backend service name if different.

5. Click "Create Static Site"

---

## **STEP 3: Configure Environment Variables**

### Backend Service Environment Variables
In your backend service settings, ensure you have:

```env
MONGO_URL=mongodb+srv://username:password@cluster.mongodb.net/squiz_production?retryWrites=true&w=majority
DB_NAME=squiz_production
JWT_SECRET=your-32-character-random-string-here
```

### Frontend Service Environment Variables
In your frontend service settings, ensure you have:

```env
REACT_APP_BACKEND_URL=https://your-backend-service-name.onrender.com
GENERATE_SOURCEMAP=false
CI=false
```

---

## **STEP 4: Update CORS Configuration**

Your backend needs to allow your frontend domain. The code is already prepared, but verify the URLs match your deployed services.

In `/app/backend/server.py`, the CORS origins should include your frontend URL:
```python
allow_origins=[
    "https://squiz-frontend.onrender.com",  # Your frontend URL
    "http://localhost:3000",                # Local development
],
```

---

## **STEP 5: Deploy & Monitor**

1. **Automatic Deployment**:
   - Render automatically builds when you create the services
   - Monitor progress in the Render dashboard
   - Check build logs for any errors

2. **Verify Services**:
   - **Backend**: Visit `https://your-backend.onrender.com/api/health`
     - Should return: `{"status":"healthy","message":"Squiz backend is running"}`
   - **Frontend**: Visit your frontend URL
     - Should show the Squiz login page

3. **Test Admin Access**:
   - Email: `admin@squiz.com`
   - Password: `admin123`

---

## **STEP 6: Custom Domain (Optional)**

If you want a custom domain:

1. **For Frontend**:
   - Go to your frontend service settings
   - Click "Custom Domains"
   - Add your domain (e.g., `quiz.yourdomain.com`)

2. **For Backend** (if needed):
   - Go to your backend service settings
   - Click "Custom Domains"
   - Add API subdomain (e.g., `api.yourdomain.com`)

3. **Update Environment Variables** if you use custom domains:
   - Update `REACT_APP_BACKEND_URL` in frontend
   - Update CORS origins in backend

---

## **STEP 7: Production Optimizations**

### Security
1. **Change Default Admin Password**:
   - Login with `admin@squiz.com` / `admin123`
   - Change password immediately

2. **Generate Strong JWT Secret**:
   - Use: `openssl rand -base64 32`
   - Update in Render backend environment variables

### Performance
1. **Enable Build Optimizations**: ✅ Already configured
2. **Database Indexing**: Your MongoDB setup handles this
3. **CDN**: Render provides this automatically

### Monitoring
1. **Health Checks**: ✅ Already configured (`/api/health`)
2. **Error Monitoring**: Check Render dashboard logs
3. **Database Monitoring**: Use MongoDB Atlas dashboard

---

## **STEP 8: Verification Checklist**

After deployment, verify these features work:

### ✅ **Basic Functionality**
- [ ] Frontend loads without errors
- [ ] Backend health check responds
- [ ] Admin login works (`admin@squiz.com` / `admin123`)
- [ ] User registration works
- [ ] Database connection is stable

### ✅ **Core Features**
- [ ] Create new quiz
- [ ] Publish quiz
- [ ] Take quiz as user
- [ ] View quiz results
- [ ] Real-time timer functionality
- [ ] File upload (images/PDFs)
- [ ] Mathematical expressions display

### ✅ **Advanced Features**
- [ ] Folder organization
- [ ] Quiz analytics
- [ ] User management
- [ ] Bulk operations
- [ ] Mobile responsiveness

---

## **Troubleshooting Common Issues**

### 🔧 **Build Failures**

**Backend Build Fails:**
```bash
# Check if requirements.txt is correct
cd backend && pip install -r requirements.txt
```

**Frontend Build Fails:**
```bash
# Check if package.json is correct
cd frontend && yarn install && yarn build
```

### 🔧 **Runtime Errors**

**Backend Won't Start:**
1. Check environment variables are set correctly
2. Verify MongoDB connection string
3. Check Render logs: Service → Logs tab

**Frontend Can't Connect to Backend:**
1. Verify `REACT_APP_BACKEND_URL` is correct
2. Check CORS configuration
3. Ensure backend is running (green status)

**Database Connection Issues:**
1. Verify MongoDB Atlas cluster is running
2. Check connection string format
3. Ensure IP whitelist allows Render's IPs (or set to 0.0.0.0/0)

### 🔧 **Performance Issues**

**Slow Loading:**
1. Check if services are on free tier (they sleep after inactivity)
2. Consider upgrading to paid plans for production use
3. Monitor database performance in Atlas

---

## **Cost Breakdown**

### Free Tier (Testing/Personal Use)
- **Frontend**: $0 (Static site)
- **Backend**: $0 (with limitations - sleeps after inactivity)
- **Database**: $0 (MongoDB Atlas free 500MB)
- **Total**: **$0/month**

### Paid Tier (Production Use)
- **Frontend**: $0 (Static site)
- **Backend**: $7/month (no sleep, better performance)
- **Database**: $5/month (MongoDB Atlas Starter 2GB)
- **Total**: **$12/month**

---

## **Next Steps After Deployment**

1. **Change Admin Password** immediately
2. **Create Subject Categories** for your quizzes
3. **Import/Create Your Quizzes**
4. **Set up User Accounts** or let users register
5. **Monitor Usage** through Render and Atlas dashboards
6. **Plan for Scaling** if you expect high traffic

---

## **Support & Resources**

- **Render Documentation**: [https://render.com/docs](https://render.com/docs)
- **MongoDB Atlas Help**: [https://docs.atlas.mongodb.com](https://docs.atlas.mongodb.com)
- **Your Application**: Already configured and production-ready!

---

## **Important URLs After Deployment**

Save these for reference:

- **Frontend URL**: `https://your-frontend-name.onrender.com`
- **Backend URL**: `https://your-backend-name.onrender.com`
- **API Health Check**: `https://your-backend-name.onrender.com/api/health`
- **Admin Login**: Use frontend URL with `admin@squiz.com` / `admin123`

---

**🎉 Congratulations!** Your Squiz Quiz Platform will be live on the internet, accessible to users worldwide!