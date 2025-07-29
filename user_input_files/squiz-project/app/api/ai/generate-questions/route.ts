import { type NextRequest, NextResponse } from "next/server"
import OpenAI from 'openai'

interface GenerateQuestionsRequest {
  topic: string
  difficulty: "easy" | "medium" | "hard"
  questionCount: number
  questionType: "multiple_choice" | "open_ended" | "mixed"
  language?: string
}

interface GeneratedQuestion {
  id: string
  question_text: string
  question_type: "multiple_choice" | "open_ended"
  options?: Array<{
    text: string
    is_correct: boolean
  }>
  multiple_correct: boolean
  open_ended_answer?: {
    expected_answers: string[]
    keywords: string[]
    case_sensitive: boolean
    partial_credit: boolean
  }
  difficulty: "easy" | "medium" | "hard"
  points: number
  explanation?: string
}

// OpenAI Configuration
const openai = new OpenAI({
  apiKey: process.env.OPENAI_API_KEY || '',
})

// Real AI question generation using ChatGPT
const generateAIQuestions = async (request: GenerateQuestionsRequest): Promise<GeneratedQuestion[]> => {
  const { topic, difficulty, questionCount, questionType, language = "az" } = request
  
  try {
    const prompt = `${language === "az" ? "Azərbaycan" : "Türk"} dilində "${topic}" mövzusunda ${questionCount} ədəd ${difficulty} səviyyəli sual yarat. 

Sual növü: ${questionType === "multiple_choice" ? "Çoxvariantlı" : questionType === "open_ended" ? "Açıq cavablı" : "Qarışıq"}

Zəhmət olmasa bu JSON formatında cavab ver:
{
  "questions": [
    {
      "question_text": "Sual mətni",
      "question_type": "multiple_choice",
      "options": [
        {"text": "Variant A", "is_correct": true},
        {"text": "Variant B", "is_correct": false},
        {"text": "Variant C", "is_correct": false},
        {"text": "Variant D", "is_correct": false}
      ],
      "explanation": "Cavab izahı",
      "difficulty": "${difficulty}",
      "points": 1
    }
  ]
}

Çoxvariantlı suallar üçün 4 variant ver, yalnız biri doğru olsun.
Açıq cavablı suallar üçün "open_ended_answer" field-i əlavə et:
{
  "expected_answers": ["Gözlənilən cavab 1", "Gözlənilən cavab 2"],
  "keywords": ["açar", "söz", "ləri"],
  "case_sensitive": false,
  "partial_credit": true
}

Mövzu haqqında keyfiyyətli, dərindən düşünülmüş suallar yarat.`

    const completion = await openai.chat.completions.create({
      model: "gpt-3.5-turbo",
      messages: [
        {
          role: "system",
          content: "Sən peşəkar test hazırlayıcısısan. Müxtəlif mövzularda keyfiyyətli, düşündürücü suallar yaratmaq sənin ixtisasındır."
        },
        {
          role: "user",
          content: prompt
        }
      ],
      temperature: 0.7,
      max_tokens: 3000
    })

    const aiResponse = completion.choices[0]?.message?.content
    if (!aiResponse) {
      throw new Error("AI cavab vermədi")
    }

    // Parse AI response
    const parsed = JSON.parse(aiResponse.replace(/```json\n|\n```/g, ''))
    
    // Add IDs and normalize data
    const questions = parsed.questions.map((q: any, index: number) => ({
      ...q,
      id: `ai-generated-${Date.now()}-${index}`,
      multiple_correct: false,
      points: difficulty === "easy" ? 1 : difficulty === "medium" ? 2 : 3
    }))

    return questions

  } catch (error) {
    console.error("OpenAI API xətası:", error)
    
    // Fallback to enhanced mock if API fails
    return generateEnhancedQuestions(request)
  }
}

// Mock AI question generation - fallback when OpenAI is not available
const generateMockQuestions = (request: GenerateQuestionsRequest): GeneratedQuestion[] => {
  const { topic, difficulty, questionCount, questionType } = request
  
  const mockQuestions: GeneratedQuestion[] = []
  
  for (let i = 1; i <= questionCount; i++) {
    const isMultipleChoice = questionType === "multiple_choice" || 
                            (questionType === "mixed" && i % 2 === 1)
    
    if (isMultipleChoice) {
      mockQuestions.push({
        id: `generated-${i}`,
        question_text: `${topic} haqqında sual ${i}: Bu mövzunun əsas xüsusiyyətlərindən biri hansıdır?`,
        question_type: "multiple_choice",
        options: [
          { text: `${topic}-nin birinci xüsusiyyəti`, is_correct: true },
          { text: `${topic}-nin yanlış xüsusiyyəti A`, is_correct: false },
          { text: `${topic}-nin yanlış xüsusiyyəti B`, is_correct: false },
          { text: `${topic}-nin yanlış xüsusiyyəti C`, is_correct: false }
        ],
        multiple_correct: false,
        difficulty,
        points: difficulty === "easy" ? 1 : difficulty === "medium" ? 2 : 3,
        explanation: `Bu sual ${topic} mövzusunun əsas anlayışlarını yoxlayır.`
      })
    } else {
      mockQuestions.push({
        id: `generated-${i}`,
        question_text: `${topic} haqqında açıq sual ${i}: ${topic} nədir və nə üçün vacibdir?`,
        question_type: "open_ended",
        multiple_correct: false,
        open_ended_answer: {
          expected_answers: [`${topic} əsas anlayışdır`, `${topic} vacib elementdir`],
          keywords: [topic.toLowerCase(), "vacib", "əsas"],
          case_sensitive: false,
          partial_credit: true
        },
        difficulty,
        points: difficulty === "easy" ? 2 : difficulty === "medium" ? 3 : 5,
        explanation: `Bu açıq sual ${topic} anlayışının dərinliyini yoxlayır.`
      })
    }
  }
  
  return mockQuestions
}

