"use client"

import { useState, useEffect, useCallback } from "react"
import { apiMethods } from "@/lib/api"
import type { AxiosResponse } from "axios"

// Generic API hook
export function useApi<T>(apiCall: () => Promise<AxiosResponse<T>>, dependencies: any[] = []) {
  const [data, setData] = useState<T | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const fetchData = useCallback(async () => {
    try {
      setLoading(true)
      setError(null)
      const response = await apiCall()
      setData(response.data)
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || "An error occurred")
    } finally {
      setLoading(false)
    }
  }, dependencies)

  useEffect(() => {
    fetchData()
  }, [fetchData])

  return { data, loading, error, refetch: fetchData }
}

// Specific hooks for different API endpoints
export function useQuizzes(params?: { subject?: string; category?: string; limit?: number; offset?: number }) {
  return useApi(() => apiMethods.quizzes.list(params), [params])
}

export function useQuiz(id: string) {
  return useApi(() => apiMethods.quizzes.get(id), [id])
}

export function useQuestions(params?: {
  limit?: number
  offset?: number
  subject?: string
  subcategory?: string
  status?: string
}) {
  return useApi(() => apiMethods.forum.questions.list(params), [params])
}

export function useQuestion(id: string) {
  return useApi(() => apiMethods.forum.questions.get(id), [id])
}

export function useUserStats() {
  return useApi(() => apiMethods.user.stats())
}

export function useAdminUsers() {
  return useApi(() => apiMethods.admin.users())
}

export function useAdminQuizzes() {
  return useApi(() => apiMethods.admin.quizzes())
}

export function useAdminAnalytics() {
  return useApi(() => apiMethods.admin.analytics())
}

export function useSubjects() {
  return useApi(() => apiMethods.subjects())
}

// Health check hook
export function useHealthCheck() {
  const [isHealthy, setIsHealthy] = useState<boolean | null>(null)
  const [lastCheck, setLastCheck] = useState<Date | null>(null)

  const checkHealth = useCallback(async () => {
    try {
      await apiMethods.health()
      setIsHealthy(true)
      setLastCheck(new Date())
    } catch (error) {
      setIsHealthy(false)
      setLastCheck(new Date())
    }
  }, [])

  useEffect(() => {
    checkHealth()
    const interval = setInterval(checkHealth, 30000) // Check every 30 seconds
    return () => clearInterval(interval)
  }, [checkHealth])

  return { isHealthy, lastCheck, checkHealth }
}

// Quiz session hook
export function useQuizSession(sessionId?: string) {
  const [session, setSession] = useState<any>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const startSession = useCallback(async (quizId: string, timeLimitMinutes?: number) => {
    try {
      setLoading(true)
      setError(null)
      const response = await apiMethods.sessions.start(quizId, timeLimitMinutes)
      setSession(response.data)
      return response.data
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message)
      throw err
    } finally {
      setLoading(false)
    }
  }, [])

  const activateSession = useCallback(async (id: string) => {
    try {
      setLoading(true)
      const response = await apiMethods.sessions.activate(id)
      setSession((prev) => ({ ...prev, ...response.data }))
      return response.data
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message)
      throw err
    } finally {
      setLoading(false)
    }
  }, [])

  const updateSession = useCallback(async (id: string, currentQuestionIndex: number, answers: string[]) => {
    try {
      const response = await apiMethods.sessions.update(id, currentQuestionIndex, answers)
      return response.data
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message)
      throw err
    }
  }, [])

  const submitSession = useCallback(async (id: string) => {
    try {
      setLoading(true)
      const response = await apiMethods.sessions.submit(id)
      setSession((prev) => ({ ...prev, status: "completed" }))
      return response.data
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message)
      throw err
    } finally {
      setLoading(false)
    }
  }, [])

  const getSessionStatus = useCallback(async (id: string) => {
    try {
      const response = await apiMethods.sessions.status(id)
      setSession(response.data)
      return response.data
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message)
      throw err
    }
  }, [])

  return {
    session,
    loading,
    error,
    startSession,
    activateSession,
    updateSession,
    submitSession,
    getSessionStatus,
  }
}
