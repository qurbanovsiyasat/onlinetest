from fastapi import FastAPI, APIRouter, HTTPException
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Optional
import uuid
from datetime import datetime


ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")


# Quiz Models
class QuizOption(BaseModel):
    text: str
    is_correct: bool

class QuizQuestion(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    question_text: str
    options: List[QuizOption]

class Quiz(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    description: str
    questions: List[QuizQuestion]
    created_at: datetime = Field(default_factory=datetime.utcnow)
    total_questions: int = 0

class QuizCreate(BaseModel):
    title: str
    description: str
    questions: List[QuizQuestion]

class QuizAttempt(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    quiz_id: str
    answers: List[str]  # List of selected option texts
    score: int
    total_questions: int
    percentage: float
    attempted_at: datetime = Field(default_factory=datetime.utcnow)

class QuizAttemptCreate(BaseModel):
    quiz_id: str
    answers: List[str]


# Routes
@api_router.get("/")
async def root():
    return {"message": "OnlineTestMaker API is running!"}

@api_router.post("/quiz", response_model=Quiz)
async def create_quiz(quiz_data: QuizCreate):
    """Create a new quiz"""
    quiz_dict = quiz_data.dict()
    quiz_obj = Quiz(**quiz_dict)
    quiz_obj.total_questions = len(quiz_obj.questions)
    
    await db.quizzes.insert_one(quiz_obj.dict())
    return quiz_obj

@api_router.get("/quiz", response_model=List[Quiz])
async def get_quizzes():
    """Get all available quizzes"""
    quizzes = await db.quizzes.find().to_list(1000)
    return [Quiz(**quiz) for quiz in quizzes]

@api_router.get("/quiz/{quiz_id}", response_model=Quiz)
async def get_quiz(quiz_id: str):
    """Get a specific quiz by ID"""
    quiz = await db.quizzes.find_one({"id": quiz_id})
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")
    return Quiz(**quiz)

@api_router.post("/quiz/{quiz_id}/attempt", response_model=QuizAttempt)
async def submit_quiz_attempt(quiz_id: str, attempt_data: QuizAttemptCreate):
    """Submit quiz answers and get score"""
    # Get the quiz
    quiz = await db.quizzes.find_one({"id": quiz_id})
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")
    
    quiz_obj = Quiz(**quiz)
    
    # Calculate score
    score = 0
    total_questions = len(quiz_obj.questions)
    
    for i, user_answer in enumerate(attempt_data.answers):
        if i < len(quiz_obj.questions):
            question = quiz_obj.questions[i]
            # Find the correct answer
            for option in question.options:
                if option.is_correct and option.text == user_answer:
                    score += 1
                    break
    
    percentage = (score / total_questions * 100) if total_questions > 0 else 0
    
    # Create attempt record
    attempt = QuizAttempt(
        quiz_id=quiz_id,
        answers=attempt_data.answers,
        score=score,
        total_questions=total_questions,
        percentage=percentage
    )
    
    await db.quiz_attempts.insert_one(attempt.dict())
    return attempt

@api_router.get("/quiz/{quiz_id}/attempts", response_model=List[QuizAttempt])
async def get_quiz_attempts(quiz_id: str):
    """Get all attempts for a specific quiz"""
    attempts = await db.quiz_attempts.find({"quiz_id": quiz_id}).to_list(1000)
    return [QuizAttempt(**attempt) for attempt in attempts]


# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()