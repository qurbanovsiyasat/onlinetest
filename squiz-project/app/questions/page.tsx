"use client"

import { useState, useEffect } from "react"
import { motion } from "framer-motion"
import { Plus, Search, Filter, Eye, ThumbsUp, MessageCircle, Share2, Calendar } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import DashboardLayout from "@/components/layout/DashboardLayout"
import MathTextRenderer from "@/components/MathTextRenderer"
import Link from "next/link"

interface SharedQuestion {
  id: string
  title: string
  question_text: string
  question_type: "multiple_choice" | "open_ended"
  category: string
  difficulty: "easy" | "medium" | "hard"
  options?: Array<{
    text: string
    is_correct: boolean
  }>
  expected_answers?: string[]
  explanation?: string
  math_formula?: string
  author: {
    name: string
    id: string
  }
  created_at: string
  likes: number
  views: number
  comments: number
  tags: string[]
  status: "pending" | "approved" | "rejected"
}

// Mock data for shared questions
const mockSharedQuestions: SharedQuestion[] = [
  {
    id: "1",
    title: "JavaScript Arrow Function",
    question_text: "Arrow function-ların this binding davranışı necədir?",
    question_type: "multiple_choice",
    category: "Programlaşdırma",
    difficulty: "medium",
    options: [
      { text: "Lexical binding istifadə edir", is_correct: true },
      { text: "Dynamic binding istifadə edir", is_correct: false },
      { text: "Global binding istifadə edir", is_correct: false },
      { text: "Heç bir binding yoxdur", is_correct: false }
    ],
    explanation: "Arrow function-lar this-i lexical olaraq bind edir, yəni öz this-ləri yoxdur.",
    author: { name: "Əli Məmmədov", id: "user1" },
    created_at: "2025-01-29T10:00:00Z",
    likes: 15,
    views: 87,
    comments: 5,
    tags: ["javascript", "arrow-function", "this"],
    status: "approved"
  },
  {
    id: "2", 
    title: "Riyaziyyat - Törəmə",
    question_text: "f(x) = x³ + 2x² - 5x + 3 funksiyasının törəməsi nədir?",
    question_type: "open_ended",
    category: "Riyaziyyat",
    difficulty: "hard",
    expected_answers: ["3x² + 4x - 5", "f'(x) = 3x² + 4x - 5"],
    explanation: "Hər hədin törəməsini ayrı-ayrı hesablamalıyıq.",
    math_formula: "f'(x) = 3x^2 + 4x - 5",
    author: { name: "Nigar Quliyeva", id: "user2" },
    created_at: "2025-01-28T14:30:00Z",
    likes: 23,
    views: 156,
    comments: 8,
    tags: ["riyaziyyat", "törəmə", "hesabat"],
    status: "approved"
  },
  {
    id: "3",
    title: "CSS Grid Layout",
    question_text: "CSS Grid-də grid-template-areas necə işləyir?",
    question_type: "multiple_choice", 
    category: "Dizayn",
    difficulty: "easy",
    options: [
      { text: "Grid sahələrini adlandırır", is_correct: true },
      { text: "Grid sütun sayısını təyin edir", is_correct: false },
      { text: "Grid sətir sayısını təyin edir", is_correct: false },
      { text: "Grid məsafəsini təyin edir", is_correct: false }
    ],
    explanation: "grid-template-areas grid sahələrinə ad verir və düzülüşü visual olaraq təyin edir.",
    author: { name: "Rəşad İsmayılov", id: "user3" },
    created_at: "2025-01-27T09:15:00Z",
    likes: 12,
    views: 94,
    comments: 3,
    tags: ["css", "grid", "layout"],
    status: "pending"
  }
]

