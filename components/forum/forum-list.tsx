"use client"

import { useState, useEffect } from "react"
import { QuestionCard } from "./question-card"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Button } from "@/components/ui/button"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Badge } from "@/components/ui/badge"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { apiMethods } from "@/lib/api"
import { Search, Filter, Plus, MessageCircle, CheckCircle, HelpCircle, Users } from "lucide-react"
import { useToast } from "@/hooks/use-toast"

export function ForumList() {
  const [questions, setQuestions] = useState<any[]>([])
  const [filteredQuestions, setFilteredQuestions] = useState<any[]>([])
  const [loading, setLoading] = useState(true)
  const [searchTerm, setSearchTerm] = useState("")
  const [selectedCategory, setSelectedCategory] = useState("all")
  const [sortBy, setSortBy] = useState("recent")
  const [activeTab, setActiveTab] = useState("all")
  const { toast } = useToast()

  // Mock data for development
  const mockQuestions = [
    {
      _id: "1",
      title: "React Hook'ları nasıl optimize edebilirim?",
      content:
        "React uygulamalarımda performans sorunları yaşıyorum. Hook'ları daha verimli kullanmak için hangi teknikleri önerirsiniz? Özellikle useEffect ve useState ile ilgili best practice'ler nelerdir?",
      category: "Frontend",
      tags: ["react", "hooks", "performance", "optimization"],
      author: {
        name: "Ahmet Yılmaz",
        avatar: "/placeholder-user.jpg",
        reputation: 1250,
      },
      votes: { up: 15, down: 2, user_vote: null },
      answers_count: 8,
      views: 234,
      is_solved: true,
      created_at: "2024-01-20T10:30:00Z",
      updated_at: "2024-01-21T14:20:00Z",
    },
    {
      _id: "2",
      title: "Node.js'de async/await vs Promise hangisini kullanmalıyım?",
      content:
        "Backend geliştirirken asenkron işlemler için async/await mi yoksa Promise chain mi kullanmalıyım? Her ikisinin de avantaj ve dezavantajları nelerdir?",
      category: "Backend",
      tags: ["nodejs", "async", "promises", "javascript"],
      author: {
        name: "Fatma Demir",
        avatar: "/placeholder-user.jpg",
        reputation: 890,
      },
      votes: { up: 12, down: 1, user_vote: "up" },
      answers_count: 5,
      views: 189,
      is_solved: false,
      created_at: "2024-01-19T16:45:00Z",
      updated_at: "2024-01-20T09:15:00Z",
    },
    {
      _id: "3",
      title: "CSS Grid vs Flexbox - Hangi durumda hangisini kullanmalıyım?",
      content:
        "Layout oluştururken CSS Grid ve Flexbox arasında kararsız kalıyorum. Hangi durumda hangisini tercih etmeliyim? Pratik örneklerle açıklayabilir misiniz?",
      category: "Frontend",
      tags: ["css", "grid", "flexbox", "layout"],
      author: {
        name: "Mehmet Kaya",
        avatar: "/placeholder-user.jpg",
        reputation: 2100,
      },
      votes: { up: 25, down: 0, user_vote: null },
      answers_count: 12,
      views: 456,
      is_solved: true,
      created_at: "2024-01-18T11:20:00Z",
      updated_at: "2024-01-19T13:30:00Z",
    },
    {
      _id: "4",
      title: "Python'da veri analizi için hangi kütüphaneleri önerirsiniz?",
      content:
        "Veri bilimi alanında yeniyim. Python ile veri analizi yapmak için hangi kütüphaneleri öğrenmeliyim? Pandas, NumPy, Matplotlib dışında başka önerileriniz var mı?",
      category: "Veri Bilimi",
      tags: ["python", "data-analysis", "pandas", "numpy"],
      author: {
        name: "Ayşe Özkan",
        avatar: "/placeholder-user.jpg",
        reputation: 650,
      },
      votes: { up: 8, down: 0, user_vote: null },
      answers_count: 3,
      views: 123,
      is_solved: false,
      created_at: "2024-01-17T14:10:00Z",
      updated_at: "2024-01-18T08:45:00Z",
    },
    {
      _id: "5",
      title: "Docker container'ları production'da nasıl yönetmeliyim?",
      content:
        "Docker ile geliştirdiğim uygulamayı production ortamına deploy etmek istiyorum. Container orchestration için hangi araçları kullanmalıyım? Kubernetes gerekli mi?",
      category: "DevOps",
      tags: ["docker", "production", "kubernetes", "deployment"],
      author: {
        name: "Ali Şahin",
        avatar: "/placeholder-user.jpg",
        reputation: 1800,
      },
      votes: { up: 18, down: 3, user_vote: "down" },
      answers_count: 0,
      views: 67,
      is_solved: false,
      created_at: "2024-01-16T09:30:00Z",
      updated_at: "2024-01-16T09:30:00Z",
    },
    {
      _id: "6",
      title: "React Native vs Flutter - Mobil uygulama geliştirme için hangisi?",
      content:
        "Cross-platform mobil uygulama geliştirmek istiyorum. React Native mi Flutter mı daha iyi bir seçim? Her ikisinin de artı ve eksi yönlerini değerlendirebilir misiniz?",
      category: "Mobil",
      tags: ["react-native", "flutter", "mobile", "cross-platform"],
      author: {
        name: "Zeynep Arslan",
        avatar: "/placeholder-user.jpg",
        reputation: 1450,
      },
      votes: { up: 22, down: 4, user_vote: null },
      answers_count: 15,
      views: 789,
      is_solved: true,
      created_at: "2024-01-15T13:20:00Z",
      updated_at: "2024-01-16T16:40:00Z",
    },
  ]

  useEffect(() => {
    fetchQuestions()
  }, [])

  useEffect(() => {
    filterAndSortQuestions()
  }, [questions, searchTerm, selectedCategory, sortBy, activeTab])

  const fetchQuestions = async () => {
    try {
      setLoading(true)
      // Try to fetch from API, fallback to mock data
      try {
        const response = await apiMethods.forum.getQuestions()
        setQuestions(response.data)
      } catch (apiError) {
        console.warn("API not available, using mock data")
        setQuestions(mockQuestions)
      }
    } catch (error) {
      console.error("Error fetching questions:", error)
      toast({
        title: "Hata",
        description: "Sorular yüklenirken bir hata oluştu.",
        variant: "destructive",
      })
      // Use mock data as fallback
      setQuestions(mockQuestions)
    } finally {
      setLoading(false)
    }
  }

  const filterAndSortQuestions = () => {
    let filtered = questions

    // Tab filter
    if (activeTab === "solved") {
      filtered = filtered.filter((q) => q.is_solved)
    } else if (activeTab === "unsolved") {
      filtered = filtered.filter((q) => !q.is_solved)
    } else if (activeTab === "unanswered") {
      filtered = filtered.filter((q) => q.answers_count === 0)
    }

    // Search filter
    if (searchTerm) {
      filtered = filtered.filter(
        (question) =>
          question.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
          question.content.toLowerCase().includes(searchTerm.toLowerCase()) ||
          question.tags.some((tag: string) => tag.toLowerCase().includes(searchTerm.toLowerCase())),
      )
    }

    // Category filter
    if (selectedCategory !== "all") {
      filtered = filtered.filter((question) => question.category === selectedCategory)
    }

    // Sort
    filtered.sort((a, b) => {
      switch (sortBy) {
        case "recent":
          return new Date(b.updated_at).getTime() - new Date(a.updated_at).getTime()
        case "popular":
          return b.votes.up - b.votes.down - (a.votes.up - a.votes.down)
        case "views":
          return b.views - a.views
        case "answers":
          return b.answers_count - a.answers_count
        default:
          return 0
      }
    })

    setFilteredQuestions(filtered)
  }

  const handleVote = async (questionId: string, vote: "up" | "down") => {
    try {
      await apiMethods.forum.voteQuestion(questionId, vote)

      // Update local state
      setQuestions((prev) =>
        prev.map((q) => {
          if (q._id === questionId) {
            const newVotes = { ...q.votes }

            // Remove previous vote if exists
            if (q.votes.user_vote === "up") newVotes.up--
            if (q.votes.user_vote === "down") newVotes.down--

            // Add new vote if different from current
            if (q.votes.user_vote !== vote) {
              if (vote === "up") newVotes.up++
              if (vote === "down") newVotes.down++
              newVotes.user_vote = vote
            } else {
              newVotes.user_vote = null
            }

            return { ...q, votes: newVotes }
          }
          return q
        }),
      )

      toast({
        title: "Başarılı",
        description: "Oyunuz kaydedildi.",
      })
    } catch (error) {
      console.error("Vote error:", error)
      toast({
        title: "Hata",
        description: "Oy verirken bir hata oluştu.",
        variant: "destructive",
      })
    }
  }

  const handleViewQuestion = (questionId: string) => {
    // Update view count
    setQuestions((prev) => prev.map((q) => (q._id === questionId ? { ...q, views: q.views + 1 } : q)))

    // In a real app, this would navigate to question detail page
    toast({
      title: "Soru Detayı",
      description: "Soru detay sayfası açılacak...",
    })
  }

  const getCategories = () => {
    const categories = [...new Set(questions.map((question) => question.category))]
    return categories
  }

  const getStats = () => {
    const totalQuestions = questions.length
    const solvedQuestions = questions.filter((q) => q.is_solved).length
    const unansweredQuestions = questions.filter((q) => q.answers_count === 0).length
    const totalViews = questions.reduce((sum, q) => sum + q.views, 0)

    return { totalQuestions, solvedQuestions, unansweredQuestions, totalViews }
  }

  if (loading) {
    return (
      <div className="space-y-6">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          {[1, 2, 3, 4].map((i) => (
            <Card key={i} className="animate-pulse">
              <CardContent className="p-4">
                <div className="h-4 bg-gray-200 rounded w-3/4 mb-2"></div>
                <div className="h-6 bg-gray-200 rounded w-1/2"></div>
              </CardContent>
            </Card>
          ))}
        </div>
        <div className="space-y-4">
          {[1, 2, 3, 4].map((i) => (
            <Card key={i} className="animate-pulse">
              <CardHeader>
                <div className="h-5 bg-gray-200 rounded w-3/4 mb-2"></div>
                <div className="h-4 bg-gray-200 rounded w-full"></div>
              </CardHeader>
              <CardContent>
                <div className="h-4 bg-gray-200 rounded w-1/2"></div>
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
                <p className="text-blue-100 text-sm">Toplam Soru</p>
                <p className="text-2xl font-bold">{stats.totalQuestions}</p>
              </div>
              <HelpCircle className="w-8 h-8 text-blue-200" />
            </div>
          </CardContent>
        </Card>

        <Card className="bg-gradient-to-r from-green-500 to-green-600 text-white">
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-green-100 text-sm">Çözülen</p>
                <p className="text-2xl font-bold">{stats.solvedQuestions}</p>
              </div>
              <CheckCircle className="w-8 h-8 text-green-200" />
            </div>
          </CardContent>
        </Card>

        <Card className="bg-gradient-to-r from-orange-500 to-orange-600 text-white">
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-orange-100 text-sm">Cevaplanmamış</p>
                <p className="text-2xl font-bold">{stats.unansweredQuestions}</p>
              </div>
              <MessageCircle className="w-8 h-8 text-orange-200" />
            </div>
          </CardContent>
        </Card>

        <Card className="bg-gradient-to-r from-purple-500 to-purple-600 text-white">
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-purple-100 text-sm">Toplam Görüntüleme</p>
                <p className="text-2xl font-bold">{stats.totalViews}</p>
              </div>
              <Users className="w-8 h-8 text-purple-200" />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Tabs */}
      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="all">Tümü ({questions.length})</TabsTrigger>
          <TabsTrigger value="solved">Çözülen ({stats.solvedQuestions})</TabsTrigger>
          <TabsTrigger value="unsolved">Çözülmeyen ({questions.length - stats.solvedQuestions})</TabsTrigger>
          <TabsTrigger value="unanswered">Cevaplanmamış ({stats.unansweredQuestions})</TabsTrigger>
        </TabsList>

        <TabsContent value="all" className="space-y-4">
          <QuestionFilters />
        </TabsContent>
        <TabsContent value="solved" className="space-y-4">
          <QuestionFilters />
        </TabsContent>
        <TabsContent value="unsolved" className="space-y-4">
          <QuestionFilters />
        </TabsContent>
        <TabsContent value="unanswered" className="space-y-4">
          <QuestionFilters />
        </TabsContent>
      </Tabs>

      {/* Question Filters Component */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle className="flex items-center space-x-2">
              <Filter className="w-5 h-5" />
              <span>Filtreler ve Sıralama</span>
            </CardTitle>
            <Button className="bg-blue-600 hover:bg-blue-700">
              <Plus className="w-4 h-4 mr-2" />
              Soru Sor
            </Button>
          </div>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
              <Input
                placeholder="Soru ara..."
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

            <Select value={sortBy} onValueChange={setSortBy}>
              <SelectTrigger>
                <SelectValue placeholder="Sıralama" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="recent">En Yeni</SelectItem>
                <SelectItem value="popular">En Popüler</SelectItem>
                <SelectItem value="views">En Çok Görüntülenen</SelectItem>
                <SelectItem value="answers">En Çok Cevaplanan</SelectItem>
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
          </div>
        </CardContent>
      </Card>

      {/* Questions List */}
      {filteredQuestions.length === 0 ? (
        <Card>
          <CardContent className="p-12 text-center">
            <MessageCircle className="w-16 h-16 text-gray-300 mx-auto mb-4" />
            <h3 className="text-lg font-semibold text-gray-600 mb-2">Soru bulunamadı</h3>
            <p className="text-gray-500 mb-4">
              {searchTerm || selectedCategory !== "all"
                ? "Arama kriterlerinize uygun soru bulunamadı. Filtreleri temizleyip tekrar deneyin."
                : "Henüz hiç soru sorulmamış."}
            </p>
            {(searchTerm || selectedCategory !== "all") && (
              <Button
                onClick={() => {
                  setSearchTerm("")
                  setSelectedCategory("all")
                }}
                variant="outline"
              >
                Filtreleri Temizle
              </Button>
            )}
          </CardContent>
        </Card>
      ) : (
        <div className="space-y-4">
          {filteredQuestions.map((question) => (
            <QuestionCard key={question._id} question={question} onVote={handleVote} onView={handleViewQuestion} />
          ))}
        </div>
      )}

      {/* Results Summary */}
      {filteredQuestions.length > 0 && (
        <div className="text-center text-sm text-gray-500">
          {filteredQuestions.length} soru gösteriliyor
          {filteredQuestions.length !== questions.length && ` (toplam ${questions.length} soru)`}
        </div>
      )}
    </div>
  )

  // Helper component for filters (to avoid repetition in tabs)
  function QuestionFilters() {
    return null // Filters are now in the main component above tabs
  }
}
