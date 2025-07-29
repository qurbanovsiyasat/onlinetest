# 🚀 TestHub/Squiz - Local Development Setup Guide

## 📋 Prerequisites

Before setting up the project locally, ensure you have the following installed:

### Required Software
- **Node.js**: Version 18.x or higher
- **Package Manager**: npm, yarn, or pnpm (recommended)
- **Git**: For version control
- **Code Editor**: VS Code (recommended) with extensions

### Recommended VS Code Extensions
```
- ES7+ React/Redux/React-Native snippets
- TypeScript Importer
- Tailwind CSS IntelliSense
- Auto Rename Tag
- Bracket Pair Colorizer
- GitLens
- Prettier - Code formatter
- ESLint
```

---

## 🔧 Quick Start (5-Minute Setup)

### 1. Clone the Repository
```bash
# Clone the project
git clone https://github.com/qurbanovqurbanov/test.git testhub-squiz
cd testhub-squiz

# Or download and extract the ZIP file
```

### 2. Install Dependencies
```bash
# Using npm
npm install

# Using yarn
yarn install

# Using pnpm (recommended for better performance)
pnpm install
```

### 3. Start Development Server
```bash
# Using npm
npm run dev

# Using yarn
yarn dev

# Using pnpm
pnpm dev
```

### 4. Open in Browser
```
http://localhost:3000
```

**🎉 That's it! Your TestHub application should now be running locally.**

---

## 📁 Project Structure Overview

```
testhub-squiz/
├── 📄 package.json          # Project dependencies and scripts
├── 📄 next.config.mjs       # Next.js configuration
├── 📄 tailwind.config.ts    # Tailwind CSS configuration
├── 📄 tsconfig.json         # TypeScript configuration
├── 📄 components.json       # Shadcn/UI component configuration
├── 📄 postcss.config.mjs    # PostCSS configuration for Tailwind
│
├── 📁 app/                  # Next.js 14 App Router
│   ├── layout.tsx           # Root layout component
│   ├── page.tsx             # Homepage
│   ├── globals.css          # Global styles
│   ├── api/                 # API routes
│   ├── dashboard/           # User dashboard
│   ├── quiz/                # Quiz management
│   ├── forum/               # Q&A forum
│   ├── admin/               # Admin panel
│   └── profile/             # User profiles
│
├── 📁 components/           # Reusable React components
│   ├── ui/                  # Shadcn/UI components
│   ├── auth/                # Authentication components
│   └── layout/              # Layout components
│
├── 📁 hooks/                # Custom React hooks
├── 📁 lib/                  # Utility functions
├── 📁 styles/               # Additional CSS files
└── 📁 public/               # Static assets
```

---

## ⚙️ Configuration Details

### Environment Variables
Create a `.env.local` file in the root directory:

```bash
# .env.local
NEXT_PUBLIC_APP_NAME="TestHub"
NEXT_PUBLIC_APP_URL="http://localhost:3000"

# API Configuration (when backend is ready)
# NEXT_PUBLIC_API_URL="http://localhost:8000"
# DATABASE_URL="your-database-url"
# JWT_SECRET="your-jwt-secret"

# Image Upload Configuration
# NEXT_PUBLIC_UPLOAD_URL="/api/upload"
# MAX_FILE_SIZE="5242880" # 5MB

# Analytics (optional)
# NEXT_PUBLIC_GA_ID="your-ga-id"
```

### Package.json Scripts
```json
{
  "scripts": {
    "dev": "next dev",                    # Start development server
    "build": "next build",                # Build for production
    "start": "next start",                # Start production server
    "lint": "next lint",                  # Run ESLint
    "type-check": "tsc --noEmit"         # TypeScript type checking
  }
}
```

---

## 🔐 Default Login Credentials

The application comes with pre-configured test accounts:

### Admin Account
```
Email: admin@squiz.com
Password: admin123
Role: Administrator
```

### Regular User Account
```
Email: user@squiz.com
Password: user123
Role: User
```

### Test Account Creation
You can also create new accounts through the registration form on the website.

---

## 🛠️ Development Workflow

### 1. Starting Development
```bash
# Start the development server
pnpm dev

# Open browser
open http://localhost:3000
```

