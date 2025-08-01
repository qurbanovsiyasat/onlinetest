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
    
    # Privacy and social settings
    is_private: bool = False  # Private profile toggle
    follower_count: int = 0  # Number of followers
    following_count: int = 0  # Number of users this user follows

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
    
    # Privacy and social settings
    is_private: bool = False
    follower_count: int = 0
    following_count: int = 0

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

# Emoji Reaction Models
class EmojiType(str, Enum):
    THUMBS_UP = "👍"
    HEART = "❤️"
    LAUGH = "😂"
    THINKING = "🤔"
    CELEBRATE = "🎉"

class AnswerReaction(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    answer_id: str
    user_id: str
    emoji: EmojiType
    created_at: datetime = Field(default_factory=datetime.utcnow)

class EmojiReactionRequest(BaseModel):
    emoji: EmojiType

class EmojiReactionStats(BaseModel):
    emoji: str
    count: int
    user_reacted: bool = False

# Social & Privacy Control Models
class FollowStatus(str, Enum):
    PENDING = "pending"  # Follow request pending approval (for private accounts)
    APPROVED = "approved"  # Follow request approved/direct follow for public accounts
    REJECTED = "rejected"  # Follow request rejected

class UserFollow(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    follower_id: str  # User who is following
    following_id: str  # User being followed
    status: FollowStatus = FollowStatus.APPROVED  # Default for public accounts
    requested_at: datetime = Field(default_factory=datetime.utcnow)
    approved_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

class FollowRequest(BaseModel):
    user_id: str

class FollowResponse(BaseModel):
    action: str  # "followed", "unfollowed", "request_sent", "request_approved", "request_rejected"
    message: str
    is_following: bool = False
    is_pending: bool = False

class UserPrivacySettings(BaseModel):
    user_id: str
    is_private: bool = False
    allow_followers_to_see_activity: bool = True
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class PrivacySettingsUpdate(BaseModel):
    is_private: Optional[bool] = None
    allow_followers_to_see_activity: Optional[bool] = None

class UserProfile(BaseModel):
    id: str
    name: str
    email: Optional[str] = None  # Hidden for non-admin viewers of private profiles
    role: UserRole
    is_active: bool
    created_at: datetime
    
    # Privacy and social
    is_private: bool = False
    follower_count: int = 0
    following_count: int = 0
    
    # Activity stats (may be hidden for private profiles)
    total_questions: Optional[int] = 0
    total_answers: Optional[int] = 0
    total_quiz_attempts: Optional[int] = 0
    average_quiz_score: Optional[float] = 0.0
    
    # Relationship status with current viewer
    is_following: bool = False
    is_pending_approval: bool = False
    can_view_activity: bool = True  # Whether current user can see this user's activity

# Notification Models for Social Features
class NotificationType(str, Enum):
    NEW_FOLLOWER = "new_follower"
    FOLLOW_REQUEST = "follow_request"
    FOLLOW_REQUEST_APPROVED = "follow_request_approved"
    NEW_QUIZ_FROM_FOLLOWED_USER = "new_quiz_from_followed_user"
    NEW_QUESTION_FROM_FOLLOWED_USER = "new_question_from_followed_user"

class Notification(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str  # Recipient of notification
    from_user_id: Optional[str] = None  # Who triggered the notification
    notification_type: NotificationType
    title: str
    message: str
    related_id: Optional[str] = None  # ID of related quiz, question, etc.
    is_read: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)

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
    
    # Note: We'll notify followers when the quiz is published, not when created as draft
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
    
    # Notify followers when admin publishes a new quiz
    await notify_followers_of_new_quiz(admin_user.id, quiz["title"], quiz_id)
    
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
    
    # Notify user about quiz result
    await notify_quiz_result(current_user.id, quiz["title"], percentage, passed)
    
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

# ====================================================================
# Q&A DISCUSSION SYSTEM API ENDPOINTS
# ====================================================================

# Helper functions for Q&A system
async def get_user_info(user_id: str):
    """Get basic user information for Q&A responses"""
    user = await db.users.find_one({"id": user_id})
    if user:
        return {
            "id": user["id"],
            "name": user["name"],
            "role": user.get("role", "user"),
            "is_admin": user.get("role") == "admin"
        }
    return {"id": user_id, "name": "Unknown User", "role": "user", "is_admin": False}

async def update_question_stats(question_id: str):
    """Update question statistics after changes"""
    answer_count = await db.answers.count_documents({"question_id": question_id})
    has_accepted_answer = bool(await db.answers.find_one({"question_id": question_id, "is_accepted": True}))
    
    status = QuestionStatus.ANSWERED if has_accepted_answer else (
        QuestionStatus.OPEN if answer_count == 0 else QuestionStatus.OPEN
    )
    
    await db.questions.update_one(
        {"id": question_id},
        {"$set": {
            "answer_count": answer_count,
            "has_accepted_answer": has_accepted_answer,
            "status": status,
            "updated_at": datetime.utcnow()
        }}
    )

# Questions API Endpoints
@api_router.get("/questions")
async def get_questions(
    subject: Optional[str] = None,
    subcategory: Optional[str] = None,
    status: Optional[str] = None,
    page: int = 1,
    limit: int = 20,
    sort_by: str = "created_at",  # created_at, upvotes, answer_count, updated_at
    sort_order: str = "desc"
):
    """Get all questions with optional filtering and pagination"""
    skip = (page - 1) * limit
    sort_direction = -1 if sort_order == "desc" else 1
    
    # Build filter
    filter_dict = {}
    if subject:
        filter_dict["subject"] = subject
    if subcategory:
        filter_dict["subcategory"] = subcategory
    if status:
        filter_dict["status"] = status
    
    # Get questions with sorting
    sort_field = sort_by if sort_by in ["created_at", "upvotes", "answer_count", "updated_at"] else "created_at"
    
    questions = await db.questions.find(filter_dict).sort(sort_field, sort_direction).skip(skip).limit(limit).to_list(limit)
    total_count = await db.questions.count_documents(filter_dict)
    
    # Enrich with user information
    enriched_questions = []
    for question in questions:
        user_info = await get_user_info(question["user_id"])
        question["user"] = user_info
        enriched_questions.append(Question(**question))
    
    return {
        "questions": enriched_questions,
        "total": total_count,
        "page": page,
        "limit": limit,
        "total_pages": (total_count + limit - 1) // limit
    }

@api_router.get("/questions/{question_id}")
async def get_question_detail(question_id: str):
    """Get detailed question with answers and discussions"""
    # Get question
    question = await db.questions.find_one({"id": question_id})
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    
    # Get question user info
    question_user = await get_user_info(question["user_id"])
    question["user"] = question_user
    
    # Get answers
    answers = await db.answers.find({"question_id": question_id}).sort("created_at", -1).to_list(100)
    enriched_answers = []
    for answer in answers:
        user_info = await get_user_info(answer["user_id"])
        answer["user"] = user_info
        enriched_answers.append(Answer(**answer))
    
    # Get discussions
    discussions = await db.discussions.find({"question_id": question_id}).sort("created_at", 1).to_list(100)
    enriched_discussions = []
    for discussion in discussions:
        user_info = await get_user_info(discussion["user_id"])
        discussion["user"] = user_info
        enriched_discussions.append(Discussion(**discussion))
    
    return {
        "question": Question(**question),
        "answers": enriched_answers,
        "discussions": enriched_discussions
    }

@api_router.post("/questions", response_model=Question)
async def create_question(question_data: QuestionCreate, current_user: User = Depends(get_current_user)):
    """Create a new question (authenticated users only)"""
    if not question_data.title.strip() or len(question_data.title.strip()) < 5:
        raise HTTPException(status_code=400, detail="Question title must be at least 5 characters long")
    
    if not question_data.content.strip() or len(question_data.content.strip()) < 10:
        raise HTTPException(status_code=400, detail="Question content must be at least 10 characters long")
    
    # Create question
    question = Question(
        **question_data.dict(),
        user_id=current_user.id
    )
    
    await db.questions.insert_one(question.dict())
    
    # Notify followers of new question
    await notify_followers_of_new_question(current_user.id, question.title, question.id)
    
    return question

@api_router.put("/questions/{question_id}", response_model=Question)
async def update_question(
    question_id: str, 
    question_data: QuestionUpdate, 
    current_user: User = Depends(get_current_user)
):
    """Update question (only by author or admin)"""
    question = await db.questions.find_one({"id": question_id})
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    
    # Check permissions
    if question["user_id"] != current_user.id and current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="You can only edit your own questions")
    
    # Update fields
    update_data = {k: v for k, v in question_data.dict().items() if v is not None}
    update_data["updated_at"] = datetime.utcnow()
    
    await db.questions.update_one({"id": question_id}, {"$set": update_data})
    
    # Return updated question
    updated_question = await db.questions.find_one({"id": question_id})
    return Question(**updated_question)

@api_router.delete("/questions/{question_id}")
async def delete_question(question_id: str, current_user: User = Depends(get_current_user)):
    """Delete question (only by author or admin)"""
    question = await db.questions.find_one({"id": question_id})
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    
    # Check permissions
    if question["user_id"] != current_user.id and current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="You can only delete your own questions")
    
    # Delete question and all related data
    await db.questions.delete_one({"id": question_id})
    await db.answers.delete_many({"question_id": question_id})
    await db.discussions.delete_many({"question_id": question_id})
    
    return {"message": "Question deleted successfully"}

