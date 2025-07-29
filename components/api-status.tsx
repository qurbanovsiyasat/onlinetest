"use client"

import { useState, useEffect } from "react"
import { Badge } from "@/components/ui/badge"
import { Card, CardContent } from "@/components/ui/card"
import { config } from "@/lib/config"
import { apiMethods } from "@/lib/api"
import { Wifi, WifiOff, AlertCircle } from "lucide-react"

export function ApiStatus() {
  const [status, setStatus] = useState<"connected" | "disconnected" | "error">("disconnected")
  const [lastCheck, setLastCheck] = useState<Date | null>(null)

  const checkApiHealth = async () => {
    try {
      await apiMethods.health.check()
      setStatus("connected")
      setLastCheck(new Date())
    } catch (error) {
      console.warn("API Health check failed:", error)
      setStatus("error")
      setLastCheck(new Date())
    }
  }

  useEffect(() => {
    // Initial check
    checkApiHealth()

    // Check every 30 seconds
    const interval = setInterval(checkApiHealth, 30000)

    return () => clearInterval(interval)
  }, [])

  if (!config.isDevelopment) {
    return null // Only show in development
  }

  const getStatusColor = () => {
    switch (status) {
      case "connected":
        return "bg-green-500"
      case "error":
        return "bg-red-500"
      default:
        return "bg-yellow-500"
    }
  }

  const getStatusIcon = () => {
    switch (status) {
      case "connected":
        return <Wifi className="w-3 h-3" />
      case "error":
        return <AlertCircle className="w-3 h-3" />
      default:
        return <WifiOff className="w-3 h-3" />
    }
  }

  const getStatusText = () => {
    switch (status) {
      case "connected":
        return "API Bağlı"
      case "error":
        return "API Hatası"
      default:
        return "Bağlanıyor..."
    }
  }

  return (
    <div className="fixed bottom-4 right-4 z-50">
      <Card className="w-auto">
        <CardContent className="p-3">
          <div className="flex items-center space-x-2">
            <Badge variant="outline" className={`${getStatusColor()} text-white border-0`}>
              {getStatusIcon()}
              <span className="ml-1 text-xs">{getStatusText()}</span>
            </Badge>
            <div className="text-xs text-gray-500">
              {lastCheck && (
                <span>
                  {lastCheck.toLocaleTimeString("tr-TR", {
                    hour: "2-digit",
                    minute: "2-digit",
                    second: "2-digit",
                  })}
                </span>
              )}
            </div>
          </div>
          <div className="text-xs text-gray-400 mt-1">{config.backendUrl}</div>
        </CardContent>
      </Card>
    </div>
  )
}
