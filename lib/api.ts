import axios, { type AxiosInstance } from "axios"
import { config } from "./config"

// Create axios instance with base configuration
const createApiClient = (): AxiosInstance => {
  const client = axios.create({
    baseURL: config.api.base,
    timeout: 10000,
    headers: {
      "Content-Type": "application/json",
    },
  })

  // Request interceptor to add auth token
  client.interceptors.request.use(
    (config) => {
      const token = localStorage.getItem("token")
      if (token) {
        config.headers.Authorization = `Bearer ${token}`
      }
      return config
    },
    (error) => Promise.reject(error),
  )

  // Response interceptor for error handling
  client.interceptors.response.use(
    (response) => response,
    (error) => {
      if (error.response?.status === 401) {
        localStorage.removeItem("token")
        window.location.href = "/login"
      }
      return Promise.reject(error)
    },
  )

  return client
}

const apiClient = createApiClient()

// API Methods
export const apiMethods = {
  // Health check
  health: {
    check: () => apiClient.get("/health"),
  },

  // Authentication
  auth: {
    login: (email: string, password: string) => apiClient.post("/api/auth/login", { email, password }),
    register: (email: string, name: string, password: string) =>
      apiClient.post("/api/auth/register", { email, name, password }),
    me: () => apiClient.get("/api/auth/me"),
    logout: () => apiClient.post("/api/auth/logout"),
  },

  // Users
  users: {
    getProfile: () => apiClient.get("/api/users/profile"),
    updateProfile: (data: any) => apiClient.put("/api/users/profile", data),
    getStats: () => apiClient.get("/api/users/stats"),
  },

  // Quizzes
  quizzes: {
    list: () => apiClient.get("/api/quizzes"),
    get: (id: string) => apiClient.get(`/api/quizzes/${id}`),
    create: (data: any) => apiClient.post("/api/quizzes", data),
    update: (id: string, data: any) => apiClient.put(`/api/quizzes/${id}`, data),
    delete: (id: string) => apiClient.delete(`/api/quizzes/${id}`),
    attempt: (id: string, answers: string[]) => apiClient.post(`/api/quizzes/${id}/attempt`, { answers }),
    getAttempts: (id: string) => apiClient.get(`/api/quizzes/${id}/attempts`),
  },

  // Forum
  forum: {
    getQuestions: () => apiClient.get("/api/forum/questions"),
    getQuestion: (id: string) => apiClient.get(`/api/forum/questions/${id}`),
    createQuestion: (data: any) => apiClient.post("/api/forum/questions", data),
    createAnswer: (questionId: string, data: any) => apiClient.post(`/api/forum/questions/${questionId}/answers`, data),
    voteQuestion: (id: string, vote: "up" | "down") => apiClient.post(`/api/forum/questions/${id}/vote`, { vote }),
    voteAnswer: (id: string, vote: "up" | "down") => apiClient.post(`/api/forum/answers/${id}/vote`, { vote }),
  },

  // Admin
  admin: {
    getAnalytics: () => apiClient.get("/api/admin/analytics"),
    getUsers: () => apiClient.get("/api/admin/users"),
    getQuizzes: () => apiClient.get("/api/admin/quizzes"),
    deleteUser: (id: string) => apiClient.delete(`/api/admin/users/${id}`),
    updateUserRole: (id: string, role: string) => apiClient.put(`/api/admin/users/${id}/role`, { role }),
  },
}

export default apiClient
