"use client"

import { useState, useEffect } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import {
  Users,
  BookOpen,
  Activity,
  UserCheck,
  Clock,
  Target,
  AlertTriangle,
  CheckCircle,
  BarChart3,
  Download,
} from "lucide-react"
import { apiMethods } from "@/lib/api"
import { useToast } from "@/hooks/use-toast"

export function AdminAnalytics() {
  const [analytics, setAnalytics] = useState<any>(null)
  const [loading, setLoading] = useState(true)
  const [timeRange, setTimeRange] = useState("7d")
  const { toast } = useToast()

  // Mock data for development
  const mockAnalytics = {
    overview: {
      total_users: 1247,
      active_users_today: 89,
      total_quizzes: 156,
      total_questions: 2340,
      total_quiz_attempts: 5678,
      average_completion_rate: 78.5,
      new_users_this_week: 23,
      popular_categories: [
        { name: "Frontend", count: 45 },
        { name: "Backend", count: 32 },
        { name: "Programlama", count: 28 },
      ],
    },
    user_analytics: {
      registration_trend: [
        { date: "2024-01-19", count: 5 },
        { date: "2024-01-20", count: 8 },
        { date: "2024-01-21", count: 3 },
        { date: "2024-01-22", count: 12 },
        { date: "2024-01-23", count: 7 },
        { date: "2024-01-24", count: 9 },
        { date: "2024-01-25", count: 15 },
      ],
      activity_levels: {
        very_active: 156, // 10+ quizzes
        active: 234, // 5-9 quizzes
        moderate: 445, // 1-4 quizzes
        inactive: 412, // 0 quizzes
      },
      top_performers: [
        { name: "Ahmet Yılmaz", quizzes_completed: 45, average_score: 92.3 },
        { name: "Fatma Demir", quizzes_completed: 38, average_score: 89.7 },
        { name: "Mehmet Kaya", quizzes_completed: 42, average_score: 87.1 },
      ],
    },
    quiz_analytics: {
      completion_rates: [
        { quiz_title: "JavaScript Temelleri", attempts: 245, completion_rate: 89.4 },
        { quiz_title: "React Hooks", attempts: 189, completion_rate: 76.2 },
        { quiz_title: "Node.js Express", attempts: 156, completion_rate: 68.5 },
      ],
      difficulty_performance: {
        easy: { avg_score: 85.2, completion_rate: 94.1 },
        medium: { avg_score: 72.8, completion_rate: 81.3 },
        hard: { avg_score: 58.9, completion_rate: 65.7 },
      },
      popular_quizzes: [
        { title: "JavaScript Temelleri", attempts: 245, rating: 4.8 },
        { title: "CSS Grid ve Flexbox", attempts: 312, rating: 4.6 },
        { title: "React Hooks Derinlemesine", attempts: 189, rating: 4.9 },
      ],
    },
    forum_analytics: {
      total_questions: 89,
      total_answers: 234,
      solved_questions: 67,
      active_contributors: 45,
      top_contributors: [
        { name: "Ali Şahin", questions: 12, answers: 34, reputation: 1800 },
        { name: "Zeynep Arslan", questions: 8, answers: 28, reputation: 1450 },
        { name: "Ayşe Özkan", questions: 15, answers: 19, reputation: 1250 },
      ],
    },
    system_health: {
      server_uptime: 99.8,
      average_response_time: 145, // ms
      error_rate: 0.2,
      database_size: 2.4, // GB
      active_sessions: 67,
      peak_concurrent_users: 123,
    },
  }

  useEffect(() => {
    fetchAnalytics()
  }, [timeRange])

  const fetchAnalytics = async () => {
    try {
      setLoading(true)
      // Try to fetch from API, fallback to mock data
      try {
        const response = await apiMethods.admin.getAnalytics()
        setAnalytics(response.data)
      } catch (apiError) {
        console.warn("API not available, using mock data")
        setAnalytics(mockAnalytics)
      }
    } catch (error) {
      console.error("Error fetching analytics:", error)
      toast({
        title: "Hata",
        description: "Analitik veriler yüklenirken bir hata oluştu.",
        variant: "destructive",
      })
      // Use mock data as fallback
      setAnalytics(mockAnalytics)
    } finally {
      setLoading(false)
    }
  }

  const formatNumber = (num: number) => {
    if (num >= 1000) {
      return (num / 1000).toFixed(1) + "K"
    }
    return num.toString()
  }

  const getActivityLevelColor = (level: string) => {
    switch (level) {
      case "very_active":
        return "bg-green-500"
      case "active":
        return "bg-blue-500"
      case "moderate":
        return "bg-yellow-500"
      case "inactive":
        return "bg-gray-400"
      default:
        return "bg-gray-400"
    }
  }

  const getActivityLevelLabel = (level: string) => {
    switch (level) {
      case "very_active":
        return "Çok Aktif"
      case "active":
        return "Aktif"
      case "moderate":
        return "Orta"
      case "inactive":
        return "Pasif"
      default:
        return level
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
          {[1, 2, 3, 4].map((i) => (
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

  if (!analytics) {
    return (
      <Card>
        <CardContent className="p-12 text-center">
          <BarChart3 className="w-16 h-16 text-gray-300 mx-auto mb-4" />
          <h3 className="text-lg font-semibold text-gray-600 mb-2">Analitik verisi bulunamadı</h3>
          <p className="text-gray-500">Admin analitik verileri yüklenemedi.</p>
        </CardContent>
      </Card>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Admin Analitikleri</h2>
          <p className="text-gray-600">Platform performansı ve kullanıcı istatistikleri</p>
        </div>
        <div className="flex items-center space-x-3">
          <Select value={timeRange} onValueChange={setTimeRange}>
            <SelectTrigger className="w-32">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="1d">Son 1 Gün</SelectItem>
              <SelectItem value="7d">Son 7 Gün</SelectItem>
              <SelectItem value="30d">Son 30 Gün</SelectItem>
              <SelectItem value="90d">Son 90 Gün</SelectItem>
            </SelectContent>
          </Select>
          <Button variant="outline">
            <Download className="w-4 h-4 mr-2" />
            Rapor İndir
          </Button>
        </div>
      </div>

      {/* Overview Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card className="bg-gradient-to-r from-blue-500 to-blue-600 text-white">
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-blue-100 text-sm">Toplam Kullanıcı</p>
                <p className="text-2xl font-bold">{formatNumber(analytics.overview.total_users)}</p>
                <p className="text-blue-200 text-xs">+{analytics.overview.new_users_this_week} bu hafta</p>
              </div>
              <Users className="w-8 h-8 text-blue-200" />
            </div>
          </CardContent>
        </Card>

        <Card className="bg-gradient-to-r from-green-500 to-green-600 text-white">
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-green-100 text-sm">Aktif Kullanıcı</p>
                <p className="text-2xl font-bold">{analytics.overview.active_users_today}</p>
                <p className="text-green-200 text-xs">Bugün online</p>
              </div>
              <UserCheck className="w-8 h-8 text-green-200" />
            </div>
          </CardContent>
        </Card>

        <Card className="bg-gradient-to-r from-purple-500 to-purple-600 text-white">
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-purple-100 text-sm">Toplam Quiz</p>
                <p className="text-2xl font-bold">{analytics.overview.total_quizzes}</p>
                <p className="text-purple-200 text-xs">{analytics.overview.total_questions} soru</p>
              </div>
              <BookOpen className="w-8 h-8 text-purple-200" />
            </div>
          </CardContent>
        </Card>

        <Card className="bg-gradient-to-r from-orange-500 to-orange-600 text-white">
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-orange-100 text-sm">Tamamlanma Oranı</p>
                <p className="text-2xl font-bold">{analytics.overview.average_completion_rate.toFixed(1)}%</p>
                <p className="text-orange-200 text-xs">Ortalama</p>
              </div>
              <Target className="w-8 h-8 text-orange-200" />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Detailed Analytics Tabs */}
      <Tabs defaultValue="users" className="space-y-4">
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="users">Kullanıcılar</TabsTrigger>
          <TabsTrigger value="quizzes">Quizler</TabsTrigger>
          <TabsTrigger value="forum">Forum</TabsTrigger>
          <TabsTrigger value="system">Sistem</TabsTrigger>
        </TabsList>

        <TabsContent value="users" className="space-y-6">
          {/* User Activity Levels */}
          <Card>
            <CardHeader>
              <CardTitle>Kullanıcı Aktivite Seviyeleri</CardTitle>
              <CardDescription>Kullanıcıların platform üzerindeki aktivite durumu</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                {Object.entries(analytics.user_analytics.activity_levels).map(([level, count]) => (
                  <div key={level} className="text-center p-4 bg-gray-50 rounded-lg">
                    <div
                      className={`w-12 h-12 ${getActivityLevelColor(level)} rounded-full mx-auto mb-2 flex items-center justify-center`}
                    >
                      <Activity className="w-6 h-6 text-white" />
                    </div>
                    <h4 className="font-semibold">{getActivityLevelLabel(level)}</h4>
                    <p className="text-2xl font-bold text-gray-900">{count as number}</p>
                    <p className="text-sm text-gray-500">kullanıcı</p>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* Top Performers */}
          <Card>
            <CardHeader>
              <CardTitle>En Başarılı Kullanıcılar</CardTitle>
              <CardDescription>Platform üzerinde en yüksek performans gösteren kullanıcılar</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {analytics.user_analytics.top_performers.map((user: any, index: number) => (
                  <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                    <div className="flex items-center space-x-3">
                      <div className="w-8 h-8 bg-blue-500 rounded-full flex items-center justify-center text-white font-bold text-sm">
                        {index + 1}
                      </div>
                      <div>
                        <h4 className="font-medium">{user.name}</h4>
                        <p className="text-sm text-gray-500">{user.quizzes_completed} quiz tamamlandı</p>
                      </div>
                    </div>
                    <Badge className="bg-green-100 text-green-800">{user.average_score.toFixed(1)}% ortalama</Badge>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* Registration Trend */}
          <Card>
            <CardHeader>
              <CardTitle>Kayıt Trendi</CardTitle>
              <CardDescription>Son 7 günde yeni kullanıcı kayıtları</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                {analytics.user_analytics.registration_trend.map((day: any, index: number) => (
                  <div key={index} className="flex items-center justify-between">
                    <span className="text-sm text-gray-600">
                      {new Date(day.date).toLocaleDateString("tr-TR", {
                        weekday: "long",
                        day: "numeric",
                        month: "short",
                      })}
                    </span>
                    <div className="flex items-center space-x-2">
                      <div className="w-24 bg-gray-200 rounded-full h-2">
                        <div
                          className="bg-blue-500 h-2 rounded-full"
                          style={{ width: `${(day.count / 15) * 100}%` }}
                        ></div>
                      </div>
                      <span className="text-sm font-medium w-8 text-right">{day.count}</span>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="quizzes" className="space-y-6">
          {/* Quiz Completion Rates */}
          <Card>
            <CardHeader>
              <CardTitle>Quiz Tamamlanma Oranları</CardTitle>
              <CardDescription>En popüler quizlerin tamamlanma oranları</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {analytics.quiz_analytics.completion_rates.map((quiz: any, index: number) => (
                  <div key={index} className="space-y-2">
                    <div className="flex items-center justify-between">
                      <h4 className="font-medium">{quiz.quiz_title}</h4>
                      <span className="text-sm text-gray-500">{quiz.attempts} deneme</span>
                    </div>
                    <div className="flex items-center space-x-2">
                      <div className="flex-1 bg-gray-200 rounded-full h-2">
                        <div
                          className="bg-green-500 h-2 rounded-full"
                          style={{ width: `${quiz.completion_rate}%` }}
                        ></div>
                      </div>
                      <span className="text-sm font-medium">{quiz.completion_rate.toFixed(1)}%</span>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* Difficulty Performance */}
          <Card>
            <CardHeader>
              <CardTitle>Zorluk Seviyesi Performansı</CardTitle>
              <CardDescription>Farklı zorluk seviyelerindeki genel performans</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                {Object.entries(analytics.quiz_analytics.difficulty_performance).map(([difficulty, stats]) => (
                  <div key={difficulty} className="p-4 border rounded-lg">
                    <h4 className="font-semibold capitalize mb-3">
                      {difficulty === "easy" ? "Kolay" : difficulty === "medium" ? "Orta" : "Zor"}
                    </h4>
                    <div className="space-y-2">
                      <div className="flex justify-between">
                        <span className="text-sm text-gray-600">Ortalama Skor:</span>
                        <span className="font-medium">{(stats as any).avg_score.toFixed(1)}%</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-sm text-gray-600">Tamamlanma:</span>
                        <span className="font-medium">{(stats as any).completion_rate.toFixed(1)}%</span>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* Popular Quizzes */}
          <Card>
            <CardHeader>
              <CardTitle>En Popüler Quizler</CardTitle>
              <CardDescription>En çok çözülen ve en yüksek puanlanan quizler</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {analytics.quiz_analytics.popular_quizzes.map((quiz: any, index: number) => (
                  <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                    <div>
                      <h4 className="font-medium">{quiz.title}</h4>
                      <p className="text-sm text-gray-500">{quiz.attempts} deneme</p>
                    </div>
                    <div className="flex items-center space-x-2">
                      <div className="flex items-center space-x-1">
                        {[...Array(5)].map((_, i) => (
                          <div
                            key={i}
                            className={`w-3 h-3 rounded-full ${
                              i < Math.floor(quiz.rating) ? "bg-yellow-400" : "bg-gray-200"
                            }`}
                          />
                        ))}
                      </div>
                      <span className="text-sm font-medium">{quiz.rating}</span>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="forum" className="space-y-6">
          {/* Forum Overview */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <Card>
              <CardContent className="p-4 text-center">
                <div className="text-2xl font-bold text-blue-600">{analytics.forum_analytics.total_questions}</div>
                <div className="text-sm text-gray-600">Toplam Soru</div>
              </CardContent>
            </Card>
            <Card>
              <CardContent className="p-4 text-center">
                <div className="text-2xl font-bold text-green-600">{analytics.forum_analytics.total_answers}</div>
                <div className="text-sm text-gray-600">Toplam Cevap</div>
              </CardContent>
            </Card>
            <Card>
              <CardContent className="p-4 text-center">
                <div className="text-2xl font-bold text-purple-600">{analytics.forum_analytics.solved_questions}</div>
                <div className="text-sm text-gray-600">Çözülen Soru</div>
              </CardContent>
            </Card>
            <Card>
              <CardContent className="p-4 text-center">
                <div className="text-2xl font-bold text-orange-600">
                  {analytics.forum_analytics.active_contributors}
                </div>
                <div className="text-sm text-gray-600">Aktif Katkıcı</div>
              </CardContent>
            </Card>
          </div>

          {/* Top Contributors */}
          <Card>
            <CardHeader>
              <CardTitle>En Aktif Katkıcılar</CardTitle>
              <CardDescription>Forum'da en çok katkı sağlayan kullanıcılar</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {analytics.forum_analytics.top_contributors.map((contributor: any, index: number) => (
                  <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                    <div className="flex items-center space-x-3">
                      <div className="w-8 h-8 bg-purple-500 rounded-full flex items-center justify-center text-white font-bold text-sm">
                        {index + 1}
                      </div>
                      <div>
                        <h4 className="font-medium">{contributor.name}</h4>
                        <p className="text-sm text-gray-500">
                          {contributor.questions} soru, {contributor.answers} cevap
                        </p>
                      </div>
                    </div>
                    <Badge className="bg-yellow-100 text-yellow-800">{contributor.reputation} puan</Badge>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="system" className="space-y-6">
          {/* System Health */}
          <Card>
            <CardHeader>
              <CardTitle>Sistem Sağlığı</CardTitle>
              <CardDescription>Platform performansı ve sistem metrikleri</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="space-y-4">
                  <div className="flex items-center justify-between p-3 bg-green-50 rounded-lg">
                    <div className="flex items-center space-x-2">
                      <CheckCircle className="w-5 h-5 text-green-600" />
                      <span className="font-medium">Sunucu Çalışma Süresi</span>
                    </div>
                    <span className="text-lg font-bold text-green-600">{analytics.system_health.server_uptime}%</span>
                  </div>

                  <div className="flex items-center justify-between p-3 bg-blue-50 rounded-lg">
                    <div className="flex items-center space-x-2">
                      <Clock className="w-5 h-5 text-blue-600" />
                      <span className="font-medium">Ortalama Yanıt Süresi</span>
                    </div>
                    <span className="text-lg font-bold text-blue-600">
                      {analytics.system_health.average_response_time}ms
                    </span>
                  </div>

                  <div className="flex items-center justify-between p-3 bg-red-50 rounded-lg">
                    <div className="flex items-center space-x-2">
                      <AlertTriangle className="w-5 h-5 text-red-600" />
                      <span className="font-medium">Hata Oranı</span>
                    </div>
                    <span className="text-lg font-bold text-red-600">{analytics.system_health.error_rate}%</span>
                  </div>
                </div>

                <div className="space-y-4">
                  <div className="flex items-center justify-between p-3 bg-purple-50 rounded-lg">
                    <div className="flex items-center space-x-2">
                      <Activity className="w-5 h-5 text-purple-600" />
                      <span className="font-medium">Aktif Oturumlar</span>
                    </div>
                    <span className="text-lg font-bold text-purple-600">{analytics.system_health.active_sessions}</span>
                  </div>

                  <div className="flex items-center justify-between p-3 bg-orange-50 rounded-lg">
                    <div className="flex items-center space-x-2">
                      <Users className="w-5 h-5 text-orange-600" />
                      <span className="font-medium">Pik Kullanıcı Sayısı</span>
                    </div>
                    <span className="text-lg font-bold text-orange-600">
                      {analytics.system_health.peak_concurrent_users}
                    </span>
                  </div>

                  <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                    <div className="flex items-center space-x-2">
                      <BarChart3 className="w-5 h-5 text-gray-600" />
                      <span className="font-medium">Veritabanı Boyutu</span>
                    </div>
                    <span className="text-lg font-bold text-gray-600">{analytics.system_health.database_size} GB</span>
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
