from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel, EmailStr
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
import jwt
import bcrypt
import uuid
import os
from contextlib import asynccontextmanager

# Environment variables
MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017")
JWT_SECRET = os.getenv("JWT_SECRET", "your-super-secret-jwt-key-change-in-production")
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_HOURS = 24

# Database connection
client = AsyncIOMotorClient(MONGO_URL)
db = client.squiz_db

# Security
security = HTTPBearer()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("🚀 Starting Squiz Platform...")
    
    # Create indexes
    await create_indexes()
    
    # Create admin user if not exists
    await create_admin_user()
    
    yield
    
    # Shutdown
    print("👋 Shutting down Squiz Platform...")
    client.close()

app = FastAPI(
    title="Squiz Platform API",
    description="Comprehensive Quiz and Assessment Platform",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic Models
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
    role: str
    is_active: bool
    created_at: datetime
    is_private: bool = False
    follower_count: int = 0
    following_count: int = 0

class QuestionOption(BaseModel):
    text: str
    is_correct: bool = False

class OpenEndedAnswer(BaseModel):
    expected_answers: List[str] = []
    keywords: List[str] = []
    case_sensitive: bool = False
    partial_credit: bool = True

class QuizQuestion(BaseModel):
    question_text: str
    question_type: str  # "multiple_choice" or "open_ended"
    options: List[QuestionOption] = []
    multiple_correct: bool = False
    open_ended_answer: Optional[OpenEndedAnswer] = None
    image_url: Optional[str] = None
    pdf_url: Optional[str] = None
    difficulty: str = "medium"  # "easy", "medium", "hard"
    points: int = 1
    explanation: Optional[str] = None

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

class QuizAttemptCreate(BaseModel):
    answers: List[str]

class QuestionCreate(BaseModel):
    title: str
    content: str
    image: Optional[str] = None
    subject: Optional[str] = None
    subcategory: Optional[str] = None
    tags: List[str] = []

class AnswerCreate(BaseModel):
    content: str
    image: Optional[str] = None

class QuizSessionCreate(BaseModel):
    quiz_id: str
    time_limit_minutes: Optional[int] = None

class QuizSessionUpdate(BaseModel):
    current_question_index: int
    answers: List[str]

class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str

# Utility Functions
def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

def create_jwt_token(user_data: dict) -> str:
    payload = {
        "sub": user_data["id"],
        "email": user_data["email"],
        "role": user_data["role"],
        "name": user_data["name"],
        "exp": datetime.utcnow() + timedelta(hours=JWT_EXPIRATION_HOURS),
        "iat": datetime.utcnow()
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        payload = jwt.decode(credentials.credentials, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        user = await db.users.find_one({"id": user_id})
        if user is None:
            raise HTTPException(status_code=401, detail="User not found")
        
        return user
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

async def get_admin_user(current_user: dict = Depends(get_current_user)):
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return current_user

async def create_indexes():
    """Create database indexes for performance"""
    # Users indexes
    await db.users.create_index("email", unique=True)
    await db.users.create_index("id", unique=True)
    await db.users.create_index("role")
    
    # Quizzes indexes
    await db.quizzes.create_index("id", unique=True)
    await db.quizzes.create_index("subject")
    await db.quizzes.create_index("is_draft")
    await db.quizzes.create_index("created_at")
    
    # Quiz attempts indexes
    await db.quiz_attempts.create_index("id", unique=True)
    await db.quiz_attempts.create_index([("quiz_id", 1), ("user_id", 1), ("attempted_at", -1)])
    
    # Questions indexes
    await db.questions.create_index("id", unique=True)
    await db.questions.create_index("subject")
    await db.questions.create_index([("is_pinned", -1), ("created_at", -1)])

async def create_admin_user():
    """Create default admin user if not exists"""
    admin_exists = await db.users.find_one({"email": "admin@squiz.com"})
    if not admin_exists:
        admin_user = {
            "id": str(uuid.uuid4()),
            "email": "admin@squiz.com",
            "name": "Admin User",
            "password": hash_password("admin123"),
            "role": "admin",
            "is_active": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "is_private": False,
            "follower_count": 0,
            "following_count": 0
        }
        await db.users.insert_one(admin_user)
        print("✅ Admin user created: admin@squiz.com / admin123")

# Authentication Endpoints
@app.post("/api/auth/register", response_model=UserResponse)
async def register(user_data: UserCreate):
    # Check if user already exists
    existing_user = await db.users.find_one({"email": user_data.email})
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Create new user
    user_id = str(uuid.uuid4())
    new_user = {
        "id": user_id,
        "email": user_data.email,
        "name": user_data.name,
        "password": hash_password(user_data.password),
        "role": "user",
        "is_active": True,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
        "is_private": False,
        "follower_count": 0,
        "following_count": 0
    }
    
    await db.users.insert_one(new_user)
    
    # Return user without password
    return UserResponse(
        id=new_user["id"],
        email=new_user["email"],
        name=new_user["name"],
        role=new_user["role"],
        is_active=new_user["is_active"],
        created_at=new_user["created_at"],
        is_private=new_user["is_private"],
        follower_count=new_user["follower_count"],
        following_count=new_user["following_count"]
    )

@app.post("/api/auth/login")
async def login(login_data: UserLogin):
    # Find user
    user = await db.users.find_one({"email": login_data.email})
    if not user or not verify_password(login_data.password, user["password"]):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    if not user["is_active"]:
        raise HTTPException(status_code=401, detail="Account is deactivated")
    
    # Create JWT token
    token = create_jwt_token(user)
    
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": UserResponse(
            id=user["id"],
            email=user["email"],
            name=user["name"],
            role=user["role"],
            is_active=user["is_active"],
            created_at=user["created_at"],
            is_private=user["is_private"],
            follower_count=user["follower_count"],
            following_count=user["following_count"]
        )
    }

@app.get("/api/auth/me", response_model=UserResponse)
async def get_current_user_info(current_user: dict = Depends(get_current_user)):
    return UserResponse(
        id=current_user["id"],
        email=current_user["email"],
        name=current_user["name"],
        role=current_user["role"],
        is_active=current_user["is_active"],
        created_at=current_user["created_at"],
        is_private=current_user["is_private"],
        follower_count=current_user["follower_count"],
        following_count=current_user["following_count"]
    )

@app.post("/api/auth/change-password")
async def change_password(
    password_data: ChangePasswordRequest,
    current_user: dict = Depends(get_current_user)
):
    # Verify current password
    if not verify_password(password_data.current_password, current_user["password"]):
        raise HTTPException(status_code=400, detail="Current password is incorrect")
    
    # Update password
    new_password_hash = hash_password(password_data.new_password)
    await db.users.update_one(
        {"id": current_user["id"]},
        {"$set": {"password": new_password_hash, "updated_at": datetime.utcnow()}}
    )
    
    return {"message": "Password updated successfully"}

# Quiz Endpoints
@app.get("/api/quizzes")
async def get_quizzes(
    subject: Optional[str] = None,
    category: Optional[str] = None,
    limit: int = 50,
    offset: int = 0
):
    # Build filter
    filter_query = {"is_draft": False}
    if subject:
        filter_query["subject"] = subject
    if category:
        filter_query["category"] = category
    
    # Get quizzes without questions for listing
    quizzes = await db.quizzes.find(
        filter_query,
        {"questions": 0, "_id": 0}  # Exclude questions array and _id for performance
    ).sort("created_at", -1).skip(offset).limit(limit).to_list(limit)
    
    return quizzes

@app.get("/api/quiz/{quiz_id}")
async def get_quiz(quiz_id: str):
    quiz = await db.quizzes.find_one({"id": quiz_id}, {"_id": 0})
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")
    
    if quiz["is_draft"]:
        raise HTTPException(status_code=403, detail="Quiz is not published")
    
    return quiz

@app.post("/api/quiz/{quiz_id}/attempt")
async def submit_quiz_attempt(
    quiz_id: str,
    attempt_data: QuizAttemptCreate,
    current_user: dict = Depends(get_current_user)
):
    # Get quiz
    quiz = await db.quizzes.find_one({"id": quiz_id}, {"_id": 0})
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")
    
    if quiz["is_draft"]:
        raise HTTPException(status_code=403, detail="Quiz is not published")
    
    # Calculate score
    questions = quiz["questions"]
    correct_answers = []
    question_results = []
    score = 0
    earned_points = 0
    total_possible_points = sum(q.get("points", 1) for q in questions)
    
    for i, question in enumerate(questions):
        user_answer = attempt_data.answers[i] if i < len(attempt_data.answers) else ""
        question_points = question.get("points", 1)
        
        if question["question_type"] == "multiple_choice":
            # Find correct answers
            correct_options = [opt["text"] for opt in question["options"] if opt["is_correct"]]
            correct_answer = correct_options[0] if correct_options else ""
            correct_answers.append(correct_answer)
            
            is_correct = user_answer in correct_options
            points_earned = question_points if is_correct else 0
            
        else:  # open_ended
            # Simple keyword matching for open-ended questions
            expected_answers = question.get("open_ended_answer", {}).get("expected_answers", [])
            keywords = question.get("open_ended_answer", {}).get("keywords", [])
            case_sensitive = question.get("open_ended_answer", {}).get("case_sensitive", False)
            
            correct_answer = expected_answers[0] if expected_answers else ""
            correct_answers.append(correct_answer)
            
            # Check if answer contains keywords or matches expected answers
            user_answer_check = user_answer if case_sensitive else user_answer.lower()
            is_correct = False
            
            for expected in expected_answers:
                expected_check = expected if case_sensitive else expected.lower()
                if expected_check in user_answer_check:
                    is_correct = True
                    break
            
            if not is_correct:
                for keyword in keywords:
                    keyword_check = keyword if case_sensitive else keyword.lower()
                    if keyword_check in user_answer_check:
                        is_correct = True
                        break
            
            points_earned = question_points if is_correct else 0
        
        if is_correct:
            score += 1
        earned_points += points_earned
        
        question_results.append({
            "question_number": i + 1,
            "question_text": question["question_text"],
            "user_answer": user_answer,
            "correct_answer": correct_answer,
            "is_correct": is_correct,
            "points_earned": points_earned,
            "points_possible": question_points,
            "explanation": question.get("explanation", "")
        })
    
    # Calculate percentages
    total_questions = len(questions)
    percentage = (score / total_questions * 100) if total_questions > 0 else 0
    points_percentage = (earned_points / total_possible_points * 100) if total_possible_points > 0 else 0
    passed = percentage >= quiz.get("min_pass_percentage", 60.0)
    
    # Create attempt record
    attempt_id = str(uuid.uuid4())
    attempt_record = {
        "id": attempt_id,
        "quiz_id": quiz_id,
        "user_id": current_user["id"],
        "answers": attempt_data.answers,
        "correct_answers": correct_answers,
        "question_results": question_results,
        "score": score,
        "total_questions": total_questions,
        "percentage": percentage,
        "earned_points": earned_points,
        "total_possible_points": total_possible_points,
        "points_percentage": points_percentage,
        "passed": passed,
        "attempted_at": datetime.utcnow(),
        "time_taken_minutes": None
    }
    
    await db.quiz_attempts.insert_one(attempt_record)
    
    # Update quiz statistics
    await update_quiz_statistics(quiz_id)
    
    return attempt_record

async def update_quiz_statistics(quiz_id: str):
    """Update quiz statistics after new attempt"""
    # Get all attempts for this quiz
    attempts = await db.quiz_attempts.find({"quiz_id": quiz_id}).to_list(None)
    
    if attempts:
        total_attempts = len(attempts)
        average_score = sum(attempt["percentage"] for attempt in attempts) / total_attempts
        
        await db.quizzes.update_one(
            {"id": quiz_id},
            {
                "$set": {
                    "total_attempts": total_attempts,
                    "average_score": average_score,
                    "updated_at": datetime.utcnow()
                }
            }
        )

# Quiz Session Endpoints (Real-time)
@app.post("/api/quiz-session/start")
async def start_quiz_session(
    session_data: QuizSessionCreate,
    current_user: dict = Depends(get_current_user)
):
    # Get quiz
    quiz = await db.quizzes.find_one({"id": session_data.quiz_id})
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")
    
    if quiz["is_draft"]:
        raise HTTPException(status_code=403, detail="Quiz is not published")
    
    # Create session
    session_id = str(uuid.uuid4())
    session = {
        "id": session_id,
        "quiz_id": session_data.quiz_id,
        "quiz_title": quiz["title"],
        "user_id": current_user["id"],
        "status": "pending",
        "start_time": None,
        "end_time": None,
        "time_limit_minutes": session_data.time_limit_minutes or quiz.get("time_limit_minutes"),
        "time_remaining_seconds": None,
        "current_question_index": 0,
        "total_questions": len(quiz["questions"]),
        "answers": [],
        "is_auto_submit": True,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
        "last_activity": datetime.utcnow()
    }
    
    await db.quiz_sessions.insert_one(session)
    
    return session

@app.post("/api/quiz-session/{session_id}/activate")
async def activate_quiz_session(
    session_id: str,
    current_user: dict = Depends(get_current_user)
):
    session = await db.quiz_sessions.find_one({"id": session_id, "user_id": current_user["id"]})
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    if session["status"] != "pending":
        raise HTTPException(status_code=400, detail="Session already activated")
    
    # Activate session
    start_time = datetime.utcnow()
    time_remaining = None
    if session["time_limit_minutes"]:
        time_remaining = session["time_limit_minutes"] * 60  # Convert to seconds
    
    await db.quiz_sessions.update_one(
        {"id": session_id},
        {
            "$set": {
                "status": "active",
                "start_time": start_time,
                "time_remaining_seconds": time_remaining,
                "updated_at": datetime.utcnow(),
                "last_activity": datetime.utcnow()
            }
        }
    )
    
    return {
        "id": session_id,
        "status": "active",
        "start_time": start_time,
        "time_remaining_seconds": time_remaining,
        "message": "Quiz session activated successfully"
    }

@app.get("/api/quiz-session/{session_id}/status")
async def get_quiz_session_status(
    session_id: str,
    current_user: dict = Depends(get_current_user)
):
    session = await db.quiz_sessions.find_one({"id": session_id, "user_id": current_user["id"]})
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Calculate remaining time if session is active
    if session["status"] == "active" and session["time_limit_minutes"]:
        elapsed_seconds = (datetime.utcnow() - session["start_time"]).total_seconds()
        total_seconds = session["time_limit_minutes"] * 60
        remaining_seconds = max(0, total_seconds - elapsed_seconds)
        
        # Auto-expire if time is up
        if remaining_seconds <= 0:
            await db.quiz_sessions.update_one(
                {"id": session_id},
                {"$set": {"status": "expired", "updated_at": datetime.utcnow()}}
            )
            session["status"] = "expired"
        
        session["time_remaining_seconds"] = remaining_seconds
    
    return session

@app.put("/api/quiz-session/{session_id}/update")
async def update_quiz_session(
    session_id: str,
    update_data: QuizSessionUpdate,
    current_user: dict = Depends(get_current_user)
):
    session = await db.quiz_sessions.find_one({"id": session_id, "user_id": current_user["id"]})
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    if session["status"] not in ["active", "paused"]:
        raise HTTPException(status_code=400, detail="Session is not active")
    
    # Update session
    await db.quiz_sessions.update_one(
        {"id": session_id},
        {
            "$set": {
                "current_question_index": update_data.current_question_index,
                "answers": update_data.answers,
                "updated_at": datetime.utcnow(),
                "last_activity": datetime.utcnow()
            }
        }
    )
    
    return {
        "message": "Session updated successfully",
        "current_question_index": update_data.current_question_index,
        "answers_saved": len(update_data.answers)
    }

@app.get("/api/quiz-session/{session_id}/pause")
async def pause_quiz_session(
    session_id: str,
    current_user: dict = Depends(get_current_user)
):
    session = await db.quiz_sessions.find_one({"id": session_id, "user_id": current_user["id"]})
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    if session["status"] != "active":
        raise HTTPException(status_code=400, detail="Session is not active")
    
    await db.quiz_sessions.update_one(
        {"id": session_id},
        {
            "$set": {
                "status": "paused",
                "updated_at": datetime.utcnow()
            }
        }
    )
    
    return {
        "message": "Quiz session paused successfully",
        "status": "paused",
        "paused_at": datetime.utcnow()
    }

@app.get("/api/quiz-session/{session_id}/resume")
async def resume_quiz_session(
    session_id: str,
    current_user: dict = Depends(get_current_user)
):
    session = await db.quiz_sessions.find_one({"id": session_id, "user_id": current_user["id"]})
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    if session["status"] != "paused":
        raise HTTPException(status_code=400, detail="Session is not paused")
    
    await db.quiz_sessions.update_one(
        {"id": session_id},
        {
            "$set": {
                "status": "active",
                "updated_at": datetime.utcnow(),
                "last_activity": datetime.utcnow()
            }
        }
    )
    
    return {
        "message": "Quiz session resumed successfully",
        "status": "active",
        "resumed_at": datetime.utcnow()
    }

@app.post("/api/quiz-session/{session_id}/submit")
async def submit_quiz_session(
    session_id: str,
    current_user: dict = Depends(get_current_user)
):
    session = await db.quiz_sessions.find_one({"id": session_id, "user_id": current_user["id"]})
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    if session["status"] == "completed":
        raise HTTPException(status_code=400, detail="Session already completed")
    
    # Mark session as completed
    await db.quiz_sessions.update_one(
        {"id": session_id},
        {
            "$set": {
                "status": "completed",
                "end_time": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
        }
    )
    
    # Create quiz attempt from session
    attempt_data = QuizAttemptCreate(answers=session.get("answers", []))
    quiz_attempt = await submit_quiz_attempt(session["quiz_id"], attempt_data, current_user)
    
    return {
        "message": "Quiz session completed successfully",
        "quiz_attempt": quiz_attempt
    }

# Q&A Forum Endpoints
@app.get("/api/questions")
async def get_questions(
    limit: int = 20,
    offset: int = 0,
    subject: Optional[str] = None,
    subcategory: Optional[str] = None,
    status: Optional[str] = None
):
    # Build filter
    filter_query = {}
    if subject:
        filter_query["subject"] = subject
    if subcategory:
        filter_query["subcategory"] = subcategory
    if status:
        filter_query["status"] = status
    
    # Get questions with user info
    pipeline = [
        {"$match": filter_query},
        {"$lookup": {
            "from": "users",
            "localField": "user_id",
            "foreignField": "id",
            "as": "user_info"
        }},
        {"$addFields": {
            "user_name": {"$arrayElemAt": ["$user_info.name", 0]}
        }},
        {"$project": {"user_info": 0, "_id": 0}},
        {"$sort": {"is_pinned": -1, "created_at": -1}},
        {"$skip": offset},
        {"$limit": limit}
    ]
    
    questions = await db.questions.aggregate(pipeline).to_list(limit)
    
    # Get total count
    total = await db.questions.count_documents(filter_query)
    
    return {
        "questions": questions,
        "total": total,
        "limit": limit,
        "offset": offset,
        "has_more": offset + limit < total
    }

@app.post("/api/questions")
async def create_question(
    question_data: QuestionCreate,
    current_user: dict = Depends(get_current_user)
):
    question_id = str(uuid.uuid4())
    question = {
        "id": question_id,
        "title": question_data.title,
        "content": question_data.content,
        "image": question_data.image,
        "user_id": current_user["id"],
        "subject": question_data.subject,
        "subcategory": question_data.subcategory,
        "tags": question_data.tags,
        "upvotes": 0,
        "downvotes": 0,
        "upvoted_by": [],
        "downvoted_by": [],
        "status": "open",
        "answer_count": 0,
        "has_accepted_answer": False,
        "is_pinned": False,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    
    await db.questions.insert_one(question)
    
    return question

@app.get("/api/questions/{question_id}")
async def get_question_detail(question_id: str):
    # Get question with user info
    pipeline = [
        {"$match": {"id": question_id}},
        {"$lookup": {
            "from": "users",
            "localField": "user_id",
            "foreignField": "id",
            "as": "user_info"
        }},
        {"$addFields": {
            "user_name": {"$arrayElemAt": ["$user_info.name", 0]}
        }},
        {"$project": {"user_info": 0, "_id": 0}}
    ]
    
    questions = await db.questions.aggregate(pipeline).to_list(1)
    if not questions:
        raise HTTPException(status_code=404, detail="Question not found")
    
    question = questions[0]
    
    # Get answers
    answers_pipeline = [
        {"$match": {"question_id": question_id}},
        {"$lookup": {
            "from": "users",
            "localField": "user_id",
            "foreignField": "id",
            "as": "user_info"
        }},
        {"$addFields": {
            "user_name": {"$arrayElemAt": ["$user_info.name", 0]}
        }},
        {"$project": {"user_info": 0, "_id": 0}},
        {"$sort": {"is_accepted": -1, "created_at": -1}}
    ]
    
    answers = await db.answers.aggregate(answers_pipeline).to_list(None)
    
    # Get discussions
    discussions_pipeline = [
        {"$match": {"question_id": question_id}},
        {"$lookup": {
            "from": "users",
            "localField": "user_id",
            "foreignField": "id",
            "as": "user_info"
        }},
        {"$addFields": {
            "user_name": {"$arrayElemAt": ["$user_info.name", 0]}
        }},
        {"$project": {"user_info": 0, "_id": 0}},
        {"$sort": {"created_at": 1}}
    ]
    
    discussions = await db.discussions.aggregate(discussions_pipeline).to_list(None)
    
    question["answers"] = answers
    question["discussions"] = discussions
    
    return question

@app.post("/api/questions/{question_id}/answers")
async def create_answer(
    question_id: str,
    answer_data: AnswerCreate,
    current_user: dict = Depends(get_current_user)
):
    # Check if question exists
    question = await db.questions.find_one({"id": question_id})
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    
    # Create answer
    answer_id = str(uuid.uuid4())
    answer = {
        "id": answer_id,
        "question_id": question_id,
        "content": answer_data.content,
        "image": answer_data.image,
        "user_id": current_user["id"],
        "upvotes": 0,
        "downvotes": 0,
        "upvoted_by": [],
        "downvoted_by": [],
        "is_accepted": False,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    
    await db.answers.insert_one(answer)
    
    # Update question answer count
    await db.questions.update_one(
        {"id": question_id},
        {
            "$inc": {"answer_count": 1},
            "$set": {"updated_at": datetime.utcnow()}
        }
    )
    
    return answer

@app.put("/api/questions/{question_id}/answers/{answer_id}/accept")
async def accept_answer(
    question_id: str,
    answer_id: str,
    current_user: dict = Depends(get_current_user)
):
    # Check if user owns the question or is admin
    question = await db.questions.find_one({"id": question_id})
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    
    if question["user_id"] != current_user["id"] and current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Only question owner or admin can accept answers")
    
    # Check if answer exists
    answer = await db.answers.find_one({"id": answer_id, "question_id": question_id})
    if not answer:
        raise HTTPException(status_code=404, detail="Answer not found")
    
    # Unaccept all other answers for this question
    await db.answers.update_many(
        {"question_id": question_id},
        {"$set": {"is_accepted": False, "updated_at": datetime.utcnow()}}
    )
    
    # Accept this answer
    await db.answers.update_one(
        {"id": answer_id},
        {"$set": {"is_accepted": True, "updated_at": datetime.utcnow()}}
    )
    
    # Update question status
    await db.questions.update_one(
        {"id": question_id},
        {
            "$set": {
                "has_accepted_answer": True,
                "status": "answered",
                "updated_at": datetime.utcnow()
            }
        }
    )
    
    return {"message": "Answer accepted successfully", "is_accepted": True}

# Admin Endpoints
@app.get("/api/admin/users")
async def get_all_users(admin_user: dict = Depends(get_admin_user)):
    users = await db.users.find({}, {"password": 0, "_id": 0}).to_list(None)
    return users

@app.post("/api/admin/quiz")
async def create_quiz(
    quiz_data: QuizCreate,
    admin_user: dict = Depends(get_admin_user)
):
    quiz_id = str(uuid.uuid4())
    
    # Add IDs to questions
    questions_with_ids = []
    for question in quiz_data.questions:
        question_dict = question.dict()
        question_dict["id"] = str(uuid.uuid4())
        question_dict["created_at"] = datetime.utcnow()
        question_dict["updated_at"] = datetime.utcnow()
        question_dict["is_mandatory"] = True
        questions_with_ids.append(question_dict)
    
    quiz = {
        "id": quiz_id,
        "title": quiz_data.title,
        "description": quiz_data.description,
        "category": quiz_data.category,
        "subject": quiz_data.subject,
        "subcategory": quiz_data.subcategory,
        "questions": questions_with_ids,
        "created_by": admin_user["id"],
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
        "total_questions": len(questions_with_ids),
        "total_points": sum(q.get("points", 1) for q in questions_with_ids),
        "is_active": True,
        "is_public": quiz_data.is_public,
        "allowed_users": quiz_data.allowed_users,
        "total_attempts": 0,
        "average_score": 0.0,
        "quiz_owner_type": "admin",
        "quiz_owner_id": admin_user["id"],
        "min_pass_percentage": quiz_data.min_pass_percentage,
        "time_limit_minutes": quiz_data.time_limit_minutes,
        "shuffle_questions": quiz_data.shuffle_questions,
        "shuffle_options": quiz_data.shuffle_options,
        "is_draft": True,  # Start as draft
        "preview_token": str(uuid.uuid4())
    }
    
    await db.quizzes.insert_one(quiz)
    
    return quiz

@app.post("/api/admin/quiz/{quiz_id}/publish")
async def publish_quiz(
    quiz_id: str,
    admin_user: dict = Depends(get_admin_user)
):
    quiz = await db.quizzes.find_one({"id": quiz_id})
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")
    
    # Check if user owns the quiz or is admin
    if quiz["quiz_owner_id"] != admin_user["id"] and admin_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Permission denied")
    
    await db.quizzes.update_one(
        {"id": quiz_id},
        {
            "$set": {
                "is_draft": False,
                "updated_at": datetime.utcnow()
            }
        }
    )
    
    return {"message": "Quiz published successfully"}

@app.get("/api/admin/quizzes")
async def get_all_quizzes(admin_user: dict = Depends(get_admin_user)):
    quizzes = await db.quizzes.find({}, {"questions": 0, "_id": 0}).sort("created_at", -1).to_list(None)
    return quizzes

@app.get("/api/admin/quiz-results")
async def get_quiz_results(admin_user: dict = Depends(get_admin_user)):
    pipeline = [
        {"$lookup": {
            "from": "quizzes",
            "localField": "quiz_id",
            "foreignField": "id",
            "as": "quiz_info"
        }},
        {"$lookup": {
            "from": "users",
            "localField": "user_id",
            "foreignField": "id",
            "as": "user_info"
        }},
        {"$addFields": {
            "quiz": {
                "title": {"$arrayElemAt": ["$quiz_info.title", 0]},
                "category": {"$arrayElemAt": ["$quiz_info.category", 0]}
            },
            "user": {
                "name": {"$arrayElemAt": ["$user_info.name", 0]},
                "email": {"$arrayElemAt": ["$user_info.email", 0]}
            }
        }},
        {"$project": {"quiz_info": 0, "user_info": 0, "_id": 0}},
        {"$sort": {"attempted_at": -1}}
    ]
    
    results = await db.quiz_attempts.aggregate(pipeline).to_list(None)
    return results

@app.get("/api/admin/analytics")
async def get_analytics(admin_user: dict = Depends(get_admin_user)):
    # Get basic counts
    total_users = await db.users.count_documents({})
    total_quizzes = await db.quizzes.count_documents({"is_draft": False})
    total_attempts = await db.quiz_attempts.count_documents({})
    
    # Calculate average score
    attempts = await db.quiz_attempts.find({}, {"percentage": 1}).to_list(None)
    average_score = sum(attempt["percentage"] for attempt in attempts) / len(attempts) if attempts else 0
    
    # Get active users (last 30 days)
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    active_users_month = await db.quiz_attempts.distinct("user_id", {"attempted_at": {"$gte": thirty_days_ago}})
    
    # Get most popular quiz
    popular_quiz_pipeline = [
        {"$group": {"_id": "$quiz_id", "attempt_count": {"$sum": 1}}},
        {"$sort": {"attempt_count": -1}},
        {"$limit": 1},
        {"$lookup": {
            "from": "quizzes",
            "localField": "_id",
            "foreignField": "id",
            "as": "quiz_info"
        }},
        {"$addFields": {
            "quiz_title": {"$arrayElemAt": ["$quiz_info.title", 0]}
        }}
    ]
    
    popular_quiz_result = await db.quiz_attempts.aggregate(popular_quiz_pipeline).to_list(1)
    most_popular_quiz = popular_quiz_result[0]["quiz_title"] if popular_quiz_result else "N/A"
    
    return {
        "total_users": total_users,
        "total_quizzes": total_quizzes,
        "total_attempts": total_attempts,
        "average_score": round(average_score, 1),
        "active_users_today": 0,  # Would need more complex query
        "active_users_week": 0,   # Would need more complex query
        "active_users_month": len(active_users_month),
        "most_popular_quiz": most_popular_quiz
    }

# Search and Utility Endpoints
@app.get("/api/subjects-available")
async def get_available_subjects():
    # Get unique subjects from quizzes
    quiz_subjects = await db.quizzes.distinct("subject", {"is_draft": False})
    
    # Get unique subjects from questions
    question_subjects = await db.questions.distinct("subject")
    
    # Combine and deduplicate
    all_subjects = list(set(quiz_subjects + question_subjects))
    
    subjects_info = []
    for subject in all_subjects:
        quiz_count = await db.quizzes.count_documents({"subject": subject, "is_draft": False})
        question_count = await db.questions.count_documents({"subject": subject})
        
        # Get subcategories
        subcategories = await db.quizzes.distinct("subcategory", {"subject": subject, "is_draft": False})
        subcategory_info = []
        
        for subcat in subcategories:
            subcat_quiz_count = await db.quizzes.count_documents({
                "subject": subject,
                "subcategory": subcat,
                "is_draft": False
            })
            subcat_question_count = await db.questions.count_documents({
                "subject": subject,
                "subcategory": subcat
            })
            
            subcategory_info.append({
                "name": subcat,
                "quiz_count": subcat_quiz_count,
                "question_count": subcat_question_count
            })
        
        subjects_info.append({
            "name": subject,
            "quiz_count": quiz_count,
            "question_count": question_count,
            "subcategories": subcategory_info
        })
    
    return {
        "subjects": subjects_info,
        "total_subjects": len(subjects_info),
        "total_subcategories": sum(len(s["subcategories"]) for s in subjects_info)
    }

@app.get("/api/user/stats")
async def get_user_stats(current_user: dict = Depends(get_current_user)):
    user_id = current_user["id"]
    
    # Get user's quiz attempts
    attempts = await db.quiz_attempts.find({"user_id": user_id}).to_list(None)
    
    if not attempts:
        return {
            "total_quizzes_taken": 0,
            "total_questions_answered": 0,
            "average_score": 0,
            "best_score": 0,
            "total_time_spent_minutes": 0,
            "quiz_attempts_by_subject": [],
            "recent_attempts": [],
            "achievements": []
        }
    
    total_quizzes = len(attempts)
    total_questions = sum(attempt["total_questions"] for attempt in attempts)
    average_score = sum(attempt["percentage"] for attempt in attempts) / total_quizzes
    best_score = max(attempt["percentage"] for attempt in attempts)
    
    # Get recent attempts with quiz info
    recent_pipeline = [
        {"$match": {"user_id": user_id}},
        {"$sort": {"attempted_at": -1}},
        {"$limit": 5},
        {"$lookup": {
            "from": "quizzes",
            "localField": "quiz_id",
            "foreignField": "id",
            "as": "quiz_info"
        }},
        {"$addFields": {
            "quiz_title": {"$arrayElemAt": ["$quiz_info.title", 0]}
        }},
        {"$project": {
            "quiz_title": 1,
            "score": 1,
            "percentage": 1,
            "attempted_at": 1
        }}
    ]
    
    recent_attempts = await db.quiz_attempts.aggregate(recent_pipeline).to_list(5)
    
    return {
        "total_quizzes_taken": total_quizzes,
        "total_questions_answered": total_questions,
        "average_score": round(average_score, 1),
        "best_score": round(best_score, 1),
        "total_time_spent_minutes": 0,  # Would need session data
        "quiz_attempts_by_subject": [],  # Would need more complex aggregation
        "recent_attempts": recent_attempts,
        "achievements": [
            {
                "type": "quizzes_completed",
                "value": total_quizzes,
                "description": f"{total_quizzes} quiz tamamlandı"
            }
        ]
    }

# Health Check
@app.get("/api/health")
async def health_check():
    try:
        # Test database connection
        await db.command("ping")
        return {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "version": "1.0.0",
            "database": "connected"
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "timestamp": datetime.utcnow().isoformat(),
            "version": "1.0.0",
            "database": "disconnected",
            "error": str(e)
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
