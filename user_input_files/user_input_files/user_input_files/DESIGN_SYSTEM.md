# 🎨 TestHub/Squiz - Numbered Design System Documentation

## 📋 Design System Overview

The TestHub/Squiz design system is built on modern design principles with a focus on accessibility, consistency, and scalability. It uses Tailwind CSS as the foundation with custom components built on Radix UI primitives.

### Design Philosophy
- **Consistency**: Unified visual language across all components
- **Accessibility**: WCAG 2.1 AA compliance with keyboard navigation
- **Modularity**: Reusable components with clear APIs
- **Responsiveness**: Mobile-first approach with adaptive layouts
- **Performance**: Optimized CSS with minimal bundle size

---

## 🎨 1. Color System

### 1.1 Primary Color Palette
```css
/* Primary Blues */
--blue-50:  #eff6ff    /* Very light blue background */
--blue-100: #dbeafe    /* Light blue background */
--blue-500: #3b82f6    /* Medium blue */
--blue-600: #2563eb    /* Primary blue - main brand color */
--blue-700: #1d4ed8    /* Dark blue hover state */
--blue-900: #1e3a8a    /* Very dark blue text */

/* Primary Purples */
--purple-50:  #faf5ff   /* Very light purple background */
--purple-100: #f3e8ff   /* Light purple background */
--purple-500: #a855f7   /* Medium purple */
--purple-600: #9333ea   /* Primary purple - secondary brand */
--purple-700: #7c3aed   /* Dark purple hover state */
--purple-900: #581c87   /* Very dark purple text */
```

### 1.2 Semantic Color System
```css
/* Success Colors */
--green-50:  #f0fdf4    /* Success background light */
--green-100: #dcfce7    /* Success background */
--green-500: #22c55e    /* Success medium */
--green-600: #16a34a    /* Success primary */
--green-700: #15803d    /* Success dark */

/* Warning Colors */
--yellow-50:  #fefce8   /* Warning background light */
--yellow-100: #fef3c7   /* Warning background */
--yellow-500: #eab308   /* Warning medium */
--yellow-600: #ca8a04   /* Warning primary */
--orange-600: #ea580c   /* Warning/alert primary */

/* Error Colors */
--red-50:  #fef2f2      /* Error background light */
--red-100: #fee2e2      /* Error background */
--red-500: #ef4444      /* Error medium */
--red-600: #dc2626      /* Error primary */
--red-700: #b91c1c      /* Error dark */

/* Neutral Colors */
--gray-50:  #f9fafb     /* Background light */
--gray-100: #f3f4f6     /* Background medium */
--gray-200: #e5e7eb     /* Border light */
--gray-300: #d1d5db     /* Border medium */
--gray-400: #9ca3af     /* Text muted */
--gray-500: #6b7280     /* Text secondary */
--gray-600: #4b5563     /* Text primary */
--gray-700: #374151     /* Text strong */
--gray-800: #1f2937     /* Text very strong */
--gray-900: #111827     /* Text maximum */
```

### 1.3 Gradient System
```css
/* Primary Gradients */
.gradient-primary {
  background: linear-gradient(135deg, #2563eb 0%, #9333ea 100%);
}

.gradient-success {
  background: linear-gradient(135deg, #16a34a 0%, #10b981 100%);
}

.gradient-warning {
  background: linear-gradient(135deg, #f59e0b 0%, #ea580c 100%);
}

.gradient-error {
  background: linear-gradient(135deg, #dc2626 0%, #ef4444 100%);
}

/* Subtle Gradients */
.gradient-subtle {
  background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
}

.gradient-glass {
  background: linear-gradient(135deg, rgba(255,255,255,0.1) 0%, rgba(255,255,255,0.05) 100%);
  backdrop-filter: blur(10px);
}
```

---

## 📐 2. Typography System

### 2.1 Font Stack
```css
/* Primary Font Family */
font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;

/* Fallback Stack */
font-family: system-ui, -apple-system, sans-serif;
```

