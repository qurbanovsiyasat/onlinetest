"use client"

import React, { useState } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import { Alert, AlertDescription } from "@/components/ui/alert"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Copy, Eye, Code, CheckCircle, AlertCircle } from "lucide-react"
import MathJax from "@/components/MathJax"

export default function MathJaxTest() {
  const [inlineMath, setInlineMath] = useState("x = \\frac{-b \\pm \\sqrt{b^2 - 4ac}}{2a}")
  const [displayMath, setDisplayMath] = useState("\\int_{-\\infty}^{\\infty} e^{-x^2} dx = \\sqrt{\\pi}")
  const [customMath, setCustomMath] = useState("")
  const [copied, setCopied] = useState<string>("")

  const examples = [
    {
      title: "Kvadrat tənlik",
      math: "x = \\frac{-b \\pm \\sqrt{b^2 - 4ac}}{2a}",
      description: "Kvadrat tənliyin həlli düsturu"
    },
    {
      title: "Eyler düsturu",
      math: "e^{i\\pi} + 1 = 0",
      description: "Riyaziyyatın ən gözəl düsturu"
    },
    {
      title: "İnteqral",
      math: "\\int_{0}^{\\infty} x^2 e^{-x} dx = 2",
      description: "Qeyri-məəyyən inteqral"
    },
    {
      title: "Matris",
      math: "\\begin{pmatrix} a & b \\\\ c & d \\end{pmatrix}",
      description: "2x2 matris"
    },
    {
      title: "Cəm",
      math: "\\sum_{n=1}^{\\infty} \\frac{1}{n^2} = \\frac{\\pi^2}{6}",
      description: "Basel problemi"
    },
    {
      title: "Həd",
      math: "\\lim_{x \\to 0} \\frac{\\sin x}{x} = 1",
      description: "Fundamental həd"
    }
  ]

  const copyToClipboard = (text: string, type: string) => {
    navigator.clipboard.writeText(text)
    setCopied(type)
    setTimeout(() => setCopied(""), 2000)
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 p-4">
      <div className="max-w-6xl mx-auto space-y-6">
        {/* Header */}
        <Card>
          <CardHeader className="text-center">
            <CardTitle className="flex items-center justify-center gap-2 text-2xl">
              <span className="text-2xl">∫</span>
              MathJax Test Səhifəsi
            </CardTitle>
            <CardDescription>
              Matematik düsturların render edilməsini test edin
            </CardDescription>
          </CardHeader>
        </Card>

        {/* Success Alert */}
        <Alert className="border-green-200 bg-green-50">
          <CheckCircle className="h-4 w-4 text-green-600" />
          <AlertDescription className="text-green-700">
            ✅ MathJax komponenti uğurla yaradıldı və işləyir!
          </AlertDescription>
        </Alert>

        <div className="grid lg:grid-cols-2 gap-6">
          {/* Left Column - Examples */}
          <div className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>Nümunə Düsturlar</CardTitle>
                <CardDescription>
                  Müxtəlif matematik ifadələrin nümunələri
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                {examples.map((example, index) => (
                  <div key={index} className="p-4 border rounded-lg bg-white">
                    <div className="flex items-center justify-between mb-2">
                      <h4 className="font-medium text-sm">{example.title}</h4>
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => copyToClipboard(example.math, `example-${index}`)}
                        className="h-6 px-2 text-xs"
                      >
                        {copied === `example-${index}` ? (
                          <CheckCircle className="w-3 h-3" />
                        ) : (
                          <Copy className="w-3 h-3" />
                        )}
                      </Button>
                    </div>
                    <p className="text-xs text-gray-600 mb-3">{example.description}</p>
                    <div className="bg-gray-50 p-3 rounded border text-center">
                      <MathJax math={example.math} display={true} />
                    </div>
                    <code className="text-xs bg-gray-100 p-1 rounded mt-2 block">
                      {example.math}
                    </code>
                  </div>
                ))}
              </CardContent>
            </Card>
          </div>

          {/* Right Column - Interactive Testing */}
          <div className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>İnteraktiv Test</CardTitle>
                <CardDescription>
                  Öz düsturlarınızı test edin
                </CardDescription>
              </CardHeader>
              <CardContent>
                <Tabs defaultValue="inline" className="w-full">
                  <TabsList className="grid w-full grid-cols-2">
                    <TabsTrigger value="inline">Inline Math</TabsTrigger>
                    <TabsTrigger value="display">Display Math</TabsTrigger>
                  </TabsList>
                  
                  <TabsContent value="inline" className="space-y-4">
                    <div className="space-y-2">
                      <Label htmlFor="inline-input">Inline düstur daxil edin:</Label>
                      <div className="flex gap-2">
                        <Input
                          id="inline-input"
                          value={inlineMath}
                          onChange={(e) => setInlineMath(e.target.value)}
                          placeholder="x^2 + y^2 = z^2"
                          className="font-mono text-sm"
                        />
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => copyToClipboard(inlineMath, 'inline')}
                        >
                          {copied === 'inline' ? <CheckCircle className="w-4 h-4" /> : <Copy className="w-4 h-4" />}
                        </Button>
                      </div>
                    </div>
                    
                    <div className="p-4 bg-white border rounded-lg text-center min-h-16 flex items-center justify-center">
                      <span>Mətndə </span>
                      <MathJax math={inlineMath} display={false} className="mx-2" />
                      <span> inline göstərilir.</span>
                    </div>
                  </TabsContent>
                  
                  <TabsContent value="display" className="space-y-4">
                    <div className="space-y-2">
                      <Label htmlFor="display-input">Display düstur daxil edin:</Label>
                      <div className="flex gap-2">
                        <Input
                          id="display-input"
                          value={displayMath}
                          onChange={(e) => setDisplayMath(e.target.value)}
                          placeholder="\\sum_{n=1}^{\\infty} \\frac{1}{n^2}"
                          className="font-mono text-sm"
                        />
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => copyToClipboard(displayMath, 'display')}
                        >
                          {copied === 'display' ? <CheckCircle className="w-4 h-4" /> : <Copy className="w-4 h-4" />}
                        </Button>
                      </div>
                    </div>
                    
                    <div className="p-6 bg-white border rounded-lg text-center min-h-20 flex items-center justify-center">
                      <MathJax math={displayMath} display={true} />
                    </div>
                  </TabsContent>
                </Tabs>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Öz Düsturunuz</CardTitle>
                <CardDescription>
                  İstədiyiniz düsturu yazıb test edin
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-2">
                  <Label htmlFor="custom-math">LaTeX düstur:</Label>
                  <Textarea
                    id="custom-math"
                    value={customMath}
                    onChange={(e) => setCustomMath(e.target.value)}
                    placeholder="\\begin{align}
