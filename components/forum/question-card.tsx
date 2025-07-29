"use client"

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import { MessageCircle, ThumbsUp, ThumbsDown, Eye, Clock, CheckCircle, HelpCircle } from "lucide-react"

interface QuestionCardProps {
  question: {
    _id: string
    title: string
    content: string
    category: string
    tags: string[]
    author: {
      name: string
      avatar?: string
      reputation: number
    }
    votes: {
      up: number
      down: number
      user_vote?: "up" | "down" | null
    }
    answers_count: number
    views: number
    is_solved: boolean
    created_at: string
    updated_at: string
  }
  onVote: (questionId: string, vote: "up" | "down") => void
  onView: (questionId: string) => void
}

export function QuestionCard({ question, onVote, onView }: QuestionCardProps) {
  const getInitials = (name: string) => {
    return name
      .split(" ")
      .map((word) => word[0])
      .join("")
      .toUpperCase()
      .slice(0, 2)
  }

  const formatTimeAgo = (dateString: string) => {
    const date = new Date(dateString)
    const now = new Date()
    const diffInSeconds = Math.floor((now.getTime() - date.getTime()) / 1000)

    if (diffInSeconds < 60) {
      return "Az önce"
    } else if (diffInSeconds < 3600) {
      const minutes = Math.floor(diffInSeconds / 60)
      return `${minutes} dakika önce`
    } else if (diffInSeconds < 86400) {
      const hours = Math.floor(diffInSeconds / 3600)
      return `${hours} saat önce`
    } else if (diffInSeconds < 2592000) {
      const days = Math.floor(diffInSeconds / 86400)
      return `${days} gün önce`
    } else {
      return date.toLocaleDateString("tr-TR")
    }
  }

  const getCategoryColor = (category: string) => {
    const colors = {
      Programlama: "bg-blue-100 text-blue-800 border-blue-200",
      Frontend: "bg-green-100 text-green-800 border-green-200",
      Backend: "bg-purple-100 text-purple-800 border-purple-200",
      "Veri Bilimi": "bg-orange-100 text-orange-800 border-orange-200",
      Mobil: "bg-pink-100 text-pink-800 border-pink-200",
      DevOps: "bg-gray-100 text-gray-800 border-gray-200",
    }
    return colors[category as keyof typeof colors] || "bg-gray-100 text-gray-800 border-gray-200"
  }

  const getStatusIcon = () => {
    if (question.is_solved) {
      return <CheckCircle className="w-4 h-4 text-green-600" />
    } else if (question.answers_count > 0) {
      return <MessageCircle className="w-4 h-4 text-blue-600" />
    } else {
      return <HelpCircle className="w-4 h-4 text-gray-400" />
    }
  }

  const getStatusText = () => {
    if (question.is_solved) {
      return "Çözüldü"
    } else if (question.answers_count > 0) {
      return "Cevaplandı"
    } else {
      return "Bekliyor"
    }
  }

  const getStatusColor = () => {
    if (question.is_solved) {
      return "text-green-600"
    } else if (question.answers_count > 0) {
      return "text-blue-600"
    } else {
      return "text-gray-500"
    }
  }

  return (
    <Card className="group hover:shadow-lg transition-all duration-300 border-l-4 border-l-blue-500">
      <CardHeader className="pb-3">
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <div className="flex items-center space-x-2 mb-2">
              {getStatusIcon()}
              <span className={`text-sm font-medium ${getStatusColor()}`}>{getStatusText()}</span>
              <Badge className={getCategoryColor(question.category)}>{question.category}</Badge>
            </div>

            <CardTitle
              className="text-lg font-semibold text-gray-900 group-hover:text-blue-600 transition-colors cursor-pointer line-clamp-2"
              onClick={() => onView(question._id)}
            >
              {question.title}
            </CardTitle>

            <CardDescription className="mt-2 text-sm text-gray-600 line-clamp-3">{question.content}</CardDescription>
          </div>
        </div>

        {/* Tags */}
        {question.tags.length > 0 && (
          <div className="flex flex-wrap gap-1 mt-3">
            {question.tags.slice(0, 3).map((tag, index) => (
              <Badge key={index} variant="outline" className="text-xs bg-gray-50 text-gray-600">
                {tag}
              </Badge>
            ))}
            {question.tags.length > 3 && (
              <Badge variant="outline" className="text-xs bg-gray-50 text-gray-500">
                +{question.tags.length - 3}
              </Badge>
            )}
          </div>
        )}
      </CardHeader>

      <CardContent className="pt-0">
        <div className="space-y-4">
          {/* Author Info */}
          <div className="flex items-center space-x-3">
            <Avatar className="w-8 h-8">
              <AvatarImage src={question.author.avatar || "/placeholder.svg"} />
              <AvatarFallback className="text-xs bg-blue-100 text-blue-700">
                {getInitials(question.author.name)}
              </AvatarFallback>
            </Avatar>
            <div className="flex-1">
              <div className="flex items-center space-x-2">
                <span className="text-sm font-medium text-gray-700">{question.author.name}</span>
                <Badge variant="outline" className="text-xs bg-yellow-50 text-yellow-700 border-yellow-200">
                  {question.author.reputation} puan
                </Badge>
              </div>
              <div className="flex items-center space-x-1 text-xs text-gray-500">
                <Clock className="w-3 h-3" />
                <span>{formatTimeAgo(question.created_at)}</span>
              </div>
            </div>
          </div>

          {/* Stats and Actions */}
          <div className="flex items-center justify-between pt-2 border-t border-gray-100">
            <div className="flex items-center space-x-4 text-sm text-gray-500">
              <div className="flex items-center space-x-1">
                <Eye className="w-4 h-4" />
                <span>{question.views}</span>
              </div>
              <div className="flex items-center space-x-1">
                <MessageCircle className="w-4 h-4" />
                <span>{question.answers_count} cevap</span>
              </div>
            </div>

            {/* Voting */}
            <div className="flex items-center space-x-2">
              <div className="flex items-center space-x-1">
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => onVote(question._id, "up")}
                  className={`p-1 h-8 w-8 ${
                    question.votes.user_vote === "up"
                      ? "text-green-600 bg-green-50"
                      : "text-gray-500 hover:text-green-600 hover:bg-green-50"
                  }`}
                >
                  <ThumbsUp className="w-4 h-4" />
                </Button>
                <span className="text-sm font-medium text-gray-700 min-w-[20px] text-center">
                  {question.votes.up - question.votes.down}
                </span>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => onVote(question._id, "down")}
                  className={`p-1 h-8 w-8 ${
                    question.votes.user_vote === "down"
                      ? "text-red-600 bg-red-50"
                      : "text-gray-500 hover:text-red-600 hover:bg-red-50"
                  }`}
                >
                  <ThumbsDown className="w-4 h-4" />
                </Button>
              </div>

              <Button
                variant="outline"
                size="sm"
                onClick={() => onView(question._id)}
                className="text-blue-600 hover:text-blue-700 hover:bg-blue-50"
              >
                Görüntüle
              </Button>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}
