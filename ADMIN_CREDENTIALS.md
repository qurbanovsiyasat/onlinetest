# 🔐 Squiz Platform - Admin Account Details

## Default Admin Account

**Admin Login Credentials:**
- **Email:** `admin@squiz.com`
- **Password:** `admin123`
- **Role:** Admin (Full Access)

## Admin Capabilities

The admin account has full access to:

### 📚 Quiz Management
- Create, edit, and delete quizzes
- Publish/unpublish quizzes (draft mode control)
- Move quizzes between subject folders
- Bulk publish multiple quizzes
- Set quiz visibility (public/private)
- Configure quiz access permissions

### 🗂️ Subject & Category Management
- Create and manage global subjects
- Add subcategories to subjects
- Organize quiz folder structure
- Set folder visibility and access

### 👥 User Management
- View all registered users
- Monitor user activity and status
- Manage user roles and permissions

### 📊 Analytics & Reports
- View quiz performance analytics
- Monitor user engagement
- Track quiz attempt statistics
- Generate leaderboards

### 🎯 Advanced Features
- Mathematical expressions support (MathJax)
- Image cropping and file uploads
- Mobile-responsive interface
- Real-time quiz validation

## Security Notes

⚠️ **IMPORTANT FOR PRODUCTION DEPLOYMENT:**

1. **Change Default Password:** After deployment, immediately change the admin password using the "Change Password" feature in the admin dashboard.

2. **Update Admin Email:** Consider changing the admin email to your organization's admin email address.

3. **Environment Variables:** Ensure JWT secrets and database credentials are properly configured in production environment variables.

## Admin Dashboard Access

1. Navigate to your deployed application URL
2. Click "Admin Login" button
3. Enter credentials above
4. Access full admin dashboard

## Creating Additional Admin Users

Currently, the system supports one primary admin account. To create additional admin users:

1. Register as a regular user first
2. Manually update the user's role in the database from 'user' to 'admin'
3. Or extend the backend to include admin user creation functionality

## Password Recovery

If admin password is lost:
1. Access the MongoDB database directly
2. Update the admin user's password hash
3. Or recreate the admin user through database operations

---

**Last Updated:** January 2025
**Platform Version:** Squiz v1.0