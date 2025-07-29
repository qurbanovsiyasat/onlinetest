# 👨‍💻 TestHub/Squiz - Complete Developer Guide

## 📋 Table of Contents
1. [Project Architecture](#project-architecture)
2. [Development Environment](#development-environment)
3. [Code Structure & Conventions](#code-structure--conventions)
4. [Component Development](#component-development)
5. [State Management](#state-management)
6. [API Integration](#api-integration)
7. [Testing Guidelines](#testing-guidelines)
8. [Performance Optimization](#performance-optimization)
9. [Deployment Guide](#deployment-guide)
10. [Troubleshooting](#troubleshooting)

---

## 🏗️ Project Architecture

### Overall System Architecture
```
TestHub/Squiz Architecture
├── 📱 Frontend (Next.js 14 + TypeScript)
│   ├── App Router (File-based routing)
│   ├── React Server Components
│   ├── Client Components with hooks
│   └── Static Generation + SSR
│
├── 🎨 UI Layer (Radix UI + Tailwind CSS)
│   ├── Design System Components
│   ├── Custom Business Components
│   ├── Animation Layer (Framer Motion)
│   └── Responsive Design System
│
├── 🔄 State Management
│   ├── React Context (Authentication)
│   ├── Custom Hooks (Business Logic)
│   ├── Local Storage (Persistence)
│   └── URL State (Navigation)
│
├── 🌐 API Layer (Mock + Future Backend)
│   ├── Next.js API Routes (Current)
│   ├── REST API Structure
│   ├── Authentication (JWT)
│   └── File Upload Handling
│
└── 🧪 Development Tools
    ├── TypeScript (Type Safety)
    ├── ESLint (Code Quality)
    ├── Prettier (Code Formatting)
    └── Tailwind CSS (Styling)
```

### Technology Stack Deep Dive

#### Core Framework
- **Next.js 14**: Latest with App Router for better performance and DX
- **TypeScript 5**: Full type safety with latest features
- **React 18**: Concurrent features and improved performance

#### Styling & UI
- **Tailwind CSS 3.4+**: Utility-first CSS framework
- **Radix UI**: Unstyled, accessible components
- **Framer Motion**: Declarative animations
- **CSS Variables**: Theme system foundation

#### Development Tools
- **PNPM**: Fast, disk space efficient package manager
- **ESLint**: Code linting with React and TypeScript rules
- **Prettier**: Opinionated code formatting
- **PostCSS**: CSS processing pipeline

---

## 🛠️ Development Environment

### Prerequisites Setup
```bash
# Install Node.js 18+ (using nvm)
nvm install 18
nvm use 18

# Install pnpm globally
npm install -g pnpm

# Verify installations
node --version    # Should be 18.x.x
pnpm --version    # Should be 8.x.x
```

### Project Setup
```bash
# Clone and setup
git clone <repository-url> testhub-squiz
cd testhub-squiz

# Install dependencies
pnpm install

# Start development server
pnpm dev

# Additional scripts
pnpm build        # Production build
pnpm start        # Production server
pnpm lint         # Run ESLint
pnpm type-check   # TypeScript checking
```

### VS Code Configuration
Create `.vscode/settings.json`:
```json
{
  "typescript.preferences.importModuleSpecifier": "relative",
  "editor.formatOnSave": true,
  "editor.defaultFormatter": "esbenp.prettier-vscode",
  "editor.codeActionsOnSave": {
    "source.fixAll.eslint": true
  },
  "files.associations": {
    "*.css": "tailwindcss"
  },
  "emmet.includeLanguages": {
    "javascript": "javascriptreact",
    "typescript": "typescriptreact"
  }
}
```

### Environment Variables
```bash
# .env.local
NEXT_PUBLIC_APP_NAME="TestHub"
NEXT_PUBLIC_APP_URL="http://localhost:3000"

# Development
NODE_ENV="development"
NEXT_PUBLIC_DEV_MODE="true"

# API Configuration (future)
# NEXT_PUBLIC_API_URL="http://localhost:8000"
# DATABASE_URL="postgresql://..."
# JWT_SECRET="your-jwt-secret"

# File Upload
# NEXT_PUBLIC_MAX_FILE_SIZE="5242880"
# UPLOAD_DIR="./public/uploads"

# Analytics (optional)
# NEXT_PUBLIC_GA_ID="GA-XXXXX"
```

---

## 📂 Code Structure & Conventions

### File Organization Patterns
```
app/
├── (auth)/                  # Route groups for organization
├── api/                     # API routes
│   ├── auth/               # Authentication endpoints
│   ├── quiz/               # Quiz management endpoints
│   └── upload/             # File upload endpoints
├── dashboard/              # Dashboard pages
├── quiz/                   # Quiz-related pages
│   ├── create/            # Quiz creation
│   └── [id]/              # Dynamic quiz pages
└── globals.css            # Global styles

components/
├── ui/                     # Reusable UI components (Shadcn)
├── auth/                   # Authentication components
├── layout/                 # Layout components
└── features/               # Feature-specific components

hooks/
├── useAuth.tsx            # Authentication hook
├── useLocalStorage.tsx    # Local storage hook
└── use-toast.ts           # Toast notifications

lib/
├── utils.ts               # Utility functions
├── validations.ts         # Zod schemas
└── constants.ts           # App constants
```

### Naming Conventions

#### Files and Folders
```bash
# Components (PascalCase)
components/AuthModal.tsx
components/QuizCreator.tsx

# Pages (lowercase)
app/dashboard/page.tsx
app/quiz/create/page.tsx

# Hooks (camelCase with 'use' prefix)
hooks/useAuth.tsx
hooks/useLocalStorage.tsx

# Utilities (camelCase)
lib/utils.ts
lib/api-client.ts

# Types (PascalCase with .types.ts)
types/auth.types.ts
types/quiz.types.ts
```

#### Variables and Functions
```typescript
// Variables (camelCase)
const userProfile = { ... }
const isLoading = false

// Functions (camelCase)
function fetchUserData() { ... }
const handleSubmit = () => { ... }

// Constants (SCREAMING_SNAKE_CASE)
const API_BASE_URL = "https://api.example.com"
const MAX_FILE_SIZE = 5 * 1024 * 1024

// Types and Interfaces (PascalCase)
interface User {
  id: string
  name: string
}

type QuizStatus = "draft" | "published" | "archived"
```

### Import/Export Conventions
```typescript
// Prefer named imports
import { useState, useEffect } from "react"
import { Button, Card } from "@/components/ui"

// Default imports for React components
import AuthModal from "@/components/auth/AuthModal"
import QuizCreator from "@/components/quiz/QuizCreator"

// Type imports
import type { User, Quiz } from "@/types"

// Utility imports with alias
import { cn, formatDate } from "@/lib/utils"

// Export patterns
export { Button } from "./button"
export type { ButtonProps } from "./button"
export default function HomePage() { ... }
```

---

## 🧩 Component Development

### Component Architecture Patterns

#### 1. Base UI Components (Radix + Shadcn/UI)
```typescript
// components/ui/button.tsx
import * as React from "react"
import { Slot } from "@radix-ui/react-slot"
import { cva, type VariantProps } from "class-variance-authority"
import { cn } from "@/lib/utils"

const buttonVariants = cva(
  "inline-flex items-center justify-center rounded-md text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50",
  {
    variants: {
      variant: {
        default: "bg-primary text-primary-foreground hover:bg-primary/90",
        destructive: "bg-destructive text-destructive-foreground hover:bg-destructive/90",
        outline: "border border-input bg-background hover:bg-accent hover:text-accent-foreground",
        secondary: "bg-secondary text-secondary-foreground hover:bg-secondary/80",
        ghost: "hover:bg-accent hover:text-accent-foreground",
        link: "text-primary underline-offset-4 hover:underline",
      },
      size: {
        default: "h-10 px-4 py-2",
        sm: "h-9 rounded-md px-3",
        lg: "h-11 rounded-md px-8",
        icon: "h-10 w-10",
      },
    },
    defaultVariants: {
      variant: "default",
      size: "default",
    },
  }
)

export interface ButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement>,
    VariantProps<typeof buttonVariants> {
  asChild?: boolean
}

const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant, size, asChild = false, ...props }, ref) => {
    const Comp = asChild ? Slot : "button"
    return (
      <Comp
        className={cn(buttonVariants({ variant, size, className }))}
        ref={ref}
        {...props}
      />
    )
  }
)
Button.displayName = "Button"

export { Button, buttonVariants }
```

#### 2. Feature Components
```typescript
// components/auth/AuthModal.tsx
"use client"

import { useState } from "react"
import { motion, AnimatePresence } from "framer-motion"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { useAuth } from "@/hooks/useAuth"

interface AuthModalProps {
  mode: "login" | "register"
  onClose: () => void
  onSwitchMode: (mode: "login" | "register") => void
}

export default function AuthModal({ mode, onClose, onSwitchMode }: AuthModalProps) {
  const [formData, setFormData] = useState({
    email: "",
    password: "",
    name: "",
  })
  const { login, register, isLoading } = useAuth()

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    try {
      if (mode === "login") {
        await login(formData.email, formData.password)
      } else {
        await register(formData.email, formData.password, formData.name)
      }
      onClose()
    } catch (error) {
      console.error("Authentication error:", error)
    }
  }

  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4"
        onClick={onClose}
      >
        <motion.div
          initial={{ opacity: 0, scale: 0.95, y: 20 }}
          animate={{ opacity: 1, scale: 1, y: 0 }}
          exit={{ opacity: 0, scale: 0.95, y: 20 }}
          onClick={(e) => e.stopPropagation()}
          className="w-full max-w-md bg-white rounded-lg shadow-xl"
        >
          {/* Modal content */}
          <form onSubmit={handleSubmit} className="p-6 space-y-4">
            {/* Form fields and submit button */}
          </form>
        </motion.div>
      </motion.div>
    </AnimatePresence>
  )
}
```

#### 3. Layout Components
```typescript
// components/layout/DashboardLayout.tsx
"use client"

import { useAuth } from "@/hooks/useAuth"
import { Button } from "@/components/ui/button"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"

interface DashboardLayoutProps {
  children: React.ReactNode
}

export default function DashboardLayout({ children }: DashboardLayoutProps) {
  const { user, logout } = useAuth()

  if (!user) {
    return <div>Loading...</div>
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white border-b border-gray-200">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <h1 className="text-xl font-bold">TestHub</h1>
              <nav className="hidden md:flex space-x-6">
                {/* Navigation items */}
              </nav>
            </div>
            
            <div className="flex items-center space-x-4">
              <Avatar>
                <AvatarImage src={user.avatar} />
                <AvatarFallback>{user.name.charAt(0)}</AvatarFallback>
              </Avatar>
              <Button variant="outline" onClick={logout}>
                Çıxış
              </Button>
            </div>
          </div>
        </div>
      </header>

      <main className="container mx-auto px-4 py-8">
        {children}
      </main>
    </div>
  )
}
```

### Component Best Practices

#### 1. TypeScript Interfaces
```typescript
// Always define proper interfaces
interface ComponentProps {
  title: string
  description?: string
  isLoading?: boolean
  onSubmit: (data: FormData) => void
  children: React.ReactNode
  className?: string
}

// Use generic types when needed
interface DataTableProps<T> {
  data: T[]
  columns: Column<T>[]
  onRowClick?: (row: T) => void
}
```

#### 2. Error Boundaries
```typescript
// components/ErrorBoundary.tsx
"use client"

import { Component, ErrorInfo, ReactNode } from "react"

interface Props {
  children: ReactNode
  fallback?: ReactNode
}

interface State {
  hasError: boolean
  error?: Error
}

export class ErrorBoundary extends Component<Props, State> {
  public state: State = {
    hasError: false
  }

  public static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error }
  }

  public componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error("Uncaught error:", error, errorInfo)
  }

  public render() {
    if (this.state.hasError) {
      return this.props.fallback || (
        <div className="p-6 text-center">
          <h2 className="text-lg font-semibold text-red-600">Something went wrong</h2>
          <p className="text-gray-600">Please refresh the page or try again later.</p>
        </div>
      )
    }

    return this.props.children
  }
}
```

#### 3. Performance Optimization
```typescript
// Use React.memo for expensive components
import { memo } from "react"

interface ExpensiveComponentProps {
  data: ComplexData[]
  calculations: number[]
}

const ExpensiveComponent = memo<ExpensiveComponentProps>(({ data, calculations }) => {
  // Expensive rendering logic
  return <div>{/* Complex rendering */}</div>
})

// Use useMemo for expensive calculations
import { useMemo } from "react"

function DataVisualization({ rawData }: { rawData: RawData[] }) {
  const processedData = useMemo(() => {
    return rawData.map(item => ({
      ...item,
      calculatedValue: expensiveCalculation(item)
    }))
  }, [rawData])

  return <Chart data={processedData} />
}

// Use useCallback for stable function references
import { useCallback } from "react"

function ParentComponent() {
  const handleSubmit = useCallback((data: FormData) => {
    // Handle submission
  }, [])

  return <ChildComponent onSubmit={handleSubmit} />
}
```

---

## 🔄 State Management

### Authentication State (Context Pattern)
```typescript
// hooks/useAuth.tsx
"use client"

import { createContext, useContext, useState, useEffect, ReactNode } from "react"

interface User {
  id: string
  email: string
  name: string
  role: "admin" | "user"
  is_active: boolean
}

interface AuthContextType {
  user: User | null
  isLoading: boolean
  login: (email: string, password: string) => Promise<void>
  register: (email: string, password: string, name: string) => Promise<void>
  logout: () => void
  updateProfile: (data: Partial<User>) => Promise<void>
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
        headers: { Authorization: `Bearer ${token}` }
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
      const response = await fetch("/api/auth/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password })
      })

      if (!response.ok) {
        const error = await response.json()
        throw new Error(error.detail || "Login failed")
      }

      const data = await response.json()
      localStorage.setItem("token", data.access_token)
      setUser(data.user)
    } finally {
      setIsLoading(false)
    }
  }

  const logout = () => {
    localStorage.removeItem("token")
    setUser(null)
  }

  return (
    <AuthContext.Provider value={{ user, isLoading, login, register, logout, updateProfile }}>
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
```

### Local Storage Hook
```typescript
// hooks/useLocalStorage.tsx
"use client"

import { useState, useEffect } from "react"

export function useLocalStorage<T>(key: string, initialValue: T) {
  const [storedValue, setStoredValue] = useState<T>(initialValue)

  useEffect(() => {
    try {
      const item = window.localStorage.getItem(key)
      if (item) {
        setStoredValue(JSON.parse(item))
      }
    } catch (error) {
      console.error(`Error reading localStorage key "${key}":`, error)
    }
  }, [key])

  const setValue = (value: T | ((val: T) => T)) => {
    try {
      const valueToStore = value instanceof Function ? value(storedValue) : value
      setStoredValue(valueToStore)
      window.localStorage.setItem(key, JSON.stringify(valueToStore))
    } catch (error) {
      console.error(`Error setting localStorage key "${key}":`, error)
    }
  }

  return [storedValue, setValue] as const
}
```

### Form State Management
```typescript
// hooks/useForm.tsx
import { useState, useCallback } from "react"

interface FormState<T> {
  values: T
  errors: Partial<Record<keyof T, string>>
  isSubmitting: boolean
}

interface UseFormOptions<T> {
  initialValues: T
  validate?: (values: T) => Partial<Record<keyof T, string>>
  onSubmit: (values: T) => Promise<void> | void
}

export function useForm<T extends Record<string, any>>({
  initialValues,
  validate,
  onSubmit
}: UseFormOptions<T>) {
  const [state, setState] = useState<FormState<T>>({
    values: initialValues,
    errors: {},
    isSubmitting: false
  })

  const setFieldValue = useCallback((field: keyof T, value: any) => {
    setState(prev => ({
      ...prev,
      values: { ...prev.values, [field]: value },
      errors: { ...prev.errors, [field]: undefined }
    }))
  }, [])

  const setFieldError = useCallback((field: keyof T, error: string) => {
    setState(prev => ({
      ...prev,
      errors: { ...prev.errors, [field]: error }
    }))
  }, [])

  const handleSubmit = useCallback(async (e: React.FormEvent) => {
    e.preventDefault()
    
    const errors = validate ? validate(state.values) : {}
    if (Object.keys(errors).length > 0) {
      setState(prev => ({ ...prev, errors }))
      return
    }

    setState(prev => ({ ...prev, isSubmitting: true }))
    try {
      await onSubmit(state.values)
    } catch (error) {
      console.error("Form submission error:", error)
    } finally {
      setState(prev => ({ ...prev, isSubmitting: false }))
    }
  }, [state.values, validate, onSubmit])

  return {
    values: state.values,
    errors: state.errors,
    isSubmitting: state.isSubmitting,
    setFieldValue,
    setFieldError,
    handleSubmit
  }
}
```

---

## 🌐 API Integration

### API Client Setup
```typescript
// lib/api-client.ts
class ApiClient {
  private baseURL: string
  
  constructor(baseURL: string = "") {
    this.baseURL = baseURL
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${this.baseURL}${endpoint}`
    const token = localStorage.getItem("token")
    
    const config: RequestInit = {
      headers: {
        "Content-Type": "application/json",
        ...(token && { Authorization: `Bearer ${token}` }),
        ...options.headers,
      },
      ...options,
    }

    const response = await fetch(url, config)
    
    if (!response.ok) {
      const error = await response.json().catch(() => ({}))
      throw new Error(error.message || `HTTP ${response.status}`)
    }

    return response.json()
  }

  async get<T>(endpoint: string): Promise<T> {
    return this.request<T>(endpoint, { method: "GET" })
  }

  async post<T>(endpoint: string, data?: any): Promise<T> {
    return this.request<T>(endpoint, {
      method: "POST",
      body: data ? JSON.stringify(data) : undefined,
    })
  }

  async put<T>(endpoint: string, data?: any): Promise<T> {
    return this.request<T>(endpoint, {
      method: "PUT",
      body: data ? JSON.stringify(data) : undefined,
    })
  }

  async delete<T>(endpoint: string): Promise<T> {
    return this.request<T>(endpoint, { method: "DELETE" })
  }

  async upload<T>(endpoint: string, formData: FormData): Promise<T> {
    const token = localStorage.getItem("token")
    
    const response = await fetch(`${this.baseURL}${endpoint}`, {
      method: "POST",
      headers: {
        ...(token && { Authorization: `Bearer ${token}` }),
      },
      body: formData,
    })

    if (!response.ok) {
      const error = await response.json().catch(() => ({}))
      throw new Error(error.message || `HTTP ${response.status}`)
    }

    return response.json()
  }
}

export const apiClient = new ApiClient("/api")
```

### API Route Examples
```typescript
// app/api/auth/login/route.ts
import { NextRequest, NextResponse } from "next/server"

const users = [
  {
    id: "1",
    email: "admin@squiz.com",
    password: "admin123",
    name: "Admin User",
    role: "admin"
  }
]

export async function POST(request: NextRequest) {
  try {
    const { email, password } = await request.json()

    const user = users.find(u => u.email === email && u.password === password)
    
    if (!user) {
      return NextResponse.json(
        { detail: "Invalid email or password" },
        { status: 401 }
      )
    }

    const token = `mock-jwt-token-${user.id}-${Date.now()}`
    const { password: _, ...userWithoutPassword } = user

    return NextResponse.json({
      access_token: token,
      token_type: "bearer",
      user: userWithoutPassword,
    })
  } catch (error) {
    return NextResponse.json(
      { detail: "Server error" },
      { status: 500 }
    )
  }
}
```

### Data Fetching Hooks
```typescript
// hooks/useQuizzes.tsx
import { useState, useEffect } from "react"
import { apiClient } from "@/lib/api-client"

interface Quiz {
  id: string
  title: string
  description: string
  category: string
  created_at: string
}

export function useQuizzes() {
  const [quizzes, setQuizzes] = useState<Quiz[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    fetchQuizzes()
  }, [])

  const fetchQuizzes = async () => {
    try {
      setIsLoading(true)
      setError(null)
      const data = await apiClient.get<Quiz[]>("/quizzes")
      setQuizzes(data)
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to fetch quizzes")
    } finally {
      setIsLoading(false)
    }
  }

  const createQuiz = async (quizData: Omit<Quiz, "id" | "created_at">) => {
    try {
      const newQuiz = await apiClient.post<Quiz>("/quiz", quizData)
      setQuizzes(prev => [newQuiz, ...prev])
      return newQuiz
    } catch (error) {
      throw error
    }
  }

  return {
    quizzes,
    isLoading,
    error,
    refetch: fetchQuizzes,
    createQuiz
  }
}
```

---

## 🧪 Testing Guidelines

### Component Testing Setup
```typescript
// __tests__/components/Button.test.tsx
import { render, screen, fireEvent } from "@testing-library/react"
import { Button } from "@/components/ui/button"

describe("Button Component", () => {
  it("renders with correct text", () => {
    render(<Button>Click me</Button>)
    expect(screen.getByText("Click me")).toBeInTheDocument()
  })

  it("calls onClick when clicked", () => {
    const handleClick = jest.fn()
    render(<Button onClick={handleClick}>Click me</Button>)
    
    fireEvent.click(screen.getByText("Click me"))
    expect(handleClick).toHaveBeenCalledTimes(1)
  })

  it("applies correct variant class", () => {
    render(<Button variant="outline">Outline Button</Button>)
    const button = screen.getByText("Outline Button")
    expect(button).toHaveClass("border")
  })

  it("is disabled when disabled prop is true", () => {
    render(<Button disabled>Disabled Button</Button>)
    const button = screen.getByText("Disabled Button")
    expect(button).toBeDisabled()
  })
})
```

### Hook Testing
```typescript
// __tests__/hooks/useAuth.test.tsx
import { renderHook, act } from "@testing-library/react"
import { AuthProvider, useAuth } from "@/hooks/useAuth"

const wrapper = ({ children }: { children: React.ReactNode }) => (
  <AuthProvider>{children}</AuthProvider>
)

describe("useAuth Hook", () => {
  beforeEach(() => {
    localStorage.clear()
    jest.clearAllMocks()
  })

  it("should initialize with null user", () => {
    const { result } = renderHook(() => useAuth(), { wrapper })
    expect(result.current.user).toBeNull()
    expect(result.current.isLoading).toBe(false)
  })

  it("should login successfully", async () => {
    const { result } = renderHook(() => useAuth(), { wrapper })

    await act(async () => {
      await result.current.login("admin@squiz.com", "admin123")
    })

    expect(result.current.user).not.toBeNull()
    expect(result.current.user?.email).toBe("admin@squiz.com")
  })
})
```

### Integration Testing
```typescript
// __tests__/pages/dashboard.test.tsx
import { render, screen, waitFor } from "@testing-library/react"
import { AuthProvider } from "@/hooks/useAuth"
import DashboardPage from "@/app/dashboard/page"

// Mock the useAuth hook
jest.mock("@/hooks/useAuth", () => ({
  useAuth: () => ({
    user: {
      id: "1",
      name: "Test User",
      email: "test@example.com",
      role: "user"
    },
    isLoading: false
  })
}))

describe("Dashboard Page", () => {
  it("renders dashboard with user data", async () => {
    render(
      <AuthProvider>
        <DashboardPage />
      </AuthProvider>
    )

    await waitFor(() => {
      expect(screen.getByText("Xoş gəldin, Test User!")).toBeInTheDocument()
    })
  })
})
```

---

## ⚡ Performance Optimization

### Code Splitting Strategies
```typescript
// Dynamic imports for heavy components
import dynamic from "next/dynamic"

const QuizEditor = dynamic(() => import("@/components/quiz/QuizEditor"), {
  loading: () => <div>Loading editor...</div>,
  ssr: false // Disable SSR for client-only components
})

const AdminPanel = dynamic(() => import("@/components/admin/AdminPanel"), {
  loading: () => <div>Loading admin panel...</div>
})

// Route-based code splitting
const DashboardPage = dynamic(() => import("@/app/dashboard/page"))
```

### Image Optimization
```typescript
// Use Next.js Image component
import Image from "next/image"

function UserAvatar({ src, alt, size = 40 }: {
  src: string
  alt: string
  size?: number
}) {
  return (
    <Image
      src={src}
      alt={alt}
      width={size}
      height={size}
      className="rounded-full"
      priority={size > 100} // Prioritize large images
      placeholder="blur"
      blurDataURL="data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQ..."
    />
  )
}
```

### Bundle Analysis
```javascript
// next.config.mjs
/** @type {import('next').NextConfig} */
const nextConfig = {
  experimental: {
    // Enable bundle analyzer in development
    bundlePagesRouterDependencies: true,
  },
  
  // Webpack optimization
  webpack: (config, { dev, isServer }) => {
    if (!dev && !isServer) {
      config.optimization.splitChunks = {
        chunks: "all",
        cacheGroups: {
          vendor: {
            test: /[\\/]node_modules[\\/]/,
            name: "vendors",
            chunks: "all",
          },
        },
      }
    }
    return config
  },
}

export default nextConfig
```

---

## 🚀 Deployment Guide

### Production Build
```bash
# Build for production
pnpm build

# Test production build locally
pnpm start

# Check bundle size
pnpm run analyze
```

### Environment Configuration
```bash
# Production .env
NEXT_PUBLIC_APP_URL="https://testhub.com"
NODE_ENV="production"

# Database
DATABASE_URL="postgresql://user:pass@host:5432/db"

# Authentication
JWT_SECRET="your-super-secret-jwt-key"
JWT_EXPIRES_IN="24h"

# File Upload
UPLOAD_DIR="/app/uploads"
NEXT_PUBLIC_MAX_FILE_SIZE="10485760"

# Analytics
NEXT_PUBLIC_GA_ID="GA-XXXXXXXXX"

# Error Tracking
SENTRY_DSN="https://your-sentry-dsn"
```

### Docker Configuration
```dockerfile
# Dockerfile
FROM node:18-alpine AS base

# Install dependencies only when needed
FROM base AS deps
RUN apk add --no-cache libc6-compat
WORKDIR /app
COPY package.json pnpm-lock.yaml* ./
RUN npm install -g pnpm && pnpm install --frozen-lockfile

# Rebuild the source code only when needed
FROM base AS builder
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .
RUN npm install -g pnpm && pnpm build

# Production image, copy all the files and run next
FROM base AS runner
WORKDIR /app

ENV NODE_ENV production

RUN addgroup --system --gid 1001 nodejs
RUN adduser --system --uid 1001 nextjs

COPY --from=builder /app/public ./public
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static

USER nextjs

EXPOSE 3000

ENV PORT 3000

CMD ["node", "server.js"]
```

### Vercel Deployment
```json
// vercel.json
{
  "buildCommand": "pnpm build",
  "outputDirectory": ".next",
  "installCommand": "pnpm install",
  "framework": "nextjs",
  "functions": {
    "app/api/**/*.ts": {
      "maxDuration": 30
    }
  },
  "regions": ["fra1"],
  "env": {
    "NODE_ENV": "production"
  }
}
```

---

## 🔧 Troubleshooting

### Common Development Issues

#### 1. TypeScript Errors
```bash
# Clear TypeScript cache
rm -rf .next
rm -rf node_modules/.cache

# Reinstall dependencies
rm -rf node_modules
pnpm install

# Check types
pnpm type-check
```

#### 2. Hydration Mismatches
```typescript
// Use dynamic imports for client-only components
const ClientOnlyComponent = dynamic(
  () => import("@/components/ClientOnlyComponent"),
  { ssr: false }
)

// Or use useEffect for client-only logic
function ComponentWithClientLogic() {
  const [mounted, setMounted] = useState(false)
  
  useEffect(() => {
    setMounted(true)
  }, [])
  
  if (!mounted) return null
  
  return <div>{/* Client-only content */}</div>
}
```

#### 3. Style Issues
```bash
# Purge Tailwind cache
rm -rf .next
pnpm dev

# Check Tailwind configuration
npx tailwindcss -i ./app/globals.css -o ./output.css --watch
```

#### 4. API Route Issues
```typescript
// Add proper error handling
export async function POST(request: NextRequest) {
  try {
    const body = await request.json()
    // Process request
    return NextResponse.json({ success: true })
  } catch (error) {
    console.error("API Error:", error)
    return NextResponse.json(
      { error: "Internal Server Error" },
      { status: 500 }
    )
  }
}
```

### Performance Debugging
```bash
# Analyze bundle size
npm install -g webpack-bundle-analyzer
npx webpack-bundle-analyzer .next/static/chunks/*.js

# Check Core Web Vitals
# Use browser DevTools > Lighthouse
# Or install web-vitals
npm install web-vitals
```

### Production Issues
```typescript
// Add error boundary for production
function MyApp({ Component, pageProps }: AppProps) {
  return (
    <ErrorBoundary>
      <Component {...pageProps} />
    </ErrorBoundary>
  )
}

// Add proper logging
if (process.env.NODE_ENV === "production") {
  console.error = (...args) => {
    // Send to error tracking service
    // e.g., Sentry, LogRocket, etc.
  }
}
```

---

This developer guide provides comprehensive information for maintaining and extending the TestHub/Squiz application. It covers everything from basic setup to advanced optimization techniques, ensuring developers can work effectively with the codebase.
