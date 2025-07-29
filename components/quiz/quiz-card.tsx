"use client"

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Progress } from "@/components/ui/progress"
import { Clock, Users, Trophy, BookOpen, Play, CheckCircle } from "lucide-react"

interface QuizCardProps {
  quiz: {
    _id: string
    title: string
    description: string
    category: string
    difficulty: "easy" | "medium" | "hard"
    questions: any[]
    time_limit: number
    attempts_count: number
    max_attempts: number
    is_active: boolean
    created_by: {
      name: string
    }
    created_at: string
  }
  userAttempts?: number
  bestScore?: number
  onAttempt: (quizId: string) => void
}

export function QuizCard({ quiz, userAttempts = 0, bestScore, onAttempt }: QuizCardProps) {
  const getDifficultyColor = (difficulty: string) => {
    switch (difficulty) {
      case "easy":
        return "bg-green-100 text-green-800 border-green-200"
      case "medium":
        return "bg-yellow-100 text-yellow-800 border-yellow-200"
      case "hard":
        return "bg-red-100 text-red-800 border-red-200"
      default:
        return "bg-gray-100 text-gray-800 border-gray-200"
    }
  }

  const getDifficultyText = (difficulty: string) => {
    switch (difficulty) {
      case "easy":
        return "Kolay"
      case "medium":
        return "Orta"
      case "hard":
        return "Zor"
      default:
        return "Bilinmiyor"
    }
  }

  const formatTimeLimit = (minutes: number) => {
    if (minutes < 60) {
      return `${minutes} dk`
    }
    const hours = Math.floor(minutes / 60)
    const remainingMinutes = minutes % 60
    return remainingMinutes > 0 ? `${hours}s ${remainingMinutes}dk` : `${hours} saat`
  }

  const canAttempt = quiz.max_attempts === 0 || userAttempts < quiz.max_attempts
  const completionRate = quiz.max_attempts > 0 ? (userAttempts / quiz.max_attempts) * 100 : 0

  return (
    <Card className="group hover:shadow-lg transition-all duration-300 border-l-4 border-l-indigo-500">
      <CardHeader className="pb-3">
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <CardTitle className="text-lg font-semibold text-gray-900 group-hover:text-indigo-600 transition-colors">
              {quiz.title}
            </CardTitle>
            <CardDescription className="mt-1 text-sm text-gray-600 line-clamp-2">{quiz.description}</CardDescription>
          </div>
          <Badge className={`ml-2 ${getDifficultyColor(quiz.difficulty)}`}>{getDifficultyText(quiz.difficulty)}</Badge>
        </div>

        <div className="flex items-center space-x-4 mt-3 text-sm text-gray-500">
          <div className="flex items-center space-x-1">
            <BookOpen className="w-4 h-4" />
            <span>{quiz.questions.length} soru</span>
          </div>
          <div className="flex items-center space-x-1">
            <Clock className="w-4 h-4" />
            <span>{formatTimeLimit(quiz.time_limit)}</span>
          </div>
          <div className="flex items-center space-x-1">
            <Users className="w-4 h-4" />
            <span>{quiz.attempts_count} deneme</span>
          </div>
        </div>
      </CardHeader>

      <CardContent className="pt-0">
        <div className="space-y-4">
          {/* Category and Creator */}
          <div className="flex items-center justify-between text-sm">
            <Badge variant="outline" className="bg-blue-50 text-blue-700 border-blue-200">
              {quiz.category}
            </Badge>
            <span className="text-gray-500">{quiz.created_by.name} tarafından</span>
          </div>

          {/* User Progress */}
          {userAttempts > 0 && (
            <div className="space-y-2">
              <div className="flex items-center justify-between text-sm">
                <span className="text-gray-600">İlerleme</span>
                <span className="text-gray-500">
                  {userAttempts}/{quiz.max_attempts > 0 ? quiz.max_attempts : "∞"} deneme
                </span>
              </div>
              {quiz.max_attempts > 0 && <Progress value={completionRate} className="h-2" />}
              {bestScore !== undefined && (
                <div className="flex items-center space-x-1 text-sm text-green-600">
                  <Trophy className="w-4 h-4" />
                  <span>En iyi skor: {bestScore}%</span>
                </div>
              )}
            </div>
          )}

          {/* Action Button */}
          <div className="flex items-center justify-between pt-2">
            <div className="text-xs text-gray-400">{new Date(quiz.created_at).toLocaleDateString("tr-TR")}</div>

            <Button
              onClick={() => onAttempt(quiz._id)}
              disabled={!quiz.is_active || !canAttempt}
              className={`
                ${
                  canAttempt && quiz.is_active
                    ? "bg-indigo-600 hover:bg-indigo-700 text-white"
                    : "bg-gray-100 text-gray-400 cursor-not-allowed"
                }
                transition-all duration-200
              `}
            >
              {!quiz.is_active ? (
                <>
                  <CheckCircle className="w-4 h-4 mr-2" />
                  Pasif
                </>
              ) : !canAttempt ? (
                <>
                  <CheckCircle className="w-4 h-4 mr-2" />
                  Tamamlandı
                </>
              ) : (
                <>
                  <Play className="w-4 h-4 mr-2" />
                  {userAttempts > 0 ? "Tekrar Çöz" : "Çözmeye Başla"}
                </>
              )}
            </Button>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}
