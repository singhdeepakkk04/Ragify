"use client"

import { useState } from "react"
import { useAuthStore } from "@/lib/auth"
import api from "@/lib/api"
import { useRouter } from "next/navigation"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card"
import { SurveyForm } from "@/components/project-wizard/SurveyForm"
import { toast } from "sonner"
import { Label } from "@/components/ui/label"
import { Input } from "@/components/ui/input"
import { Textarea } from "@/components/ui/textarea"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Loader2, Sparkles } from "lucide-react"

type SetupMode = "choice" | "manual" | "survey" | "review"

export default function NewProjectPage() {
    const { isAuthenticated } = useAuthStore()
    const router = useRouter()

    const [mode, setMode] = useState<SetupMode>("choice")
    const [isCreating, setIsCreating] = useState(false)
    const [config, setConfig] = useState<any>({
        name: "",
        description: "",
        project_type: "byor",
        llm_model: "gpt-3.5-turbo",
        chunk_size: 1000,
        temperature: 0.7,
    })

    const handleSurveyComplete = (recommendedConfig: any) => {
        setConfig({ ...config, ...recommendedConfig })
        setMode("review")
    }

    const handleCreate = async () => {
        if (!config.name?.trim()) {
            toast.error("Project name is required")
            return
        }
        if (config.temperature < 0 || config.temperature > 2) {
            toast.error("Temperature must be between 0.0 and 2.0")
            return
        }
        if (config.chunk_size < 100) {
            toast.error("Chunk size must be at least 100")
            return
        }

        setIsCreating(true)
        try {
            const { _model_reason, ...payload } = config
            await api.post("/projects/", payload)
            toast.success("Project created successfully!")
            router.push("/dashboard")
        } catch (error: any) {
            // Show the actual backend error so we can see what's failing
            const msg =
                error?.response?.data?.detail ||
                error?.message ||
                "Failed to create project"
            toast.error(typeof msg === "string" ? msg : JSON.stringify(msg))
            console.error("Project creation error:", error?.response?.data || error)
            setIsCreating(false)
        }
    }

    if (mode === "choice") {
        return (
            <div className="flex flex-col items-center justify-center min-h-[60vh] space-y-8">
                <h1 className="text-3xl font-bold" style={{ fontFamily: 'var(--font-serif), Georgia, serif' }}>Create a New Project</h1>
                <p className="text-muted-foreground text-sm">Choose how you'd like to set things up.</p>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6 w-full max-w-4xl">
                    <Card className="hover:border-primary cursor-pointer transition-all" onClick={() => setMode("manual")}>
                        <CardHeader>
                            <CardTitle>I Know What I Want</CardTitle>
                            <CardDescription>Configure LLM, chunking, and other settings yourself.</CardDescription>
                        </CardHeader>
                        <CardContent>
                            <ul className="list-disc pl-5 text-sm text-muted-foreground space-y-1.5">
                                <li>Pick your AI model</li>
                                <li>Set chunking & retrieval params</li>
                                <li>Full control</li>
                            </ul>
                        </CardContent>
                    </Card>

                    <Card className="hover:border-primary cursor-pointer transition-all" onClick={() => setMode("survey")}>
                        <CardHeader>
                            <CardTitle>Help Me Decide</CardTitle>
                            <CardDescription>Answer a few simple questions and we'll configure everything.</CardDescription>
                        </CardHeader>
                        <CardContent>
                            <ul className="list-disc pl-5 text-sm text-muted-foreground space-y-1.5">
                                <li>8 simple questions</li>
                                <li>Smart recommendations</li>
                                <li>Best-practice defaults</li>
                            </ul>
                        </CardContent>
                    </Card>
                </div>
            </div>
        )
    }

    if (mode === "survey") {
        return (
            <div className="container mx-auto py-10">
                <SurveyForm onComplete={handleSurveyComplete} />
            </div>
        )
    }

    // Manual / Review Mode (Shared Form)
    return (
        <div className="container mx-auto py-10 max-w-2xl">
            <Card>
                <CardHeader>
                    <CardTitle style={{ fontFamily: 'var(--font-serif), Georgia, serif' }}>{mode === "review" ? "Review Configuration" : "Manual Setup"}</CardTitle>
                    <CardDescription>Adjust any settings before creating your project.</CardDescription>
                </CardHeader>
                <CardContent className="space-y-6">
                    <div className="space-y-2">
                        <Label>Project Name</Label>
                        <Input value={config.name} onChange={(e) => setConfig({ ...config, name: e.target.value })} placeholder="My Awesome RAG" />
                    </div>

                    <div className="space-y-2">
                        <Label>AI Model</Label>
                        <Select value={config.llm_model} onValueChange={(val) => setConfig({ ...config, llm_model: val })}>
                            <SelectTrigger><SelectValue placeholder="Select a model" /></SelectTrigger>
                            <SelectContent>
                                <SelectItem value="gpt-3.5-turbo">
                                    <div className="flex items-center gap-2">
                                        <span>GPT-3.5 Turbo</span>
                                        <span className="text-[10px] text-muted-foreground bg-muted px-1.5 py-0.5 rounded">OpenAI · Cheap</span>
                                    </div>
                                </SelectItem>
                                <SelectItem value="gpt-4o-mini">
                                    <div className="flex items-center gap-2">
                                        <span>GPT-4o Mini</span>
                                        <span className="text-[10px] text-muted-foreground bg-muted px-1.5 py-0.5 rounded">OpenAI · Moderate</span>
                                    </div>
                                </SelectItem>
                                <SelectItem value="gpt-4-turbo">
                                    <div className="flex items-center gap-2">
                                        <span>GPT-4 Turbo</span>
                                        <span className="text-[10px] text-muted-foreground bg-muted px-1.5 py-0.5 rounded">OpenAI · Expensive</span>
                                    </div>
                                </SelectItem>
                                <SelectItem value="sarvam-m">
                                    <div className="flex items-center gap-2">
                                        <span>Sarvam-M</span>
                                        <span className="text-[10px] text-emerald-700 bg-emerald-50 px-1.5 py-0.5 rounded">Sarvam AI · Indian Languages</span>
                                    </div>
                                </SelectItem>
                                <SelectItem value="groq-llama3">
                                    <div className="flex items-center gap-2">
                                        <span>Llama 3 70B</span>
                                        <span className="text-[10px] text-blue-700 bg-blue-50 px-1.5 py-0.5 rounded">Groq · Free</span>
                                    </div>
                                </SelectItem>
                                <SelectItem value="groq-mixtral">
                                    <div className="flex items-center gap-2">
                                        <span>Mixtral 8x7B</span>
                                        <span className="text-[10px] text-blue-700 bg-blue-50 px-1.5 py-0.5 rounded">Groq · Free · 32K Context</span>
                                    </div>
                                </SelectItem>
                            </SelectContent>
                        </Select>
                        <p className="text-[11px] text-muted-foreground">Each model requires its provider's API key in .env</p>
                        {mode === "review" && config._model_reason && (
                            <div className="mt-2 flex items-start gap-2 rounded-lg border border-emerald-200 bg-emerald-50 px-3 py-2.5">
                                <span className="text-emerald-600 text-sm mt-0.5">✨</span>
                                <div>
                                    <p className="text-xs font-medium text-emerald-800">Auto-recommended</p>
                                    <p className="text-[11px] text-emerald-700">{config._model_reason}</p>
                                </div>
                            </div>
                        )}
                    </div>

                    <div className="grid grid-cols-2 gap-4">
                        <div className="space-y-2">
                            <Label>Chunk Size</Label>
                            <Input type="number" value={config.chunk_size} onChange={(e) => setConfig({ ...config, chunk_size: parseInt(e.target.value) })} />
                        </div>
                        <div className="space-y-2">
                            <Label>Temperature</Label>
                            <Input type="number" step="0.1" value={config.temperature} onChange={(e) => setConfig({ ...config, temperature: parseFloat(e.target.value) })} />
                        </div>
                    </div>

                    {/* Add more fields for full config */}

                    <div className="flex justify-between pt-4">
                        <Button variant="outline" onClick={() => setMode("choice")} disabled={isCreating}>Back</Button>
                        <Button onClick={handleCreate} disabled={isCreating} className="min-w-[160px]">
                            {isCreating ? (
                                <>
                                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                                    Creating project...
                                </>
                            ) : (
                                <>
                                    <Sparkles className="mr-2 h-4 w-4" />
                                    Create Project
                                </>
                            )}
                        </Button>
                    </div>
                </CardContent>
            </Card>
        </div>
    )
}
