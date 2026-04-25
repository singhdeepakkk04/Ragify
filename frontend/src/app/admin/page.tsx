"use client"

import { useEffect, useState } from "react"
import { useAuthStore } from "@/lib/auth"
import api from "@/lib/api"
import { useRouter } from "next/navigation"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { toast } from "sonner"

export default function AdminDashboard() {
    const { user } = useAuthStore()
    const router = useRouter()
    const [stats, setStats] = useState<any>(null)
    const [users, setUsers] = useState<any[]>([])

    useEffect(() => {
        if (!user) {
            router.push("/login")
            return // don't execute further
        }

        // Simple client-side role check (backend enforces real security)
        // We need to decode token/check user object.
        // Assuming /users/me returns role, or we stored it in auth store.
        // If not stored, we'll find out when api calls 403.

        const fetchData = async () => {
            try {
                const statsRes = await api.get("/admin/stats")
                setStats(statsRes.data)

                const usersRes = await api.get("/admin/users")
                setUsers(usersRes.data)
            } catch (error: any) {
                console.error("Admin Access Error", error)
                if (error.response?.status === 403) {
                    toast.error("Access Denied: Admin only")
                    router.push("/dashboard")
                }
            }
        }
        fetchData()
    }, [user, router])

    if (!stats) return <div className="p-8">Loading Admin Panel...</div>

    return (
        <div className="flex min-h-screen w-full flex-col p-8 space-y-8">
            <h1 className="text-3xl font-bold">Admin Dashboard</h1>

            <div className="grid gap-4 md:grid-cols-3">
                <Card>
                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                        <CardTitle className="text-sm font-medium">Total Users</CardTitle>
                    </CardHeader>
                    <CardContent>
                        <div className="text-2xl font-bold">{stats.total_users}</div>
                    </CardContent>
                </Card>
                <Card>
                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                        <CardTitle className="text-sm font-medium">Total Projects</CardTitle>
                    </CardHeader>
                    <CardContent>
                        <div className="text-2xl font-bold">{stats.total_projects}</div>
                    </CardContent>
                </Card>
                <Card>
                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                        <CardTitle className="text-sm font-medium">Total Documents</CardTitle>
                    </CardHeader>
                    <CardContent>
                        <div className="text-2xl font-bold">{stats.total_documents}</div>
                    </CardContent>
                </Card>
            </div>

            <Card>
                <CardHeader>
                    <CardTitle>User Management</CardTitle>
                </CardHeader>
                <CardContent>
                    <Table>
                        <TableHeader>
                            <TableRow>
                                <TableHead>ID</TableHead>
                                <TableHead>Email</TableHead>
                                <TableHead>Role</TableHead>
                                <TableHead>Status</TableHead>
                            </TableRow>
                        </TableHeader>
                        <TableBody>
                            {users.map((u) => (
                                <TableRow key={u.id}>
                                    <TableCell>{u.id}</TableCell>
                                    <TableCell>{u.email}</TableCell>
                                    <TableCell className="capitalize">{u.role}</TableCell>
                                    <TableCell>{u.is_active ? "Active" : "Inactive"}</TableCell>
                                </TableRow>
                            ))}
                        </TableBody>
                    </Table>
                </CardContent>
            </Card>
        </div>
    )
}
