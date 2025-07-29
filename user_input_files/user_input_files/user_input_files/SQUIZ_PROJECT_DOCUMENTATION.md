# 📚 TestHub/Squiz - Complete Project Documentation

## 🎯 Project Overview

**TestHub** (originally Squiz) is a comprehensive online quiz and assessment platform built with modern web technologies. It serves as a complete educational ecosystem for creating, managing, and analyzing quizzes with advanced features like real-time sessions, community forums, and detailed analytics.

### 🏗️ Core Architecture

```
TestHub/Squiz Architecture
├── Frontend: Next.js 14 + TypeScript + Tailwind CSS
├── UI Components: Radix UI + Custom Components
├── Authentication: JWT-based with Role Management
├── State Management: React Context + Custom Hooks
├── Animations: Framer Motion
├── Styling: Tailwind CSS + CSS Variables
└── Build System: Next.js with TypeScript
```

---

## 📋 Feature Inventory (Numbered System)

### 1. Authentication & User Management
- **1.1** User Registration & Login System
- **1.2** JWT Token-based Authentication
- **1.3** Role-based Access Control (Admin/User)
- **1.4** Password Validation & Security
- **1.5** Profile Management
- **1.6** Avatar & Bio Management
- **1.7** Privacy Settings
- **1.8** Social Following System

### 2. Quiz Creation & Management
- **2.1** Advanced Quiz Builder
- **2.2** Multiple Question Types:
  - **2.2.1** Multiple Choice Questions
  - **2.2.2** Open-ended Questions
  - **2.2.3** Image-based Questions
  - **2.2.4** Mathematical Formula Support (LaTeX)
- **2.3** Question Difficulty Levels (Easy/Medium/Hard)
- **2.4** Point System & Scoring
- **2.5** Question Randomization
- **2.6** Time Limits & Auto-submission
- **2.7** Draft & Publish System
- **2.8** Category & Subject Organization
- **2.9** Image Upload & Management
- **2.10** Question Explanation System

### 3. Quiz Taking Experience
- **3.1** Real-time Quiz Sessions
- **3.2** Live Timer & Countdown
- **3.3** Progress Tracking
- **3.4** Auto-save Functionality
- **3.5** Session Pause/Resume
- **3.6** Instant Score Calculation
- **3.7** Detailed Results & Analytics
- **3.8** Answer Review & Explanations

### 4. Dashboard & Analytics
- **4.1** Personal Dashboard
- **4.2** Quiz Statistics & Performance
- **4.3** Recent Activity Tracking
- **4.4** Achievement System
- **4.5** Progress Charts & Graphs
- **4.6** Category-wise Performance
- **4.7** Time-based Analytics
- **4.8** Comparison & Ranking

### 5. Q&A Forum System
- **5.1** Community Question Posting
- **5.2** Answer & Reply System
- **5.3** Upvote/Downvote Mechanism
- **5.4** Best Answer Selection
- **5.5** Category & Tag System
- **5.6** Search & Filter Functionality
- **5.7** Image Attachments
- **5.8** Solved/Unsolved Status
- **5.9** Popular Posts Tracking

### 6. Admin Panel
- **6.1** User Management
- **6.2** Quiz Oversight & Moderation
- **6.3** System Analytics
- **6.4** Content Moderation
- **6.5** Report Management
- **6.6** Data Export Functionality
- **6.7** System Health Monitoring
- **6.8** Role & Permission Management

### 7. UI/UX Components
- **7.1** Responsive Layout System
- **7.2** Dark/Light Theme Support
- **7.3** Interactive Animations
- **7.4** Loading States & Skeletons
- **7.5** Toast Notifications
- **7.6** Modal & Dialog System
- **7.7** Form Validation & Error Handling
- **7.8** Accessibility Features

---

## 🗂️ Complete File Structure Analysis

