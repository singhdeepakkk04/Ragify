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
import Link from "next/link"
import { createClient } from "@/lib/supabase"
import { Mail, CheckCircle2, Loader2 } from "lucide-react"

const formSchema = z.object({
    email: z.string().email("Please enter a valid email address."),
    password: z.string().min(8, {
        message: "Password must be at least 8 characters.",
    }),
    confirmPassword: z.string()
}).refine((data) => data.password === data.confirmPassword, {
    message: "Passwords do not match",
    path: ["confirmPassword"],
})

export default function SignupPage() {
    const supabase = createClient()
    const [isLoading, setIsLoading] = useState(false)
    const [emailSent, setEmailSent] = useState(false)
    const [submittedEmail, setSubmittedEmail] = useState("")

    const form = useForm<z.infer<typeof formSchema>>({
        resolver: zodResolver(formSchema),
        defaultValues: { email: "", password: "", confirmPassword: "" },
    })

    async function onSubmit(values: z.infer<typeof formSchema>) {
        setIsLoading(true)
        try {
            const { error } = await supabase.auth.signUp({
                email: values.email,
                password: values.password,
                options: {
                    emailRedirectTo: `${window.location.origin}/auth/callback`,
                },
            })

            if (error) {
                toast.error(error.message)
                return
            }

            setSubmittedEmail(values.email)
            setEmailSent(true)
        } catch {
            toast.error("Something went wrong. Please try again.")
        } finally {
            setIsLoading(false)
        }
    }

    // ── Email Sent Confirmation Screen ──────────────────────────────────────
    if (emailSent) {
        return (
            <Card>
                <CardContent className="pt-8 pb-8 flex flex-col items-center text-center gap-4">
                    <div className="h-16 w-16 rounded-full bg-emerald-100 dark:bg-emerald-900/30 flex items-center justify-center">
                        <Mail className="h-8 w-8 text-emerald-600" />
                    </div>
                    <div>
                        <h2 className="text-xl font-bold mb-1">Check your inbox</h2>
                        <p className="text-sm text-muted-foreground max-w-xs">
                            We sent a confirmation link to{" "}
                            <span className="font-semibold text-foreground">{submittedEmail}</span>.
                            Click the link to activate your account.
                        </p>
                    </div>
                    <div className="w-full space-y-2 pt-2">
                        <p className="text-xs text-muted-foreground">Didn&apos;t receive it?</p>
                        <Button
                            variant="outline"
                            size="sm"
                            className="w-full"
                            onClick={async () => {
                                await supabase.auth.resend({
                                    type: "signup",
                                    email: submittedEmail,
                                    options: { emailRedirectTo: `${window.location.origin}/auth/callback` },
                                })
                                toast.success("Confirmation email resent!")
                            }}
                        >
                            Resend Email
                        </Button>
                        <Link href="/login">
                            <Button variant="ghost" size="sm" className="w-full text-muted-foreground">
                                Back to Login
                            </Button>
                        </Link>
                    </div>
                </CardContent>
            </Card>
        )
    }

    // ── Signup Form ──────────────────────────────────────────────────────────
    return (
        <Card>
            <CardHeader>
                <CardTitle>Create an account</CardTitle>
                <CardDescription>
                    Enter your email and password to get started.
                </CardDescription>
            </CardHeader>
            <CardContent>
                <Form {...form}>
                    <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
                        <FormField
                            control={form.control}
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
                            control={form.control}
                            name="password"
                            render={({ field }) => (
                                <FormItem>
                                    <FormLabel>Password</FormLabel>
                                    <FormControl>
                                        <Input type="password" placeholder="Min. 8 characters" {...field} />
                                    </FormControl>
                                    <FormMessage />
                                </FormItem>
                            )}
                        />
                        <FormField
                            control={form.control}
                            name="confirmPassword"
                            render={({ field }) => (
                                <FormItem>
                                    <FormLabel>Confirm Password</FormLabel>
                                    <FormControl>
                                        <Input type="password" placeholder="Repeat your password" {...field} />
                                    </FormControl>
                                    <FormMessage />
                                </FormItem>
                            )}
                        />
                        <Button type="submit" className="w-full" disabled={isLoading}>
                            {isLoading ? (
                                <><Loader2 className="mr-2 h-4 w-4 animate-spin" /> Creating account...</>
                            ) : (
                                "Create Account"
                            )}
                        </Button>
                    </form>
                </Form>
                <div className="mt-4 text-center text-sm">
                    Already have an account?{" "}
                    <Link href="/login" className="underline font-medium">
                        Log in
                    </Link>
                </div>
            </CardContent>
        </Card>
    )
}
