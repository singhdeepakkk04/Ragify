"use client"

import { useAuthStore } from "@/lib/auth"
import { useRouter } from "next/navigation"
import { useEffect } from "react"
import Link from "next/link"
import { LayoutDashboard, Plus, Settings, LogOut, BarChart3 } from "lucide-react"
import { Button } from "@/components/ui/button"

export default function DashboardLayout({
    children,
}: {
    children: React.ReactNode
}) {
    const { isAuthenticated, isLoading, logout, initialize } = useAuthStore()
    const router = useRouter()

    useEffect(() => {
        initialize()
    }, [initialize])

    useEffect(() => {
        // ONLY redirect after auth has fully loaded — never while isLoading is true
        // (this was causing the OAuth flash-and-redirect: isAuthenticated was briefly
        //  false before the session cookie was read, triggering an immediate redirect)
        if (!isLoading && !isAuthenticated) {
            router.push("/login")
        }
    }, [isLoading, isAuthenticated, router])

    // Show a loading spinner while auth state is hydrating
    // (returning null here was causing the dashboard to flash then disappear)
    if (isLoading) {
        return (
            <div className="flex h-screen items-center justify-center bg-background">
                <div className="flex flex-col items-center gap-3">
                    <div className="h-8 w-8 animate-spin rounded-full border-2 border-border border-t-primary" />
                    <p className="text-xs text-muted-foreground font-mono tracking-wider">AUTHENTICATING...</p>
                </div>
            </div>
        )
    }

    if (!isAuthenticated) return null


    return (
        <div className="flex h-screen bg-background">
            {/* Sidebar */}
            <div className="w-64 bg-card border-r border-border hidden md:flex flex-col">
                <div className="p-6">
                    <h1 className="text-xl font-bold tracking-wider text-foreground select-none" style={{ fontFamily: 'var(--font-geist-mono)' }}>
                        [ RAGIFY ]
                    </h1>
                </div>
                <nav className="flex-1 px-4 space-y-2">
                    <Link href="/dashboard">
                        <Button variant="ghost" className="w-full justify-start">
                            <LayoutDashboard className="mr-2 h-4 w-4" />
                            Dashboard
                        </Button>
                    </Link>
                    <Link href="/dashboard/projects/new">
                        <Button variant="ghost" className="w-full justify-start">
                            <Plus className="mr-2 h-4 w-4" />
                            New Project
                        </Button>
                    </Link>
                    <Link href="/dashboard/usage">
                        <Button variant="ghost" className="w-full justify-start">
                            <BarChart3 className="mr-2 h-4 w-4" />
                            Usage
                        </Button>
                    </Link>
                    <Link href="/dashboard/settings">
                        <Button variant="ghost" className="w-full justify-start">
                            <Settings className="mr-2 h-4 w-4" />
                            Settings
                        </Button>
                    </Link>
                </nav>
                <div className="p-4 border-t border-border">
                    <Button variant="outline" className="w-full justify-start text-destructive hover:text-destructive" onClick={logout}>
                        <LogOut className="mr-2 h-4 w-4" />
                        Logout
                    </Button>
                </div>
            </div>

            {/* Main Content */}
            <div className="flex-1 flex flex-col overflow-hidden">
                <header className="h-16 bg-card border-b border-border flex items-center justify-between px-6 md:hidden">
                    <h1 className="text-lg font-bold tracking-wider text-foreground" style={{ fontFamily: 'var(--font-geist-mono)' }}>[ RAGIFY ]</h1>
                </header>
                <main className="flex-1 overflow-x-hidden overflow-y-auto p-6">
                    {children}
                </main>
            </div>
        </div>
    )
}