```
squiz-project/
├── 📄 package.json                 # Dependencies & Scripts
├── 📄 next.config.mjs             # Next.js Configuration
├── 📄 tailwind.config.ts          # Tailwind CSS Configuration
├── 📄 tsconfig.json               # TypeScript Configuration
├── 📄 components.json             # Shadcn/UI Configuration
├── 📄 postcss.config.mjs          # PostCSS Configuration
├── 📄 README.md                   # Project README
├── 📄 test_result.md              # Testing Documentation
│
├── 📁 app/                        # Next.js 14 App Router
│   ├── 📄 layout.tsx              # Root Layout
│   ├── 📄 page.tsx                # Home Page (Landing)
│   ├── 📄 globals.css             # Global Styles
│   │
│   ├── 📁 api/                    # API Routes
│   │   ├── 📁 auth/               # Authentication APIs
│   │   │   ├── 📁 login/          # Login Endpoint
│   │   │   ├── 📁 register/       # Registration Endpoint
│   │   │   └── 📁 me/             # User Profile Endpoint
│   │   ├── 📁 dashboard/          # Dashboard APIs
│   │   ├── 📁 forum/              # Forum APIs
│   │   ├── 📁 admin/              # Admin APIs
│   │   ├── 📁 profile/            # Profile APIs
│   │   └── 📁 upload/             # File Upload APIs
│   │
│   ├── 📁 dashboard/              # User Dashboard
│   │   └── 📄 page.tsx
│   │
│   ├── 📁 quiz/                   # Quiz Management
│   │   ├── 📁 create/             # Quiz Creation
│   │   └── 📁 [id]/               # Individual Quiz
│   │
│   ├── 📁 quizzes/                # Quiz Listing
│   │   └── 📄 page.tsx
│   │
│   ├── 📁 forum/                  # Q&A Forum
│   │   ├── 📄 page.tsx
│   │   └── 📁 post/[id]/          # Individual Forum Post
│   │
│   ├── 📁 admin/                  # Admin Panel
│   │   ├── 📄 page.tsx
│   │   ├── 📁 profile/
│   │   └── 📁 settings/
│   │
│   └── 📁 profile/                # User Profile
│       └── 📄 page.tsx
│
├── 📁 components/                 # React Components
│   ├── 📄 theme-provider.tsx     # Theme Context Provider
│   ├── 📄 MathEditor.tsx          # Mathematical Formula Editor
│   │
│   ├── 📁 ui/                     # Shadcn/UI Components
│   │   ├── 📄 button.tsx          # Button Component
│   │   ├── 📄 input.tsx           # Input Component
│   │   ├── 📄 card.tsx            # Card Component
│   │   ├── 📄 dialog.tsx          # Dialog/Modal Component
│   │   ├── 📄 tabs.tsx            # Tabs Component
│   │   ├── 📄 badge.tsx           # Badge Component
│   │   ├── 📄 avatar.tsx          # Avatar Component
│   │   ├── 📄 progress.tsx        # Progress Bar
│   │   ├── 📄 select.tsx          # Select Dropdown
│   │   ├── 📄 textarea.tsx        # Textarea Component
│   │   ├── 📄 switch.tsx          # Toggle Switch
│   │   ├── 📄 alert.tsx           # Alert Component
│   │   ├── 📄 toast.tsx           # Toast Notification
│   │   └── [30+ more UI components]
│   │
│   ├── 📁 auth/                   # Authentication Components
│   │   └── 📄 AuthModal.tsx       # Login/Register Modal
│   │
│   └── 📁 layout/                 # Layout Components
│       └── 📄 DashboardLayout.tsx # Dashboard Layout
│
├── 📁 hooks/                      # Custom React Hooks
│   ├── 📄 useAuth.tsx            # Authentication Hook
│   ├── 📄 use-toast.ts           # Toast Notification Hook
│   └── 📄 use-mobile.tsx         # Mobile Detection Hook
│
├── 📁 lib/                       # Utility Libraries
│   └── 📄 utils.ts               # Utility Functions
│
├── 📁 styles/                    # Additional Styles
│   └── 📄 globals.css            # Additional Global Styles
│
└── 📁 public/                    # Static Assets
    ├── 📄 placeholder.jpg        # Placeholder Images
    ├── 📄 placeholder-user.jpg
    ├── 📄 placeholder-logo.png
    └── 📄 placeholder.svg
```

---

## 🔧 Technology Stack Deep Dive

