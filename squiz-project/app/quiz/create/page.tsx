"use client"

import type React from "react"
import { useState, useEffect } from "react"
import { Plus, Trash2, Save, Eye, Check, AlertCircle, ImageIcon, Upload, X, Sparkles, Brain, Clock, AlertTriangle } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Switch } from "@/components/ui/switch"
import { Badge } from "@/components/ui/badge"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from "@/components/ui/dialog"
import { Alert, AlertDescription } from "@/components/ui/alert"
import { toast } from "@/hooks/use-toast"
import DashboardLayout from "@/components/layout/DashboardLayout"
import MathEditor from "@/components/MathEditor"
import { MathInput } from "@/components/MathTextRenderer"
import MathTextRenderer from "@/components/MathTextRenderer"
import { useQuizStorage } from "@/hooks/useQuizStorage"
import { useAuth } from "@/hooks/useAuth"
import Link from "next/link"

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

export default function CreateQuizPage() {
  const { user, canCreateQuiz } = useAuth()
  const {
    quizData,
    updateQuizData,
    saveToStorage,
    clearDraft,
    hasDraft,
    lastSaved,
    autoSaveEnabled,
    setAutoSaveEnabled
  } = useQuizStorage()

  const [currentQuestion, setCurrentQuestion] = useState<QuizQuestion>({
    id: "",
    question_text: "",
    question_type: "multiple_choice",
    options: [
      { text: "", is_correct: false },
      { text: "", is_correct: false },
    ],
    multiple_correct: false,
    difficulty: "medium",
    points: 1,
    explanation: "",
    math_formula: "",
  })

  const [activeTab, setActiveTab] = useState("basic")
  const [isPreview, setIsPreview] = useState(false)
  const [isSaving, setIsSaving] = useState(false)
  const [questionImageFile, setQuestionImageFile] = useState<File | null>(null)
  const [optionImageFiles, setOptionImageFiles] = useState<{ [key: number]: File | null }>({})
  const [showDraftDialog, setShowDraftDialog] = useState(false)
  
  // AI generation state
  const [showAIDialog, setShowAIDialog] = useState(false)
  const [isGenerating, setIsGenerating] = useState(false)
  const [aiTopic, setAiTopic] = useState("")
  const [aiDifficulty, setAiDifficulty] = useState<"easy" | "medium" | "hard">("medium")
  const [aiQuestionCount, setAiQuestionCount] = useState(5)
  const [aiQuestionType, setAiQuestionType] = useState<"multiple_choice" | "open_ended" | "mixed">("multiple_choice")

  // Draft restore effect
  useEffect(() => {
    if (hasDraft()) {
      setShowDraftDialog(true)
    }
  }, [])

  // Şəkil yükləmə funksiyası
  const handleImageUpload = async (file: File): Promise<string> => {
    const formData = new FormData()
    formData.append("image", file)

    try {
      const response = await fetch("/api/upload/image", {
        method: "POST",
        body: formData,
      })

      if (response.ok) {
        const data = await response.json()
        return data.url
      } else {
        throw new Error("Şəkil yükləmə uğursuz oldu")
      }
    } catch (error) {
      console.error("Şəkil yükləmə xətası:", error)
      toast({
        title: "Xəta",
        description: "Şəkil yükləmə zamanı xəta baş verdi",
        variant: "destructive",
      })
      return URL.createObjectURL(file) // Müvəqqəti URL
    }
  }

  const handleQuestionImageChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (file) {
      setQuestionImageFile(file)
      const imageUrl = await handleImageUpload(file)
      setCurrentQuestion((prev) => ({ ...prev, image_url: imageUrl }))
    }
  }

  const handleOptionImageChange = async (index: number, e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (file) {
      setOptionImageFiles((prev) => ({ ...prev, [index]: file }))
      const imageUrl = await handleImageUpload(file)
      setCurrentQuestion((prev) => ({
        ...prev,
        options: prev.options.map((option, i) => (i === index ? { ...option, image_url: imageUrl } : option)),
      }))
    }
  }

  const removeQuestionImage = () => {
    setQuestionImageFile(null)
    setCurrentQuestion((prev) => ({ ...prev, image_url: undefined }))
  }

  const removeOptionImage = (index: number) => {
    setOptionImageFiles((prev) => {
      const newFiles = { ...prev }
      delete newFiles[index]
      return newFiles
    })
    setCurrentQuestion((prev) => ({
      ...prev,
      options: prev.options.map((option, i) => (i === index ? { ...option, image_url: undefined } : option)),
    }))
  }

  const addOption = () => {
    if (currentQuestion.options.length < 6) {
      setCurrentQuestion((prev) => ({
        ...prev,
        options: [...prev.options, { text: "", is_correct: false }],
      }))
    }
  }

  const removeOption = (index: number) => {
    if (currentQuestion.options.length > 2) {
      setCurrentQuestion((prev) => ({
        ...prev,
        options: prev.options.filter((_, i) => i !== index),
      }))
    }
  }

  const updateOption = (index: number, field: "text" | "is_correct", value: string | boolean) => {
    setCurrentQuestion((prev) => ({
      ...prev,
      options: prev.options.map((option, i) => (i === index ? { ...option, [field]: value } : option)),
    }))
  }

  const addQuestion = () => {
    if (!currentQuestion.question_text.trim()) {
      toast({
        title: "Xəta",
        description: "Sual mətni boş ola bilməz",
        variant: "destructive",
      })
      return
    }

    // Çoxvariantlı suallar üçün ən azı bir düzgün cavab olmalıdır
    if (currentQuestion.question_type === "multiple_choice") {
      const hasCorrectAnswer = currentQuestion.options.some((option) => option.is_correct && option.text.trim())
      if (!hasCorrectAnswer) {
        toast({
          title: "Xəta",
          description: "Ən azı bir düzgün cavab seçin və mətni daxil edin",
          variant: "destructive",
        })
        return
      }
    }

    const newQuestion = {
      ...currentQuestion,
      id: Date.now().toString(),
    }

    updateQuizData((prev) => ({
      ...prev,
      questions: [...prev.questions, newQuestion],
    }))

    // Reset current question
    setCurrentQuestion({
      id: "",
      question_text: "",
      question_type: "multiple_choice",
      options: [
        { text: "", is_correct: false },
        { text: "", is_correct: false },
      ],
      multiple_correct: false,
      difficulty: "medium",
      points: 1,
      explanation: "",
      math_formula: "",
    })
    setQuestionImageFile(null)
    setOptionImageFiles({})

    toast({
      title: "Uğurlu",
      description: "Sual əlavə edildi",
    })
  }

  const removeQuestion = (questionId: string) => {
    updateQuizData((prev) => ({
      ...prev,
      questions: prev.questions.filter((q) => q.id !== questionId),
    }))

    toast({
      title: "Uğurlu",
      description: "Sual silindi",
    })
  }

  const saveQuiz = async (isDraft = true) => {
    // Validasiya
    if (!quizData.title.trim()) {
      toast({
        title: "Xəta",
        description: "Test başlığı boş ola bilməz",
        variant: "destructive",
      })
      return
    }

    if (!quizData.description.trim()) {
      toast({
        title: "Xəta",
        description: "Test açıqlaması boş ola bilməz",
        variant: "destructive",
      })
      return
    }

    if (!quizData.category) {
      toast({
        title: "Xəta",
        description: "Kateqoriya seçin",
        variant: "destructive",
      })
      return
    }

    if (quizData.questions.length === 0) {
      toast({
        title: "Xəta",
        description: "Ən azı bir sual əlavə edin",
        variant: "destructive",
      })
      return
    }

    setIsSaving(true)
    try {
      // Mock API call - real implementation would save to database
      await new Promise((resolve) => setTimeout(resolve, 2000))

      toast({
        title: "Uğurlu",
        description: isDraft ? "Test layihə olaraq saxlandı" : "Test dərc edildi",
      })

      // Uğurlu saxlandıqdan sonra draft-ı təmizlə
      if (!isDraft) {
        clearDraft()
      }

      setTimeout(() => {
        window.location.href = "/quizzes"
      }, 1000)
    } catch (error) {
      console.error("Test saxlama xətası:", error)
      toast({
        title: "Xəta",
        description: "Test saxlanıla bilmədi",
        variant: "destructive",
      })
    } finally {
      setIsSaving(false)
    }
  }

  // AI Question Generation Function
  const generateAIQuestions = async () => {
    if (!aiTopic.trim()) {
      toast({
        title: "Xəta",
        description: "Mövzu daxil edin",
        variant: "destructive",
      })
      return
    }

    setIsGenerating(true)
    try {
      const response = await fetch("/api/ai/generate-questions", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          topic: aiTopic,
          difficulty: aiDifficulty,
          questionCount: aiQuestionCount,
          questionType: aiQuestionType,
          language: "az"
        }),
      })

      if (!response.ok) {
        throw new Error("AI sual generasiya edilmədi")
      }

      const data = await response.json()
      
      // Add generated questions to quiz
      updateQuizData((prev) => ({
        ...prev,
        questions: [...prev.questions, ...data.questions],
      }))

      toast({
        title: "Uğurlu",
        description: `${data.questions.length} sual AI tərəfindən yaradıldı`,
      })

      // Close AI dialog and reset values
      setShowAIDialog(false)
      setAiTopic("")
      setAiDifficulty("medium")
      setAiQuestionCount(5)
      setAiQuestionType("multiple_choice")

    } catch (error) {
      console.error("AI sual generasiya xətası:", error)
      toast({
        title: "Xəta",
        description: "AI sualları yarada bilmədi",
        variant: "destructive",
      })
    } finally {
      setIsGenerating(false)
    }
  }

  const getDifficultyColor = (difficulty: string) => {
    switch (difficulty) {
      case "easy":
        return "bg-green-100 text-green-800"
      case "medium":
        return "bg-yellow-100 text-yellow-800"
      case "hard":
        return "bg-red-100 text-red-800"
      default:
        return "bg-gray-100 text-gray-800"
    }
  }

  // Quiz yaratma icazəsi yoxlaması
  if (user && !canCreateQuiz()) {
    return (
      <DashboardLayout>
        <div className="max-w-4xl mx-auto p-4 sm:p-6">
          <Card>
            <CardContent className="text-center py-12">
              <AlertTriangle className="w-16 h-16 text-yellow-500 mx-auto mb-4" />
              <h1 className="text-2xl font-bold text-gray-900 mb-4">Quiz Yaratma İcazəsi Yoxdur</h1>
              <p className="text-gray-600 mb-6 max-w-md mx-auto">
                Test yaratmaq üçün admin tərəfindən icazə verilməlidir. Admin ilə əlaqə saxlayın.
              </p>
              <Button asChild>
                <Link href="/dashboard">Dashboard-a Qayıt</Link>
              </Button>
            </CardContent>
          </Card>
        </div>
      </DashboardLayout>
    )
  }

  return (
    <DashboardLayout>
      <div className="max-w-4xl mx-auto space-y-6 p-4 sm:p-6">
        {/* Header */}
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
          <div>
            <h1 className="text-2xl sm:text-3xl font-bold text-gray-900">Yeni Test Yarat</h1>
            <p className="text-gray-600 mt-2">Tələbələriniz üçün interaktiv test yaradın</p>
            {lastSaved && (
              <div className="flex items-center gap-2 mt-1">
                <Clock className="w-4 h-4 text-green-600" />
                <span className="text-sm text-green-600">
                  Son saxlanılan: {lastSaved.toLocaleTimeString('az-AZ')}
                </span>
              </div>
            )}
          </div>

          <div className="flex flex-col sm:flex-row gap-3">
            <div className="flex items-center gap-2">
              <Switch
                checked={autoSaveEnabled}
                onCheckedChange={setAutoSaveEnabled}
                size="sm"
              />
              <span className="text-sm text-gray-600">Avtomatik saxlama</span>
            </div>
            <Button variant="outline" onClick={() => setIsPreview(!isPreview)} className="w-full sm:w-auto">
              <Eye className="w-4 h-4 mr-2" />
              {isPreview ? "Redaktə Et" : "Önizləmə"}
            </Button>
            <Button onClick={() => saveQuiz(true)} disabled={isSaving} className="w-full sm:w-auto">
              <Save className="w-4 h-4 mr-2" />
              {isSaving ? "Saxlanılır..." : "Layihə Saxla"}
            </Button>
          </div>
        </div>

        {!isPreview ? (
          <Tabs value={activeTab} onValueChange={setActiveTab}>
            <TabsList className="grid w-full grid-cols-3">
              <TabsTrigger value="basic">Əsas</TabsTrigger>
              <TabsTrigger value="questions">Suallar</TabsTrigger>
              <TabsTrigger value="settings">Ayarlar</TabsTrigger>
            </TabsList>

            {/* Basic Information */}
            <TabsContent value="basic" className="space-y-6">
              <Card>
                <CardHeader>
                  <CardTitle>Test Məlumatları</CardTitle>
                  <CardDescription>Testinizin əsas məlumatlarını daxil edin</CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="grid grid-cols-1 gap-4">
                    <div className="space-y-2">
                      <Label htmlFor="title">Test Başlığı *</Label>
                      <Input
                        id="title"
                        placeholder="Məs: JavaScript Əsasları"
                        value={quizData.title}
                        onChange={(e) => updateQuizData((prev) => ({ ...prev, title: e.target.value }))}
                      />
                    </div>

                    <div className="space-y-2">
                      <Label htmlFor="category">Kateqoriya *</Label>
                      <Select
                        value={quizData.category}
                        onValueChange={(value) => updateQuizData((prev) => ({ ...prev, category: value }))}
                      >
                        <SelectTrigger>
                          <SelectValue placeholder="Kateqoriya seçin" />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="Proqramlaşdırma">Proqramlaşdırma</SelectItem>
                          <SelectItem value="Dizayn">Dizayn</SelectItem>
                          <SelectItem value="Riyaziyyat">Riyaziyyat</SelectItem>
                          <SelectItem value="Fen Elmləri">Fen Elmləri</SelectItem>
                          <SelectItem value="Dil">Dil</SelectItem>
                          <SelectItem value="Tarix">Tarix</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>
                  </div>

                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                    <div className="space-y-2">
                      <Label htmlFor="subject">Mövzu *</Label>
                      <Input
                        id="subject"
                        placeholder="Məs: Web Development"
                        value={quizData.subject}
                        onChange={(e) => updateQuizData((prev) => ({ ...prev, subject: e.target.value }))}
                      />
                    </div>

                    <div className="space-y-2">
                      <Label htmlFor="subcategory">Alt Kateqoriya</Label>
                      <Input
                        id="subcategory"
                        placeholder="Məs: Frontend"
                        value={quizData.subcategory}
                        onChange={(e) => updateQuizData((prev) => ({ ...prev, subcategory: e.target.value }))}
                      />
                    </div>
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="description">Açıqlama *</Label>
                    <Textarea
                      id="description"
                      placeholder="Test haqqında ətraflı açıqlama yazın..."
                      rows={4}
                      value={quizData.description}
                      onChange={(e) => updateQuizData((prev) => ({ ...prev, description: e.target.value }))}
                    />
                  </div>
                </CardContent>
              </Card>
            </TabsContent>

            {/* Questions */}
            <TabsContent value="questions" className="space-y-6">
              {/* Add Question Form */}
              <Card>
                <CardHeader>
                  <CardTitle>Yeni Sual Əlavə Et</CardTitle>
                  <CardDescription>Testinizə sual əlavə edin</CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="space-y-2">
                    <MathInput
                      value={currentQuestion.question_text}
                      onChange={(value) => setCurrentQuestion((prev) => ({ ...prev, question_text: value }))}
                      placeholder="Sualınızı buraya yazın... (LaTeX dəstəklənir: $x^2$, $$\frac{a}{b}$$)"
                    />
                  </div>

                  {/* Sual üçün şəkil yükləmə */}
                  <div className="space-y-2">
                    <Label>Sual Şəkli (İstəyə görə)</Label>
                    <div className="flex items-center gap-4">
                      <div className="flex-1">
                        <Input
                          type="file"
                          accept="image/*"
                          onChange={handleQuestionImageChange}
                          className="hidden"
                          id="question-image"
                        />
                        <Label
                          htmlFor="question-image"
                          className="flex items-center justify-center w-full h-24 sm:h-32 border-2 border-dashed border-gray-300 rounded-lg cursor-pointer hover:border-gray-400 transition-colors"
                        >
                          {currentQuestion.image_url ? (
                            <div className="relative w-full h-full">
                              <img
                                src={currentQuestion.image_url || "/placeholder.svg"}
                                alt="Sual şəkli"
                                className="w-full h-full object-cover rounded-lg"
                              />
                              <Button
                                type="button"
                                variant="destructive"
                                size="sm"
                                onClick={removeQuestionImage}
                                className="absolute top-2 right-2"
                              >
                                <X className="w-4 h-4" />
                              </Button>
                            </div>
                          ) : (
                            <div className="text-center">
                              <Upload className="w-6 sm:w-8 h-6 sm:h-8 text-gray-400 mx-auto mb-2" />
                              <p className="text-sm text-gray-600">Şəkil yüklə</p>
                            </div>
                          )}
                        </Label>
                      </div>
                    </div>
                  </div>

                  {/* Riyazi İfadə Editoru */}
                  <MathEditor
                    value={currentQuestion.math_formula || ""}
                    onChange={(value) => setCurrentQuestion((prev) => ({ ...prev, math_formula: value }))}
                    placeholder="Riyazi ifadə və ya formula daxil edin..."
                  />

                  <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                    <div className="space-y-2">
                      <Label>Sual Növü</Label>
                      <Select
                        value={currentQuestion.question_type}
                        onValueChange={(value: "multiple_choice" | "open_ended") =>
                          setCurrentQuestion((prev) => ({ ...prev, question_type: value }))
                        }
                      >
                        <SelectTrigger>
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="multiple_choice">Çoxvariantlı</SelectItem>
                          <SelectItem value="open_ended">Açıq Cavablı</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>

                    <div className="space-y-2">
                      <Label>Çətinlik</Label>
                      <Select
                        value={currentQuestion.difficulty}
                        onValueChange={(value: "easy" | "medium" | "hard") =>
                          setCurrentQuestion((prev) => ({ ...prev, difficulty: value }))
                        }
                      >
                        <SelectTrigger>
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="easy">Asan</SelectItem>
                          <SelectItem value="medium">Orta</SelectItem>
                          <SelectItem value="hard">Çətin</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>

                    <div className="space-y-2">
                      <Label htmlFor="points">Bal</Label>
                      <Input
                        id="points"
                        type="number"
                        min="1"
                        max="10"
                        value={currentQuestion.points}
                        onChange={(e) =>
                          setCurrentQuestion((prev) => ({ ...prev, points: Number.parseInt(e.target.value) || 1 }))
                        }
                      />
                    </div>
                  </div>

                  {/* Multiple Choice Options */}
                  {currentQuestion.question_type === "multiple_choice" && (
                    <div className="space-y-4">
                      <div className="flex items-center justify-between">
                        <Label>Variantlar</Label>
                        <Button
                          type="button"
                          variant="outline"
                          size="sm"
                          onClick={addOption}
                          disabled={currentQuestion.options.length >= 6}
                        >
                          <Plus className="w-4 h-4 mr-2" />
                          Variant Əlavə Et
                        </Button>
                      </div>

                      <div className="space-y-3">
                        {currentQuestion.options.map((option, index) => (
                          <div key={index} className="space-y-2 p-3 border rounded-lg">
                            <div className="flex items-center gap-3">
                              <div className="flex items-center">
                                <input
                                  type="checkbox"
                                  checked={option.is_correct}
                                  onChange={(e) => updateOption(index, "is_correct", e.target.checked)}
                                  className="w-4 h-4 text-blue-600 rounded focus:ring-blue-500"
                                />
                              </div>
                              <div className="flex-1 space-y-1">
                                <Input
                                  placeholder={`Variant ${index + 1} (LaTeX: $x^2$)`}
                                  value={option.text}
                                  onChange={(e) => updateOption(index, "text", e.target.value)}
                                />
                                {option.text && /\$.*?\$|\\\(.*?\\\)/.test(option.text) && (
                                  <div className="text-xs p-2 bg-gray-50 border rounded">
                                    <MathInput
                                      value={option.text}
                                      onChange={(value) => updateOption(index, "text", value)}
                                      className="hidden"
                                    />
                                    <div className="text-gray-600">Önizləmə: </div>
                                    <div className="mt-1">
                                      <MathTextRenderer text={option.text} />
                                    </div>
                                  </div>
                                )}
                              </div>
                              {currentQuestion.options.length > 2 && (
                                <Button type="button" variant="ghost" size="sm" onClick={() => removeOption(index)}>
                                  <Trash2 className="w-4 h-4" />
                                </Button>
                              )}
                            </div>

                            {/* Variant üçün şəkil */}
                            <div className="ml-7">
                              <Input
                                type="file"
                                accept="image/*"
                                onChange={(e) => handleOptionImageChange(index, e)}
                                className="hidden"
                                id={`option-image-${index}`}
                              />
                              <Label
                                htmlFor={`option-image-${index}`}
                                className="flex items-center justify-center w-full h-16 sm:h-20 border border-dashed border-gray-300 rounded cursor-pointer hover:border-gray-400 transition-colors"
                              >
                                {option.image_url ? (
                                  <div className="relative w-full h-full">
                                    <img
                                      src={option.image_url || "/placeholder.svg"}
                                      alt={`Variant ${index + 1} şəkli`}
                                      className="w-full h-full object-cover rounded"
                                    />
                                    <Button
                                      type="button"
                                      variant="destructive"
                                      size="sm"
                                      onClick={() => removeOptionImage(index)}
                                      className="absolute top-1 right-1 h-6 w-6 p-0"
                                    >
                                      <X className="w-3 h-3" />
                                    </Button>
                                  </div>
                                ) : (
                                  <div className="text-center">
                                    <ImageIcon className="w-4 h-4 text-gray-400 mx-auto mb-1" />
                                    <p className="text-xs text-gray-600">Şəkil</p>
                                  </div>
                                )}
                              </Label>
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Open Ended Answer */}
                  {currentQuestion.question_type === "open_ended" && (
                    <div className="space-y-4">
                      <div className="space-y-2">
                        <Label>Gözlənilən Cavablar</Label>
                        <Textarea placeholder="Qəbul ediləcək cavabları vergüllə ayıraraq yazın..." rows={3} />
                      </div>
                      <div className="space-y-2">
                        <Label>Açar Sözlər</Label>
                        <Input placeholder="Qiymətləndirmə üçün açar sözlər..." />
                      </div>
                    </div>
                  )}

                  <div className="space-y-2">
                    <Label htmlFor="explanation">Açıqlama (İstəyə görə)</Label>
                    <Textarea
                      id="explanation"
                      placeholder="Sual üçün açıqlama və ya ipucu..."
                      rows={2}
                      value={currentQuestion.explanation}
                      onChange={(e) => setCurrentQuestion((prev) => ({ ...prev, explanation: e.target.value }))}
                    />
                  </div>

                  <div className="flex gap-2">
                    <Button onClick={addQuestion} disabled={!currentQuestion.question_text.trim()} className="flex-1">
                      <Plus className="w-4 h-4 mr-2" />
                      Sual Əlavə Et
                    </Button>
                    <Button 
                      onClick={() => setShowAIDialog(true)} 
                      variant="outline" 
                      className="flex-1 bg-gradient-to-r from-purple-50 to-blue-50 border-purple-200 hover:from-purple-100 hover:to-blue-100"
                    >
                      <Brain className="w-4 h-4 mr-2" />
                      AI ilə Sual Yarat
                    </Button>
                  </div>
                </CardContent>
              </Card>

              {/* Questions List */}
              {quizData.questions.length > 0 && (
                <Card>
                  <CardHeader>
                    <CardTitle>Əlavə Edilmiş Suallar ({quizData.questions.length})</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-4">
                      {quizData.questions.map((question, index) => (
                        <div key={question.id} className="p-4 border rounded-lg">
                          <div className="flex items-start justify-between">
                            <div className="flex-1">
                              <div className="flex items-center gap-2 mb-2 flex-wrap">
                                <Badge variant="outline">Sual {index + 1}</Badge>
                                <Badge className={getDifficultyColor(question.difficulty)}>
                                  {question.difficulty === "easy"
                                    ? "Asan"
                                    : question.difficulty === "medium"
                                      ? "Orta"
                                      : "Çətin"}
                                </Badge>
                                <Badge variant="secondary">{question.points} bal</Badge>
                              </div>
                              <p className="font-medium mb-2">
                                <MathTextRenderer text={question.question_text} />
                              </p>

                              {question.image_url && (
                                <img
                                  src={question.image_url || "/placeholder.svg"}
                                  alt="Sual şəkli"
                                  className="w-24 sm:w-32 h-16 sm:h-20 object-cover rounded mb-2"
                                />
                              )}

                              {question.math_formula && (
                                <div className="bg-blue-50 p-2 rounded mb-2">
                                  <span className="font-mono text-sm">{question.math_formula}</span>
                                </div>
                              )}

                              {question.question_type === "multiple_choice" && (
                                <div className="space-y-1">
                                  {question.options.map((option, optIndex) => (
                                    <div key={optIndex} className="flex items-center gap-2 text-sm">
                                      {option.is_correct ? (
                                        <Check className="w-4 h-4 text-green-600" />
                                      ) : (
                                        <div className="w-4 h-4" />
                                      )}
                                      <span
                                        className={option.is_correct ? "text-green-600 font-medium" : "text-gray-600"}
                                      >
                                        <MathTextRenderer text={option.text} />
                                      </span>
                                      {option.image_url && (
                                        <img
                                          src={option.image_url || "/placeholder.svg"}
                                          alt="Variant şəkli"
                                          className="w-6 sm:w-8 h-4 sm:h-6 object-cover rounded ml-2"
                                        />
                                      )}
                                    </div>
                                  ))}
                                </div>
                              )}
                            </div>
                            <Button variant="ghost" size="sm" onClick={() => removeQuestion(question.id)}>
                              <Trash2 className="w-4 h-4" />
                            </Button>
                          </div>
                        </div>
                      ))}
                    </div>
                  </CardContent>
                </Card>
              )}
            </TabsContent>

            {/* Settings */}
            <TabsContent value="settings" className="space-y-6">
              <Card>
                <CardHeader>
                  <CardTitle>Test Ayarları</CardTitle>
                  <CardDescription>Testinizin davranış ayarlarını konfiqurasiya edin</CardDescription>
                </CardHeader>
                <CardContent className="space-y-6">
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
                    <div className="space-y-2">
                      <Label htmlFor="min_pass_percentage">Keçid Balı (%)</Label>
                      <Input
                        id="min_pass_percentage"
                        type="number"
                        min="0"
                        max="100"
                        value={quizData.min_pass_percentage}
                        onChange={(e) =>
                          updateQuizData((prev) => ({
                            ...prev,
                            min_pass_percentage: Number.parseInt(e.target.value) || 70,
                          }))
                        }
                      />
                    </div>

                    <div className="space-y-2">
                      <Label htmlFor="time_limit">Vaxt Limiti (dəqiqə)</Label>
                      <Input
                        id="time_limit"
                        type="number"
                        min="1"
                        placeholder="Vaxt limiti yoxdur"
                        value={quizData.time_limit_minutes || ""}
                        onChange={(e) =>
                          updateQuizData((prev) => ({
                            ...prev,
                            time_limit_minutes: e.target.value ? Number.parseInt(e.target.value) : null,
                          }))
                        }
                      />
                    </div>
                  </div>

                  <div className="space-y-4">
                    <div className="flex items-center justify-between">
                      <div>
                        <Label>Hamı Üçün Açıq</Label>
                        <p className="text-sm text-gray-600">Testi bütün istifadəçilər görə bilər</p>
                      </div>
                      <Switch
                        checked={quizData.is_public}
                        onCheckedChange={(checked) => updateQuizData((prev) => ({ ...prev, is_public: checked }))}
                      />
                    </div>

                    <div className="flex items-center justify-between">
                      <div>
                        <Label>Sualları Qarışdır</Label>
                        <p className="text-sm text-gray-600">Hər cəhddə suallar fərqli sırada göstərilir</p>
                      </div>
                      <Switch
                        checked={quizData.shuffle_questions}
                        onCheckedChange={(checked) => updateQuizData((prev) => ({ ...prev, shuffle_questions: checked }))}
                      />
                    </div>

                    <div className="flex items-center justify-between">
                      <div>
                        <Label>Variantları Qarışdır</Label>
                        <p className="text-sm text-gray-600">Çoxvariantlı suallarda variantlar qarışdırılır</p>
                      </div>
                      <Switch
                        checked={quizData.shuffle_options}
                        onCheckedChange={(checked) => updateQuizData((prev) => ({ ...prev, shuffle_options: checked }))}
                      />
                    </div>
                  </div>
                </CardContent>
              </Card>
            </TabsContent>
          </Tabs>
        ) : (
          /* Preview Mode */
          <Card>
            <CardHeader>
              <CardTitle>Test Önizləməsi</CardTitle>
              <CardDescription>Testinizin necə görünəcəyini yoxlayın</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-6">
                <div>
                  <h2 className="text-xl sm:text-2xl font-bold mb-2">{quizData.title || "Test Başlığı"}</h2>
                  <p className="text-gray-600 mb-4">{quizData.description || "Test açıqlaması"}</p>
                  <div className="flex gap-2 mb-4 flex-wrap">
                    <Badge>{quizData.category || "Kateqoriya"}</Badge>
                    <Badge variant="outline">{quizData.subject || "Mövzu"}</Badge>
                  </div>
                </div>

                {quizData.questions.length > 0 ? (
                  <div className="space-y-6">
                    {quizData.questions.map((question, index) => (
                      <div key={question.id} className="p-4 border rounded-lg">
                        <div className="flex items-center gap-2 mb-3 flex-wrap">
                          <Badge variant="outline">Sual {index + 1}</Badge>
                          <Badge className={getDifficultyColor(question.difficulty)}>
                            {question.difficulty === "easy"
                              ? "Asan"
                              : question.difficulty === "medium"
                                ? "Orta"
                                : "Çətin"}
                          </Badge>
                          <Badge variant="secondary">{question.points} bal</Badge>
                        </div>

                        <h3 className="font-medium mb-3">
                          <MathTextRenderer text={question.question_text} />
                        </h3>

                        {question.image_url && (
                          <img
                            src={question.image_url || "/placeholder.svg"}
                            alt="Sual şəkli"
                            className="w-full max-w-md h-40 object-cover rounded mb-3"
                          />
                        )}

                        {question.math_formula && (
                          <div className="bg-blue-50 p-3 rounded mb-3">
                            <span className="font-mono">{question.math_formula}</span>
                          </div>
                        )}

                        {question.question_type === "multiple_choice" && (
                          <div className="space-y-2">
                            {question.options.map((option, optIndex) => (
                              <div key={optIndex} className="flex items-center gap-3">
                                <input type="radio" name={`question-${question.id}`} className="w-4 h-4" disabled />
                                <span><MathTextRenderer text={option.text} /></span>
                                {option.image_url && (
                                  <img
                                    src={option.image_url || "/placeholder.svg"}
                                    alt="Variant şəkli"
                                    className="w-12 sm:w-16 h-8 sm:h-12 object-cover rounded"
                                  />
                                )}
                              </div>
                            ))}
                          </div>
                        )}

                        {question.question_type === "open_ended" && (
                          <Textarea placeholder="Cavabınızı buraya yazın..." rows={3} disabled />
                        )}
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="text-center py-8">
                    <AlertCircle className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                    <p className="text-gray-600">Hələ sual əlavə edilməyib</p>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        )}

        {/* Action Buttons */}
        <div className="flex flex-col sm:flex-row justify-between gap-3">
          <Button variant="outline" onClick={() => window.history.back()} className="w-full sm:w-auto">
            Ləğv Et
          </Button>

          <div className="flex flex-col sm:flex-row gap-3">
            <Button
              variant="outline"
              onClick={() => saveQuiz(true)}
              disabled={isSaving || !quizData.title || !quizData.description || quizData.questions.length === 0}
              className="w-full sm:w-auto"
            >
              Layihə Saxla
            </Button>
            <Button
              onClick={() => saveQuiz(false)}
              disabled={isSaving || !quizData.title || !quizData.description || quizData.questions.length === 0}
              className="w-full sm:w-auto"
            >
              Dərc Et
            </Button>
          </div>
        </div>
      </div>

      {/* AI Question Generation Dialog */}
      <Dialog open={showAIDialog} onOpenChange={setShowAIDialog}>
        <DialogContent className="max-w-md">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2">
              <Brain className="w-5 h-5 text-purple-600" />
              AI ilə Sual Yaratma
            </DialogTitle>
            <DialogDescription>
              AI-yə mövzu verin və avtomatik suallar yaradaq
            </DialogDescription>
          </DialogHeader>

          <div className="space-y-4">
            <Alert>
              <Brain className="w-4 h-4" />
              <AlertDescription>
                ChatGPT API istifadə edirik. Daha dəqiq nəticələr üçün mövzunu detallı yazın.
              </AlertDescription>
            </Alert>
            
            <div className="space-y-2">
              <Label htmlFor="ai-topic">Mövzu və Kontekst *</Label>
              <Textarea
                id="ai-topic"
                placeholder="Məsələn: JavaScript ES6 xüsusiyyətləri (arrow functions, destructuring, promises), Analitik həndəsədə düz xətt tənlikləri, Osmanlı İmperiyasının son dövrü"
                value={aiTopic}
                onChange={(e) => setAiTopic(e.target.value)}
                rows={3}
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="ai-difficulty">Çətinlik Dərəcəsi</Label>
              <Select value={aiDifficulty} onValueChange={(value: "easy" | "medium" | "hard") => setAiDifficulty(value)}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="easy">Asan</SelectItem>
                  <SelectItem value="medium">Orta</SelectItem>
                  <SelectItem value="hard">Çətin</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <Label htmlFor="ai-question-type">Sual Növü</Label>
              <Select value={aiQuestionType} onValueChange={(value: "multiple_choice" | "open_ended" | "mixed") => setAiQuestionType(value)}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="multiple_choice">Çoxvariantlı</SelectItem>
                  <SelectItem value="open_ended">Açıq Cavablı</SelectItem>
                  <SelectItem value="mixed">Qarışıq</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <Label htmlFor="ai-question-count">Sual Sayı</Label>
              <Select value={aiQuestionCount.toString()} onValueChange={(value) => setAiQuestionCount(parseInt(value))}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="3">3 sual</SelectItem>
                  <SelectItem value="5">5 sual</SelectItem>
                  <SelectItem value="10">10 sual</SelectItem>
                  <SelectItem value="15">15 sual</SelectItem>
                  <SelectItem value="20">20 sual</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>

          <DialogFooter>
            <Button variant="outline" onClick={() => setShowAIDialog(false)}>
              Ləğv Et
            </Button>
            <Button 
              onClick={generateAIQuestions} 
              disabled={isGenerating || !aiTopic.trim()}
              className="bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700"
            >
              {isGenerating ? (
                <div className="flex items-center gap-2">
                  <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                  Yaradılır...
                </div>
              ) : (
                <div className="flex items-center gap-2">
                  <Sparkles className="w-4 h-4" />
                  Sualları Yarat
                </div>
              )}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Draft Restore Dialog */}
      <Dialog open={showDraftDialog} onOpenChange={setShowDraftDialog}>
        <DialogContent className="max-w-md">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2">
              <AlertTriangle className="w-5 h-5 text-yellow-600" />
              Saxlanmış Layihə Tapıldı
            </DialogTitle>
            <DialogDescription>
              Əvvəllər işlədiyiniz test layihəsi tapıldı. Onu bərpa etmək istəyirsiniz?
            </DialogDescription>
          </DialogHeader>

          <div className="space-y-3">
            <Alert>
              <Clock className="w-4 h-4" />
              <AlertDescription>
                {lastSaved && `Son dəyişiklik: ${lastSaved.toLocaleString('az-AZ')}`}
              </AlertDescription>
            </Alert>
          </div>

          <DialogFooter>
            <Button 
              variant="outline" 
              onClick={() => {
                clearDraft()
                setShowDraftDialog(false)
              }}
            >
              Yeni Başla
            </Button>
            <Button 
              onClick={() => setShowDraftDialog(false)}
              className="bg-blue-600 hover:bg-blue-700"
            >
              Layihəni Bərpa Et
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </DashboardLayout>
  )
}
