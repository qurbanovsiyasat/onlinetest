"use client"

import type React from "react"
import { useState, useEffect, createContext, useContext } from "react"
import { config, validateConfig } from "@/lib/config"
import { apiMethods } from "@/lib/api"
import { ApiStatus } from "@/components/api-status"
import { QuizList } from "@/components/quiz/quiz-list"
import { ForumList } from "@/components/forum/forum-list"
import { UserStats } from "@/components/stats/user-stats"
import { AdminAnalytics } from "@/components/admin/admin-analytics"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Badge } from "@/components/ui/badge"
import { useToast } from "@/hooks/use-toast"
import { Toaster } from "@/components/ui/toaster"
import { LogOut, UserIcon, Settings, Shield } from "lucide-react"

// Validate configuration on app start
try {
  validateConfig()
} catch (error) {
  console.error("Configuration validation failed:", error)
}

// Types
interface AuthContextType {
  user: any | null
  token: string | null
  loading: boolean
  login: (email: string, password: string) => Promise<{ success: boolean; error?: string }>
  register: (email: string, name: string, password: string) => Promise<{ success: boolean; error?: string }>
  logout: () => void
  isAuthenticated: boolean
  isAdmin: boolean
}

// Auth Context
const AuthContext = createContext<AuthContextType | undefined>(undefined)

const useAuth = () => {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error("useAuth must be used within an AuthProvider")
  }
  return context
}

// Auth Provider
const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<any | null>(null)
  const [token, setToken] = useState<string | null>(localStorage.getItem("token"))
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (token) {
      fetchCurrentUser()
    } else {
      setLoading(false)
    }
  }, [token])

  const fetchCurrentUser = async () => {
    try {
      const response = await apiMethods.auth.me()
      setUser(response.data)
    } catch (error) {
      console.error("Failed to fetch user:", error)
      logout()
    } finally {
      setLoading(false)
    }
  }

  const login = async (email: string, password: string) => {
    try {
      const response = await apiMethods.auth.login(email, password)
      const { access_token, user: userData } = response.data

      setToken(access_token)
      setUser(userData)
      localStorage.setItem("token", access_token)

      return { success: true }
    } catch (error: any) {
      return {
        success: false,
        error: error.response?.data?.detail || "Login failed",
      }
    }
  }

  const register = async (email: string, name: string, password: string) => {
    try {
      const response = await apiMethods.auth.register(email, name, password)
      return { success: true, user: response.data }
    } catch (error: any) {
      return {
        success: false,
        error: error.response?.data?.detail || "Registration failed",
      }
    }
  }

  const logout = () => {
    setUser(null)
    setToken(null)
    localStorage.removeItem("token")
  }

  const value: AuthContextType = {
    user,
    token,
    loading,
    login,
    register,
    logout,
    isAuthenticated: !!user,
    isAdmin: user?.role === "admin",
  }

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

// Login Form Component
const LoginForm: React.FC<{ onSwitchToRegister: () => void }> = ({ onSwitchToRegister }) => {
  const [email, setEmail] = useState("")
  const [password, setPassword] = useState("")
  const [loading, setLoading] = useState(false)
  const { login } = useAuth()
  const { toast } = useToast()

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)

    const result = await login(email, password)
    if (!result.success) {
      toast({
        title: "Giriş Hatası",
        description: result.error,
        variant: "destructive",
      })
    }
    setLoading(false)
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-indigo-50 to-blue-100 py-12 px-4 sm:px-6 lg:px-8">
      <Card className="w-full max-w-md">
        <CardHeader className="text-center">
          <CardTitle className="text-3xl font-bold text-gray-900">{config.appName}</CardTitle>
          <CardDescription className="mt-2">Giriş yapın veya hesap oluşturun</CardDescription>
          <div className="mt-2 p-2 bg-blue-50 rounded-lg">
            <p className="text-sm text-blue-700">
              <strong>Demo Hesap:</strong> admin@squiz.com / admin123
            </p>
          </div>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <Input
                type="email"
                placeholder="Email adresi"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                className="w-full"
              />
            </div>
            <div>
              <Input
                type="password"
                placeholder="Şifre"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                className="w-full"
              />
            </div>
            <Button type="submit" disabled={loading} className="w-full bg-indigo-600 hover:bg-indigo-700">
              {loading ? "Giriş yapılıyor..." : "Giriş Yap"}
            </Button>
          </form>
          <div className="mt-4 text-center">
            <Button
              type="button"
              variant="link"
              onClick={onSwitchToRegister}
              className="text-indigo-600 hover:text-indigo-500"
            >
              Hesabınız yok mu? Kayıt olun
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}