### Frontend Framework
- **Next.js 14**: Latest version with App Router
- **TypeScript**: Full type safety and modern JavaScript features
- **React 18**: Latest React with concurrent features

### UI & Styling
- **Tailwind CSS 3.4+**: Utility-first CSS framework
- **Radix UI**: Headless UI components with accessibility
- **Framer Motion**: Animation library for smooth interactions
- **Lucide React**: Modern icon library

### State Management
- **React Context**: Global state management
- **Custom Hooks**: Encapsulated business logic
- **Local Storage**: Client-side data persistence

### Development Tools
- **ESLint**: Code linting and quality
- **PostCSS**: CSS processing
- **PNPM**: Package manager for better performance

### Key Dependencies
```json
{
  "next": "14.2.16",
  "react": "^18",
  "typescript": "^5",
  "tailwindcss": "^3.4.17",
  "framer-motion": "latest",
  "lucide-react": "^0.454.0",
  "@radix-ui/react-*": "latest",
  "class-variance-authority": "^0.7.1",
  "clsx": "^2.1.1",
  "tailwind-merge": "^2.5.5"
}
```

---

## 📱 Feature Analysis by Page

### 1. Landing Page (`app/page.tsx`)
**Features:**
- Hero section with animated elements
- Feature showcase with icons and descriptions
- Statistics counter
- Testimonial section
- Pricing tiers
- Trust indicators and social proof
- Responsive design with mobile optimization

**Key Components:**
- Authentication modal integration
- Animated statistics
- Feature cards with hover effects
- Gradient backgrounds and modern design

### 2. Dashboard (`app/dashboard/page.tsx`)
**Features:**
- Welcome message with personalization
- Quick statistics overview
- Recent quiz activity
- Performance charts and graphs
- Quick action buttons
- Activity feed
- Achievement tracking

**Key Metrics Displayed:**
- Total quizzes taken
- Average score
- Recent attempts
- Time spent learning
- Achievement badges

### 3. Quiz Creator (`app/quiz/create/page.tsx`)
**Features:**
- Multi-step quiz creation wizard
- Rich text editor for questions
- Image upload and cropping
- Mathematical formula support (LaTeX)
- Multiple question types
- Difficulty level selection
- Point assignment
- Time limit configuration
- Preview functionality
- Draft saving

**Question Types:**
- Multiple choice (single/multiple correct)
- Open-ended text answers
- Image-based questions
- Mathematical formula questions

### 4. Forum System (`app/forum/page.tsx`)
**Features:**
- Question posting with rich content
- Category and tag system
- Search and filter functionality
- Upvote/downvote system
- Best answer selection
- Image attachments
- User reputation tracking
- Real-time updates

**Forum Stats:**
- Total posts
- Solved questions
- Popular topics
- Active contributors

### 5. Admin Panel (`app/admin/page.tsx`)
**Features:**
- System overview dashboard
- User management
- Quiz moderation
- Content oversight
- Analytics and reporting
- Data export functionality
- System health monitoring
- Role management

**Admin Capabilities:**
- User activation/deactivation
- Quiz approval/rejection
- Content moderation
- System statistics
- Data backup and export

---

## 🎨 Design System Elements

### Color Palette
```css
/* Primary Colors */
--blue-600: #2563eb
--purple-600: #9333ea
--green-600: #16a34a
--orange-600: #ea580c
--red-600: #dc2626

/* Gradients */
--gradient-primary: linear-gradient(to right, #2563eb, #9333ea)
--gradient-success: linear-gradient(to right, #16a34a, #10b981)
--gradient-warning: linear-gradient(to right, #f59e0b, #ea580c)

/* Neutral Colors */
--gray-50: #f9fafb
--gray-100: #f3f4f6
--gray-600: #4b5563
--gray-900: #111827
```

### Typography Scale
```css
/* Headings */
.text-3xl: 1.875rem (30px)
.text-2xl: 1.5rem (24px)
.text-xl: 1.25rem (20px)
.text-lg: 1.125rem (18px)

/* Body Text */
.text-base: 1rem (16px)
.text-sm: 0.875rem (14px)
.text-xs: 0.75rem (12px)

/* Font Weights */
.font-bold: 700
.font-semibold: 600
.font-medium: 500
.font-normal: 400
```

