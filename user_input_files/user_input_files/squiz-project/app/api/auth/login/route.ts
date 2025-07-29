import { type NextRequest, NextResponse } from "next/server"
import { getUsers } from "@/lib/storage"

export async function POST(request: NextRequest) {
  try {
    const { email, password } = await request.json()

    // Get users from persistent storage
    const users = getUsers()

    // Find user
    const user = users.find((u) => u.email === email && u.password === password)

    if (!user) {
      return NextResponse.json({ detail: "Yanlış e-poçt və ya şifrə" }, { status: 401 })
    }

    // Generate mock JWT token
    const token = `mock-jwt-token-${user.id}-${Date.now()}`

    // Return user data without password
    const { password: _, ...userWithoutPassword } = user

    return NextResponse.json({
      access_token: token,
      token_type: "bearer",
      user: userWithoutPassword,
    })
  } catch (error) {
    return NextResponse.json({ detail: "Server xətası" }, { status: 500 })
  }
}
