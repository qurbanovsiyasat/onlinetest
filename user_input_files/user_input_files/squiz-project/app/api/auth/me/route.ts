import { type NextRequest, NextResponse } from "next/server"
import { getUsers } from "@/lib/storage"

export async function GET(request: NextRequest) {
  try {
    const authHeader = request.headers.get("authorization")

    if (!authHeader || !authHeader.startsWith("Bearer ")) {
      return NextResponse.json({ detail: "Token tələb olunur" }, { status: 401 })
    }

    const token = authHeader.substring(7)

    // Extract user ID from mock token
    const userId = token.split("-")[3]

    // Get users from persistent storage
    const users = getUsers()
    const user = users.find((u) => u.id === userId)

    if (!user) {
      return NextResponse.json({ detail: "Yanlış token" }, { status: 401 })
    }

    // Return user data without password
    const { password: _, ...userWithoutPassword } = user

    return NextResponse.json(userWithoutPassword)
  } catch (error) {
    return NextResponse.json({ detail: "Server xətası" }, { status: 500 })
  }
}