### Component Variants
```css
/* Button Variants */
.btn-primary: bg-gradient-primary + hover effects
.btn-secondary: bg-gray-100 + hover effects
.btn-outline: border + transparent bg
.btn-ghost: transparent + hover bg

/* Card Styles */
.card-default: white bg + shadow + rounded borders
.card-hover: scale transform + shadow increase
.card-gradient: gradient background variants

/* Badge Styles */
.badge-success: green background
.badge-warning: yellow background
.badge-error: red background
.badge-info: blue background
```

---

## 🔐 Authentication System

### User Roles & Permissions
```typescript
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
}
```

### Authentication Flow
1. **Registration**: Email + Password + Name validation
2. **Login**: JWT token generation and storage
3. **Session Management**: Token-based authentication
4. **Role Verification**: Route-level protection
5. **Profile Management**: Update user information
6. **Password Management**: Secure password changes

### Security Features
- Password strength validation
- JWT token expiration
- Role-based route protection
- Input sanitization
- CSRF protection ready

---

## 📊 Data Models & Interfaces

### Quiz Structure
```typescript
interface Quiz {
  id: string
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
  created_at: string
  total_attempts: number
  average_score: number
}
```

### Question Types
```typescript
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
```

### Forum Post Structure
```typescript
interface ForumPost {
  id: string
  title: string
  content: string
  author: {
    id: string
    name: string
    avatar?: string
    role: string
  }
  category: string
  tags: string[]
  created_at: string
  views: number
  likes: number
  replies: number
  is_solved: boolean
  is_pinned: boolean
  images?: string[]
}
```

---

## 🚀 Performance Optimizations

### Code Splitting
- Route-based code splitting with Next.js App Router
- Component-level lazy loading
- Dynamic imports for heavy components

### Image Optimization
- Next.js Image component for automatic optimization
- WebP format support
- Responsive image loading
- Lazy loading implementation

### Caching Strategy
- Static generation for public pages
- Server-side rendering for dynamic content
- Browser caching for static assets
- Memory optimization with React useMemo/useCallback

### Bundle Optimization
- Tree shaking for unused code elimination
- Minification in production builds
- Gzip compression ready
- Critical CSS inlining

---

## 🧪 Testing Framework

### Current Testing Setup
Based on `test_result.md`, the project includes:
- Frontend functionality testing
- Authentication flow testing
- Form validation testing
- Component integration testing

### Test Coverage Areas
- Authentication system
- Quiz creation workflow
- Forum functionality
- Admin panel operations
- Responsive design testing

---

## 🌐 Internationalization

### Language Support
- Primary: Turkish (tr)
- UI Text: Azerbaijani/Turkish mixed
- Date formatting: Turkish locale
- Number formatting: Turkish standards

### Localization Features
- Currency display (₼ - Azerbaijani Manat)
- Date/time formatting
- Text direction support
- Cultural adaptations

---

## 📈 Analytics & Tracking

### User Analytics
- Quiz completion rates
- Time spent on platform
- Popular categories
- User engagement metrics
- Performance trends

### System Analytics
- API response times
- Error rates
- User activity patterns
- Resource usage
- Feature adoption rates

---

## 🔧 Development Workflow

### Code Organization
- Feature-based folder structure
- Component composition patterns
- Custom hook abstractions
- Utility function libraries
- Type-safe development

### Build Process
1. TypeScript compilation
2. Tailwind CSS processing
3. Component tree shaking
4. Asset optimization
5. Production bundle generation

### Quality Assurance
- TypeScript type checking
- ESLint code analysis
- Prettier code formatting
- Component testing
- Integration testing

---

## 🚀 Deployment Considerations

### Production Readiness
- Environment variable management
- API endpoint configuration
- Database integration points
- CDN setup for static assets
- SSL certificate implementation

### Scalability Features
- Component modularity
- API abstraction layers
- State management optimization
- Performance monitoring hooks
- Error boundary implementation

---

This comprehensive documentation provides a complete overview of the TestHub/Squiz project structure, features, and implementation details. The numbered feature system allows for easy reference and systematic development tracking.
