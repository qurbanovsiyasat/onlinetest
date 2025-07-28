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


ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# JWT Settings - Use environment variable in production
JWT_SECRET = os.environ.get('JWT_SECRET', 'Squiz_Secret_Key_2025')  # Default for development
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_HOURS = 24

# Create the main app
app = FastAPI()
api_router = APIRouter(prefix="/api")
# YALNIZ BİR DƏFƏ import edin
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# CORS Middleware-i ƏN ƏVVƏL ƏLAVƏ EDİN
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://squiz-frontend.onrender.com",  # Production frontend URL
        "https://squiz-k5qa.onrender.com",      # Alternative frontend URL
        "http://localhost:3000",                # Local development
    ],
    allow_credentials=True,
    allow_methods=["*"],                    # Bütün metodlara icazə
    allow_headers=["*"],                    # Bütün başlıqlara icazə
    expose_headers=["*"]                    # Bütün cavab başlıqlarını göstər
)

# OPTIONS sorğuları üçün xüsusi handler
@app.options("/api/{path:path}")
async def options_handler():
    return {"message": "CORS preflight"}
# Security
security = HTTPBearer()

# Enums
class UserRole(str, Enum):
    ADMIN = "admin"
    USER = "user"

# Health check endpoint for self-hosted deployment verification
@api_router.get("/health")
async def health_check():
    """Health check endpoint to verify self-hosted backend is running"""
    try:
        # Check database connection
        await db.command("ping")
        return {
            "status": "healthy",
            "message": "Squiz backend is running (self-hosted)",
            "database": "connected",
            "timestamp": datetime.utcnow().isoformat(),
            "version": "1.0.0",
            "hosting": "self-hosted"
        }
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail=f"Health check failed: {str(e)}"
        )

@api_router.get("/cors-info")
async def cors_info():
    """CORS configuration information for debugging"""
    return {
        "allowed_origins": get_cors_origins(),
        "allowed_methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allowed_headers": [
            "Accept", "Accept-Language", "Content-Language",
            "Content-Type", "Authorization", "X-Requested-With", "X-CSRF-Token"
        ],
        "credentials_allowed": True,
        "max_age": 600,
        "note": "This endpoint helps debug CORS issues in self-hosted deployments"
    }
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

from enum import Enum

class QuestionType(str, Enum):
    MULTIPLE_CHOICE = "multiple_choice"
    OPEN_ENDED = "open_ended"

