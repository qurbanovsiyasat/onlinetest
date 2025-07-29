import { type NextRequest, NextResponse } from "next/server"
import { getQuizzes, saveQuizzes } from "@/lib/storage"

interface QuizQuestion {
  id: string
  question_text: string
  question_type: "multiple_choice" | "open_ended"
  options: Array<{
    text: string
    is_correct: boolean
    image_url?: string
  }>
  multiple_correct: boolean
  open_ended_answer?: {
    expected_answers: string[]
    keywords: string[]
    case_sensitive: boolean
    partial_credit: boolean
  }
  image_url?: string
  difficulty: "easy" | "medium" | "hard"
  points: number
  explanation?: string
  math_formula?: string
}

interface Quiz {
  id: string
  title: string
  description: string
  category: string
  subject: string
  subcategory: string
  questions: QuizQuestion[]
  is_public: boolean
  min_pass_percentage: number
  time_limit_minutes: number | null
  shuffle_questions: boolean
  shuffle_options: boolean
  created_at: string
  creator_id: string
  creator_name: string
  total_questions: number
  total_points: number
  total_attempts: number
  average_score: number
  difficulty: "easy" | "medium" | "hard"
  tags: string[]
  is_featured: boolean
}



// GET - List all quizzes
export async function GET(request: NextRequest) {
  try {
    const searchParams = request.nextUrl.searchParams
    const category = searchParams.get('category')
    const difficulty = searchParams.get('difficulty')
    const search = searchParams.get('search')
    const featured = searchParams.get('featured')

    // Get quizzes from persistent storage
    let filteredQuizzes = getQuizzes()

    // Filter by category
    if (category && category !== 'all') {
      filteredQuizzes = filteredQuizzes.filter(quiz => quiz.category === category)
    }

    // Filter by difficulty
    if (difficulty && difficulty !== 'all') {
      filteredQuizzes = filteredQuizzes.filter(quiz => quiz.difficulty === difficulty)
    }

    // Filter by search term
    if (search) {
      const searchLower = search.toLowerCase()
      filteredQuizzes = filteredQuizzes.filter(quiz =>
        quiz.title.toLowerCase().includes(searchLower) ||
        quiz.description.toLowerCase().includes(searchLower) ||
        quiz.tags.some(tag => tag.toLowerCase().includes(searchLower))
      )
    }

    // Filter featured
    if (featured === 'true') {
      filteredQuizzes = filteredQuizzes.filter(quiz => quiz.is_featured)
    }

    return NextResponse.json(filteredQuizzes)
  } catch (error) {
    console.error("Quiz listeleme xətası:", error)
    return NextResponse.json({ detail: "Sunucu hatası" }, { status: 500 })
  }
}

// POST - Create new quiz
export async function POST(request: NextRequest) {
  try {
    const quizData = await request.json()

    // Validation
    if (!quizData.title || !quizData.description || !quizData.category) {
      return NextResponse.json({ detail: "Bütün mütləq sahələri doldurun" }, { status: 400 })
    }

    if (!quizData.questions || quizData.questions.length === 0) {
      return NextResponse.json({ detail: "Ən azı bir sual əlavə edin" }, { status: 400 })
    }

    // Get current quizzes
    const quizzes = getQuizzes()

    // Calculate quiz statistics
    const totalQuestions = quizData.questions.length
    const totalPoints = quizData.questions.reduce((sum: number, q: QuizQuestion) => sum + q.points, 0)
    
    // Determine overall difficulty based on questions
    const difficulties = quizData.questions.map((q: QuizQuestion) => q.difficulty)
    const avgDifficulty = difficulties.includes('hard') ? 'hard' : 
                         difficulties.includes('medium') ? 'medium' : 'easy'

    // Extract tags from title and description
    const tags = [
      ...quizData.title.toLowerCase().split(' ').filter((word: string) => word.length > 3),
      quizData.category.toLowerCase(),
      quizData.subject?.toLowerCase()
    ].filter(Boolean)

    const newQuiz: Quiz = {
      id: String(quizzes.length + 1),
      ...quizData,
      created_at: new Date().toISOString(),
      creator_id: "1", // Mock user ID - in real app, get from auth token
      creator_name: "Cari İstifadəçi", // Mock name - in real app, get from auth token
      total_questions: totalQuestions,
      total_points: totalPoints,
      total_attempts: 0,
      average_score: 0,
      difficulty: avgDifficulty,
      tags: tags.slice(0, 5), // Limit to 5 tags
      is_featured: false,
    }

    quizzes.push(newQuiz)
    
    // Save quizzes to persistent storage
    saveQuizzes(quizzes)

    return NextResponse.json(newQuiz, { status: 201 })
  } catch (error) {
    console.error("Quiz yaratma xətası:", error)
    return NextResponse.json({ detail: "Server xətası" }, { status: 500 })
  }
}