// Register Form Component
const RegisterForm: React.FC<{ onSwitchToLogin: () => void }> = ({ onSwitchToLogin }) => {
  const [email, setEmail] = useState("")
  const [name, setName] = useState("")
  const [password, setPassword] = useState("")
  const [loading, setLoading] = useState(false)
  const [success, setSuccess] = useState(false)
  const { register } = useAuth()
  const { toast } = useToast()

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)

    const result = await register(email, name, password)
    if (result.success) {
      setSuccess(true)
      toast({
        title: "Kayıt Başarılı",
        description: "Hesabınız oluşturuldu. Giriş sayfasına yönlendiriliyorsunuz...",
      })
      setTimeout(() => onSwitchToLogin(), 2000)
    } else {
      toast({
        title: "Kayıt Hatası",
        description: result.error,
        variant: "destructive",
      })
    }
    setLoading(false)
  }

  if (success) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-green-50 to-emerald-100">
        <Card className="w-full max-w-md">
          <CardContent className="p-6 text-center">
            <div className="text-green-600 mb-4">
              <div className="w-16 h-16 mx-auto bg-green-100 rounded-full flex items-center justify-center mb-4">✓</div>
              <h3 className="text-lg font-semibold">Kayıt Başarılı!</h3>
              <p className="text-sm mt-2">Giriş sayfasına yönlendiriliyorsunuz...</p>
            </div>
          </CardContent>
        </Card>
      </div>
    )
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-indigo-50 to-blue-100 py-12 px-4 sm:px-6 lg:px-8">
      <Card className="w-full max-w-md">
        <CardHeader className="text-center">
          <CardTitle className="text-3xl font-bold text-gray-900">{config.appName}</CardTitle>
          <CardDescription className="mt-2">Yeni hesap oluşturun</CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <Input
                type="text"
                placeholder="Ad Soyad"
                value={name}
                onChange={(e) => setName(e.target.value)}
                required
                className="w-full"
              />
            </div>
            <div>
              <Input
                type="email"
                placeholder="Email adresi"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                className="w-full"
              />
            </div>
            <div>
              <Input
                type="password"
                placeholder="Şifre (en az 6 karakter)"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                minLength={6}
                className="w-full"
              />
            </div>
            <Button type="submit" disabled={loading} className="w-full bg-indigo-600 hover:bg-indigo-700">
              {loading ? "Kayıt yapılıyor..." : "Kayıt Ol"}
            </Button>
          </form>
          <div className="mt-4 text-center">
            <Button
              type="button"
              variant="link"
              onClick={onSwitchToLogin}
              className="text-indigo-600 hover:text-indigo-500"
            >
              Zaten hesabınız var mı? Giriş yapın
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}

