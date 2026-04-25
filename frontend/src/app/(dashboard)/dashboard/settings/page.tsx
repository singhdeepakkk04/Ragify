"use client"

import { useState, useEffect } from "react"
import { useAuthStore } from "@/lib/auth"
import { useTheme } from "next-themes"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import { Separator } from "@/components/ui/separator"
import { Switch } from "@/components/ui/switch"
import { AlertCircle, CreditCard, Moon, Sun, Monitor, User, Trash2, Mail } from "lucide-react"
import { toast } from "sonner"
import api from "@/lib/api"
import {
    AlertDialog,
    AlertDialogAction,
    AlertDialogCancel,
    AlertDialogContent,
    AlertDialogDescription,
    AlertDialogFooter,
    AlertDialogHeader,
    AlertDialogTitle,
    AlertDialogTrigger,
} from "@/components/ui/alert-dialog"

export default function SettingsPage() {
    const { user, logout } = useAuthStore()
    const { theme, setTheme } = useTheme()
    const [isLoading, setIsLoading] = useState(false)
    const [displayName, setDisplayName] = useState("")

    // Load profile on mount
    useEffect(() => {
        api.get("/users/me")
            .then(res => {
                if (res.data.display_name) setDisplayName(res.data.display_name)
            })
            .catch(() => {})
    }, [])

    const handleUpdateProfile = async () => {
        setIsLoading(true)
        try {
            await api.patch("/users/me", { display_name: displayName })
            toast.success("Profile updated successfully")
        } catch {
            toast.error("Failed to update profile")
        } finally {
            setIsLoading(false)
        }
    }

    const handleDeleteAccount = async () => {
        try {
            await api.delete("/users/me")
            toast.success("Account deleted successfully")
            logout()
        } catch {
            toast.error("Failed to delete account. Please try again.")
        }
    }

    const firstName = displayName || user?.email?.split("@")[0] || "User"
    const initials = firstName.slice(0, 2).toUpperCase()

    return (
        <div className="max-w-4xl space-y-8 animate-in fade-in duration-500">
            <div>
                <h2 className="text-3xl font-bold tracking-tight" style={{ fontFamily: 'var(--font-serif), Georgia, serif' }}>Settings</h2>
                <p className="text-muted-foreground mt-1">
                    Manage your account settings and preferences.
                </p>
            </div>

            <Tabs defaultValue="general" className="w-full">
                <TabsList className="bg-muted/50 w-full justify-start overflow-x-auto">
                    <TabsTrigger value="general">General</TabsTrigger>
                    <TabsTrigger value="billing">Billing</TabsTrigger>
                    <TabsTrigger value="appearance">Appearance</TabsTrigger>
                    <TabsTrigger value="notifications">Notifications</TabsTrigger>
                </TabsList>

                {/* General Settings */}
                <TabsContent value="general" className="space-y-6 mt-6">
                    <Card>
                        <CardHeader>
                            <CardTitle>Profile</CardTitle>
                            <CardDescription>
                                This is how others will see you on the site.
                            </CardDescription>
                        </CardHeader>
                        <CardContent className="space-y-6">
                            <div className="flex items-center gap-6">
                                <Avatar className="h-20 w-20">
                                    <AvatarImage src="" />
                                    <AvatarFallback className="text-lg bg-primary/10 text-primary font-bold">
                                        {initials}
                                    </AvatarFallback>
                                </Avatar>
                                <div className="space-y-1">
                                    <Button variant="outline" size="sm">Change Avatar</Button>
                                    <p className="text-xs text-muted-foreground">JPG, GIF or PNG. 1MB max.</p>
                                </div>
                            </div>

                            <Separator />

                            <div className="grid gap-4 md:grid-cols-2">
                                <div className="space-y-2">
                                    <Label htmlFor="name">Display Name</Label>
                                    <Input id="name" placeholder="Your name" value={displayName} onChange={(e) => setDisplayName(e.target.value)} />
                                </div>
                                <div className="space-y-2">
                                    <Label htmlFor="email">Email</Label>
                                    <Input id="email" value={user?.email || ""} disabled className="bg-muted" />
                                    <p className="text-[11px] text-muted-foreground flex items-center gap-1">
                                        <Mail className="h-3 w-3" /> Managed by Supabase Auth
                                    </p>
                                </div>
                            </div>
                        </CardContent>
                        <CardFooter className="border-t px-6 py-4 bg-muted/20 flex justify-end">
                            <Button onClick={handleUpdateProfile} disabled={isLoading}>
                                {isLoading ? "Saving..." : "Save Changes"}
                            </Button>
                        </CardFooter>
                    </Card>

                    <Card className="border-destructive/30">
                        <CardHeader>
                            <CardTitle className="text-destructive flex items-center gap-2">
                                <AlertCircle className="h-5 w-5" /> Danger Zone
                            </CardTitle>
                            <CardDescription>
                                Irreversible actions for your account.
                            </CardDescription>
                        </CardHeader>
                        <CardContent>
                            <div className="flex items-center justify-between">
                                <div className="space-y-1">
                                    <p className="font-medium text-sm">Delete Account</p>
                                    <p className="text-xs text-muted-foreground">
                                        Permanently delete your account and all data.
                                    </p>
                                </div>
                                <AlertDialog>
                                    <AlertDialogTrigger asChild>
                                        <Button variant="destructive" size="sm">Delete Account</Button>
                                    </AlertDialogTrigger>
                                    <AlertDialogContent>
                                        <AlertDialogHeader>
                                            <AlertDialogTitle>Are you absolutely sure?</AlertDialogTitle>
                                            <AlertDialogDescription>
                                                This action cannot be undone. This will permanently delete your account and remove your data from our servers.
                                            </AlertDialogDescription>
                                        </AlertDialogHeader>
                                        <AlertDialogFooter>
                                            <AlertDialogCancel>Cancel</AlertDialogCancel>
                                            <AlertDialogAction onClick={handleDeleteAccount} className="bg-destructive text-destructive-foreground hover:bg-destructive/90">
                                                Delete Account
                                            </AlertDialogAction>
                                        </AlertDialogFooter>
                                    </AlertDialogContent>
                                </AlertDialog>
                            </div>
                        </CardContent>
                    </Card>
                </TabsContent>

                {/* Billing Settings */}
                <TabsContent value="billing" className="space-y-6 mt-6">
                    <Card>
                        <CardHeader>
                            <CardTitle>Subscription Plan</CardTitle>
                            <CardDescription>
                                You are currently on the <span className="font-semibold text-foreground">Free Plan</span>.
                            </CardDescription>
                        </CardHeader>
                        <CardContent className="space-y-4">
                            <div className="rounded-lg border p-4 bg-muted/30">
                                <div className="flex items-center justify-between">
                                    <div className="flex items-center gap-3">
                                        <div className="h-10 w-10 rounded-full bg-primary/10 flex items-center justify-center">
                                            <CreditCard className="h-5 w-5 text-primary" />
                                        </div>
                                        <div>
                                            <p className="font-medium text-sm">Free Tier</p>
                                            <p className="text-xs text-muted-foreground">$0 / month</p>
                                        </div>
                                    </div>
                                    <Button variant="outline" size="sm" disabled>Current Plan</Button>
                                </div>
                            </div>

                            <div className="space-y-2">
                                <div className="flex items-center justify-between text-sm">
                                    <span>Projects Used</span>
                                    <span className="font-medium">3 / 5</span>
                                </div>
                                <div className="h-2 w-full bg-muted rounded-full overflow-hidden">
                                    <div className="h-full bg-primary w-[60%]" />
                                </div>
                                <p className="text-xs text-muted-foreground">Upgrade to Pro for unlimited projects.</p>
                            </div>
                        </CardContent>
                        <CardFooter className="border-t px-6 py-4 bg-muted/20 flex justify-end">
                            <Button>Upgrade to Pro</Button>
                        </CardFooter>
                    </Card>
                </TabsContent>

                {/* Appearance Settings */}
                <TabsContent value="appearance" className="space-y-6 mt-6">
                    <Card>
                        <CardHeader>
                            <CardTitle>Theme</CardTitle>
                            <CardDescription>
                                Customize the look and feel of the dashboard.
                            </CardDescription>
                        </CardHeader>
                        <CardContent>
                            <div className="grid grid-cols-3 gap-4 max-w-lg">
                                <div className="space-y-2 cursor-pointer" onClick={() => setTheme("light")}>
                                    <div className={`rounded-lg border-2 p-1 hover:border-primary transition-all ${theme === 'light' ? 'border-primary bg-primary/5' : 'border-muted'}`}>
                                        <div className="space-y-2 rounded-md bg-[#ecedef] p-2">
                                            <div className="space-y-2 rounded-md bg-white p-2 shadow-sm">
                                                <div className="h-2 w-[80px] rounded-lg bg-[#ecedef]" />
                                                <div className="h-2 w-[100px] rounded-lg bg-[#ecedef]" />
                                            </div>
                                            <div className="flex items-center space-x-2 rounded-md bg-white p-2 shadow-sm">
                                                <div className="h-4 w-4 rounded-full bg-[#ecedef]" />
                                                <div className="h-2 w-[100px] rounded-lg bg-[#ecedef]" />
                                            </div>
                                        </div>
                                    </div>
                                    <div className="flex items-center justify-center gap-2">
                                        <Sun className="h-4 w-4" />
                                        <span className="text-sm font-medium">Light</span>
                                    </div>
                                </div>
                                <div className="space-y-2 cursor-pointer" onClick={() => setTheme("dark")}>
                                    <div className={`rounded-lg border-2 p-1 hover:border-primary transition-all ${theme === 'dark' ? 'border-primary bg-primary/5' : 'border-muted'}`}>
                                        <div className="space-y-2 rounded-md bg-slate-950 p-2">
                                            <div className="space-y-2 rounded-md bg-slate-800 p-2 shadow-sm">
                                                <div className="h-2 w-[80px] rounded-lg bg-slate-400" />
                                                <div className="h-2 w-[100px] rounded-lg bg-slate-400" />
                                            </div>
                                            <div className="flex items-center space-x-2 rounded-md bg-slate-800 p-2 shadow-sm">
                                                <div className="h-4 w-4 rounded-full bg-slate-400" />
                                                <div className="h-2 w-[100px] rounded-lg bg-slate-400" />
                                            </div>
                                        </div>
                                    </div>
                                    <div className="flex items-center justify-center gap-2">
                                        <Moon className="h-4 w-4" />
                                        <span className="text-sm font-medium">Dark</span>
                                    </div>
                                </div>
                                <div className="space-y-2 cursor-pointer" onClick={() => setTheme("system")}>
                                    <div className={`rounded-lg border-2 p-1 hover:border-primary transition-all ${theme === 'system' ? 'border-primary bg-primary/5' : 'border-muted'}`}>
                                        <div className="space-y-2 rounded-md bg-slate-950 p-2">
                                            <div className="space-y-2 rounded-md bg-slate-800 p-2 shadow-sm">
                                                <div className="h-2 w-[80px] rounded-lg bg-slate-400" />
                                                <div className="h-2 w-[100px] rounded-lg bg-slate-400" />
                                            </div>
                                            <div className="flex items-center space-x-2 rounded-md bg-slate-800 p-2 shadow-sm">
                                                <div className="h-4 w-4 rounded-full bg-slate-400" />
                                                <div className="h-2 w-[100px] rounded-lg bg-slate-400" />
                                            </div>
                                        </div>
                                    </div>
                                    <div className="flex items-center justify-center gap-2">
                                        <Monitor className="h-4 w-4" />
                                        <span className="text-sm font-medium">System</span>
                                    </div>
                                </div>
                            </div>
                        </CardContent>
                    </Card>
                </TabsContent>

                {/* Notifications */}
                <TabsContent value="notifications" className="mt-6">
                    <Card>
                        <CardHeader>
                            <CardTitle>Notifications</CardTitle>
                            <CardDescription>
                                Configure how you receive alerts.
                            </CardDescription>
                        </CardHeader>
                        <CardContent className="space-y-4">
                            <div className="flex items-center justify-between space-x-2">
                                <Label htmlFor="email-notifs" className="flex flex-col space-y-1">
                                    <span>Email Notifications</span>
                                    <span className="font-normal text-xs text-muted-foreground">Receive weekly digests about your projects.</span>
                                </Label>
                                <Switch id="email-notifs" defaultChecked />
                            </div>
                            <Separator />
                            <div className="flex items-center justify-between space-x-2">
                                <Label htmlFor="api-alerts" className="flex flex-col space-y-1">
                                    <span>API Usage Alerts</span>
                                    <span className="font-normal text-xs text-muted-foreground">Get notified when you approach your plan limits.</span>
                                </Label>
                                <Switch id="api-alerts" defaultChecked />
                            </div>
                        </CardContent>
                    </Card>
                </TabsContent>
            </Tabs>
        </div>
    )
}