# Answers API Endpoints
@api_router.post("/questions/{question_id}/answers", response_model=Answer)
async def create_answer(
    question_id: str, 
    answer_data: AnswerCreate, 
    current_user: User = Depends(get_current_user)
):
    """Add answer to question (authenticated users only)"""
    # Check if question exists
    question = await db.questions.find_one({"id": question_id})
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    
    if not answer_data.content.strip() or len(answer_data.content.strip()) < 5:
        raise HTTPException(status_code=400, detail="Answer content must be at least 5 characters long")
    
    # Create answer
    answer = Answer(
        **answer_data.dict(),
        question_id=question_id,
        user_id=current_user.id
    )
    
    await db.answers.insert_one(answer.dict())
    
    # Update question stats
    await update_question_stats(question_id)
    
    # Notify question author about new answer (if not answering own question)
    if question["user_id"] != current_user.id:
        await notify_question_answered(question_id, current_user.name)
    
    return answer

@api_router.put("/questions/{question_id}/answers/{answer_id}", response_model=Answer)
async def update_answer(
    question_id: str,
    answer_id: str,
    answer_data: AnswerUpdate,
    current_user: User = Depends(get_current_user)
):
    """Update answer (only by author or admin)"""
    answer = await db.answers.find_one({"id": answer_id, "question_id": question_id})
    if not answer:
        raise HTTPException(status_code=404, detail="Answer not found")
    
    # Check permissions for content updates
    if answer_data.content is not None or answer_data.image is not None:
        if answer["user_id"] != current_user.id and current_user.role != UserRole.ADMIN:
            raise HTTPException(status_code=403, detail="You can only edit your own answers")
    
    # Check permissions for accepting answer (only question author or admin)
    if answer_data.is_accepted is not None:
        question = await db.questions.find_one({"id": question_id})
        if question["user_id"] != current_user.id and current_user.role != UserRole.ADMIN:
            raise HTTPException(status_code=403, detail="Only the question author can accept answers")
        
        # If accepting this answer, un-accept all others
        if answer_data.is_accepted:
            await db.answers.update_many(
                {"question_id": question_id},
                {"$set": {"is_accepted": False}}
            )
    
    # Update fields
    update_data = {k: v for k, v in answer_data.dict().items() if v is not None}
    update_data["updated_at"] = datetime.utcnow()
    
    await db.answers.update_one({"id": answer_id}, {"$set": update_data})
    
    # Update question stats
    await update_question_stats(question_id)
    
    # Notify user if their answer was accepted
    if answer_data.is_accepted and answer["user_id"] != current_user.id:
        await notify_answer_accepted(answer_id)
    
    # Return updated answer
    updated_answer = await db.answers.find_one({"id": answer_id})
    return Answer(**updated_answer)

@api_router.delete("/questions/{question_id}/answers/{answer_id}")
async def delete_answer(
    question_id: str,
    answer_id: str,
    current_user: User = Depends(get_current_user)
):
    """Delete answer (only by author or admin)"""
    answer = await db.answers.find_one({"id": answer_id, "question_id": question_id})
    if not answer:
        raise HTTPException(status_code=404, detail="Answer not found")
    
    # Check permissions
    if answer["user_id"] != current_user.id and current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="You can only delete your own answers")
    
    await db.answers.delete_one({"id": answer_id})
    
    # Update question stats
    await update_question_stats(question_id)
    
    return {"message": "Answer deleted successfully"}

# Discussions API Endpoints
@api_router.get("/questions/{question_id}/discussions")
async def get_discussions(question_id: str):
    """Get all discussions for a question"""
    discussions = await db.discussions.find({"question_id": question_id}).sort("created_at", 1).to_list(100)
    
    enriched_discussions = []
    for discussion in discussions:
        user_info = await get_user_info(discussion["user_id"])
        discussion["user"] = user_info
        enriched_discussions.append(Discussion(**discussion))
    
    return enriched_discussions

@api_router.post("/questions/{question_id}/discussions", response_model=Discussion)
async def create_discussion(
    question_id: str,
    discussion_data: DiscussionCreate,
    current_user: User = Depends(get_current_user)
):
    """Add discussion message to question (authenticated users only)"""
    # Check if question exists
    question = await db.questions.find_one({"id": question_id})
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    
    if not discussion_data.message.strip() or len(discussion_data.message.strip()) < 1:
        raise HTTPException(status_code=400, detail="Discussion message cannot be empty")
    
    # Create discussion
    discussion = Discussion(
        **discussion_data.dict(),
        question_id=question_id,
        user_id=current_user.id
    )
    
    await db.discussions.insert_one(discussion.dict())
    return discussion

@api_router.put("/questions/{question_id}/discussions/{discussion_id}", response_model=Discussion)
async def update_discussion(
    question_id: str,
    discussion_id: str,
    discussion_data: DiscussionUpdate,
    current_user: User = Depends(get_current_user)
):
    """Update discussion message (only by author or admin)"""
    discussion = await db.discussions.find_one({"id": discussion_id, "question_id": question_id})
    if not discussion:
        raise HTTPException(status_code=404, detail="Discussion message not found")
    
    # Check permissions
    if discussion["user_id"] != current_user.id and current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="You can only edit your own messages")
    
    # Update fields
    update_data = {k: v for k, v in discussion_data.dict().items() if v is not None}
    update_data["updated_at"] = datetime.utcnow()
    
    await db.discussions.update_one({"id": discussion_id}, {"$set": update_data})
    
    # Return updated discussion
    updated_discussion = await db.discussions.find_one({"id": discussion_id})
    return Discussion(**updated_discussion)

@api_router.delete("/questions/{question_id}/discussions/{discussion_id}")
async def delete_discussion(
    question_id: str,
    discussion_id: str,
    current_user: User = Depends(get_current_user)
):
    """Delete discussion message (only by author or admin)"""
    discussion = await db.discussions.find_one({"id": discussion_id, "question_id": question_id})
    if not discussion:
        raise HTTPException(status_code=404, detail="Discussion message not found")
    
    # Check permissions
    if discussion["user_id"] != current_user.id and current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="You can only delete your own messages")
    
    await db.discussions.delete_one({"id": discussion_id})
    return {"message": "Discussion message deleted successfully"}

# Voting API Endpoints
@api_router.post("/questions/{question_id}/vote")
async def vote_question(
    question_id: str,
    vote_data: VoteRequest,
    current_user: User = Depends(get_current_user)
):
    """Vote on a question (upvote/downvote/remove)"""
    question = await db.questions.find_one({"id": question_id})
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    
    # Prevent voting on own question
    if question["user_id"] == current_user.id:
        raise HTTPException(status_code=400, detail="You cannot vote on your own question")
    
    user_id = current_user.id
    upvoted_by = question.get("upvoted_by", [])
    downvoted_by = question.get("downvoted_by", [])
    
    # Remove existing votes first
    if user_id in upvoted_by:
        upvoted_by.remove(user_id)
    if user_id in downvoted_by:
        downvoted_by.remove(user_id)
    
    # Add new vote
    if vote_data.vote_type == VoteType.UPVOTE:
        upvoted_by.append(user_id)
    elif vote_data.vote_type == VoteType.DOWNVOTE:
        downvoted_by.append(user_id)
    # For REMOVE, we just removed existing votes above
    
    # Update question
    await db.questions.update_one(
        {"id": question_id},
        {"$set": {
            "upvotes": len(upvoted_by),
            "downvotes": len(downvoted_by),
            "upvoted_by": upvoted_by,
            "downvoted_by": downvoted_by,
            "updated_at": datetime.utcnow()
        }}
    )
    
    return {
        "message": "Vote recorded successfully",
        "upvotes": len(upvoted_by),
        "downvotes": len(downvoted_by)
    }

@api_router.post("/answers/{answer_id}/vote")
async def vote_answer(
    answer_id: str,
    vote_data: VoteRequest,
    current_user: User = Depends(get_current_user)
):
    """Vote on an answer (upvote/downvote/remove)"""
    answer = await db.answers.find_one({"id": answer_id})
    if not answer:
        raise HTTPException(status_code=404, detail="Answer not found")
    
    # Prevent voting on own answer
    if answer["user_id"] == current_user.id:
        raise HTTPException(status_code=400, detail="You cannot vote on your own answer")
    
    user_id = current_user.id
    upvoted_by = answer.get("upvoted_by", [])
    downvoted_by = answer.get("downvoted_by", [])
    
    # Remove existing votes first
    if user_id in upvoted_by:
        upvoted_by.remove(user_id)
    if user_id in downvoted_by:
        downvoted_by.remove(user_id)
    
    # Add new vote
    if vote_data.vote_type == VoteType.UPVOTE:
        upvoted_by.append(user_id)
    elif vote_data.vote_type == VoteType.DOWNVOTE:
        downvoted_by.append(user_id)
    
    # Update answer
    await db.answers.update_one(
        {"id": answer_id},
        {"$set": {
            "upvotes": len(upvoted_by),
            "downvotes": len(downvoted_by),
            "upvoted_by": upvoted_by,
            "downvoted_by": downvoted_by,
            "updated_at": datetime.utcnow()
        }}
    )
    
    return {
        "message": "Vote recorded successfully",
        "upvotes": len(upvoted_by),
        "downvotes": len(downvoted_by)
    }

