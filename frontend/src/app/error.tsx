"use client"

import { useEffect } from "react"
import { Button } from "@/components/ui/button"

export default function GlobalError({
    error,
    reset,
}: {
    error: Error & { digest?: string }
    reset: () => void
}) {
    useEffect(() => {
        console.error("Unhandled error:", error)
    }, [error])

    return (
        <div className="flex min-h-screen items-center justify-center bg-background">
            <div className="text-center space-y-4 max-w-md px-6">
                <div className="text-4xl font-bold text-destructive">Something went wrong</div>
                <p className="text-muted-foreground text-sm">
                    An unexpected error occurred. This has been logged automatically.
                </p>
                <Button onClick={reset} variant="outline">
                    Try Again
                </Button>
            </div>
        </div>
    )
}
