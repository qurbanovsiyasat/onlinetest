from fastapi import FastAPI, APIRouter, HTTPException, Depends, status, UploadFile, File
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional
import uuid
from datetime import datetime, timedelta
import jwt
import bcrypt
from enum import Enum
import base64
import imghdr


ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# JWT Settings
JWT_SECRET = "OnlineTestMaker_Secret_Key_2025"  # In production, use environment variable
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_HOURS = 24

# Create the main app
app = FastAPI()
api_router = APIRouter(prefix="/api")

# Security
security = HTTPBearer()

# Enums
class UserRole(str, Enum):
    ADMIN = "admin"
    USER = "user"

# Models
class User(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    email: EmailStr
    name: str
    role: UserRole = UserRole.USER
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)

class UserCreate(BaseModel):
    email: EmailStr
    name: str
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: str
    email: str
    name: str
    role: UserRole
    is_active: bool
    created_at: datetime

class Token(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse

class QuizOption(BaseModel):
    text: str
    is_correct: bool

class QuizQuestion(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    question_text: str
    options: List[QuizOption]
    image_url: Optional[str] = None

class Quiz(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    description: str
    category: str
    questions: List[QuizQuestion]
    created_by: str  # Admin user ID
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    total_questions: int = 0
    is_active: bool = True
    is_public: bool = False  # New: Public/Private toggle
    allowed_users: List[str] = []  # New: List of user IDs who can access public quiz
    subject_folder: str = "General"  # New: Subject folder organization

class QuizCreate(BaseModel):
    title: str
    description: str
    category: str
    questions: List[QuizQuestion]

class QuizAttempt(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    quiz_id: str
    user_id: str
    answers: List[str]
    score: int
    total_questions: int
    percentage: float
    attempted_at: datetime = Field(default_factory=datetime.utcnow)

class QuizAttemptCreate(BaseModel):
    quiz_id: str
    answers: List[str]

class Category(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

# Utility Functions
def hash_password(password: str) -> str:
    """Hash password using bcrypt"""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(password: str, hashed_password: str) -> bool:
    """Verify password against hash"""
    return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))

def create_access_token(user_data: dict) -> str:
    """Create JWT access token"""
    expire = datetime.utcnow() + timedelta(hours=JWT_EXPIRATION_HOURS)
    user_data.update({"exp": expire})
    return jwt.encode(user_data, JWT_SECRET, algorithm=JWT_ALGORITHM)

def decode_access_token(token: str) -> dict:
    """Decode JWT access token"""
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

# Dependencies
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get current user from JWT token"""
    token = credentials.credentials
    payload = decode_access_token(token)
    
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    # Get user from database
    user_doc = await db.users.find_one({"id": user_id})
    if not user_doc:
        raise HTTPException(status_code=401, detail="User not found")
    
    return User(**user_doc)

async def get_admin_user(current_user: User = Depends(get_current_user)):
    """Ensure current user is admin"""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Admin access required")
    return current_user

# Authentication Routes
@api_router.post("/auth/register", response_model=UserResponse)
async def register(user_data: UserCreate):
    """Register new user"""
    # Check if user already exists
    existing_user = await db.users.find_one({"email": user_data.email})
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Hash password
    hashed_password = hash_password(user_data.password)
    
    # Create user
    user = User(
        email=user_data.email,
        name=user_data.name,
        role=UserRole.USER  # Default role is user
    )
    
    # Store user with hashed password
    user_dict = user.dict()
    user_dict["password"] = hashed_password
    
    await db.users.insert_one(user_dict)
    
    return UserResponse(**user.dict())

@api_router.post("/auth/login", response_model=Token)
async def login(login_data: UserLogin):
    """Login user"""
    # Find user
    user_doc = await db.users.find_one({"email": login_data.email})
    if not user_doc:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    # Verify password
    if not verify_password(login_data.password, user_doc["password"]):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    # Create token
    user = User(**user_doc)
    token_data = {
        "sub": user.id,
        "email": user.email,
        "role": user.role,
        "name": user.name
    }
    access_token = create_access_token(token_data)
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": UserResponse(**user.dict())
    }

@api_router.get("/auth/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    """Get current user info"""
    return UserResponse(**current_user.dict())

# Admin Routes
@api_router.get("/admin/users", response_model=List[UserResponse])
async def get_all_users(admin_user: User = Depends(get_admin_user)):
    """Get all users (admin only)"""
    users = await db.users.find().to_list(1000)
    return [UserResponse(**user) for user in users]

@api_router.post("/admin/quiz", response_model=Quiz)
async def create_quiz(quiz_data: QuizCreate, admin_user: User = Depends(get_admin_user)):
    """Create quiz (admin only)"""
    quiz = Quiz(**quiz_data.dict(), created_by=admin_user.id)
    quiz.total_questions = len(quiz.questions)
    
    await db.quizzes.insert_one(quiz.dict())
    return quiz

@api_router.get("/admin/quizzes", response_model=List[Quiz])
async def get_all_quizzes_admin(admin_user: User = Depends(get_admin_user)):
    """Get all quizzes (admin only)"""
    quizzes = await db.quizzes.find().to_list(1000)
    valid_quizzes = []
    for quiz in quizzes:
        # Handle old quizzes without required fields
        if 'category' not in quiz:
            quiz['category'] = 'Uncategorized'
        if 'created_by' not in quiz:
            quiz['created_by'] = admin_user.id
        if 'is_active' not in quiz:
            quiz['is_active'] = True
        try:
            valid_quizzes.append(Quiz(**quiz))
        except Exception as e:
            # Skip invalid quiz records
            print(f"Skipping invalid quiz: {quiz.get('id', 'unknown')} - {str(e)}")
            continue
    return valid_quizzes

@api_router.delete("/admin/quiz/{quiz_id}")
async def delete_quiz(quiz_id: str, admin_user: User = Depends(get_admin_user)):
    """Delete quiz (admin only)"""
    result = await db.quizzes.delete_one({"id": quiz_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Quiz not found")
    return {"message": "Quiz deleted successfully"}

@api_router.post("/admin/category", response_model=Category)
async def create_category(category_name: str, description: str = "", admin_user: User = Depends(get_admin_user)):
    """Create category (admin only)"""
    category = Category(name=category_name, description=description)
    await db.categories.insert_one(category.dict())
    return category

@api_router.get("/admin/categories", response_model=List[Category])
async def get_categories(admin_user: User = Depends(get_admin_user)):
    """Get all categories (admin only)"""
    categories = await db.categories.find().to_list(1000)
    return [Category(**cat) for cat in categories]

# User Routes (Quiz Taking)
@api_router.get("/quizzes", response_model=List[Quiz])
async def get_public_quizzes(current_user: User = Depends(get_current_user)):
    """Get all active quizzes for users"""
    quizzes = await db.quizzes.find({"is_active": True}).to_list(1000)
    return [Quiz(**quiz) for quiz in quizzes]

@api_router.get("/quiz/{quiz_id}", response_model=Quiz)
async def get_quiz(quiz_id: str, current_user: User = Depends(get_current_user)):
    """Get specific quiz"""
    quiz = await db.quizzes.find_one({"id": quiz_id, "is_active": True})
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")
    return Quiz(**quiz)

@api_router.post("/quiz/{quiz_id}/attempt", response_model=QuizAttempt)
async def submit_quiz_attempt(quiz_id: str, attempt_data: QuizAttemptCreate, current_user: User = Depends(get_current_user)):
    """Submit quiz attempt (users only)"""
    if current_user.role == UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Admins cannot take quizzes")
    
    # Get quiz
    quiz = await db.quizzes.find_one({"id": quiz_id, "is_active": True})
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")
    
    quiz_obj = Quiz(**quiz)
    
    # Calculate score
    score = 0
    total_questions = len(quiz_obj.questions)
    
    for i, user_answer in enumerate(attempt_data.answers):
        if i < len(quiz_obj.questions):
            question = quiz_obj.questions[i]
            for option in question.options:
                if option.is_correct and option.text == user_answer:
                    score += 1
                    break
    
    percentage = (score / total_questions * 100) if total_questions > 0 else 0
    
    # Create attempt
    attempt = QuizAttempt(
        quiz_id=quiz_id,
        user_id=current_user.id,
        answers=attempt_data.answers,
        score=score,
        total_questions=total_questions,
        percentage=percentage
    )
    
    await db.quiz_attempts.insert_one(attempt.dict())
    return attempt

@api_router.get("/my-attempts", response_model=List[QuizAttempt])
async def get_my_attempts(current_user: User = Depends(get_current_user)):
    """Get current user's quiz attempts"""
    attempts = await db.quiz_attempts.find({"user_id": current_user.id}).to_list(1000)
    return [QuizAttempt(**attempt) for attempt in attempts]

# Image Upload Routes
@api_router.post("/admin/upload-image")
async def upload_image(file: UploadFile = File(...), admin_user: User = Depends(get_admin_user)):
    """Upload image for quiz questions (admin only)"""
    # Validate file type
    if not file.content_type.startswith('image/'):
        raise HTTPException(status_code=400, detail="File must be an image")
    
    # Validate file size (max 5MB)
    content = await file.read()
    if len(content) > 5 * 1024 * 1024:  # 5MB
        raise HTTPException(status_code=400, detail="File size must be less than 5MB")
    
    # Validate image format
    file_type = imghdr.what(None, h=content)
    if file_type not in ['jpeg', 'jpg', 'png', 'gif', 'webp']:
        raise HTTPException(status_code=400, detail="Unsupported image format")
    
    # Generate unique filename
    file_id = str(uuid.uuid4())
    file_extension = file.filename.split('.')[-1] if '.' in file.filename else file_type
    filename = f"{file_id}.{file_extension}"
    
    # Convert to base64 for storage (in production, use cloud storage)
    base64_content = base64.b64encode(content).decode('utf-8')
    
    # Store image metadata in database
    image_data = {
        "id": file_id,
        "filename": filename,
        "original_name": file.filename,
        "content_type": file.content_type,
        "size": len(content),
        "base64_data": base64_content,
        "uploaded_by": admin_user.id,
        "uploaded_at": datetime.utcnow()
    }
    
    await db.images.insert_one(image_data)
    
    # Return image URL (base64 data URL)
    data_url = f"data:{file.content_type};base64,{base64_content}"
    
    return {
        "id": file_id,
        "filename": filename,
        "url": data_url,
        "size": len(content)
    }

@api_router.get("/image/{image_id}")
async def get_image(image_id: str):
    """Get image by ID"""
    image = await db.images.find_one({"id": image_id})
    if not image:
        raise HTTPException(status_code=404, detail="Image not found")
    
    # Return base64 data URL
    data_url = f"data:{image['content_type']};base64,{image['base64_data']}"
    return {"url": data_url}
@api_router.post("/init-admin")
async def initialize_admin():
    """Initialize admin user (run once)"""
    # Check if admin already exists
    admin_exists = await db.users.find_one({"role": "admin"})
    if admin_exists:
        raise HTTPException(status_code=400, detail="Admin already exists")
    
    # Create admin user
    admin_password = hash_password("admin123")  # Change this in production
    admin_user = User(
        email="admin@onlinetestmaker.com",
        name="System Administrator",
        role=UserRole.ADMIN
    )
    
    admin_dict = admin_user.dict()
    admin_dict["password"] = admin_password
    
    await db.users.insert_one(admin_dict)
    
    return {
        "message": "Admin user created successfully",
        "email": "admin@onlinetestmaker.com",
        "password": "admin123"
    }

# General Routes
@api_router.get("/")
async def root():
    return {"message": "OnlineTestMaker API - Admin Centered Version"}

# Admin Results Viewing Routes
@api_router.get("/admin/quiz-results")
async def get_all_quiz_results(admin_user: User = Depends(get_admin_user)):
    """Get all quiz attempts/results (admin only)"""
    # Get all attempts with additional user and quiz information
    attempts = await db.quiz_attempts.find().to_list(1000)
    
    # Enrich attempts with user and quiz information
    enriched_results = []
    for attempt in attempts:
        # Skip attempts without user_id (old data)
        if 'user_id' not in attempt:
            continue
            
        # Get user info
        user = await db.users.find_one({"id": attempt["user_id"]})
        user_info = {
            "name": user.get("name", "Unknown User") if user else "Unknown User",
            "email": user.get("email", "Unknown Email") if user else "Unknown Email"
        }
        
        # Get quiz info
        quiz = await db.quizzes.find_one({"id": attempt["quiz_id"]})
        quiz_info = {
            "title": quiz.get("title", "Unknown Quiz") if quiz else "Unknown Quiz",
            "category": quiz.get("category", "Unknown Category") if quiz else "Unknown Category"
        }
        
        # Combine all information
        result = {
            "attempt_id": attempt["id"],
            "user": user_info,
            "quiz": quiz_info,
            "score": attempt["score"],
            "total_questions": attempt["total_questions"],
            "percentage": attempt["percentage"],
            "attempted_at": attempt["attempted_at"],
            "answers": attempt.get("answers", [])
        }
        enriched_results.append(result)
    
    # Sort by attempt date (newest first)
    enriched_results.sort(key=lambda x: x["attempted_at"], reverse=True)
    
    return enriched_results

@api_router.get("/admin/quiz-results/user/{user_id}")
async def get_user_quiz_results(user_id: str, admin_user: User = Depends(get_admin_user)):
    """Get all quiz results for a specific user (admin only)"""
    attempts = await db.quiz_attempts.find({"user_id": user_id}).to_list(1000)
    
    enriched_results = []
    for attempt in attempts:
        # Get quiz info
        quiz = await db.quizzes.find_one({"id": attempt["quiz_id"]})
        quiz_info = {
            "title": quiz.get("title", "Unknown Quiz") if quiz else "Unknown Quiz",
            "category": quiz.get("category", "Unknown Category") if quiz else "Unknown Category"
        }
        
        result = {
            "attempt_id": attempt["id"],
            "quiz": quiz_info,
            "score": attempt["score"],
            "total_questions": attempt["total_questions"],
            "percentage": attempt["percentage"],
            "attempted_at": attempt["attempted_at"]
        }
        enriched_results.append(result)
    
    # Sort by attempt date (newest first)
    enriched_results.sort(key=lambda x: x["attempted_at"], reverse=True)
    
    return enriched_results

@api_router.get("/admin/quiz-results/quiz/{quiz_id}")
async def get_quiz_results(quiz_id: str, admin_user: User = Depends(get_admin_user)):
    """Get all results for a specific quiz (admin only)"""
    attempts = await db.quiz_attempts.find({"quiz_id": quiz_id}).to_list(1000)
    
    enriched_results = []
    for attempt in attempts:
        # Get user info
        user = await db.users.find_one({"id": attempt["user_id"]})
        user_info = {
            "name": user.get("name", "Unknown User") if user else "Unknown User",
            "email": user.get("email", "Unknown Email") if user else "Unknown Email"
        }
        
        result = {
            "attempt_id": attempt["id"],
            "user": user_info,
            "score": attempt["score"],
            "total_questions": attempt["total_questions"],
            "percentage": attempt["percentage"],
            "attempted_at": attempt["attempted_at"]
        }
        enriched_results.append(result)
    
    # Sort by attempt date (newest first)
    enriched_results.sort(key=lambda x: x["attempted_at"], reverse=True)
    
    return enriched_results

@api_router.get("/admin/analytics/summary")
async def get_analytics_summary(admin_user: User = Depends(get_admin_user)):
    """Get analytics summary for admin dashboard"""
    # Count total users
    total_users = await db.users.count_documents({"role": "user"})
    
    # Count total quizzes
    total_quizzes = await db.quizzes.count_documents({"is_active": True})
    
    # Count total attempts
    total_attempts = await db.quiz_attempts.count_documents({})
    
    # Calculate average score
    attempts = await db.quiz_attempts.find().to_list(1000)
    avg_score = 0
    if attempts:
        total_percentage = sum(attempt["percentage"] for attempt in attempts)
        avg_score = total_percentage / len(attempts)
    
    # Get most popular quiz
    quiz_attempt_counts = {}
    for attempt in attempts:
        quiz_id = attempt["quiz_id"]
        quiz_attempt_counts[quiz_id] = quiz_attempt_counts.get(quiz_id, 0) + 1
    
    most_popular_quiz = "None"
    if quiz_attempt_counts:
        most_popular_quiz_id = max(quiz_attempt_counts, key=quiz_attempt_counts.get)
        quiz = await db.quizzes.find_one({"id": most_popular_quiz_id})
        if quiz:
            most_popular_quiz = quiz.get("title", "Unknown Quiz")
    
    return {
        "total_users": total_users,
        "total_quizzes": total_quizzes,
        "total_attempts": total_attempts,
        "average_score": round(avg_score, 1),
        "most_popular_quiz": most_popular_quiz
    }
async def get_public_categories():
    """Get all categories for public viewing"""
    categories = await db.categories.find().to_list(1000)
    return [Category(**cat) for cat in categories]

# Include router
app.include_router(api_router)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()