@api_router.post("/discussions/{discussion_id}/vote")
async def vote_discussion(
    discussion_id: str,
    vote_data: VoteRequest,
    current_user: User = Depends(get_current_user)
):
    """Vote on a discussion message (upvote/downvote/remove)"""
    discussion = await db.discussions.find_one({"id": discussion_id})
    if not discussion:
        raise HTTPException(status_code=404, detail="Discussion message not found")
    
    # Prevent voting on own message
    if discussion["user_id"] == current_user.id:
        raise HTTPException(status_code=400, detail="You cannot vote on your own message")
    
    user_id = current_user.id
    upvoted_by = discussion.get("upvoted_by", [])
    downvoted_by = discussion.get("downvoted_by", [])
    
    # Remove existing votes first
    if user_id in upvoted_by:
        upvoted_by.remove(user_id)
    if user_id in downvoted_by:
        downvoted_by.remove(user_id)
    
    # Add new vote
    if vote_data.vote_type == VoteType.UPVOTE:
        upvoted_by.append(user_id)
    elif vote_data.vote_type == VoteType.DOWNVOTE:
        downvoted_by.append(user_id)
    
    # Update discussion
    await db.discussions.update_one(
        {"id": discussion_id},
        {"$set": {
            "upvotes": len(upvoted_by),
            "downvotes": len(downvoted_by),
            "upvoted_by": upvoted_by,
            "downvoted_by": downvoted_by,
            "updated_at": datetime.utcnow()
        }}
    )
    
    return {
        "message": "Vote recorded successfully",
        "upvotes": len(upvoted_by),
        "downvotes": len(downvoted_by)
    }

# Admin Q&A Management Endpoints
@api_router.get("/admin/qa-stats")
async def get_qa_stats(admin_user: User = Depends(get_admin_user)):
    """Get Q&A system statistics (admin only)"""
    total_questions = await db.questions.count_documents({})
    total_answers = await db.answers.count_documents({})
    total_discussions = await db.discussions.count_documents({})
    
    # Questions by status
    open_questions = await db.questions.count_documents({"status": "open"})
    answered_questions = await db.questions.count_documents({"status": "answered"})
    closed_questions = await db.questions.count_documents({"status": "closed"})
    
    # Questions by subject
    subjects_pipeline = [
        {"$group": {"_id": "$subject", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}}
    ]
    subjects_stats = await db.questions.aggregate(subjects_pipeline).to_list(100)
    
    return {
        "total_questions": total_questions,
        "total_answers": total_answers,
        "total_discussions": total_discussions,
        "questions_by_status": {
            "open": open_questions,
            "answered": answered_questions,
            "closed": closed_questions
        },
        "questions_by_subject": subjects_stats
    }

@api_router.put("/admin/questions/{question_id}/pin")
async def toggle_question_pin(question_id: str, admin_user: User = Depends(get_admin_user)):
    """Pin/unpin a question (admin only)"""
    question = await db.questions.find_one({"id": question_id})
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    
    new_pin_status = not question.get("is_pinned", False)
    
    await db.questions.update_one(
        {"id": question_id},
        {"$set": {
            "is_pinned": new_pin_status,
            "updated_at": datetime.utcnow()
        }}
    )
    
    return {
        "message": f"Question {'pinned' if new_pin_status else 'unpinned'} successfully",
        "is_pinned": new_pin_status
    }

# Emoji Reaction Endpoints
@api_router.post("/answers/{answer_id}/react")
async def add_emoji_reaction(
    answer_id: str,
    reaction_data: EmojiReactionRequest,
    current_user: User = Depends(get_current_user)
):
    """Add or update emoji reaction to an answer"""
    # Check if answer exists
    answer = await db.answers.find_one({"id": answer_id})
    if not answer:
        raise HTTPException(status_code=404, detail="Answer not found")
    
    # Remove existing reaction from this user for this answer
    await db.answer_reactions.delete_many({
        "answer_id": answer_id,
        "user_id": current_user.id
    })
    
    # Add new reaction
    reaction = AnswerReaction(
        answer_id=answer_id,
        user_id=current_user.id,
        emoji=reaction_data.emoji
    )
    
    await db.answer_reactions.insert_one(reaction.dict())
    
    return {"message": "Reaction added successfully", "emoji": reaction_data.emoji.value}

@api_router.delete("/answers/{answer_id}/react")
async def remove_emoji_reaction(
    answer_id: str,
    current_user: User = Depends(get_current_user)
):
    """Remove user's emoji reaction from an answer"""
    result = await db.answer_reactions.delete_many({
        "answer_id": answer_id,
        "user_id": current_user.id
    })
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="No reaction found to remove")
    
    return {"message": "Reaction removed successfully"}

