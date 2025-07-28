from fastapi import FastAPI, APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel, Field, EmailStr
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from dotenv import load_dotenv
from pathlib import Path
import os
import uuid
from typing import List, Optional, Dict, Any
import logging

# Load environment variables
ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# Security configuration
SECRET_KEY = os.environ.get("SECRET_KEY", "your-secret-key-here")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Pre-configured admin emails
ADMIN_EMAILS = ["admin@squiz.com", "admin@example.com"]

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app
app = FastAPI(title="Q&A Forum API", version="1.0.0")

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class UserBase(BaseModel):
    username: str
    email: EmailStr
    full_name: str

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: str
    is_admin: bool
    is_private: bool
    created_at: datetime
    followers_count: int = 0
    following_count: int = 0

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserUpdate(BaseModel):
    username: Optional[str] = None
    full_name: Optional[str] = None
    is_private: Optional[bool] = None

class Token(BaseModel):
    access_token: str
    token_type: str

class QuestionBase(BaseModel):
    title: str
    content: str
    category: str

class QuestionCreate(QuestionBase):
    pass

class QuestionResponse(QuestionBase):
    id: str
    author_id: str
    author_name: str
    author_is_admin: bool
    created_at: datetime
    updated_at: datetime
    answers_count: int = 0
    likes_count: int = 0
    is_liked: bool = False

class AnswerBase(BaseModel):
    content: str

class AnswerCreate(AnswerBase):
    pass

class AnswerResponse(AnswerBase):
    id: str
    question_id: str
    author_id: str
    author_name: str
    author_is_admin: bool
    created_at: datetime
    updated_at: datetime
    likes_count: int = 0
    is_liked: bool = False

class FollowRequest(BaseModel):
    user_id: str

class CategoryResponse(BaseModel):
    name: str
    question_count: int

# Utility functions
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = await db.users.find_one({"id": user_id})
    if user is None:
        raise credentials_exception
    return user

async def get_current_user_optional(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        return await get_current_user(credentials)
    except HTTPException:
        return None

# Authentication endpoints
@api_router.post("/auth/register", response_model=UserResponse)
async def register(user: UserCreate):
    # Check if user already exists
    existing_user = await db.users.find_one({"email": user.email})
    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )
    
    # Check if username already exists
    existing_username = await db.users.find_one({"username": user.username})
    if existing_username:
        raise HTTPException(
            status_code=400,
            detail="Username already taken"
        )
    
    # Create new user
    hashed_password = get_password_hash(user.password)
    user_id = str(uuid.uuid4())
    is_admin = user.email in ADMIN_EMAILS
    
    user_doc = {
        "id": user_id,
        "username": user.username,
        "email": user.email,
        "full_name": user.full_name,
        "hashed_password": hashed_password,
        "is_admin": is_admin,
        "is_private": False,
        "created_at": datetime.utcnow(),
        "followers_count": 0,
        "following_count": 0
    }
    
    await db.users.insert_one(user_doc)
    
    return UserResponse(
        id=user_id,
        username=user.username,
        email=user.email,
        full_name=user.full_name,
        is_admin=is_admin,
        is_private=False,
        created_at=user_doc["created_at"],
        followers_count=0,
        following_count=0
    )

