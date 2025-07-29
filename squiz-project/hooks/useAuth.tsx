"use client"

import React, { useState, useEffect, createContext, useContext, ReactNode } from "react"

interface User {
  id: string
  email: string
  name: string
  role: "admin" | "user"
  is_active: boolean
  created_at: string
  is_private: boolean
  follower_count: number
  following_count: number
  avatar?: string
  bio?: string
  location?: string
  website?: string
  can_create_quiz?: boolean
}

interface AuthContextType {
  user: User | null
  isLoading: boolean
  login: (email: string, password: string) => Promise<void>
  register: (email: string, password: string, name: string) => Promise<void>
  logout: () => void
  updateProfile: (data: Partial<User>) => Promise<void>
  changePassword: (currentPassword: string, newPassword: string) => Promise<void>
  canCreateQuiz: () => boolean
  hasPermission: (permission: string) => boolean
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    // Check for existing token on mount
    const token = localStorage.getItem("token")
    if (token) {
      fetchUserData(token)
    } else {
      setIsLoading(false)
    }
  }, [])

  const fetchUserData = async (token: string) => {
    try {
      const response = await fetch("/api/auth/me", {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      })

      if (response.ok) {
        const userData = await response.json()
        setUser(userData)
      } else {
        localStorage.removeItem("token")
      }
    } catch (error) {
      console.error("Error fetching user data:", error)
      localStorage.removeItem("token")
    } finally {
      setIsLoading(false)
    }
  }

  const login = async (email: string, password: string) => {
    setIsLoading(true)
    try {
      const response = await fetch(`${window.location.origin}/api/auth/login`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ email, password }),
      })

      if (!response.ok) {
        const error = await response.json()
        throw new Error(error.detail || "Giriş uğursuz")
      }

      const data = await response.json()
      localStorage.setItem("token", data.access_token)
      setUser(data.user)
    } finally {
      setIsLoading(false)
    }
  }

  const register = async (email: string, password: string, name: string) => {
    setIsLoading(true)
    try {
      const response = await fetch(`${window.location.origin}/api/auth/register`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ email, password, name }),
      })

      if (!response.ok) {
        const error = await response.json()
        throw new Error(error.detail || "Qeydiyyat uğursuz")
      }

      // Auto login after registration
      await login(email, password)
    } finally {
      setIsLoading(false)
    }
  }

  const updateProfile = async (data: Partial<User>) => {
    try {
      const token = localStorage.getItem("token")
      const response = await fetch("/api/auth/profile", {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify(data),
      })

      if (!response.ok) {
        const error = await response.json()
        throw new Error(error.detail || "Profil yenilənmədi")
      }

      const updatedUser = await response.json()
      setUser(updatedUser)
    } catch (error) {
      throw error
    }
  }

  const changePassword = async (currentPassword: string, newPassword: string) => {
    try {
      const token = localStorage.getItem("token")
      const response = await fetch("/api/auth/change-password", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({ current_password: currentPassword, new_password: newPassword }),
      })

      if (!response.ok) {
        const error = await response.json()
        throw new Error(error.detail || "Şifrə dəyişdirilmədi")
      }
    } catch (error) {
      throw error
    }
  }

  const logout = () => {
    localStorage.removeItem("token")
    setUser(null)
  }

  const canCreateQuiz = () => {
    if (!user) return false
    // Admin-lər həmişə quiz yarada bilər
    if (user.role === "admin") return true
    // Digər istifadəçilər üçün icazə yoxlanılır
    return user.can_create_quiz === true
  }

  const hasPermission = (permission: string) => {
    if (!user) return false
    
    // Admin-lər bütün icazələrə malikdir
    if (user.role === "admin") return true
    
    switch (permission) {
      case "create_quiz":
        return canCreateQuiz()
      case "manage_users":
        return user.role === "admin"
      case "view_reports":
        return user.role === "admin"
      default:
        return false
    }
  }

  return (
    <AuthContext.Provider 
      value={{ 
        user, 
        isLoading, 
        login, 
        register, 
        logout, 
        updateProfile, 
        changePassword,
        canCreateQuiz,
        hasPermission
      }}
    >
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (context === undefined) {
    throw new Error("useAuth must be used within an AuthProvider")
  }
  return context
}
