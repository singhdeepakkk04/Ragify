"use client"

import { useState, useCallback } from "react"
import { useParams, useRouter, useSearchParams } from "next/navigation"
import { createClient } from "@/lib/supabase"
import { useQuery } from "@tanstack/react-query"
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Skeleton } from "@/components/ui/skeleton"
import { toast } from "sonner"
import {
    ArrowLeft, Upload, FileText, Trash2, Copy, Activity,
    Clock, Cpu, Settings2, CheckCircle2, AlertCircle, Loader2
} from "lucide-react"
import {
    AlertDialog,
    AlertDialogAction,
    AlertDialogContent,
    AlertDialogDescription,
    AlertDialogFooter,
    AlertDialogHeader,
    AlertDialogTitle,
} from "@/components/ui/alert-dialog"
import Link from "next/link"
import ReactMarkdown from "react-markdown"
import remarkGfm from "remark-gfm"
import api, { getToken } from '@/lib/api'

interface Project {
    id: number
    name: string
    project_type: string
    description: string | null
    llm_model: string | null
    embedding_model: string | null
    temperature: number | null
    chunk_size: number | null
    chunk_overlap: number | null
    top_k: number | null
    created_at: string
}

interface Document {
    id: number
    filename: string
    content: string | null
    status: string
    created_at: string
}

const TYPE_COLORS: Record<string, string> = {
    chatbot: "bg-blue-100 text-blue-700",
    search: "bg-emerald-100 text-emerald-700",
    assistant: "bg-violet-100 text-violet-700",
    api: "bg-amber-100 text-amber-700",
}