@api_router.post("/auth/login", response_model=Token)
async def login(user: UserLogin):
    # Find user by email
    db_user = await db.users.find_one({"email": user.email})
    if not db_user or not verify_password(user.password, db_user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": db_user["id"]}, expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

@api_router.get("/auth/me", response_model=UserResponse)
async def get_current_user_info(current_user: dict = Depends(get_current_user)):
    return UserResponse(
        id=current_user["id"],
        username=current_user["username"],
        email=current_user["email"],
        full_name=current_user["full_name"],
        is_admin=current_user["is_admin"],
        is_private=current_user["is_private"],
        created_at=current_user["created_at"],
        followers_count=current_user.get("followers_count", 0),
        following_count=current_user.get("following_count", 0)
    )

# User profile endpoints
@api_router.get("/users/{user_id}", response_model=UserResponse)
async def get_user_profile(user_id: str, current_user: dict = Depends(get_current_user_optional)):
    user = await db.users.find_one({"id": user_id})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Check if profile is private and current user is not admin or the profile owner
    if user["is_private"] and current_user:
        if current_user["id"] != user_id and not current_user["is_admin"]:
            raise HTTPException(status_code=403, detail="This profile is private")
    elif user["is_private"] and not current_user:
        raise HTTPException(status_code=403, detail="This profile is private")
    
    return UserResponse(
        id=user["id"],
        username=user["username"],
        email=user["email"],
        full_name=user["full_name"],
        is_admin=user["is_admin"],
        is_private=user["is_private"],
        created_at=user["created_at"],
        followers_count=user.get("followers_count", 0),
        following_count=user.get("following_count", 0)
    )

@api_router.put("/users/me", response_model=UserResponse)
async def update_user_profile(user_update: UserUpdate, current_user: dict = Depends(get_current_user)):
    update_data = {k: v for k, v in user_update.dict().items() if v is not None}
    
    if update_data:
        await db.users.update_one(
            {"id": current_user["id"]},
            {"$set": update_data}
        )
    
    updated_user = await db.users.find_one({"id": current_user["id"]})
    return UserResponse(
        id=updated_user["id"],
        username=updated_user["username"],
        email=updated_user["email"],
        full_name=updated_user["full_name"],
        is_admin=updated_user["is_admin"],
        is_private=updated_user["is_private"],
        created_at=updated_user["created_at"],
        followers_count=updated_user.get("followers_count", 0),
        following_count=updated_user.get("following_count", 0)
    )

# Question endpoints
@api_router.post("/questions", response_model=QuestionResponse)
async def create_question(question: QuestionCreate, current_user: dict = Depends(get_current_user)):
    question_id = str(uuid.uuid4())
    question_doc = {
        "id": question_id,
        "title": question.title,
        "content": question.content,
        "category": question.category,
        "author_id": current_user["id"],
        "author_name": current_user["username"],
        "author_is_admin": current_user["is_admin"],
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
        "answers_count": 0,
        "likes_count": 0
    }
    
    await db.questions.insert_one(question_doc)
    
    return QuestionResponse(
        id=question_id,
        title=question.title,
        content=question.content,
        category=question.category,
        author_id=current_user["id"],
        author_name=current_user["username"],
        author_is_admin=current_user["is_admin"],
        created_at=question_doc["created_at"],
        updated_at=question_doc["updated_at"],
        answers_count=0,
        likes_count=0,
        is_liked=False
    )

@api_router.get("/questions", response_model=List[QuestionResponse])
async def get_questions(
    category: Optional[str] = None,
    skip: int = 0,
    limit: int = 20,
    current_user: dict = Depends(get_current_user_optional)
):
    query = {}
    if category:
        query["category"] = category
    
    questions = await db.questions.find(query).skip(skip).limit(limit).to_list(length=limit)
    
    result = []
    for question in questions:
        is_liked = False
        if current_user:
            like = await db.likes.find_one({
                "user_id": current_user["id"],
                "question_id": question["id"]
            })
            is_liked = like is not None
        
        result.append(QuestionResponse(
            id=question["id"],
            title=question["title"],
            content=question["content"],
            category=question["category"],
            author_id=question["author_id"],
            author_name=question["author_name"],
            author_is_admin=question["author_is_admin"],
            created_at=question["created_at"],
            updated_at=question["updated_at"],
            answers_count=question.get("answers_count", 0),
            likes_count=question.get("likes_count", 0),
            is_liked=is_liked
        ))
    
    return result

@api_router.get("/questions/{question_id}", response_model=QuestionResponse)
async def get_question(question_id: str, current_user: dict = Depends(get_current_user_optional)):
    question = await db.questions.find_one({"id": question_id})
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    
    is_liked = False
    if current_user:
        like = await db.likes.find_one({
            "user_id": current_user["id"],
            "question_id": question_id
        })
        is_liked = like is not None
    
    return QuestionResponse(
        id=question["id"],
        title=question["title"],
        content=question["content"],
        category=question["category"],
        author_id=question["author_id"],
        author_name=question["author_name"],
        author_is_admin=question["author_is_admin"],
        created_at=question["created_at"],
        updated_at=question["updated_at"],
        answers_count=question.get("answers_count", 0),
        likes_count=question.get("likes_count", 0),
        is_liked=is_liked
    )

# Answer endpoints
@api_router.post("/questions/{question_id}/answers", response_model=AnswerResponse)
async def create_answer(question_id: str, answer: AnswerCreate, current_user: dict = Depends(get_current_user)):
    # Check if question exists
    question = await db.questions.find_one({"id": question_id})
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    
    answer_id = str(uuid.uuid4())
    answer_doc = {
        "id": answer_id,
        "question_id": question_id,
        "content": answer.content,
        "author_id": current_user["id"],
        "author_name": current_user["username"],
        "author_is_admin": current_user["is_admin"],
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
        "likes_count": 0
    }
    
    await db.answers.insert_one(answer_doc)
    
    # Update question's answer count
    await db.questions.update_one(
        {"id": question_id},
        {"$inc": {"answers_count": 1}}
    )
    
    return AnswerResponse(
        id=answer_id,
        question_id=question_id,
        content=answer.content,
        author_id=current_user["id"],
        author_name=current_user["username"],
        author_is_admin=current_user["is_admin"],
        created_at=answer_doc["created_at"],
        updated_at=answer_doc["updated_at"],
        likes_count=0,
        is_liked=False
    )

@api_router.get("/questions/{question_id}/answers", response_model=List[AnswerResponse])
async def get_answers(
    question_id: str,
    skip: int = 0,
    limit: int = 20,
    current_user: dict = Depends(get_current_user_optional)
):
    answers = await db.answers.find({"question_id": question_id}).skip(skip).limit(limit).to_list(length=limit)
    
    result = []
    for answer in answers:
        is_liked = False
        if current_user:
            like = await db.likes.find_one({
                "user_id": current_user["id"],
                "answer_id": answer["id"]
            })
            is_liked = like is not None
        
        result.append(AnswerResponse(
            id=answer["id"],
            question_id=answer["question_id"],
            content=answer["content"],
            author_id=answer["author_id"],
            author_name=answer["author_name"],
            author_is_admin=answer["author_is_admin"],
            created_at=answer["created_at"],
            updated_at=answer["updated_at"],
            likes_count=answer.get("likes_count", 0),
            is_liked=is_liked
        ))
    
    return result

# Like/Unlike endpoints
@api_router.post("/questions/{question_id}/like")
async def like_question(question_id: str, current_user: dict = Depends(get_current_user)):
    # Check if question exists
    question = await db.questions.find_one({"id": question_id})
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    
    # Check if already liked
    existing_like = await db.likes.find_one({
        "user_id": current_user["id"],
        "question_id": question_id
    })
    
    if existing_like:
        # Unlike
        await db.likes.delete_one({"_id": existing_like["_id"]})
        await db.questions.update_one(
            {"id": question_id},
            {"$inc": {"likes_count": -1}}
        )
        return {"message": "Question unliked"}
    else:
        # Like
        like_doc = {
            "id": str(uuid.uuid4()),
            "user_id": current_user["id"],
            "question_id": question_id,
            "created_at": datetime.utcnow()
        }
        await db.likes.insert_one(like_doc)
        await db.questions.update_one(
            {"id": question_id},
            {"$inc": {"likes_count": 1}}
        )
        return {"message": "Question liked"}

@api_router.post("/answers/{answer_id}/like")
async def like_answer(answer_id: str, current_user: dict = Depends(get_current_user)):
    # Check if answer exists
    answer = await db.answers.find_one({"id": answer_id})
    if not answer:
        raise HTTPException(status_code=404, detail="Answer not found")
    
    # Check if already liked
    existing_like = await db.likes.find_one({
        "user_id": current_user["id"],
        "answer_id": answer_id
    })
    
    if existing_like:
        # Unlike
        await db.likes.delete_one({"_id": existing_like["_id"]})
        await db.answers.update_one(
            {"id": answer_id},
            {"$inc": {"likes_count": -1}}
        )
        return {"message": "Answer unliked"}
    else:
        # Like
        like_doc = {
            "id": str(uuid.uuid4()),
            "user_id": current_user["id"],
            "answer_id": answer_id,
            "created_at": datetime.utcnow()
        }
        await db.likes.insert_one(like_doc)
        await db.answers.update_one(
            {"id": answer_id},
            {"$inc": {"likes_count": 1}}
        )
        return {"message": "Answer liked"}

# Follow system endpoints
@api_router.post("/users/{user_id}/follow")
async def follow_user(user_id: str, current_user: dict = Depends(get_current_user)):
    if user_id == current_user["id"]:
        raise HTTPException(status_code=400, detail="Cannot follow yourself")
    
    # Check if user exists
    target_user = await db.users.find_one({"id": user_id})
    if not target_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Check if already following
    existing_follow = await db.follows.find_one({
        "follower_id": current_user["id"],
        "following_id": user_id
    })
    
    if existing_follow:
        # Unfollow
        await db.follows.delete_one({"_id": existing_follow["_id"]})
        await db.users.update_one(
            {"id": user_id},
            {"$inc": {"followers_count": -1}}
        )
        await db.users.update_one(
            {"id": current_user["id"]},
            {"$inc": {"following_count": -1}}
        )
        return {"message": "User unfollowed"}
    else:
        # Follow
        follow_doc = {
            "id": str(uuid.uuid4()),
            "follower_id": current_user["id"],
            "following_id": user_id,
            "created_at": datetime.utcnow()
        }
        await db.follows.insert_one(follow_doc)
        await db.users.update_one(
            {"id": user_id},
            {"$inc": {"followers_count": 1}}
        )
        await db.users.update_one(
            {"id": current_user["id"]},
            {"$inc": {"following_count": 1}}
        )
        return {"message": "User followed"}

# Categories endpoint
@api_router.get("/categories", response_model=List[CategoryResponse])
async def get_categories():
    pipeline = [
        {"$group": {"_id": "$category", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}}
    ]
    
    categories = await db.questions.aggregate(pipeline).to_list(length=None)
    
    return [
        CategoryResponse(name=cat["_id"], question_count=cat["count"])
        for cat in categories
    ]

# User activity endpoints
@api_router.get("/users/{user_id}/questions", response_model=List[QuestionResponse])
async def get_user_questions(
    user_id: str,
    skip: int = 0,
    limit: int = 20,
    current_user: dict = Depends(get_current_user_optional)
):
    # Check if user exists and is accessible
    user = await db.users.find_one({"id": user_id})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Check privacy settings
    if user["is_private"] and current_user:
        if current_user["id"] != user_id and not current_user["is_admin"]:
            raise HTTPException(status_code=403, detail="This profile is private")
    elif user["is_private"] and not current_user:
        raise HTTPException(status_code=403, detail="This profile is private")
    
    questions = await db.questions.find({"author_id": user_id}).skip(skip).limit(limit).to_list(length=limit)
    
    result = []
    for question in questions:
        is_liked = False
        if current_user:
            like = await db.likes.find_one({
                "user_id": current_user["id"],
                "question_id": question["id"]
            })
            is_liked = like is not None
        
        result.append(QuestionResponse(
            id=question["id"],
            title=question["title"],
            content=question["content"],
            category=question["category"],
            author_id=question["author_id"],
            author_name=question["author_name"],
            author_is_admin=question["author_is_admin"],
            created_at=question["created_at"],
            updated_at=question["updated_at"],
            answers_count=question.get("answers_count", 0),
            likes_count=question.get("likes_count", 0),
            is_liked=is_liked
        ))
    
    return result

@api_router.get("/users/{user_id}/answers", response_model=List[AnswerResponse])
async def get_user_answers(
    user_id: str,
    skip: int = 0,
    limit: int = 20,
    current_user: dict = Depends(get_current_user_optional)
):
    # Check if user exists and is accessible
    user = await db.users.find_one({"id": user_id})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Check privacy settings
    if user["is_private"] and current_user:
        if current_user["id"] != user_id and not current_user["is_admin"]:
            raise HTTPException(status_code=403, detail="This profile is private")
    elif user["is_private"] and not current_user:
        raise HTTPException(status_code=403, detail="This profile is private")
    
    answers = await db.answers.find({"author_id": user_id}).skip(skip).limit(limit).to_list(length=limit)
    
    result = []
    for answer in answers:
        is_liked = False
        if current_user:
            like = await db.likes.find_one({
                "user_id": current_user["id"],
                "answer_id": answer["id"]
            })
            is_liked = like is not None
        
        result.append(AnswerResponse(
            id=answer["id"],
            question_id=answer["question_id"],
            content=answer["content"],
            author_id=answer["author_id"],
            author_name=answer["author_name"],
            author_is_admin=answer["author_is_admin"],
            created_at=answer["created_at"],
            updated_at=answer["updated_at"],
            likes_count=answer.get("likes_count", 0),
            is_liked=is_liked
        ))
    
    return result

# Basic health check
@api_router.get("/")
async def root():
    return {"message": "Q&A Forum API is running"}

# Include the router in the main app
app.include_router(api_router)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
