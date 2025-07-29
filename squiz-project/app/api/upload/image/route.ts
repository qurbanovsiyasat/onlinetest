import { type NextRequest, NextResponse } from "next/server"

export async function POST(request: NextRequest) {
  try {
    const formData = await request.formData()
    const file = formData.get("image") as File

    if (!file) {
      return NextResponse.json({ error: "Fayl tapılmadı" }, { status: 400 })
    }

    // Fayl növünü yoxla
    if (!file.type.startsWith("image/")) {
      return NextResponse.json({ error: "Yalnız şəkil faylları qəbul edilir" }, { status: 400 })
    }

    // Fayl ölçüsünü yoxla (5MB maksimum)
    if (file.size > 5 * 1024 * 1024) {
      return NextResponse.json({ error: "Fayl ölçüsü 5MB-dan böyük ola bilməz" }, { status: 400 })
    }

    // Convert image to base64 for frontend display
    const bytes = await file.arrayBuffer()
    const buffer = Buffer.from(bytes)
    const base64 = buffer.toString('base64')
    const base64Url = `data:${file.type};base64,${base64}`

    return NextResponse.json({
      url: base64Url,
      filename: file.name,
      size: file.size,
      type: file.type,
      success: true
    })
  } catch (error) {
    console.error("Şəkil yükləmə xətası:", error)
    return NextResponse.json({ error: "Şəkil yükləmə zamanı xəta baş verdi" }, { status: 500 })
  }
}