// Dashboard Component
const Dashboard: React.FC = () => {
  const { user, logout, isAdmin } = useAuth()
  const { toast } = useToast()

  const handleQuizAttempt = async (quizId: string) => {
    try {
      // Get quiz details first
      const quizResponse = await apiMethods.quizzes.get(quizId)
      const quiz = quizResponse.data

      // For demo purposes, generate random answers
      const answers = quiz.questions.map((q: any) => {
        if (q.question_type === "multiple_choice") {
          const correctOption = q.options.find((opt: any) => opt.is_correct)
          return correctOption ? correctOption.text : q.options[0]?.text || ""
        } else {
          return q.open_ended_answer?.expected_answers[0] || "Sample answer"
        }
      })

      // Submit quiz attempt
      const result = await apiMethods.quizzes.attempt(quizId, answers)

      toast({
        title: "Quiz Tamamlandı!",
        description: `Puanınız: ${result.data.score}/${result.data.total_questions} (${result.data.percentage.toFixed(1)}%)`,
        variant: result.data.passed ? "default" : "destructive",
      })
    } catch (error: any) {
      console.error("Quiz attempt failed:", error)
      toast({
        title: "Hata",
        description: "Quiz çözülürken bir hata oluştu.",
        variant: "destructive",
      })
    }
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-4">
            <div className="flex items-center space-x-4">
              <h1 className="text-2xl font-bold text-gray-900">{config.appName}</h1>
              {isAdmin && (
                <Badge className="bg-red-100 text-red-800">
                  <Shield className="w-3 h-3 mr-1" />
                  Admin
                </Badge>
              )}
            </div>

            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-2 text-gray-700">
                <UserIcon className="w-4 h-4" />
                <span className="hidden sm:inline">Hoş geldin, {user?.name}</span>
              </div>

              <Button variant="outline" size="sm" className="hidden sm:flex bg-transparent">
                <Settings className="w-4 h-4 mr-2" />
                Ayarlar
              </Button>

              <Button
                onClick={logout}
                variant="outline"
                size="sm"
                className="text-red-600 hover:text-red-700 hover:bg-red-50 bg-transparent"
              >
                <LogOut className="w-4 h-4 mr-2" />
                Çıkış
              </Button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto py-6 px-4 sm:px-6 lg:px-8">
        <Tabs defaultValue="quizzes" className="space-y-6">
          <TabsList className="grid w-full grid-cols-4 lg:w-auto lg:grid-cols-none lg:inline-flex">
            <TabsTrigger value="quizzes" className="flex items-center space-x-2">
              <span>Quizler</span>
            </TabsTrigger>
            <TabsTrigger value="forum" className="flex items-center space-x-2">
              <span>Forum</span>
            </TabsTrigger>
            <TabsTrigger value="stats" className="flex items-center space-x-2">
              <span>İstatistikler</span>
            </TabsTrigger>
            {isAdmin && (
              <TabsTrigger value="admin" className="flex items-center space-x-2">
                <span>Admin</span>
              </TabsTrigger>
            )}
          </TabsList>

          <TabsContent value="quizzes" className="space-y-6">
            <QuizList onQuizAttempt={handleQuizAttempt} />
          </TabsContent>

          <TabsContent value="forum" className="space-y-6">
            <ForumList />
          </TabsContent>

          <TabsContent value="stats" className="space-y-6">
            <UserStats />
          </TabsContent>

          {isAdmin && (
            <TabsContent value="admin" className="space-y-6">
              <AdminAnalytics />
            </TabsContent>
          )}
        </Tabs>
      </main>

      {/* API Status (Development only) */}
      <ApiStatus />
    </div>
  )
}

// Main App Component
const App: React.FC = () => {
  const [showRegister, setShowRegister] = useState(false)

  return (
    <AuthProvider>
      <div className="App">
        <AuthenticatedApp showRegister={showRegister} setShowRegister={setShowRegister} />
        <Toaster />
      </div>
    </AuthProvider>
  )
}

// Authenticated App Wrapper
const AuthenticatedApp: React.FC<{
  showRegister: boolean
  setShowRegister: (show: boolean) => void
}> = ({ showRegister, setShowRegister }) => {
  const { isAuthenticated, loading } = useAuth()

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Yükleniyor...</p>
        </div>
      </div>
    )
  }

  if (!isAuthenticated) {
    return showRegister ? (
      <RegisterForm onSwitchToLogin={() => setShowRegister(false)} />
    ) : (
      <LoginForm onSwitchToRegister={() => setShowRegister(true)} />
    )
  }

  return <Dashboard />
}

export default App
