import { type NextRequest, NextResponse } from "next/server"
import { getQuizzes, saveQuizzes } from "@/lib/storage"

// GET - Get single quiz by ID
export async function GET(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  try {
    const quizzes = getQuizzes()
    const quiz = quizzes.find(q => q.id === params.id)
    
    if (!quiz) {
      return NextResponse.json({ detail: "Quiz tapılmadı" }, { status: 404 })
    }

    return NextResponse.json(quiz)
  } catch (error) {
    console.error("Quiz əldə etmə xətası:", error)
    return NextResponse.json({ detail: "Server xətası" }, { status: 500 })
  }
}

// PUT - Update quiz
export async function PUT(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  try {
    const quizData = await request.json()
    const quizzes = getQuizzes()
    const quizIndex = quizzes.findIndex(q => q.id === params.id)
    
    if (quizIndex === -1) {
      return NextResponse.json({ detail: "Quiz tapılmadı" }, { status: 404 })
    }

    // Calculate updated statistics
    const totalQuestions = quizData.questions?.length || quizzes[quizIndex].total_questions
    const totalPoints = quizData.questions?.reduce((sum: number, q: any) => sum + q.points, 0) || 
                       quizzes[quizIndex].total_points

    // Update quiz
    quizzes[quizIndex] = {
      ...quizzes[quizIndex],
      ...quizData,
      total_questions: totalQuestions,
      total_points: totalPoints,
      updated_at: new Date().toISOString()
    }

    // Save to persistent storage
    saveQuizzes(quizzes)

    return NextResponse.json(quizzes[quizIndex])
  } catch (error) {
    console.error("Quiz yenilənmə xətası:", error)
    return NextResponse.json({ detail: "Server xətası" }, { status: 500 })
  }
}

// DELETE - Delete quiz
export async function DELETE(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  try {
    const quizzes = getQuizzes()
    const quizIndex = quizzes.findIndex(q => q.id === params.id)
    
    if (quizIndex === -1) {
      return NextResponse.json({ detail: "Quiz tapılmadı" }, { status: 404 })
    }

    quizzes.splice(quizIndex, 1)

    // Save to persistent storage
    saveQuizzes(quizzes)

    return NextResponse.json({ detail: "Quiz uğurla silindi" })
  } catch (error) {
    console.error("Quiz silmə xətası:", error)
    return NextResponse.json({ detail: "Server xətası" }, { status: 500 })
  }
}
