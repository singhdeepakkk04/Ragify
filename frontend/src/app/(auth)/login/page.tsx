"use client"

import { useState } from "react"
import { useForm } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"
import * as z from "zod"
import { Button } from "@/components/ui/button"
import {
    Form,
    FormControl,
    FormField,
    FormItem,
    FormLabel,
    FormMessage,
} from "@/components/ui/form"
import { Input } from "@/components/ui/input"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { toast } from "sonner"
import { useRouter } from "next/navigation"
import Link from "next/link"
import { createClient } from "@/lib/supabase"
import { Mail, Loader2 } from "lucide-react"

const passwordSchema = z.object({
    email: z.string().email(),
    password: z.string().min(1, "Password is required"),
})

const magicLinkSchema = z.object({
    email: z.string().email("Please enter a valid email."),
})

export default function LoginPage() {
    const router = useRouter()
    const supabase = createClient()
    const [isGoogleLoading, setIsGoogleLoading] = useState(false)
    const [isPasswordLoading, setIsPasswordLoading] = useState(false)
    const [isMagicLinkLoading, setIsMagicLinkLoading] = useState(false)
    const [magicLinkSent, setMagicLinkSent] = useState(false)
    const [magicEmail, setMagicEmail] = useState("")
    const [mode, setMode] = useState<"password" | "magic">("password")

    const passwordForm = useForm<z.infer<typeof passwordSchema>>({
        resolver: zodResolver(passwordSchema),
        defaultValues: { email: "", password: "" },
    })

    const magicForm = useForm<z.infer<typeof magicLinkSchema>>({
        resolver: zodResolver(magicLinkSchema),
        defaultValues: { email: "" },
    })

    // ── Password Login ───────────────────────────────────────────────────────
    async function onPasswordSubmit(values: z.infer<typeof passwordSchema>) {
        setIsPasswordLoading(true)
        try {
            const { error } = await supabase.auth.signInWithPassword({
                email: values.email,
                password: values.password,
            })
            if (error) {
                toast.error(error.message)
                return
            }
            toast.success("Logged in successfully!")
            router.push("/dashboard")
        } catch {
            toast.error("Something went wrong")
        } finally {
            setIsPasswordLoading(false)
        }
    }

    // ── Magic Link Login ─────────────────────────────────────────────────────
    async function onMagicLinkSubmit(values: z.infer<typeof magicLinkSchema>) {
        setIsMagicLinkLoading(true)
        try {
            const { error } = await supabase.auth.signInWithOtp({
                email: values.email,
                options: {
                    emailRedirectTo: `${window.location.origin}/auth/callback`,
                },
            })
            if (error) {
                toast.error(error.message)
                return
            }
            setMagicEmail(values.email)
            setMagicLinkSent(true)
        } catch {
            toast.error("Something went wrong")
        } finally {
            setIsMagicLinkLoading(false)
        }
    }

    // ── Google Login ─────────────────────────────────────────────────────────
    async function handleGoogleLogin() {
        setIsGoogleLoading(true)
        const { error } = await supabase.auth.signInWithOAuth({
            provider: "google",
            options: { redirectTo: `${window.location.origin}/auth/callback` },
        })
        if (error) {
            toast.error(error.message)
            setIsGoogleLoading(false)
        }
    }

    // ── Magic Link Sent Screen ───────────────────────────────────────────────
    if (magicLinkSent) {
        return (
            <Card>
                <CardContent className="pt-8 pb-8 flex flex-col items-center text-center gap-4">
                    <div className="h-16 w-16 rounded-full bg-primary/10 flex items-center justify-center">
                        <Mail className="h-8 w-8 text-primary" />
                    </div>
                    <div>
                        <h2 className="text-xl font-bold mb-1">Check your inbox</h2>
                        <p className="text-sm text-muted-foreground max-w-xs">
                            We sent a magic link to{" "}
                            <span className="font-semibold text-foreground">{magicEmail}</span>.
                            Click the link to sign in — no password needed.
                        </p>
                    </div>
                    <div className="w-full space-y-2 pt-2">
                        <p className="text-xs text-muted-foreground">Didn&apos;t receive it?</p>
                        <Button
                            variant="outline"
                            size="sm"
                            className="w-full"
                            onClick={async () => {
                                await supabase.auth.signInWithOtp({
                                    email: magicEmail,
                                    options: { emailRedirectTo: `${window.location.origin}/auth/callback` },
                                })
                                toast.success("Magic link resent!")
                            }}
                        >
                            Resend Link
                        </Button>
                        <Button
                            variant="ghost"
                            size="sm"
                            className="w-full text-muted-foreground"
                            onClick={() => { setMagicLinkSent(false); setMode("password") }}
                        >
                            Use password instead
                        </Button>
                    </div>
                </CardContent>
            </Card>
        )
    }

    return (
        <Card>
            <CardHeader>
                <CardTitle>Welcome back</CardTitle>
                <CardDescription>
                    {mode === "password"
                        ? "Sign in with your email and password."
                        : "We'll send a magic link to your inbox."}
                </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">

                {/* ── Password Mode ── */}
                {mode === "password" && (
                    <Form {...passwordForm}>
                        <form onSubmit={passwordForm.handleSubmit(onPasswordSubmit)} className="space-y-4">
                            <FormField
                                control={passwordForm.control}
                                name="email"
                                render={({ field }) => (
                                    <FormItem>
                                        <FormLabel>Email</FormLabel>
                                        <FormControl>
                                            <Input placeholder="you@example.com" type="email" {...field} />
                                        </FormControl>
                                        <FormMessage />
                                    </FormItem>
                                )}
                            />
                            <FormField
                                control={passwordForm.control}
                                name="password"
                                render={({ field }) => (
                                    <FormItem>
                                        <div className="flex items-center justify-between">
                                            <FormLabel>Password</FormLabel>
                                        </div>
                                        <FormControl>
                                            <Input type="password" placeholder="••••••••" {...field} />
                                        </FormControl>
                                        <FormMessage />
                                    </FormItem>
                                )}
                            />
                            <Button type="submit" className="w-full" disabled={isPasswordLoading}>
                                {isPasswordLoading ? (
                                    <><Loader2 className="mr-2 h-4 w-4 animate-spin" /> Signing in...</>
                                ) : "Sign In"}
                            </Button>
                        </form>
                    </Form>
                )}

                {/* ── Magic Link Mode ── */}
                {mode === "magic" && (
                    <Form {...magicForm}>
                        <form onSubmit={magicForm.handleSubmit(onMagicLinkSubmit)} className="space-y-4">
                            <FormField
                                control={magicForm.control}
                                name="email"
                                render={({ field }) => (
                                    <FormItem>
                                        <FormLabel>Email</FormLabel>
                                        <FormControl>
                                            <Input placeholder="you@example.com" type="email" {...field} />
                                        </FormControl>
                                        <FormMessage />
                                    </FormItem>
                                )}
                            />
                            <Button type="submit" className="w-full" disabled={isMagicLinkLoading}>
                                {isMagicLinkLoading ? (
                                    <><Loader2 className="mr-2 h-4 w-4 animate-spin" /> Sending link...</>
                                ) : (
                                    <><Mail className="mr-2 h-4 w-4" /> Send Magic Link</>
                                )}
                            </Button>
                        </form>
                    </Form>
                )}

                {/* ── Toggle Mode ── */}
                <Button
                    variant="ghost"
                    size="sm"
                    className="w-full text-muted-foreground text-xs"
                    type="button"
                    onClick={() => setMode(mode === "password" ? "magic" : "password")}
                >
                    {mode === "password"
                        ? "Sign in with a magic link instead →"
                        : "← Use password instead"}
                </Button>

                {/* ── Divider ── */}
                <div className="relative">
                    <div className="absolute inset-0 flex items-center">
                        <span className="w-full border-t" />
                    </div>
                    <div className="relative flex justify-center text-xs uppercase">
                        <span className="bg-card px-2 text-muted-foreground">Or continue with</span>
                    </div>
                </div>

                {/* ── Google ── */}
                <Button
                    variant="outline"
                    className="w-full"
                    type="button"
                    onClick={handleGoogleLogin}
                    disabled={isGoogleLoading}
                >
                    <svg className="mr-2 h-4 w-4" aria-hidden="true" focusable="false" role="img" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 488 512">
                        <path fill="currentColor" d="M488 261.8C488 403.3 391.1 504 248 504 110.8 504 0 393.2 0 256S110.8 8 248 8c66.8 0 123 24.5 166.3 64.9l-67.5 64.9C258.5 52.6 94.3 116.6 94.3 256c0 86.5 69.1 156.6 153.7 156.6 98.2 0 135-70.4 140.8-106.9H248v-85.3h236.1c2.3 12.7 3.9 24.9 3.9 41.4z" />
                    </svg>
                    {isGoogleLoading ? "Redirecting..." : "Sign in with Google"}
                </Button>

                <div className="text-center text-sm">
                    Don&apos;t have an account?{" "}
                    <Link href="/signup" className="underline font-medium">Sign up</Link>
                </div>
            </CardContent>
        </Card>
    )
}
