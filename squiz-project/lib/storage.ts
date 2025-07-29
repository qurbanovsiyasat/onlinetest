import fs from 'fs'
import path from 'path'

const DATA_DIR = path.join(process.cwd(), 'data')
const USERS_FILE = path.join(DATA_DIR, 'users.json')
const QUIZZES_FILE = path.join(DATA_DIR, 'quizzes.json')
const RESULTS_FILE = path.join(DATA_DIR, 'quiz-results.json')
const ATTEMPTS_FILE = path.join(DATA_DIR, 'quiz-attempts.json')

// Ensure data directory exists
if (!fs.existsSync(DATA_DIR)) {
  fs.mkdirSync(DATA_DIR, { recursive: true })
}

// Default users
const defaultUsers = [
  {
    id: "1",
    email: "admin@squiz.com",
    password: "admin123",
    name: "Admin İstifadəçi",
    role: "admin",
    is_active: true,
    created_at: "2025-01-01T00:00:00Z",
    is_private: false,
    follower_count: 0,
    following_count: 0,
    can_create_quiz: true,
  },
  {
    id: "2", 
    email: "user@squiz.com",
    password: "user123",
    name: "Test İstifadəçi",
    role: "user",
    is_active: true,
    created_at: "2025-01-01T00:00:00Z",
    is_private: false,
    follower_count: 5,
    following_count: 10,
    can_create_quiz: true,
  },
]

// Default quizzes
const defaultQuizzes = [
  {
    id: "1",
    title: "JavaScript Əsasları",
    description: "JavaScript programlaşdırma dilinin əsas anlayışları, dəyişənlər, funksiyalar və DOM manipulyasiyası",
    category: "Programlaşdırma",
    subject: "Veb İnkişaf",
    subcategory: "Frontend",
    questions: [
      {
        id: "1",
        question_text: "JavaScript-də dəyişən müəyyən etmək üçün hansı açar söz istifadə olunur?",
        question_type: "multiple_choice",
        options: [
          { text: "var", is_correct: true },
          { text: "variable", is_correct: false },
          { text: "define", is_correct: false },
          { text: "set", is_correct: false }
        ],
        multiple_correct: false,
        difficulty: "easy",
        points: 1,
        explanation: "JavaScript-də dəyişən müəyyən etmək üçün var, let və ya const açar sözləri istifadə olunur."
      }
    ],
    is_public: true,
    min_pass_percentage: 70,
    time_limit_minutes: 30,
    shuffle_questions: false,
    shuffle_options: false,
    created_at: "2025-01-20T10:00:00Z",
    creator_id: "1",
    creator_name: "Admin İstifadəçi",
    total_questions: 1,
    total_points: 1,
    total_attempts: 245,
    average_score: 78.5,
    difficulty: "medium",
    tags: ["javascript", "veb", "frontend"],
    is_featured: true,
  }
]

export function getUsers() {
  try {
    if (fs.existsSync(USERS_FILE)) {
      const data = fs.readFileSync(USERS_FILE, 'utf8')
      return JSON.parse(data)
    } else {
      // Create default users file
      fs.writeFileSync(USERS_FILE, JSON.stringify(defaultUsers, null, 2))
      return defaultUsers
    }
  } catch (error) {
    console.error('Error reading users:', error)
    return defaultUsers
  }
}

export function saveUsers(users: any[]) {
  try {
    fs.writeFileSync(USERS_FILE, JSON.stringify(users, null, 2))
    return true
  } catch (error) {
    console.error('Error saving users:', error)
    return false
  }
}

export function getQuizzes() {
  try {
    if (fs.existsSync(QUIZZES_FILE)) {
      const data = fs.readFileSync(QUIZZES_FILE, 'utf8')
      return JSON.parse(data)
    } else {
      // Create default quizzes file
      fs.writeFileSync(QUIZZES_FILE, JSON.stringify(defaultQuizzes, null, 2))
      return defaultQuizzes
    }
  } catch (error) {
    console.error('Error reading quizzes:', error)
    return defaultQuizzes
  }
}

export function saveQuizzes(quizzes: any[]) {
  try {
    fs.writeFileSync(QUIZZES_FILE, JSON.stringify(quizzes, null, 2))
    return true
  } catch (error) {
    console.error('Error saving quizzes:', error)
    return false
  }
}

// Quiz Results Functions
export function getQuizResults() {
  try {
    if (fs.existsSync(RESULTS_FILE)) {
      const data = fs.readFileSync(RESULTS_FILE, 'utf8')
      return JSON.parse(data)
    } else {
      fs.writeFileSync(RESULTS_FILE, JSON.stringify([], null, 2))
      return []
    }
  } catch (error) {
    console.error('Error reading quiz results:', error)
    return []
  }
}

export function saveQuizResults(results: any[]) {
  try {
    fs.writeFileSync(RESULTS_FILE, JSON.stringify(results, null, 2))
    return true
  } catch (error) {
    console.error('Error saving quiz results:', error)
    return false
  }
}

// Quiz Attempts Functions
export function getQuizAttempts() {
  try {
    if (fs.existsSync(ATTEMPTS_FILE)) {
      const data = fs.readFileSync(ATTEMPTS_FILE, 'utf8')
      return JSON.parse(data)
    } else {
      fs.writeFileSync(ATTEMPTS_FILE, JSON.stringify([], null, 2))
      return []
    }
  } catch (error) {
    console.error('Error reading quiz attempts:', error)
    return []
  }
}

export function saveQuizAttempts(attempts: any[]) {
  try {
    fs.writeFileSync(ATTEMPTS_FILE, JSON.stringify(attempts, null, 2))
    return true
  } catch (error) {
    console.error('Error saving quiz attempts:', error)
    return false
  }
}

// User Progress Functions
export function getUserProgress(userId: string) {
  try {
    const results = getQuizResults()
    const userResults = results.filter(result => result.userId === userId)
    
    return {
      totalAttempts: userResults.length,
      passedQuizzes: userResults.filter(r => r.passed).length,
      averageScore: userResults.length > 0 
        ? Math.round(userResults.reduce((sum, r) => sum + r.scorePercentage, 0) / userResults.length)
        : 0,
      totalPoints: userResults.reduce((sum, r) => sum + r.earnedPoints, 0),
      recentResults: userResults.slice(-5).reverse()
    }
  } catch (error) {
    console.error('Error getting user progress:', error)
    return {
      totalAttempts: 0,
      passedQuizzes: 0,
      averageScore: 0,
      totalPoints: 0,
      recentResults: []
    }
  }
}
