import { type NextRequest, NextResponse } from "next/server"
import { getForumPosts, saveForumPosts, getUsers } from "@/lib/storage"

// GET - List all forum posts
export async function GET(request: NextRequest) {
  try {
    const searchParams = request.nextUrl.searchParams
    const category = searchParams.get('category')
    const search = searchParams.get('search')

    let posts = getForumPosts()

    // Filter by category
    if (category && category !== 'all') {
      posts = posts.filter(post => post.category === category)
    }

    // Filter by search term
    if (search) {
      const searchLower = search.toLowerCase()
      posts = posts.filter(post =>
        post.title.toLowerCase().includes(searchLower) ||
        post.content.toLowerCase().includes(searchLower) ||
        post.tags.some((tag: string) => tag.toLowerCase().includes(searchLower))
      )
    }

    // Sort by newest first
    posts.sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime())

    return NextResponse.json(posts)
  } catch (error) {
    console.error("Forum postları yükləmə xətası:", error)
    return NextResponse.json({ error: "Server xətası" }, { status: 500 })
  }
}

// POST - Create new forum post
export async function POST(request: NextRequest) {
  try {
    const authHeader = request.headers.get("authorization")
    if (!authHeader || !authHeader.startsWith("Bearer ")) {
      return NextResponse.json({ error: "Giriş tələb olunur" }, { status: 401 })
    }

    // Get user from token
    const token = authHeader.substring(7)
    const userId = token.split("-")[3]
    const users = getUsers()
    const user = users.find(u => u.id === userId)

    if (!user) {
      return NextResponse.json({ error: "İstifadəçi tapılmadı" }, { status: 401 })
    }

    const body = await request.json()
    const { title, content, category, tags, images = [] } = body

    // Validation
    if (!title || !content || !category) {
      return NextResponse.json({ error: "Başlıq, məzmun və kateqoriya tələb olunur" }, { status: 400 })
    }

    // Get current posts
    const posts = getForumPosts()

    // Create new post
    const newPost = {
      id: Date.now().toString(),
      title,
      content,
      category,
      tags: Array.isArray(tags) ? tags : (tags ? tags.split(",").map((tag: string) => tag.trim()) : []),
      images: images || [],
      author: {
        id: user.id,
        name: user.name,
        avatar: user.avatar || "",
        role: user.role,
      },
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
      views: 0,
      likes: 0,
      replies: 0,
      is_solved: false,
      is_pinned: false,
      user_liked: false,
    }

    posts.push(newPost)
    saveForumPosts(posts)

    return NextResponse.json(newPost, { status: 201 })
  } catch (error) {
    console.error("Post yaratma xətası:", error)
    return NextResponse.json({ error: "Daxili server xətası" }, { status: 500 })
  }
}