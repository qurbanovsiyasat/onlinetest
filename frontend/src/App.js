"use client"

import { useState, useEffect, createContext, useContext } from "react"
import axios from "axios"
import "./App.css"

// API Configuration
const API_BASE_URL = process.env.REACT_APP_BACKEND_URL || "http://localhost:8001"
const api = axios.create({
  baseURL: API_BASE_URL,
})

// Auth Context
const AuthContext = createContext()

const useAuth = () => {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error("useAuth must be used within an AuthProvider")
  }
  return context
}

// Auth Provider
const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null)
  const [token, setToken] = useState(localStorage.getItem("token"))
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (token) {
      api.defaults.headers.common["Authorization"] = `Bearer ${token}`
      fetchCurrentUser()
    } else {
      setLoading(false)
    }
  }, [token])

  const fetchCurrentUser = async () => {
    try {
      const response = await api.get("/api/auth/me")
      setUser(response.data)
    } catch (error) {
      console.error("Failed to fetch user:", error)
      logout()
    } finally {
      setLoading(false)
    }
  }

  const login = async (email, password) => {
    try {
      const response = await api.post("/api/auth/login", { email, password })
      const { access_token, user: userData } = response.data

      setToken(access_token)
      setUser(userData)
      localStorage.setItem("token", access_token)
      api.defaults.headers.common["Authorization"] = `Bearer ${access_token}`

      return { success: true }
    } catch (error) {
      return {
        success: false,
        error: error.response?.data?.detail || "Login failed",
      }
    }
  }

  const register = async (email, name, password) => {
    try {
      const response = await api.post("/api/auth/register", { email, name, password })
      return { success: true, user: response.data }
    } catch (error) {
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
    delete api.defaults.headers.common["Authorization"]
  }

  const value = {
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

// Components
const LoginForm = ({ onSwitchToRegister }) => {
  const [email, setEmail] = useState("")
  const [password, setPassword] = useState("")
  const [error, setError] = useState("")
  const [loading, setLoading] = useState(false)
  const { login } = useAuth()

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    setError("")

    const result = await login(email, password)
    if (!result.success) {
      setError(result.error)
    }
    setLoading(false)
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8">
        <div>
          <h2 className="mt-6 text-center text-3xl font-extrabold text-gray-900">Squiz'e Giriş Yapın</h2>
          <p className="mt-2 text-center text-sm text-gray-600">Demo hesap: admin@squiz.com / admin123</p>
        </div>
        <form className="mt-8 space-y-6" onSubmit={handleSubmit}>
          {error && <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">{error}</div>}
          <div className="rounded-md shadow-sm -space-y-px">
            <div>
              <input
                type="email"
                required
                className="appearance-none rounded-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-t-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 focus:z-10 sm:text-sm"
                placeholder="Email adresi"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
              />
            </div>
            <div>
              <input
                type="password"
                required
                className="appearance-none rounded-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-b-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 focus:z-10 sm:text-sm"
                placeholder="Şifre"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
              />
            </div>
          </div>

          <div>
            <button
              type="submit"
              disabled={loading}
              className="group relative w-full flex justify-center py-2 px-4 border border-transparent text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50"
            >
              {loading ? "Giriş yapılıyor..." : "Giriş Yap"}
            </button>
          </div>

          <div className="text-center">
            <button type="button" onClick={onSwitchToRegister} className="text-indigo-600 hover:text-indigo-500">
              Hesabınız yok mu? Kayıt olun
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}

const RegisterForm = ({ onSwitchToLogin }) => {
  const [email, setEmail] = useState("")
  const [name, setName] = useState("")
  const [password, setPassword] = useState("")
  const [error, setError] = useState("")
  const [loading, setLoading] = useState(false)
  const [success, setSuccess] = useState(false)
  const { register } = useAuth()

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    setError("")

    const result = await register(email, name, password)
    if (result.success) {
      setSuccess(true)
      setTimeout(() => onSwitchToLogin(), 2000)
    } else {
      setError(result.error)
    }
    setLoading(false)
  }

  if (success) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="max-w-md w-full text-center">
          <div className="bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded">
            Kayıt başarılı! Giriş sayfasına yönlendiriliyorsunuz...
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8">
        <div>
          <h2 className="mt-6 text-center text-3xl font-extrabold text-gray-900">Squiz'e Kayıt Olun</h2>
        </div>
        <form className="mt-8 space-y-6" onSubmit={handleSubmit}>
          {error && <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">{error}</div>}
          <div className="rounded-md shadow-sm -space-y-px">
            <div>
              <input
                type="text"
                required
                className="appearance-none rounded-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-t-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 focus:z-10 sm:text-sm"
                placeholder="Ad Soyad"
                value={name}
                onChange={(e) => setName(e.target.value)}
              />
            </div>
            <div>
              <input
                type="email"
                required
                className="appearance-none rounded-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 focus:z-10 sm:text-sm"
                placeholder="Email adresi"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
              />
            </div>
            <div>
              <input
                type="password"
                required
                minLength={6}
                className="appearance-none rounded-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-b-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 focus:z-10 sm:text-sm"
                placeholder="Şifre (en az 6 karakter)"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
              />
            </div>
          </div>

          <div>
            <button
              type="submit"
              disabled={loading}
              className="group relative w-full flex justify-center py-2 px-4 border border-transparent text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50"
            >
              {loading ? "Kayıt yapılıyor..." : "Kayıt Ol"}
            </button>
          </div>

          <div className="text-center">
            <button type="button" onClick={onSwitchToLogin} className="text-indigo-600 hover:text-indigo-500">
              Zaten hesabınız var mı? Giriş yapın
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}

const Dashboard = () => {
  const { user, logout, isAdmin } = useAuth()
  const [quizzes, setQuizzes] = useState([])
  const [questions, setQuestions] = useState([])
  const [loading, setLoading] = useState(true)
  const [activeTab, setActiveTab] = useState("quizzes")
  const [userStats, setUserStats] = useState(null)

  useEffect(() => {
    fetchData()
  }, [])

  const fetchData = async () => {
    try {
      const [quizzesRes, questionsRes, statsRes] = await Promise.all([
        api.get("/api/quizzes"),
        api.get("/api/questions"),
        api.get("/api/user/stats"),
      ])

      setQuizzes(quizzesRes.data)
      setQuestions(questionsRes.data.questions)
      setUserStats(statsRes.data)
    } catch (error) {
      console.error("Failed to fetch data:", error)
    } finally {
      setLoading(false)
    }
  }

  const handleQuizAttempt = async (quizId) => {
    try {
      // For demo, we'll submit random answers
      const quiz = await api.get(`/api/quiz/${quizId}`)
      const answers = quiz.data.questions.map((q) => {
        if (q.question_type === "multiple_choice") {
          const correctOption = q.options.find((opt) => opt.is_correct)
          return correctOption ? correctOption.text : q.options[0]?.text || ""
        } else {
          return q.open_ended_answer?.expected_answers[0] || "Sample answer"
        }
      })

      const result = await api.post(`/api/quiz/${quizId}/attempt`, { answers })
      alert(
        `Quiz tamamlandı! Puanınız: ${result.data.score}/${result.data.total_questions} (${result.data.percentage.toFixed(1)}%)`,
      )
      fetchData() // Refresh data
    } catch (error) {
      console.error("Quiz attempt failed:", error)
      alert("Quiz çözülürken bir hata oluştu.")
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-xl">Yükleniyor...</div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-6">
            <div className="flex items-center">
              <h1 className="text-3xl font-bold text-gray-900">Squiz Platform</h1>
              {isAdmin && (
                <span className="ml-3 px-2 py-1 text-xs font-semibold text-white bg-red-600 rounded">Admin</span>
              )}
            </div>
            <div className="flex items-center space-x-4">
              <span className="text-gray-700">Hoş geldin, {user.name}</span>
              <button
                onClick={logout}
                className="bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded-md text-sm font-medium"
              >
                Çıkış Yap
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Navigation Tabs */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="border-b border-gray-200">
          <nav className="-mb-px flex space-x-8">
            <button
              onClick={() => setActiveTab("quizzes")}
              className={`py-2 px-1 border-b-2 font-medium text-sm ${
                activeTab === "quizzes"
                  ? "border-indigo-500 text-indigo-600"
                  : "border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300"
              }`}
            >
              Quizler
            </button>
            <button
              onClick={() => setActiveTab("forum")}
              className={`py-2 px-1 border-b-2 font-medium text-sm ${
                activeTab === "forum"
                  ? "border-indigo-500 text-indigo-600"
                  : "border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300"
              }`}
            >
              Q&A Forum
            </button>
            <button
              onClick={() => setActiveTab("stats")}
              className={`py-2 px-1 border-b-2 font-medium text-sm ${
                activeTab === "stats"
                  ? "border-indigo-500 text-indigo-600"
                  : "border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300"
              }`}
            >
              İstatistikler
            </button>
            {isAdmin && (
              <button
                onClick={() => setActiveTab("admin")}
                className={`py-2 px-1 border-b-2 font-medium text-sm ${
                  activeTab === "admin"
                    ? "border-indigo-500 text-indigo-600"
                    : "border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300"
                }`}
              >
                Admin Panel
              </button>
            )}
          </nav>
        </div>
      </div>

      {/* Content */}
      <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        {activeTab === "quizzes" && (
          <div className="px-4 py-6 sm:px-0">
            <h2 className="text-2xl font-bold text-gray-900 mb-6">Mevcut Quizler</h2>
            {quizzes.length === 0 ? (
              <div className="text-center py-12">
                <p className="text-gray-500">Henüz quiz bulunmuyor.</p>
              </div>
            ) : (
              <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
                {quizzes.map((quiz) => (
                  <div key={quiz.id} className="bg-white overflow-hidden shadow rounded-lg">
                    <div className="p-6">
                      <h3 className="text-lg font-medium text-gray-900 mb-2">{quiz.title}</h3>
                      <p className="text-sm text-gray-600 mb-4">{quiz.description}</p>
                      <div className="flex justify-between items-center text-sm text-gray-500 mb-4">
                        <span>
                          {quiz.subject} • {quiz.subcategory}
                        </span>
                        <span>{quiz.total_questions} soru</span>
                      </div>
                      <div className="flex justify-between items-center">
                        <div className="text-sm text-gray-500">
                          <div>Deneme: {quiz.total_attempts}</div>
                          <div>Ortalama: {quiz.average_score.toFixed(1)}%</div>
                        </div>
                        <button
                          onClick={() => handleQuizAttempt(quiz.id)}
                          className="bg-indigo-600 hover:bg-indigo-700 text-white px-4 py-2 rounded-md text-sm font-medium"
                        >
                          Quiz'i Çöz
                        </button>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {activeTab === "forum" && (
          <div className="px-4 py-6 sm:px-0">
            <h2 className="text-2xl font-bold text-gray-900 mb-6">Q&A Forum</h2>
            {questions.length === 0 ? (
              <div className="text-center py-12">
                <p className="text-gray-500">Henüz soru bulunmuyor.</p>
              </div>
            ) : (
              <div className="space-y-6">
                {questions.map((question) => (
                  <div key={question.id} className="bg-white shadow rounded-lg p-6">
                    <div className="flex justify-between items-start">
                      <div className="flex-1">
                        <h3 className="text-lg font-medium text-gray-900 mb-2">{question.title}</h3>
                        <p className="text-gray-600 mb-4">{question.content}</p>
                        <div className="flex items-center space-x-4 text-sm text-gray-500">
                          <span>👤 {question.user_name}</span>
                          <span>📅 {new Date(question.created_at).toLocaleDateString("tr-TR")}</span>
                          <span>💬 {question.answer_count} cevap</span>
                          <span>
                            👍 {question.upvotes} 👎 {question.downvotes}
                          </span>
                        </div>
                      </div>
                      <div className="flex items-center space-x-2">
                        {question.has_accepted_answer && (
                          <span className="px-2 py-1 text-xs font-semibold text-green-800 bg-green-100 rounded">
                            Cevaplanmış
                          </span>
                        )}
                        {question.is_pinned && (
                          <span className="px-2 py-1 text-xs font-semibold text-blue-800 bg-blue-100 rounded">
                            Sabitlenmiş
                          </span>
                        )}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {activeTab === "stats" && userStats && (
          <div className="px-4 py-6 sm:px-0">
            <h2 className="text-2xl font-bold text-gray-900 mb-6">İstatistiklerim</h2>
            <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-4">
              <div className="bg-white overflow-hidden shadow rounded-lg">
                <div className="p-5">
                  <div className="flex items-center">
                    <div className="flex-shrink-0">
                      <div className="text-2xl">📝</div>
                    </div>
                    <div className="ml-5 w-0 flex-1">
                      <dl>
                        <dt className="text-sm font-medium text-gray-500 truncate">Toplam Quiz</dt>
                        <dd className="text-lg font-medium text-gray-900">{userStats.total_quizzes_taken}</dd>
                      </dl>
                    </div>
                  </div>
                </div>
              </div>

              <div className="bg-white overflow-hidden shadow rounded-lg">
                <div className="p-5">
                  <div className="flex items-center">
                    <div className="flex-shrink-0">
                      <div className="text-2xl">❓</div>
                    </div>
                    <div className="ml-5 w-0 flex-1">
                      <dl>
                        <dt className="text-sm font-medium text-gray-500 truncate">Toplam Soru</dt>
                        <dd className="text-lg font-medium text-gray-900">{userStats.total_questions_answered}</dd>
                      </dl>
                    </div>
                  </div>
                </div>
              </div>

              <div className="bg-white overflow-hidden shadow rounded-lg">
                <div className="p-5">
                  <div className="flex items-center">
                    <div className="flex-shrink-0">
                      <div className="text-2xl">📊</div>
                    </div>
                    <div className="ml-5 w-0 flex-1">
                      <dl>
                        <dt className="text-sm font-medium text-gray-500 truncate">Ortalama Puan</dt>
                        <dd className="text-lg font-medium text-gray-900">{userStats.average_score}%</dd>
                      </dl>
                    </div>
                  </div>
                </div>
              </div>

              <div className="bg-white overflow-hidden shadow rounded-lg">
                <div className="p-5">
                  <div className="flex items-center">
                    <div className="flex-shrink-0">
                      <div className="text-2xl">🏆</div>
                    </div>
                    <div className="ml-5 w-0 flex-1">
                      <dl>
                        <dt className="text-sm font-medium text-gray-500 truncate">En Yüksek Puan</dt>
                        <dd className="text-lg font-medium text-gray-900">{userStats.best_score}%</dd>
                      </dl>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* Recent Attempts */}
            {userStats.recent_attempts.length > 0 && (
              <div className="mt-8">
                <h3 className="text-lg font-medium text-gray-900 mb-4">Son Denemeler</h3>
                <div className="bg-white shadow overflow-hidden sm:rounded-md">
                  <ul className="divide-y divide-gray-200">
                    {userStats.recent_attempts.map((attempt, index) => (
                      <li key={index} className="px-6 py-4">
                        <div className="flex items-center justify-between">
                          <div className="flex items-center">
                            <div className="flex-shrink-0">
                              <div className="text-lg">{attempt.percentage >= 60 ? "✅" : "❌"}</div>
                            </div>
                            <div className="ml-4">
                              <div className="text-sm font-medium text-gray-900">{attempt.quiz_title}</div>
                              <div className="text-sm text-gray-500">
                                {new Date(attempt.attempted_at).toLocaleDateString("tr-TR")}
                              </div>
                            </div>
                          </div>
                          <div className="text-sm font-medium text-gray-900">
                            {attempt.score} puan ({attempt.percentage.toFixed(1)}%)
                          </div>
                        </div>
                      </li>
                    ))}
                  </ul>
                </div>
              </div>
            )}
          </div>
        )}

        {activeTab === "admin" && isAdmin && <AdminPanel />}
      </main>
    </div>
  )
}

const AdminPanel = () => {
  const [users, setUsers] = useState([])
  const [quizzes, setQuizzes] = useState([])
  const [analytics, setAnalytics] = useState(null)
  const [loading, setLoading] = useState(true)
  const [activeAdminTab, setActiveAdminTab] = useState("analytics")

  useEffect(() => {
    fetchAdminData()
  }, [])

  const fetchAdminData = async () => {
    try {
      const [usersRes, quizzesRes, analyticsRes] = await Promise.all([
        api.get("/api/admin/users"),
        api.get("/api/admin/quizzes"),
        api.get("/api/admin/analytics"),
      ])

      setUsers(usersRes.data)
      setQuizzes(quizzesRes.data)
      setAnalytics(analyticsRes.data)
    } catch (error) {
      console.error("Failed to fetch admin data:", error)
    } finally {
      setLoading(false)
    }
  }

  const publishQuiz = async (quizId) => {
    try {
      await api.post(`/api/admin/quiz/${quizId}/publish`)
      alert("Quiz başarıyla yayınlandı!")
      fetchAdminData()
    } catch (error) {
      console.error("Failed to publish quiz:", error)
      alert("Quiz yayınlanırken bir hata oluştu.")
    }
  }

  if (loading) {
    return <div className="text-center py-12">Yükleniyor...</div>
  }

  return (
    <div className="px-4 py-6 sm:px-0">
      <h2 className="text-2xl font-bold text-gray-900 mb-6">Admin Panel</h2>

      {/* Admin Navigation */}
      <div className="border-b border-gray-200 mb-6">
        <nav className="-mb-px flex space-x-8">
          <button
            onClick={() => setActiveAdminTab("analytics")}
            className={`py-2 px-1 border-b-2 font-medium text-sm ${
              activeAdminTab === "analytics"
                ? "border-indigo-500 text-indigo-600"
                : "border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300"
            }`}
          >
            Analitik
          </button>
          <button
            onClick={() => setActiveAdminTab("users")}
            className={`py-2 px-1 border-b-2 font-medium text-sm ${
              activeAdminTab === "users"
                ? "border-indigo-500 text-indigo-600"
                : "border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300"
            }`}
          >
            Kullanıcılar
          </button>
          <button
            onClick={() => setActiveAdminTab("quizzes")}
            className={`py-2 px-1 border-b-2 font-medium text-sm ${
              activeAdminTab === "quizzes"
                ? "border-indigo-500 text-indigo-600"
                : "border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300"
            }`}
          >
            Quiz Yönetimi
          </button>
        </nav>
      </div>

      {/* Analytics Tab */}
      {activeAdminTab === "analytics" && analytics && (
        <div>
          <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-4 mb-8">
            <div className="bg-white overflow-hidden shadow rounded-lg">
              <div className="p-5">
                <div className="flex items-center">
                  <div className="flex-shrink-0">
                    <div className="text-2xl">👥</div>
                  </div>
                  <div className="ml-5 w-0 flex-1">
                    <dl>
                      <dt className="text-sm font-medium text-gray-500 truncate">Toplam Kullanıcı</dt>
                      <dd className="text-lg font-medium text-gray-900">{analytics.total_users}</dd>
                    </dl>
                  </div>
                </div>
              </div>
            </div>

            <div className="bg-white overflow-hidden shadow rounded-lg">
              <div className="p-5">
                <div className="flex items-center">
                  <div className="flex-shrink-0">
                    <div className="text-2xl">📝</div>
                  </div>
                  <div className="ml-5 w-0 flex-1">
                    <dl>
                      <dt className="text-sm font-medium text-gray-500 truncate">Toplam Quiz</dt>
                      <dd className="text-lg font-medium text-gray-900">{analytics.total_quizzes}</dd>
                    </dl>
                  </div>
                </div>
              </div>
            </div>

            <div className="bg-white overflow-hidden shadow rounded-lg">
              <div className="p-5">
                <div className="flex items-center">
                  <div className="flex-shrink-0">
                    <div className="text-2xl">🎯</div>
                  </div>
                  <div className="ml-5 w-0 flex-1">
                    <dl>
                      <dt className="text-sm font-medium text-gray-500 truncate">Toplam Deneme</dt>
                      <dd className="text-lg font-medium text-gray-900">{analytics.total_attempts}</dd>
                    </dl>
                  </div>
                </div>
              </div>
            </div>

            <div className="bg-white overflow-hidden shadow rounded-lg">
              <div className="p-5">
                <div className="flex items-center">
                  <div className="flex-shrink-0">
                    <div className="text-2xl">📊</div>
                  </div>
                  <div className="ml-5 w-0 flex-1">
                    <dl>
                      <dt className="text-sm font-medium text-gray-500 truncate">Ortalama Puan</dt>
                      <dd className="text-lg font-medium text-gray-900">{analytics.average_score}%</dd>
                    </dl>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div className="bg-white shadow rounded-lg p-6">
            <h3 className="text-lg font-medium text-gray-900 mb-4">Platform Özeti</h3>
            <div className="space-y-3">
              <div className="flex justify-between">
                <span className="text-gray-600">Aktif Kullanıcı (Bu Ay):</span>
                <span className="font-medium">{analytics.active_users_month}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">En Popüler Quiz:</span>
                <span className="font-medium">{analytics.most_popular_quiz}</span>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Users Tab */}
      {activeAdminTab === "users" && (
        <div>
          <h3 className="text-lg font-medium text-gray-900 mb-4">Kullanıcı Listesi</h3>
          <div className="bg-white shadow overflow-hidden sm:rounded-md">
            <ul className="divide-y divide-gray-200">
              {users.map((user) => (
                <li key={user.id} className="px-6 py-4">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center">
                      <div className="flex-shrink-0">
                        <div className="text-lg">{user.role === "admin" ? "👑" : "👤"}</div>
                      </div>
                      <div className="ml-4">
                        <div className="text-sm font-medium text-gray-900">{user.name}</div>
                        <div className="text-sm text-gray-500">{user.email}</div>
                      </div>
                    </div>
                    <div className="flex items-center space-x-2">
                      <span
                        className={`px-2 py-1 text-xs font-semibold rounded ${
                          user.role === "admin" ? "text-red-800 bg-red-100" : "text-blue-800 bg-blue-100"
                        }`}
                      >
                        {user.role}
                      </span>
                      <span
                        className={`px-2 py-1 text-xs font-semibold rounded ${
                          user.is_active ? "text-green-800 bg-green-100" : "text-red-800 bg-red-100"
                        }`}
                      >
                        {user.is_active ? "Aktif" : "Pasif"}
                      </span>
                    </div>
                  </div>
                </li>
              ))}
            </ul>
          </div>
        </div>
      )}

      {/* Quizzes Tab */}
      {activeAdminTab === "quizzes" && (
        <div>
          <h3 className="text-lg font-medium text-gray-900 mb-4">Quiz Yönetimi</h3>
          <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
            {quizzes.map((quiz) => (
              <div key={quiz.id} className="bg-white overflow-hidden shadow rounded-lg">
                <div className="p-6">
                  <h4 className="text-lg font-medium text-gray-900 mb-2">{quiz.title}</h4>
                  <p className="text-sm text-gray-600 mb-4">{quiz.description}</p>
                  <div className="flex justify-between items-center text-sm text-gray-500 mb-4">
                    <span>
                      {quiz.subject} • {quiz.subcategory}
                    </span>
                    <span>{quiz.total_questions} soru</span>
                  </div>
                  <div className="flex justify-between items-center">
                    <div className="flex items-center space-x-2">
                      <span
                        className={`px-2 py-1 text-xs font-semibold rounded ${
                          quiz.is_draft ? "text-yellow-800 bg-yellow-100" : "text-green-800 bg-green-100"
                        }`}
                      >
                        {quiz.is_draft ? "Taslak" : "Yayında"}
                      </span>
                    </div>
                    {quiz.is_draft && (
                      <button
                        onClick={() => publishQuiz(quiz.id)}
                        className="bg-green-600 hover:bg-green-700 text-white px-3 py-1 rounded text-sm"
                      >
                        Yayınla
                      </button>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}

// Main App Component
const App = () => {
  const [showRegister, setShowRegister] = useState(false)

  return (
    <AuthProvider>
      <div className="App">
        <AuthenticatedApp showRegister={showRegister} setShowRegister={setShowRegister} />
      </div>
    </AuthProvider>
  )
}

const AuthenticatedApp = ({ showRegister, setShowRegister }) => {
  const { isAuthenticated, loading } = useAuth()

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-xl">Yükleniyor...</div>
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