### 2. Making Changes
- Edit files in `app/`, `components/`, or `hooks/`
- Changes are automatically hot-reloaded
- TypeScript errors will show in terminal and browser
- Tailwind CSS classes are processed automatically

### 3. Adding New Components
```bash
# Example: Adding a new UI component
npx shadcn-ui@latest add button

# Or create custom components in components/ folder
```

### 4. Code Quality Checks
```bash
# Run TypeScript type checking
pnpm type-check

# Run ESLint
pnpm lint

# Fix auto-fixable ESLint issues
pnpm lint --fix
```

---

## 📦 Package Management

### Current Dependencies

#### Core Framework
```json
{
  "next": "14.2.16",
  "react": "^18",
  "react-dom": "^18",
  "typescript": "^5"
}
```

#### UI & Styling
```json
{
  "tailwindcss": "^3.4.17",
  "framer-motion": "latest",
  "lucide-react": "^0.454.0",
  "@radix-ui/react-*": "latest"
}
```

#### Utilities
```json
{
  "class-variance-authority": "^0.7.1",
  "clsx": "^2.1.1",
  "tailwind-merge": "^2.5.5",
  "zod": "^3.24.1"
}
```

### Adding New Dependencies
```bash
# Add a new dependency
pnpm add package-name

# Add a dev dependency
pnpm add -D package-name

# Add a specific version
pnpm add package-name@version
```

---

## 🎨 UI Component System

### Shadcn/UI Components
The project uses Shadcn/UI components. To add new components:

```bash
# List available components
npx shadcn-ui@latest add

# Add specific components
npx shadcn-ui@latest add button
npx shadcn-ui@latest add card
npx shadcn-ui@latest add dialog
npx shadcn-ui@latest add tabs
```

### Custom Component Creation
```tsx
// components/custom/MyComponent.tsx
import { cn } from "@/lib/utils"

interface MyComponentProps {
  className?: string
  children: React.ReactNode
}

export function MyComponent({ className, children }: MyComponentProps) {
  return (
    <div className={cn("base-styles", className)}>
      {children}
    </div>
  )
}
```

---

## 🔧 Tailwind CSS Configuration

### Custom Utilities
The project includes custom Tailwind configurations:

```typescript
// tailwind.config.ts
export default {
  theme: {
    extend: {
      colors: {
        primary: "hsl(var(--primary))",
        secondary: "hsl(var(--secondary))",
        // ... more custom colors
      },
      fontFamily: {
        sans: ["Inter", "sans-serif"],
      },
      animation: {
        "accordion-down": "accordion-down 0.2s ease-out",
        "accordion-up": "accordion-up 0.2s ease-out",
      },
    },
  },
}
```

### CSS Variables
```css
/* app/globals.css */
:root {
  --background: 0 0% 100%;
  --foreground: 222.2 84% 4.9%;
  --primary: 221.2 83.2% 53.3%;
  --secondary: 210 40% 96%;
  /* ... more variables */
}
```

---

## 📱 Testing the Application

### Manual Testing Checklist

#### 1. Authentication Flow
- [ ] Homepage loads correctly
- [ ] Login modal opens when clicking "Daxil Ol"
- [ ] Registration modal opens when clicking "Pulsuz Başla"
- [ ] Admin login works with admin@squiz.com/admin123
- [ ] User login works with user@squiz.com/user123
- [ ] Form validation shows appropriate errors
- [ ] Successful login redirects to dashboard

#### 2. Dashboard Functionality
- [ ] Dashboard loads with user-specific data
- [ ] Statistics display correctly
- [ ] Recent activity shows
- [ ] Navigation works between sections
- [ ] Quick action buttons function

#### 3. Quiz System
- [ ] Quiz creation page loads
- [ ] Question types can be added
- [ ] Image upload works
- [ ] Quiz preview functions
- [ ] Save and publish options work

#### 4. Forum System
- [ ] Forum page displays posts
- [ ] Search and filter functionality
- [ ] New post creation works
- [ ] Voting system functions
- [ ] Category filtering works

#### 5. Admin Panel
- [ ] Admin panel accessible to admin users
- [ ] User management functions
- [ ] Quiz oversight works
- [ ] System statistics display
- [ ] Export functionality works

