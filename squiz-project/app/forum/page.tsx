"use client"

import { useState, useEffect } from "react"
import { motion } from "framer-motion"
import { MessageSquare, Plus, Search, Filter, Eye, Heart, MessageCircle, Pin, CheckCircle2, Clock, User, Tag } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import DashboardLayout from "@/components/layout/DashboardLayout"
import { useAuth } from "@/hooks/useAuth"
import { toast } from "@/hooks/use-toast"
import Link from "next/link"

interface ForumPost {
  id: string
  title: string
  content: string
  author: {
    id: string
    name: string
    avatar: string
    role: string
  }
  category: string
  tags: string[]
  created_at: string
  updated_at: string
  views: number
  likes: number
  replies: number
  is_solved: boolean
  is_pinned: boolean
  images: string[]
  user_liked: boolean
}

export default function ForumPage() {
  const { user } = useAuth()
  const [posts, setPosts] = useState<ForumPost[]>([])
  const [filteredPosts, setFilteredPosts] = useState<ForumPost[]>([])
  const [searchTerm, setSearchTerm] = useState("")
  const [selectedCategory, setSelectedCategory] = useState<string>("all")
  const [activeTab, setActiveTab] = useState("all")
  const [isLoading, setIsLoading] = useState(true)
  const [showCreateModal, setShowCreateModal] = useState(false)
  
  // Create post form state
  const [newPost, setNewPost] = useState({
    title: "",
    content: "",
    category: "",
    tags: ""
  })
  const [isSubmitting, setIsSubmitting] = useState(false)

  useEffect(() => {
    fetchPosts()
  }, [])

  useEffect(() => {
    filterPosts()
  }, [searchTerm, selectedCategory, activeTab, posts])

  const fetchPosts = async () => {
    try {
      const response = await fetch(`/api/forum/posts`)
      if (response.ok) {
        const data = await response.json()
        setPosts(data)
      } else {
        toast({
          title: "Xəta",
          description: "Postları yükləmək mümkün olmadı",
          variant: "destructive",
        })
      }
    } catch (error) {
      console.error("Posts yükləmə xətası:", error)
      toast({
        title: "Xəta",
        description: "Postları yükləmək mümkün olmadı",
        variant: "destructive",
      })
    } finally {
      setIsLoading(false)
    }
  }

  const filterPosts = () => {
    let filtered = posts

    // Tab filter
    if (activeTab === "solved") {
      filtered = filtered.filter((post) => post.is_solved)
    } else if (activeTab === "unsolved") {
      filtered = filtered.filter((post) => !post.is_solved)
    } else if (activeTab === "my") {
      filtered = filtered.filter((post) => post.author.id === user?.id)
    }

    // Search filter
    if (searchTerm) {
      filtered = filtered.filter(
        (post) =>
          post.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
          post.content.toLowerCase().includes(searchTerm.toLowerCase()) ||
          post.tags.some((tag) => tag.toLowerCase().includes(searchTerm.toLowerCase()))
      )
    }

    // Category filter
    if (selectedCategory !== "all") {
      filtered = filtered.filter((post) => post.category === selectedCategory)
    }

    setFilteredPosts(filtered)
  }

  const handleCreatePost = async () => {
    if (!newPost.title.trim() || !newPost.content.trim() || !newPost.category) {
      toast({
        title: "Xəta",
        description: "Bütün tələb olunan sahələri doldurun",
        variant: "destructive",
      })
      return
    }

    setIsSubmitting(true)
    try {
      const token = localStorage.getItem("token")
      const response = await fetch('/api/forum/posts', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(newPost)
      })

      if (response.ok) {
        const createdPost = await response.json()
        setPosts([createdPost, ...posts])
        setNewPost({ title: "", content: "", category: "", tags: "" })
        setShowCreateModal(false)
        toast({
          title: "Uğurlu",
          description: "Post yaradıldı",
        })
      } else {
        const error = await response.json()
        toast({
          title: "Xəta",
          description: error.error || "Post yaradıla bilmədi",
          variant: "destructive",
        })
      }
    } catch (error) {
      console.error("Post yaratma xətası:", error)
      toast({
        title: "Xəta",
        description: "Post yaradıla bilmədi",
        variant: "destructive",
      })
    } finally {
      setIsSubmitting(false)
    }
  }

  const formatDate = (dateString: string) => {
    const date = new Date(dateString)
    const now = new Date()
    const diffInMinutes = Math.floor((now.getTime() - date.getTime()) / (1000 * 60))

    if (diffInMinutes < 1) return "İndi"
    if (diffInMinutes < 60) return `${diffInMinutes} dəqiqə əvvəl`
    if (diffInMinutes < 1440) return `${Math.floor(diffInMinutes / 60)} saat əvvəl`
    return date.toLocaleDateString('az-AZ')
  }

  const categories = ["Proqramlaşdırma", "Riyaziyyat", "Fen Elmləri", "Dil", "Dizayn", "Digər"]

  if (isLoading) {
    return (
      <DashboardLayout>
        <div className="flex items-center justify-center min-h-screen">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        </div>
      </DashboardLayout>
    )
  }

  return (
    <DashboardLayout>
      <div className="space-y-8 p-6">
        {/* Header */}
        <div className="flex flex-col md:flex-row md:items-center md:justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Forum - Sual Paylaşımı</h1>
            <p className="text-gray-600 mt-2">Suallarınızı paylaşın və cavablar alın</p>
          </div>

          <Dialog open={showCreateModal} onOpenChange={setShowCreateModal}>
            <DialogTrigger asChild>
              <Button className="bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 mt-4 md:mt-0">
                <Plus className="w-4 h-4 mr-2" />
                Yeni Sual
              </Button>
            </DialogTrigger>
            <DialogContent className="max-w-2xl">
              <DialogHeader>
                <DialogTitle>Yeni Sual Paylaş</DialogTitle>
                <DialogDescription>
                  Sualınızı paylaşın və cəmiyyətdən kömək alın
                </DialogDescription>
              </DialogHeader>

              <div className="space-y-4">
                <div className="space-y-2">
                  <Label htmlFor="title">Başlıq *</Label>
                  <Input
                    id="title"
                    placeholder="Sualınızın qısa başlığını yazın..."
                    value={newPost.title}
                    onChange={(e) => setNewPost({ ...newPost, title: e.target.value })}
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="category">Kateqoriya *</Label>
                  <Select
                    value={newPost.category}
                    onValueChange={(value) => setNewPost({ ...newPost, category: value })}
                  >
                    <SelectTrigger>
                      <SelectValue placeholder="Kateqoriya seçin" />
                    </SelectTrigger>
                    <SelectContent>
                      {categories.map((category) => (
                        <SelectItem key={category} value={category}>
                          {category}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="content">Sualınızın Təfərrüatı *</Label>
                  <Textarea
                    id="content"
                    placeholder="Sualınızı ətraflı izah edin..."
                    rows={6}
                    value={newPost.content}
                    onChange={(e) => setNewPost({ ...newPost, content: e.target.value })}
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="tags">Etiketlər (İstəyə görə)</Label>
                  <Input
                    id="tags"
                    placeholder="Etiketləri vergüllə ayıraraq yazın: javascript, react, css"
                    value={newPost.tags}
                    onChange={(e) => setNewPost({ ...newPost, tags: e.target.value })}
                  />
                </div>
              </div>

              <div className="flex justify-end gap-2 mt-6">
                <Button variant="outline" onClick={() => setShowCreateModal(false)}>
                  Ləğv Et
                </Button>
                <Button onClick={handleCreatePost} disabled={isSubmitting}>
                  {isSubmitting ? "Paylaşılır..." : "Sualı Paylaş"}
                </Button>
              </div>
            </DialogContent>
          </Dialog>
        </div>

        {/* Tabs */}
        <Tabs value={activeTab} onValueChange={setActiveTab}>
          <TabsList className="grid w-full grid-cols-4">
            <TabsTrigger value="all">Hamısı ({posts.length})</TabsTrigger>
            <TabsTrigger value="unsolved">Həllsiz ({posts.filter((p) => !p.is_solved).length})</TabsTrigger>
            <TabsTrigger value="solved">Həll Edilmiş ({posts.filter((p) => p.is_solved).length})</TabsTrigger>
            <TabsTrigger value="my">Mənim Suallarım ({posts.filter((p) => p.author.id === user?.id).length})</TabsTrigger>
          </TabsList>

          <TabsContent value={activeTab} className="space-y-6">
            {/* Filters */}
            <Card>
              <CardContent className="p-6">
                <div className="flex flex-col lg:flex-row gap-4">
                  {/* Search */}
                  <div className="flex-1">
                    <div className="relative">
                      <Search className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
                      <Input
                        placeholder="Suallar arasında axtarış..."
                        value={searchTerm}
                        onChange={(e) => setSearchTerm(e.target.value)}
                        className="pl-10"
                      />
                    </div>
                  </div>

                  {/* Category Filter */}
                  <Select value={selectedCategory} onValueChange={setSelectedCategory}>
                    <SelectTrigger className="w-full lg:w-48">
                      <Filter className="w-4 h-4 mr-2" />
                      <SelectValue placeholder="Kateqoriya" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="all">Bütün Kateqoriyalar</SelectItem>
                      {categories.map((category) => (
                        <SelectItem key={category} value={category}>
                          {category}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
              </CardContent>
            </Card>

            {/* Posts List */}
            <div className="space-y-4">
              {filteredPosts.length > 0 ? (
                filteredPosts.map((post, index) => (
                  <motion.div
                    key={post.id}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.5, delay: index * 0.1 }}
                  >
                    <Card className="hover:shadow-lg transition-all duration-300">
                      <CardContent className="p-6">
                        <div className="flex items-start justify-between">
                          <div className="flex-1">
                            <div className="flex items-center gap-2 mb-3">
                              {post.is_pinned && (
                                <Badge variant="secondary" className="bg-yellow-100 text-yellow-800">
                                  <Pin className="w-3 h-3 mr-1" />
                                  Sabitlənmiş
                                </Badge>
                              )}
                              {post.is_solved && (
                                <Badge variant="secondary" className="bg-green-100 text-green-800">
                                  <CheckCircle2 className="w-3 h-3 mr-1" />
                                  Həll Edilmiş
                                </Badge>
                              )}
                              <Badge variant="outline">{post.category}</Badge>
                            </div>

                            <Link
                              href={`/forum/post/${post.id}`}
                              className="text-xl font-semibold text-gray-900 hover:text-blue-600 transition-colors line-clamp-2"
                            >
                              {post.title}
                            </Link>

                            <p className="text-gray-600 mt-2 line-clamp-2">{post.content}</p>

                            {/* Tags */}
                            {post.tags.length > 0 && (
                              <div className="flex flex-wrap gap-1 mt-3">
                                {post.tags.slice(0, 4).map((tag) => (
                                  <Badge key={tag} variant="secondary" className="text-xs">
                                    <Tag className="w-3 h-3 mr-1" />
                                    {tag}
                                  </Badge>
                                ))}
                                {post.tags.length > 4 && (
                                  <Badge variant="secondary" className="text-xs">
                                    +{post.tags.length - 4}
                                  </Badge>
                                )}
                              </div>
                            )}

                            {/* Author and Stats */}
                            <div className="flex items-center justify-between mt-4">
                              <div className="flex items-center gap-3">
                                <div className="flex items-center gap-2">
                                  <User className="w-4 h-4 text-gray-400" />
                                  <span className="text-sm font-medium text-gray-700">
                                    {post.author.name}
                                  </span>
                                  <Badge variant="outline" className="text-xs">
                                    {post.author.role}
                                  </Badge>
                                </div>
                                <div className="flex items-center gap-1 text-xs text-gray-500">
                                  <Clock className="w-3 h-3" />
                                  {formatDate(post.created_at)}
                                </div>
                              </div>

                              <div className="flex items-center gap-4 text-sm text-gray-500">
                                <div className="flex items-center gap-1">
                                  <Eye className="w-4 h-4" />
                                  {post.views}
                                </div>
                                <div className="flex items-center gap-1">
                                  <Heart className="w-4 h-4" />
                                  {post.likes}
                                </div>
                                <div className="flex items-center gap-1">
                                  <MessageCircle className="w-4 h-4" />
                                  {post.replies}
                                </div>
                              </div>
                            </div>
                          </div>
                        </div>
                      </CardContent>
                    </Card>
                  </motion.div>
                ))
              ) : (
                <div className="text-center py-12">
                  <MessageSquare className="w-16 h-16 text-gray-400 mx-auto mb-4" />
                  <h3 className="text-lg font-medium text-gray-900 mb-2">Sual tapılmadı</h3>
                  <p className="text-gray-600 mb-6">
                    Axtarış kriterlərinizə uyğun sual tapılmadı.
                  </p>
                  <Button onClick={() => setShowCreateModal(true)}>
                    <Plus className="w-4 h-4 mr-2" />
                    İlk Sualı Siz Paylaşın
                  </Button>
                </div>
              )}
            </div>
          </TabsContent>
        </Tabs>
      </div>
    </DashboardLayout>
  )
}