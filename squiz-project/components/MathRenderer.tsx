'use client'

import { useEffect, useRef } from 'react'

declare global {
  interface Window {
    MathJax: any
  }
}

interface MathRendererProps {
  math: string
  display?: boolean
  className?: string
}

export default function MathRenderer({ math, display = false, className = '' }: MathRendererProps) {
  const containerRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    const loadMathJax = async () => {
      if (!window.MathJax) {
        // Load MathJax via CDN
        const script = document.createElement('script')
        script.src = 'https://polyfill.io/v3/polyfill.min.js?features=es6'
        document.head.appendChild(script)
        
        const mathJaxScript = document.createElement('script')
        mathJaxScript.src = 'https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js'
        mathJaxScript.async = true
        
        // Configure MathJax
        window.MathJax = {
          tex: {
            inlineMath: [['$', '$'], ['\\(', '\\)']],
            displayMath: [['$$', '$$'], ['\\[', '\\]']],
            processEscapes: true,
            processEnvironments: true
          },
          options: {
            skipHtmlTags: ['script', 'noscript', 'style', 'textarea', 'pre'],
            ignoreHtmlClass: 'tex2jax_ignore',
            processHtmlClass: 'tex2jax_process'
          }
        }
        
        document.head.appendChild(mathJaxScript)
        
        mathJaxScript.onload = () => {
          renderMath()
        }
      } else {
        renderMath()
      }
    }

    const renderMath = () => {
      if (window.MathJax && containerRef.current) {
        // Clear previous content
        containerRef.current.innerHTML = ''
        
        // Add the math content
        const mathElement = document.createElement(display ? 'div' : 'span')
        mathElement.textContent = display ? `$$${math}$$` : `$${math}$`
        containerRef.current.appendChild(mathElement)
        
        // Process the math
        window.MathJax.typesetPromise([containerRef.current]).catch((err: any) => {
          console.error('MathJax rendering error:', err)
        })
      }
    }

    loadMathJax()
  }, [math, display])

  return (
    <div 
      ref={containerRef} 
      className={`math-renderer ${display ? 'block text-center' : 'inline'} ${className}`}
    />
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