// Enhanced mock questions with better content
const generateEnhancedQuestions = (request: GenerateQuestionsRequest): GeneratedQuestion[] => {
  const { topic, difficulty, questionCount, questionType } = request
  
  const topicTemplates: Record<string, any> = {
    "JavaScript": {
      multiple_choice: [
        {
          question: "JavaScript-də dəyişən elan etmək üçün hansı açar sözləri istifadə olunur?",
          options: ["var, let, const", "variable, define", "set, get", "int, string"],
          correct: 0,
          explanation: "JavaScript-də dəyişən elan etmək üçün var, let və const açar sözləri istifadə olunur."
        },
        {
          question: "JavaScript-də funksiya necə müəyyən edilir?",
          options: ["function myFunc() {}", "def myFunc():", "func myFunc() {}", "method myFunc() {}"],
          correct: 0,
          explanation: "JavaScript-də funksiyanı function açar sözü ilə müəyyən edirik."
        }
      ],
      open_ended: [
        {
          question: "JavaScript-də 'hoisting' anlayışını izah edin.",
          keywords: ["hoisting", "dəyişən", "funksiya", "yuxarı", "scope"],
          expected: ["Hoisting JavaScript-də dəyişən və funksiya elanlarının scope-un yuxarısına qaldırılması prosesidir"]
        }
      ]
    },
    "Riyaziyyat": {
      multiple_choice: [
        {
          question: "2x + 5 = 15 tənliyində x-in qiyməti nədir?",
          options: ["5", "10", "7.5", "15"],
          correct: 0,
          explanation: "2x = 15 - 5 = 10, beləliklə x = 5"
        }
      ],
      open_ended: [
        {
          question: "Kvadrat tənliyin ümumi formasını yazın və diskriminantı izah edin.",
          keywords: ["ax²+bx+c", "diskriminant", "b²-4ac", "kök"],
          expected: ["Kvadrat tənliyin ümumi forması ax²+bx+c=0, diskriminant D=b²-4ac"]
        }
      ]
    }
  }
  
  const questions: GeneratedQuestion[] = []
  const templates = topicTemplates[topic] || topicTemplates["JavaScript"] // Default to JS if topic not found
  
  for (let i = 1; i <= questionCount; i++) {
    const isMultipleChoice = questionType === "multiple_choice" || 
                            (questionType === "mixed" && i % 2 === 1)
    
    if (isMultipleChoice && templates.multiple_choice) {
      const template = templates.multiple_choice[(i - 1) % templates.multiple_choice.length]
      questions.push({
        id: `ai-generated-${i}`,
        question_text: template.question,
        question_type: "multiple_choice",
        options: template.options.map((opt: string, idx: number) => ({
          text: opt,
          is_correct: idx === template.correct
        })),
        multiple_correct: false,
        difficulty,
        points: difficulty === "easy" ? 1 : difficulty === "medium" ? 2 : 3,
        explanation: template.explanation
      })
    } else if (templates.open_ended) {
      const template = templates.open_ended[(i - 1) % templates.open_ended.length]
      questions.push({
        id: `ai-generated-${i}`,
        question_text: template.question,
        question_type: "open_ended",
        multiple_correct: false,
        open_ended_answer: {
          expected_answers: template.expected,
          keywords: template.keywords,
          case_sensitive: false,
          partial_credit: true
        },
        difficulty,
        points: difficulty === "easy" ? 2 : difficulty === "medium" ? 3 : 5,
        explanation: `Bu sual ${topic} mövzusunda dərin bilgi tələb edir.`
      })
    }
  }
  
  return questions
}

export async function POST(request: NextRequest) {
  try {
    const requestData: GenerateQuestionsRequest = await request.json()
    
    // Validation
    if (!requestData.topic || !requestData.difficulty || !requestData.questionCount) {
      return NextResponse.json(
        { detail: "Mövzu, çətinlik və sual sayı tələb olunur" }, 
        { status: 400 }
      )
    }
    
    if (requestData.questionCount < 1 || requestData.questionCount > 20) {
      return NextResponse.json(
        { detail: "Sual sayı 1-20 arasında olmalıdır" }, 
        { status: 400 }
      )
    }
    
    // Generate questions using real AI (with fallback to enhanced mock)
    const generatedQuestions = await generateAIQuestions(requestData)
    
    return NextResponse.json({
      success: true,
      questions: generatedQuestions,
      metadata: {
        topic: requestData.topic,
        difficulty: requestData.difficulty,
        questionCount: generatedQuestions.length,
        generatedAt: new Date().toISOString()
      }
    })
    
  } catch (error) {
    console.error("AI sual generasiya xətası:", error)
    return NextResponse.json(
      { detail: "AI sual generasiya xətası" }, 
      { status: 500 }
    )
  }
}