x &= a + b \\\\
y &= c + d
\\end{align}"
                    className="font-mono text-sm"
                    rows={4}
                  />
                </div>
                
                {customMath && (
                  <div className="p-4 bg-white border rounded-lg text-center min-h-16 flex items-center justify-center">
                    <MathJax math={customMath} display={true} />
                  </div>
                )}
                
                {!customMath && (
                  <div className="p-4 bg-gray-50 border rounded-lg text-center text-gray-500">
                    Düstur daxil etdikdən sonra burada görünəcək
                  </div>
                )}
              </CardContent>
            </Card>

            {/* LaTeX Guide */}
            <Card>
              <CardHeader>
                <CardTitle>LaTeX İpuçları</CardTitle>
                <CardDescription>
                  Tez-tez istifadə olunan simvollar
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-2 gap-2 text-sm">
                  <div className="space-y-1">
                    <code>x^2</code> → xüsusi
                    <br />
                    <code>x_1</code> → alt indeks
                    <br />
                    <code>\\frac{a}{b}</code> → kəsr
                    <br />
                    <code>\\sqrt{x}</code> → kök
                  </div>
                  <div className="space-y-1">
                    <code>\\sum</code> → cəm
                    <br />
                    <code>\\int</code> → inteqral
                    <br />
                    <code>\\alpha</code> → yunan hərfləri
                    <br />
                    <code>\\infty</code> → sonsuzluq
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </div>
  )
}