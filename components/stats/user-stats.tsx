"use client"

import { useState, useEffect } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Progress } from "@/components/ui/progress"
import { Badge } from "@/components/ui/badge"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Trophy, Target, Clock, TrendingUp, Award, BookOpen, Star, Calendar, BarChart3 } from "lucide-react"
import { apiMethods } from "@/lib/api"
import { useToast } from "@/hooks/use-toast"

export function UserStats() {
  const [stats, setStats] = useState<any>(null)
  const [loading, setLoading] = useState(true)
  const { toast } = useToast()

  // Mock data for development
  const mockStats = {
    overview: {
      total_quizzes_attempted: 15,
      total_questions_answered: 287,
      average_score: 78.5,
      total_time_spent: 1245, // minutes
      current_streak: 7,
      best_streak: 12,
      level: 5,
      experience_points: 2340,
      next_level_xp: 2500,
    },
    quiz_performance: {
      by_category: [
        { category: "Frontend", attempted: 8, average_score: 85.2, best_score: 95 },
        { category: "Backend", attempted: 4, average_score: 72.5, best_score: 88 },
        { category: "Programlama", attempted: 3, average_score: 80.0, best_score: 92 },
      ],
      by_difficulty: [
        { difficulty: "easy", attempted: 6, average_score: 88.3, success_rate: 100 },
        { difficulty: "medium", attempted: 7, average_score: 75.1, success_rate: 85.7 },
        { difficulty: "hard", attempted: 2, average_score: 65.0, success_rate: 50 },
      ],
      recent_attempts: [
        {
          quiz_title: "React Hooks Derinlemesine",
          score: 92,
          total_questions: 20,
          completed_at: "2024-01-25T14:30:00Z",
          time_taken: 35,
        },
        {
          quiz_title: "JavaScript Temelleri",
          score: 85,
          total_questions: 15,
          completed_at: "2024-01-24T10:15:00Z",
          time_taken: 28,
        },
        {
          quiz_title: "CSS Grid ve Flexbox",
          score: 78,
          total_questions: 18,
          completed_at: "2024-01-23T16:45:00Z",
          time_taken: 42,
        },
      ],
    },
    achievements: [
      {
        id: "first_quiz",
        title: "İlk Adım",
        description: "İlk quiz'inizi tamamladınız",
        icon: "trophy",
        earned_at: "2024-01-15T10:00:00Z",
        rarity: "common",
      },
      {
        id: "perfect_score",
        title: "Mükemmel!",
        description: "Bir quiz'de 100 puan aldınız",
        icon: "star",
        earned_at: "2024-01-20T14:30:00Z",
        rarity: "rare",
      },
      {
        id: "streak_7",
        title: "7 Günlük Seri",
        description: "7 gün üst üste quiz çözdünüz",
        icon: "calendar",
        earned_at: "2024-01-25T09:00:00Z",
        rarity: "uncommon",
      },
    ],
    forum_activity: {
      questions_asked: 3,
      answers_given: 12,
      helpful_votes: 45,
      reputation: 1250,
    },
  }

  useEffect(() => {
    fetchStats()
  }, [])

  const fetchStats = async () => {
    try {
      setLoading(true)
      // Try to fetch from API, fallback to mock data
      try {
        const response = await apiMethods.users.getStats()
        setStats(response.data)
      } catch (apiError) {
        console.warn("API not available, using mock data")
        setStats(mockStats)
      }
    } catch (error) {
      console.error("Error fetching stats:", error)
      toast({
        title: "Hata",
        description: "İstatistikler yüklenirken bir hata oluştu.",
        variant: "destructive",
      })
      // Use mock data as fallback
      setStats(mockStats)
    } finally {
      setLoading(false)
    }
  }

  const formatTime = (minutes: number) => {
    const hours = Math.floor(minutes / 60)
    const remainingMinutes = minutes % 60
    if (hours > 0) {
      return `${hours}s ${remainingMinutes}dk`
    }
    return `${minutes} dakika`
  }

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString("tr-TR", {
      day: "numeric",
      month: "short",
      hour: "2-digit",
      minute: "2-digit",
    })
  }

  const getLevelProgress = () => {
    if (!stats?.overview) return 0
    const { experience_points, next_level_xp } = stats.overview
    const currentLevelXp = next_level_xp - 160 // Assuming 160 XP per level
    const progress = ((experience_points - currentLevelXp) / 160) * 100
    return Math.max(0, Math.min(100, progress))
  }

  const getDifficultyColor = (difficulty: string) => {
    switch (difficulty) {
      case "easy":
        return "text-green-600 bg-green-100"
      case "medium":
        return "text-yellow-600 bg-yellow-100"
      case "hard":
        return "text-red-600 bg-red-100"
      default:
        return "text-gray-600 bg-gray-100"
    }
  }

  const getAchievementIcon = (iconName: string) => {
    switch (iconName) {
      case "trophy":
        return <Trophy className="w-6 h-6" />
      case "star":
        return <Star className="w-6 h-6" />
      case "calendar":
        return <Calendar className="w-6 h-6" />
      default:
        return <Award className="w-6 h-6" />
    }
  }

  const getRarityColor = (rarity: string) => {
    switch (rarity) {
      case "common":
        return "border-gray-300 bg-gray-50"
      case "uncommon":
        return "border-green-300 bg-green-50"
      case "rare":
        return "border-blue-300 bg-blue-50"
      case "epic":
        return "border-purple-300 bg-purple-50"
      case "legendary":
        return "border-yellow-300 bg-yellow-50"
      default:
        return "border-gray-300 bg-gray-50"
    }
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
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {[1, 2].map((i) => (
            <Card key={i} className="animate-pulse">
              <CardHeader>
                <div className="h-5 bg-gray-200 rounded w-1/2"></div>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  <div className="h-4 bg-gray-200 rounded"></div>
                  <div className="h-4 bg-gray-200 rounded w-3/4"></div>
                  <div className="h-4 bg-gray-200 rounded w-1/2"></div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    )
  }

  if (!stats) {
    return (
      <Card>
        <CardContent className="p-12 text-center">
          <BarChart3 className="w-16 h-16 text-gray-300 mx-auto mb-4" />
          <h3 className="text-lg font-semibold text-gray-600 mb-2">İstatistik bulunamadı</h3>
          <p className="text-gray-500">Henüz hiç quiz çözmediniz.</p>
        </CardContent>
      </Card>
    )
  }

  return (
    <div className="space-y-6">
      {/* Overview Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card className="bg-gradient-to-r from-blue-500 to-blue-600 text-white">
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-blue-100 text-sm">Çözülen Quiz</p>
                <p className="text-2xl font-bold">{stats.overview.total_quizzes_attempted}</p>
              </div>
              <BookOpen className="w-8 h-8 text-blue-200" />
            </div>
          </CardContent>
        </Card>

        <Card className="bg-gradient-to-r from-green-500 to-green-600 text-white">
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-green-100 text-sm">Ortalama Skor</p>
                <p className="text-2xl font-bold">{stats.overview.average_score.toFixed(1)}%</p>
              </div>
              <Target className="w-8 h-8 text-green-200" />
            </div>
          </CardContent>
        </Card>

        <Card className="bg-gradient-to-r from-purple-500 to-purple-600 text-white">
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-purple-100 text-sm">Güncel Seri</p>
                <p className="text-2xl font-bold">{stats.overview.current_streak}</p>
              </div>
              <TrendingUp className="w-8 h-8 text-purple-200" />
            </div>
          </CardContent>
        </Card>

        <Card className="bg-gradient-to-r from-orange-500 to-orange-600 text-white">
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-orange-100 text-sm">Toplam Süre</p>
                <p className="text-2xl font-bold">{formatTime(stats.overview.total_time_spent)}</p>
              </div>
              <Clock className="w-8 h-8 text-orange-200" />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Level Progress */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <Award className="w-5 h-5" />
            <span>Seviye İlerlemesi</span>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center space-x-4">
            <div className="flex-shrink-0">
              <div className="w-16 h-16 bg-gradient-to-r from-blue-500 to-purple-600 rounded-full flex items-center justify-center text-white font-bold text-xl">
                {stats.overview.level}
              </div>
            </div>
            <div className="flex-1">
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm font-medium">Seviye {stats.overview.level}</span>
                <span className="text-sm text-gray-500">
                  {stats.overview.experience_points} / {stats.overview.next_level_xp} XP
                </span>
              </div>
              <Progress value={getLevelProgress()} className="h-3" />
              <p className="text-xs text-gray-500 mt-1">
                Bir sonraki seviyeye {stats.overview.next_level_xp - stats.overview.experience_points} XP kaldı
              </p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Detailed Stats Tabs */}
      <Tabs defaultValue="performance" className="space-y-4">
        <TabsList className="grid w-full grid-cols-3">
          <TabsTrigger value="performance">Performans</TabsTrigger>
          <TabsTrigger value="achievements">Başarımlar</TabsTrigger>
          <TabsTrigger value="activity">Forum Aktivitesi</TabsTrigger>
        </TabsList>

        <TabsContent value="performance" className="space-y-6">
          {/* Category Performance */}
          <Card>
            <CardHeader>
              <CardTitle>Kategoriye Göre Performans</CardTitle>
              <CardDescription>Her kategorideki başarı durumunuz</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {stats.quiz_performance.by_category.map((category: any, index: number) => (
                  <div key={index} className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                    <div className="flex-1">
                      <h4 className="font-medium">{category.category}</h4>
                      <p className="text-sm text-gray-500">{category.attempted} quiz çözüldü</p>
                    </div>
                    <div className="text-right">
                      <p className="font-semibold text-lg">{category.average_score.toFixed(1)}%</p>
                      <p className="text-sm text-gray-500">En iyi: {category.best_score}%</p>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* Difficulty Performance */}
          <Card>
            <CardHeader>
              <CardTitle>Zorluk Seviyesine Göre Performans</CardTitle>
              <CardDescription>Farklı zorluk seviyelerindeki başarınız</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                {stats.quiz_performance.by_difficulty.map((difficulty: any, index: number) => (
                  <div key={index} className={`p-4 rounded-lg border-2 ${getDifficultyColor(difficulty.difficulty)}`}>
                    <h4 className="font-semibold capitalize mb-2">
                      {difficulty.difficulty === "easy" ? "Kolay" : difficulty.difficulty === "medium" ? "Orta" : "Zor"}
                    </h4>
                    <div className="space-y-2">
                      <div className="flex justify-between">
                        <span className="text-sm">Çözülen:</span>
                        <span className="font-medium">{difficulty.attempted}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-sm">Ortalama:</span>
                        <span className="font-medium">{difficulty.average_score.toFixed(1)}%</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-sm">Başarı Oranı:</span>
                        <span className="font-medium">{difficulty.success_rate}%</span>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* Recent Attempts */}
          <Card>
            <CardHeader>
              <CardTitle>Son Quiz Denemeleri</CardTitle>
              <CardDescription>En son çözdüğünüz quizler</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {stats.quiz_performance.recent_attempts.map((attempt: any, index: number) => (
                  <div key={index} className="flex items-center justify-between p-3 border rounded-lg">
                    <div className="flex-1">
                      <h4 className="font-medium">{attempt.quiz_title}</h4>
                      <p className="text-sm text-gray-500">
                        {formatDate(attempt.completed_at)} • {formatTime(attempt.time_taken)}
                      </p>
                    </div>
                    <div className="text-right">
                      <Badge
                        className={`${
                          attempt.score >= 80
                            ? "bg-green-100 text-green-800"
                            : attempt.score >= 60
                              ? "bg-yellow-100 text-yellow-800"
                              : "bg-red-100 text-red-800"
                        }`}
                      >
                        {attempt.score}/{attempt.total_questions}
                      </Badge>
                      <p className="text-sm text-gray-500 mt-1">
                        {((attempt.score / attempt.total_questions) * 100).toFixed(0)}%
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="achievements" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Kazanılan Başarımlar</CardTitle>
              <CardDescription>Elde ettiğiniz başarımlar ve rozetler</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {stats.achievements.map((achievement: any) => (
                  <div key={achievement.id} className={`p-4 rounded-lg border-2 ${getRarityColor(achievement.rarity)}`}>
                    <div className="flex items-center space-x-3 mb-2">
                      <div className="text-yellow-600">{getAchievementIcon(achievement.icon)}</div>
                      <div className="flex-1">
                        <h4 className="font-semibold">{achievement.title}</h4>
                        <Badge variant="outline" className="text-xs capitalize">
                          {achievement.rarity}
                        </Badge>
                      </div>
                    </div>
                    <p className="text-sm text-gray-600 mb-2">{achievement.description}</p>
                    <p className="text-xs text-gray-500">{formatDate(achievement.earned_at)} tarihinde kazanıldı</p>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="activity" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Forum Aktivitesi</CardTitle>
              <CardDescription>Topluluk katılımınız ve itibarınız</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="space-y-4">
                  <div className="flex items-center justify-between p-3 bg-blue-50 rounded-lg">
                    <span className="font-medium">Sorduğunuz Sorular</span>
                    <span className="text-xl font-bold text-blue-600">{stats.forum_activity.questions_asked}</span>
                  </div>
                  <div className="flex items-center justify-between p-3 bg-green-50 rounded-lg">
                    <span className="font-medium">Verdiğiniz Cevaplar</span>
                    <span className="text-xl font-bold text-green-600">{stats.forum_activity.answers_given}</span>
                  </div>
                </div>
                <div className="space-y-4">
                  <div className="flex items-center justify-between p-3 bg-purple-50 rounded-lg">
                    <span className="font-medium">Aldığınız Beğeniler</span>
                    <span className="text-xl font-bold text-purple-600">{stats.forum_activity.helpful_votes}</span>
                  </div>
                  <div className="flex items-center justify-between p-3 bg-orange-50 rounded-lg">
                    <span className="font-medium">İtibar Puanı</span>
                    <span className="text-xl font-bold text-orange-600">{stats.forum_activity.reputation}</span>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}
