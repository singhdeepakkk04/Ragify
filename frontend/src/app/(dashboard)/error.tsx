"use client"

import { useEffect } from "react"
import { Button } from "@/components/ui/button"
import { AlertTriangle, RotateCcw, Home } from "lucide-react"
import Link from "next/link"

export default function DashboardError({
    error,
    reset,
}: {
    error: Error & { digest?: string }
    reset: () => void
}) {
    useEffect(() => {
        console.error("Dashboard error:", error)
    }, [error])

    return (
        <div className="flex h-[60vh] items-center justify-center">
            <div className="text-center space-y-4 max-w-md px-6">
                <AlertTriangle className="h-10 w-10 text-destructive mx-auto" />
                <h2 className="text-xl font-semibold">Dashboard Error</h2>
                <p className="text-muted-foreground text-sm">
                    {error.message || "Something went wrong loading this page."}
                </p>
                <div className="flex items-center justify-center gap-3">
                    <Button onClick={reset} variant="outline" size="sm">
                        <RotateCcw className="h-4 w-4 mr-2" /> Retry
                    </Button>
                    <Link href="/dashboard">
                        <Button variant="ghost" size="sm">
                            <Home className="h-4 w-4 mr-2" /> Dashboard
                        </Button>
                    </Link>
                </div>
            </div>
        </div>
    )
}
