# 🔧 SQUIZ - Teknik Referans ve API Dokümantasyonu

## 📋 İçindekiler
1. [API Referansı](#api-referansı)
2. [Veritabanı Şeması](#veritabanı-şeması)
3. [Sistem Mimarisi](#sistem-mimarisi)
4. [Güvenlik Protokolleri](#güvenlik-protokolleri)
5. [Performans Optimizasyonları](#performans-optimizasyonları)
6. [Hata Yönetimi](#hata-yönetimi)
7. [Test Stratejileri](#test-stratejileri)
8. [Deployment Konfigürasyonları](#deployment-konfigürasyonları)

---

## 🔌 API Referansı

### Base URL
\`\`\`
Development: http://localhost:8001/api
Production: https://api.squiz.com/api
\`\`\`

### Kimlik Doğrulama
Tüm korumalı endpointler için JWT token gereklidir:
\`\`\`
Authorization: Bearer <jwt_token>
\`\`\`

---

## 🔐 Authentication Endpoints

### POST /api/auth/register
**Yeni kullanıcı kaydı**

**Request Body:**
\`\`\`json
{
  "email": "string (email format, required)",
  "name": "string (min: 2, max: 100, required)",
  "password": "string (min: 6, max: 128, required)"
}
\`\`\`

**Response (201):**
\`\`\`json
{
  "id": "string",
  "email": "string",
  "name": "string",
  "role": "user",
  "is_active": true,
  "created_at": "2025-01-29T10:00:00Z",
  "is_private": false,
  "follower_count": 0,
  "following_count": 0
}
\`\`\`

**Error Responses:**
- `400`: Email zaten kayıtlı
- `422`: Validasyon hatası

---

### POST /api/auth/login
**Kullanıcı girişi**

**Request Body:**
\`\`\`json
{
  "email": "string (email format, required)",
  "password": "string (required)"
}
\`\`\`

**Response (200):**
\`\`\`json
{
  "access_token": "string",
  "token_type": "bearer",
  "user": {
    "id": "string",
    "email": "string",
    "name": "string",
    "role": "user|admin",
    "is_active": true,
    "created_at": "2025-01-29T10:00:00Z",
    "is_private": false,
    "follower_count": 0,
    "following_count": 0
  }
}
\`\`\`

**Error Responses:**
- `401`: Geçersiz email veya şifre

---

## 📝 Quiz Endpoints

### GET /api/quizzes
**Yayınlanmış quizleri listele**

**Query Parameters:**
- `subject` (optional): Konu bazında filtreleme
- `category` (optional): Kategori bazında filtreleme
- `limit` (optional, default: 50): Sonuç limiti
- `offset` (optional, default: 0): Sayfalama offset'i

**Response (200):**
\`\`\`json
[
  {
    "id": "string",
    "title": "string",
    "description": "string",
    "category": "string",
    "subject": "string",
    "subcategory": "string",
    "total_questions": 0,
    "total_points": 0,
    "total_attempts": 0,
    "average_score": 0.0,
    "min_pass_percentage": 60.0,
    "time_limit_minutes": null,
    "created_at": "2025-01-29T10:00:00Z",
    "quiz_owner_type": "admin|user",
    "is_public": true,
    "is_draft": false
  }
]
\`\`\`

---

### GET /api/quiz/{quiz_id}
**Quiz detaylarını getir**

**Path Parameters:**
- `quiz_id`: Quiz UUID'si

**Response (200):**
\`\`\`json
{
  "id": "string",
  "title": "string",
  "description": "string",
  "category": "string",
  "subject": "string",
  "subcategory": "string",
  "questions": [
    {
      "id": "string",
      "question_text": "string",
      "question_type": "multiple_choice|open_ended",
      "options": [
        {
          "text": "string",
          "is_correct": false
        }
      ],
      "multiple_correct": false,
      "open_ended_answer": {
        "expected_answers": ["string"],
        "keywords": ["string"],
        "case_sensitive": false,
        "partial_credit": true
      },
      "image_url": "string (base64)",
      "pdf_url": "string (base64)",
      "difficulty": "easy|medium|hard",
      "points": 1,
      "explanation": "string"
    }
  ],
  "total_questions": 0,
  "total_points": 0,
  "min_pass_percentage": 60.0,
  "time_limit_minutes": null,
  "shuffle_questions": false,
  "shuffle_options": false,
  "created_at": "2025-01-29T10:00:00Z"
}
\`\`\`

**Error Responses:**
- `404`: Quiz bulunamadı
- `403`: Erişim izni yok (draft quiz)

---

## ⏱️ Real-time Quiz Session Endpoints

### POST /api/quiz-session/start
**Quiz oturumu başlat**

**Headers:** Authorization required

**Request Body:**
\`\`\`json
{
  "quiz_id": "string (required)",
  "time_limit_minutes": "number (optional)"
}
\`\`\`

**Response (201):**
\`\`\`json
{
  "id": "string",
  "quiz_id": "string",
  "quiz_title": "string",
  "user_id": "string",
  "status": "pending",
  "time_limit_minutes": null,
  "total_questions": 0,
  "created_at": "2025-01-29T10:00:00Z"
}
\`\`\`

---

## 💬 Q&A Forum Endpoints

### GET /api/questions
**Soruları listele**

**Query Parameters:**
- `limit` (default: 20): Sayfa başına sonuç
- `offset` (default: 0): Sayfalama offset'i
- `subject` (optional): Konu filtreleme
- `subcategory` (optional): Alt kategori filtreleme
- `status` (optional): open|answered|closed

**Response (200):**
\`\`\`json
{
  "questions": [
    {
      "id": "string",
      "title": "string",
      "content": "string",
      "image": "string (base64, optional)",
      "user_id": "string",
      "user_name": "string",
      "subject": "string",
      "subcategory": "string",
      "tags": ["string"],
      "upvotes": 0,
      "downvotes": 0,
      "status": "open|answered|closed",
      "answer_count": 0,
      "has_accepted_answer": false,
      "is_pinned": false,
      "created_at": "2025-01-29T10:00:00Z",
      "updated_at": "2025-01-29T10:00:00Z"
    }
  ],
  "total": 100,
  "limit": 20,
  "offset": 0,
  "has_more": true
}
\`\`\`

---

## 🗄️ Veritabanı Şeması

### Users Collection
\`\`\`javascript
{
  _id: ObjectId,
  id: String, // UUID
  email: String, // Unique
  name: String,
  password: String, // Hashed with bcrypt
  role: String, // "admin" | "user"
  is_active: Boolean,
  created_at: Date,
  updated_at: Date,
  
  // Privacy and social
  is_private: Boolean,
  follower_count: Number,
  following_count: Number,
  
  // Indexes
  indexes: [
    { email: 1 }, // Unique
    { id: 1 }, // Unique
    { role: 1 },
    { created_at: -1 }
  ]
}
\`\`\`

---

### Quizzes Collection
\`\`\`javascript
{
  _id: ObjectId,
  id: String, // UUID
  title: String,
  description: String,
  category: String,
  subject: String,
  subcategory: String,
  questions: [
    {
      id: String, // UUID
      question_text: String,
      question_type: String, // "multiple_choice" | "open_ended"
      options: [
        {
          text: String,
          is_correct: Boolean
        }
      ],
      multiple_correct: Boolean,
      open_ended_answer: {
        expected_answers: [String],
        keywords: [String],
        case_sensitive: Boolean,
        partial_credit: Boolean
      },
      image_url: String, // Base64
      pdf_url: String, // Base64
      difficulty: String, // "easy" | "medium" | "hard"
      points: Number,
      is_mandatory: Boolean,
      explanation: String,
      created_at: Date,
      updated_at: Date
    }
  ],
  created_by: String, // User ID
  created_at: Date,
  updated_at: Date,
  total_questions: Number,
  total_points: Number,
  is_active: Boolean,
  is_public: Boolean,
  allowed_users: [String], // User IDs
  total_attempts: Number,
  average_score: Number,
  
  // Ownership
  quiz_owner_type: String, // "admin" | "user"
  quiz_owner_id: String,
  
  // Settings
  min_pass_percentage: Number,
  time_limit_minutes: Number,
  shuffle_questions: Boolean,
  shuffle_options: Boolean,
  
  // Publishing
  is_draft: Boolean,
  preview_token: String,
  
  // Indexes
  indexes: [
    { id: 1 }, // Unique
    { created_by: 1 },
    { subject: 1 },
    { category: 1 },
    { is_draft: 1 },
    { is_public: 1 },
    { created_at: -1 },
    { "questions.id": 1 }
  ]
}
\`\`\`

---

*[Teknik dokümantasyon devam ediyor... Tam içerik için dosyayı indirin]*
