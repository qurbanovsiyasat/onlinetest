// Configuration management for environment variables
export const config = {
  // API Configuration
  backendUrl: process.env.NEXT_PUBLIC_BACKEND_URL || "http://localhost:8001",
  apiVersion: process.env.NEXT_PUBLIC_API_VERSION || "v1",

  // App Configuration
  appName: process.env.NEXT_PUBLIC_APP_NAME || "Squiz Platform",
  environment: process.env.NEXT_PUBLIC_ENVIRONMENT || "development",
  debug: process.env.NEXT_PUBLIC_DEBUG === "true",

  // API Endpoints
  api: {
    base: process.env.NEXT_PUBLIC_BACKEND_URL || "http://localhost:8001",
    auth: "/api/auth",
    users: "/api/users",
    quizzes: "/api/quizzes",
    questions: "/api/questions",
    sessions: "/api/sessions",
    forum: "/api/forum",
    admin: "/api/admin",
  },

  // Development settings
  isDevelopment: (process.env.NEXT_PUBLIC_ENVIRONMENT || "development") === "development",
  isProduction: (process.env.NEXT_PUBLIC_ENVIRONMENT || "development") === "production",

  // Feature flags
  features: {
    realTimeQuiz: true,
    forum: true,
    analytics: true,
    adminPanel: true,
  },
}

// Validation function to check if all required env vars are set
export const validateConfig = () => {
  // For development, we provide defaults, so validation is optional
  const warnings = []

  if (!process.env.NEXT_PUBLIC_BACKEND_URL) {
    warnings.push("NEXT_PUBLIC_BACKEND_URL not set, using default: http://localhost:8001")
  }

  if (!process.env.NEXT_PUBLIC_ENVIRONMENT) {
    warnings.push("NEXT_PUBLIC_ENVIRONMENT not set, using default: development")
  }

  if (warnings.length > 0 && config.debug) {
    console.warn("⚠️ Configuration warnings:", warnings)
  }

  console.log("✅ Configuration loaded successfully")
  console.log("🔧 Backend URL:", config.backendUrl)
  console.log("🌍 Environment:", config.environment)

  return true
}

// Export individual config values for convenience
export const { backendUrl, apiVersion, appName, environment, debug, api, isDevelopment, isProduction, features } =
  config
