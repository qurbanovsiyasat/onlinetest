"use client"

import React, { useState, useRef } from 'react'
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Alert, AlertDescription } from "@/components/ui/alert"
import { Progress } from "@/components/ui/progress"
import { Upload, X, Image as ImageIcon, CheckCircle, AlertCircle, Trash2 } from "lucide-react"

interface UploadedImage {
  filename: string
  path: string
  base64: string
  size: number
  type: string
  uploadedAt: string
}

interface ImageUploaderProps {
  onImageUploaded?: (image: UploadedImage) => void
  maxFiles?: number
  allowMultiple?: boolean
  showPreview?: boolean
  className?: string
}

export default function ImageUploader({
  onImageUploaded,
  maxFiles = 5,
  allowMultiple = true,
  showPreview = true,
  className = ""
}: ImageUploaderProps) {
  const [uploadedImages, setUploadedImages] = useState<UploadedImage[]>([])
  const [isUploading, setIsUploading] = useState(false)
  const [uploadProgress, setUploadProgress] = useState(0)
  const [error, setError] = useState<string>("")
  const [success, setSuccess] = useState<string>("")
  const fileInputRef = useRef<HTMLInputElement>(null)

  const handleFileSelect = () => {
    fileInputRef.current?.click()
  }

  const handleFileChange = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const files = event.target.files
    if (!files || files.length === 0) return

    // Check file count limit
    if (uploadedImages.length + files.length > maxFiles) {
      setError(`Maksimum ${maxFiles} şəkil yükləyə bilərsiniz`)
      return
    }

    setError("")
    setSuccess("")
    setIsUploading(true)
    setUploadProgress(0)

    try {
      const uploadPromises = Array.from(files).map(async (file, index) => {
        const formData = new FormData()
        formData.append('file', file)

        const response = await fetch(`${window.location.origin}/api/upload`, {
          method: 'POST',
          body: formData,
        })

        // Update progress
        const progress = ((index + 1) / files.length) * 100
        setUploadProgress(progress)

        if (!response.ok) {
          const errorData = await response.json()
          throw new Error(errorData.error || 'Yükləmə uğursuz')
        }

        return await response.json()
      })

      const results = await Promise.all(uploadPromises)
      
      const newImages = results.map(result => result.data)
      setUploadedImages(prev => [...prev, ...newImages])
      
      // Call callback for each uploaded image
      newImages.forEach(image => {
        onImageUploaded?.(image)
      })

      setSuccess(`${newImages.length} şəkil uğurla yükləndi`)
      
    } catch (error: any) {
      setError(error.message || 'Şəkil yükləmə zamanı xəta baş verdi')
    } finally {
      setIsUploading(false)
      setUploadProgress(0)
      // Reset file input
      if (fileInputRef.current) {
        fileInputRef.current.value = ''
      }
    }
  }

  const handleRemoveImage = (index: number) => {
    setUploadedImages(prev => prev.filter((_, i) => i !== index))
    setError("")
    setSuccess("")
  }

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes'
    const k = 1024
    const sizes = ['Bytes', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
  }

  return (
    <Card className={`w-full ${className}`}>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <ImageIcon className="w-5 h-5" />
          Şəkil Yükləyici
        </CardTitle>
        <CardDescription>
          JPEG, PNG, GIF və WebP formatlarında maksimum 5MB ölçüsündə şəkillər yükləyə bilərsiniz
        </CardDescription>
      </CardHeader>

      <CardContent className="space-y-4">
        {/* Error Alert */}
        {error && (
          <Alert variant="destructive">
            <AlertCircle className="h-4 w-4" />
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}

        {/* Success Alert */}
        {success && (
          <Alert className="border-green-200 bg-green-50">
            <CheckCircle className="h-4 w-4 text-green-600" />
            <AlertDescription className="text-green-700">{success}</AlertDescription>
          </Alert>
        )}

        {/* Upload Progress */}
        {isUploading && (
          <div className="space-y-2">
            <div className="flex items-center justify-between text-sm">
              <span>Yüklənir...</span>
              <span>{Math.round(uploadProgress)}%</span>
            </div>
            <Progress value={uploadProgress} className="w-full" />
          </div>
        )}

        {/* Upload Button */}
        <div className="flex flex-col items-center">
          <input
            ref={fileInputRef}
            type="file"
            accept="image/*"
            multiple={allowMultiple}
            onChange={handleFileChange}
            className="hidden"
          />
          
          <Button
            onClick={handleFileSelect}
            disabled={isUploading || uploadedImages.length >= maxFiles}
            className="w-full h-32 border-2 border-dashed border-gray-300 hover:border-blue-500 bg-transparent hover:bg-blue-50 text-gray-600 hover:text-blue-600"
            variant="outline"
          >
            <div className="flex flex-col items-center gap-2">
              <Upload className="w-8 h-8" />
              <div className="text-center">
                <p className="font-medium">Şəkil seçin</p>
                <p className="text-sm text-gray-500">
                  və ya bura sürükləyin ({uploadedImages.length}/{maxFiles})
                </p>
              </div>
            </div>
          </Button>
        </div>

        {/* Image Previews */}
        {showPreview && uploadedImages.length > 0 && (
          <div className="space-y-3">
            <h4 className="font-medium text-sm">Yüklənən Şəkillər:</h4>
            <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
              {uploadedImages.map((image, index) => (
                <div key={index} className="relative group">
                  <div className="aspect-square rounded-lg overflow-hidden bg-gray-100">
                    <img
                      src={image.base64}
                      alt={`Yüklənən şəkil ${index + 1}`}
                      className="w-full h-full object-cover"
                    />
                  </div>
                  
                  {/* Remove Button */}
                  <Button
                    size="sm"
                    variant="destructive"
                    onClick={() => handleRemoveImage(index)}
                    className="absolute top-1 right-1 w-6 h-6 p-0 opacity-0 group-hover:opacity-100 transition-opacity"
                  >
                    <X className="w-3 h-3" />
                  </Button>
                  
                  {/* File Info */}
                  <div className="mt-1 text-xs text-gray-500 text-center">
                    <p className="truncate">{image.filename}</p>
                    <p>{formatFileSize(image.size)}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Upload Summary */}
        {uploadedImages.length > 0 && (
          <div className="text-sm text-gray-600 text-center">
            <p>
              {uploadedImages.length} şəkil yükləndi • Cəmi ölçü: {" "}
              {formatFileSize(uploadedImages.reduce((total, img) => total + img.size, 0))}
            </p>
          </div>
        )}
      </CardContent>
    </Card>
  )
}