### 2.2 Typography Scale
```css
/* Display Headings */
.text-7xl {    /* 72px / 4.5rem */
  font-size: 4.5rem;
  line-height: 1.1;
  font-weight: 800;
  letter-spacing: -0.025em;
}

.text-6xl {    /* 60px / 3.75rem */
  font-size: 3.75rem;
  line-height: 1.1;
  font-weight: 800;
  letter-spacing: -0.025em;
}

.text-5xl {    /* 48px / 3rem */
  font-size: 3rem;
  line-height: 1.2;
  font-weight: 700;
  letter-spacing: -0.025em;
}

/* Headings */
.text-4xl {    /* 36px / 2.25rem - H1 */
  font-size: 2.25rem;
  line-height: 1.25;
  font-weight: 700;
  letter-spacing: -0.025em;
}

.text-3xl {    /* 30px / 1.875rem - H2 */
  font-size: 1.875rem;
  line-height: 1.3;
  font-weight: 700;
  letter-spacing: -0.025em;
}

.text-2xl {    /* 24px / 1.5rem - H3 */
  font-size: 1.5rem;
  line-height: 1.35;
  font-weight: 600;
  letter-spacing: -0.025em;
}

.text-xl {     /* 20px / 1.25rem - H4 */
  font-size: 1.25rem;
  line-height: 1.4;
  font-weight: 600;
}

.text-lg {     /* 18px / 1.125rem - H5 */
  font-size: 1.125rem;
  line-height: 1.45;
  font-weight: 600;
}

/* Body Text */
.text-base {   /* 16px / 1rem - Body Large */
  font-size: 1rem;
  line-height: 1.5;
  font-weight: 400;
}

.text-sm {     /* 14px / 0.875rem - Body */
  font-size: 0.875rem;
  line-height: 1.5;
  font-weight: 400;
}

.text-xs {     /* 12px / 0.75rem - Caption */
  font-size: 0.75rem;
  line-height: 1.5;
  font-weight: 400;
}
```

### 2.3 Font Weight Scale
```css
.font-light     { font-weight: 300; }
.font-normal    { font-weight: 400; }
.font-medium    { font-weight: 500; }
.font-semibold  { font-weight: 600; }
.font-bold      { font-weight: 700; }
.font-extrabold { font-weight: 800; }
.font-black     { font-weight: 900; }
```

---

## 📏 3. Spacing System

### 3.1 Base Spacing Scale
```css
/* Tailwind Spacing Scale (4px base) */
--space-0:  0rem      /* 0px */
--space-1:  0.25rem   /* 4px */
--space-2:  0.5rem    /* 8px */
--space-3:  0.75rem   /* 12px */
--space-4:  1rem      /* 16px */
--space-5:  1.25rem   /* 20px */
--space-6:  1.5rem    /* 24px */
--space-8:  2rem      /* 32px */
--space-10: 2.5rem    /* 40px */
--space-12: 3rem      /* 48px */
--space-16: 4rem      /* 64px */
--space-20: 5rem      /* 80px */
--space-24: 6rem      /* 96px */
--space-32: 8rem      /* 128px */
```

### 3.2 Component Spacing Guidelines
```css
/* Container Spacing */
.container-padding     { padding: 1rem; }           /* Mobile: 16px */
.container-padding-md  { padding: 1.5rem; }         /* Tablet: 24px */
.container-padding-lg  { padding: 2rem; }           /* Desktop: 32px */

/* Section Spacing */
.section-gap-sm   { gap: 1rem; }      /* 16px */
.section-gap-md   { gap: 1.5rem; }    /* 24px */
.section-gap-lg   { gap: 2rem; }      /* 32px */
.section-gap-xl   { gap: 3rem; }      /* 48px */

/* Component Spacing */
.component-gap-xs { gap: 0.5rem; }    /* 8px */
.component-gap-sm { gap: 0.75rem; }   /* 12px */
.component-gap-md { gap: 1rem; }      /* 16px */
.component-gap-lg { gap: 1.5rem; }    /* 24px */
```

---

## 🎯 4. Component System

### 4.1 Button Components

#### 4.1.1 Primary Button
```tsx
// Usage
<Button variant="default" size="default">
  Primary Action
</Button>

// Styles
.btn-primary {
  background: linear-gradient(135deg, #2563eb, #9333ea);
  color: white;
  padding: 0.5rem 1rem;
  border-radius: 0.375rem;
  font-weight: 500;
  transition: all 0.2s;
}

.btn-primary:hover {
  background: linear-gradient(135deg, #1d4ed8, #7c3aed);
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(37, 99, 235, 0.4);
}
```

