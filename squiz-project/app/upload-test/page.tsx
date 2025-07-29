"use client"

import { useState } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import { Alert, AlertDescription } from "@/components/ui/alert"
import { Upload, CheckCircle, AlertCircle } from "lucide-react"
import ImageUploader from "@/components/ImageUploader"

interface UploadedImage {
  filename: string
  path: string
  base64: string
  size: number
  type: string
  uploadedAt: string
}

export default function ImageUploadDemo() {
  const [images, setImages] = useState<UploadedImage[]>([])
  const [description, setDescription] = useState("")
  const [title, setTitle] = useState("")
  const [message, setMessage] = useState<{ type: 'success' | 'error', text: string } | null>(null)

  const handleImageUploaded = (image: UploadedImage) => {
    setImages(prev => [...prev, image])
    setMessage({ type: 'success', text: `Şəkil "${image.filename}" uğurla yükləndi!` })
    
    // Clear message after 3 seconds
    setTimeout(() => setMessage(null), 3000)
  }

  const handleSaveProject = () => {
    if (!title.trim()) {
      setMessage({ type: 'error', text: 'Layihə adı tələb olunur' })
      return
    }

    if (images.length === 0) {
      setMessage({ type: 'error', text: 'Ən azı bir şəkil yükləyin' })
      return
    }

    // Here you would typically save to database
    const projectData = {
      title: title.trim(),
      description: description.trim(),
      images: images,
      createdAt: new Date().toISOString()
    }

    console.log('Layihə saxlanıldı:', projectData)
    setMessage({ type: 'success', text: 'Layihə uğurla saxlanıldı!' })
    
    // Reset form
    setTitle("")
    setDescription("")
    setImages([])
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 p-4">
      <div className="max-w-4xl mx-auto space-y-6">
        {/* Header */}
        <Card>
          <CardHeader className="text-center">
            <CardTitle className="flex items-center justify-center gap-2 text-2xl">
              <Upload className="w-6 h-6" />
              Şəkil Yükləmə Test Səhifəsi
            </CardTitle>
            <CardDescription>
              Şəkil yükləmə API-sini və komponentini test edin
            </CardDescription>
          </CardHeader>
        </Card>

        {/* Alert Messages */}
        {message && (
          <Alert variant={message.type === 'error' ? "destructive" : "default"} 
                className={message.type === 'success' ? "border-green-200 bg-green-50" : ""}>
            {message.type === 'success' ? (
              <CheckCircle className="h-4 w-4 text-green-600" />
            ) : (
              <AlertCircle className="h-4 w-4" />
            )}
            <AlertDescription className={message.type === 'success' ? "text-green-700" : ""}>
              {message.text}
            </AlertDescription>
          </Alert>
        )}

        {/* Project Form */}
        <Card>
          <CardHeader>
            <CardTitle>Yeni Layihə Yaradın</CardTitle>
            <CardDescription>
              Layihə məlumatlarını doldurun və şəkillər yükləyin
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="title">Layihə Adı</Label>
              <Input
                id="title"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                placeholder="Layihə adını daxil edin..."
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="description">Təsvir (İstəyə görə)</Label>
              <Textarea
                id="description"
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                placeholder="Layihə haqqında qısa məlumat..."
                rows={3}
              />
            </div>

            <Button 
              onClick={handleSaveProject}
              className="w-full bg-green-600 hover:bg-green-700"
              disabled={!title.trim() || images.length === 0}
            >
              Layihəni Saxla ({images.length} şəkil)
            </Button>
          </CardContent>
        </Card>

        {/* Image Uploader */}
        <ImageUploader
          onImageUploaded={handleImageUploaded}
          maxFiles={10}
          allowMultiple={true}
          showPreview={true}
        />

        {/* Statistics */}
        {images.length > 0 && (
          <Card>
            <CardHeader>
              <CardTitle>Yüklənən Şəkillər Statistikası</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-center">
                <div className="p-3 bg-blue-50 rounded-lg">
                  <p className="text-2xl font-bold text-blue-600">{images.length}</p>
                  <p className="text-sm text-blue-700">Cəmi Şəkil</p>
                </div>
                
                <div className="p-3 bg-green-50 rounded-lg">
                  <p className="text-2xl font-bold text-green-600">
                    {Math.round(images.reduce((total, img) => total + img.size, 0) / 1024)}
                  </p>
                  <p className="text-sm text-green-700">KB Ölçü</p>
                </div>
                
                <div className="p-3 bg-purple-50 rounded-lg">
                  <p className="text-2xl font-bold text-purple-600">
                    {new Set(images.map(img => img.type)).size}
                  </p>
                  <p className="text-sm text-purple-700">Format Növü</p>
                </div>
                
                <div className="p-3 bg-orange-50 rounded-lg">
                  <p className="text-2xl font-bold text-orange-600">
                    {images.length > 0 ? Math.round(images.reduce((total, img) => total + img.size, 0) / images.length / 1024) : 0}
                  </p>
                  <p className="text-sm text-orange-700">Orta KB</p>
                </div>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Raw Data Display for Debugging */}
        {images.length > 0 && (
          <Card>
            <CardHeader>
              <CardTitle>Debug Məlumatları</CardTitle>
              <CardDescription>
                Developer üçün - şəkil məlumatları (konsola baxın)
              </CardDescription>
            </CardHeader>
            <CardContent>
              <pre className="text-xs bg-gray-100 p-3 rounded overflow-x-auto">
                {JSON.stringify(images.map(img => ({
                  filename: img.filename,
                  size: img.size,
                  type: img.type,
                  base64Length: img.base64.length
                })), null, 2)}
              </pre>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  )
}