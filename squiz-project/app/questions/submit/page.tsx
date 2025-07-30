"use client"

import { useState } from "react"
import { motion } from "framer-motion"
import { ArrowLeft, Send, Plus, Trash2, Check, Brain, Save, Eye, AlertCircle, CheckCircle } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Switch } from "@/components/ui/switch"
import { Badge } from "@/components/ui/badge"
import { Alert, AlertDescription } from "@/components/ui/alert"
import { toast } from "@/hooks/use-toast"
import DashboardLayout from "@/components/layout/DashboardLayout"
import MathTextRenderer from "@/components/MathTextRenderer"
import { MathInput } from "@/components/MathTextRenderer"
import Link from "next/link"
import { useRouter } from "next/navigation"

interface QuestionOption {
  text: string
  is_correct: boolean
}

interface QuestionData {
  title: string
  question_text: string
  question_type: "multiple_choice" | "open_ended"
  category: string
  difficulty: "easy" | "medium" | "hard"
  options: QuestionOption[]
  expected_answers: string[]
  keywords: string[]
  explanation: string
  math_formula: string
  tags: string[]
  is_public: boolean
}

export default function SubmitQuestionPage() {
  const router = useRouter()
  const [isPreview, setIsPreview] = useState(false)
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [showSuccessAlert, setShowSuccessAlert] = useState(false)

  const [questionData, setQuestionData] = useState<QuestionData>({
    title: "",
    question_text: "",
    question_type: "multiple_choice",
    category: "",
    difficulty: "medium",
    options: [
      { text: "", is_correct: false },
      { text: "", is_correct: false }
    ],
    expected_answers: [""],
    keywords: [""],
    explanation: "",
    math_formula: "",
    tags: [],
    is_public: true
  })

  const [currentTag, setCurrentTag] = useState("")

  const addOption = () => {
    if (questionData.options.length < 6) {
      setQuestionData(prev => ({
        ...prev,
        options: [...prev.options, { text: "", is_correct: false }]
      }))
    }
  }

  const removeOption = (index: number) => {
    if (questionData.options.length > 2) {
      setQuestionData(prev => ({
        ...prev,
        options: prev.options.filter((_, i) => i !== index)
      }))
    }
  }

  const updateOption = (index: number, field: "text" | "is_correct", value: string | boolean) => {
    setQuestionData(prev => ({
      ...prev,
      options: prev.options.map((option, i) => 
        i === index ? { ...option, [field]: value } : option
      )
    }))
  }

  const addExpectedAnswer = () => {
    setQuestionData(prev => ({
      ...prev,
      expected_answers: [...prev.expected_answers, ""]
    }))
  }

  const removeExpectedAnswer = (index: number) => {
    if (questionData.expected_answers.length > 1) {
      setQuestionData(prev => ({
        ...prev,
        expected_answers: prev.expected_answers.filter((_, i) => i !== index)
      }))
    }
  }

  const updateExpectedAnswer = (index: number, value: string) => {
    setQuestionData(prev => ({
      ...prev,
      expected_answers: prev.expected_answers.map((answer, i) => 
        i === index ? value : answer
      )
    }))
  }

  const addKeyword = () => {
    setQuestionData(prev => ({
      ...prev,
      keywords: [...prev.keywords, ""]
    }))
  }

  const removeKeyword = (index: number) => {
    if (questionData.keywords.length > 1) {
      setQuestionData(prev => ({
        ...prev,
        keywords: prev.keywords.filter((_, i) => i !== index)
      }))
    }
  }

  const updateKeyword = (index: number, value: string) => {
    setQuestionData(prev => ({
      ...prev,
      keywords: prev.keywords.map((keyword, i) => 
        i === index ? value : keyword
      )
    }))
  }

  const addTag = () => {
    if (currentTag.trim() && !questionData.tags.includes(currentTag.trim().toLowerCase())) {
      setQuestionData(prev => ({
        ...prev,
        tags: [...prev.tags, currentTag.trim().toLowerCase()]
      }))
      setCurrentTag("")
    }
  }

  const removeTag = (tagToRemove: string) => {
    setQuestionData(prev => ({
      ...prev,
      tags: prev.tags.filter(tag => tag !== tagToRemove)
    }))
  }

  const validateForm = (): string[] => {
    const errors: string[] = []

    if (!questionData.title.trim()) {
      errors.push("Sual başlığı tələb olunur")
    }

    if (!questionData.question_text.trim()) {
      errors.push("Sual mətni tələb olunur")
    }

    if (!questionData.category) {
      errors.push("Kateqoriya seçin")
    }

    if (questionData.question_type === "multiple_choice") {
      const validOptions = questionData.options.filter(opt => opt.text.trim())
      if (validOptions.length < 2) {
        errors.push("Ən azı 2 variant daxil edin")
      }
      
      const correctOptions = questionData.options.filter(opt => opt.is_correct && opt.text.trim())
      if (correctOptions.length === 0) {
        errors.push("Ən azı bir düzgün cavab seçin")
      }
    }

    if (questionData.question_type === "open_ended") {
      const validAnswers = questionData.expected_answers.filter(ans => ans.trim())
      if (validAnswers.length === 0) {
        errors.push("Ən azı bir gözlənilən cavab daxil edin")
      }
    }

    return errors
  }

  const handleSubmit = async () => {
    const errors = validateForm()
    if (errors.length > 0) {
      errors.forEach(error => {
        toast({
          title: "Xəta",
          description: error,
          variant: "destructive"
        })
      })
      return
    }

    setIsSubmitting(true)

    try {
      // Mock API call - replace with real implementation
      await new Promise(resolve => setTimeout(resolve, 2000))

      setShowSuccessAlert(true)
      
      toast({
        title: "Uğurlu!",
        description: "Sualınız uğurla göndərildi və moderasiya gözləyir",
      })

      // Reset form after successful submission
      setTimeout(() => {
        router.push("/questions")
      }, 3000)

    } catch (error) {
      toast({
        title: "Xəta",
        description: "Sual göndərilə bilmədi",
        variant: "destructive"
      })
    } finally {
      setIsSubmitting(false)
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

  if (showSuccessAlert) {
    return (
      <DashboardLayout>
        <div className="max-w-2xl mx-auto">
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            className="text-center py-12"
          >
            <div className="w-20 h-20 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-6">
              <CheckCircle className="w-10 h-10 text-green-600" />
            </div>
            <h1 className="text-3xl font-bold text-gray-900 mb-4">Sual Uğurla Göndərildi!</h1>
            <p className="text-gray-600 mb-8 leading-relaxed">
              Sualınız moderasiyanın baxması üçün göndərildi. Təsdiqləndiyi zaman həm siz, həm də digər istifadəçilər onu görə biləcək.
            </p>
            
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-8">
              <h3 className="font-semibold text-blue-900 mb-2">Növbəti Addımlar:</h3>
              <ul className="text-sm text-blue-800 space-y-1 text-left">
                <li>• Moderatorlar sualınızı 24-48 saat ərzində yoxlayacaq</li>
                <li>• Təsdiqləndiyi zaman e-poçt bildirişi alacaqsınız</li>
                <li>• Sualınız icma üçün əlçatan olacaq</li>
                <li>• Digər istifadəçilər onu öz testlərində istifadə edə biləcək</li>
              </ul>
            </div>

            <div className="flex gap-4 justify-center">
              <Button asChild variant="outline">
                <Link href="/questions">
                  <ArrowLeft className="w-4 h-4 mr-2" />
                  Sualları Gör
                </Link>
              </Button>
              <Button asChild>
                <Link href="/questions/submit">
                  <Plus className="w-4 h-4 mr-2" />
                  Başqa Sual Əlavə Et
                </Link>
              </Button>
            </div>
          </motion.div>
        </div>
      </DashboardLayout>
    )
  }

  return (
    <DashboardLayout>
      <div className="max-w-4xl mx-auto space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Sual Paylaş</h1>
            <p className="text-gray-600 mt-2">İcma ilə sualınızı paylaşın</p>
          </div>
          
          <div className="flex gap-3">
            <Button variant="outline" onClick={() => setIsPreview(!isPreview)}>
              <Eye className="w-4 h-4 mr-2" />
              {isPreview ? "Redaktə Et" : "Önizləmə"}
            </Button>
            <Button asChild variant="outline">
              <Link href="/questions">
                <ArrowLeft className="w-4 h-4 mr-2" />
                Geriyə
              </Link>
            </Button>
          </div>
        </div>

        {!isPreview ? (
          /* Form Mode */
          <div className="space-y-6">
            {/* Basic Information */}
            <Card>
              <CardHeader>
                <CardTitle>Sual Məlumatları</CardTitle>
                <CardDescription>Sualınızın əsas məlumatlarını daxil edin</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-2">
                  <Label htmlFor="title">Sual Başlığı *</Label>
                  <Input
                    id="title"
                    placeholder="Məs: JavaScript Array Methods"
                    value={questionData.title}
                    onChange={(e) => setQuestionData(prev => ({ ...prev, title: e.target.value }))}
                  />
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="category">Kateqoriya *</Label>
                    <Select
                      value={questionData.category}
                      onValueChange={(value) => setQuestionData(prev => ({ ...prev, category: value }))}
                    >
                      <SelectTrigger>
                        <SelectValue placeholder="Kateqoriya seçin" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="Programlaşdırma">Programlaşdırma</SelectItem>
                        <SelectItem value="Riyaziyyat">Riyaziyyat</SelectItem>
                        <SelectItem value="Fen Elmləri">Fen Elmləri</SelectItem>
                        <SelectItem value="Dizayn">Dizayn</SelectItem>
                        <SelectItem value="Dil">Dil</SelectItem>
                        <SelectItem value="Tarix">Tarix</SelectItem>
                        <SelectItem value="İqtisadiyyat">İqtisadiyyat</SelectItem>
                        <SelectItem value="Digər">Digər</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="difficulty">Çətinlik Dərəcəsi *</Label>
                    <Select
                      value={questionData.difficulty}
                      onValueChange={(value: "easy" | "medium" | "hard") => setQuestionData(prev => ({ ...prev, difficulty: value }))}
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
                </div>

                <div className="space-y-2">
                  <Label htmlFor="question_type">Sual Növü *</Label>
                  <Select
                    value={questionData.question_type}
                    onValueChange={(value: "multiple_choice" | "open_ended") => setQuestionData(prev => ({ ...prev, question_type: value }))}
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
              </CardContent>
            </Card>

            {/* Question Content */}
            <Card>
              <CardHeader>
                <CardTitle>Sual Məzmunu</CardTitle>
                <CardDescription>Sualınızın mətnini və riyazi formulları daxil edin</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-2">
                  <Label htmlFor="question_text">Sual Mətni *</Label>
                  <MathInput
                    value={questionData.question_text}
                    onChange={(value) => setQuestionData(prev => ({ ...prev, question_text: value }))}
                    placeholder="Sualınızı buraya yazın... (LaTeX dəstəklənir: $x^2$, $$\frac{a}{b}$$)"
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="math_formula">Riyazi Formula (İstəyə görə)</Label>
                  <MathInput
                    value={questionData.math_formula}
                    onChange={(value) => setQuestionData(prev => ({ ...prev, math_formula: value }))}
                    placeholder="Riyazi formula daxil edin... Məs: $f(x) = x^2 + 2x + 1$"
                  />
                  {questionData.math_formula && (
                    <div className="bg-blue-50 p-3 rounded border">
                      <p className="text-sm text-blue-700 mb-1">Önizləmə:</p>
                      <MathTextRenderer text={questionData.math_formula} />
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>

            {/* Multiple Choice Options */}
            {questionData.question_type === "multiple_choice" && (
              <Card>
                <CardHeader>
                  <CardTitle>Cavab Variantları</CardTitle>
                  <CardDescription>Sualınız üçün cavab variantlarını əlavə edin</CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  {questionData.options.map((option, index) => (
                    <div key={index} className="space-y-2 p-3 border rounded-lg">
                      <div className="flex items-center gap-3">
                        <input
                          type="checkbox"
                          checked={option.is_correct}
                          onChange={(e) => updateOption(index, "is_correct", e.target.checked)}
                          className="w-4 h-4 text-blue-600 rounded focus:ring-blue-500"
                        />
                        <div className="flex-1">
                          <MathInput
                            placeholder={`Variant ${index + 1} (LaTeX: $x^2$)`}
                            value={option.text}
                            onChange={(value) => updateOption(index, "text", value)}
                          />
                        </div>
                        {questionData.options.length > 2 && (
                          <Button type="button" variant="ghost" size="sm" onClick={() => removeOption(index)}>
                            <Trash2 className="w-4 h-4" />
                          </Button>
                        )}
                      </div>
                      {option.text && /\$.*?\$|\\\(.*?\\\)/.test(option.text) && (
                        <div className="ml-7 bg-gray-50 p-2 rounded text-sm">
                          <span className="text-gray-600">Önizləmə: </span>
                          <MathTextRenderer text={option.text} />
                        </div>
                      )}
                    </div>
                  ))}
                  
                  <Button
                    type="button"
                    variant="outline"
                    onClick={addOption}
                    disabled={questionData.options.length >= 6}
                    className="w-full"
                  >
                    <Plus className="w-4 h-4 mr-2" />
                    Variant Əlavə Et
                  </Button>
                </CardContent>
              </Card>
            )}

            {/* Open Ended Answers */}
            {questionData.question_type === "open_ended" && (
              <Card>
                <CardHeader>
                  <CardTitle>Gözlənilən Cavablar</CardTitle>
                  <CardDescription>Düzgün cavabları və açar sözləri daxil edin</CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="space-y-3">
                    <Label>Gözlənilən Cavablar *</Label>
                    {questionData.expected_answers.map((answer, index) => (
                      <div key={index} className="flex gap-2">
                        <MathInput
                          placeholder={`Cavab ${index + 1}`}
                          value={answer}
                          onChange={(value) => updateExpectedAnswer(index, value)}
                          className="flex-1"
                        />
                        {questionData.expected_answers.length > 1 && (
                          <Button type="button" variant="ghost" size="sm" onClick={() => removeExpectedAnswer(index)}>
                            <Trash2 className="w-4 h-4" />
                          </Button>
                        )}
                      </div>
                    ))}
                    <Button type="button" variant="outline" onClick={addExpectedAnswer} className="w-full">
                      <Plus className="w-4 h-4 mr-2" />
                      Cavab Əlavə Et
                    </Button>
                  </div>

                  <div className="space-y-3">
                    <Label>Açar Sözlər (İstəyə görə)</Label>
                    {questionData.keywords.map((keyword, index) => (
                      <div key={index} className="flex gap-2">
                        <Input
                          placeholder={`Açar söz ${index + 1}`}
                          value={keyword}
                          onChange={(e) => updateKeyword(index, e.target.value)}
                          className="flex-1"
                        />
                        {questionData.keywords.length > 1 && (
                          <Button type="button" variant="ghost" size="sm" onClick={() => removeKeyword(index)}>
                            <Trash2 className="w-4 h-4" />
                          </Button>
                        )}
                      </div>
                    ))}
                    <Button type="button" variant="outline" onClick={addKeyword} className="w-full">
                      <Plus className="w-4 h-4 mr-2" />
                      Açar Söz Əlavə Et
                    </Button>
                  </div>
                </CardContent>
              </Card>
            )}

            {/* Additional Information */}
            <Card>
              <CardHeader>
                <CardTitle>Əlavə Məlumatlar</CardTitle>
                <CardDescription>Açıqlama, etiketlər və paylaşım ayarları</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-2">
                  <Label htmlFor="explanation">Açıqlama (İstəyə görə)</Label>
                  <Textarea
                    id="explanation"
                    placeholder="Sualın cavabı üçün açıqlama yazın..."
                    rows={3}
                    value={questionData.explanation}
                    onChange={(e) => setQuestionData(prev => ({ ...prev, explanation: e.target.value }))}
                  />
                </div>

                <div className="space-y-2">
                  <Label>Etiketlər</Label>
                  <div className="flex gap-2">
                    <Input
                      placeholder="Etiket əlavə et..."
                      value={currentTag}
                      onChange={(e) => setCurrentTag(e.target.value)}
                      onKeyPress={(e) => e.key === 'Enter' && (e.preventDefault(), addTag())}
                      className="flex-1"
                    />
                    <Button type="button" onClick={addTag} variant="outline">
                      <Plus className="w-4 h-4" />
                    </Button>
                  </div>
                  {questionData.tags.length > 0 && (
                    <div className="flex flex-wrap gap-2 mt-2">
                      {questionData.tags.map((tag) => (
                        <Badge key={tag} variant="secondary" className="cursor-pointer" onClick={() => removeTag(tag)}>
                          #{tag} <Trash2 className="w-3 h-3 ml-1" />
                        </Badge>
                      ))}
                    </div>
                  )}
                </div>

                <div className="flex items-center justify-between">
                  <div>
                    <Label>Hamı Üçün Açıq</Label>
                    <p className="text-sm text-gray-600">Sualı bütün istifadəçilər görə bilər</p>
                  </div>
                  <Switch
                    checked={questionData.is_public}
                    onCheckedChange={(checked) => setQuestionData(prev => ({ ...prev, is_public: checked }))}
                  />
                </div>
              </CardContent>
            </Card>
          </div>
        ) : (
          /* Preview Mode */
          <Card>
            <CardHeader>
              <CardTitle>Sual Önizləməsi</CardTitle>
              <CardDescription>Sualınızın necə görünəcəyini yoxlayın</CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="space-y-4">
                <div className="flex items-center gap-2">
                  <Badge className={getDifficultyColor(questionData.difficulty)}>
                    {questionData.difficulty === "easy" ? "Asan" : questionData.difficulty === "medium" ? "Orta" : "Çətin"}
                  </Badge>
                  <Badge variant="outline">
                    {questionData.question_type === "multiple_choice" ? "Çoxvariantlı" : "Açıq cavab"}
                  </Badge>
                  <Badge variant="outline">{questionData.category}</Badge>
                </div>

                <h2 className="text-2xl font-bold">{questionData.title || "Sual başlığı"}</h2>
                
                <div className="bg-gray-50 p-4 rounded-lg">
                  <MathTextRenderer text={questionData.question_text || "Sual mətni buraya gələcək"} />
                </div>

                {questionData.math_formula && (
                  <div className="bg-blue-50 p-4 rounded-lg">
                    <p className="text-blue-700 font-medium mb-2">Formula:</p>
                    <MathTextRenderer text={questionData.math_formula} />
                  </div>
                )}

                {questionData.question_type === "multiple_choice" && (
                  <div className="space-y-2">
                    <p className="font-medium">Variantlar:</p>
                    {questionData.options.filter(opt => opt.text.trim()).map((option, index) => (
                      <div key={index} className="flex items-center gap-3 p-2 border rounded">
                        <input type="radio" name="preview" disabled />
                        <span className={option.is_correct ? "font-medium text-green-700" : ""}>
                          <MathTextRenderer text={option.text} />
                        </span>
                        {option.is_correct && <Check className="w-4 h-4 text-green-600" />}
                      </div>
                    ))}
                  </div>
                )}

                {questionData.question_type === "open_ended" && (
                  <div className="space-y-3">
                    <Textarea placeholder="Cavabınızı buraya yazın..." rows={3} disabled />
                    {questionData.expected_answers.filter(ans => ans.trim()).length > 0 && (
                      <div className="bg-green-50 p-3 rounded">
                        <p className="text-green-700 font-medium mb-2">Gözlənilən cavablar:</p>
                        <ul className="list-disc list-inside text-sm text-green-700">
                          {questionData.expected_answers.filter(ans => ans.trim()).map((answer, index) => (
                            <li key={index}><MathTextRenderer text={answer} /></li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </div>
                )}

                {questionData.explanation && (
                  <div className="bg-blue-50 p-3 rounded">
                    <p className="text-blue-700 font-medium mb-1">Açıqlama:</p>
                    <p className="text-blue-700 text-sm">{questionData.explanation}</p>
                  </div>
                )}

                {questionData.tags.length > 0 && (
                  <div className="flex flex-wrap gap-2">
                    {questionData.tags.map((tag) => (
                      <Badge key={tag} variant="secondary">#{tag}</Badge>
                    ))}
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        )}

        {/* Action Buttons */}
        <div className="flex justify-between items-center">
          <Button variant="outline" asChild>
            <Link href="/questions">
              <ArrowLeft className="w-4 h-4 mr-2" />
              Ləğv Et
            </Link>
          </Button>

          <div className="flex gap-3">
            <Button
              variant="outline"
              onClick={() => setIsPreview(!isPreview)}
            >
              <Eye className="w-4 h-4 mr-2" />
              {isPreview ? "Redaktə Et" : "Önizləmə"}
            </Button>
            <Button
              onClick={handleSubmit}
              disabled={isSubmitting}
              className="bg-gradient-to-r from-green-600 to-blue-600 hover:from-green-700 hover:to-blue-700"
            >
              {isSubmitting ? (
                <>
                  <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin mr-2" />
                  Göndərilir...
                </>
              ) : (
                <>
                  <Send className="w-4 h-4 mr-2" />
                  Sualı Göndər
                </>
              )}
            </Button>
          </div>
        </div>
      </div>
    </DashboardLayout>
  )
}