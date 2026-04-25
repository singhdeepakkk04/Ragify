"use client"

import { useState, useEffect } from "react"
import api from "@/lib/api"
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import {
    BarChart3, Activity, Clock, FileText, FolderOpen,
    Zap, Loader2, AlertTriangle, Cpu
} from "lucide-react"
import {
    AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
    PieChart, Pie, Cell, Legend
} from 'recharts'

interface UsageData {
    total_queries: number
    queries_today: number
    queries_this_week: number
    total_documents: number
    total_projects: number
    avg_latency_ms: number
    rate_limit: { limit: number; remaining: number; used: number; window_seconds: number }
    model_breakdown: { model: string; count: number }[]
    project_breakdown: { project: string; queries: number; avg_latency: number }[]
    recent_queries: { query: string; model: string; latency_ms: number; timestamp: string; project: string }[]
    daily_usage: { date: string; queries: number }[]
}

export default function UsagePage() {
    const [data, setData] = useState<UsageData | null>(null)
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState<string | null>(null)

    useEffect(() => {
        api.get("/usage/")
            .then(res => { setData(res.data); setLoading(false) })
            .catch(err => {
                setError(err?.response?.data?.detail || "Failed to load usage data")
                setLoading(false)
            })
    }, [])

    if (loading) {
        return (
            <div className="flex items-center justify-center h-[60vh]">
                <div className="flex flex-col items-center gap-3">
                    <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
                    <p className="text-sm text-muted-foreground">Loading usage metrics...</p>
                </div>
            </div>
        )
    }

    if (error || !data) {
        return (
            <div className="flex items-center justify-center h-[60vh]">
                <div className="flex flex-col items-center gap-3 text-center">
                    <AlertTriangle className="h-8 w-8 text-destructive" />
                    <p className="text-sm text-destructive">{error || "No data"}</p>
                    <p className="text-xs text-muted-foreground">Make sure the usage_logs table exists. Run the migration first.</p>
                </div>
            </div>
        )
    }

    const maxModelCount = Math.max(...data.model_breakdown.map(m => m.count), 1)
    const maxDailyQueries = Math.max(...(data.daily_usage.map(d => d.queries) || [1]), 1)
    const rateLimitPercent = ((data.rate_limit.remaining / data.rate_limit.limit) * 100)

    return (
        <div className="w-full space-y-6">
            {/* Header */}
            <div>
                <h1 className="text-2xl font-bold tracking-tight" style={{ fontFamily: 'var(--font-geist-sans)' }}>
                    USAGE_METRICS
                </h1>
                <p className="text-sm text-muted-foreground mt-1 font-mono text-xs">
                    // MONITOR PIPELINE PERFORMANCE & COSTS
                </p>
            </div>

            {/* Stat Cards */}
            <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3">
                <StatCard icon={<Activity className="h-4 w-4" />} label="TOTAL QUERIES" value={data.total_queries} />
                <StatCard icon={<Zap className="h-4 w-4" />} label="TODAY" value={data.queries_today} accent />
                <StatCard icon={<BarChart3 className="h-4 w-4" />} label="THIS WEEK" value={data.queries_this_week} />
                <StatCard icon={<FileText className="h-4 w-4" />} label="DOCUMENTS" value={data.total_documents} />
                <StatCard icon={<FolderOpen className="h-4 w-4" />} label="PROJECTS" value={data.total_projects} />
                <StatCard icon={<Clock className="h-4 w-4" />} label="LATENCY (AVG)" value={`${data.avg_latency_ms}ms`} />
            </div>

            {/* Rate Limit Bar */}
            <Card className="border border-border/50 bg-card/50 shadow-sm">
                <CardContent className="pt-5 pb-4">
                    <div className="flex items-center justify-between mb-2">
                        <div className="flex items-center gap-2">
                            <Zap className="h-4 w-4 text-primary" />
                            <span className="text-sm font-medium font-mono uppercase tracking-wider">Rate Limit Status</span>
                        </div>
                        <span className="text-xs text-muted-foreground font-mono">
                            {data.rate_limit.remaining}/{data.rate_limit.limit} REQ/MIN
                        </span>
                    </div>
                    <div className="h-1 bg-muted rounded-full overflow-hidden">
                        <div
                            className={`h-full rounded-full transition-all duration-500 ${rateLimitPercent > 50 ? 'bg-primary' : rateLimitPercent > 20 ? 'bg-amber-500' : 'bg-red-500'}`}
                            style={{ width: `${rateLimitPercent}%` }}
                        />
                    </div>
                </CardContent>
            </Card>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
                {/* Daily Usage Chart */}
                <Card className="border shadow-sm overflow-hidden">
                    <CardHeader className="pb-3 bg-muted/10">
                        <CardTitle className="text-sm flex items-center gap-2">
                            <BarChart3 className="h-4 w-4 text-primary" />
                            Activity Pulse (7 Days)
                        </CardTitle>
                    </CardHeader>
                    <CardContent className="p-0">
                        {data.daily_usage.length > 0 ? (
                            <div className="h-[220px] w-full pt-4 pr-4">
                                <ResponsiveContainer width="100%" height="100%">
                                    <AreaChart data={data.daily_usage} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                                        <defs>
                                            <linearGradient id="colorQueries" x1="0" y1="0" x2="0" y2="1">
                                                <stop offset="5%" stopColor="hsl(var(--primary))" stopOpacity={0.4} />
                                                <stop offset="95%" stopColor="hsl(var(--primary))" stopOpacity={0} />
                                            </linearGradient>
                                        </defs>
                                        <XAxis
                                            dataKey="date"
                                            tickFormatter={(val) => new Date(val).toLocaleDateString('en', { weekday: 'short' })}
                                            axisLine={false}
                                            tickLine={false}
                                            tick={{ fontSize: 10, fill: 'hsl(var(--muted-foreground))' }}
                                            dy={10}
                                        />
                                        <YAxis
                                            axisLine={false}
                                            tickLine={false}
                                            tick={{ fontSize: 10, fill: 'hsl(var(--muted-foreground))' }}
                                        />
                                        <Tooltip
                                            contentStyle={{ backgroundColor: 'hsl(var(--card))', borderColor: 'hsl(var(--border))', borderRadius: '8px', fontSize: '12px' }}
                                            labelFormatter={(l) => new Date(l).toLocaleDateString()}
                                            itemStyle={{ color: 'hsl(var(--foreground))' }}
                                        />
                                        <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="hsl(var(--border))" opacity={0.4} />
                                        <Area
                                            type="monotone"
                                            dataKey="queries"
                                            stroke="hsl(var(--primary))"
                                            strokeWidth={3}
                                            fillOpacity={1}
                                            fill="url(#colorQueries)"
                                            activeDot={{ r: 6, strokeWidth: 0, fill: 'hsl(var(--primary))' }}
                                        />
                                    </AreaChart>
                                </ResponsiveContainer>
                            </div>
                        ) : (
                            <p className="text-sm text-muted-foreground text-center py-12">No activity detected this week.</p>
                        )}
                    </CardContent>
                </Card>

                {/* Model Breakdown */}
                <Card className="border shadow-sm overflow-hidden">
                    <CardHeader className="pb-3 bg-muted/10">
                        <CardTitle className="text-sm flex items-center gap-2">
                            <Cpu className="h-4 w-4 text-emerald-500" />
                            Compute Distribution
                        </CardTitle>
                    </CardHeader>
                    <CardContent className="p-0 flex items-center justify-center">
                        {data.model_breakdown.length > 0 ? (
                            <div className="h-[220px] w-full pt-4">
                                <ResponsiveContainer width="100%" height="100%">
                                    <PieChart>
                                        <Tooltip
                                            contentStyle={{ backgroundColor: 'hsl(var(--card))', borderColor: 'hsl(var(--border))', borderRadius: '8px', fontSize: '12px' }}
                                            itemStyle={{ color: 'hsl(var(--foreground))' }}
                                        />
                                        <Pie
                                            data={data.model_breakdown}
                                            dataKey="count"
                                            nameKey="model"
                                            cx="50%"
                                            cy="50%"
                                            innerRadius={60}
                                            outerRadius={85}
                                            paddingAngle={4}
                                            stroke="none"
                                        >
                                            {data.model_breakdown.map((entry, index) => {
                                                const colors = ['#3b82f6', '#10b981', '#f59e0b', '#8b5cf6', '#ef4444', '#06b6d4'];
                                                return <Cell key={`cell-${index}`} fill={colors[index % colors.length]} />
                                            })}
                                        </Pie>
                                        <Legend
                                            verticalAlign="bottom"
                                            height={36}
                                            iconType="circle"
                                            formatter={(value) => <span className="text-[10px] text-foreground font-medium uppercase tracking-wider">{value}</span>}
                                        />
                                    </PieChart>
                                </ResponsiveContainer>
                            </div>
                        ) : (
                            <p className="text-sm text-muted-foreground text-center py-12">No compute utilized yet.</p>
                        )}
                    </CardContent>
                </Card>
            </div>

            {/* Project Breakdown */}
            {data.project_breakdown.length > 0 && (
                <Card className="border shadow-sm">
                    <CardHeader className="pb-3">
                        <CardTitle className="text-sm">Usage by Project</CardTitle>
                    </CardHeader>
                    <CardContent>
                        <div className="overflow-x-auto">
                            <table className="w-full text-sm">
                                <thead>
                                    <tr className="border-b text-left">
                                        <th className="pb-2 font-medium text-muted-foreground">Project</th>
                                        <th className="pb-2 font-medium text-muted-foreground text-center">Queries</th>
                                        <th className="pb-2 font-medium text-muted-foreground text-right">Avg Latency</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {data.project_breakdown.map((p, i) => (
                                        <tr key={i} className="border-b last:border-0">
                                            <td className="py-2.5 font-medium">{p.project}</td>
                                            <td className="py-2.5 text-center">
                                                <Badge variant="secondary" className="text-[10px]">{p.queries}</Badge>
                                            </td>
                                            <td className="py-2.5 text-right text-muted-foreground">{p.avg_latency}ms</td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>
                    </CardContent>
                </Card>
            )}

            {/* Recent Queries */}
            {data.recent_queries.length > 0 && (
                <Card className="border shadow-sm">
                    <CardHeader className="pb-3">
                        <CardTitle className="text-sm">Recent Queries</CardTitle>
                        <CardDescription className="text-xs">Last 20 queries across all projects</CardDescription>
                    </CardHeader>
                    <CardContent>
                        <div className="space-y-2 max-h-[400px] overflow-y-auto">
                            {data.recent_queries.map((q, i) => (
                                <div key={i} className="flex items-start justify-between py-2 px-3 rounded-lg hover:bg-muted/50 transition-colors border-b last:border-0">
                                    <div className="flex-1 min-w-0 mr-4">
                                        <p className="text-sm truncate">{q.query}</p>
                                        <div className="flex items-center gap-2 mt-0.5">
                                            <span className="text-[10px] text-muted-foreground">{q.project}</span>
                                            <span className="text-[10px] text-muted-foreground">·</span>
                                            <Badge variant="outline" className="text-[10px] px-1.5 py-0">{q.model}</Badge>
                                        </div>
                                    </div>
                                    <div className="text-right shrink-0">
                                        <p className="text-xs text-muted-foreground">{q.latency_ms}ms</p>
                                        <p className="text-[10px] text-muted-foreground">
                                            {new Date(q.timestamp).toLocaleString('en', { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' })}
                                        </p>
                                    </div>
                                </div>
                            ))}
                        </div>
                    </CardContent>
                </Card>
            )}
        </div>
    )
}

/* ── Stat Card Component ── */
function StatCard({ icon, label, value, accent }: { icon: React.ReactNode; label: string; value: string | number; accent?: boolean }) {
    return (
        <Card className={`border border-border/50 bg-card/50 shadow-sm hover:border-primary/30 transition-colors ${accent ? 'border-primary/20 bg-primary/5' : ''}`}>
            <CardContent className="pt-4 pb-3 px-4">
                <div className="flex items-center gap-2 text-muted-foreground mb-1.5 opacity-80">
                    {icon}
                    <span className="text-[10px] font-mono uppercase tracking-wider">{label}</span>
                </div>
                <p className="text-xl font-bold font-mono tracking-tight">{value}</p>
            </CardContent>
        </Card>
    )
}
