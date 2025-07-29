'use client'

import { useEffect, useRef, useState } from 'react'

interface MathRendererProps {
  math: string
  display?: boolean
  className?: string
}

export default function MathRenderer({ math, display = false, className = '' }: MathRendererProps) {
  const [rendered, setRendered] = useState('')
  
  useEffect(() => {
    // Simple math renderer for common symbols
    const renderSimpleMath = (mathText: string) => {
      return mathText
        .replace(/\^{([^}]+)}/g, '<sup>$1</sup>')
        .replace(/\^(\w+)/g, '<sup>$1</sup>')
        .replace(/_{([^}]+)}/g, '<sub>$1</sub>')
        .replace(/_(\w+)/g, '<sub>$1</sub>')
        .replace(/\\frac{([^}]+)}{([^}]+)}/g, '<span class="fraction"><span class="numerator">$1</span><span class="denominator">$2</span></span>')
        .replace(/\\sqrt{([^}]+)}/g, '√($1)')
        .replace(/\\pi/g, 'π')
        .replace(/\\alpha/g, 'α')
        .replace(/\\beta/g, 'β')
        .replace(/\\gamma/g, 'γ')
        .replace(/\\delta/g, 'δ')
        .replace(/\\theta/g, 'θ')
        .replace(/\\lambda/g, 'λ')
        .replace(/\\mu/g, 'μ')
        .replace(/\\sigma/g, 'σ')
        .replace(/\\omega/g, 'ω')
        .replace(/\\sum/g, '∑')
        .replace(/\\int/g, '∫')
        .replace(/\\infty/g, '∞')
        .replace(/\\pm/g, '±')
        .replace(/\\times/g, '×')
        .replace(/\\div/g, '÷')
        .replace(/\\leq/g, '≤')
        .replace(/\\geq/g, '≥')
        .replace(/\\neq/g, '≠')
        .replace(/\\approx/g, '≈')
    }
    
    setRendered(renderSimpleMath(math))
  }, [math])

  return (
    <>
      <style jsx>{`
        .fraction {
          display: inline-block;
          vertical-align: middle;
          text-align: center;
        }
        .numerator {
          display: block;
          border-bottom: 1px solid currentColor;
          font-size: 0.8em;
          line-height: 1.2;
        }
        .denominator {
          display: block;
          font-size: 0.8em;
          line-height: 1.2;
        }
      `}</style>
      <span 
        className={`math-renderer ${display ? 'block text-center text-lg' : 'inline'} ${className}`}
        dangerouslySetInnerHTML={{ __html: rendered }}
      />
    </>
  )
}

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

  return parts
}
