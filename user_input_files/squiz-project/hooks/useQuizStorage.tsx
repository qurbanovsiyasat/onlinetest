"use client"

import { useState, useEffect, useCallback } from "react"

interface QuizQuestion {
  id: string
  question_text: string
  question_type: "multiple_choice" | "open_ended"
  options: Array<{
    text: string
    is_correct: boolean
    image_url?: string
  }>
  multiple_correct: boolean
  open_ended_answer?: {
    expected_answers: string[]
    keywords: string[]
    case_sensitive: boolean
    partial_credit: boolean
  }
  image_url?: string
  difficulty: "easy" | "medium" | "hard"
  points: number
  explanation?: string
  math_formula?: string
}

interface QuizData {
  title: string
  description: string
  category: string
  subject: string
  subcategory: string
  questions: QuizQuestion[]
  is_public: boolean
  min_pass_percentage: number
  time_limit_minutes: number | null
  shuffle_questions: boolean
  shuffle_options: boolean
}

const STORAGE_KEY = "quiz_draft_data"
const AUTO_SAVE_INTERVAL = 5000 // 5 saniyədə bir avtomatik saxlama

export function useQuizStorage() {
  const [quizData, setQuizData] = useState<QuizData>({
    title: "",
    description: "",
    category: "",
    subject: "",
    subcategory: "Ümumi",
    questions: [],
    is_public: true,
    min_pass_percentage: 70,
    time_limit_minutes: null,
    shuffle_questions: false,
    shuffle_options: false,
  })

  const [lastSaved, setLastSaved] = useState<Date | null>(null)
  const [autoSaveEnabled, setAutoSaveEnabled] = useState(true)

  // LocalStorage-dən məlumatları yüklə
  const loadFromStorage = useCallback(() => {
    try {
      const savedData = localStorage.getItem(STORAGE_KEY)
      if (savedData) {
        const parsed = JSON.parse(savedData)
        setQuizData(parsed.quizData)
        setLastSaved(parsed.lastSaved ? new Date(parsed.lastSaved) : null)
        return true
      }
    } catch (error) {
      console.error("Quiz məlumatları yüklənərkən xəta:", error)
    }
    return false
  }, [])

  // LocalStorage-ə məlumatları saxla
  const saveToStorage = useCallback((data?: QuizData) => {
    try {
      const dataToSave = data || quizData
      const saveData = {
        quizData: dataToSave,
        lastSaved: new Date().toISOString(),
        timestamp: Date.now()
      }
      localStorage.setItem(STORAGE_KEY, JSON.stringify(saveData))
      setLastSaved(new Date())
      return true
    } catch (error) {
      console.error("Quiz məlumatları saxlanılarkən xəta:", error)
      return false
    }
  }, [quizData])

  // Quiz məlumatlarını yenilə və saxla
  const updateQuizData = useCallback((updater: (prev: QuizData) => QuizData) => {
    setQuizData(prev => {
      const newData = updater(prev)
      
      // Avtomatik saxlama aktiv isə dərhal saxla
      if (autoSaveEnabled) {
        setTimeout(() => saveToStorage(newData), 100)
      }
      
      return newData
    })
  }, [autoSaveEnabled, saveToStorage])

  // Draft-ı təmizlə
  const clearDraft = useCallback(() => {
    try {
      localStorage.removeItem(STORAGE_KEY)
      setQuizData({
        title: "",
        description: "",
        category: "",
        subject: "",
        subcategory: "Ümumi",
        questions: [],
        is_public: true,
        min_pass_percentage: 70,
        time_limit_minutes: null,
        shuffle_questions: false,
        shuffle_options: false,
      })
      setLastSaved(null)
      return true
    } catch (error) {
      console.error("Draft təmizlənərkən xəta:", error)
      return false
    }
  }, [])

  // Draft mövcudluğunu yoxla
  const hasDraft = useCallback(() => {
    try {
      const savedData = localStorage.getItem(STORAGE_KEY)
      if (savedData) {
        const parsed = JSON.parse(savedData)
        return !!(parsed.quizData.title || parsed.quizData.description || parsed.quizData.questions.length > 0)
      }
    } catch (error) {
      console.error("Draft yoxlanılarkən xəta:", error)
    }
    return false
  }, [])

  // Avtomatik saxlama sistemi
  useEffect(() => {
    if (!autoSaveEnabled) return

    const interval = setInterval(() => {
      // Yalnız məzmun varsa avtomatik saxla
      if (quizData.title || quizData.description || quizData.questions.length > 0) {
        saveToStorage()
      }
    }, AUTO_SAVE_INTERVAL)

    return () => clearInterval(interval)
  }, [quizData, autoSaveEnabled, saveToStorage])

  // Komponent mount olduqda məlumatları yüklə
  useEffect(() => {
    loadFromStorage()
  }, [loadFromStorage])

  // Browser bağlandıqda məlumatları saxla
  useEffect(() => {
    const handleBeforeUnload = () => {
      if (quizData.title || quizData.description || quizData.questions.length > 0) {
        saveToStorage()
      }
    }

    window.addEventListener('beforeunload', handleBeforeUnload)
    return () => window.removeEventListener('beforeunload', handleBeforeUnload)
  }, [quizData, saveToStorage])

  return {
    quizData,
    setQuizData,
    updateQuizData,
    saveToStorage,
    loadFromStorage,
    clearDraft,
    hasDraft,
    lastSaved,
    autoSaveEnabled,
    setAutoSaveEnabled
  }
}
