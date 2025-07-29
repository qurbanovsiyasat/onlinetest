"use client"

import { useState, useEffect } from "react"
import { QuizCard } from "./quiz-card"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { apiMethods } from "@/lib/api"
import { Search, Filter, BookOpen, Clock, TrendingUp } from "lucide-react"
import { useToast } from "@/hooks/use-toast"

interface QuizListProps {
  onQuizAttempt: (quizId: string) => void
}

export function QuizList({ onQuizAttempt }: QuizListProps) {
  const [quizzes, setQuizzes] = useState<any[]>([])
  const [filteredQuizzes, setFilteredQuizzes] = useState<any[]>([])
  const [loading, setLoading] = useState(true)
  const [searchTerm, setSearchTerm] = useState("")
  const [selectedCategory, setSelectedCategory] = useState("all")
  const [selectedDifficulty, setSelectedDifficulty] = useState("all")
  const [userStats, setUserStats] = useState<any>({})
  const { toast } = useToast()

  // Mock data for development
  const mockQuizzes = [
    {
      _id: "1",
      title: "JavaScript Temelleri",
      description:
        "JavaScript programlama dilinin temel kavramlarını öğrenin. Değişkenler, fonksiyonlar, döngüler ve daha fazlası.",
      category: "Programlama",
      difficulty: "easy",
      questions: Array(15).fill({}),
      time_limit: 30,
      attempts_count: 245,
      max_attempts: 3,
      is_active: true,
      created_by: { name: "Ahmet Yılmaz" },
      created_at: "2024-01-15T10:00:00Z",
    },
    {
      _id: "2",
      title: "React Hooks Derinlemesine",
      description:
        "React Hooks kullanarak modern React uygulamaları geliştirmeyi öğrenin. useState, useEffect ve custom hooks.",
      category: "Frontend",
      difficulty: "medium",
      questions: Array(20).fill({}),
      time_limit: 45,
      attempts_count: 189,
      max_attempts: 2,
      is_active: true,
      created_by: { name: "Fatma Demir" },
      created_at: "2024-01-20T14:30:00Z",
    },
    {
      _id: "3",
      title: "Node.js ve Express",
      description:
        "Backend geliştirme için Node.js ve Express framework kullanımını öğrenin. API geliştirme ve veritabanı entegrasyonu.",
      category: "Backend",
      difficulty: "hard",
      questions: Array(25).fill({}),
      time_limit: 60,
      attempts_count: 156,
      max_attempts: 1,
      is_active: true,
      created_by: { name: "Mehmet Kaya" },
      created_at: "2024-01-25T09:15:00Z",
    },
    {
      _id: "4",
      title: "CSS Grid ve Flexbox",
      description: "Modern CSS layout teknikleri ile responsive tasarımlar oluşturun. Grid ve Flexbox kullanımı.",
      category: "Frontend",
      difficulty: "medium",
      questions: Array(18).fill({}),
      time_limit: 40,
      attempts_count: 312,
      max_attempts: 0,
      is_active: true,
      created_by: { name: "Ayşe Özkan" },
      created_at: "2024-01-28T16:45:00Z",
    },
    {
      _id: "5",
      title: "Python Veri Analizi",
      description: "Python ile veri analizi yapmayı öğrenin. Pandas, NumPy ve Matplotlib kütüphaneleri.",
      category: "Veri Bilimi",
      difficulty: "hard",
      questions: Array(22).fill({}),
      time_limit: 75,
      attempts_count: 98,
      max_attempts: 2,
      is_active: false,
      created_by: { name: "Ali Şahin" },
      created_at: "2024-02-01T11:20:00Z",
    },
    {
      _id: "6",
      title: "HTML5 Semantik Etiketler",
      description: "HTML5 ile semantik web sayfaları oluşturun. Erişilebilirlik ve SEO optimizasyonu.",
      category: "Frontend",
      difficulty: "easy",
      questions: Array(12).fill({}),
      time_limit: 25,
      attempts_count: 445,
      max_attempts: 5,
      is_active: true,
      created_by: { name: "Zeynep Arslan" },
      created_at: "2024-02-05T13:10:00Z",
    },
  ]

  const mockUserStats = {
    "1": { attempts: 2, bestScore: 85 },
    "2": { attempts: 1, bestScore: 92 },
    "4": { attempts: 3, bestScore: 78 },
    "6": { attempts: 1, bestScore: 95 },
  }

  useEffect(() => {
    fetchQuizzes()
  }, [])

  useEffect(() => {
    filterQuizzes()
  }, [quizzes, searchTerm, selectedCategory, selectedDifficulty])

  const fetchQuizzes = async () => {
    try {
      setLoading(true)
      // Try to fetch from API, fallback to mock data
      try {
        const response = await apiMethods.quizzes.list()
        setQuizzes(response.data)

        // Fetch user stats
        const statsResponse = await apiMethods.users.getStats()
        setUserStats(statsResponse.data.quiz_attempts || {})
      } catch (apiError) {
        console.warn("API not available, using mock data")
        setQuizzes(mockQuizzes)
        setUserStats(mockUserStats)
      }
    } catch (error) {
      console.error("Error fetching quizzes:", error)
      toast({
        title: "Hata",
        description: "Quizler yüklenirken bir hata oluştu.",
        variant: "destructive",
      })
      // Use mock data as fallback
      setQuizzes(mockQuizzes)
      setUserStats(mockUserStats)
    } finally {
      setLoading(false)
    }
  }

  const filterQuizzes = () => {
    let filtered = quizzes

    // Search filter
    if (searchTerm) {
      filtered = filtered.filter(
        (quiz) =>
          quiz.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
          quiz.description.toLowerCase().includes(searchTerm.toLowerCase()) ||
          quiz.category.toLowerCase().includes(searchTerm.toLowerCase()),
      )
    }

    // Category filter
    if (selectedCategory !== "all") {
      filtered = filtered.filter((quiz) => quiz.category === selectedCategory)
    }

    // Difficulty filter
    if (selectedDifficulty !== "all") {
      filtered = filtered.filter((quiz) => quiz.difficulty === selectedDifficulty)
    }

    setFilteredQuizzes(filtered)
  }

  const getCategories = () => {
    const categories = [...new Set(quizzes.map((quiz) => quiz.category))]
    return categories
  }

  const getStats = () => {
    const totalQuizzes = quizzes.length
    const activeQuizzes = quizzes.filter((q) => q.is_active).length
    const completedQuizzes = Object.keys(userStats).length
    const avgScore =
      Object.values(userStats).reduce((acc: number, stat: any) => acc + (stat.bestScore || 0), 0) /
      Math.max(completedQuizzes, 1)

    return { totalQuizzes, activeQuizzes, completedQuizzes, avgScore: Math.round(avgScore) }
  }

  if (loading) {
    return (
      <div className="space-y-6">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {[1, 2, 3].map((i) => (
            <Card key={i} className="animate-pulse">
              <CardContent className="p-6">
                <div className="h-4 bg-gray-200 rounded w-3/4 mb-2"></div>
                <div className="h-3 bg-gray-200 rounded w-1/2"></div>
              </CardContent>
            </Card>
          ))}
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {[1, 2, 3, 4, 5, 6].map((i) => (
            <Card key={i} className="animate-pulse">
              <CardHeader>
                <div className="h-5 bg-gray-200 rounded w-3/4 mb-2"></div>
                <div className="h-4 bg-gray-200 rounded w-full"></div>
              </CardHeader>
              <CardContent>
                <div className="h-4 bg-gray-200 rounded w-1/2 mb-4"></div>
                <div className="h-10 bg-gray-200 rounded"></div>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    )
  }

  const stats = getStats()

  return (
    <div className="space-y-6">
      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card className="bg-gradient-to-r from-blue-500 to-blue-600 text-white">
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-blue-100 text-sm">Toplam Quiz</p>
                <p className="text-2xl font-bold">{stats.totalQuizzes}</p>
              </div>
              <BookOpen className="w-8 h-8 text-blue-200" />
            </div>
          </CardContent>
        </Card>

        <Card className="bg-gradient-to-r from-green-500 to-green-600 text-white">
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-green-100 text-sm">Aktif Quiz</p>
                <p className="text-2xl font-bold">{stats.activeQuizzes}</p>
              </div>
              <Clock className="w-8 h-8 text-green-200" />
            </div>
          </CardContent>
        </Card>

        <Card className="bg-gradient-to-r from-purple-500 to-purple-600 text-white">
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-purple-100 text-sm">Tamamlanan</p>
                <p className="text-2xl font-bold">{stats.completedQuizzes}</p>
              </div>
              <TrendingUp className="w-8 h-8 text-purple-200" />
            </div>
          </CardContent>
        </Card>

        <Card className="bg-gradient-to-r from-orange-500 to-orange-600 text-white">
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-orange-100 text-sm">Ortalama Skor</p>
                <p className="text-2xl font-bold">{stats.avgScore}%</p>
              </div>
              <TrendingUp className="w-8 h-8 text-orange-200" />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Filters */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <Filter className="w-5 h-5" />
            <span>Filtreler</span>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
              <Input
                placeholder="Quiz ara..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-10"
              />
            </div>

            <Select value={selectedCategory} onValueChange={setSelectedCategory}>
              <SelectTrigger>
                <SelectValue placeholder="Kategori seçin" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">Tüm Kategoriler</SelectItem>
                {getCategories().map((category) => (
                  <SelectItem key={category} value={category}>
                    {category}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>

            <Select value={selectedDifficulty} onValueChange={setSelectedDifficulty}>
              <SelectTrigger>
                <SelectValue placeholder="Zorluk seçin" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">Tüm Zorluklar</SelectItem>
                <SelectItem value="easy">Kolay</SelectItem>
                <SelectItem value="medium">Orta</SelectItem>
                <SelectItem value="hard">Zor</SelectItem>
              </SelectContent>
            </Select>
          </div>

          {/* Active Filters */}
          <div className="flex flex-wrap gap-2 mt-4">
            {searchTerm && (
              <Badge variant="secondary" className="bg-blue-100 text-blue-800">
                Arama: {searchTerm}
                <button onClick={() => setSearchTerm("")} className="ml-2 text-blue-600 hover:text-blue-800">
                  ×
                </button>
              </Badge>
            )}
            {selectedCategory !== "all" && (
              <Badge variant="secondary" className="bg-green-100 text-green-800">
                Kategori: {selectedCategory}
                <button onClick={() => setSelectedCategory("all")} className="ml-2 text-green-600 hover:text-green-800">
                  ×
                </button>
              </Badge>
            )}
            {selectedDifficulty !== "all" && (
              <Badge variant="secondary" className="bg-orange-100 text-orange-800">
                Zorluk: {selectedDifficulty === "easy" ? "Kolay" : selectedDifficulty === "medium" ? "Orta" : "Zor"}
                <button
                  onClick={() => setSelectedDifficulty("all")}
                  className="ml-2 text-orange-600 hover:text-orange-800"
                >
                  ×
                </button>
              </Badge>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Quiz Grid */}
      {filteredQuizzes.length === 0 ? (
        <Card>
          <CardContent className="p-12 text-center">
            <BookOpen className="w-16 h-16 text-gray-300 mx-auto mb-4" />
            <h3 className="text-lg font-semibold text-gray-600 mb-2">Quiz bulunamadı</h3>
            <p className="text-gray-500 mb-4">
              {searchTerm || selectedCategory !== "all" || selectedDifficulty !== "all"
                ? "Arama kriterlerinize uygun quiz bulunamadı. Filtreleri temizleyip tekrar deneyin."
                : "Henüz hiç quiz eklenmemiş."}
            </p>
            {(searchTerm || selectedCategory !== "all" || selectedDifficulty !== "all") && (
              <Button
                onClick={() => {
                  setSearchTerm("")
                  setSelectedCategory("all")
                  setSelectedDifficulty("all")
                }}
                variant="outline"
              >
                Filtreleri Temizle
              </Button>
            )}
          </CardContent>
        </Card>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredQuizzes.map((quiz) => (
            <QuizCard
              key={quiz._id}
              quiz={quiz}
              userAttempts={userStats[quiz._id]?.attempts || 0}
              bestScore={userStats[quiz._id]?.bestScore}
              onAttempt={onQuizAttempt}
            />
          ))}
        </div>
      )}

      {/* Results Summary */}
      {filteredQuizzes.length > 0 && (
        <div className="text-center text-sm text-gray-500">
          {filteredQuizzes.length} quiz gösteriliyor
          {filteredQuizzes.length !== quizzes.length && ` (toplam ${quizzes.length} quiz)`}
        </div>
      )}
    </div>
  )
}
