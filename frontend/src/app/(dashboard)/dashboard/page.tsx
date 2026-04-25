"use client"

import { useState, useEffect } from "react"
import { useAuthStore } from "@/lib/auth"
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query"
import { Card, CardContent } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import {
    Plus, Database, Activity, Clock, Zap, ArrowRight, Folder, MoreVertical,
    Trash2, Settings, FileText, Loader2, AlertCircle
} from "lucide-react"
import Link from "next/link"
import { Badge } from "@/components/ui/badge"
import { Skeleton } from "@/components/ui/skeleton"
import {
    DropdownMenu,
    DropdownMenuContent,
    DropdownMenuItem,
    DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import {
    AlertDialog,
    AlertDialogAction,
    AlertDialogCancel,
    AlertDialogContent,
    AlertDialogDescription,
    AlertDialogFooter,
    AlertDialogHeader,
    AlertDialogTitle,
} from "@/components/ui/alert-dialog"
import { toast } from "sonner"
import api from "@/lib/api"

interface Project {
    id: number
    name: string
    project_type: string
    created_at: string
    description?: string
    llm_model?: string
}

const TYPE_COLORS: Record<string, string> = {
    chatbot: "bg-blue-50 text-blue-700 border-blue-200",
    search: "bg-emerald-50 text-emerald-700 border-emerald-200",
    assistant: "bg-violet-50 text-violet-700 border-violet-200",
    api: "bg-amber-50 text-amber-700 border-amber-200",
    byor: "bg-gray-50 text-gray-700 border-gray-200",
}

function getGreeting() {
    const h = new Date().getHours()
    if (h < 12) return "Good morning"
    if (h < 17) return "Good afternoon"
    return "Good evening"
}

function timeAgo(date: string) {
    const now = new Date()
    const d = new Date(date)
    const diff = Math.floor((now.getTime() - d.getTime()) / 1000)
    if (diff < 60) return "just now"
    if (diff < 3600) return `${Math.floor(diff / 60)}m ago`
    if (diff < 86400) return `${Math.floor(diff / 3600)}h ago`
    if (diff < 604800) return `${Math.floor(diff / 86400)}d ago`
    return d.toLocaleDateString()
}

export default function DashboardPage() {
    const { user } = useAuthStore()
    const queryClient = useQueryClient()
    const [projectToDelete, setProjectToDelete] = useState<Project | null>(null)
    const [greeting, setGreeting] = useState("Welcome")

    useEffect(() => {
        setGreeting(getGreeting())
    }, [])

    const { data: projects, isLoading, isError, error } = useQuery<Project[]>({
        queryKey: ["projects"],
        queryFn: async () => {
            const res = await api.get("/projects")
            return res.data
        },
    })

    const { data: usage } = useQuery<{
        total_queries: number
        total_documents: number
        avg_latency_ms: number
    }>({
        queryKey: ["usage-stats"],
        queryFn: async () => {
            const res = await api.get("/usage/")
            return res.data
        },
    })

    const deleteMutation = useMutation({
        mutationFn: async (id: number) => {
            await api.delete(`/projects/${id}`)
        },
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ["projects"] })
            toast.success("Project deleted successfully")
            setProjectToDelete(null)
        },
        onError: (error) => {
            console.error(error)
            toast.error("Failed to delete project")
        }
    })

    const firstName = user?.user_metadata?.full_name?.split(" ")[0] || user?.user_metadata?.name?.split(" ")[0] || user?.email?.split("@")[0] || "User"

    return (
        <div className="space-y-8 w-full animate-in fade-in duration-500">
            {/* Header */}
            <div className="flex items-end justify-between">
                <div>
                    <h2 className="text-3xl font-bold tracking-tight text-foreground" style={{ fontFamily: 'var(--font-geist-sans)' }}>
                        {greeting}, <span className="text-muted-foreground">{firstName}</span>
                    </h2>
                    <p className="text-muted-foreground mt-1 font-mono text-xs uppercase tracking-wide">
                        System Status: Operational
                    </p>
                </div>
                <Link href="/dashboard/projects/new">
                    <Button className="h-10 px-5 rounded-md text-sm font-medium border border-primary/20 hover:border-primary/50 bg-primary/10 hover:bg-primary/20 text-primary transition-all">
                        <Plus className="mr-1.5 h-4 w-4" /> Initialize Project
                    </Button>
                </Link>
            </div>

            {/* Stats Row */}
            <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
                {[
                    { label: "TOTAL PROJECTS", value: projects?.length ?? 0, icon: Database },
                    { label: "API REQUESTS", value: usage?.total_queries ?? 0, icon: Activity },
                    { label: "DOCUMENTS INDEXED", value: usage?.total_documents ?? 0, icon: FileText },
                    { label: "AVG LATENCY", value: usage?.avg_latency_ms ? `${usage.avg_latency_ms}ms` : "0ms", icon: Clock },
                ].map((stat, i) => (
                    <Card key={i} className="border border-border bg-card hover:border-primary/30 transition-all duration-300">
                        <CardContent className="pt-6 pb-5 px-6">
                            <div className="flex items-center justify-between mb-4">
                                <stat.icon className="h-5 w-5 text-muted-foreground" />
                            </div>
                            <div className="text-3xl font-bold tracking-tight text-foreground font-mono">
                                {isLoading ? <Skeleton className="h-8 w-16" /> : stat.value}
                            </div>
                            <p className="text-[10px] text-muted-foreground mt-1 font-medium tracking-wider">{stat.label}</p>
                        </CardContent>
                    </Card>
                ))}
            </div>

            {/* Projects Section */}
            <div>
                <div className="flex items-center justify-between mb-5">
                    <h3 className="text-lg font-semibold tracking-tight">Active Projects</h3>
                    {projects && projects.length > 0 && (
                        <span className="font-mono text-xs text-muted-foreground">
                            [{projects.length}]
                        </span>
                    )}
                </div>

                {isLoading ? (
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
                        {Array.from({ length: 3 }).map((_, i) => (
                            <Card key={i} className="border border-border bg-card h-[180px]">
                                <CardContent className="p-6 space-y-4">
                                    <Skeleton className="h-10 w-10 rounded" />
                                    <Skeleton className="h-5 w-3/4" />
                                    <Skeleton className="h-4 w-1/2" />
                                </CardContent>
                            </Card>
                        ))}
                    </div>
                ) : isError ? (
                    <Card className="border border-destructive/30 bg-destructive/5 shadow-none">
                        <CardContent className="flex flex-col items-center justify-center py-16 text-center">
                            <div className="h-14 w-14 rounded-full bg-destructive/10 flex items-center justify-center mb-4">
                                <AlertCircle className="h-7 w-7 text-destructive" />
                            </div>
                            <h4 className="text-base font-semibold mb-2">Failed to load projects</h4>
                            <p className="text-sm text-muted-foreground mb-5 max-w-sm">
                                Could not connect to the backend. Make sure the API server is running on port 8000.
                            </p>
                            <Button
                                variant="outline"
                                size="sm"
                                onClick={() => queryClient.invalidateQueries({ queryKey: ["projects"] })}
                            >
                                Retry
                            </Button>
                        </CardContent>
                    </Card>
                ) : projects?.length === 0 ? (
                    <Card className="border border-dashed border-border/50 shadow-none bg-transparent">
                        <CardContent className="flex flex-col items-center justify-center py-20 text-center">
                            <div className="h-16 w-16 rounded-full bg-muted/10 border border-border/30 flex items-center justify-center mb-5">
                                <Folder className="h-8 w-8 text-muted-foreground/50" />
                            </div>
                            <h4 className="text-base font-semibold mb-2">No active projects</h4>
                            <p className="text-sm text-muted-foreground mb-6 max-w-sm">
                                Initialize a new RAG project to begin.
                            </p>
                            <Link href="/dashboard/projects/new">
                                <Button size="default" variant="outline" className="rounded-md border-primary/20 hover:border-primary/50 text-foreground">
                                    <Plus className="mr-2 h-4 w-4" /> Initialize
                                </Button>
                            </Link>
                        </CardContent>
                    </Card>
                ) : (
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
                        {projects?.map((project) => (
                            <div key={project.id} className="group relative">
                                <Link
                                    href={`/dashboard/projects/${project.id}`}
                                    className="block h-full"
                                >
                                    <Card className="h-full border border-border bg-card hover:bg-accent hover:border-primary/50 transition-all duration-300 relative overflow-hidden group-hover:shadow-[0_0_20px_-10px_rgba(255,255,255,0.1)]">
                                        <CardContent className="p-6">
                                            <div className="flex items-start justify-between mb-4">
                                                <div className="h-10 w-10 rounded border border-border/50 bg-background flex items-center justify-center text-sm font-bold text-muted-foreground font-mono">
                                                    {project.name.slice(0, 2).toUpperCase()}
                                                </div>
                                                {/* Status Dot */}
                                                <div className="flex items-center gap-2">
                                                    <div className="h-1.5 w-1.5 rounded-full bg-emerald-500 shadow-[0_0_8px_rgba(16,185,129,0.6)]" />
                                                </div>
                                            </div>

                                            <h4 className="text-base font-semibold mb-2 group-hover:text-primary transition-colors truncate pr-8 tracking-wide">
                                                {project.name}
                                            </h4>

                                            <div className="flex items-center gap-2 mb-4">
                                                <Badge variant="outline" className="text-[10px] px-2 py-0.5 border-border/60 text-muted-foreground bg-transparent font-mono uppercase">
                                                    {project.project_type}
                                                </Badge>
                                                {project.llm_model && (
                                                    <span className="text-[10px] text-muted-foreground bg-muted/50 px-1.5 py-0.5 rounded-md border border-transparent">
                                                        {project.llm_model}
                                                    </span>
                                                )}
                                            </div>

                                            <div className="flex items-center justify-between text-xs text-muted-foreground mt-auto pt-2 border-t border-dashed">
                                                <span>Updated {timeAgo(project.created_at)}</span>
                                                <ArrowRight className="h-3.5 w-3.5 opacity-0 group-hover:opacity-100 -translate-x-2 group-hover:translate-x-0 transition-all" />
                                            </div>
                                        </CardContent>
                                    </Card>
                                </Link>

                                {/* Dropdown Menu (Absolute Positioned) */}
                                <div className="absolute top-4 right-4 z-10 opacity-0 group-hover:opacity-100 transition-opacity">
                                    <DropdownMenu>
                                        <DropdownMenuTrigger asChild>
                                            <Button variant="ghost" size="icon" className="h-8 w-8 bg-background/80 backdrop-blur-sm hover:bg-background border shadow-sm">
                                                <MoreVertical className="h-4 w-4 text-muted-foreground" />
                                            </Button>
                                        </DropdownMenuTrigger>
                                        <DropdownMenuContent align="end" className="w-40">
                                            <Link href={`/dashboard/projects/${project.id}`}>
                                                <DropdownMenuItem>
                                                    <Activity className="mr-2 h-4 w-4" /> Open
                                                </DropdownMenuItem>
                                            </Link>
                                            <Link href={`/dashboard/projects/${project.id}?tab=settings`}>
                                                <DropdownMenuItem>
                                                    <Settings className="mr-2 h-4 w-4" /> Settings
                                                </DropdownMenuItem>
                                            </Link>
                                            <DropdownMenuItem
                                                className="text-destructive focus:text-destructive"
                                                onSelect={(e) => {
                                                    e.preventDefault()
                                                    setProjectToDelete(project)
                                                }}
                                            >
                                                <Trash2 className="mr-2 h-4 w-4" /> Delete
                                            </DropdownMenuItem>
                                        </DropdownMenuContent>
                                    </DropdownMenu>
                                </div>
                            </div>
                        ))}


                        {/* "New Project" card */}
                        <Link href="/dashboard/projects/new" className="group block h-full">
                            <Card className="h-full border border-border bg-card/80 hover:bg-card hover:border-primary/40 transition-all duration-300 flex flex-col items-center justify-center p-6 text-center">
                                <div className="h-12 w-12 rounded-full bg-muted/20 group-hover:bg-primary/10 flex items-center justify-center mb-3 transition-colors border border-border/30">
                                    <Plus className="h-6 w-6 text-muted-foreground group-hover:text-primary transition-colors" />
                                </div>
                                <span className="text-sm font-medium text-muted-foreground group-hover:text-foreground transition-colors tracking-wide">INITIALIZE PROJECT</span>
                            </Card>
                        </Link>
                    </div>
                )}
            </div>

            {/* Delete Confirmation Dialog */}
            <AlertDialog open={!!projectToDelete} onOpenChange={(open) => !open && setProjectToDelete(null)}>
                <AlertDialogContent>
                    <AlertDialogHeader>
                        <AlertDialogTitle>Are you sure?</AlertDialogTitle>
                        <AlertDialogDescription>
                            This will permanently delete the project <span className="font-semibold text-foreground">"{projectToDelete?.name}"</span> and all its associated documents and embeddings. This action cannot be undone.
                        </AlertDialogDescription>
                    </AlertDialogHeader>
                    <AlertDialogFooter>
                        <AlertDialogCancel disabled={deleteMutation.isPending}>Cancel</AlertDialogCancel>
                        <AlertDialogAction
                            onClick={() => projectToDelete && deleteMutation.mutate(projectToDelete.id)}
                            disabled={deleteMutation.isPending}
                            className="bg-destructive text-destructive-foreground hover:bg-destructive/90"
                        >
                            {deleteMutation.isPending ? (
                                <><Loader2 className="mr-2 h-4 w-4 animate-spin" /> Deleting...</>
                            ) : (
                                "Delete Project"
                            )}
                        </AlertDialogAction>
                    </AlertDialogFooter>
                </AlertDialogContent>
            </AlertDialog>
        </div>
    )
}