@api_router.get("/answers/{answer_id}/reactions")
async def get_answer_reactions(
    answer_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get emoji reaction statistics for an answer"""
    # Get all reactions for this answer
    reactions = await db.answer_reactions.find({"answer_id": answer_id}).to_list(1000)
    
    # Count reactions by emoji
    emoji_counts = {}
    user_reaction = None
    
    for reaction in reactions:
        emoji = reaction["emoji"]
        emoji_counts[emoji] = emoji_counts.get(emoji, 0) + 1
        
        if reaction["user_id"] == current_user.id:
            user_reaction = emoji
    
    # Format response
    reaction_stats = []
    for emoji, count in emoji_counts.items():
        reaction_stats.append(EmojiReactionStats(
            emoji=emoji,
            count=count,
            user_reacted=(emoji == user_reaction)
        ))
    
    return {
        "reactions": reaction_stats,
        "total_reactions": len(reactions),
        "user_reaction": user_reaction
    }

@api_router.get("/subjects-available")
async def get_available_subjects():
    """Get all subjects available in both quizzes and questions (public endpoint)"""
    # Get subjects from quizzes
    quiz_subjects = await db.quizzes.distinct("subject")
    
    # Get subjects from questions
    question_subjects = await db.questions.distinct("subject")
    
    # Combine and remove None values
    all_subjects = list(set(quiz_subjects + question_subjects))
    all_subjects = [s for s in all_subjects if s is not None]
    all_subjects.sort()
    
    return {
        "subjects": all_subjects,
        "quiz_subjects": sorted(quiz_subjects),
        "question_subjects": sorted(question_subjects)
    }

# ====================================================================
# END Q&A DISCUSSION SYSTEM API ENDPOINTS
# ====================================================================

# Router will be included at the end after all endpoints are defined

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
# =====================================
# USER PROFILE SYSTEM
# =====================================

class UserProfile(BaseModel):
    id: str
    email: Optional[str] = None  # Hidden for non-admin viewers of private profiles
    name: str
    role: UserRole
    avatar: Optional[str] = None  # Base64 encoded image
    bio: Optional[str] = None
    location: Optional[str] = None
    website: Optional[str] = None
    is_active: bool
    created_at: datetime
    
    # Privacy and social features
    is_private: bool = False
    follower_count: int = 0
    following_count: int = 0
    
    # Activity statistics
    questions_count: int = 0
    answers_count: int = 0
    quizzes_taken: int = 0
    total_quiz_score: float = 0.0
    avg_quiz_score: float = 0.0
    accepted_answers: int = 0
    
    # Social relationship status with current viewer
    is_following: bool = False
    is_pending_approval: bool = False
    can_view_activity: bool = True  # Whether current user can see this user's activity
    
    # Admin features
    is_admin: bool = False
    admin_badge: Optional[str] = None  # Admin badge text/emoji
    
    # Profile visibility for current viewer
    profile_visible: bool = True  # Whether current user can see full profile

class UserProfileUpdate(BaseModel):
    name: Optional[str] = None
    bio: Optional[str] = None
    location: Optional[str] = None
    website: Optional[str] = None
    avatar: Optional[str] = None

class NotificationType(str, Enum):
    NEW_ANSWER = "new_answer"
    ANSWER_ACCEPTED = "answer_accepted"
    REPLY_TO_ANSWER = "reply_to_answer"
    QUIZ_RESULT = "quiz_result"
    LEADERBOARD_UPDATE = "leaderboard_update"
    QUESTION_VOTE = "question_vote"
    ANSWER_VOTE = "answer_vote"
    NEW_FOLLOWER = "new_follower"
    FOLLOWED_USER_QUESTION = "followed_user_question"
    FOLLOWED_USER_QUIZ = "followed_user_quiz"

class Notification(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    type: NotificationType
    title: str
    message: str
    related_id: Optional[str] = None  # ID of related question, answer, quiz, etc.
    is_read: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)

class NotificationCreate(BaseModel):
    user_id: str
    type: NotificationType
    title: str
    message: str
    related_id: Optional[str] = None

# =====================================
# USER PROFILE ENDPOINTS
# =====================================

@api_router.get("/users/{user_id}/profile", response_model=UserProfile)
async def get_user_profile(user_id: str, current_user: User = Depends(get_current_user)):
    """Get user profile with admin access to private profiles"""
    user = await db.users.find_one({"id": user_id})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Check if current user is admin or viewing their own profile
    is_admin = current_user.role == UserRole.ADMIN
    is_own_profile = current_user.id == user_id
    is_target_private = user.get("is_private", False)
    
    # Check if user can view this profile
    can_view_full_profile = is_admin or is_own_profile or not is_target_private
    
    # Check follow relationship for private profiles
    is_following = False
    is_pending_approval = False
    
    if is_target_private and not is_admin and not is_own_profile:
        # Check if current user follows this private user
        follow_relation = await db.user_follows.find_one({
            "follower_id": current_user.id,
            "following_id": user_id
        })
        if follow_relation:
            is_following = follow_relation.get("status") == "approved"
            is_pending_approval = follow_relation.get("status") == "pending"
            can_view_full_profile = is_following
    
    # Calculate user statistics (only if can view profile)
    questions_count = 0
    answers_count = 0
    accepted_answers = 0
    quizzes_taken = 0
    total_quiz_score = 0.0
    avg_quiz_score = 0.0
    
    if can_view_full_profile:
        questions_count = await db.questions.count_documents({"user_id": user_id})
        answers_count = await db.answers.count_documents({"user_id": user_id})
        accepted_answers = await db.answers.count_documents({"user_id": user_id, "is_accepted": True})
        
        # Quiz statistics
        quiz_attempts = await db.quiz_attempts.find({"user_id": user_id}).to_list(1000)
        quizzes_taken = len(quiz_attempts)
        total_quiz_score = sum(attempt.get("percentage", 0) for attempt in quiz_attempts)
        avg_quiz_score = total_quiz_score / quizzes_taken if quizzes_taken > 0 else 0.0
    
    # Get follower/following counts
    follower_count = await db.user_follows.count_documents({"following_id": user_id, "status": "approved"})
    following_count = await db.user_follows.count_documents({"follower_id": user_id, "status": "approved"})
    
    # Determine admin badge
    admin_badge = None
    is_user_admin = user.get("role") == "admin"
    if is_user_admin:
        admin_badge = "🛡️ Admin"
    
    return UserProfile(
        id=user["id"],
        email=user["email"] if (is_admin or is_own_profile) else None,  # Hide email for non-admins viewing others
        name=user["name"],
        role=user["role"],
        avatar=user.get("avatar"),
        bio=user.get("bio") if can_view_full_profile else None,
        location=user.get("location") if can_view_full_profile else None,
        website=user.get("website") if can_view_full_profile else None,
        is_active=user["is_active"],
        created_at=user["created_at"],
        is_private=user.get("is_private", False),
        follower_count=follower_count,
        following_count=following_count,
        questions_count=questions_count if can_view_full_profile else 0,
        answers_count=answers_count if can_view_full_profile else 0,
        quizzes_taken=quizzes_taken if can_view_full_profile else 0,
        total_quiz_score=total_quiz_score if can_view_full_profile else 0.0,
        avg_quiz_score=round(avg_quiz_score, 1) if can_view_full_profile else 0.0,
        accepted_answers=accepted_answers if can_view_full_profile else 0,
        is_following=is_following,
        is_pending_approval=is_pending_approval,
        can_view_activity=can_view_full_profile,
        is_admin=is_user_admin,
        admin_badge=admin_badge,
        profile_visible=can_view_full_profile
    )

@api_router.get("/profile", response_model=UserProfile)
async def get_my_profile(current_user: User = Depends(get_current_user)):
    """Get current user's profile"""
    return await get_user_profile(current_user.id)

@api_router.put("/profile", response_model=UserProfile)
async def update_my_profile(
    profile_data: UserProfileUpdate, 
    current_user: User = Depends(get_current_user)
):
    """Update current user's profile"""
    update_data = {k: v for k, v in profile_data.dict().items() if v is not None}
    
    if update_data:
        await db.users.update_one(
            {"id": current_user.id}, 
            {"$set": update_data}
        )
    
    return await get_user_profile(current_user.id)

@api_router.get("/users/{user_id}/questions")
async def get_user_questions(user_id: str, skip: int = 0, limit: int = 20, current_user: User = Depends(get_current_user)):
    """Get questions posted by a specific user (respects privacy settings)"""
    # Check if user exists
    user = await db.users.find_one({"id": user_id})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Check if current user can view this user's activity
    is_admin = current_user.role == UserRole.ADMIN
    is_own_profile = current_user.id == user_id
    is_target_private = user.get("is_private", False)
    
    can_view_activity = is_admin or is_own_profile or not is_target_private
    
    # For private profiles, check follow relationship
    if is_target_private and not is_admin and not is_own_profile:
        follow_relation = await db.user_follows.find_one({
            "follower_id": current_user.id,
            "following_id": user_id,
            "status": "approved"
        })
        can_view_activity = bool(follow_relation)
    
    if not can_view_activity:
        return {
            "questions": [],
            "message": "This user's activity is private",
            "can_view": False
        }
    
    questions = await db.questions.find({"user_id": user_id}).sort("created_at", -1).skip(skip).limit(limit).to_list(limit)
    
    enriched_questions = []
    for question in questions:
        user_info = await get_user_info(question["user_id"])
        question["user"] = user_info
        enriched_questions.append(question)
    
    return {
        "questions": enriched_questions,
        "can_view": True
    }

@api_router.get("/users/{user_id}/answers")
async def get_user_answers(user_id: str, skip: int = 0, limit: int = 20, current_user: User = Depends(get_current_user)):
    """Get answers posted by a specific user (respects privacy settings)"""
    # Check if user exists
    user = await db.users.find_one({"id": user_id})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Check if current user can view this user's activity
    is_admin = current_user.role == UserRole.ADMIN
    is_own_profile = current_user.id == user_id
    is_target_private = user.get("is_private", False)
    
    can_view_activity = is_admin or is_own_profile or not is_target_private
    
    # For private profiles, check follow relationship
    if is_target_private and not is_admin and not is_own_profile:
        follow_relation = await db.user_follows.find_one({
            "follower_id": current_user.id,
            "following_id": user_id,
            "status": "approved"
        })
        can_view_activity = bool(follow_relation)
    
    if not can_view_activity:
        return {
            "answers": [],
            "message": "This user's activity is private",
            "can_view": False
        }
    
    answers = await db.answers.find({"user_id": user_id}).sort("created_at", -1).skip(skip).limit(limit).to_list(limit)
    
    enriched_answers = []
    for answer in answers:
        user_info = await get_user_info(answer["user_id"])
        answer["user"] = user_info
        
        # Get question info
        question = await db.questions.find_one({"id": answer["question_id"]})
        answer["question"] = {"id": question["id"], "title": question["title"]} if question else None
        
        enriched_answers.append(answer)
    
    return {
        "answers": enriched_answers,
        "can_view": True
    }

@api_router.get("/users/{user_id}/followers")
async def get_user_followers(user_id: str, skip: int = 0, limit: int = 20, current_user: User = Depends(get_current_user)):
    """Get user's followers list (respects privacy settings)"""
    # Check if user exists
    user = await db.users.find_one({"id": user_id})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Check if current user can view this user's followers
    is_admin = current_user.role == UserRole.ADMIN
    is_own_profile = current_user.id == user_id
    is_target_private = user.get("is_private", False)
    
    can_view_followers = is_admin or is_own_profile or not is_target_private
    
    # For private profiles, check follow relationship
    if is_target_private and not is_admin and not is_own_profile:
        follow_relation = await db.user_follows.find_one({
            "follower_id": current_user.id,
            "following_id": user_id,
            "status": "approved"
        })
        can_view_followers = bool(follow_relation)
    
    if not can_view_followers:
        return {
            "followers": [],
            "message": "This user's followers list is private",
            "can_view": False
        }
    
    # Get followers
    follow_relations = await db.user_follows.find({
        "following_id": user_id,
        "status": "approved"
    }).skip(skip).limit(limit).to_list(limit)
    
    followers = []
    for relation in follow_relations:
        follower = await db.users.find_one({"id": relation["follower_id"]})
        if follower:
            followers.append({
                "id": follower["id"],
                "name": follower["name"],
                "role": follower.get("role", "user"),
                "is_admin": follower.get("role") == "admin",
                "admin_badge": "🛡️ Admin" if follower.get("role") == "admin" else None,
                "avatar": follower.get("avatar"),
                "followed_at": relation.get("approved_at") or relation.get("created_at")
            })
    
    return {
        "followers": followers,
        "can_view": True
    }

@api_router.get("/users/{user_id}/following")
async def get_user_following(user_id: str, skip: int = 0, limit: int = 20, current_user: User = Depends(get_current_user)):
    """Get user's following list (respects privacy settings)"""
    # Check if user exists
    user = await db.users.find_one({"id": user_id})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Check if current user can view this user's following list
    is_admin = current_user.role == UserRole.ADMIN
    is_own_profile = current_user.id == user_id
    is_target_private = user.get("is_private", False)
    
    can_view_following = is_admin or is_own_profile or not is_target_private
    
    # For private profiles, check follow relationship
    if is_target_private and not is_admin and not is_own_profile:
        follow_relation = await db.user_follows.find_one({
            "follower_id": current_user.id,
            "following_id": user_id,
            "status": "approved"
        })
        can_view_following = bool(follow_relation)
    
    if not can_view_following:
        return {
            "following": [],
            "message": "This user's following list is private",
            "can_view": False
        }
    
    # Get following
    follow_relations = await db.user_follows.find({
        "follower_id": user_id,
        "status": "approved"
    }).skip(skip).limit(limit).to_list(limit)
    
    following = []
    for relation in follow_relations:
        followed_user = await db.users.find_one({"id": relation["following_id"]})
        if followed_user:
            following.append({
                "id": followed_user["id"],
                "name": followed_user["name"],
                "role": followed_user.get("role", "user"),
                "is_admin": followed_user.get("role") == "admin",
                "admin_badge": "🛡️ Admin" if followed_user.get("role") == "admin" else None,
                "avatar": followed_user.get("avatar"),
                "followed_at": relation.get("approved_at") or relation.get("created_at")
            })
    
    return {
        "following": following,
        "can_view": True
    }

@api_router.get("/users/{user_id}/activity")
async def get_user_activity(user_id: str, skip: int = 0, limit: int = 20, current_user: User = Depends(get_current_user)):
    """Get user's recent activity (questions, answers, quiz attempts) - respects privacy settings"""
    # Check if user exists
    user = await db.users.find_one({"id": user_id})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Check if current user can view this user's activity
    is_admin = current_user.role == UserRole.ADMIN
    is_own_profile = current_user.id == user_id
    is_target_private = user.get("is_private", False)
    
    can_view_activity = is_admin or is_own_profile or not is_target_private
    
    # For private profiles, check follow relationship
    if is_target_private and not is_admin and not is_own_profile:
        follow_relation = await db.user_follows.find_one({
            "follower_id": current_user.id,
            "following_id": user_id,
            "status": "approved"
        })
        can_view_activity = bool(follow_relation)
    
    if not can_view_activity:
        return {
            "activities": [],
            "message": "This user's activity is private",
            "can_view": False
        }
    
    activities = []
    
    # Get recent questions
    recent_questions = await db.questions.find({"user_id": user_id}).sort("created_at", -1).limit(10).to_list(10)
    for question in recent_questions:
        activities.append({
            "type": "question_posted",
            "title": f"Posted a question: {question['title']}",
            "content": question.get("content", "")[:200] + "..." if len(question.get("content", "")) > 200 else question.get("content", ""),
            "created_at": question["created_at"],
            "link": f"/questions/{question['id']}",
            "subject": question.get("subject"),
            "upvotes": question.get("upvotes", 0)
        })
    
    # Get recent answers
    recent_answers = await db.answers.find({"user_id": user_id}).sort("created_at", -1).limit(10).to_list(10)
    for answer in recent_answers:
        # Get question title
        question = await db.questions.find_one({"id": answer["question_id"]})
        question_title = question["title"] if question else "Unknown Question"
        
        activities.append({
            "type": "answer_posted",
            "title": f"Answered: {question_title}",
            "content": answer.get("content", "")[:200] + "..." if len(answer.get("content", "")) > 200 else answer.get("content", ""),
            "created_at": answer["created_at"],
            "link": f"/questions/{answer['question_id']}",
            "is_accepted": answer.get("is_accepted", False),
            "upvotes": answer.get("upvotes", 0)
        })
    
    # Get recent quiz attempts (high scores only)
    recent_quiz_attempts = await db.quiz_attempts.find({
        "user_id": user_id,
        "percentage": {"$gte": 80}  # Only show high score attempts
    }).sort("attempted_at", -1).limit(5).to_list(5)
    
    for attempt in recent_quiz_attempts:
        # Get quiz title
        quiz = await db.quizzes.find_one({"id": attempt["quiz_id"]})
        quiz_title = quiz["title"] if quiz else "Unknown Quiz"
        
        activities.append({
            "type": "quiz_completed",
            "title": f"Completed quiz: {quiz_title}",
            "content": f"Score: {attempt['percentage']:.1f}% ({attempt['score']}/{attempt['total_questions']})",
            "created_at": attempt["attempted_at"],
            "link": f"/quiz/{attempt['quiz_id']}/results",
            "score": attempt["percentage"],
            "subject": quiz.get("subject") if quiz else None
        })
    
    # Sort all activities by date
    activities.sort(key=lambda x: x["created_at"], reverse=True)
    
    # Apply pagination
    paginated_activities = activities[skip:skip + limit]
    
    return {
        "activities": paginated_activities,
        "total": len(activities),
        "can_view": True
    }

@api_router.get("/users/{user_id}/quiz-attempts")
async def get_user_quiz_attempts(user_id: str, skip: int = 0, limit: int = 20):
    """Get quiz attempts by a specific user"""
    attempts = await db.quiz_attempts.find({"user_id": user_id}).sort("attempted_at", -1).skip(skip).limit(limit).to_list(limit)
    
    enriched_attempts = []
    for attempt in attempts:
        # Get quiz info
        quiz = await db.quizzes.find_one({"id": attempt["quiz_id"]})
        attempt["quiz"] = {"id": quiz["id"], "title": quiz["title"]} if quiz else None
        enriched_attempts.append(attempt)
    
    return {"quiz_attempts": enriched_attempts}

# =====================================
# NOTIFICATION SYSTEM
# =====================================

async def create_notification(notification_data: NotificationCreate):
    """Helper function to create a notification"""
    notification = Notification(**notification_data.dict())
    await db.notifications.insert_one(notification.dict())
    return notification

@api_router.get("/notifications", response_model=List[Notification])
async def get_my_notifications(
    current_user: User = Depends(get_current_user),
    skip: int = 0,
    limit: int = 50,
    unread_only: bool = False
):
    """Get current user's notifications"""
    query = {"user_id": current_user.id}
    if unread_only:
        query["is_read"] = False
    
    notifications = await db.notifications.find(query).sort("created_at", -1).skip(skip).limit(limit).to_list(limit)
    return [Notification(**notification) for notification in notifications]

@api_router.get("/notifications/count")
async def get_notification_count(current_user: User = Depends(get_current_user)):
    """Get notification counts"""
    total_count = await db.notifications.count_documents({"user_id": current_user.id})
    unread_count = await db.notifications.count_documents({"user_id": current_user.id, "is_read": False})
    
    return {
        "total_count": total_count,
        "unread_count": unread_count
    }

@api_router.put("/notifications/{notification_id}/read")
async def mark_notification_read(
    notification_id: str, 
    current_user: User = Depends(get_current_user)
):
    """Mark a notification as read"""
    result = await db.notifications.update_one(
        {"id": notification_id, "user_id": current_user.id},
        {"$set": {"is_read": True}}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Notification not found")
    
    return {"message": "Notification marked as read"}

@api_router.put("/notifications/mark-all-read")
async def mark_all_notifications_read(current_user: User = Depends(get_current_user)):
    """Mark all notifications as read for current user"""
    await db.notifications.update_many(
        {"user_id": current_user.id, "is_read": False},
        {"$set": {"is_read": True}}
    )
    
    return {"message": "All notifications marked as read"}

@api_router.delete("/notifications/{notification_id}")
async def delete_notification(
    notification_id: str, 
    current_user: User = Depends(get_current_user)
):
    """Delete a notification"""
    result = await db.notifications.delete_one(
        {"id": notification_id, "user_id": current_user.id}
    )
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Notification not found")
    
    return {"message": "Notification deleted"}

# =====================================
# NOTIFICATION TRIGGERS
# =====================================

async def notify_question_answered(question_id: str, answerer_name: str):
    """Notify question author when someone answers their question"""
    question = await db.questions.find_one({"id": question_id})
    if not question:
        return
    
    notification = NotificationCreate(
        user_id=question["user_id"],
        type=NotificationType.NEW_ANSWER,
        title="New Answer",
        message=f"{answerer_name} answered your question: {question['title'][:50]}...",
        related_id=question_id
    )
    await create_notification(notification)

async def notify_answer_accepted(answer_id: str):
    """Notify user when their answer is accepted"""
    answer = await db.answers.find_one({"id": answer_id})
    if not answer:
        return
    
    question = await db.questions.find_one({"id": answer["question_id"]})
    if not question:
        return
    
    notification = NotificationCreate(
        user_id=answer["user_id"],
        type=NotificationType.ANSWER_ACCEPTED,
        title="Answer Accepted!",
        message=f"Your answer to '{question['title'][:50]}...' was accepted as the best answer!",
        related_id=answer["question_id"]
    )
    await create_notification(notification)

async def notify_quiz_result(user_id: str, quiz_title: str, score: float, passed: bool):
    """Notify user about their quiz result"""
    status = "passed" if passed else "failed"
    notification = NotificationCreate(
        user_id=user_id,
        type=NotificationType.QUIZ_RESULT,
        title="Quiz Completed",
        message=f"You {status} '{quiz_title}' with a score of {score}%",
        related_id=None
    )
    await create_notification(notification)

# =====================================
# BOOKMARKS SYSTEM
# =====================================

class BookmarkType(str, Enum):
    QUESTION = "question"
    QUIZ = "quiz"

class Bookmark(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    item_id: str  # ID of question or quiz
    item_type: BookmarkType
    created_at: datetime = Field(default_factory=datetime.utcnow)

class BookmarkCreate(BaseModel):
    item_id: str
    item_type: BookmarkType

# =====================================
# ENHANCED FOLLOWING SYSTEM WITH PRIVACY CONTROLS
# =====================================

class Follow(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    follower_id: str  # User who follows
    following_id: str  # User being followed
    status: FollowStatus = FollowStatus.APPROVED  # Follow status (pending/approved/rejected)
    requested_at: datetime = Field(default_factory=datetime.utcnow)
    approved_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

class FollowCreate(BaseModel):
    user_id: str  # User to follow

class UserFollowStats(BaseModel):
    followers_count: int = 0
    following_count: int = 0
    pending_requests_count: int = 0  # Number of pending follow requests
    is_following: bool = False  # Whether current user follows this user
    is_followed_by: bool = False  # Whether this user follows current user
    is_pending_approval: bool = False  # Whether current user has pending follow request

# =====================================
# BOOKMARKS ENDPOINTS
# =====================================

@api_router.post("/bookmarks")
async def create_bookmark(
    bookmark_data: BookmarkCreate,
    current_user: User = Depends(get_current_user)
):
    """Create a bookmark for a question or quiz"""
    # Check if bookmark already exists
    existing_bookmark = await db.bookmarks.find_one({
        "user_id": current_user.id,
        "item_id": bookmark_data.item_id,
        "item_type": bookmark_data.item_type
    })
    
    if existing_bookmark:
        raise HTTPException(status_code=400, detail="Item already bookmarked")
    
    # Verify the item exists
    if bookmark_data.item_type == BookmarkType.QUESTION:
        item = await db.questions.find_one({"id": bookmark_data.item_id})
        if not item:
            raise HTTPException(status_code=404, detail="Question not found")
    elif bookmark_data.item_type == BookmarkType.QUIZ:
        item = await db.quizzes.find_one({"id": bookmark_data.item_id})
        if not item:
            raise HTTPException(status_code=404, detail="Quiz not found")
    
    bookmark = Bookmark(
        user_id=current_user.id,
        item_id=bookmark_data.item_id,
        item_type=bookmark_data.item_type
    )
    
    await db.bookmarks.insert_one(bookmark.dict())
    return {"message": "Item bookmarked successfully", "bookmark": bookmark}

@api_router.delete("/bookmarks/{item_id}")
async def remove_bookmark(
    item_id: str,
    item_type: BookmarkType,
    current_user: User = Depends(get_current_user)
):
    """Remove a bookmark"""
    result = await db.bookmarks.delete_one({
        "user_id": current_user.id,
        "item_id": item_id,
        "item_type": item_type
    })
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Bookmark not found")
    
    return {"message": "Bookmark removed successfully"}

@api_router.get("/bookmarks")
async def get_my_bookmarks(
    current_user: User = Depends(get_current_user),
    item_type: Optional[BookmarkType] = None,
    skip: int = 0,
    limit: int = 20
):
    """Get current user's bookmarks with enriched content"""
    query = {"user_id": current_user.id}
    if item_type:
        query["item_type"] = item_type
    
    bookmarks = await db.bookmarks.find(query).sort("created_at", -1).skip(skip).limit(limit).to_list(limit)
    
    enriched_bookmarks = []
    for bookmark in bookmarks:
        enriched_bookmark = bookmark.copy()
        
        if bookmark["item_type"] == BookmarkType.QUESTION:
            # Get question details
            question = await db.questions.find_one({"id": bookmark["item_id"]})
            if question:
                user_info = await get_user_info(question["user_id"])
                question["user"] = user_info
                enriched_bookmark["item"] = question
            
        elif bookmark["item_type"] == BookmarkType.QUIZ:
            # Get quiz details
            quiz = await db.quizzes.find_one({"id": bookmark["item_id"]})
            if quiz:
                enriched_bookmark["item"] = quiz
        
        enriched_bookmarks.append(enriched_bookmark)
    
    return {"bookmarks": enriched_bookmarks}

@api_router.get("/bookmarks/check/{item_id}")
async def check_bookmark_status(
    item_id: str,
    item_type: BookmarkType,
    current_user: User = Depends(get_current_user)
):
    """Check if an item is bookmarked by current user"""
    bookmark = await db.bookmarks.find_one({
        "user_id": current_user.id,
        "item_id": item_id,
        "item_type": item_type
    })
    
    return {"is_bookmarked": bookmark is not None}

# =====================================
# PRIVACY AND SOCIAL UTILITY FUNCTIONS
# =====================================

async def can_view_user_activity(viewer_user_id: str, target_user_id: str) -> bool:
    """Check if viewer can see target user's activity (questions, answers, etc.)"""
    # Same user can always view their own content
    if viewer_user_id == target_user_id:
        return True
    
    # Get target user's privacy settings
    target_user = await db.users.find_one({"id": target_user_id})
    if not target_user:
        return False
    
    # Check if viewer is admin - admins can see everything
    viewer_user = await db.users.find_one({"id": viewer_user_id})
    if viewer_user and viewer_user.get("role") == UserRole.ADMIN:
        return True
    
    # If target user has private profile
    if target_user.get("is_private", False):
        # Check if viewer is an approved follower
        follow_relationship = await db.follows.find_one({
            "follower_id": viewer_user_id,
            "following_id": target_user_id,
            "status": FollowStatus.APPROVED
        })
        return follow_relationship is not None
    
    # Public profile - everyone can see
    return True

async def get_user_profile_for_viewer(user_id: str, viewer_id: str) -> UserProfile:
    """Get user profile with appropriate privacy filtering"""
    user = await db.users.find_one({"id": user_id})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    viewer = await db.users.find_one({"id": viewer_id})
    is_admin_viewer = viewer and viewer.get("role") == UserRole.ADMIN
    can_view_activity = await can_view_user_activity(viewer_id, user_id)
    
    # Get follow relationship status
    follow_relationship = await db.follows.find_one({
        "follower_id": viewer_id,
        "following_id": user_id
    })
    is_following = follow_relationship is not None and follow_relationship.get("status") == FollowStatus.APPROVED
    is_pending_approval = follow_relationship is not None and follow_relationship.get("status") == FollowStatus.PENDING
    
    # Get activity stats if viewer can see them
    activity_stats = {
        "total_questions": 0,
        "total_answers": 0,
        "total_quiz_attempts": 0,
        "average_quiz_score": 0.0
    }
    
    if can_view_activity:
        # Get actual activity stats
        questions_count = await db.questions.count_documents({"user_id": user_id})
        answers_count = await db.answers.count_documents({"user_id": user_id})
        attempts_count = await db.quiz_attempts.count_documents({"user_id": user_id})
        
        # Calculate average quiz score
        attempts = await db.quiz_attempts.find({"user_id": user_id}).to_list(1000)
        avg_score = sum(a.get("percentage", 0) for a in attempts) / len(attempts) if attempts else 0.0
        
        activity_stats = {
            "total_questions": questions_count,
            "total_answers": answers_count,
            "total_quiz_attempts": attempts_count,
            "average_quiz_score": round(avg_score, 1)
        }
    
    return UserProfile(
        id=user["id"],
        name=user["name"],
        email=user["email"] if (can_view_activity or is_admin_viewer) else None,
        role=user["role"],
        is_active=user.get("is_active", True),
        created_at=user["created_at"],
        is_private=user.get("is_private", False),
        follower_count=user.get("follower_count", 0),
        following_count=user.get("following_count", 0),
        total_questions=activity_stats["total_questions"] if can_view_activity else None,
        total_answers=activity_stats["total_answers"] if can_view_activity else None,
        total_quiz_attempts=activity_stats["total_quiz_attempts"] if can_view_activity else None,
        average_quiz_score=activity_stats["average_quiz_score"] if can_view_activity else None,
        is_following=is_following,
        is_pending_approval=is_pending_approval,
        can_view_activity=can_view_activity
    )

async def update_user_follow_counts(user_id: str):
    """Update user's follower and following counts"""
    follower_count = await db.follows.count_documents({
        "following_id": user_id,
        "status": FollowStatus.APPROVED
    })
    following_count = await db.follows.count_documents({
        "follower_id": user_id,
        "status": FollowStatus.APPROVED
    })
    
    await db.users.update_one(
        {"id": user_id},
        {"$set": {
            "follower_count": follower_count,
            "following_count": following_count
        }}
    )

# =====================================
# FOLLOWING ENDPOINTS
# =====================================

@api_router.post("/follow", response_model=FollowResponse)
async def follow_user(
    follow_data: FollowRequest,
    current_user: User = Depends(get_current_user)
):
    """Follow another user (handles both public and private accounts)"""
    if current_user.id == follow_data.user_id:
        raise HTTPException(status_code=400, detail="Cannot follow yourself")
    
    # Check if user exists
    user_to_follow = await db.users.find_one({"id": follow_data.user_id})
    if not user_to_follow:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Check if already following or has pending request
    existing_follow = await db.follows.find_one({
        "follower_id": current_user.id,
        "following_id": follow_data.user_id
    })
    
    if existing_follow:
        if existing_follow["status"] == FollowStatus.APPROVED:
            raise HTTPException(status_code=400, detail="Already following this user")
        elif existing_follow["status"] == FollowStatus.PENDING:
            raise HTTPException(status_code=400, detail="Follow request already pending")
        elif existing_follow["status"] == FollowStatus.REJECTED:
            # Update rejected request to pending (allow re-request)
            await db.follows.update_one(
                {"id": existing_follow["id"]},
                {"$set": {
                    "status": FollowStatus.PENDING,
                    "requested_at": datetime.utcnow()
                }}
            )
            return FollowResponse(
                action="request_sent",
                message="Follow request sent again",
                is_following=False,
                is_pending=True
            )
    
    # Check if target user has private profile
    is_private = user_to_follow.get("is_private", False)
    
    follow = UserFollow(
        follower_id=current_user.id,
        following_id=follow_data.user_id,
        status=FollowStatus.PENDING if is_private else FollowStatus.APPROVED,
        approved_at=datetime.utcnow() if not is_private else None
    )
    
    await db.follows.insert_one(follow.dict())
    
    # Update follow counts
    await update_user_follow_counts(current_user.id)
    await update_user_follow_counts(follow_data.user_id)
    
    if is_private:
        # Create notification for follow request (temporarily disabled for testing)
        # notification = Notification(
        #     user_id=follow_data.user_id,
        #     from_user_id=current_user.id,
        #     notification_type=NotificationType.FOLLOW_REQUEST,
        #     title="New Follow Request",
        #     message=f"{current_user.name} wants to follow you",
        #     related_id=current_user.id
        # )
        # await db.notifications.insert_one(notification.dict())
        
        return FollowResponse(
            action="request_sent",
            message="Follow request sent (account is private)",
            is_following=False,
            is_pending=True
        )
    else:
        # Create notification for new follower (temporarily disabled for testing)
        # notification = Notification(
        #     user_id=follow_data.user_id,
        #     from_user_id=current_user.id,
        #     notification_type=NotificationType.NEW_FOLLOWER,
        #     title="New Follower",
        #     message=f"{current_user.name} started following you",
        #     related_id=current_user.id
        # )
        # await db.notifications.insert_one(notification.dict())
        
        return FollowResponse(
            action="followed",
            message="Now following user",
            is_following=True,
            is_pending=False
        )

@api_router.delete("/follow/{user_id}", response_model=FollowResponse)
async def unfollow_user(
    user_id: str,
    current_user: User = Depends(get_current_user)
):
    """Unfollow a user or cancel follow request"""
    result = await db.follows.delete_one({
        "follower_id": current_user.id,
        "following_id": user_id
    })
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Not following this user")
    
    # Update follow counts
    await update_user_follow_counts(current_user.id)
    await update_user_follow_counts(user_id)
    
    return FollowResponse(
        action="unfollowed",
        message="User unfollowed successfully",
        is_following=False,
        is_pending=False
    )

@api_router.get("/users/{user_id}/follow-stats", response_model=UserFollowStats)
async def get_user_follow_stats(
    user_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get follow statistics for a user"""
    # Only count approved follows for public stats
    followers_count = await db.follows.count_documents({
        "following_id": user_id,
        "status": FollowStatus.APPROVED
    })
    following_count = await db.follows.count_documents({
        "follower_id": user_id,
        "status": FollowStatus.APPROVED
    })
    
    # For the user's own stats, also show pending requests
    pending_requests_count = 0
    if current_user.id == user_id:
        pending_requests_count = await db.follows.count_documents({
            "following_id": user_id,
            "status": FollowStatus.PENDING
        })
    
    # Check current user's relationship with this user
    follow_relationship = await db.follows.find_one({
        "follower_id": current_user.id,
        "following_id": user_id
    })
    
    is_following = follow_relationship is not None and follow_relationship.get("status") == FollowStatus.APPROVED
    is_pending_approval = follow_relationship is not None and follow_relationship.get("status") == FollowStatus.PENDING
    
    # Check reverse relationship
    reverse_follow = await db.follows.find_one({
        "follower_id": user_id,
        "following_id": current_user.id,
        "status": FollowStatus.APPROVED
    })
    is_followed_by = reverse_follow is not None
    
    return UserFollowStats(
        followers_count=followers_count,
        following_count=following_count,
        pending_requests_count=pending_requests_count,
        is_following=is_following,
        is_followed_by=is_followed_by,
        is_pending_approval=is_pending_approval
    )

@api_router.get("/following")
async def get_my_following(
    current_user: User = Depends(get_current_user),
    skip: int = 0,
    limit: int = 20
):
    """Get list of users current user is following"""
    follows = await db.follows.find({"follower_id": current_user.id}).sort("created_at", -1).skip(skip).limit(limit).to_list(limit)
    
    following_users = []
    for follow in follows:
        user = await db.users.find_one({"id": follow["following_id"]})
        if user:
            user_info = await get_user_info(follow["following_id"])
            following_users.append({
                "user": user_info,
                "followed_at": follow["created_at"]
            })
    
    return {"following": following_users}

@api_router.get("/followers")
async def get_my_followers(
    current_user: User = Depends(get_current_user),
    skip: int = 0,
    limit: int = 20
):
    """Get list of users following current user"""
    follows = await db.follows.find({"following_id": current_user.id}).sort("created_at", -1).skip(skip).limit(limit).to_list(limit)
    
    followers = []
    for follow in follows:
        user = await db.users.find_one({"id": follow["follower_id"]})
        if user:
            user_info = await get_user_info(follow["follower_id"])
            followers.append({
                "user": user_info,
                "followed_at": follow["created_at"]
            })
    
    return {"followers": followers}

@api_router.get("/users/{user_id}/followers")
async def get_user_followers(
    user_id: str,
    skip: int = 0,
    limit: int = 20
):
    """Get followers of a specific user (public endpoint)"""
    follows = await db.follows.find({"following_id": user_id}).sort("created_at", -1).skip(skip).limit(limit).to_list(limit)
    
    followers = []
    for follow in follows:
        user_info = await get_user_info(follow["follower_id"])
        followers.append({
            "user": user_info,
            "followed_at": follow["created_at"]
        })
    
    return {"followers": followers}

@api_router.get("/users/{user_id}/following")
async def get_user_following(
    user_id: str,
    skip: int = 0,
    limit: int = 20
):
    """Get who a specific user is following (public endpoint)"""
    follows = await db.follows.find({"follower_id": user_id}).sort("created_at", -1).skip(skip).limit(limit).to_list(limit)
    
    following_users = []
    for follow in follows:
        user_info = await get_user_info(follow["following_id"])
        following_users.append({
            "user": user_info,
            "followed_at": follow["created_at"]
        })
    
    return {"following": following_users}

# =====================================
# FOLLOW REQUEST MANAGEMENT
# =====================================

@api_router.get("/follow-requests")
async def get_pending_follow_requests(
    current_user: User = Depends(get_current_user)
):
    """Get pending follow requests for current user"""
    requests = await db.follows.find({
        "following_id": current_user.id,
        "status": FollowStatus.PENDING
    }).sort("requested_at", -1).to_list(100)
    
    request_list = []
    for request in requests:
        requester = await db.users.find_one({"id": request["follower_id"]})
        if requester:
            request_list.append({
                "request_id": request["id"],
                "user": {
                    "id": requester["id"],
                    "name": requester["name"],
                    "email": requester["email"],
                    "role": requester["role"]
                },
                "requested_at": request["requested_at"]
            })
    
    return {"requests": request_list}

@api_router.post("/follow-requests/{request_id}/approve", response_model=FollowResponse)
async def approve_follow_request(
    request_id: str,
    current_user: User = Depends(get_current_user)
):
    """Approve a follow request"""
    follow_request = await db.follows.find_one({
        "id": request_id,
        "following_id": current_user.id,
        "status": FollowStatus.PENDING
    })
    
    if not follow_request:
        raise HTTPException(status_code=404, detail="Follow request not found")
    
    # Update follow status to approved
    await db.follows.update_one(
        {"id": request_id},
        {"$set": {
            "status": FollowStatus.APPROVED,
            "approved_at": datetime.utcnow()
        }}
    )
    
    # Update follow counts
    await update_user_follow_counts(current_user.id)
    await update_user_follow_counts(follow_request["follower_id"])
    
    # Create notification for the requester (temporarily disabled for testing)
    # notification = Notification(
    #     user_id=follow_request["follower_id"],
    #     from_user_id=current_user.id,
    #     notification_type=NotificationType.FOLLOW_REQUEST_APPROVED,
    #     title="Follow Request Approved",
    #     message=f"{current_user.name} approved your follow request",
    #     related_id=current_user.id
    # )
    # await db.notifications.insert_one(notification.dict())
    
    return FollowResponse(
        action="request_approved",
        message="Follow request approved",
        is_following=True,
        is_pending=False
    )

@api_router.post("/follow-requests/{request_id}/reject", response_model=FollowResponse)
async def reject_follow_request(
    request_id: str,
    current_user: User = Depends(get_current_user)
):
    """Reject a follow request"""
    follow_request = await db.follows.find_one({
        "id": request_id,
        "following_id": current_user.id,
        "status": FollowStatus.PENDING
    })
    
    if not follow_request:
        raise HTTPException(status_code=404, detail="Follow request not found")
    
    # Update follow status to rejected
    await db.follows.update_one(
        {"id": request_id},
        {"$set": {"status": FollowStatus.REJECTED}}
    )
    
    return FollowResponse(
        action="request_rejected",
        message="Follow request rejected",
        is_following=False,
        is_pending=False
    )

# =====================================
# PRIVACY SETTINGS MANAGEMENT
# =====================================

@api_router.get("/privacy-settings")
async def get_privacy_settings(
    current_user: User = Depends(get_current_user)
):
    """Get current user's privacy settings"""
    return {
        "is_private": current_user.is_private,
        "follower_count": current_user.follower_count,
        "following_count": current_user.following_count
    }

@api_router.put("/privacy-settings")
async def update_privacy_settings(
    settings: PrivacySettingsUpdate,
    current_user: User = Depends(get_current_user)
):
    """Update privacy settings for current user"""
    update_data = {}
    
    if settings.is_private is not None:
        update_data["is_private"] = settings.is_private
        
        # If changing to public, approve all pending follow requests
        if not settings.is_private:
            await db.follows.update_many(
                {"following_id": current_user.id, "status": FollowStatus.PENDING},
                {"$set": {
                    "status": FollowStatus.APPROVED,
                    "approved_at": datetime.utcnow()
                }}
            )
            
            # Update follow counts
            await update_user_follow_counts(current_user.id)
    
    if update_data:
        await db.users.update_one(
            {"id": current_user.id},
            {"$set": update_data}
        )
    
    return {"message": "Privacy settings updated successfully"}

@api_router.get("/users/{user_id}/profile", response_model=UserProfile)
async def get_user_profile(
    user_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get user profile with privacy filtering"""
    return await get_user_profile_for_viewer(user_id, current_user.id)

# =====================================
# ACTIVITY FEED ENDPOINTS
# =====================================

class ActivityType(str, Enum):
    QUIZ_PUBLISHED = "quiz_published"
    QUESTION_POSTED = "question_posted"
    ANSWER_POSTED = "answer_posted"
    QUIZ_COMPLETED = "quiz_completed"
    USER_FOLLOWED = "user_followed"

class ActivityItem(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    activity_type: ActivityType
    user_id: str
    user_name: str
    title: str
    description: str
    related_id: Optional[str] = None  # ID of quiz, question, etc.
    created_at: datetime
    metadata: dict = {}  # Additional data like score, quiz title, etc.

@api_router.get("/user/activity-feed")
async def get_activity_feed(
    limit: int = 20,
    offset: int = 0,
    current_user: User = Depends(get_current_user)
):
    """Get activity feed from followed users"""
    try:
        # Get all users that current user follows
        follows = await db.follows.find({
            "follower_id": current_user.id,
            "status": FollowStatus.APPROVED
        }).to_list(1000)
        
        if not follows:
            return {
                "activities": [],
                "total": 0,
                "has_more": False
            }
        
        followed_user_ids = [follow["following_id"] for follow in follows]
        
        activities = []
        
        # Get recent quiz publications from followed users
        recent_quizzes = await db.quizzes.find({
            "$or": [
                {"created_by": {"$in": followed_user_ids}, "is_draft": False},
                {"quiz_owner_id": {"$in": followed_user_ids}, "is_draft": False}
            ]
        }).sort("created_at", -1).limit(50).to_list(50)
        
        for quiz in recent_quizzes:
            # Get user info
            user_info = await db.users.find_one({"id": quiz["created_by"]})
            if user_info:
                activities.append({
                    "id": f"quiz_{quiz['id']}",
                    "activity_type": ActivityType.QUIZ_PUBLISHED,
                    "user_id": user_info["id"],
                    "user_name": user_info["name"],
                    "title": f"Published a new quiz",
                    "description": f'Created "{quiz["title"]}" in {quiz.get("subject", "General")}',
                    "related_id": quiz["id"],
                    "created_at": quiz["created_at"],
                    "metadata": {
                        "quiz_title": quiz["title"],
                        "subject": quiz.get("subject", "General"),
                        "total_questions": quiz.get("total_questions", 0)
                    }
                })
        
        # Get recent questions from followed users
        recent_questions = await db.questions.find({
            "user_id": {"$in": followed_user_ids}
        }).sort("created_at", -1).limit(30).to_list(30)
        
        for question in recent_questions:
            user_info = await db.users.find_one({"id": question["user_id"]})
            if user_info:
                activities.append({
                    "id": f"question_{question['id']}",
                    "activity_type": ActivityType.QUESTION_POSTED,
                    "user_id": user_info["id"],
                    "user_name": user_info["name"],
                    "title": f"Posted a question",
                    "description": question["title"][:100] + ("..." if len(question["title"]) > 100 else ""),
                    "related_id": question["id"],
                    "created_at": question["created_at"],
                    "metadata": {
                        "question_title": question["title"],
                        "subject": question.get("subject", "General"),
                        "tags": question.get("tags", [])
                    }
                })
        
        # Get recent answers from followed users
        recent_answers = await db.answers.find({
            "user_id": {"$in": followed_user_ids}
        }).sort("created_at", -1).limit(20).to_list(20)
        
        for answer in recent_answers:
            # Get the question title for context
            question = await db.questions.find_one({"id": answer["question_id"]})
            user_info = await db.users.find_one({"id": answer["user_id"]})
            
            if user_info and question:
                activities.append({
                    "id": f"answer_{answer['id']}",
                    "activity_type": ActivityType.ANSWER_POSTED,
                    "user_id": user_info["id"],
                    "user_name": user_info["name"],
                    "title": f"Answered a question",
                    "description": f'Answered "{question["title"][:80]}..."',
                    "related_id": question["id"],
                    "created_at": answer["created_at"],
                    "metadata": {
                        "question_title": question["title"],
                        "answer_preview": answer["content"][:100],
                        "is_accepted": answer.get("is_accepted", False)
                    }
                })
        
        # Get recent quiz completions from followed users (high scores only)
        recent_attempts = await db.quiz_attempts.find({
            "user_id": {"$in": followed_user_ids},
            "percentage": {"$gte": 80}  # Only show high-score completions
        }).sort("attempted_at", -1).limit(15).to_list(15)
        
        for attempt in recent_attempts:
            user_info = await db.users.find_one({"id": attempt["user_id"]})
            quiz_info = await db.quizzes.find_one({"id": attempt["quiz_id"]})
            
            if user_info and quiz_info:
                activities.append({
                    "id": f"attempt_{attempt['id']}",
                    "activity_type": ActivityType.QUIZ_COMPLETED,
                    "user_id": user_info["id"],
                    "user_name": user_info["name"],
                    "title": f"Completed a quiz with high score",
                    "description": f'Scored {attempt["percentage"]:.1f}% on "{quiz_info["title"]}"',
                    "related_id": quiz_info["id"],
                    "created_at": attempt["attempted_at"],
                    "metadata": {
                        "quiz_title": quiz_info["title"],
                        "score": attempt["percentage"],
                        "passed": attempt.get("passed", False)
                    }
                })
        
        # Get recent follow activities
        recent_follows = await db.follows.find({
            "follower_id": {"$in": followed_user_ids},
            "status": FollowStatus.APPROVED
        }).sort("created_at", -1).limit(10).to_list(10)
        
        for follow in recent_follows:
            follower_info = await db.users.find_one({"id": follow["follower_id"]})
            followed_info = await db.users.find_one({"id": follow["following_id"]})
            
            if follower_info and followed_info:
                activities.append({
                    "id": f"follow_{follow['id']}",
                    "activity_type": ActivityType.USER_FOLLOWED,
                    "user_id": follower_info["id"],
                    "user_name": follower_info["name"],
                    "title": f"Started following someone",
                    "description": f'Started following {followed_info["name"]}',
                    "related_id": followed_info["id"],
                    "created_at": follow["created_at"],
                    "metadata": {
                        "followed_user_name": followed_info["name"]
                    }
                })
        
        # Sort all activities by creation time (newest first)
        activities.sort(key=lambda x: x["created_at"], reverse=True)
        
        # Apply pagination
        total_activities = len(activities)
        paginated_activities = activities[offset:offset + limit]
        has_more = offset + limit < total_activities
        
        return {
            "activities": paginated_activities,
            "total": total_activities,
            "has_more": has_more,
            "offset": offset,
            "limit": limit
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching activity feed: {str(e)}"
        )

# =====================================
# ENHANCED ADMIN CONTROLS FOR SOCIAL FEATURES
# =====================================

@api_router.get("/admin/social-overview")
async def get_social_overview(
    admin_user: User = Depends(get_admin_user)
):
    """Get overview of social features for admin"""
    total_follows = await db.follows.count_documents({"status": FollowStatus.APPROVED})
    pending_requests = await db.follows.count_documents({"status": FollowStatus.PENDING})
    private_accounts = await db.users.count_documents({"is_private": True})
    public_accounts = await db.users.count_documents({"is_private": False})
    
    return {
        "total_approved_follows": total_follows,
        "pending_follow_requests": pending_requests,
        "private_accounts": private_accounts,
        "public_accounts": public_accounts,
        "total_notifications": await db.notifications.count_documents({})
    }

@api_router.get("/admin/users/{user_id}/followers")
async def admin_get_user_followers(
    user_id: str,
    admin_user: User = Depends(get_admin_user)
):
    """Admin endpoint to view any user's followers (including private accounts)"""
    follows = await db.follows.find({"following_id": user_id}).to_list(1000)
    
    followers = []
    for follow in follows:
        user_info = await db.users.find_one({"id": follow["follower_id"]})
        if user_info:
            followers.append({
                "user": {
                    "id": user_info["id"],
                    "name": user_info["name"],
                    "email": user_info["email"],
                    "role": user_info["role"],
                    "is_private": user_info.get("is_private", False)
                },
                "status": follow.get("status", FollowStatus.APPROVED),
                "followed_at": follow["created_at"]
            })
    
    return {"followers": followers}

# =====================================
# ENHANCED NOTIFICATION TRIGGERS FOR FOLLOWING
# =====================================

async def notify_followers_of_new_question(user_id: str, question_title: str, question_id: str):
    """Notify approved followers when a user posts a new question"""
    # Get all approved followers of this user
    follows = await db.follows.find({
        "following_id": user_id,
        "status": FollowStatus.APPROVED
    }).to_list(1000)
    
    user_info = await db.users.find_one({"id": user_id})
    if not user_info:
        return
    
    for follow in follows:
        notification = Notification(
            user_id=follow["follower_id"],
            from_user_id=user_id,
            notification_type=NotificationType.NEW_QUESTION_FROM_FOLLOWED_USER,
            title="New Question from Followed User",
            message=f"{user_info['name']} posted a new question: {question_title[:50]}...",
            related_id=question_id
        )
        await db.notifications.insert_one(notification.dict())

async def notify_followers_of_new_quiz(user_id: str, quiz_title: str, quiz_id: str):
    """Notify approved followers when a user creates a new quiz"""
    # Get all approved followers of this user
    follows = await db.follows.find({
        "following_id": user_id,
        "status": FollowStatus.APPROVED
    }).to_list(1000)
    
    user_info = await db.users.find_one({"id": user_id})
    if not user_info:
        return
    
    for follow in follows:
        notification = Notification(
            user_id=follow["follower_id"],
            from_user_id=user_id,
            notification_type=NotificationType.NEW_QUIZ_FROM_FOLLOWED_USER,
            title="New Quiz from Followed User",
            message=f"{user_info['name']} created a new quiz: {quiz_title[:50]}...",
            related_id=quiz_id
        )
        await db.notifications.insert_one(notification.dict())

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

# Include router after all endpoints are defined
app.include_router(api_router)
