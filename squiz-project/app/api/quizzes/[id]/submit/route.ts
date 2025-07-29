import { type NextRequest, NextResponse } from "next/server"
import { getQuizzes, saveQuizzes } from "@/lib/storage"

// Quiz results storage
const RESULTS_FILE = require('path').join(process.cwd(), 'data', 'quiz-results.json')
const fs = require('fs')

// Ensure results file exists
function getQuizResults() {
  try {
    if (fs.existsSync(RESULTS_FILE)) {
      const data = fs.readFileSync(RESULTS_FILE, 'utf8')
      return JSON.parse(data)
    } else {
      return []
    }
  } catch (error) {
    console.error('Error reading quiz results:', error)
    return []
  }
}

function saveQuizResults(results: any[]) {
  try {
    fs.writeFileSync(RESULTS_FILE, JSON.stringify(results, null, 2))
    return true
  } catch (error) {
    console.error('Error saving quiz results:', error)
    return false
  }
}

// POST - Submit quiz attempt
export async function POST(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  try {
    const submissionData = await request.json()
    const { answers, userId, userEmail, timeSpent } = submissionData

    // Get quiz
    const quizzes = getQuizzes()
    const quiz = quizzes.find(q => q.id === params.id)
    
    if (!quiz) {
      return NextResponse.json({ detail: "Quiz tapılmadı" }, { status: 404 })
    }

    // Calculate score
    let correctAnswers = 0
    let totalPoints = 0
    let earnedPoints = 0
    
    const detailedResults = quiz.questions.map((question: any, index: number) => {
      const userAnswer = answers[question.id] || answers[index]
      let isCorrect = false
      let pointsEarned = 0

      if (question.question_type === 'multiple_choice') {
        if (question.multiple_correct) {
          // Multiple correct answers
          const correctOptions = question.options
            .filter((opt: any) => opt.is_correct)
            .map((opt: any) => opt.text)
          
          const userAnswers = Array.isArray(userAnswer) ? userAnswer : [userAnswer]
          const correctCount = userAnswers.filter((ans: string) => correctOptions.includes(ans)).length
          const incorrectCount = userAnswers.filter((ans: string) => !correctOptions.includes(ans)).length
          
          if (correctCount === correctOptions.length && incorrectCount === 0) {
            isCorrect = true
            pointsEarned = question.points
          } else if (correctCount > 0) {
            // Partial credit
            pointsEarned = Math.round((correctCount / correctOptions.length) * question.points)
          }
        } else {
          // Single correct answer
          const correctOption = question.options.find((opt: any) => opt.is_correct)
          isCorrect = userAnswer === correctOption?.text
          pointsEarned = isCorrect ? question.points : 0
        }
      } else if (question.question_type === 'open_ended') {
        // Open-ended question evaluation
        const expectedAnswers = question.open_ended_answer?.expected_answers || []
        const keywords = question.open_ended_answer?.keywords || []
        const caseSensitive = question.open_ended_answer?.case_sensitive || false
        
        const userText = caseSensitive ? userAnswer : userAnswer?.toLowerCase()
        
        // Check exact matches
        const hasExactMatch = expectedAnswers.some((expected: string) => {
          const expectedText = caseSensitive ? expected : expected.toLowerCase()
          return userText === expectedText
        })
        
        // Check keyword matches
        const keywordMatches = keywords.filter((keyword: string) => {
          const keywordText = caseSensitive ? keyword : keyword.toLowerCase()
          return userText?.includes(keywordText)
        }).length
        
        if (hasExactMatch) {
          isCorrect = true
          pointsEarned = question.points
        } else if (keywordMatches > 0 && question.open_ended_answer?.partial_credit) {
          // Partial credit based on keyword matches
          pointsEarned = Math.round((keywordMatches / keywords.length) * question.points)
        }
      }

      if (isCorrect) correctAnswers++
      totalPoints += question.points
      earnedPoints += pointsEarned

      return {
        questionId: question.id,
        questionText: question.question_text,
        userAnswer,
        correctAnswer: question.question_type === 'multiple_choice' 
          ? question.options.filter((opt: any) => opt.is_correct).map((opt: any) => opt.text)
          : question.open_ended_answer?.expected_answers,
        isCorrect,
        pointsEarned,
        maxPoints: question.points,
        explanation: question.explanation
      }
    })

    const scorePercentage = totalPoints > 0 ? Math.round((earnedPoints / totalPoints) * 100) : 0
    const passed = scorePercentage >= (quiz.min_pass_percentage || 70)

    // Create result record
    const result = {
      id: `result_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      quizId: quiz.id,
      quizTitle: quiz.title,
      userId: userId || 'anonymous',
      userEmail: userEmail || '',
      submittedAt: new Date().toISOString(),
      timeSpent: timeSpent || 0,
      totalQuestions: quiz.questions.length,
      correctAnswers,
      totalPoints,
      earnedPoints,
      scorePercentage,
      passed,
      detailedResults
    }

    // Save result
    const results = getQuizResults()
    results.push(result)
    saveQuizResults(results)

    // Update quiz statistics
    const quizIndex = quizzes.findIndex(q => q.id === params.id)
    if (quizIndex !== -1) {
      quizzes[quizIndex].total_attempts = (quizzes[quizIndex].total_attempts || 0) + 1
      
      // Calculate new average score
      const allQuizResults = results.filter(r => r.quizId === quiz.id)
      const avgScore = allQuizResults.length > 0 
        ? Math.round(allQuizResults.reduce((sum, r) => sum + r.scorePercentage, 0) / allQuizResults.length)
        : 0
      
      quizzes[quizIndex].average_score = avgScore
      saveQuizzes(quizzes)
    }

    return NextResponse.json({
      success: true,
      result: {
        id: result.id,
        scorePercentage,
        earnedPoints,
        totalPoints,
        correctAnswers,
        totalQuestions: quiz.questions.length,
        passed,
        timeSpent,
        detailedResults
      }
    })

  } catch (error) {
    console.error("Quiz təqdim etmə xətası:", error)
    return NextResponse.json({ detail: "Server xətası" }, { status: 500 })
  }
}