class DifficultyLevel(str, Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"

class QuizOption(BaseModel):
    text: str
    is_correct: bool

class OpenEndedAnswer(BaseModel):
    expected_answers: List[str]  # List of acceptable answers
    keywords: List[str] = []  # Keywords for auto-grading
    case_sensitive: bool = False
    partial_credit: bool = True

class QuizQuestion(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    question_text: str
    question_type: QuestionType = QuestionType.MULTIPLE_CHOICE
    
    # Multiple Choice specific
    options: List[QuizOption] = []
    multiple_correct: bool = False  # Allow multiple correct answers
    
    # Open Ended specific
    open_ended_answer: Optional[OpenEndedAnswer] = None
    
    # Media attachments
    image_url: Optional[str] = None
    pdf_url: Optional[str] = None
    
    # Question metadata
    difficulty: Optional[DifficultyLevel] = None
    points: int = 1
    is_mandatory: bool = True
    explanation: Optional[str] = None  # Explanation shown after answer
    
    # Validation
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class Quiz(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    description: str
    category: str
    subject: str  # Main subject (e.g., "Mathematics", "Science")
    subcategory: str = "General"  # Subcategory (e.g., "Triangle", "Algebra")
    questions: List[QuizQuestion]
    created_by: str  # User ID (admin or regular user)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    total_questions: int = 0
    total_points: int = 0  # Sum of all question points
    is_active: bool = True
    is_public: bool = False  # Public/Private toggle
    allowed_users: List[str] = []  # List of user IDs who can access public quiz
    total_attempts: int = 0  # Track how many times quiz was taken
    average_score: float = 0.0  # Average score across all attempts
    
    # Ownership fields
    quiz_owner_type: str = "admin"  # "admin" or "user"
    quiz_owner_id: str = ""  # ID of the owner (admin or user)
    
    # Validation settings
    min_pass_percentage: float = 60.0  # Minimum percentage to pass
    time_limit_minutes: Optional[int] = None  # Optional time limit
    shuffle_questions: bool = False  # Randomize question order
    shuffle_options: bool = False  # Randomize option order
    
    # Preview and publishing
    is_draft: bool = True  # Quiz starts as draft until published
    preview_token: Optional[str] = None  # Token for preview access

class QuizCreate(BaseModel):
    title: str
    description: str
    category: str
    subject: str
    subcategory: str = "General"
    questions: List[QuizQuestion]
    is_public: bool = False
    allowed_users: List[str] = []
    min_pass_percentage: float = 60.0
    time_limit_minutes: Optional[int] = None
    shuffle_questions: bool = False
    shuffle_options: bool = False

class QuizUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    subject: Optional[str] = None
    subcategory: Optional[str] = None
    questions: Optional[List[QuizQuestion]] = None
    is_public: Optional[bool] = None
    allowed_users: Optional[List[str]] = None
    is_active: Optional[bool] = None
    min_pass_percentage: Optional[float] = None
    time_limit_minutes: Optional[int] = None
    shuffle_questions: Optional[bool] = None
    shuffle_options: Optional[bool] = None
    is_draft: Optional[bool] = None

class QuizValidationError(BaseModel):
    field: str
    message: str
    question_index: Optional[int] = None

class SubjectFolder(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: Optional[str] = None
    subcategories: List[str] = []
    is_active: bool = True
    allowed_users: List[str] = []  # Users who can access this folder
    is_public: bool = True  # If false, only allowed_users can see it
    created_by: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class SubjectFolderCreate(BaseModel):
    name: str
    description: Optional[str] = None
    subcategories: List[str] = []
    is_public: bool = True
    allowed_users: List[str] = []

class SubjectFolderUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    subcategories: Optional[List[str]] = None
    is_active: Optional[bool] = None
    is_public: Optional[bool] = None
    allowed_users: Optional[List[str]] = None

class QuizAttempt(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    quiz_id: str
    user_id: str
    answers: List[str]
    correct_answers: List[str] = []  # Store correct answers for review
    question_results: List[dict] = []  # Detailed question results
    score: int  # Number of questions correct
    total_questions: int
    percentage: float  # Percentage of questions correct
    earned_points: int = 0  # Total points earned
    total_possible_points: int = 0  # Total points possible
    points_percentage: float = 0.0  # Percentage of points earned
    passed: bool = False  # Whether user passed based on min_pass_percentage
    attempted_at: datetime = Field(default_factory=datetime.utcnow)
    time_taken_minutes: Optional[int] = None  # Time taken to complete quiz

class PasswordChange(BaseModel):
    current_password: str
    new_password: str

class UserQuizAccess(BaseModel):
    quiz_id: str
    user_ids: List[str]

class QuizAttemptCreate(BaseModel):
    quiz_id: str
    answers: List[str]

# Real-time Quiz Session Models
class QuizSessionStatus(str, Enum):
    PENDING = "pending"
    ACTIVE = "active" 
    PAUSED = "paused"
    COMPLETED = "completed"
    EXPIRED = "expired"

class QuizSession(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    quiz_id: str
    user_id: str
    status: QuizSessionStatus = QuizSessionStatus.PENDING
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    time_limit_minutes: Optional[int] = None  # Session-specific time limit
    time_remaining_seconds: Optional[int] = None  # Current remaining time
    current_question_index: int = 0  # Track current question
    answers: List[str] = []  # Current answers (partial submission)
    is_auto_submit: bool = False  # Whether session will auto-submit
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    last_activity: datetime = Field(default_factory=datetime.utcnow)  # For session timeout

class QuizSessionCreate(BaseModel):
    quiz_id: str
    time_limit_minutes: Optional[int] = None  # Override quiz default time limit

class QuizSessionUpdate(BaseModel):
    current_question_index: Optional[int] = None
    answers: Optional[List[str]] = None
    status: Optional[QuizSessionStatus] = None

class QuizSessionResponse(BaseModel):
    id: str
    quiz_id: str
    quiz_title: str
    user_id: str
    status: QuizSessionStatus
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    time_limit_minutes: Optional[int] = None
    time_remaining_seconds: Optional[int] = None
    current_question_index: int
    total_questions: int
    answers: List[str]
    is_auto_submit: bool
    created_at: datetime
    last_activity: datetime

# Q&A Discussion System Models
class QuestionStatus(str, Enum):
    OPEN = "open"
    ANSWERED = "answered"
    CLOSED = "closed"

class Question(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    content: str
    image: Optional[str] = None  # Base64 encoded image
    user_id: str
    subject: Optional[str] = None  # Link to quiz subjects for categorization
    subcategory: Optional[str] = None
    tags: List[str] = []
    upvotes: int = 0
    downvotes: int = 0
    upvoted_by: List[str] = []  # List of user IDs who upvoted
    downvoted_by: List[str] = []  # List of user IDs who downvoted
    status: QuestionStatus = QuestionStatus.OPEN
    answer_count: int = 0
    has_accepted_answer: bool = False
    is_pinned: bool = False  # Admin can pin important questions
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class QuestionCreate(BaseModel):
    title: str
    content: str
    image: Optional[str] = None
    subject: Optional[str] = None
    subcategory: Optional[str] = None
    tags: List[str] = []

class QuestionUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    image: Optional[str] = None
    subject: Optional[str] = None
    subcategory: Optional[str] = None
    tags: Optional[List[str]] = None
    status: Optional[QuestionStatus] = None
    is_pinned: Optional[bool] = None

class Answer(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    question_id: str
    content: str
    image: Optional[str] = None  # Base64 encoded image
    user_id: str
    upvotes: int = 0
    downvotes: int = 0
    upvoted_by: List[str] = []
    downvoted_by: List[str] = []
    is_accepted: bool = False  # Marked as best answer by question author
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class AnswerCreate(BaseModel):
    content: str
    image: Optional[str] = None

class AnswerUpdate(BaseModel):
    content: Optional[str] = None
    image: Optional[str] = None
    is_accepted: Optional[bool] = None

class Discussion(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    question_id: str
    user_id: str
    message: str
    image: Optional[str] = None  # Base64 encoded image
    reply_to_id: Optional[str] = None  # For threaded conversations
    upvotes: int = 0
    downvotes: int = 0
    upvoted_by: List[str] = []
    downvoted_by: List[str] = []
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class DiscussionCreate(BaseModel):
    message: str
    image: Optional[str] = None
    reply_to_id: Optional[str] = None

class DiscussionUpdate(BaseModel):
    message: Optional[str] = None
    image: Optional[str] = None

# Vote related models
class VoteType(str, Enum):
    UPVOTE = "upvote"
    DOWNVOTE = "downvote"
    REMOVE = "remove"

class VoteRequest(BaseModel):
    vote_type: VoteType

class Category(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

# Comprehensive Quiz Validation
def validate_quiz_data(quiz_data: QuizCreate) -> List[QuizValidationError]:
    """Validate quiz data and return list of errors"""
    errors = []
    
    # Basic quiz validation
    if not quiz_data.title or len(quiz_data.title.strip()) < 3:
        errors.append(QuizValidationError(
            field="title", 
            message="Title must be at least 3 characters long"
        ))
    
    if not quiz_data.description or len(quiz_data.description.strip()) < 10:
        errors.append(QuizValidationError(
            field="description", 
            message="Description must be at least 10 characters long"
        ))
    
    if not quiz_data.category or len(quiz_data.category.strip()) < 2:
        errors.append(QuizValidationError(
            field="category", 
            message="Category is required and must be at least 2 characters"
        ))
    
    if not quiz_data.subject or len(quiz_data.subject.strip()) < 2:
        errors.append(QuizValidationError(
            field="subject", 
            message="Subject folder is required"
        ))
    
    # Questions validation
    if not quiz_data.questions or len(quiz_data.questions) == 0:
        errors.append(QuizValidationError(
            field="questions", 
            message="At least one question is required"
        ))
    
    # Individual question validation
    for i, question in enumerate(quiz_data.questions):
        question_errors = validate_question(question, i)
        errors.extend(question_errors)
    
    # Pass percentage validation
    if quiz_data.min_pass_percentage < 0 or quiz_data.min_pass_percentage > 100:
        errors.append(QuizValidationError(
            field="min_pass_percentage", 
            message="Pass percentage must be between 0 and 100"
        ))
    
    # Time limit validation
    if quiz_data.time_limit_minutes is not None and quiz_data.time_limit_minutes <= 0:
        errors.append(QuizValidationError(
            field="time_limit_minutes", 
            message="Time limit must be positive if specified"
        ))
    
    return errors

def validate_question(question: QuizQuestion, question_index: int) -> List[QuizValidationError]:
    """Validate individual question"""
    errors = []
    
    # Basic question validation
    if not question.question_text or len(question.question_text.strip()) < 5:
        errors.append(QuizValidationError(
            field="question_text", 
            message="Question text must be at least 5 characters long",
            question_index=question_index
        ))
    
    # Points validation
    if question.points <= 0:
        errors.append(QuizValidationError(
            field="points", 
            message="Question points must be positive",
            question_index=question_index
        ))
    
    # Type-specific validation
    if question.question_type == QuestionType.MULTIPLE_CHOICE:
        errors.extend(validate_multiple_choice_question(question, question_index))
    elif question.question_type == QuestionType.OPEN_ENDED:
        errors.extend(validate_open_ended_question(question, question_index))
    
    return errors

def validate_multiple_choice_question(question: QuizQuestion, question_index: int) -> List[QuizValidationError]:
    """Validate multiple choice question"""
    errors = []
    
    # Options validation
    if not question.options or len(question.options) < 2:
        errors.append(QuizValidationError(
            field="options", 
            message="Multiple choice question must have at least 2 options",
            question_index=question_index
        ))
        return errors
    
    if len(question.options) > 6:
        errors.append(QuizValidationError(
            field="options", 
            message="Multiple choice question cannot have more than 6 options",
            question_index=question_index
        ))
    
    # Check if all options have text
    for i, option in enumerate(question.options):
        if not option.text or len(option.text.strip()) < 1:
            errors.append(QuizValidationError(
                field="options", 
                message=f"Option {i+1} cannot be empty",
                question_index=question_index
            ))
    
    # Check correct answers
    correct_count = sum(1 for option in question.options if option.is_correct)
    if correct_count == 0:
        errors.append(QuizValidationError(
            field="options", 
            message="At least one option must be marked as correct",
            question_index=question_index
        ))
    
    if not question.multiple_correct and correct_count > 1:
        errors.append(QuizValidationError(
            field="options", 
            message="Only one option can be correct unless multiple correct answers are enabled",
            question_index=question_index
        ))
    
    return errors

def validate_open_ended_question(question: QuizQuestion, question_index: int) -> List[QuizValidationError]:
    """Validate open-ended question"""
    errors = []
    
    if not question.open_ended_answer:
        errors.append(QuizValidationError(
            field="open_ended_answer", 
            message="Open-ended question must have expected answer(s)",
            question_index=question_index
        ))
        return errors
    
    if not question.open_ended_answer.expected_answers or len(question.open_ended_answer.expected_answers) == 0:
        errors.append(QuizValidationError(
            field="expected_answers", 
            message="At least one expected answer is required",
            question_index=question_index
        ))
    
    # Check that expected answers are not empty
    for i, answer in enumerate(question.open_ended_answer.expected_answers):
        if not answer or len(answer.strip()) < 1:
            errors.append(QuizValidationError(
                field="expected_answers", 
                message=f"Expected answer {i+1} cannot be empty",
                question_index=question_index
            ))
    
    return errors
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

@api_router.post("/auth/change-password")
async def change_password(password_data: PasswordChange, current_user: User = Depends(get_current_user)):
    """Change user password"""
    # Get current user with password
    user_doc = await db.users.find_one({"id": current_user.id})
    if not user_doc:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Verify current password
    if not verify_password(password_data.current_password, user_doc["password"]):
        raise HTTPException(status_code=400, detail="Current password is incorrect")
    
    # Hash new password
    new_hashed_password = hash_password(password_data.new_password)
    
    # Update password
    await db.users.update_one(
        {"id": current_user.id},
        {"$set": {"password": new_hashed_password}}
    )
    
    return {"message": "Password updated successfully"}

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
    """Create quiz with comprehensive validation (admin only)"""
    # Validate quiz data
    validation_errors = validate_quiz_data(quiz_data)
    if validation_errors:
        error_messages = []
        for error in validation_errors:
            if error.question_index is not None:
                error_messages.append(f"Question {error.question_index + 1}: {error.message}")
            else:
                error_messages.append(f"{error.field}: {error.message}")
        
        raise HTTPException(
            status_code=400, 
            detail={
                "message": "Quiz validation failed",
                "errors": error_messages,
                "validation_errors": [error.dict() for error in validation_errors]
            }
        )
    
    # Calculate total points
    total_points = sum(question.points for question in quiz_data.questions)
    
    # Create quiz with admin ownership
    quiz = Quiz(**quiz_data.dict(), created_by=admin_user.id)
    quiz.total_questions = len(quiz.questions)
    quiz.total_points = total_points
    quiz.updated_at = datetime.utcnow()
    quiz.is_draft = True  # Start as draft
    quiz.quiz_owner_type = "admin"
    quiz.quiz_owner_id = admin_user.id
    
    await db.quizzes.insert_one(quiz.dict())
    return quiz

@api_router.post("/admin/quiz/{quiz_id}/publish")
async def publish_quiz(quiz_id: str, admin_user: User = Depends(get_admin_user)):
    """Publish quiz (make it available to users)"""
    quiz = await db.quizzes.find_one({"id": quiz_id})
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")
    
    if quiz["created_by"] != admin_user.id:
        raise HTTPException(status_code=403, detail="You can only publish quizzes you created")
    
    # Re-validate quiz before publishing
    quiz_obj = Quiz(**quiz)
    validation_errors = validate_quiz_data(QuizCreate(**quiz))
    if validation_errors:
        raise HTTPException(
            status_code=400, 
            detail="Cannot publish quiz with validation errors. Please fix the errors first."
        )
    
    # Publish quiz
    await db.quizzes.update_one(
        {"id": quiz_id},
        {"$set": {
            "is_draft": False,
            "updated_at": datetime.utcnow()
        }}
    )
    
    return {"message": "Quiz published successfully"}

@api_router.post("/admin/quiz/{quiz_id}/preview-token")
async def generate_preview_token(quiz_id: str, admin_user: User = Depends(get_admin_user)):
    """Generate preview token for quiz"""
    quiz = await db.quizzes.find_one({"id": quiz_id})
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")
    
    if quiz["created_by"] != admin_user.id:
        raise HTTPException(status_code=403, detail="You can only preview quizzes you created")
    
    # Generate preview token
    preview_token = str(uuid.uuid4())
    
    await db.quizzes.update_one(
        {"id": quiz_id},
        {"$set": {
            "preview_token": preview_token,
            "updated_at": datetime.utcnow()
        }}
    )
    
    return {
        "preview_token": preview_token,
        "preview_url": f"/quiz/{quiz_id}/preview/{preview_token}"
    }

@api_router.get("/admin/quiz/{quiz_id}/validate")
async def validate_quiz(quiz_id: str, admin_user: User = Depends(get_admin_user)):
    """Validate quiz and return any errors"""
    quiz = await db.quizzes.find_one({"id": quiz_id})
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")
    
    if quiz["created_by"] != admin_user.id:
        raise HTTPException(status_code=403, detail="You can only validate quizzes you created")
    
    # Validate quiz
    try:
        quiz_create_data = QuizCreate(**quiz)
        validation_errors = validate_quiz_data(quiz_create_data)
        
        return {
            "is_valid": len(validation_errors) == 0,
            "errors": [error.dict() for error in validation_errors],
            "total_questions": len(quiz.get("questions", [])),
            "total_points": sum(q.get("points", 1) for q in quiz.get("questions", []))
        }
    except Exception as e:
        return {
            "is_valid": False,
            "errors": [{"field": "general", "message": f"Quiz structure error: {str(e)}"}]
        }

@api_router.put("/admin/quiz/{quiz_id}", response_model=Quiz)
async def update_quiz(quiz_id: str, quiz_data: QuizUpdate, admin_user: User = Depends(get_admin_user)):
    """Update quiz with enhanced question editing (admin only - only creator can edit)"""
    # Check if quiz exists and user is the creator
    existing_quiz = await db.quizzes.find_one({"id": quiz_id})
    if not existing_quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")
    
    if existing_quiz["created_by"] != admin_user.id:
        raise HTTPException(status_code=403, detail="You can only edit quizzes you created")
    
    # Update fields
    update_data = {k: v for k, v in quiz_data.dict().items() if v is not None}
    update_data["updated_at"] = datetime.utcnow()
    
    # Recalculate total questions if questions are updated
    if "questions" in update_data:
        update_data["total_questions"] = len(update_data["questions"])
        
        # If questions are updated, reset statistics
        update_data["total_attempts"] = 0
        update_data["average_score"] = 0.0
    
    await db.quizzes.update_one({"id": quiz_id}, {"$set": update_data})
    
    # Return updated quiz
    updated_quiz = await db.quizzes.find_one({"id": quiz_id})
    return Quiz(**updated_quiz)

@api_router.get("/admin/quiz/{quiz_id}/edit-details")
async def get_quiz_edit_details(quiz_id: str, admin_user: User = Depends(get_admin_user)):
    """Get detailed quiz information for editing including all questions"""
    quiz = await db.quizzes.find_one({"id": quiz_id})
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")
    
    if quiz["created_by"] != admin_user.id:
        raise HTTPException(status_code=403, detail="You can only edit quizzes you created")
    
    # Return full quiz details with all questions for editing
    return {
        "quiz": Quiz(**quiz),
        "total_attempts": quiz.get("total_attempts", 0),
        "average_score": quiz.get("average_score", 0.0),
        "last_updated": quiz.get("updated_at", quiz.get("created_at"))
    }

@api_router.post("/admin/quiz/{quiz_id}/access")
async def set_quiz_access(quiz_id: str, access_data: UserQuizAccess, admin_user: User = Depends(get_admin_user)):
    """Set which users can access a public quiz (admin only)"""
    quiz = await db.quizzes.find_one({"id": quiz_id})
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")
    
    if quiz["created_by"] != admin_user.id:
        raise HTTPException(status_code=403, detail="You can only modify access for quizzes you created")
    
    await db.quizzes.update_one(
        {"id": quiz_id}, 
        {"$set": {"allowed_users": access_data.user_ids, "updated_at": datetime.utcnow()}}
    )
    
    return {"message": "Quiz access updated successfully"}

@api_router.get("/admin/quiz/{quiz_id}/leaderboard")
async def get_quiz_leaderboard(quiz_id: str, admin_user: User = Depends(get_admin_user)):
    """Get top 3 performers for a quiz (admin only) - based on FIRST attempts only"""
    # Get all attempts for this quiz
    attempts = await db.quiz_attempts.find({"quiz_id": quiz_id}).to_list(1000)
    
    # Group by user and get FIRST attempt for each user (not best)
    user_first_attempts = {}
    for attempt in attempts:
        user_id = attempt["user_id"]
        if user_id not in user_first_attempts or attempt["attempted_at"] < user_first_attempts[user_id]["attempted_at"]:
            user_first_attempts[user_id] = attempt
    
    # Sort by percentage and get top 3 (based on first attempts only)
    top_attempts = sorted(user_first_attempts.values(), key=lambda x: x["percentage"], reverse=True)[:3]
    
    # Enrich with user information
    leaderboard = []
    for i, attempt in enumerate(top_attempts):
        user = await db.users.find_one({"id": attempt["user_id"]})
        leaderboard.append({
            "rank": i + 1,
            "user_name": user.get("name", "Unknown User") if user else "Unknown User",
            "user_email": user.get("email", "Unknown Email") if user else "Unknown Email",
            "score": attempt["score"],
            "total_questions": attempt["total_questions"],
            "percentage": attempt["percentage"],
            "attempted_at": attempt["attempted_at"],
            "is_first_attempt": True  # Indicator that this is user's first attempt
        })
    
    return leaderboard

@api_router.get("/admin/quizzes", response_model=List[Quiz])
async def get_all_quizzes_admin(admin_user: User = Depends(get_admin_user)):
    """Get all quizzes (admin only) - sorted by creation date with enhanced fields"""
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
        if 'is_public' not in quiz:
            quiz['is_public'] = False
        if 'allowed_users' not in quiz:
            quiz['allowed_users'] = []
        if 'subject' not in quiz:
            quiz['subject'] = quiz.get('subject_folder', 'General')
        if 'subcategory' not in quiz:
            quiz['subcategory'] = 'General'
        if 'updated_at' not in quiz:
            quiz['updated_at'] = quiz.get('created_at', datetime.utcnow())
        if 'total_attempts' not in quiz:
            quiz['total_attempts'] = 0
        if 'average_score' not in quiz:
            quiz['average_score'] = 0.0
        # Handle ownership fields for backwards compatibility
        if 'quiz_owner_type' not in quiz:
            quiz['quiz_owner_type'] = 'admin'  # Legacy quizzes are admin-created
        if 'quiz_owner_id' not in quiz:
            quiz['quiz_owner_id'] = quiz['created_by']
            
        try:
            valid_quizzes.append(Quiz(**quiz))
        except Exception as e:
            # Skip invalid quiz records
            print(f"Skipping invalid quiz: {quiz.get('id', 'unknown')} - {str(e)}")
            continue
    
    # Sort by creation date (newest first)
    valid_quizzes.sort(key=lambda x: x.created_at, reverse=True)
    
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
    """Get all accessible admin-created quizzes only"""
    # Get all active, published quizzes from admin only
    all_quizzes = await db.quizzes.find({"is_active": True}).to_list(1000)
    
    accessible_quizzes = []
    for quiz in all_quizzes:
        # CRITICAL: Exclude draft quizzes explicitly - security requirement
        if quiz.get('is_draft', False) is True:
            continue  # Skip draft quizzes - they should not be visible to users
            
        # Handle old quizzes without required fields (same as admin function)
        if 'category' not in quiz:
            quiz['category'] = 'Uncategorized'
        if 'created_by' not in quiz:
            quiz['created_by'] = 'system'
        if 'is_active' not in quiz:
            quiz['is_active'] = True
        if 'is_public' not in quiz:
            quiz['is_public'] = False
        if 'allowed_users' not in quiz:
            quiz['allowed_users'] = []
        if 'subject' not in quiz:
            quiz['subject'] = quiz.get('subject_folder', 'General')
        if 'subcategory' not in quiz:
            quiz['subcategory'] = 'General'
        if 'updated_at' not in quiz:
            quiz['updated_at'] = quiz.get('created_at', datetime.utcnow())
        if 'total_attempts' not in quiz:
            quiz['total_attempts'] = 0
        if 'average_score' not in quiz:
            quiz['average_score'] = 0.0
        # Handle ownership fields for backwards compatibility
        if 'quiz_owner_type' not in quiz:
            quiz['quiz_owner_type'] = 'admin'  # Legacy quizzes are admin-created
        if 'quiz_owner_id' not in quiz:
            quiz['quiz_owner_id'] = quiz['created_by']
        
        try:
            # Only include admin-created quizzes
            quiz_owner_type = quiz.get('quiz_owner_type', 'admin')
            
            if quiz_owner_type == 'admin':
                # Admin quizzes: Include if public and user is in allowed_users list, or if not public (legacy behavior)
                if quiz.get("is_public", False) and current_user.id in quiz.get("allowed_users", []):
                    accessible_quizzes.append(Quiz(**quiz))
                elif not quiz.get("is_public", False):
                    # For backward compatibility, include non-public admin quizzes (legacy behavior)
                    accessible_quizzes.append(Quiz(**quiz))
            # User-created quizzes are no longer included - admin-only content
        except Exception as e:
            # Skip invalid quiz records
            print(f"Skipping invalid quiz: {quiz.get('id', 'unknown')} - {str(e)}")
            continue
    
    # Sort by creation date (newest first)
    accessible_quizzes.sort(key=lambda x: x.created_at, reverse=True)
    
    return accessible_quizzes

@api_router.get("/quiz/{quiz_id}/leaderboard")
async def get_public_quiz_leaderboard(quiz_id: str, current_user: User = Depends(get_current_user)):
    """Get top 3 performers for a quiz (public view) - based on FIRST attempts only"""
    # Check if user can access this quiz
    quiz = await db.quizzes.find_one({"id": quiz_id, "is_active": True, "is_draft": False})
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")
    
    # Check access permissions
    if quiz.get("is_public", False) and current_user.id not in quiz.get("allowed_users", []):
        raise HTTPException(status_code=403, detail="You don't have access to this quiz")
    
    # Get all attempts for this quiz
    attempts = await db.quiz_attempts.find({"quiz_id": quiz_id}).to_list(1000)
    
    # Group by user and get FIRST attempt for each user (not best)
    user_first_attempts = {}
    for attempt in attempts:
        user_id = attempt["user_id"]
        if user_id not in user_first_attempts or attempt["attempted_at"] < user_first_attempts[user_id]["attempted_at"]:
            user_first_attempts[user_id] = attempt
    
    # Sort by percentage and get top 3 (based on first attempts only)
    top_attempts = sorted(user_first_attempts.values(), key=lambda x: x["percentage"], reverse=True)[:3]
    
    # Enrich with user information (anonymized for privacy)
    leaderboard = []
    for i, attempt in enumerate(top_attempts):
        user = await db.users.find_one({"id": attempt["user_id"]})
        # Only show first name + last initial for privacy
        full_name = user.get("name", "Anonymous") if user else "Anonymous"
        display_name = full_name.split()[0] + " " + full_name.split()[-1][0] + "." if len(full_name.split()) > 1 else full_name
        
        leaderboard.append({
            "rank": i + 1,
            "user_name": display_name,
            "score": attempt["score"],
            "total_questions": attempt["total_questions"],
            "percentage": attempt["percentage"],
            "attempted_at": attempt["attempted_at"],
            "is_first_attempt": True  # Indicator that this is user's first attempt
        })
    
    return leaderboard

@api_router.get("/quiz/{quiz_id}", response_model=Quiz)
async def get_quiz(quiz_id: str, current_user: User = Depends(get_current_user)):
    """Get specific quiz"""
    quiz = await db.quizzes.find_one({"id": quiz_id, "is_active": True})
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")
    
    # CRITICAL: Exclude draft quizzes explicitly - security requirement
    if quiz.get('is_draft', False) is True:
        raise HTTPException(status_code=404, detail="Quiz not found")
    
    return Quiz(**quiz)

@api_router.post("/quiz/{quiz_id}/attempt", response_model=QuizAttempt)
async def submit_quiz_attempt(quiz_id: str, attempt_data: QuizAttemptCreate, current_user: User = Depends(get_current_user)):
    """Submit quiz attempt with enhanced question type support (users only)"""
    if current_user.role == UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Admins cannot take quizzes")
    
    # Get quiz
    quiz = await db.quizzes.find_one({"id": quiz_id, "is_active": True, "is_draft": False})
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found or not published")
    
    # Check access permissions for public quizzes
    if quiz.get("is_public", False) and current_user.id not in quiz.get("allowed_users", []):
        raise HTTPException(status_code=403, detail="You don't have access to this quiz")
    
    quiz_obj = Quiz(**quiz)
    
    # Calculate score and track detailed results
    score = 0
    total_possible_points = sum(question.points for question in quiz_obj.questions)
    earned_points = 0
    correct_answers = []
    question_results = []
    
    for i, user_answer in enumerate(attempt_data.answers):
        if i < len(quiz_obj.questions):
            question = quiz_obj.questions[i]
            
            if question.question_type == QuestionType.MULTIPLE_CHOICE:
                result = grade_multiple_choice_question(question, user_answer, i)
            elif question.question_type == QuestionType.OPEN_ENDED:
                result = grade_open_ended_question(question, user_answer, i)
            else:
                result = {
                    "question_number": i + 1,
                    "question_text": question.question_text,
                    "question_type": question.question_type,
                    "user_answer": user_answer,
                    "correct_answer": "Unknown",
                    "is_correct": False,
                    "points_earned": 0,
                    "points_possible": question.points,
                    "explanation": "Unknown question type"
                }
            
            question_results.append(result)
            correct_answers.append(result["correct_answer"])
            
            if result["is_correct"]:
                score += 1
            
            earned_points += result["points_earned"]
    
    # Calculate percentages
    percentage = (score / len(quiz_obj.questions) * 100) if len(quiz_obj.questions) > 0 else 0
    points_percentage = (earned_points / total_possible_points * 100) if total_possible_points > 0 else 0
    
    # Determine if user passed
    passed = points_percentage >= quiz.get("min_pass_percentage", 60.0)
    
    # Create enhanced attempt record
    attempt = QuizAttempt(
        quiz_id=quiz_id,
        user_id=current_user.id,
        answers=attempt_data.answers,
        correct_answers=correct_answers,
        question_results=question_results,
        score=score,
        total_questions=len(quiz_obj.questions),
        percentage=percentage,
        earned_points=int(round(earned_points)),  # Convert float to int
        total_possible_points=total_possible_points,
        points_percentage=points_percentage,
        passed=passed
    )
    
    await db.quiz_attempts.insert_one(attempt.dict())
    
    # Update quiz statistics
    await update_quiz_statistics(quiz_id)
    
    return attempt

def grade_multiple_choice_question(question: QuizQuestion, user_answer: str, question_index: int) -> dict:
    """Grade a multiple choice question"""
    correct_options = [opt.text for opt in question.options if opt.is_correct]
    
    if question.multiple_correct:
        # For multiple correct answers, user_answer should be comma-separated
        user_answers = [ans.strip() for ans in user_answer.split(',') if ans.strip()]
        correct_count = len([ans for ans in user_answers if ans in correct_options])
        incorrect_count = len([ans for ans in user_answers if ans not in correct_options])
        missed_count = len([opt for opt in correct_options if opt not in user_answers])
        
        # Partial credit calculation
        if correct_count == len(correct_options) and incorrect_count == 0:
            points_earned = question.points  # Full credit
            is_correct = True
        elif correct_count > 0 and incorrect_count == 0:
            points_earned = question.points * (correct_count / len(correct_options))  # Partial credit
            is_correct = False
        else:
            points_earned = 0  # Incorrect answers present
            is_correct = False
        
        correct_answer = ", ".join(correct_options)
    else:
        # Single correct answer
        is_correct = user_answer in correct_options
        points_earned = question.points if is_correct else 0
        correct_answer = correct_options[0] if correct_options else "No correct answer"
    
    return {
        "question_number": question_index + 1,
        "question_text": question.question_text,
        "question_type": question.question_type,
        "user_answer": user_answer,
        "correct_answer": correct_answer,
        "is_correct": is_correct,
        "points_earned": points_earned,
        "points_possible": question.points,
        "all_options": [opt.text for opt in question.options],
        "question_image": question.image_url,
        "question_pdf": question.pdf_url,
        "explanation": question.explanation,
        "difficulty": question.difficulty
    }

def grade_open_ended_question(question: QuizQuestion, user_answer: str, question_index: int) -> dict:
    """Grade an open-ended question"""
    if not question.open_ended_answer:
        return {
            "question_number": question_index + 1,
            "question_text": question.question_text,
            "question_type": question.question_type,
            "user_answer": user_answer,
            "correct_answer": "No expected answer defined",
            "is_correct": False,
            "points_earned": 0,
            "points_possible": question.points,
            "explanation": "Question configuration error"
        }
    
    expected_answers = question.open_ended_answer.expected_answers
    keywords = question.open_ended_answer.keywords
    case_sensitive = question.open_ended_answer.case_sensitive
    partial_credit = question.open_ended_answer.partial_credit
    
    user_answer_processed = user_answer if case_sensitive else user_answer.lower()
    
    # Check for exact matches
    is_exact_match = False
    for expected in expected_answers:
        expected_processed = expected if case_sensitive else expected.lower()
        if user_answer_processed.strip() == expected_processed.strip():
            is_exact_match = True
            break
    
    # Check for keyword matches if partial credit is enabled
    keyword_matches = 0
    if keywords and partial_credit:
        for keyword in keywords:
            keyword_processed = keyword if case_sensitive else keyword.lower()
            if keyword_processed in user_answer_processed:
                keyword_matches += 1
    
    # Calculate points
    if is_exact_match:
        points_earned = question.points
        is_correct = True
    elif keyword_matches > 0 and partial_credit:
        points_earned = question.points * (keyword_matches / len(keywords)) * 0.5  # 50% max for partial
        is_correct = False
    else:
        points_earned = 0
        is_correct = False
    
    return {
        "question_number": question_index + 1,
        "question_text": question.question_text,
        "question_type": question.question_type,
        "user_answer": user_answer,
        "correct_answer": " OR ".join(expected_answers),
        "is_correct": is_correct,
        "points_earned": points_earned,
        "points_possible": question.points,
        "keyword_matches": keyword_matches,
        "total_keywords": len(keywords),
        "question_image": question.image_url,
        "question_pdf": question.pdf_url,
        "explanation": question.explanation,
        "difficulty": question.difficulty
    }

async def update_quiz_statistics(quiz_id: str):
    """Update quiz statistics after a new attempt"""
    # Get all attempts for this quiz
    attempts = await db.quiz_attempts.find({"quiz_id": quiz_id}).to_list(1000)
    
    if attempts:
        total_attempts = len(attempts)
        total_percentage = sum(attempt["percentage"] for attempt in attempts)
        average_score = total_percentage / total_attempts
        
        # Update quiz document
        await db.quizzes.update_one(
            {"id": quiz_id},
            {
                "$set": {
                    "total_attempts": total_attempts,
                    "average_score": round(average_score, 1),
                    "updated_at": datetime.utcnow()
                }
            }
        )

@api_router.get("/quiz/{quiz_id}/results-ranking")
async def get_quiz_results_ranking(quiz_id: str, current_user: User = Depends(get_current_user)):
    """Get ranked results for a quiz with top performers and user's position - based on FIRST attempts only"""
    # Check if user can access this quiz
    quiz = await db.quizzes.find_one({"id": quiz_id, "is_active": True, "is_draft": False})
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")
    
    # Check access permissions
    if quiz.get("is_public", False) and current_user.id not in quiz.get("allowed_users", []):
        raise HTTPException(status_code=403, detail="You don't have access to this quiz")
    
    # Get all attempts for this quiz
    attempts = await db.quiz_attempts.find({"quiz_id": quiz_id}).to_list(1000)
    
    # Group by user and get FIRST attempt for each user (not best)
    user_first_attempts = {}
    for attempt in attempts:
        user_id = attempt["user_id"]
        if user_id not in user_first_attempts or attempt["attempted_at"] < user_first_attempts[user_id]["attempted_at"]:
            user_first_attempts[user_id] = attempt
    
    # Create ranking list
    ranking = []
    for attempt in user_first_attempts.values():
        user = await db.users.find_one({"id": attempt["user_id"]})
        if user:
            ranking.append({
                "user_id": attempt["user_id"],
                "user_name": user["name"],
                "user_email": user["email"],
                "score": attempt["score"],
                "total_questions": attempt["total_questions"],
                "percentage": attempt["percentage"],
                "attempted_at": attempt["attempted_at"],
                "is_first_attempt": True  # Indicator that this is user's first attempt
            })
    
    # Sort by percentage (highest first), then by date (earliest first for same percentage)
    ranking.sort(key=lambda x: (-x["percentage"], x["attempted_at"]))
    
    # Add rank numbers
    for i, entry in enumerate(ranking):
        entry["rank"] = i + 1
    
    # Find current user's position (based on their first attempt)
    user_rank = None
    user_entry = None
    for entry in ranking:
        if entry["user_id"] == current_user.id:
            user_rank = entry["rank"]
            user_entry = entry
            break
    
    return {
        "quiz_title": quiz["title"],
        "total_participants": len(ranking),
        "top_3": ranking[:3],
        "full_ranking": ranking,
        "user_position": {
            "rank": user_rank,
            "entry": user_entry
        } if user_rank else None,
        "quiz_stats": {
            "total_attempts": quiz.get("total_attempts", 0),
            "average_score": quiz.get("average_score", 0.0)
        },
        "ranking_note": "Rankings based on users' first quiz attempts only"
    }

@api_router.get("/my-attempts", response_model=List[QuizAttempt])
async def get_my_attempts(current_user: User = Depends(get_current_user)):
    """Get current user's quiz attempts"""
    attempts = await db.quiz_attempts.find({"user_id": current_user.id}).to_list(1000)
    return [QuizAttempt(**attempt) for attempt in attempts]

# Real-time Quiz Session Management
@api_router.post("/quiz-session/start", response_model=QuizSessionResponse)
async def start_quiz_session(session_data: QuizSessionCreate, current_user: User = Depends(get_current_user)):
    """Start a new real-time quiz session"""
    if current_user.role == UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Admins cannot take quizzes")
    
    # Get quiz
    quiz = await db.quizzes.find_one({"id": session_data.quiz_id, "is_active": True, "is_draft": False})
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found or not published")
    
    # Check access permissions
    if quiz.get("is_public", False) and current_user.id not in quiz.get("allowed_users", []):
        raise HTTPException(status_code=403, detail="You don't have access to this quiz")
    
    # Check if user already has an active session for this quiz
    existing_session = await db.quiz_sessions.find_one({
        "quiz_id": session_data.quiz_id,
        "user_id": current_user.id,
        "status": {"$in": ["pending", "active", "paused"]}
    })
    
    if existing_session:
        raise HTTPException(status_code=400, detail="You already have an active session for this quiz")
    
    # Determine time limit (session override or quiz default)
    time_limit = session_data.time_limit_minutes or quiz.get("time_limit_minutes")
    time_remaining = time_limit * 60 if time_limit else None  # Convert to seconds
    
    # Create new session
    session = QuizSession(
        quiz_id=session_data.quiz_id,
        user_id=current_user.id,
        status=QuizSessionStatus.PENDING,
        time_limit_minutes=time_limit,
        time_remaining_seconds=time_remaining,
        is_auto_submit=time_limit is not None  # Auto-submit if there's a time limit
    )
    
    await db.quiz_sessions.insert_one(session.dict())
    
    # Return session with quiz info
    return QuizSessionResponse(
        id=session.id,
        quiz_id=session.quiz_id,
        quiz_title=quiz["title"],
        user_id=session.user_id,
        status=session.status,
        start_time=session.start_time,
        end_time=session.end_time,
        time_limit_minutes=session.time_limit_minutes,
        time_remaining_seconds=session.time_remaining_seconds,
        current_question_index=session.current_question_index,
        total_questions=len(quiz.get("questions", [])),
        answers=session.answers,
        is_auto_submit=session.is_auto_submit,
        created_at=session.created_at,
        last_activity=session.last_activity
    )

@api_router.post("/quiz-session/{session_id}/activate")
async def activate_quiz_session(session_id: str, current_user: User = Depends(get_current_user)):
    """Activate a pending quiz session (start the timer)"""
    session = await db.quiz_sessions.find_one({"id": session_id, "user_id": current_user.id})
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    if session["status"] != QuizSessionStatus.PENDING:
        raise HTTPException(status_code=400, detail="Session is not in pending state")
    
    # Activate session
    start_time = datetime.utcnow()
    update_data = {
        "status": QuizSessionStatus.ACTIVE,
        "start_time": start_time,
        "updated_at": start_time,
        "last_activity": start_time
    }
    
    await db.quiz_sessions.update_one({"id": session_id}, {"$set": update_data})
    
    # Get updated session with quiz info
    updated_session = await db.quiz_sessions.find_one({"id": session_id})
    quiz = await db.quizzes.find_one({"id": updated_session["quiz_id"]})
    
    return QuizSessionResponse(
        id=updated_session["id"],
        quiz_id=updated_session["quiz_id"],
        quiz_title=quiz["title"],
        user_id=updated_session["user_id"],
        status=QuizSessionStatus(updated_session["status"]),
        start_time=updated_session["start_time"],
        end_time=updated_session.get("end_time"),
        time_limit_minutes=updated_session.get("time_limit_minutes"),
        time_remaining_seconds=updated_session.get("time_remaining_seconds"),
        current_question_index=updated_session["current_question_index"],
        total_questions=len(quiz.get("questions", [])),
        answers=updated_session["answers"],
        is_auto_submit=updated_session["is_auto_submit"],
        created_at=updated_session["created_at"],
        last_activity=updated_session["last_activity"]
    )

@api_router.get("/quiz-session/{session_id}/status", response_model=QuizSessionResponse)
async def get_quiz_session_status(session_id: str, current_user: User = Depends(get_current_user)):
    """Get current status of a quiz session with real-time timer updates"""
    session = await db.quiz_sessions.find_one({"id": session_id, "user_id": current_user.id})
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    quiz = await db.quizzes.find_one({"id": session["quiz_id"]})
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")
    
    # Calculate remaining time if session is active
    time_remaining_seconds = session.get("time_remaining_seconds")
    if session["status"] == QuizSessionStatus.ACTIVE and session.get("start_time") and time_remaining_seconds:
        elapsed_seconds = (datetime.utcnow() - session["start_time"]).total_seconds()
        time_remaining_seconds = max(0, time_remaining_seconds - int(elapsed_seconds))
        
        # Auto-expire session if time is up
        if time_remaining_seconds <= 0 and session["status"] == QuizSessionStatus.ACTIVE:
            await db.quiz_sessions.update_one(
                {"id": session_id},
                {"$set": {
                    "status": QuizSessionStatus.EXPIRED,
                    "end_time": datetime.utcnow(),
                    "updated_at": datetime.utcnow()
                }}
            )
            session["status"] = QuizSessionStatus.EXPIRED
            session["end_time"] = datetime.utcnow()
    
    return QuizSessionResponse(
        id=session["id"],
        quiz_id=session["quiz_id"],
        quiz_title=quiz["title"],
        user_id=session["user_id"],
        status=QuizSessionStatus(session["status"]),
        start_time=session.get("start_time"),
        end_time=session.get("end_time"),
        time_limit_minutes=session.get("time_limit_minutes"),
        time_remaining_seconds=time_remaining_seconds,
        current_question_index=session["current_question_index"],
        total_questions=len(quiz.get("questions", [])),
        answers=session["answers"],
        is_auto_submit=session["is_auto_submit"],
        created_at=session["created_at"],
        last_activity=session["last_activity"]
    )

@api_router.put("/quiz-session/{session_id}/update")  
async def update_quiz_session(session_id: str, update_data: QuizSessionUpdate, current_user: User = Depends(get_current_user)):
    """Update quiz session progress (save answers, update current question)"""
    session = await db.quiz_sessions.find_one({"id": session_id, "user_id": current_user.id})
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    if session["status"] not in [QuizSessionStatus.ACTIVE, QuizSessionStatus.PAUSED]:
        raise HTTPException(status_code=400, detail="Session is not active")
    
    # Check if session has expired
    if session.get("start_time") and session.get("time_remaining_seconds"):
        elapsed_seconds = (datetime.utcnow() - session["start_time"]).total_seconds()
        time_remaining = max(0, session["time_remaining_seconds"] - int(elapsed_seconds))
        
        if time_remaining <= 0:
            await db.quiz_sessions.update_one(
                {"id": session_id},
                {"$set": {
                    "status": QuizSessionStatus.EXPIRED,
                    "end_time": datetime.utcnow(),
                    "updated_at": datetime.utcnow()
                }}
            )
            raise HTTPException(status_code=400, detail="Session has expired")
    
    # Update session data
    update_fields = {
        "updated_at": datetime.utcnow(),
        "last_activity": datetime.utcnow()
    }
    
    if update_data.current_question_index is not None:
        update_fields["current_question_index"] = update_data.current_question_index
    
    if update_data.answers is not None:
        update_fields["answers"] = update_data.answers
    
    if update_data.status is not None:
        update_fields["status"] = update_data.status
    
    await db.quiz_sessions.update_one({"id": session_id}, {"$set": update_fields})
    
    return {"message": "Session updated successfully"}

@api_router.post("/quiz-session/{session_id}/submit", response_model=QuizAttempt)
async def submit_quiz_session(session_id: str, current_user: User = Depends(get_current_user)):
    """Submit quiz session and create final attempt record"""
    session = await db.quiz_sessions.find_one({"id": session_id, "user_id": current_user.id})
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    if session["status"] not in [QuizSessionStatus.ACTIVE, QuizSessionStatus.PAUSED, QuizSessionStatus.EXPIRED]:
        raise HTTPException(status_code=400, detail="Session cannot be submitted")
    
    # Get quiz
    quiz = await db.quizzes.find_one({"id": session["quiz_id"]})
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")
    
    # Calculate actual time taken
    time_taken_minutes = None
    if session.get("start_time"):
        elapsed_seconds = (datetime.utcnow() - session["start_time"]).total_seconds()
        time_taken_minutes = int(elapsed_seconds / 60)
    
    # Create quiz attempt using existing grading logic
    attempt_data = QuizAttemptCreate(
        quiz_id=session["quiz_id"],
        answers=session["answers"]
    )
    
    # Use existing submit_quiz_attempt logic for grading
    quiz_obj = Quiz(**quiz)
    
    # Calculate score and track detailed results (copied from existing function)
    score = 0
    total_possible_points = sum(question.points for question in quiz_obj.questions)
    earned_points = 0
    correct_answers = []
    question_results = []
    
    for i, user_answer in enumerate(attempt_data.answers):
        if i < len(quiz_obj.questions):
            question = quiz_obj.questions[i]
            
            if question.question_type == QuestionType.MULTIPLE_CHOICE:
                result = grade_multiple_choice_question(question, user_answer, i)
            elif question.question_type == QuestionType.OPEN_ENDED:
                result = grade_open_ended_question(question, user_answer, i)
            else:
                result = {
                    "question_number": i + 1,
                    "question_text": question.question_text,
                    "question_type": question.question_type,
                    "user_answer": user_answer,
                    "correct_answer": "Unknown",
                    "is_correct": False,
                    "points_earned": 0,
                    "points_possible": question.points,
                    "explanation": "Unknown question type"
                }
            
            question_results.append(result)
            correct_answers.append(result["correct_answer"])
            
            if result["is_correct"]:
                score += 1
            
            earned_points += result["points_earned"]
    
    # Calculate percentages
    percentage = (score / len(quiz_obj.questions) * 100) if len(quiz_obj.questions) > 0 else 0
    points_percentage = (earned_points / total_possible_points * 100) if total_possible_points > 0 else 0
    
    # Determine if user passed
    passed = points_percentage >= quiz.get("min_pass_percentage", 60.0)
    
    # Create enhanced attempt record
    attempt = QuizAttempt(
        quiz_id=session["quiz_id"],
        user_id=current_user.id,
        answers=attempt_data.answers,
        correct_answers=correct_answers,
        question_results=question_results,
        score=score,
        total_questions=len(quiz_obj.questions),
        percentage=percentage,
        earned_points=int(round(earned_points)),
        total_possible_points=total_possible_points,
        points_percentage=points_percentage,
        passed=passed,
        time_taken_minutes=time_taken_minutes
    )
    
    await db.quiz_attempts.insert_one(attempt.dict())
    
    # Update session to completed
    await db.quiz_sessions.update_one(
        {"id": session_id},
        {"$set": {
            "status": QuizSessionStatus.COMPLETED,
            "end_time": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }}
    )
    
    # Update quiz statistics
    await update_quiz_statistics(session["quiz_id"])
    
    return attempt

@api_router.get("/quiz-session/{session_id}/pause")
async def pause_quiz_session(session_id: str, current_user: User = Depends(get_current_user)):
    """Pause an active quiz session"""
    session = await db.quiz_sessions.find_one({"id": session_id, "user_id": current_user.id})
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    if session["status"] != QuizSessionStatus.ACTIVE:
        raise HTTPException(status_code=400, detail="Only active sessions can be paused")
    
    await db.quiz_sessions.update_one(
        {"id": session_id},
        {"$set": {
            "status": QuizSessionStatus.PAUSED,
            "updated_at": datetime.utcnow()
        }}
    )
    
    return {"message": "Session paused successfully"}

@api_router.get("/quiz-session/{session_id}/resume")
async def resume_quiz_session(session_id: str, current_user: User = Depends(get_current_user)):
    """Resume a paused quiz session"""
    session = await db.quiz_sessions.find_one({"id": session_id, "user_id": current_user.id})
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    if session["status"] != QuizSessionStatus.PAUSED:
        raise HTTPException(status_code=400, detail="Only paused sessions can be resumed")
    
    await db.quiz_sessions.update_one(
        {"id": session_id},
        {"$set": {
            "status": QuizSessionStatus.ACTIVE,
            "updated_at": datetime.utcnow(),
            "last_activity": datetime.utcnow()
        }}
    )
    
    return {"message": "Session resumed successfully"}

@api_router.get("/my-quiz-sessions", response_model=List[QuizSessionResponse])
async def get_my_quiz_sessions(current_user: User = Depends(get_current_user)):
    """Get all quiz sessions for current user"""
    sessions = await db.quiz_sessions.find({"user_id": current_user.id}).to_list(1000)
    
    session_responses = []
    for session in sessions:
        quiz = await db.quizzes.find_one({"id": session["quiz_id"]})
        if quiz:
            session_responses.append(QuizSessionResponse(
                id=session["id"],
                quiz_id=session["quiz_id"],
                quiz_title=quiz["title"],
                user_id=session["user_id"],
                status=QuizSessionStatus(session["status"]),
                start_time=session.get("start_time"),
                end_time=session.get("end_time"),
                time_limit_minutes=session.get("time_limit_minutes"),
                time_remaining_seconds=session.get("time_remaining_seconds"),
                current_question_index=session["current_question_index"],
                total_questions=len(quiz.get("questions", [])),
                answers=session["answers"],
                is_auto_submit=session["is_auto_submit"],
                created_at=session["created_at"],
                last_activity=session["last_activity"]
            ))
    
    # Sort by last activity (most recent first)
    session_responses.sort(key=lambda x: x.last_activity, reverse=True)
    
    return session_responses

# Enhanced Media Upload (Images and PDFs)
@api_router.post("/admin/upload-file")
async def upload_file(file: UploadFile = File(...), admin_user: User = Depends(get_admin_user)):
    """Upload file (image or PDF) for quiz questions (admin only)"""
    # Validate file type
    allowed_image_types = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'image/webp']
    allowed_pdf_types = ['application/pdf']
    allowed_types = allowed_image_types + allowed_pdf_types
    
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=400, 
            detail=f"File type not supported. Allowed types: {', '.join(allowed_types)}"
        )
    
    # Validate file size (max 10MB for PDFs, 5MB for images)
    content = await file.read()
    max_size = 10 * 1024 * 1024 if file.content_type in allowed_pdf_types else 5 * 1024 * 1024
    
    if len(content) > max_size:
        size_limit = "10MB" if file.content_type in allowed_pdf_types else "5MB"
        raise HTTPException(status_code=400, detail=f"File size must be less than {size_limit}")
    
    # Validate file format for images
    if file.content_type in allowed_image_types:
        # Skip additional image format validation since content_type is already validated
        pass
    
    # Generate unique filename
    file_id = str(uuid.uuid4())
    file_extension = file.filename.split('.')[-1] if '.' in file.filename else (
        'pdf' if file.content_type in allowed_pdf_types else 'jpg'
    )
    filename = f"{file_id}.{file_extension}"
    
    # Convert to base64 for storage (in production, use cloud storage)
    base64_content = base64.b64encode(content).decode('utf-8')
    
    # Determine file category
    file_category = 'pdf' if file.content_type in allowed_pdf_types else 'image'
    
    # Store file metadata in database
    file_data = {
        "id": file_id,
        "filename": filename,
        "original_name": file.filename,
        "content_type": file.content_type,
        "category": file_category,
        "size": len(content),
        "base64_data": base64_content,
        "uploaded_by": admin_user.id,
        "uploaded_at": datetime.utcnow()
    }
    
    await db.files.insert_one(file_data)
    
    # Return file URL (base64 data URL)
    data_url = f"data:{file.content_type};base64,{base64_content}"
    
    return {
        "id": file_id,
        "filename": filename,
        "original_name": file.filename,
        "url": data_url,
        "size": len(content),
        "category": file_category,
        "content_type": file.content_type
    }

@api_router.get("/file/{file_id}")
async def get_file(file_id: str):
    """Get file by ID (public access for quiz files)"""
    file_doc = await db.files.find_one({"id": file_id})
    if not file_doc:
        raise HTTPException(status_code=404, detail="File not found")
    
    # Return base64 data URL
    data_url = f"data:{file_doc['content_type']};base64,{file_doc['base64_data']}"
    return {
        "url": data_url,
        "filename": file_doc['filename'],
        "original_name": file_doc['original_name'],
        "content_type": file_doc['content_type'],
        "size": file_doc['size']
    }

@api_router.get("/admin/files")
async def get_admin_files(admin_user: User = Depends(get_admin_user)):
    """Get all uploaded files for admin"""
    files = await db.files.find({"uploaded_by": admin_user.id}).to_list(1000)
    
    file_list = []
    for file_doc in files:
        file_list.append({
            "id": file_doc["id"],
            "filename": file_doc["filename"],
            "original_name": file_doc["original_name"],
            "content_type": file_doc["content_type"],
            "category": file_doc.get("category", "unknown"),
            "size": file_doc["size"],
            "uploaded_at": file_doc["uploaded_at"]
        })
    
    return file_list

@api_router.delete("/admin/file/{file_id}")
async def delete_file(file_id: str, admin_user: User = Depends(get_admin_user)):
    """Delete uploaded file (admin only)"""
    file_doc = await db.files.find_one({"id": file_id})
    if not file_doc:
        raise HTTPException(status_code=404, detail="File not found")
    
    if file_doc["uploaded_by"] != admin_user.id:
        raise HTTPException(status_code=403, detail="You can only delete files you uploaded")
    
    # Check if file is used in any quiz questions
    quizzes_using_file = await db.quizzes.find({
        "$or": [
            {"questions.image_url": {"$regex": file_id}},
            {"questions.pdf_url": {"$regex": file_id}}
        ]
    }).to_list(10)
    
    if quizzes_using_file:
        quiz_titles = [quiz.get("title", "Unknown") for quiz in quizzes_using_file]
        raise HTTPException(
            status_code=400, 
            detail=f"Cannot delete file. It is used in {len(quizzes_using_file)} quiz(s): {', '.join(quiz_titles[:3])}"
        )
    
    # Delete file
    await db.files.delete_one({"id": file_id})
    
    return {"message": "File deleted successfully"}
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
    
    # Validate image format - skip additional validation since content_type is already validated
    
    # Generate unique filename
    file_id = str(uuid.uuid4())
    file_extension = file.filename.split('.')[-1] if '.' in file.filename else 'jpg'
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
        email="admin@squiz.com",
        name="System Administrator",
        role=UserRole.ADMIN
    )
    
    admin_dict = admin_user.dict()
    admin_dict["password"] = admin_password
    
    await db.users.insert_one(admin_dict)
    
    return {
        "message": "Admin user created successfully",
        "email": "admin@squiz.com",
        "password": "admin123"
    }

# General Routes
@api_router.get("/")
async def root():
    return {"message": "Squiz API - Admin Centered Version"}

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
@api_router.get("/admin/subjects-structure")
async def get_subjects_structure(admin_user: User = Depends(get_admin_user)):
    """Get nested subject structure (Subject -> Subcategories -> Quizzes)"""
    quizzes = await db.quizzes.find({"is_active": True}).to_list(1000)
    
    subjects = {}
    for quiz in quizzes:
        subject = quiz.get("subject", "General")
        subcategory = quiz.get("subcategory", "General")
        
        if subject not in subjects:
            subjects[subject] = {
                "name": subject,
                "subcategories": {},
                "total_quizzes": 0
            }
        
        if subcategory not in subjects[subject]["subcategories"]:
            subjects[subject]["subcategories"][subcategory] = {
                "name": subcategory,
                "quizzes": [],
                "quiz_count": 0
            }
        
        # Add quiz info
        quiz_info = {
            "id": quiz["id"],
            "title": quiz["title"],
            "category": quiz.get("category", ""),
            "created_at": quiz["created_at"],
            "is_public": quiz.get("is_public", False),
            "total_questions": quiz.get("total_questions", 0),
            "total_attempts": quiz.get("total_attempts", 0),
            "average_score": quiz.get("average_score", 0.0)
        }
        
        subjects[subject]["subcategories"][subcategory]["quizzes"].append(quiz_info)
        subjects[subject]["subcategories"][subcategory]["quiz_count"] += 1
        subjects[subject]["total_quizzes"] += 1
    
    # Sort quizzes by creation date within each subcategory
    for subject in subjects.values():
        for subcategory in subject["subcategories"].values():
            subcategory["quizzes"].sort(key=lambda x: x["created_at"], reverse=True)
    
    return subjects

# Global Subject Management Models
class GlobalSubfolder(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: Optional[str] = None

class GlobalSubject(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: Optional[str] = None
    subfolders: List[GlobalSubfolder] = []
    created_by: str  # Admin user ID
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class GlobalSubjectCreate(BaseModel):
    name: str
    description: Optional[str] = None
    subfolders: List[str] = []  # List of subfolder names

class GlobalSubjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    subfolders: Optional[List[str]] = None

class PersonalSubject(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: Optional[str] = None
    subfolders: List[str] = []  # Simple list of subfolder names
    user_id: str  # User who created this
    created_at: datetime = Field(default_factory=datetime.utcnow)

class PersonalSubjectCreate(BaseModel):
    name: str
    description: Optional[str] = None
    subfolders: List[str] = []

# Global Subject Management API Endpoints

@api_router.post("/admin/global-subject", response_model=GlobalSubject)
async def create_global_subject(subject_data: GlobalSubjectCreate, admin_user: User = Depends(get_admin_user)):
    """Create global subject with subfolders (admin only)"""
    # Check if subject already exists
    existing = await db.global_subjects.find_one({"name": subject_data.name})
    if existing:
        raise HTTPException(status_code=400, detail=f"Global subject '{subject_data.name}' already exists")
    
    # Create subfolders
    subfolders = []
    for subfolder_name in subject_data.subfolders:
        subfolder = GlobalSubfolder(name=subfolder_name)
        subfolders.append(subfolder)
    
    # Create global subject
    global_subject = GlobalSubject(
        name=subject_data.name,
        description=subject_data.description,
        subfolders=subfolders,
        created_by=admin_user.id
    )
    
    await db.global_subjects.insert_one(global_subject.dict())
    return global_subject

@api_router.get("/admin/global-subjects", response_model=List[GlobalSubject])
async def get_all_global_subjects(admin_user: User = Depends(get_admin_user)):
    """Get all global subjects with subfolders (admin only)"""
    subjects = await db.global_subjects.find().to_list(1000)
    return [GlobalSubject(**subject) for subject in subjects]

@api_router.put("/admin/global-subject/{subject_id}", response_model=GlobalSubject)
async def update_global_subject(
    subject_id: str, 
    subject_data: GlobalSubjectUpdate, 
    admin_user: User = Depends(get_admin_user)
):
    """Update global subject (admin only)"""
    existing = await db.global_subjects.find_one({"id": subject_id})
    if not existing:
        raise HTTPException(status_code=404, detail="Global subject not found")
    
    update_data = {k: v for k, v in subject_data.dict().items() if v is not None}
    
    if "subfolders" in update_data:
        # Convert subfolder names to GlobalSubfolder objects
        subfolders = []
        for subfolder_name in update_data["subfolders"]:
            subfolder = GlobalSubfolder(name=subfolder_name)
            subfolders.append(subfolder.dict())
        update_data["subfolders"] = subfolders
    
    update_data["updated_at"] = datetime.utcnow()
    
    await db.global_subjects.update_one({"id": subject_id}, {"$set": update_data})
    
    updated_subject = await db.global_subjects.find_one({"id": subject_id})
    return GlobalSubject(**updated_subject)

@api_router.post("/admin/global-subject/{subject_id}/subfolder")
async def add_subfolder_to_global_subject(
    subject_id: str,
    subfolder_name: str,
    admin_user: User = Depends(get_admin_user)
):
    """Add subfolder to existing global subject (admin only)"""
    subject = await db.global_subjects.find_one({"id": subject_id})
    if not subject:
        raise HTTPException(status_code=404, detail="Global subject not found")
    
    # Check if subfolder already exists
    existing_subfolders = [sf["name"] for sf in subject.get("subfolders", [])]
    if subfolder_name in existing_subfolders:
        raise HTTPException(status_code=400, detail=f"Subfolder '{subfolder_name}' already exists")
    
    new_subfolder = GlobalSubfolder(name=subfolder_name)
    
    await db.global_subjects.update_one(
        {"id": subject_id},
        {
            "$push": {"subfolders": new_subfolder.dict()},
            "$set": {"updated_at": datetime.utcnow()}
        }
    )
    
    return {"message": f"Subfolder '{subfolder_name}' added successfully"}

@api_router.delete("/admin/global-subject/{subject_id}")
async def delete_global_subject(subject_id: str, admin_user: User = Depends(get_admin_user)):
    """Delete global subject (admin only)"""
    # Check if any quizzes are using this subject
    quizzes_using_subject = await db.quizzes.find({"subject": subject_id}).to_list(10)
    if quizzes_using_subject:
        raise HTTPException(
            status_code=400, 
            detail=f"Cannot delete subject. {len(quizzes_using_subject)} quiz(es) are using this subject."
        )
    
    result = await db.global_subjects.delete_one({"id": subject_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Global subject not found")
    
    return {"message": "Global subject deleted successfully"}

@api_router.delete("/admin/global-subject/{subject_id}/subfolder/{subfolder_id}")
async def delete_global_subfolder(
    subject_id: str, 
    subfolder_id: str, 
    admin_user: User = Depends(get_admin_user)
):
    """Delete specific subfolder from global subject (admin only)"""
    subject = await db.global_subjects.find_one({"id": subject_id})
    if not subject:
        raise HTTPException(status_code=404, detail="Global subject not found")
    
    # Check if any quizzes are using this subfolder
    quizzes_using_subfolder = await db.quizzes.find({
        "subject": subject_id, 
        "subcategory": subfolder_id
    }).to_list(10)
    
    if quizzes_using_subfolder:
        raise HTTPException(
            status_code=400, 
            detail=f"Cannot delete subfolder. {len(quizzes_using_subfolder)} quiz(es) are using this subfolder."
        )
    
    await db.global_subjects.update_one(
        {"id": subject_id},
        {
            "$pull": {"subfolders": {"id": subfolder_id}},
            "$set": {"updated_at": datetime.utcnow()}
        }
    )
    
    return {"message": "Subfolder deleted successfully"}

# User Quiz Creation and Management API Endpoints

# User personal subject creation removed - admin-only functionality

@api_router.get("/user/available-subjects")
async def get_available_subjects_for_user(current_user: User = Depends(get_current_user)):
    """Get list of admin-created global subjects only"""
    # Get global subjects (admin-created only)
    global_subjects = await db.global_subjects.find().to_list(1000)
    global_formatted = []
    for subject in global_subjects:
        global_formatted.append({
            "id": subject["id"],
            "name": subject["name"],
            "description": subject.get("description", ""),
            "subfolders": [
                {"id": sf["id"], "name": sf["name"], "description": sf.get("description", "")}
                for sf in subject.get("subfolders", [])
            ],
            "type": "global",
            "icon": "🌐"
        })
    
    return {
        "global_subjects": global_formatted,
        "personal_subjects": [],  # No personal subjects allowed
        "combined": global_formatted  # Only global subjects
    }

# User quiz creation removed - admin-only functionality

# User quiz management removed - admin-only functionality

# User quiz update/delete/publish functions removed - admin-only functionality

# Enhanced Folder Management for Admin
@api_router.post("/admin/subject-folder", response_model=SubjectFolder)
async def create_subject_folder(folder_data: SubjectFolderCreate, admin_user: User = Depends(get_admin_user)):
    """Create new subject folder with access control"""
    # Check if folder already exists
    existing = await db.subject_folders.find_one({"name": folder_data.name, "is_active": True})
    if existing:
        raise HTTPException(status_code=400, detail="Subject folder already exists")
    
    # Create new subject folder
    folder = SubjectFolder(
        **folder_data.dict(),
        created_by=admin_user.id
    )
    
    await db.subject_folders.insert_one(folder.dict())
    return folder

@api_router.get("/admin/subject-folders", response_model=List[SubjectFolder])
async def get_all_subject_folders(admin_user: User = Depends(get_admin_user)):
    """Get all subject folders for admin management"""
    folders = await db.subject_folders.find({"is_active": True}).to_list(1000)
    return [SubjectFolder(**folder) for folder in folders]

@api_router.put("/admin/subject-folder/{folder_id}", response_model=SubjectFolder)
async def update_subject_folder(folder_id: str, folder_data: SubjectFolderUpdate, admin_user: User = Depends(get_admin_user)):
    """Update subject folder"""
    existing = await db.subject_folders.find_one({"id": folder_id, "is_active": True})
    if not existing:
        raise HTTPException(status_code=404, detail="Subject folder not found")
    
    # Update data
    update_data = {k: v for k, v in folder_data.dict().items() if v is not None}
    update_data["updated_at"] = datetime.utcnow()
    
    await db.subject_folders.update_one({"id": folder_id}, {"$set": update_data})
    
    # Return updated folder
    updated_folder = await db.subject_folders.find_one({"id": folder_id})
    return SubjectFolder(**updated_folder)

@api_router.delete("/admin/subject-folder/{folder_id}")
async def delete_subject_folder(folder_id: str, admin_user: User = Depends(get_admin_user)):
    """Delete subject folder (soft delete)"""
    existing = await db.subject_folders.find_one({"id": folder_id, "is_active": True})
    if not existing:
        raise HTTPException(status_code=404, detail="Subject folder not found")
    
    # Check if there are quizzes in this folder
    quizzes_in_folder = await db.quizzes.find({"subject": existing["name"], "is_active": True}).to_list(10)
    if quizzes_in_folder:
        raise HTTPException(status_code=400, detail=f"Cannot delete folder with {len(quizzes_in_folder)} quizzes. Move quizzes first.")
    
    # Soft delete
    await db.subject_folders.update_one(
        {"id": folder_id}, 
        {"$set": {"is_active": False, "updated_at": datetime.utcnow()}}
    )
    
    return {"message": "Subject folder deleted successfully"}

@api_router.post("/admin/quiz/{quiz_id}/move-folder")
async def move_quiz_to_folder(quiz_id: str, new_subject: str, new_subcategory: str = "General", admin_user: User = Depends(get_admin_user)):
    """Move quiz to different folder/subject"""
    # Check if quiz exists
    quiz = await db.quizzes.find_one({"id": quiz_id})
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")
    
    # Check if admin is the creator
    if quiz["created_by"] != admin_user.id:
        raise HTTPException(status_code=403, detail="You can only move quizzes you created")
    
    # Check if target folder exists
    target_folder = await db.subject_folders.find_one({"name": new_subject, "is_active": True})
    if not target_folder:
        raise HTTPException(status_code=404, detail="Target subject folder not found")
    
    # Update quiz location
    await db.quizzes.update_one(
        {"id": quiz_id},
        {"$set": {
            "subject": new_subject,
            "subcategory": new_subcategory,
            "updated_at": datetime.utcnow()
        }}
    )
    
    return {"message": f"Quiz moved to {new_subject} → {new_subcategory}"}

@api_router.get("/admin/folder-quiz-count")
async def get_folder_quiz_counts(admin_user: User = Depends(get_admin_user)):
    """Get quiz counts for each folder"""
    folders = await db.subject_folders.find({"is_active": True}).to_list(1000)
    folder_counts = {}
    
    for folder in folders:
        quiz_count = await db.quizzes.count_documents({
            "subject": folder["name"],
            "is_active": True
        })
        folder_counts[folder["name"]] = {
            "id": folder["id"],
            "name": folder["name"],
            "description": folder.get("description", ""),
            "quiz_count": quiz_count,
            "is_public": folder.get("is_public", True),
            "subcategories": folder.get("subcategories", [])
        }
    
    return folder_counts

@api_router.get("/admin/predefined-subjects")
async def get_predefined_subjects(admin_user: User = Depends(get_admin_user)):
    """Get admin-created subjects with their subcategories (no hardcoded subjects)"""
    admin_subjects = {}
    
    # Get admin-created global subjects from the global_subjects collection
    global_subjects = await db.global_subjects.find().to_list(1000)
    for subject in global_subjects:
        subject_name = subject.get("name", "Unknown")
        # Extract subfolder names from the subfolders array
        subfolders = []
        for subfolder in subject.get("subfolders", []):
            if isinstance(subfolder, dict):
                subfolders.append(subfolder.get("name", "General"))
            else:
                subfolders.append(str(subfolder))
        
        # If no subfolders, add "General" as default
        if not subfolders:
            subfolders = ["General"]
            
        admin_subjects[subject_name] = subfolders
    
    # Also get legacy custom subjects from subject_categories for backward compatibility
    legacy_subjects = await db.subject_categories.find().to_list(1000)
    for custom in legacy_subjects:
        subject_name = custom.get("name", custom.get("subject", "Unknown"))
        admin_subjects[subject_name] = custom.get("subcategories", ["General"])
    
    return admin_subjects
@api_router.post("/init-admin")
async def initialize_admin(_: User = Depends(get_admin_user)): # Requires admin user
    """Initialize admin user (run once)"""
    # Check if admin already exists
    admin_exists = await db.users.find_one({"role": "admin"})
    if admin_exists:
        raise HTTPException(status_code=400, detail="Admin already exists")

    # Create admin user
    admin_password = hash_password("admin123")  # Change this in production!
    admin_user = User(
        email="admin@squiz.com",
        name="System Administrator",
        role=UserRole.ADMIN
    )

    admin_dict = admin_user.dict()
    admin_dict["password"] = admin_password

    await db.users.insert_one(admin_dict)

    return {
        "message": "Admin user created successfully",
        "email": "admin@squiz.com",
        "password": "admin123"  # Remove this in production!
    }
@api_router.get("/admin/user/{user_id}/details")
async def get_user_details(user_id: str, admin_user: User = Depends(get_admin_user)):
    """Get detailed user information including quiz history and mistakes"""
    # Get user info
    user = await db.users.find_one({"id": user_id})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Get all attempts by this user
    attempts = await db.quiz_attempts.find({"user_id": user_id}).to_list(1000)
    
    # Enrich attempts with quiz information
    detailed_attempts = []
    for attempt in attempts:
        quiz = await db.quizzes.find_one({"id": attempt["quiz_id"]})
        quiz_title = quiz.get("title", "Unknown Quiz") if quiz else "Unknown Quiz"
        
        detailed_attempts.append({
            "attempt_id": attempt["id"],
            "quiz_title": quiz_title,
            "quiz_category": quiz.get("category", "Unknown") if quiz else "Unknown",
            "score": attempt["score"],
            "total_questions": attempt["total_questions"],
            "percentage": attempt["percentage"],
            "attempted_at": attempt["attempted_at"],
            "question_results": attempt.get("question_results", []),
            "mistakes": [
                result for result in attempt.get("question_results", [])
                if not result.get("is_correct", True)
            ]
        })
    
    # Sort by attempt date (newest first)
    detailed_attempts.sort(key=lambda x: x["attempted_at"], reverse=True)
    
    # Calculate statistics
    total_attempts = len(detailed_attempts)
    total_score = sum(attempt["score"] for attempt in detailed_attempts)
    total_questions = sum(attempt["total_questions"] for attempt in detailed_attempts)
    average_percentage = sum(attempt["percentage"] for attempt in detailed_attempts) / total_attempts if total_attempts > 0 else 0
    
    return {
        "user": {
            "id": user["id"],
            "name": user["name"],
            "email": user["email"],
            "role": user["role"],
            "created_at": user.get("created_at")
        },
        "statistics": {
            "total_attempts": total_attempts,
            "total_score": total_score,
            "total_questions": total_questions,
            "average_percentage": round(average_percentage, 1),
            "best_score": max([attempt["percentage"] for attempt in detailed_attempts]) if detailed_attempts else 0
        },
        "attempts": detailed_attempts
    }

# Include router
app.include_router(api_router)

# CORS Configuration for Self-Hosted and Cloud Deployment
def get_cors_origins():
    """Get allowed CORS origins from environment or use secure defaults"""
    # Get environment-specific origins
    allowed_origins = os.environ.get('ALLOWED_ORIGINS', '').split(',')
    frontend_url = os.environ.get('FRONTEND_URL', '')
    
    # Default origins for development
    default_origins = [
        "http://localhost:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001",
        "http://localhost",
        "http://127.0.0.1",
    ]
    
    # Add production frontend URL if provided
    if frontend_url:
        default_origins.append(frontend_url)
        default_origins.append(frontend_url.replace('http://', 'https://'))
    
    # Add Render.com patterns for production
    render_patterns = [
        "https://*.onrender.com",
        "https://squiz-frontend.onrender.com",
        "https://squiz-backend.onrender.com"
    ]
    default_origins.extend(render_patterns)
    
    # Add server IP addresses for self-hosted
    try:
        import socket
        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)
        default_origins.extend([
            f"http://{local_ip}:3000",
            f"http://{local_ip}",
            f"https://{local_ip}:3000", 
            f"https://{local_ip}"
        ])
    except:
        pass
    
    # Combine environment origins with defaults
    all_origins = list(set(default_origins + [origin.strip() for origin in allowed_origins if origin.strip()]))
    
    # Remove empty strings
    all_origins = [origin for origin in all_origins if origin]
    
    logging.info(f"CORS allowed origins: {all_origins}")
    return all_origins

# Apply CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=get_cors_origins(),
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=[
        "Accept",
        "Accept-Language", 
        "Content-Language",
        "Content-Type",
        "Authorization",
        "X-Requested-With",
        "X-CSRF-Token"
    ],
    expose_headers=["Content-Range", "X-Content-Range"],
    max_age=600  # Cache preflight requests for 10 minutes
)

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Startup event - Initialize admin user
@app.on_event("startup")
async def startup_initialize():
    """Initialize application on startup"""
    logger.info("🚀 Starting Squiz application...")
    
    # Create admin user if it doesn't exist
    admin_email = "admin@squiz.com"
    existing_admin = await db.users.find_one({"email": admin_email})
    
    if not existing_admin:
        logger.info("📝 Creating default admin user...")
        admin_user = User(
            email=admin_email,
            name="Squiz Administrator",
            role=UserRole.ADMIN
        )
        admin_dict = admin_user.dict()
        admin_dict["password"] = hash_password("admin123")
        
        await db.users.insert_one(admin_dict)
        logger.info(f"✅ Admin user created: {admin_email}")
    else:
        logger.info(f"✅ Admin user already exists: {admin_email}")
    
    # Log deployment information
    is_production = os.environ.get('RENDER', False) or os.environ.get('NODE_ENV') == 'production'
    env_type = "PRODUCTION" if is_production else "DEVELOPMENT"
    
    logger.info(f"🌍 Environment: {env_type}")
    logger.info(f"🔐 JWT Secret: {'[CONFIGURED]' if os.environ.get('JWT_SECRET') else '[USING DEFAULT - UPDATE FOR PRODUCTION]'}")
    logger.info(f"🗄️  Database: {os.environ.get('DB_NAME', 'test_database')}")
    logger.info("🎯 Squiz application ready!")

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
