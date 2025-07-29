# 🎯 Squiz Platform - Comprehensive Quiz & Assessment System

Squiz is a modern, full-featured online quiz and assessment platform designed for educational institutions, teachers, and students. Built with React.js frontend and FastAPI backend, it provides a complete solution for creating, managing, and analyzing quizzes.

## ✨ Features

### 🔐 Authentication & User Management
- JWT-based secure authentication
- Role-based access control (Admin/User)
- User profile management
- Social features (follow system, privacy controls)

### 📝 Quiz Management System
- **Flexible Question Types**: Multiple choice, open-ended
- **Media Support**: Image and PDF uploads with cropping
- **Math Support**: LaTeX mathematical expressions
- **Hierarchical Organization**: Subject → Subcategory → Quiz
- **Draft/Publish System**: Safe quiz publishing workflow

### ⏱️ Real-time Quiz Sessions
- Live quiz session management
- Timed quizzes with auto-submission
- Session pause/resume functionality
- Real-time progress tracking

### 💬 Q&A Forum System
- Question and answer platform
- Upvote/downvote system
- Threaded discussions
- Accepted answer system
- Admin moderation tools

### 📊 Advanced Analytics & Reporting
- Detailed quiz performance analysis
- User statistics and progress tracking
- Platform-wide analytics
- Customizable reports

### 🎛️ Comprehensive Admin Panel
- Quiz management and bulk operations
- User management
- Statistics dashboards
- Forum moderation

## 🚀 Quick Start

### Prerequisites
- Node.js 18.x or higher
- Python 3.11 or higher
- MongoDB (local or Atlas)
- Docker (optional)

### Installation

#### Option 1: Docker Compose (Recommended)
\`\`\`bash
# Clone the repository
git clone <repository-url>
cd squiz-platform

# Start all services
docker-compose up -d

# Access the application
# Frontend: http://localhost:3000
# Backend API: http://localhost:8001
# MongoDB: localhost:27017
\`\`\`

#### Option 2: Manual Setup
\`\`\`bash
# Clone the repository
git clone <repository-url>
cd squiz-platform

# Backend setup
cd backend
pip install -r requirements.txt
cp .env.example .env  # Configure environment variables
python server.py

# Frontend setup (in new terminal)
cd frontend
npm install
cp .env.example .env  # Configure backend URL
npm start
\`\`\`

### Default Login Credentials
\`\`\`
Admin Account:
Email: admin@squiz.com
Password: admin123
\`\`\`

## 🏗️ Architecture

### Technology Stack
\`\`\`
Frontend:  React.js + Tailwind CSS + Axios
Backend:   FastAPI + Python 3.11 + Motor (MongoDB)
Database:  MongoDB Atlas/Local
Auth:      JWT + Bcrypt
Cache:     Redis (optional)
Deploy:    Docker + Docker Compose
\`\`\`

### System Architecture
\`\`\`
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │    Backend      │    │   Database      │
│   React.js      │◄──►│   FastAPI       │◄──►│   MongoDB       │
│   Port: 3000    │    │   Port: 8001    │    │   Port: 27017   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
\`\`\`

## 📚 API Documentation

### Base URL
- Development: `http://localhost:8001/api`
- Production: `https://api.yourdomain.com/api`

### Key Endpoints

#### Authentication
- `POST /api/auth/register` - User registration
- `POST /api/auth/login` - User login
- `GET /api/auth/me` - Get current user
- `POST /api/auth/change-password` - Change password

#### Quizzes
- `GET /api/quizzes` - List published quizzes
- `GET /api/quiz/{quiz_id}` - Get quiz details
- `POST /api/quiz/{quiz_id}/attempt` - Submit quiz attempt

#### Real-time Sessions
- `POST /api/quiz-session/start` - Start quiz session
- `POST /api/quiz-session/{session_id}/activate` - Activate session
- `GET /api/quiz-session/{session_id}/status` - Get session status
- `POST /api/quiz-session/{session_id}/submit` - Submit session

#### Q&A Forum
- `GET /api/questions` - List questions
- `POST /api/questions` - Create question
- `GET /api/questions/{question_id}` - Get question details
- `POST /api/questions/{question_id}/answers` - Answer question

#### Admin
- `GET /api/admin/users` - List all users
- `POST /api/admin/quiz` - Create quiz
- `POST /api/admin/quiz/{quiz_id}/publish` - Publish quiz
- `GET /api/admin/analytics` - Get platform analytics

