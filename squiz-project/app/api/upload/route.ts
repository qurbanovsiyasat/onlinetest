import { type NextRequest, NextResponse } from "next/server"
import fs from 'fs'
import path from 'path'

// Create uploads directory if it doesn't exist
const UPLOADS_DIR = path.join(process.cwd(), 'public', 'uploads')
if (!fs.existsSync(UPLOADS_DIR)) {
  fs.mkdirSync(UPLOADS_DIR, { recursive: true })
}

export async function POST(request: NextRequest) {
  try {
    const formData = await request.formData()
    const file = formData.get('file') as File
    
    if (!file) {
      return NextResponse.json({ error: "Fayl seçilməyib" }, { status: 400 })
    }

    // Validate file type (only image files)
    const allowedTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'image/webp']
    if (!allowedTypes.includes(file.type)) {
      return NextResponse.json({ 
        error: "Yalnız şəkil faylları qəbul edilir (JPEG, PNG, GIF, WebP)" 
      }, { status: 400 })
    }

    // Validate file size (max 5MB)
    const maxSize = 5 * 1024 * 1024 // 5MB
    if (file.size > maxSize) {
      return NextResponse.json({ 
        error: "Fayl ölçüsü maksimum 5MB ola bilər" 
      }, { status: 400 })
    }

    // Generate unique filename
    const timestamp = Date.now()
    const extension = path.extname(file.name)
    const filename = `${timestamp}_${Math.random().toString(36).substr(2, 9)}${extension}`
    
    // Convert file to buffer
    const bytes = await file.arrayBuffer()
    const buffer = Buffer.from(bytes)
    
    // Convert to base64 for storage
    const base64 = buffer.toString('base64')
    const mimeType = file.type
    const base64WithPrefix = `data:${mimeType};base64,${base64}`

    // Also save physical file for backup
    const filePath = path.join(UPLOADS_DIR, filename)
    fs.writeFileSync(filePath, buffer)

    // Return success response with both file path and base64
    return NextResponse.json({
      success: true,
      message: "Şəkil uğurla yükləndi",
      data: {
        filename,
        path: `/uploads/${filename}`,
        base64: base64WithPrefix,
        size: file.size,
        type: file.type,
        uploadedAt: new Date().toISOString()
      }
    })

  } catch (error) {
    console.error('Şəkil yükləmə xətası:', error)
    return NextResponse.json({ 
      error: "Şəkil yükləmə zamanı xəta baş verdi" 
    }, { status: 500 })
  }
}

// GET method to retrieve uploaded images list
export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url)
    const page = parseInt(searchParams.get('page') || '1')
    const limit = parseInt(searchParams.get('limit') || '10')
    
    // Read all files from uploads directory
    const files = fs.readdirSync(UPLOADS_DIR)
    const imageFiles = files.filter(file => {
      const ext = path.extname(file).toLowerCase()
      return ['.jpg', '.jpeg', '.png', '.gif', '.webp'].includes(ext)
    })

    // Sort by creation time (newest first)
    const sortedFiles = imageFiles
      .map(file => {
        const filePath = path.join(UPLOADS_DIR, file)
        const stats = fs.statSync(filePath)
        return {
          filename: file,
          path: `/uploads/${file}`,
          size: stats.size,
          createdAt: stats.birthtime.toISOString()
        }
      })
      .sort((a, b) => new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime())

    // Pagination
    const startIndex = (page - 1) * limit
    const endIndex = startIndex + limit
    const paginatedFiles = sortedFiles.slice(startIndex, endIndex)

    return NextResponse.json({
      success: true,
      data: {
        images: paginatedFiles,
        pagination: {
          page,
          limit,
          total: sortedFiles.length,
          totalPages: Math.ceil(sortedFiles.length / limit)
        }
      }
    })

  } catch (error) {
    console.error('Şəkil siyahısı xətası:', error)
    return NextResponse.json({ 
      error: "Şəkil siyahısı alınarkən xəta baş verdi" 
    }, { status: 500 })
  }
}

// DELETE method to remove uploaded images
export async function DELETE(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url)
    const filename = searchParams.get('filename')
    
    if (!filename) {
      return NextResponse.json({ error: "Fayl adı tələb olunur" }, { status: 400 })
    }

    const filePath = path.join(UPLOADS_DIR, filename)
    
    if (!fs.existsSync(filePath)) {
      return NextResponse.json({ error: "Fayl tapılmadı" }, { status: 404 })
    }

    // Delete the file
    fs.unlinkSync(filePath)

    return NextResponse.json({
      success: true,
      message: "Şəkil uğurla silindi"
    })

  } catch (error) {
    console.error('Şəkil silmə xətası:', error)
    return NextResponse.json({ 
      error: "Şəkil silinərkən xəta baş verdi" 
    }, { status: 500 })
  }
}