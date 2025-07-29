import { type NextRequest, NextResponse } from "next/server"
import { getUsers, saveUsers } from "@/lib/storage"

export async function POST(request: NextRequest) {
  try {
    const { email, password, name } = await request.json()

    // Validation
    if (!email || !password || !name) {
      return NextResponse.json({ detail: "Bütün sahələr tələb olunur" }, { status: 400 })
    }

    if (password.length < 6) {
      return NextResponse.json({ detail: "Şifrə ən azı 6 simvol olmalıdır" }, { status: 400 })
    }

    // Get current users
    const users = getUsers()

    // Check if user already exists
    const existingUser = users.find((u) => u.email === email)
    if (existingUser) {
      return NextResponse.json({ detail: "Bu e-poçt ünvanı artıq qeydiyyatdan keçib" }, { status: 400 })
    }

    // Create new user
    const newUser = {
      id: String(users.length + 1),
      email,
      password, // In real app, this would be hashed
      name,
      role: "user" as const,
      is_active: true,
      created_at: new Date().toISOString(),
      is_private: false,
      follower_count: 0,
      following_count: 0,
    }

    users.push(newUser)
    
    // Save users to persistent storage
    saveUsers(users)

    // Generate mock JWT token
    const token = `mock-jwt-token-${newUser.id}-${Date.now()}`

    // Return user data without password and include token
    const { password: _, ...userWithoutPassword } = newUser

    return NextResponse.json({
      access_token: token,
      token_type: "bearer",
      user: userWithoutPassword,
    }, { status: 201 })
  } catch (error) {
    console.error("Qeydiyyat xətası:", error)
    return NextResponse.json({ detail: "Server xətası" }, { status: 500 })
  }
}