#### 4.1.2 Secondary Button
```tsx
// Usage
<Button variant="secondary" size="default">
  Secondary Action
</Button>

// Styles
.btn-secondary {
  background: #f1f5f9;
  color: #334155;
  border: 1px solid #e2e8f0;
  padding: 0.5rem 1rem;
  border-radius: 0.375rem;
  font-weight: 500;
  transition: all 0.2s;
}
```

#### 4.1.3 Button Sizes
```css
/* Size Variants */
.btn-sm     { height: 2.25rem; padding: 0 0.75rem; font-size: 0.875rem; }  /* 36px height */
.btn-default{ height: 2.5rem;  padding: 0 1rem;    font-size: 0.875rem; }  /* 40px height */
.btn-lg     { height: 2.75rem; padding: 0 2rem;    font-size: 1rem; }      /* 44px height */
.btn-xl     { height: 3rem;    padding: 0 2rem;    font-size: 1.125rem; }  /* 48px height */
```

### 4.2 Card Components

#### 4.2.1 Base Card
```tsx
// Usage
<Card className="p-6">
  <CardHeader>
    <CardTitle>Card Title</CardTitle>
    <CardDescription>Card description</CardDescription>
  </CardHeader>
  <CardContent>
    Card content goes here
  </CardContent>
</Card>

// Styles
.card {
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 0.5rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  transition: all 0.2s ease;
}

.card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  border-color: #d1d5db;
}
```

#### 4.2.2 Interactive Card
```css
.card-interactive {
  cursor: pointer;
  transform: translateY(0);
  transition: all 0.2s ease;
}

.card-interactive:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
}
```

### 4.3 Input Components

#### 4.3.1 Text Input
```tsx
// Usage
<Input 
  type="text" 
  placeholder="Enter text here" 
  className="w-full"
/>

// Styles
.input {
  width: 100%;
  height: 2.5rem;
  padding: 0 0.75rem;
  border: 1px solid #d1d5db;
  border-radius: 0.375rem;
  font-size: 0.875rem;
  background: white;
  transition: all 0.2s ease;
}

.input:focus {
  outline: none;
  border-color: #2563eb;
  box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1);
}

.input:error {
  border-color: #dc2626;
  box-shadow: 0 0 0 3px rgba(220, 38, 38, 0.1);
}
```

#### 4.3.2 Textarea
```css
.textarea {
  min-height: 6rem;
  resize: vertical;
  padding: 0.75rem;
  line-height: 1.5;
}
```

### 4.4 Badge Components

#### 4.4.1 Status Badges
```tsx
// Usage
<Badge variant="success">Active</Badge>
<Badge variant="warning">Pending</Badge>
<Badge variant="error">Error</Badge>

// Styles
.badge {
  display: inline-flex;
  align-items: center;
  padding: 0.25rem 0.75rem;
  border-radius: 9999px;
  font-size: 0.75rem;
  font-weight: 500;
  line-height: 1;
}

.badge-success {
  background: #dcfce7;
  color: #15803d;
}

.badge-warning {
  background: #fef3c7;
  color: #92400e;
}

.badge-error {
  background: #fee2e2;
  color: #b91c1c;
}

.badge-info {
  background: #dbeafe;
  color: #1d4ed8;
}
```

### 4.5 Navigation Components

#### 4.5.1 Tab Navigation
```tsx
// Usage
<Tabs defaultValue="tab1">
  <TabsList>
    <TabsTrigger value="tab1">Tab 1</TabsTrigger>
    <TabsTrigger value="tab2">Tab 2</TabsTrigger>
  </TabsList>
  <TabsContent value="tab1">Content 1</TabsContent>
  <TabsContent value="tab2">Content 2</TabsContent>
</Tabs>

// Styles
.tabs-list {
  display: inline-flex;
  padding: 0.25rem;
  background: #f1f5f9;
  border-radius: 0.5rem;
  gap: 0.25rem;
}

.tabs-trigger {
  padding: 0.5rem 1rem;
  border-radius: 0.25rem;
  font-size: 0.875rem;
  font-weight: 500;
  transition: all 0.2s;
}

.tabs-trigger[data-state="active"] {
  background: white;
  color: #1e40af;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}
```

### 4.6 Modal/Dialog Components

