"use client"

import React, { useEffect, useRef } from 'react'

interface MathJaxProps {
  math: string
  display?: boolean
  className?: string
  style?: React.CSSProperties
}

declare global {
  interface Window {
    MathJax: any
  }
}

export default function MathJax({ math, display = false, className = "", style }: MathJaxProps) {
  const mathRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    // Load MathJax script if not already loaded
    if (!window.MathJax) {
      const script = document.createElement('script')
      script.src = 'https://polyfill.io/v3/polyfill.min.js?features=es6'
      document.head.appendChild(script)

      const mathJaxScript = document.createElement('script')
      mathJaxScript.src = 'https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js'
      mathJaxScript.async = true
      document.head.appendChild(mathJaxScript)

      // Configure MathJax
      window.MathJax = {
        tex: {
          inlineMath: [['$', '$'], ['\\(', '\\)']],
          displayMath: [['$$', '$$'], ['\\[', '\\]']],
          processEscapes: true,
          processEnvironments: true,
        },
        options: {
          skipHtmlTags: ['script', 'noscript', 'style', 'textarea', 'pre'],
          ignoreHtmlClass: 'tex2jax_ignore',
          processHtmlClass: 'tex2jax_process'
        },
        startup: {
          ready: () => {
            window.MathJax.startup.defaultReady()
            renderMath()
          }
        }
      }
    } else {
      renderMath()
    }

    function renderMath() {
      if (window.MathJax && window.MathJax.typesetPromise) {
        if (mathRef.current) {
          window.MathJax.typesetPromise([mathRef.current]).catch((err: any) => {
            console.error('MathJax rendering error:', err)
          })
        }
      }
    }
  }, [math])

  const formattedMath = display ? `$$${math}$$` : `$${math}$`

  return (
    <div 
      ref={mathRef}
      className={`mathjax-container ${className}`}
      style={style}
      dangerouslySetInnerHTML={{ __html: formattedMath }}
    />
  )
}