export default function QuestionsPage() {
  const [questions, setQuestions] = useState<SharedQuestion[]>(mockSharedQuestions)
  const [filteredQuestions, setFilteredQuestions] = useState<SharedQuestion[]>(mockSharedQuestions)
  const [searchTerm, setSearchTerm] = useState("")
  const [selectedCategory, setSelectedCategory] = useState<string>("all")
  const [selectedDifficulty, setSelectedDifficulty] = useState<string>("all")
  const [activeTab, setActiveTab] = useState("all")

  useEffect(() => {
    filterQuestions()
  }, [searchTerm, selectedCategory, selectedDifficulty, activeTab, questions])

  const filterQuestions = () => {
    let filtered = questions

    // Tab filter
    if (activeTab === "approved") {
      filtered = filtered.filter((q) => q.status === "approved")
    } else if (activeTab === "pending") {
      filtered = filtered.filter((q) => q.status === "pending")
    } else if (activeTab === "popular") {
      filtered = filtered.filter((q) => q.likes > 10)
    }

    // Search filter
    if (searchTerm) {
      filtered = filtered.filter(
        (q) =>
          q.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
          q.question_text.toLowerCase().includes(searchTerm.toLowerCase()) ||
          q.category.toLowerCase().includes(searchTerm.toLowerCase()) ||
          q.tags.some((tag) => tag.toLowerCase().includes(searchTerm.toLowerCase()))
      )
    }

    // Category filter
    if (selectedCategory !== "all") {
      filtered = filtered.filter((q) => q.category === selectedCategory)
    }

    // Difficulty filter
    if (selectedDifficulty !== "all") {
      filtered = filtered.filter((q) => q.difficulty === selectedDifficulty)
    }

    // Sort by newest
    filtered.sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime())

    setFilteredQuestions(filtered)
  }

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
        return "Asan"
      case "medium":
        return "Orta"
      case "hard":
        return "Çətin"
      default:
        return "Bilinmir"
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case "approved":
        return "bg-green-100 text-green-800"
      case "pending":
        return "bg-yellow-100 text-yellow-800"
      case "rejected":
        return "bg-red-100 text-red-800"
      default:
        return "bg-gray-100 text-gray-800"
    }
  }

  const getStatusText = (status: string) => {
    switch (status) {
      case "approved":
        return "Təsdiqlənib"
      case "pending":
        return "Gözləmədə"
      case "rejected":
        return "Rədd edilib"
      default:
        return "Bilinmir"
    }
  }

  const categories = Array.from(new Set(questions.map((q) => q.category)))

  return (
    <DashboardLayout>
      <div className="space-y-8">
        {/* Header */}
        <div className="flex flex-col md:flex-row md:items-center md:justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Paylaşılmış Suallar</h1>
            <p className="text-gray-600 mt-2">İcma tərəfindən paylaşılmış sualları kəşf edin və öz suallarınızı əlavə edin</p>
          </div>

          <div className="flex gap-3 mt-4 md:mt-0">
            <Button
              asChild
              className="bg-gradient-to-r from-green-600 to-blue-600 hover:from-green-700 hover:to-blue-700"
            >
              <Link href="/questions/submit">
                <Plus className="w-4 h-4 mr-2" />
                Sual Paylaş
              </Link>
            </Button>
          </div>
        </div>

        {/* Tabs */}
        <Tabs value={activeTab} onValueChange={setActiveTab}>
          <TabsList className="grid w-full grid-cols-4">
            <TabsTrigger value="all">Hamısı ({questions.length})</TabsTrigger>
            <TabsTrigger value="approved">Təsdiqlənmiş ({questions.filter((q) => q.status === "approved").length})</TabsTrigger>
            <TabsTrigger value="pending">Gözləmədə ({questions.filter((q) => q.status === "pending").length})</TabsTrigger>
            <TabsTrigger value="popular">Populyar ({questions.filter((q) => q.likes > 10).length})</TabsTrigger>
          </TabsList>

          <TabsContent value={activeTab} className="space-y-6">
            {/* Filters */}
            <Card>
              <CardContent className="p-6">
                <div className="flex flex-col lg:flex-row gap-4">
                  {/* Search */}
                  <div className="flex-1">
                    <div className="relative">
                      <Search className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
                      <Input
                        placeholder="Sual axtar... (başlıq, mətn, etiket)"
                        value={searchTerm}
                        onChange={(e) => setSearchTerm(e.target.value)}
                        className="pl-10"
                      />
                    </div>
                  </div>

                  {/* Category Filter */}
                  <Select value={selectedCategory} onValueChange={setSelectedCategory}>
                    <SelectTrigger className="w-full lg:w-48">
                      <Filter className="w-4 h-4 mr-2" />
                      <SelectValue placeholder="Kateqoriya seçin" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="all">Bütün Kateqoriyalar</SelectItem>
                      {categories.map((category) => (
                        <SelectItem key={category} value={category}>
                          {category}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>

                  {/* Difficulty Filter */}
                  <Select value={selectedDifficulty} onValueChange={setSelectedDifficulty}>
                    <SelectTrigger className="w-full lg:w-48">
                      <SelectValue placeholder="Çətinlik seçin" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="all">Bütün Çətinliklər</SelectItem>
                      <SelectItem value="easy">Asan</SelectItem>
                      <SelectItem value="medium">Orta</SelectItem>
                      <SelectItem value="hard">Çətin</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </CardContent>
            </Card>

            {/* Questions Grid */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {filteredQuestions.map((question, index) => (
                <motion.div
                  key={question.id}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.5, delay: index * 0.1 }}
                >
                  <Card className="h-full hover:shadow-xl transition-all duration-300 group border-0 shadow-md">
                    <CardHeader className="pb-3">
                      <div className="flex items-start justify-between mb-2">
                        <div className="flex items-center gap-2 flex-wrap">
                          <Badge className={getDifficultyColor(question.difficulty)} variant="outline">
                            {getDifficultyText(question.difficulty)}
                          </Badge>
                          <Badge className={getStatusColor(question.status)} variant="outline">
                            {getStatusText(question.status)}
                          </Badge>
                          <Badge variant="outline" className="text-xs">
                            {question.question_type === "multiple_choice" ? "Çoxvariantlı" : "Açıq cavab"}
                          </Badge>
                        </div>
                      </div>

                      <CardTitle className="text-lg group-hover:text-blue-600 transition-colors line-clamp-2">
                        {question.title}
                      </CardTitle>
                    </CardHeader>

                    <CardContent className="space-y-4">
                      {/* Question Text */}
                      <div className="bg-gray-50 p-3 rounded-lg">
                        <p className="text-sm text-gray-700 font-medium mb-2">Sual:</p>
                        <div className="text-sm">
                          <MathTextRenderer text={question.question_text} />
                        </div>
                      </div>

                      {/* Math Formula */}
                      {question.math_formula && (
                        <div className="bg-blue-50 p-3 rounded-lg">
                          <p className="text-sm text-blue-700 font-medium mb-2">Formula:</p>
                          <div className="font-mono text-sm">
                            <MathTextRenderer text={question.math_formula} />
                          </div>
                        </div>
                      )}

                      {/* Multiple Choice Options Preview */}
                      {question.question_type === "multiple_choice" && question.options && (
                        <div className="space-y-2">
                          <p className="text-sm text-gray-600 font-medium">Variantlar:</p>
                          <div className="space-y-1">
                            {question.options.slice(0, 2).map((option, idx) => (
                              <div key={idx} className="flex items-center gap-2 text-xs">
                                <div className={`w-2 h-2 rounded-full ${option.is_correct ? 'bg-green-500' : 'bg-gray-300'}`} />
                                <span className="truncate">{option.text}</span>
                              </div>
                            ))}
                            {question.options.length > 2 && (
                              <p className="text-xs text-gray-500">+{question.options.length - 2} variant daha</p>
                            )}
                          </div>
                        </div>
                      )}

                      {/* Category and Tags */}
                      <div className="space-y-2">
                        <Badge variant="outline" className="text-xs">
                          {question.category}
                        </Badge>
                        <div className="flex flex-wrap gap-1">
                          {question.tags.slice(0, 3).map((tag) => (
                            <Badge key={tag} variant="secondary" className="text-xs px-2 py-0.5">
                              #{tag}
                            </Badge>
                          ))}
                          {question.tags.length > 3 && (
                            <Badge variant="secondary" className="text-xs px-2 py-0.5">
                              +{question.tags.length - 3}
                            </Badge>
                          )}
                        </div>
                      </div>

                      {/* Stats */}
                      <div className="grid grid-cols-3 gap-2 text-xs text-gray-600">
                        <div className="flex items-center gap-1">
                          <ThumbsUp className="w-3 h-3" />
                          <span>{question.likes}</span>
                        </div>
                        <div className="flex items-center gap-1">
                          <Eye className="w-3 h-3" />
                          <span>{question.views}</span>
                        </div>
                        <div className="flex items-center gap-1">
                          <MessageCircle className="w-3 h-3" />
                          <span>{question.comments}</span>
                        </div>
                      </div>

                      {/* Author and Date */}
                      <div className="text-xs text-gray-500 border-t pt-3">
                        <div className="flex items-center justify-between">
                          <span>
                            <span className="font-medium">{question.author.name}</span> tərəfindən
                          </span>
                          <div className="flex items-center gap-1">
                            <Calendar className="w-3 h-3" />
                            <span>{new Date(question.created_at).toLocaleDateString('az-AZ')}</span>
                          </div>
                        </div>
                      </div>

                      {/* Action Buttons */}
                      <div className="flex gap-2 pt-2">
                        <Button variant="outline" size="sm" className="flex-1">
                          <Eye className="w-3 h-3 mr-1" />
                          Bax
                        </Button>
                        <Button variant="outline" size="sm">
                          <ThumbsUp className="w-3 h-3" />
                        </Button>
                        <Button variant="outline" size="sm">
                          <Share2 className="w-3 h-3" />
                        </Button>
                      </div>
                    </CardContent>
                  </Card>
                </motion.div>
              ))}
            </div>

            {/* Empty State */}
            {filteredQuestions.length === 0 && (
              <div className="text-center py-12">
                <MessageCircle className="w-16 h-16 text-gray-400 mx-auto mb-4" />
                <h3 className="text-lg font-medium text-gray-900 mb-2">Sual tapılmadı</h3>
                <p className="text-gray-600 mb-6">
                  Axtarış kriteriyalarına uyğun sual tapılmadı. Filterləri dəyişməyi sınayın.
                </p>
                <div className="flex gap-3 justify-center">
                  <Button
                    onClick={() => {
                      setSearchTerm("")
                      setSelectedCategory("all")
                      setSelectedDifficulty("all")
                    }}
                    variant="outline"
                  >
                    Filterləri Təmizlə
                  </Button>
                  <Button asChild>
                    <Link href="/questions/submit">
                      <Plus className="w-4 h-4 mr-2" />
                      Sual Paylaş
                    </Link>
                  </Button>
                </div>
              </div>
            )}
          </TabsContent>
        </Tabs>
      </div>
    </DashboardLayout>
  )
}