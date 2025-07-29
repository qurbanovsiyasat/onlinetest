import { type NextRequest, NextResponse } from "next/server"

// This would be imported from the main quizzes route in a real app
// For now, we'll maintain a simple in-memory store
let quizzes: any[] = []

// GET - Get single quiz by ID
export async function GET(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  try {
    const quiz = quizzes.find(q => q.id === params.id)
    
    if (!quiz) {
      return NextResponse.json({ detail: "Quiz bulunamadı" }, { status: 404 })
    }

    return NextResponse.json(quiz)
  } catch (error) {
    console.error("Quiz getirme xətası:", error)
    return NextResponse.json({ detail: "Sunucu hatası" }, { status: 500 })
  }
}

// PUT - Update quiz
export async function PUT(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  try {
    const quizData = await request.json()
    const quizIndex = quizzes.findIndex(q => q.id === params.id)
    
    if (quizIndex === -1) {
      return NextResponse.json({ detail: "Quiz bulunamadı" }, { status: 404 })
    }

    // Update quiz
    quizzes[quizIndex] = {
      ...quizzes[quizIndex],
      ...quizData,
      updated_at: new Date().toISOString()
    }

    return NextResponse.json(quizzes[quizIndex])
  } catch (error) {
    console.error("Quiz güncelleme xətası:", error)
    return NextResponse.json({ detail: "Sunucu hatası" }, { status: 500 })
  }
}

// DELETE - Delete quiz
export async function DELETE(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  try {
    const quizIndex = quizzes.findIndex(q => q.id === params.id)
    
    if (quizIndex === -1) {
      return NextResponse.json({ detail: "Quiz bulunamadı" }, { status: 404 })
    }

    quizzes.splice(quizIndex, 1)

    return NextResponse.json({ detail: "Quiz başarıyla silindi" })
  } catch (error) {
    console.error("Quiz silme xətası:", error)
    return NextResponse.json({ detail: "Sunucu hatası" }, { status: 500 })
  }
}