#### 4.6.1 Modal Overlay
```css
.modal-overlay {
  position: fixed;
  inset: 0;
  z-index: 50;
  background: rgba(0, 0, 0, 0.8);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1rem;
}

.modal-content {
  background: white;
  border-radius: 0.5rem;
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1);
  max-width: 32rem;
  width: 100%;
  max-height: 90vh;
  overflow-y: auto;
}
```

### 4.7 Progress Components

#### 4.7.1 Progress Bar
```tsx
// Usage
<Progress value={65} className="w-full" />

// Styles
.progress {
  position: relative;
  height: 0.5rem;
  width: 100%;
  overflow: hidden;
  border-radius: 9999px;
  background: #f1f5f9;
}

.progress-indicator {
  height: 100%;
  width: 100%;
  flex: 1 1 0%;
  background: linear-gradient(90deg, #2563eb, #9333ea);
  transition: all 0.3s ease;
  border-radius: 9999px;
}
```

---

## 📱 5. Responsive Design System

### 5.1 Breakpoint System
```css
/* Tailwind CSS Breakpoints */
/* Small devices (landscape phones, 640px and up) */
@media (min-width: 640px) { .sm\: }

/* Medium devices (tablets, 768px and up) */
@media (min-width: 768px) { .md\: }

/* Large devices (desktops, 1024px and up) */
@media (min-width: 1024px) { .lg\: }

/* Extra large devices (large desktops, 1280px and up) */
@media (min-width: 1280px) { .xl\: }

/* 2X Extra large devices (larger desktops, 1536px and up) */
@media (min-width: 1536px) { .2xl\: }
```

### 5.2 Grid System
```css
/* Container Widths */
.container {
  width: 100%;
  margin: 0 auto;
  padding: 0 1rem;
}

@media (min-width: 640px) {
  .container { max-width: 640px; }
}

@media (min-width: 768px) {
  .container { max-width: 768px; }
}

@media (min-width: 1024px) {
  .container { max-width: 1024px; padding: 0 2rem; }
}

@media (min-width: 1280px) {
  .container { max-width: 1280px; }
}
```

### 5.3 Responsive Typography
```css
/* Responsive Headings */
.heading-responsive {
  font-size: 1.875rem;  /* Mobile: 30px */
  line-height: 1.3;
}

@media (min-width: 768px) {
  .heading-responsive {
    font-size: 2.25rem;  /* Tablet: 36px */
  }
}

@media (min-width: 1024px) {
  .heading-responsive {
    font-size: 3rem;     /* Desktop: 48px */
  }
}
```

---

## 🎭 6. Animation System

### 6.1 Transition Standards
```css
/* Standard Transitions */
.transition-fast    { transition: all 0.15s ease; }
.transition-normal  { transition: all 0.2s ease; }
.transition-slow    { transition: all 0.3s ease; }

/* Specific Property Transitions */
.transition-colors  { transition: color, background-color, border-color 0.2s ease; }
.transition-shadow  { transition: box-shadow 0.2s ease; }
.transition-transform { transition: transform 0.2s ease; }
```

### 6.2 Hover Effects
```css
/* Elevation Effects */
.hover-lift {
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.hover-lift:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
}

/* Scale Effects */
.hover-scale {
  transition: transform 0.2s ease;
}

.hover-scale:hover {
  transform: scale(1.05);
}
```

### 6.3 Loading Animations
```css
/* Spinner Animation */
@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.animate-spin {
  animation: spin 1s linear infinite;
}

/* Pulse Animation */
@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

.animate-pulse {
  animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
}
```

---

## 🌙 7. Dark Mode Support

### 7.1 Dark Mode Variables
```css
:root {
  --background: 0 0% 100%;
  --foreground: 222.2 84% 4.9%;
}

[data-theme="dark"] {
  --background: 222.2 84% 4.9%;
  --foreground: 210 40% 98%;
}

/* Usage */
.bg-background { background-color: hsl(var(--background)); }
.text-foreground { color: hsl(var(--foreground)); }
```

### 7.2 Dark Mode Components
```css
/* Dark Mode Button */
.dark .btn-primary {
  background: linear-gradient(135deg, #3b82f6, #a855f7);
}

.dark .card {
  background: hsl(var(--card));
  border-color: hsl(var(--border));
}
```

---

## ♿ 8. Accessibility Standards

### 8.1 Color Contrast
- **AA Standard**: 4.5:1 contrast ratio for normal text
- **AAA Standard**: 7:1 contrast ratio for enhanced accessibility
- **Large Text**: 3:1 minimum contrast ratio

