"use client"

import { useEffect } from "react"
import { useAuth } from "@/hooks/useAuth"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { BookOpen, Users, Award, Settings } from "lucide-react"
import AuthModal from "@/components/auth/AuthModal"
import { useState } from "react"
import Link from "next/link"

export default function HomePage() {
  const [showAuthModal, setShowAuthModal] = useState(false)
  const [authMode, setAuthMode] = useState<"login" | "register">("login")
  const { user, isLoading } = useAuth()

  // Authenticated users are redirected to quizzes
  useEffect(() => {
    if (user && !isLoading) {
      window.location.href = "/quizzes"
    }
  }, [user, isLoading])

  const handleLogin = () => {
    setAuthMode("login")
    setShowAuthModal(true)
  }

  const handleRegister = () => {
    setAuthMode("register")
    setShowAuthModal(true)
  }

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    )
  }

  if (user) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center p-4">
      <div className="max-w-4xl w-full">
        {/* Header */}
        <div className="text-center mb-8">
          <div className="flex items-center justify-center mb-4">
            <div className="w-16 h-16 bg-gradient-to-r from-blue-600 to-purple-600 rounded-xl flex items-center justify-center">
              <BookOpen className="w-8 h-8 text-white" />
            </div>
          </div>
          <h1 className="text-4xl font-bold text-gray-900 mb-2">Quiz Sistemi</h1>
          <p className="text-lg text-gray-600">
            Quizlər yaradın, iştirak edin və öyrənin
          </p>
        </div>

        {/* Auth Cards */}
        <div className="grid md:grid-cols-2 gap-6 mb-8">
          <Card className="hover:shadow-lg transition-shadow">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Users className="w-5 h-5 text-blue-600" />
                Daxil Ol
              </CardTitle>
              <CardDescription>
                Mövcud hesabınızla daxil olaraq quizlərə iştirak edin
              </CardDescription>
            </CardHeader>
            <CardContent>
              <Button onClick={handleLogin} className="w-full bg-blue-600 hover:bg-blue-700">
                Daxil Ol
              </Button>
            </CardContent>
          </Card>

          <Card className="hover:shadow-lg transition-shadow">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Award className="w-5 h-5 text-green-600" />
                Qeydiyyat
              </CardTitle>
              <CardDescription>
                Yeni hesab yaradaraq quiz yaratmağa başlayın
              </CardDescription>
            </CardHeader>
            <CardContent>
              <Button onClick={handleRegister} className="w-full bg-green-600 hover:bg-green-700">
                Qeydiyyat
              </Button>
            </CardContent>
          </Card>
        </div>

        {/* Quick Features */}
        <div className="grid md:grid-cols-3 gap-4 text-center">
          <div className="p-4 bg-white rounded-lg shadow-sm">
            <BookOpen className="w-8 h-8 text-blue-600 mx-auto mb-2" />
            <h3 className="font-medium text-gray-900">Quiz Yaradın</h3>
            <p className="text-sm text-gray-600">AI ilə sual yaradın</p>
          </div>
          <div className="p-4 bg-white rounded-lg shadow-sm">
            <Users className="w-8 h-8 text-green-600 mx-auto mb-2" />
            <h3 className="font-medium text-gray-900">İştirak Edin</h3>
            <p className="text-sm text-gray-600">Quizləri həll edin</p>
          </div>
          <div className="p-4 bg-white rounded-lg shadow-sm">
            <Award className="w-8 h-8 text-purple-600 mx-auto mb-2" />
            <h3 className="font-medium text-gray-900">Nəticələr</h3>
            <p className="text-sm text-gray-600">Performansı izləyin</p>
          </div>
        </div>
      </div>

      <AuthModal
        isOpen={showAuthModal}
        onClose={() => setShowAuthModal(false)}
        mode={authMode}
        onToggleMode={() => setAuthMode(authMode === "login" ? "register" : "login")}
      />
    </div>
  )
}
