
"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle, CardDescription, CardFooter } from "@/components/ui/card"
import { Label } from "@/components/ui/label"
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group"
import { Checkbox } from "@/components/ui/checkbox"
import { Progress } from "@/components/ui/progress"
import { getRecommendation } from "@/lib/recommendationEngine"

interface SurveyFormProps {
    onComplete: (config: any) => void
}

interface Question {
    id: string
    question: string
    subtitle: string
    multiSelect?: boolean
    options: { value: string; label: string }[]
}

const QUESTIONS: Question[] = [
    {
        id: "goal",
        question: "What do you want to build?",
        subtitle: "This helps us pick the right setup for your use case.",
        options: [
            { value: "chatbot", label: "A chatbot that answers questions from my docs" },
            { value: "search", label: "A smart search engine over documents" },
            { value: "assistant", label: "An AI assistant for my team" },
            { value: "api", label: "A document Q&A API for my app" },
        ]
    },
    {
        id: "documents",
        question: "What kind of documents will you upload?",
        subtitle: "Select all that apply. This helps optimize chunking strategy.",
        multiSelect: true,
        options: [
            { value: "pdf", label: "PDFs (reports, papers, manuals)" },
            { value: "text", label: "Plain text or markdown files" },
            { value: "docx", label: "Word documents (.docx)" },
            { value: "code", label: "Code files and technical docs" },
        ]
    },
    {
        id: "language",
        question: "What language are your documents in?",
        subtitle: "We'll pick the best model for your language needs.",
        options: [
            { value: "english", label: "English only" },
            { value: "indian", label: "Indian languages (Hindi, Tamil, Telugu, Marathi, etc.)" },
            { value: "multilingual", label: "Multiple languages including Indian" },
            { value: "other", label: "Other languages" },
        ]
    },
    {
        id: "volume",
        question: "How many documents will you start with?",
        subtitle: "We'll optimize storage and retrieval based on your scale.",
        options: [
            { value: "small", label: "Just a few (under 50)" },
            { value: "medium", label: "A moderate collection (50–500)" },
            { value: "large", label: "A large library (500+)" },
        ]
    },
    {
        id: "accuracy",
        question: "How important is answer accuracy vs speed?",
        subtitle: "High accuracy uses smarter (but slower) models.",
        options: [
            { value: "speed", label: "Speed first — I need fast responses" },
            { value: "balanced", label: "A good balance of both" },
            { value: "accuracy", label: "Accuracy first — correctness matters most" },
        ]
    },
    {
        id: "audience",
        question: "Who will be using this?",
        subtitle: "This determines privacy defaults and access settings.",
        options: [
            { value: "just_me", label: "Just me (personal project)" },
            { value: "team", label: "My team or organization" },
            { value: "customers", label: "My customers or end users" },
            { value: "public", label: "Anyone (public access)" },
        ]
    },
    {
        id: "sensitivity",
        question: "How sensitive is the data?",
        subtitle: "We'll adjust safety and privacy settings accordingly.",
        options: [
            { value: "public", label: "Not sensitive — publicly available info" },
            { value: "internal", label: "Internal — company data, not public" },
            { value: "confidential", label: "Confidential — legal, financial, or personal data" },
        ]
    },
    {
        id: "creativity",
        question: "How should the AI respond?",
        subtitle: "Controls how creative vs factual the answers are.",
        options: [
            { value: "strict", label: "Stick strictly to the documents" },
            { value: "moderate", label: "Mostly from docs, with some reasoning" },
            { value: "creative", label: "Be more conversational and exploratory" },
        ]
    },
    {
        id: "budget",
        question: "What's your priority for cost?",
        subtitle: "Smarter models cost more per query. We'll match your budget.",
        options: [
            { value: "free", label: "Keep it free / as cheap as possible" },
            { value: "moderate", label: "I can pay a bit for better results" },
            { value: "premium", label: "I want the best, cost doesn't matter" },
        ]
    },
]