### 8.2 Focus States
```css
/* Focus Ring System */
.focus-ring {
  outline: 2px solid transparent;
  outline-offset: 2px;
}

.focus-ring:focus-visible {
  outline: 2px solid hsl(var(--ring));
  outline-offset: 2px;
}

/* Interactive Element Focus */
.interactive:focus-visible {
  outline: 2px solid #2563eb;
  outline-offset: 2px;
  border-radius: 0.25rem;
}
```

### 8.3 Screen Reader Support
```css
/* Screen Reader Only Content */
.sr-only {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border: 0;
}
```

---

## 🔧 9. Component Usage Examples

### 9.1 Form Layout Example
```tsx
<form className="space-y-6">
  <div className="space-y-2">
    <Label htmlFor="email">Email Address</Label>
    <Input 
      id="email" 
      type="email" 
      placeholder="Enter your email" 
      required 
    />
  </div>
  
  <div className="space-y-2">
    <Label htmlFor="password">Password</Label>
    <Input 
      id="password" 
      type="password" 
      placeholder="Enter your password" 
      required 
    />
  </div>
  
  <Button type="submit" className="w-full">
    Sign In
  </Button>
</form>
```

### 9.2 Dashboard Card Layout
```tsx
<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
  {stats.map((stat, index) => (
    <Card key={index} className="p-6">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm font-medium text-gray-600">{stat.title}</p>
          <p className="text-2xl font-bold text-gray-900">{stat.value}</p>
        </div>
        <div className="p-3 bg-blue-100 rounded-full">
          <stat.icon className="w-6 h-6 text-blue-600" />
        </div>
      </div>
    </Card>
  ))}
</div>
```

### 9.3 Navigation Menu Example
```tsx
<nav className="flex items-center space-x-8">
  <Link 
    href="/dashboard" 
    className="text-gray-600 hover:text-blue-600 transition-colors font-medium"
  >
    Dashboard
  </Link>
  <Link 
    href="/quizzes" 
    className="text-gray-600 hover:text-blue-600 transition-colors font-medium"
  >
    Quizzes
  </Link>
  <Link 
    href="/forum" 
    className="text-gray-600 hover:text-blue-600 transition-colors font-medium"
  >
    Forum
  </Link>
</nav>
```

---

## 📐 10. Layout Patterns

### 10.1 Page Layout Structure
```tsx
// Standard Page Layout
<div className="min-h-screen bg-gray-50">
  <header className="bg-white border-b border-gray-200">
    {/* Header Content */}
  </header>
  
  <main className="container mx-auto py-8 px-4">
    <div className="space-y-8">
      {/* Page Content */}
    </div>
  </main>
  
  <footer className="bg-gray-900 text-white py-12">
    {/* Footer Content */}
  </footer>
</div>
```

### 10.2 Dashboard Layout Pattern
```tsx
// Dashboard with Sidebar
<div className="flex h-screen bg-gray-50">
  <aside className="w-64 bg-white border-r border-gray-200">
    {/* Sidebar Navigation */}
  </aside>
  
  <main className="flex-1 overflow-y-auto">
    <div className="p-8">
      <div className="space-y-8">
        {/* Dashboard Content */}
      </div>
    </div>
  </main>
</div>
```

### 10.3 Modal Layout Pattern
```tsx
// Modal/Dialog Layout
<div className="fixed inset-0 z-50 bg-black/50 backdrop-blur-sm flex items-center justify-center p-4">
  <div className="bg-white rounded-lg shadow-xl max-w-md w-full max-h-[90vh] overflow-y-auto">
    <div className="p-6">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-xl font-semibold">Modal Title</h2>
        <Button variant="ghost" size="sm">
          <X className="w-4 h-4" />
        </Button>
      </div>
      
      <div className="space-y-4">
        {/* Modal Content */}
      </div>
      
      <div className="flex justify-end space-x-3 mt-6">
        <Button variant="outline">Cancel</Button>
        <Button>Confirm</Button>
      </div>
    </div>
  </div>
</div>
```

---

This numbered design system provides a comprehensive reference for all visual and interactive elements in the TestHub/Squiz application. Each component is documented with usage examples, CSS specifications, and accessibility considerations to ensure consistent implementation across the entire platform.