function getApiV1BaseUrl(): string {
    const raw = (process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000').replace(/\/+$/, '')
    return raw.endsWith('/api/v1') ? raw : `${raw}/api/v1`
}

/* ── Playground Component (proper React state) ── */
function PlaygroundSection({ projectId }: { projectId: string }) {
    const [query, setQuery] = useState("")
    const [answer, setAnswer] = useState<string | null>(null)
    const [citations, setCitations] = useState<any[]>([])
    const [loading, setLoading] = useState(false)
    const [error, setError] = useState<string | null>(null)
    const [isCached, setIsCached] = useState(false)

    const apiV1BaseUrl = getApiV1BaseUrl()

    const handleAsk = async () => {
        const q = query.trim()
        if (!q || loading) return

        setLoading(true)
        setAnswer("") // Start with empty string for streaming
        setCitations([])
        setError(null)
        setIsCached(false)

        try {
            const token = await getToken()
            console.log("TEST_TERMINAL token:", token ? "Token acquired" : "Token is null")
            
            const response = await fetch(`${apiV1BaseUrl}/rag/query`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "Authorization": `Bearer ${token}`
                },
                body: JSON.stringify({
                    project_id: parseInt(projectId),
                    query: q,
                    top_k: 4,
                })
            })

            if (!response.ok) {
                const errorData = await response.json()
                throw new Error(errorData.detail || "Search failed")
            }

            const reader = response.body?.getReader()
            const decoder = new TextDecoder()
            
            if (!reader) return

            let accumulatedAnswer = ""

            // Read the stream
            while (true) {
                const { done, value } = await reader.read()
                if (done) break

                const chunk = decoder.decode(value, { stream: true })
                const lines = chunk.split("\n").filter(l => l.trim())

                for (const line of lines) {
                    try {
                        const parsed = JSON.parse(line)
                        if (parsed.token) {
                            accumulatedAnswer += parsed.token
                            setAnswer(accumulatedAnswer)
                        } else if (parsed.citations) {
                            setCitations(parsed.citations)
                        } else if (parsed.correction) {
                            // Output guardrail fired — replace streamed answer
                            accumulatedAnswer = parsed.correction
                            setAnswer(accumulatedAnswer)
                        } else if (parsed.error) {
                            setError(parsed.error)
                        }
                    } catch (e) {
                        console.warn("Error parsing stream chunk:", e)
                    }
                }
            }
        } catch (err: any) {
            console.error("RAG query error:", err)
            setError(err.message || "Failed to query.")
        } finally {
            setLoading(false)
        }
    }

    return (
        <Card className="border border-border/50 bg-card/50 shadow-sm">
            <CardHeader className="pb-3 border-b border-border/50">
                <CardTitle className="text-sm flex items-center gap-2 font-mono uppercase tracking-wider">
                    <Activity className="h-4 w-4" /> TEST_TERMINAL
                </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4 pt-4">
                {/* Query Input */}
                <div className="flex gap-2">
                    <div className="relative flex-1">
                        <span className="absolute left-3 top-2.5 text-muted-foreground font-mono text-xs">{">"}</span>
                        <input
                            type="text"
                            value={query}
                            onChange={(e) => setQuery(e.target.value)}
                            placeholder="Input query sequence..."
                            className="w-full pl-6 pr-3 py-2 text-sm border border-border/50 rounded bg-background/50 focus:outline-none focus:ring-1 focus:ring-primary/50 font-mono"
                            onKeyDown={(e) => { if (e.key === 'Enter') handleAsk() }}
                            disabled={loading}
                            autoFocus
                        />
                    </div>
                    <Button size="sm" onClick={handleAsk} disabled={loading || !query.trim()} className="rounded font-mono uppercase text-xs px-4">
                        {loading ? (
                            <><Loader2 className="h-3 w-3 mr-2 animate-spin" /> PROCESSING</>
                        ) : (
                            "EXECUTE"
                        )}
                    </Button>
                </div>

                {/* Answer */}
                <div className="min-h-[120px] p-4 rounded bg-muted/30 border border-border/50 font-sans">
                    {loading && !answer && citations.length === 0 ? (
                        <div className="flex flex-col gap-2">
                            <div className="flex items-center gap-2 text-xs text-primary font-mono animate-pulse">
                                <span className="h-2 w-2 bg-primary rounded-full" />
                                ANALYZING VECTOR SPACE...
                            </div>
                            <div className="space-y-2 mt-2">
                                <Skeleton className="h-4 w-3/4 bg-primary/10" />
                                <Skeleton className="h-4 w-1/2 bg-primary/10" />
                            </div>
                        </div>
                    ) : error ? (
                        <div className="flex items-center gap-2 text-sm text-destructive font-mono">
                            <AlertCircle className="h-4 w-4" />
                            ERROR: {error}
                        </div>
                    ) : answer || citations.length > 0 ? (
                        <div className="animate-in fade-in duration-500">
                            {isCached && (
                                <div className="flex items-center gap-1.5 mb-3">
                                    <Badge variant="outline" className="text-[10px] border-primary/30 text-primary bg-primary/5 font-mono uppercase tracking-wider">
                                        ⚡ CACHE HIT
                                    </Badge>
                                </div>
                            )}
                            <div className="text-sm leading-relaxed text-foreground/90 prose prose-sm dark:prose-invert max-w-none">
                                {answer ? (
                                    <ReactMarkdown remarkPlugins={[remarkGfm]}>
                                        {answer}
                                    </ReactMarkdown>
                                ) : (
                                    <div className="flex items-center gap-2 text-xs text-primary font-mono animate-pulse my-2">
                                        <span className="h-2 w-2 bg-primary rounded-full" />
                                        GENERATING RESPONSE...
                                    </div>
                                )}
                            </div>
                        </div>
                    ) : (
                        <div className="h-full flex flex-col items-center justify-center text-muted-foreground/40 font-mono text-xs mt-4">
                            <span>AWAITING INPUT...</span>
                        </div>
                    )}
                </div>

                {/* Citations */}
                {citations.length > 0 && (
                    <div className="border-t border-border/50 pt-3">
                        <p className="text-[10px] font-mono text-muted-foreground mb-2 uppercase tracking-wider">REFERENCE_DATA</p>
                        <div className="space-y-2">
                            {citations.map((c: any, i: number) => (
                                <details key={i} className="group">
                                    <summary className="cursor-pointer inline-flex items-center gap-1.5 px-2 py-1 rounded bg-muted/20 border border-border/50 text-xs font-medium hover:bg-muted/40 transition-colors select-none">
                                        <span className="text-[10px] font-mono text-muted-foreground font-bold mr-1">[Source {i + 1}]</span>
                                        <FileText className="h-3 w-3 text-muted-foreground" />
                                        <span className="font-mono text-[10px]">{c.filename}</span>
                                        {c.page_number && <span className="text-muted-foreground/60 font-mono text-[10px]">:: pg.{c.page_number}</span>}
                                    </summary>
                                    <div className="mt-1.5 ml-1 p-3 rounded bg-muted/10 text-xs text-muted-foreground border-l-2 border-primary/20 font-mono leading-relaxed">
                                        "{c.snippet}"
                                    </div>
                                </details>
                            ))}
                        </div>
                    </div>
                )}
            </CardContent>
        </Card>
    )
}

