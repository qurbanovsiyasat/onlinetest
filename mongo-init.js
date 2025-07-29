// MongoDB initialization script
const db = db.getSiblingDB("squiz_db")

// Create collections
db.createCollection("users")
db.createCollection("quizzes")
db.createCollection("quiz_attempts")
db.createCollection("quiz_sessions")
db.createCollection("questions")
db.createCollection("answers")
db.createCollection("discussions")
db.createCollection("user_follows")

// Create indexes for performance
db.users.createIndex({ email: 1 }, { unique: true })
db.users.createIndex({ id: 1 }, { unique: true })
db.users.createIndex({ role: 1 })

db.quizzes.createIndex({ id: 1 }, { unique: true })
db.quizzes.createIndex({ subject: 1 })
db.quizzes.createIndex({ is_draft: 1 })
db.quizzes.createIndex({ created_at: -1 })

db.quiz_attempts.createIndex({ id: 1 }, { unique: true })
db.quiz_attempts.createIndex({ quiz_id: 1, user_id: 1, attempted_at: -1 })

db.quiz_sessions.createIndex({ id: 1 }, { unique: true })
db.quiz_sessions.createIndex({ user_id: 1 })
db.quiz_sessions.createIndex({ status: 1 })

db.questions.createIndex({ id: 1 }, { unique: true })
db.questions.createIndex({ subject: 1 })
db.questions.createIndex({ is_pinned: -1, created_at: -1 })

db.answers.createIndex({ id: 1 }, { unique: true })
db.answers.createIndex({ question_id: 1 })

db.discussions.createIndex({ id: 1 }, { unique: true })
db.discussions.createIndex({ question_id: 1 })

db.user_follows.createIndex({ id: 1 }, { unique: true })
db.user_follows.createIndex({ follower_id: 1, following_id: 1 }, { unique: true })

print("Database initialized successfully!")
