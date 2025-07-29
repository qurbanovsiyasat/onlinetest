'use client'

// Utility function to detect if text contains math
export function containsMath(text: string): boolean {
  return /\$.*?\$|\\\(.*?\\\)|\\\[.*?\\\]|\$\$.*?\$\$/.test(text)
}

// Utility function to parse text with math
export function parseMathText(text: string) {
  const parts: { type: 'text' | 'math'; content: string; display?: boolean }[] = []
  let currentIndex = 0

  // Regex to match different math delimiters
  const mathRegex = /(\$\$[\s\S]*?\$\$|\\\[[\s\S]*?\\\]|\$[^$]*?\$|\\\([^)]*?\\\))/g
  let match

  while ((match = mathRegex.exec(text)) !== null) {
    // Add text before math
    if (match.index > currentIndex) {
      parts.push({
        type: 'text',
        content: text.slice(currentIndex, match.index)
      })
    }

    // Add math content
    const mathContent = match[1]
    let display = false
    let cleanMath = mathContent

    if (mathContent.startsWith('$$') && mathContent.endsWith('$$')) {
      display = true
      cleanMath = mathContent.slice(2, -2)
    } else if (mathContent.startsWith('\\[') && mathContent.endsWith('\\]')) {
      display = true
      cleanMath = mathContent.slice(2, -2)
    } else if (mathContent.startsWith('$') && mathContent.endsWith('$')) {
      cleanMath = mathContent.slice(1, -1)
    } else if (mathContent.startsWith('\\(') && mathContent.endsWith('\\)')) {
      cleanMath = mathContent.slice(2, -2)
    }

    parts.push({
      type: 'math',
      content: cleanMath,
      display
    })

    currentIndex = match.index + match[0].length
  }

  // Add remaining text
  if (currentIndex < text.length) {
    parts.push({
      type: 'text',
      content: text.slice(currentIndex)
    })
  }

  // If no math found, return single text part
  if (parts.length === 0) {
    parts.push({
      type: 'text',
      content: text
    })
  }

  return parts
}

interface MathTextRendererProps {
  text: string
  className?: string
}

export default function MathTextRenderer({ text, className = '' }: MathTextRendererProps) {
  const parts = parseMathText(text)

  return (
    <div className={className}>
      {parts.map((part, index) => (
        <span key={index}>
          {part.type === 'text' ? (
            part.content
          ) : (
            <MathRenderer 
              math={part.content} 
              display={part.display}
              className="mx-1"
            />
          )}
        </span>
      ))}
    </div>
  )
}

// Component for math input with preview
interface MathInputProps {
  value: string
  onChange: (value: string) => void
  placeholder?: string
  className?: string
}

export function MathInput({ value, onChange, placeholder = "Riyazi ifadə daxil edin...", className = '' }: MathInputProps) {
  return (
    <div className={`space-y-2 ${className}`}>
      <div>
        <label className="text-sm font-medium text-gray-700">
          Mətin (LaTeX dəstəklənir: $...$ və $$...$$)
        </label>
        <textarea
          value={value}
          onChange={(e) => onChange(e.target.value)}
          placeholder={placeholder}
          className="w-full mt-1 p-3 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          rows={3}
        />
      </div>
      
      {value && (
        <div className="p-3 bg-gray-50 border border-gray-200 rounded-md">
          <label className="text-sm font-medium text-gray-700 block mb-2">
            Önizləmə:
          </label>
          <MathTextRenderer text={value} className="prose max-w-none" />
        </div>
      )}
      
      <div className="text-xs text-gray-500">
        <p><strong>Nümunələr:</strong></p>
        <ul className="list-disc list-inside space-y-1">
          <li>Kəsr: <code>$\frac{'{a}'}{'{b}'}$</code></li>
          <li>Köklü: <code>$\sqrt{'{a^2 + b^2}'}$</code></li>
          <li>Üst/alt indeks: <code>$x^{'{2}'} + y_{'{1}'}$</code></li>
          <li>Yunan hərfləri: <code>$\alpha, \beta, \gamma$</code></li>
          <li>Böyük riyazi: <code>$$\sum_{'{i=1}'}^{'{n}'} x_i$$</code></li>
        </ul>
      </div>
    </div>
  )
}
