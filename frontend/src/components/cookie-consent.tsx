"use client"

import { useState, useEffect } from "react"
import { Button } from "@/components/ui/button"
import Link from "next/link"

export function CookieConsent() {
    const [visible, setVisible] = useState(false)

    useEffect(() => {
        const consent = localStorage.getItem("cookie-consent")
        if (!consent) setVisible(true)
    }, [])

    const accept = () => {
        localStorage.setItem("cookie-consent", "accepted")
        setVisible(false)
    }

    const decline = () => {
        localStorage.setItem("cookie-consent", "declined")
        setVisible(false)
    }

    if (!visible) return null

    return (
        <div className="fixed bottom-0 left-0 right-0 z-50 bg-card border-t border-border p-4 shadow-lg animate-in slide-in-from-bottom duration-300">
            <div className="max-w-5xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-4">
                <p className="text-sm text-muted-foreground text-center sm:text-left">
                    We use essential cookies for authentication. See our{" "}
                    <Link href="/cookies" className="underline hover:text-foreground">
                        Cookie Policy
                    </Link>{" "}
                    for details.
                </p>
                <div className="flex items-center gap-2 shrink-0">
                    <Button variant="outline" size="sm" onClick={decline}>
                        Decline
                    </Button>
                    <Button size="sm" onClick={accept}>
                        Accept
                    </Button>
                </div>
            </div>
        </div>
    )
}