### Responsive Design Testing
Test the application on different screen sizes:
- Desktop (1920x1080)
- Laptop (1366x768)
- Tablet (768x1024)
- Mobile (375x667)

---

## 🐛 Troubleshooting

### Common Issues & Solutions

#### Issue: Port 3000 is already in use
```bash
# Solution 1: Use a different port
PORT=3001 pnpm dev

# Solution 2: Kill the process using port 3000
# On macOS/Linux:
lsof -ti:3000 | xargs kill -9

# On Windows:
netstat -ano | findstr :3000
taskkill /PID <PID> /F
```

#### Issue: TypeScript errors
```bash
# Clear TypeScript cache
rm -rf .next
pnpm dev

# Check for type errors
pnpm type-check
```

#### Issue: Tailwind styles not working
```bash
# Restart development server
pnpm dev

# Clear browser cache
# Check if Tailwind is properly imported in globals.css
```

#### Issue: Module resolution errors
```bash
# Clear node_modules and reinstall
rm -rf node_modules
rm pnpm-lock.yaml
pnpm install
```

#### Issue: Image upload not working
- Check if the `/api/upload/image` endpoint is implemented
- Verify file size limits
- Check browser console for errors

---

## 🔄 Hot Reloading & Fast Refresh

### Features
- **Instant Updates**: Changes reflect immediately in browser
- **State Preservation**: React state maintained during updates
- **Error Recovery**: Automatic recovery from syntax errors
- **CSS Hot Reload**: Tailwind changes update instantly

### Best Practices
- Keep components small and focused
- Use TypeScript for better error detection
- Utilize React DevTools for debugging
- Monitor console for warnings and errors

---

## 📊 Performance Monitoring

### Development Tools
```bash
# Bundle analyzer (add to package.json)
npm install --save-dev @next/bundle-analyzer

# Performance monitoring
# Open browser DevTools > Performance tab
# Run Lighthouse audits for optimization insights
```

### Optimization Tips
- Use Next.js Image component for images
- Implement proper loading states
- Optimize bundle size with tree shaking
- Use React.memo for expensive components
- Implement proper error boundaries

---

## 🚀 Building for Production

### Local Production Build
```bash
# Build the application
pnpm build

# Start production server
pnpm start

# Test production build locally
open http://localhost:3000
```

### Production Checklist
- [ ] All environment variables configured
- [ ] API endpoints updated for production
- [ ] Error handling implemented
- [ ] Performance optimized
- [ ] Security measures in place
- [ ] Analytics configured
- [ ] SEO meta tags added

---

## 📚 Additional Resources

### Documentation Links
- [Next.js 14 Documentation](https://nextjs.org/docs)
- [Tailwind CSS Documentation](https://tailwindcss.com/docs)
- [Radix UI Components](https://www.radix-ui.com/)
- [Framer Motion API](https://www.framer.com/motion/)
- [TypeScript Handbook](https://www.typescriptlang.org/docs/)

### Community & Support
- [Next.js Discord](https://discord.gg/nextjs)
- [Tailwind CSS Discord](https://discord.gg/tailwindcss)
- [React Developer Tools](https://react.dev/learn/react-developer-tools)

### Learning Resources
- [React 18 Features](https://react.dev/blog/2022/03/29/react-v18)
- [Next.js App Router Guide](https://nextjs.org/docs/app)
- [Tailwind CSS Best Practices](https://tailwindcss.com/docs/editor-setup)

---

## 🤝 Contributing Guidelines

### Code Style
- Use TypeScript for all new files
- Follow ESLint and Prettier configurations
- Use meaningful component and variable names
- Add JSDoc comments for complex functions
- Maintain consistent file organization

### Git Workflow
```bash
# Create feature branch
git checkout -b feature/your-feature-name

# Make changes and commit
git add .
git commit -m "feat: add new feature description"

# Push to repository
git push origin feature/your-feature-name
```

### Pull Request Guidelines
- Provide clear description of changes
- Include screenshots for UI changes
- Ensure all tests pass
- Update documentation if needed
- Request code review from team members

---

This setup guide provides everything needed to get TestHub/Squiz running locally and contributing to the project effectively. The application is designed to work out of the box with minimal configuration required.