### Authentication
All protected endpoints require JWT token:
\`\`\`
Authorization: Bearer <jwt_token>
\`\`\`

## 🗄️ Database Schema

### Collections
- `users` - User accounts and profiles
- `quizzes` - Quiz definitions and questions
- `quiz_attempts` - Quiz submission results
- `quiz_sessions` - Real-time quiz sessions
- `questions` - Forum questions
- `answers` - Forum answers
- `discussions` - Forum discussions
- `user_follows` - User follow relationships

## 🔧 Configuration

### Environment Variables

#### Backend (.env)
\`\`\`bash
# Database
MONGO_URL=mongodb://localhost:27017
# or MongoDB Atlas: mongodb+srv://username:password@cluster.mongodb.net/squiz_db

# JWT Configuration
JWT_SECRET=your-super-secret-jwt-key-256-bit-minimum
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24

# CORS
CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000

# Application
DEBUG=True
ENVIRONMENT=development
\`\`\`

#### Frontend (.env)
\`\`\`bash
# Backend API URL
REACT_APP_BACKEND_URL=http://localhost:8001

# Environment
REACT_APP_ENVIRONMENT=development

# Feature flags
REACT_APP_ENABLE_ANALYTICS=true
REACT_APP_ENABLE_FORUM=true
REACT_APP_ENABLE_REALTIME=true
\`\`\`

## 🧪 Testing

### Backend Tests
\`\`\`bash
cd backend
pip install pytest pytest-asyncio
pytest tests/
\`\`\`

### Frontend Tests
\`\`\`bash
cd frontend
npm test
\`\`\`

### API Testing
\`\`\`bash
# Health check
curl http://localhost:8001/api/health

# Login test
curl -X POST http://localhost:8001/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@squiz.com","password":"admin123"}'
\`\`\`

## 📦 Deployment

### Docker Production
\`\`\`bash
# Build and deploy
docker-compose -f docker-compose.prod.yml up -d

# Scale services
docker-compose up -d --scale backend=3
\`\`\`

### Cloud Deployment
1. **Database**: MongoDB Atlas cluster
2. **Backend**: Deploy to AWS ECS, Google Cloud Run, or Azure Container Instances
3. **Frontend**: Deploy to Vercel, Netlify, or AWS S3 + CloudFront
4. **CDN**: CloudFront, CloudFlare for static assets

## 🔒 Security

### Implemented Security Measures
- JWT token authentication with expiration
- Password hashing with bcrypt
- CORS configuration
- Input validation with Pydantic
- SQL injection prevention (MongoDB)
- XSS protection headers

### Security Best Practices
- Use HTTPS in production
- Implement rate limiting
- Regular security audits
- Keep dependencies updated
- Use environment variables for secrets

## 📊 Performance

### Optimization Features
- Database indexing for fast queries
- Pagination for large datasets
- Image optimization and compression
- Caching with Redis (optional)
- CDN for static assets

### Monitoring
- Health check endpoints
- Application metrics
- Error tracking with Sentry (configurable)
- Performance monitoring

## 🤝 Contributing

### Development Workflow
1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

### Code Standards
- **Backend**: Follow PEP 8 Python standards
- **Frontend**: ESLint + Prettier formatting
- **Documentation**: Update README for new features
- **Testing**: Include tests for new functionality

## 📈 Roadmap

### Phase 1 (Current)
- [x] Core quiz functionality
- [x] User authentication
- [x] Admin panel
- [x] Q&A forum
- [x] Real-time sessions

### Phase 2 (Next 3-6 months)
- [ ] AI-powered question generation
- [ ] Advanced learning analytics
- [ ] Mobile native apps
- [ ] SSO integration
- [ ] White-label deployment

### Phase 3 (6-12 months)
- [ ] Blockchain certificates
- [ ] VR/AR quiz experiences
- [ ] Multi-language support
- [ ] Enterprise API marketplace
- [ ] Advanced AI tutoring

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

### Documentation
- [API Documentation](docs/api.md)
- [User Guide](docs/user-guide.md)
- [Admin Guide](docs/admin-guide.md)

### Community
- GitHub Issues for bug reports
- GitHub Discussions for questions
- Discord community (coming soon)

### Commercial Support
For enterprise support, custom development, or consulting services, contact: support@squiz.com

---

**Built with ❤️ by the Squiz Team**

*Transform education through technology* 🚀