function ConfigurationSection({ project }: { project: Project }) {
    const [isEditing, setIsEditing] = useState(false)
    const [isLoading, setIsLoading] = useState(false)
    const [models, setModels] = useState<any[]>([])
    const router = useRouter()

    // Form State
    const [formData, setFormData] = useState({
        llm_model: project.llm_model || "gpt-3.5-turbo",
        embedding_provider: (project as any).embedding_provider || "openai",
        embedding_model: project.embedding_model || "text-embedding-3-small",
        temperature: project.temperature ?? 0,
        top_k: project.top_k ?? 4,
    })

    const applyEmbeddingProvider = (provider: string) => {
        // Keep this dead-simple: set the provider and a safe default model.
        if (provider === "gemini") {
            setFormData((prev) => ({
                ...prev,
                embedding_provider: "gemini",
                embedding_model: "gemini-embedding-2-preview",
            }))
            return
        }
        setFormData((prev) => ({
            ...prev,
            embedding_provider: "openai",
            embedding_model: prev.embedding_model?.startsWith("gemini-") ? "text-embedding-3-small" : prev.embedding_model,
        }))
    }

    const fetchModels = async () => {
        try {
            const res = await api.get("/projects/models")
            setModels(res.data)
        } catch (error) {
            console.error("Failed to fetch models", error)
            toast.error("Could not load available models")
        }
    }

    const handleSave = async () => {
        setIsLoading(true)
        try {
            await api.patch(`/projects/${project.id}`, {
                name: project.name, // Required by backend schema currently
                ...formData
            })
            toast.success("Configuration updated successfully")
            setIsEditing(false)
            router.refresh()
        } catch (error) {
            const msg: any = (error as any)?.response?.data?.detail || (error as any)?.message || "Failed to update configuration"
            toast.error(typeof msg === "string" ? msg : JSON.stringify(msg))
        } finally {
            setIsLoading(false)
        }
    }

    return (
        <Card className="border border-border/50 bg-card/50 shadow-sm relative">
            <CardHeader className="pb-3 border-b border-border/50 flex flex-row items-center justify-between">
                <div>
                    <CardTitle className="text-sm flex items-center gap-2 font-mono uppercase tracking-wider">
                        <Settings2 className="h-4 w-4" /> Pipeline Config
                    </CardTitle>
                    <CardDescription className="text-xs">Configure LLM and Retrieval parameters.</CardDescription>
                </div>
                {!isEditing ? (
                    <Button variant="outline" size="sm" onClick={() => { setIsEditing(true); fetchModels(); }} className="h-7 text-xs font-mono">
                        EDIT CONFIG
                    </Button>
                ) : (
                    <div className="flex gap-2">
                        <Button variant="ghost" size="sm" onClick={() => setIsEditing(false)} className="h-7 text-xs font-mono" disabled={isLoading}>
                            CANCEL
                        </Button>
                        <Button size="sm" onClick={handleSave} className="h-7 text-xs font-mono" disabled={isLoading}>
                            {isLoading ? "SAVING..." : "SAVE CHANGES"}
                        </Button>
                    </div>
                )}
            </CardHeader>
            <CardContent className="pt-4">
                {!isEditing ? (
                    <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                        {[
                            { label: "LLM Model", value: project.llm_model || "gpt-3.5-turbo" },
                            { label: "Embedding Model", value: project.embedding_model || "text-embedding-3-small" },
                            { label: "Temperature", value: String(project.temperature ?? 0) },
                            { label: "Chunk Size", value: `${project.chunk_size ?? 1000} tokens` },
                            { label: "Chunk Overlap", value: `${project.chunk_overlap ?? 200} tokens` },
                            { label: "Top K", value: String(project.top_k ?? 4) },
                        ].map((item) => (
                            <div key={item.label} className="p-3 rounded bg-muted/20 border border-border/50">
                                <p className="text-[10px] text-muted-foreground mb-1 font-mono uppercase">{item.label}</p>
                                <p className="text-sm font-medium font-mono">{item.value}</p>
                            </div>
                        ))}
                    </div>
                ) : (
                    <div className="space-y-4 max-w-lg">
                        <div className="space-y-2">
                            <label className="text-xs font-mono uppercase text-muted-foreground">LLM Model</label>
                            <select
                                className="w-full p-2 rounded border border-border bg-background/50 text-sm"
                                value={formData.llm_model}
                                onChange={(e) => setFormData({ ...formData, llm_model: e.target.value })}
                            >
                                {models.map(m => (
                                    <option key={m.id} value={m.id}>
                                        {m.name} ({m.provider}) - {m.cost_tier}
                                    </option>
                                ))}
                                {models.length === 0 && <option value={formData.llm_model}>{formData.llm_model}</option>}
                            </select>
                            <p className="text-[10px] text-muted-foreground">
                                Select the model used for response generation.
                            </p>
                        </div>

                        <div className="space-y-2">
                            <label className="text-xs font-mono uppercase text-muted-foreground">Embedding Provider</label>
                            <select
                                className="w-full p-2 rounded border border-border bg-background/50 text-sm"
                                value={(formData as any).embedding_provider}
                                onChange={(e) => applyEmbeddingProvider(e.target.value)}
                            >
                                <option value="openai">OpenAI</option>
                                <option value="gemini">Gemini</option>
                            </select>
                            <p className="text-[10px] text-muted-foreground">
                                Changing embedding provider requires re-ingesting documents.
                            </p>
                        </div>

                        <div className="space-y-2">
                            <label className="text-xs font-mono uppercase text-muted-foreground">Embedding Model</label>
                            <input
                                className="w-full p-2 rounded border border-border bg-background/50 text-sm"
                                value={(formData as any).embedding_model}
                                onChange={(e) => setFormData({ ...(formData as any), embedding_model: e.target.value })}
                                placeholder="text-embedding-3-small"
                            />
                            <p className="text-[10px] text-muted-foreground">
                                For Gemini embeddings use `gemini-embedding-2-preview`.
                            </p>
                        </div>

                        <div className="space-y-2">
                            <label className="text-xs font-mono uppercase text-muted-foreground">Temperature ({formData.temperature})</label>
                            <input
                                type="range"
                                min="0" max="1" step="0.1"
                                className="w-full accent-primary"
                                value={formData.temperature}
                                onChange={(e) => setFormData({ ...formData, temperature: parseFloat(e.target.value) })}
                            />
                            <p className="text-[10px] text-muted-foreground">
                                Controls randomness. 0 = deterministic, 1 = creative.
                            </p>
                        </div>

                        <div className="space-y-2">
                            <label className="text-xs font-mono uppercase text-muted-foreground">Top K Retrieval ({formData.top_k})</label>
                            <div className="flex gap-4">
                                {[2, 4, 6, 8, 10].map(k => (
                                    <button
                                        key={k}
                                        onClick={() => setFormData({ ...formData, top_k: k })}
                                        className={`px-3 py-1 rounded text-xs font-mono border transition-colors ${formData.top_k === k
                                            ? 'bg-primary text-primary-foreground border-primary'
                                            : 'bg-muted/10 border-border hover:border-primary/50'
                                            }`}
                                    >
                                        {k}
                                    </button>
                                ))}
                            </div>
                            <p className="text-[10px] text-muted-foreground">
                                Number of document chunks to retrieve per query.
                            </p>
                        </div>
                    </div>
                )}
            </CardContent>
        </Card>
    )
}