export function SurveyForm({ onComplete }: SurveyFormProps) {
    const [step, setStep] = useState(0)
    const [answers, setAnswers] = useState<Record<string, string | string[]>>({})

    const handleRadioSelect = (value: string) => {
        setAnswers({ ...answers, [QUESTIONS[step].id]: value })
    }

    const handleCheckboxToggle = (value: string) => {
        const qid = QUESTIONS[step].id
        const current = (answers[qid] as string[]) || []
        const updated = current.includes(value)
            ? current.filter((v) => v !== value)
            : [...current, value]
        setAnswers({ ...answers, [qid]: updated })
    }

    const handleNext = () => {
        if (step < QUESTIONS.length - 1) {
            setStep(step + 1)
        } else {
            const config = getRecommendation(answers)
            onComplete(config)
        }
    }

    const handleBack = () => {
        if (step > 0) setStep(step - 1)
    }

    const currentQ = QUESTIONS[step]
    const progress = ((step + 1) / QUESTIONS.length) * 100

    // Check if the current question has a valid answer
    const hasAnswer = currentQ.multiSelect
        ? Array.isArray(answers[currentQ.id]) && (answers[currentQ.id] as string[]).length > 0
        : !!answers[currentQ.id]

    return (
        <Card className="w-full max-w-2xl mx-auto">
            <CardHeader>
                <div className="flex items-center justify-between mb-1">
                    <CardTitle className="text-lg">RAG Setup Wizard</CardTitle>
                    <span className="text-xs text-muted-foreground">{step + 1} of {QUESTIONS.length}</span>
                </div>
                <Progress value={progress} className="h-1.5" />
            </CardHeader>
            <CardContent className="space-y-5 pt-2">
                <div>
                    <h3 className="text-base font-semibold mb-1">{currentQ.question}</h3>
                    <p className="text-sm text-muted-foreground">{currentQ.subtitle}</p>
                </div>

                {currentQ.multiSelect ? (
                    /* ── Checkbox (Multi-Select) ── */
                    <div className="space-y-2">
                        {currentQ.options.map((opt) => {
                            const checked = Array.isArray(answers[currentQ.id])
                                && (answers[currentQ.id] as string[]).includes(opt.value)
                            return (
                                <label
                                    key={opt.value}
                                    htmlFor={`check-${opt.value}`}
                                    className={`flex items-center gap-3 rounded-lg border px-4 py-3 cursor-pointer transition-colors hover:bg-muted/50 ${checked ? 'border-primary bg-primary/5' : ''}`}
                                >
                                    <Checkbox
                                        id={`check-${opt.value}`}
                                        checked={checked}
                                        onCheckedChange={() => handleCheckboxToggle(opt.value)}
                                    />
                                    <span className="text-sm">{opt.label}</span>
                                </label>
                            )
                        })}
                    </div>
                ) : (
                    /* ── Radio (Single Select) ── */
                    <RadioGroup
                        onValueChange={handleRadioSelect}
                        value={answers[currentQ.id] as string}
                        className="space-y-2"
                    >
                        {currentQ.options.map((opt) => (
                            <label
                                key={opt.value}
                                htmlFor={opt.value}
                                className={`flex items-center gap-3 rounded-lg border px-4 py-3 cursor-pointer transition-colors hover:bg-muted/50 ${answers[currentQ.id] === opt.value ? 'border-primary bg-primary/5' : ''}`}
                            >
                                <RadioGroupItem value={opt.value} id={opt.value} />
                                <span className="text-sm">{opt.label}</span>
                            </label>
                        ))}
                    </RadioGroup>
                )}
            </CardContent>
            <CardFooter className="flex justify-between">
                <Button variant="outline" onClick={handleBack} disabled={step === 0}>Back</Button>
                <Button onClick={handleNext} disabled={!hasAnswer}>
                    {step === QUESTIONS.length - 1 ? "See Recommendations" : "Next"}
                </Button>
            </CardFooter>
        </Card>
    )
}