export default function ProjectDetailsPage() {
    const params = useParams()
    const router = useRouter()
    const searchParams = useSearchParams()
    const initialTab = searchParams.get("tab") || "documents"
    const projectId = params.id as string

    const [uploading, setUploading] = useState(false)
    const [dragActive, setDragActive] = useState(false)
    const [newPlaintextKey, setNewPlaintextKey] = useState<string | null>(null)

    // Fetch project from secure backend API
    const { data: project, isLoading } = useQuery<Project | null>({
        queryKey: ["project", projectId],
        queryFn: async () => {
            try {
                const res = await api.get(`/projects/${projectId}`)
                return res.data
            } catch (error) {
                return null
            }
        },
    })

    // Fetch documents for this project via secure backend API
    const { data: documents = [], refetch: refetchDocs } = useQuery<Document[]>({
        queryKey: ["documents", projectId],
        queryFn: async () => {
            try {
                const res = await api.get(`/documents?project_id=${projectId}`)
                return res.data.sort((a: Document, b: Document) =>
                    new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
                )
            } catch (error) {
                return []
            }
        },
        refetchInterval: (query) => {
            const docs = query.state.data ?? []
            const hasProcessing = docs.some((d: Document) => d.status === "pending" || d.status === "processing")
            return hasProcessing ? 3000 : false
        },
    })

    // Fetch usage logs for this project
    const { data: projectLogs } = useQuery<{
        total: number
        logs: { id: number; query: string; model_used: string; tokens_used: number; latency_ms: number; created_at: string }[]
    }>({
        queryKey: ["project-logs", projectId],
        queryFn: async () => {
            try {
                const res = await api.get(`/usage/project/${projectId}`)
                return res.data
            } catch { return { total: 0, logs: [] } }
        },
        enabled: !!projectId,
    })

    // Fetch API Key when project is loaded
    const { data: apiKey, refetch: refetchKey, isLoading: isLoadingKey } = useQuery({
        queryKey: ["apiKey", projectId],
        queryFn: async () => {
            // Only fetch if project exists (handled by enabled) works, 
            // but we also need to handle the case where user doesn't have permissions gracefully
            try {
                const res = await api.get(`/projects/${projectId}/api-key`)
                return res.data
            } catch (e) {
                return null
            }
        },
        enabled: !!projectId,
    })

    const handleRegenerateKey = async () => {
        if (!confirm("Are you sure? The old API key will stop working immediately.")) return
        try {
            const res = await api.post(`/projects/${projectId}/api-key/regenerate`)
            setNewPlaintextKey(res.data.plaintext_key) // Show the modal exactly once
            toast.success("New API Key generated")
            refetchKey()
        } catch (error) {
            toast.error("Failed to regenerate key")
        }
    }

    const handleFileUpload = useCallback(async (files: FileList | null) => {
        if (!files || files.length === 0) return
        setUploading(true)

        try {
            for (const file of Array.from(files)) {
                const formData = new FormData()
                formData.append("file", file)
                formData.append("project_id", projectId)

                await api.post("/documents/upload", formData, {
                    headers: { "Content-Type": "multipart/form-data" },
                })
            }
            toast.success(`${files.length} file(s) uploaded successfully`)
            refetchDocs()
        } catch (error) {
            toast.error("Upload failed — backend /documents/upload endpoint not configured yet")
        } finally {
            setUploading(false)
        }
    }, [projectId, refetchDocs])

    const handleDeleteDocument = async (docId: number) => {
        if (!confirm("Are you sure you want to delete this document?")) return
        try {
            await api.delete(`/documents/${docId}`)
            toast.success("Document deleted")
            refetchDocs()
        } catch (error) {
            toast.error("Failed to delete document")
        }
    }

    const handleDrop = useCallback((e: React.DragEvent) => {
        e.preventDefault()
        setDragActive(false)
        handleFileUpload(e.dataTransfer.files)
    }, [handleFileUpload])

    const copyToClipboard = (text: string) => {
        navigator.clipboard.writeText(text)
        toast.success("Copied to clipboard")
    }

    if (isLoading) {
        return (
            <div className="w-full space-y-6">
                <Skeleton className="h-8 w-48" />
                <div className="grid grid-cols-4 gap-4">
                    {Array.from({ length: 4 }).map((_, i) => <Skeleton key={i} className="h-24" />)}
                </div>
                <Skeleton className="h-96" />
            </div>
        )
    }

    if (!project) {
        return (
            <div className="w-full">
                <div className="flex flex-col items-center justify-center py-24 text-center">
                    <AlertCircle className="h-12 w-12 text-muted-foreground mb-4" />
                    <h3 className="text-lg font-semibold mb-1">Project not found</h3>
                    <p className="text-sm text-muted-foreground mb-4">This project may have been deleted or you don&apos;t have access.</p>
                    <Link href="/dashboard"><Button variant="outline" size="sm">Back to Dashboard</Button></Link>
                </div>
            </div>
        )
    }

        const apiV1BaseUrl = getApiV1BaseUrl()

    const curlExample = `curl -X POST "${apiV1BaseUrl}/rag/query" \\
  -H "X-API-Key: $YOUR_API_KEY" \\
  -H "Content-Type: application/json" \\
  -d '{
    "project_id": ${project.id},
    "query": "What does this document say?"
  }'`

    return (
        <div className="w-full space-y-6">
            {/* ... Header & Stats ... */}
            {/* (Header and Stats code remains same, omitted for brevity in replace block if possible, but strict replace needs exact context) */}
            {/* actually I need to target the return block to insert the modal or just the tabs content */}

            {/* Header */}
            <div className="flex items-start justify-between">
                <div className="flex items-start gap-4">
                    <button onClick={() => router.back()} className="mt-1.5 text-muted-foreground hover:text-foreground transition-colors">
                        <ArrowLeft className="h-5 w-5" />
                    </button>
                    <div>
                        <div className="flex items-center gap-3 mb-1">
                            <h1 className="text-2xl font-bold tracking-tight" style={{ fontFamily: 'var(--font-geist-sans)' }}>
                                {project.name}
                            </h1>
                            <Badge variant="outline" className="text-[10px] px-2 py-0.5 border-border/60 text-muted-foreground bg-transparent font-mono uppercase">
                                {project.project_type}
                            </Badge>
                        </div>
                        <p className="text-sm text-muted-foreground font-mono text-xs">
                            {project.description || "// NO DESCRIPTION PROVIDED"}
                        </p>
                    </div>
                </div>
            </div>

            {/* Quick Stats */}
            <div className="grid grid-cols-2 lg:grid-cols-4 gap-3">
                <Card className="border border-border/50 bg-card/50 shadow-sm hover:border-primary/30 transition-colors">
                    <CardContent className="pt-4 pb-3 px-4">
                        <div className="flex items-center gap-2 mb-1.5 opacity-80">
                            <Cpu className="h-3.5 w-3.5 text-muted-foreground" />
                            <span className="text-[10px] font-mono uppercase tracking-wider text-muted-foreground">Model</span>
                        </div>
                        <p className="text-sm font-semibold truncate font-mono">{project.llm_model || "gpt-3.5-turbo"}</p>
                    </CardContent>
                </Card>
                <Card className="border border-border/50 bg-card/50 shadow-sm hover:border-primary/30 transition-colors">
                    <CardContent className="pt-4 pb-3 px-4">
                        <div className="flex items-center gap-2 mb-1.5 opacity-80">
                            <FileText className="h-3.5 w-3.5 text-muted-foreground" />
                            <span className="text-[10px] font-mono uppercase tracking-wider text-muted-foreground">Documents</span>
                        </div>
                        <p className="text-sm font-semibold font-mono">{documents.length}</p>
                    </CardContent>
                </Card>
                <Card className="border border-border/50 bg-card/50 shadow-sm hover:border-primary/30 transition-colors">
                    <CardContent className="pt-4 pb-3 px-4">
                        <div className="flex items-center gap-2 mb-1.5 opacity-80">
                            <Activity className="h-3.5 w-3.5 text-muted-foreground" />
                            <span className="text-[10px] font-mono uppercase tracking-wider text-muted-foreground">Requests</span>
                        </div>
                        <p className="text-sm font-semibold font-mono">{projectLogs?.total ?? 0}</p>
                    </CardContent>
                </Card>
                <Card className="border border-border/50 bg-card/50 shadow-sm hover:border-primary/30 transition-colors">
                    <CardContent className="pt-4 pb-3 px-4">
                        <div className="flex items-center gap-2 mb-1.5 opacity-80">
                            <Clock className="h-3.5 w-3.5 text-muted-foreground" />
                            <span className="text-[10px] font-mono uppercase tracking-wider text-muted-foreground">Created</span>
                        </div>
                        <p className="text-sm font-semibold font-mono">{new Date(project.created_at).toLocaleDateString()}</p>
                    </CardContent>
                </Card>
            </div>

            {/* Tabs */}
            <Tabs defaultValue={initialTab} className="w-full">
                <TabsList className="bg-muted/50">
                    <TabsTrigger value="documents">Documents</TabsTrigger>
                    <TabsTrigger value="logs">Logs</TabsTrigger>
                    <TabsTrigger value="settings">Configuration</TabsTrigger>
                    <TabsTrigger value="api">API & Integration</TabsTrigger>
                    <TabsTrigger value="playground">Playground</TabsTrigger>
                </TabsList>

                {/* Documents Tab */}
                <TabsContent value="documents" className="mt-4 space-y-4">
                    {/* Upload Zone */}
                    <Card className={`border-2 border-dashed transition-colors ${dragActive ? 'border-primary bg-primary/5' : 'border-border/40 hover:border-border/60 bg-card/30'}`}>
                        <CardContent className="py-10">
                            <div
                                className="flex flex-col items-center justify-center text-center"
                                onDragOver={(e) => { e.preventDefault(); setDragActive(true) }}
                                onDragLeave={() => setDragActive(false)}
                                onDrop={handleDrop}
                            >
                                {uploading ? (
                                    <Loader2 className="h-10 w-10 text-primary animate-spin mb-3" />
                                ) : (
                                    <div className="h-12 w-12 rounded-xl bg-muted/50 flex items-center justify-center mb-3">
                                        <Upload className="h-6 w-6 text-muted-foreground" />
                                    </div>
                                )}
                                <h4 className="text-sm font-semibold mb-1">
                                    {uploading ? "Uploading..." : "Upload Documents"}
                                </h4>
                                <p className="text-xs text-muted-foreground mb-4 max-w-sm">
                                    Drag and drop your PDFs, DOCX, or TXT files here, or click to browse.
                                </p>
                                <label>
                                    <input
                                        type="file"
                                        multiple
                                        accept=".pdf,.docx,.txt,.md,.csv"
                                        className="hidden"
                                        onChange={(e) => handleFileUpload(e.target.files)}
                                        disabled={uploading}
                                    />
                                    <Button variant="outline" size="sm" className="text-xs cursor-pointer border-primary/20 hover:bg-primary/5" asChild>
                                        <span>Browse Files</span>
                                    </Button>
                                </label>
                            </div>
                        </CardContent>
                    </Card>

                    {/* Document List */}
                    {documents.length > 0 ? (
                        <Card className="border border-border/50 bg-card/50 shadow-sm">
                            <CardHeader className="pb-3 border-b border-border/50">
                                <CardTitle className="text-sm font-mono uppercase tracking-wider">Uploaded Documents</CardTitle>
                            </CardHeader>
                            <CardContent className="pt-3">
                                <div className="space-y-2">
                                    {documents.map((doc) => (
                                        <div key={doc.id} className="flex items-center justify-between py-2.5 px-3 rounded-lg hover:bg-muted/50 transition-colors border border-transparent hover:border-border/50">
                                            <div className="flex items-center gap-3">
                                                <FileText className="h-4 w-4 text-muted-foreground" />
                                                <div>
                                                    <p className="text-sm font-medium">{doc.filename}</p>
                                                    <p className="text-[11px] text-muted-foreground font-mono">
                                                        {new Date(doc.created_at).toLocaleDateString()}
                                                    </p>
                                                </div>
                                            </div>
                                            <div className="flex items-center gap-2">
                                                <Badge variant="outline" className="text-[10px] border-border/50">
                                                    {doc.status === "completed" ? (
                                                        <><CheckCircle2 className="h-3 w-3 mr-1 text-emerald-500" /> READY</>
                                                    ) : doc.status === "failed" ? (
                                                        <><span className="h-3 w-3 mr-1 text-red-500">✗</span> FAILED</>
                                                    ) : (
                                                        <><Loader2 className="h-3 w-3 mr-1 animate-spin" /> SYNCING</>
                                                    )}
                                                </Badge>
                                                <Button
                                                    variant="ghost"
                                                    size="icon"
                                                    className="h-7 w-7 hover:text-destructive hover:bg-destructive/10"
                                                    onClick={() => handleDeleteDocument(doc.id)}
                                                >
                                                    <Trash2 className="h-3.5 w-3.5" />
                                                </Button>
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            </CardContent>
                        </Card>
                    ) : (
                        <div className="text-center py-8 text-sm text-muted-foreground font-mono text-xs">
                            NO DOCUMENTS FOUND. UPLOAD ABOVE.
                        </div>
                    )}
                </TabsContent>

                {/* Configuration Tab */}
                <TabsContent value="settings" className="mt-4">
                    <ConfigurationSection project={project} />
                </TabsContent>

                {/* API Tab */}
                <TabsContent value="api" className="mt-4 space-y-4">
                    {/* API Key Section */}
                    <Card className="border border-border/50 bg-card/50 shadow-sm">
                        <CardHeader className="pb-3 border-b border-border/50">
                            <CardTitle className="text-sm font-mono uppercase tracking-wider">Project API Key</CardTitle>
                            <CardDescription className="text-xs">
                                Use this key to authenticate requests from your chatbot or external applications. For security, only the prefix is shown.
                            </CardDescription>
                        </CardHeader>
                        <CardContent className="pt-4 space-y-4">
                            <div className="flex items-center gap-2">
                                <div className="relative flex-1">
                                    <input
                                        type="text"
                                        readOnly
                                        value={isLoadingKey ? "Loading..." : (apiKey?.prefix ? `${apiKey.prefix}••••••••••••••••••••` : "No API Key found. Generate one below.")}
                                        className="w-full px-3 py-2 text-sm bg-muted/30 border border-border/50 rounded font-mono text-muted-foreground"
                                    />
                                    {/* Copy button removed since we don't have the full key */}
                                </div>
                                <Button
                                    variant="outline"
                                    size="sm"
                                    onClick={handleRegenerateKey}
                                    className="border-destructive/30 hover:bg-destructive/10 hover:text-destructive transition-colors font-mono text-xs uppercase"
                                >
                                    Regenerate
                                </Button>
                            </div>
                            <div className="p-3 rounded bg-amber-500/10 border border-amber-500/20 text-xs text-amber-500/90 flex gap-2 items-start">
                                <AlertCircle className="h-4 w-4 shrink-0 mt-0.5" />
                                <p>This key grants full access to query this project. Keep it secure and never share it publicly. You cannot view the full key again after creation.</p>
                            </div>
                        </CardContent>
                    </Card>

                    {/* Example Code */}
                    <Card className="border border-border/50 bg-card/50 shadow-sm">
                        <CardHeader className="pb-3 border-b border-border/50">
                            <CardTitle className="text-sm font-mono uppercase tracking-wider">Integration Example (cURL)</CardTitle>
                        </CardHeader>
                        <CardContent className="pt-4">
                            <div className="relative group">
                                <pre className="bg-zinc-950 text-zinc-300 p-4 rounded-lg overflow-x-auto text-xs leading-relaxed font-mono border border-white/5">
                                    {curlExample}
                                </pre>
                                <Button
                                    variant="ghost"
                                    size="icon"
                                    className="absolute top-2 right-2 h-7 w-7 bg-zinc-800 hover:bg-zinc-700 text-zinc-300 opacity-0 group-hover:opacity-100 transition-opacity"
                                    onClick={() => copyToClipboard(curlExample)}
                                >
                                    <Copy className="h-3.5 w-3.5" />
                                </Button>
                            </div>
                        </CardContent>
                    </Card>
                </TabsContent>

                {/* Logs Tab */}
                <TabsContent value="logs" className="mt-4 space-y-4">
                    <Card className="border border-border/50 bg-card/50 shadow-sm">
                        <CardHeader className="pb-3">
                            <CardTitle className="text-base font-semibold tracking-tight">Query History</CardTitle>
                            <CardDescription className="text-xs">
                                {projectLogs?.total ?? 0} total requests logged
                            </CardDescription>
                        </CardHeader>
                        <CardContent>
                            {!projectLogs?.logs?.length ? (
                                <div className="flex flex-col items-center justify-center py-12 text-center">
                                    <Activity className="h-8 w-8 text-muted-foreground/40 mb-3" />
                                    <p className="text-sm text-muted-foreground">No queries yet</p>
                                    <p className="text-xs text-muted-foreground/60 mt-1">Use the Playground to make your first query</p>
                                </div>
                            ) : (
                                <div className="space-y-2">
                                    {projectLogs.logs.map((log) => (
                                        <div key={log.id} className="flex items-start justify-between gap-4 p-3 rounded-lg border border-border/40 bg-background/50 hover:bg-muted/30 transition-colors">
                                            <div className="flex-1 min-w-0">
                                                <p className="text-sm font-medium truncate">{log.query}</p>
                                                <div className="flex items-center gap-3 mt-1.5">
                                                    <span className="text-[10px] font-mono text-muted-foreground bg-muted/50 px-1.5 py-0.5 rounded">{log.model_used}</span>
                                                    <span className="text-[10px] text-muted-foreground flex items-center gap-1">
                                                        <Clock className="h-3 w-3" /> {log.latency_ms}ms
                                                    </span>
                                                    <span className="text-[10px] text-muted-foreground">
                                                        ~{log.tokens_used} tokens
                                                    </span>
                                                </div>
                                            </div>
                                            <span className="text-[10px] text-muted-foreground whitespace-nowrap">
                                                {new Date(log.created_at).toLocaleString()}
                                            </span>
                                        </div>
                                    ))}
                                </div>
                            )}
                        </CardContent>
                    </Card>
                </TabsContent>

                {/* Playground Tab */}
                <TabsContent value="playground" className="mt-4 space-y-4">
                    <PlaygroundSection projectId={projectId} />
                </TabsContent>
            </Tabs>

            {/* NEW KEY EXACTLY-ONCE MODAL */}
            <AlertDialog open={!!newPlaintextKey}>
                <AlertDialogContent>
                    <AlertDialogHeader>
                        <AlertDialogTitle>Save your new API Key</AlertDialogTitle>
                        <AlertDialogDescription>
                            Please copy your new API key now. <strong className="text-foreground">You will not be able to see it again!</strong>
                        </AlertDialogDescription>
                    </AlertDialogHeader>
                    
                    <div className="relative my-4">
                        <input
                            type="text"
                            readOnly
                            value={newPlaintextKey || ""}
                            className="w-full pl-3 pr-10 py-3 text-sm bg-muted border border-border rounded font-mono text-foreground"
                        />
                        <div className="absolute inset-y-0 right-0 flex items-center pr-2">
                            <Button
                                variant="ghost"
                                size="icon"
                                className="h-8 w-8 hover:bg-muted-foreground/20"
                                onClick={() => {
                                    if(newPlaintextKey) {
                                        copyToClipboard(newPlaintextKey);
                                    }
                                }}
                            >
                                <Copy className="h-4 w-4" />
                            </Button>
                        </div>
                    </div>

                    <AlertDialogFooter>
                        <AlertDialogAction onClick={() => setNewPlaintextKey(null)}>
                            I have saved my key
                        </AlertDialogAction>
                    </AlertDialogFooter>
                </AlertDialogContent>
            </AlertDialog>
        </div>
    )
}
