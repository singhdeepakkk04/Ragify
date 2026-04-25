"use client"

import Link from "next/link"
import { Button } from "@/components/ui/button"
import { ArrowRight, Database, Lock, Code, Zap, Globe, Cpu, TerminalSquare, MessageSquare, FileSearch, Bot, Shield, BarChart3, Users, BookOpen, ChevronDown, Github, Twitter, Linkedin, Mail, Layers, Workflow, Sparkles, Clock, CheckCircle2 } from "lucide-react"
import { useState } from "react"
import { useAuthStore } from "@/lib/auth"
import { useEffect } from "react"

export default function LandingPage() {
  const { isAuthenticated, isLoading, initialize } = useAuthStore()
  const [openFaq, setOpenFaq] = useState<number | null>(null)

  useEffect(() => {
    initialize()
  }, [initialize])

  return (
    <div className="flex min-h-screen flex-col bg-[#FAFAFA] text-slate-900 selection:bg-slate-200 selection:text-black overflow-hidden font-sans relative">
      
      {/* Premium Light Background Effects */}
      <div className="absolute top-0 inset-x-0 h-[800px] bg-gradient-to-b from-slate-200/50 via-slate-50/20 to-transparent pointer-events-none" />
      <div className="absolute top-[-20%] left-[50%] translate-x-[-50%] w-[1000px] h-[500px] bg-white opacity-80 blur-[100px] rounded-full pointer-events-none" />
      {/* Subtle grid texture overlay */}
      <div className="absolute inset-0 bg-[linear-gradient(to_right,#e2e8f0_1px,transparent_1px),linear-gradient(to_bottom,#e2e8f0_1px,transparent_1px)] bg-[size:4rem_4rem] [mask-image:radial-gradient(ellipse_60%_50%_at_50%_0%,#000_70%,transparent_100%)] opacity-30 pointer-events-none" />

      {/* Glassmorphic Header */}
      <header className="fixed top-0 z-50 w-full border-b border-slate-200/50 bg-white/70 backdrop-blur-xl supports-[backdrop-filter]:bg-white/60">
        <div className="container mx-auto flex h-16 items-center justify-between px-6">
          <Link className="flex items-center gap-2.5 group" href="/">
            <img src="/logo.svg" alt="RAGify Logo" className="h-7 w-auto transition-transform duration-300 group-hover:scale-105" />
          </Link>
          <nav className="hidden md:flex items-center gap-8">
            <Link className="text-sm font-medium text-slate-500 hover:text-slate-900 transition-colors" href="#features">Features</Link>
            <Link className="text-sm font-medium text-slate-500 hover:text-slate-900 transition-colors" href="#use-cases">Use Cases</Link>
            <Link className="text-sm font-medium text-slate-500 hover:text-slate-900 transition-colors" href="#pricing">Pricing</Link>
            <Link className="text-sm font-medium text-slate-500 hover:text-slate-900 transition-colors" href="#faq">FAQ</Link>
            
            <div className="w-px h-5 bg-slate-200" />
            
            {isLoading ? (
              <div className="h-9 w-24 animate-pulse bg-slate-200 rounded-full" />
            ) : isAuthenticated ? (
              <Link href="/dashboard">
                <Button size="sm" className="h-9 rounded-full px-5 bg-black text-white hover:bg-slate-800 text-sm font-medium transition-all shadow-md hover:shadow-xl">
                  Dashboard
                </Button>
              </Link>
            ) : (
              <div className="flex items-center gap-3">
                <Link href="/login">
                  <Button variant="ghost" size="sm" className="h-9 rounded-full px-5 text-sm font-medium text-slate-600 hover:text-slate-900 hover:bg-slate-100 transition-colors">
                    Login
                  </Button>
                </Link>
                <Link href="/signup">
                  <Button size="sm" className="h-9 rounded-full px-5 bg-black text-white hover:bg-slate-800 text-sm font-medium transition-all shadow-md hover:shadow-lg hover:-translate-y-0.5">
                    Start Building
                  </Button>
                </Link>
              </div>
            )}
          </nav>
        </div>
      </header>

      <main className="flex-1 relative z-10 w-full">
        {/* Irresistible Hero Section */}
        <section className="pt-28 md:pt-32 pb-20 container mx-auto px-6 flex flex-col items-center text-center">
          
          {/* Version Badge */}
          <div className="animate-fade-in-up inline-flex items-center gap-2 border border-slate-200 bg-white px-3 py-1.5 text-xs font-semibold text-slate-600 mb-8 rounded-full shadow-sm">
            <span className="flex h-2 w-2 rounded-full bg-emerald-500 shadow-[0_0_10px_rgba(16,185,129,0.5)] animate-pulse" />
            RAG Engine v2.0 is Live
          </div>

          <h1 className="animate-fade-in-up delay-100 text-6xl sm:text-7xl md:text-[5.5rem] lg:text-[7rem] font-extrabold tracking-tight leading-[1.05] max-w-5xl mb-8">
            Give your AI a <br />
            <span className="bg-clip-text text-transparent bg-gradient-to-r from-slate-900 via-slate-600 to-slate-400">
              Photographic Memory.
            </span>
          </h1>

          <p className="animate-fade-in-up delay-200 text-lg md:text-xl text-slate-600 max-w-2xl leading-relaxed mb-10 font-medium">
            The premium knowledge retrieval engine for production AI apps. 
            No complex infrastructure. No vector tweaking. Just instant, hyper-accurate context.
          </p>

          <div className="animate-fade-in-up delay-300 flex flex-col sm:flex-row items-center gap-4 w-full sm:w-auto">
            <Link href={isAuthenticated ? "/dashboard" : "/signup"} className="w-full sm:w-auto">
              <Button size="lg" className="w-full sm:w-auto h-14 px-8 rounded-full bg-black text-white hover:bg-slate-800 text-base font-semibold shadow-[0_8px_30px_rgb(0,0,0,0.12)] hover:shadow-[0_8px_30px_rgb(0,0,0,0.2)] hover:-translate-y-1 transition-all duration-300 group">
                {isAuthenticated ? "Enter Console" : "Get Started for Free"}
                <ArrowRight className="ml-2 h-4 w-4 group-hover:translate-x-1 transition-transform" />
              </Button>
            </Link>
            <Link href="#documentation" className="w-full sm:w-auto">
              <Button variant="outline" size="lg" className="w-full sm:w-auto h-14 px-8 rounded-full border-slate-200 bg-white/50 hover:bg-slate-50 text-slate-700 text-base font-semibold backdrop-blur-md transition-all shadow-sm">
                <TerminalSquare className="mr-2 h-4 w-4" />
                Read the Docs
              </Button>
            </Link>
          </div>
        </section>

        {/* High-Contrast Beautiful Terminal Showcase */}
        <section className="animate-fade-in-up delay-[400ms] container mx-auto px-6 mb-32 flex justify-center">
          <div className="w-full max-w-4xl rounded-2xl p-2 bg-gradient-to-b from-slate-200 to-slate-100 shadow-2xl shadow-slate-200/50">
            <div className="w-full bg-[#0D1117] rounded-xl overflow-hidden shadow-inner border border-white/10">
              {/* Mac Window Controls */}
              <div className="flex items-center gap-2 px-4 py-3 bg-[#161B22] border-b border-white/5">
                <div className="w-3 h-3 rounded-full bg-[#FF5F56] border border-black/10" />
                <div className="w-3 h-3 rounded-full bg-[#FFBD2E] border border-black/10" />
                <div className="w-3 h-3 rounded-full bg-[#27C93F] border border-black/10" />
                <div className="flex-1 text-center text-xs font-mono text-slate-400">api.ragify.net/v1/query</div>
              </div>
              
              <div className="p-6 md:p-8 font-mono text-sm md:text-base leading-relaxed text-slate-300 overflow-x-auto">
                <div className="flex">
                  <span className="text-[#7ee787] mr-3">❯</span>
                  <span className="text-[#79c0ff]">curl</span> -X POST https://api.ragify.net/v1/query \
                </div>
                <div className="flex">
                  <span className="text-transparent mr-3">❯</span>
                  &nbsp;&nbsp;-H <span className="text-[#a5d6ff]">"Authorization: Bearer sk_live_..."</span> \
                </div>
                <div className="flex">
                  <span className="text-transparent mr-3">❯</span>
                  &nbsp;&nbsp;-d <span className="text-[#a5d6ff]">'{"{"}"query":"Extract standard operating procedure"{"}"}'</span>
                </div>
                <div className="flex mt-8">
                  <span className="text-slate-500">{"// RESPONSE"}</span>
                </div>
                <div className="flex">
                  <span className="text-slate-300">{"{"}</span>
                </div>
                <div className="flex">
                  &nbsp;&nbsp;<span className="text-[#79c0ff]">"data"</span>: <span className="text-[#a5d6ff]">"The SOP requires triple redundancy..."</span>,
                </div>
                <div className="flex">
                  &nbsp;&nbsp;<span className="text-[#79c0ff]">"sources"</span>: [
                  <span className="text-[#a5d6ff]">"operations_manual.pdf:p42"</span>
                  ],
                </div>
                <div className="flex">
                  &nbsp;&nbsp;<span className="text-[#79c0ff]">"latency_ms"</span>: <span className="text-[#ff7b72]">42</span>
                </div>
                <div className="flex">
                  <span className="text-slate-300">{"}"}</span>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* Integrations Marquee / Tech Stack */}
        <section className="py-12 border-y border-slate-200/50 bg-white/40 backdrop-blur-sm">
          <div className="container mx-auto px-6">
            <p className="text-center text-sm font-semibold text-slate-400 uppercase tracking-widest mb-8">
              Engineered to support the best in AI
            </p>
            <div className="flex flex-wrap justify-center items-center gap-8 md:gap-16 opacity-60 grayscale hover:grayscale-0 transition-all duration-500">
              <span className="text-xl font-bold font-mono text-slate-800 tracking-tighter">OpenAI</span>
              <span className="text-xl font-bold font-serif text-slate-800 italic tracking-tight">Anthropic</span>
              <span className="text-xl font-bold font-sans text-slate-800 tracking-widest">pgvector</span>
              <span className="text-xl font-black font-mono text-slate-800 tracking-tight">DeepSeek</span>
              <span className="text-xl font-bold font-sans text-slate-800">Meta Llama</span>
            </div>
          </div>
        </section>

        {/* Stats / Social Proof */}
        <section className="py-16 bg-white border-b border-slate-200/50">
          <div className="container mx-auto px-6">
            <div className="grid grid-cols-2 md:grid-cols-4 gap-8 max-w-5xl mx-auto text-center">
              <div className="space-y-2">
                <p className="text-4xl md:text-5xl font-extrabold text-slate-900 tracking-tight">10M+</p>
                <p className="text-sm font-semibold text-slate-500 uppercase tracking-wider">Queries Processed</p>
              </div>
              <div className="space-y-2">
                <p className="text-4xl md:text-5xl font-extrabold text-slate-900 tracking-tight">99.99%</p>
                <p className="text-sm font-semibold text-slate-500 uppercase tracking-wider">Uptime SLA</p>
              </div>
              <div className="space-y-2">
                <p className="text-4xl md:text-5xl font-extrabold text-slate-900 tracking-tight">&lt;42ms</p>
                <p className="text-sm font-semibold text-slate-500 uppercase tracking-wider">Avg Latency</p>
              </div>
              <div className="space-y-2">
                <p className="text-4xl md:text-5xl font-extrabold text-slate-900 tracking-tight">2,500+</p>
                <p className="text-sm font-semibold text-slate-500 uppercase tracking-wider">Teams Building</p>
              </div>
            </div>
          </div>
        </section>

        {/* Hyperscale How It Works Section */}
        <section id="how-it-works" className="py-24 bg-white relative border-b border-slate-200/50 overflow-hidden">
          {/* Decorative background grids */}
          <div className="absolute inset-0 bg-[linear-gradient(to_right,#f1f5f9_1px,transparent_1px),linear-gradient(to_bottom,#f1f5f9_1px,transparent_1px)] bg-[size:3rem_3rem] [mask-image:radial-gradient(ellipse_80%_50%_at_50%_50%,#000_20%,transparent_100%)] opacity-50 pointer-events-none" />
          
          <div className="container mx-auto px-6 relative z-10">
            <div className="text-center mb-20 max-w-4xl mx-auto">
              <h2 className="text-4xl md:text-6xl font-extrabold tracking-tight mb-6 text-slate-900 leading-tight">
                Three Steps to <span className="text-transparent bg-clip-text bg-gradient-to-r from-slate-600 to-slate-400">Omniscience.</span>
              </h2>
              <p className="text-lg md:text-xl text-slate-600 font-medium leading-relaxed">
                We've abstracted months of complex vector engineering and infrastructure scaling into three devastatingly simple API calls. 
              </p>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-3 gap-12 relative max-w-6xl mx-auto">
              {/* Animated Connecting Laser Line */}
              <div className="hidden md:block absolute top-[2.5rem] left-[16%] right-[16%] h-[2px] bg-slate-100 z-0 overflow-hidden">
                <div className="absolute top-0 bottom-0 w-[200px] h-full bg-gradient-to-r from-transparent via-slate-400 to-transparent opacity-50 animate-[pulse_3s_infinite]" />
              </div>
              
              {/* Step 1 */}
              <div className="relative z-10 flex flex-col items-center text-center group cursor-default">
                <div className="w-20 h-20 rounded-2xl bg-white border border-slate-200 shadow-[0_8px_30px_rgb(0,0,0,0.06)] flex items-center justify-center text-2xl font-black text-slate-900 mb-8 group-hover:scale-110 group-hover:shadow-[0_8px_30px_rgb(0,0,0,0.12)] transition-all duration-500 backdrop-blur-sm group-hover:bg-slate-900 group-hover:text-white group-hover:border-slate-900">1</div>
                <h3 className="text-xl font-bold text-slate-900 mb-4 tracking-tight">Polymorphic Ingestion</h3>
                <p className="text-slate-600 font-medium max-w-sm leading-relaxed">Stream raw PDFs, massive datalakes, or scattered docs into our secure ingestion fabric. We instantly parse and normalize the chaos.</p>
              </div>
              
              {/* Step 2 */}
              <div className="relative z-10 flex flex-col items-center text-center group cursor-default">
                <div className="absolute inset-0 bg-slate-900 blur-[80px] opacity-0 group-hover:opacity-10 transition-opacity duration-500 rounded-full" />
                <div className="w-20 h-20 rounded-2xl bg-slate-900 border border-slate-800 shadow-[0_8px_30px_rgb(0,0,0,0.12)] flex items-center justify-center text-2xl font-black text-white mb-8 group-hover:scale-110 transition-all duration-500 z-10">2</div>
                <h3 className="text-xl font-bold text-slate-900 mb-4 tracking-tight z-10">Zero-Config Vectorization</h3>
                <p className="text-slate-600 font-medium max-w-sm leading-relaxed z-10">Our engine identifies semantic boundaries, applies multi-dimensional embedding topology, and indexes data into a custom hardware-accelerated vector space.</p>
              </div>
              
              {/* Step 3 */}
              <div className="relative z-10 flex flex-col items-center text-center group cursor-default">
                <div className="w-20 h-20 rounded-2xl bg-white border border-slate-200 shadow-[0_8px_30px_rgb(0,0,0,0.06)] flex items-center justify-center text-2xl font-black text-slate-900 mb-8 group-hover:scale-110 group-hover:shadow-[0_8px_30px_rgb(0,0,0,0.12)] transition-all duration-500 group-hover:bg-emerald-500 group-hover:text-white group-hover:border-emerald-500">3</div>
                <h3 className="text-xl font-bold text-slate-900 mb-4 tracking-tight">Precision Injection</h3>
                <p className="text-slate-600 font-medium max-w-sm leading-relaxed">Submit an inference query and our retrieval fabric isolates hyper-relevant context, injecting seamless neural memories directly into your LLM prompt in under 50ms.</p>
              </div>
            </div>
          </div>
        </section>

        {/* Premium Bento Grid Features */}
        <section id="features" className="py-24 relative">
          <div className="container mx-auto px-6">
            <div className="text-center mb-16 max-w-3xl mx-auto">
              <h2 className="text-3xl md:text-5xl font-extrabold tracking-tight mb-6 text-slate-900">
                Engineered for <span className="text-slate-400">Precision.</span>
              </h2>
              <p className="text-lg text-slate-600 font-medium">
                We handle the complex orchestration of embeddings, vector storage, and retrieval, so you can focus on building the product.
              </p>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 auto-rows-fr">
              
              {/* Box 1 (Span 2 cols) */}
              <div className="md:col-span-2 bg-white rounded-3xl p-8 border border-slate-200 shadow-sm hover:shadow-xl hover:-translate-y-1 transition-all duration-300 relative overflow-hidden group">
                <div className="w-12 h-12 rounded-xl bg-slate-100 flex items-center justify-center mb-6 border border-slate-200 group-hover:bg-black group-hover:text-white transition-colors duration-300">
                  <Database className="h-6 w-6" />
                </div>
                <h3 className="text-2xl font-bold mb-3 text-slate-900 tracking-tight">Managed Vector Topology</h3>
                <p className="text-slate-600 text-base leading-relaxed max-w-lg font-medium">
                  Powered by custom pgvector pipelines with automated chunking, sophisticated embedding generation, and seamless document synchronization. Zero database maintenance required on your end.
                </p>
                <div className="absolute top-0 right-0 w-64 h-64 bg-slate-50 rounded-full blur-3xl -z-10 group-hover:bg-slate-100 transition-colors" />
              </div>

              {/* Box 2 */}
              <div className="bg-white rounded-3xl p-8 border border-slate-200 shadow-sm hover:shadow-xl hover:-translate-y-1 transition-all duration-300 group">
                <div className="w-12 h-12 rounded-xl bg-slate-100 flex items-center justify-center mb-6 border border-slate-200 group-hover:bg-black group-hover:text-white transition-colors duration-300">
                  <Zap className="h-6 w-6" />
                </div>
                <h3 className="text-xl font-bold mb-3 text-slate-900 tracking-tight">Ultra-Low Latency</h3>
                <p className="text-slate-600 text-base leading-relaxed font-medium">
                  Sub-50ms retrieval times, heavily optimized for responsive, real-time generative agents.
                </p>
              </div>

              {/* Box 3 */}
              <div className="bg-white rounded-3xl p-8 border border-slate-200 shadow-sm hover:shadow-xl hover:-translate-y-1 transition-all duration-300 group">
                <div className="w-12 h-12 rounded-xl bg-slate-100 flex items-center justify-center mb-6 border border-slate-200 group-hover:bg-black group-hover:text-white transition-colors duration-300">
                  <Lock className="h-6 w-6" />
                </div>
                <h3 className="text-xl font-bold mb-3 text-slate-900 tracking-tight">Military Grade Security</h3>
                <p className="text-slate-600 text-base leading-relaxed font-medium">
                  Strict tenancy boundaries, SHA-256 hashed API keys, and end-to-end encryption.
                </p>
              </div>

              {/* Box 4 */}
              <div className="bg-white rounded-3xl p-8 border border-slate-200 shadow-sm hover:shadow-xl hover:-translate-y-1 transition-all duration-300 group">
                <div className="w-12 h-12 rounded-xl bg-slate-100 flex items-center justify-center mb-6 border border-slate-200 group-hover:bg-black group-hover:text-white transition-colors duration-300">
                  <Cpu className="h-6 w-6" />
                </div>
                <h3 className="text-xl font-bold mb-3 text-slate-900 tracking-tight">Model Agnostic</h3>
                <p className="text-slate-600 text-base leading-relaxed font-medium">
                  Hot-swap between OpenAI, DeepSeek, and local Llama instantly without changing your codebase.
                </p>
              </div>

              {/* Box 5 */}
              <div className="bg-white rounded-3xl p-8 border border-slate-200 shadow-sm hover:shadow-xl hover:-translate-y-1 transition-all duration-300 group">
                <div className="w-12 h-12 rounded-xl bg-slate-100 flex items-center justify-center mb-6 border border-slate-200 group-hover:bg-black group-hover:text-white transition-colors duration-300">
                  <Globe className="h-6 w-6" />
                </div>
                <h3 className="text-xl font-bold mb-3 text-slate-900 tracking-tight">Edge Deployed</h3>
                <p className="text-slate-600 text-base leading-relaxed font-medium">
                  Globally distributed architecture ensuring consistent reliability and uptime.
                </p>
              </div>

            </div>
          </div>
        </section>

        {/* Use Cases Section */}
        <section id="use-cases" className="py-24 bg-white border-b border-slate-200/50">
          <div className="container mx-auto px-6">
            <div className="text-center mb-16 max-w-3xl mx-auto">
              <h2 className="text-3xl md:text-5xl font-extrabold tracking-tight mb-6 text-slate-900">
                Built for Every <span className="text-slate-400">Use Case.</span>
              </h2>
              <p className="text-lg text-slate-600 font-medium">
                From customer support bots to enterprise knowledge bases — RAGify powers intelligent retrieval across industries.
              </p>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8 max-w-6xl mx-auto">
              {[
                { icon: MessageSquare, title: "Customer Support AI", desc: "Build support agents that instantly surface answers from your knowledge base, tickets, and documentation." },
                { icon: FileSearch, title: "Enterprise Search", desc: "Enable employees to search across internal wikis, Confluence, Notion, and proprietary documents with natural language." },
                { icon: Bot, title: "AI Assistants & Copilots", desc: "Create context-aware copilots for coding, writing, research, or domain-specific workflows." },
                { icon: Layers, title: "Document Intelligence", desc: "Extract insights from contracts, research papers, compliance filings, and legal documents at scale." },
                { icon: Workflow, title: "Agentic Workflows", desc: "Power multi-step AI agents with persistent memory and real-time context retrieval across tool calls." },
                { icon: BarChart3, title: "Analytics & Reporting", desc: "Generate intelligent summaries and trend analysis from large datasets and historical reports." },
              ].map((useCase, i) => (
                <div key={i} className="bg-slate-50/50 rounded-2xl p-8 border border-slate-100 hover:bg-white hover:border-slate-200 hover:shadow-lg hover:-translate-y-1 transition-all duration-300 group">
                  <div className="w-11 h-11 rounded-xl bg-white border border-slate-200 flex items-center justify-center mb-5 group-hover:bg-slate-900 group-hover:text-white group-hover:border-slate-900 transition-colors duration-300">
                    <useCase.icon className="h-5 w-5" />
                  </div>
                  <h3 className="text-lg font-bold text-slate-900 mb-2 tracking-tight">{useCase.title}</h3>
                  <p className="text-slate-600 text-sm leading-relaxed font-medium">{useCase.desc}</p>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* Developer Experience / SDK Section */}
        <section id="developers" className="py-24 bg-slate-50/50 border-b border-slate-200/50">
          <div className="container mx-auto px-6">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-16 items-center max-w-6xl mx-auto">
              <div>
                <div className="inline-flex items-center gap-2 border border-slate-200 bg-white px-3 py-1.5 text-xs font-semibold text-slate-600 mb-6 rounded-full shadow-sm">
                  <Code className="h-3.5 w-3.5" />
                  Developer First
                </div>
                <h2 className="text-3xl md:text-5xl font-extrabold tracking-tight mb-6 text-slate-900 leading-tight">
                  Ship in <span className="text-transparent bg-clip-text bg-gradient-to-r from-slate-600 to-slate-400">Minutes,</span><br />Not Months.
                </h2>
                <p className="text-lg text-slate-600 font-medium leading-relaxed mb-8">
                  Our SDK is designed to feel invisible. Three lines of code to ingest your knowledge base. One line to query it. Full type-safety included.
                </p>
                <ul className="space-y-4">
                  {[
                    "Official SDKs for Python, TypeScript, and Go",
                    "OpenAPI spec with auto-generated clients",
                    "Webhook events for real-time sync",
                    "Comprehensive docs with runnable examples",
                  ].map((item, i) => (
                    <li key={i} className="flex items-center gap-3 text-sm font-medium text-slate-700">
                      <CheckCircle2 className="h-4 w-4 text-emerald-500 flex-shrink-0" />
                      {item}
                    </li>
                  ))}
                </ul>
              </div>
              <div className="w-full rounded-2xl p-2 bg-gradient-to-b from-slate-200 to-slate-100 shadow-xl">
                <div className="w-full bg-[#0D1117] rounded-xl overflow-hidden border border-white/10">
                  <div className="flex items-center gap-2 px-4 py-3 bg-[#161B22] border-b border-white/5">
                    <div className="w-3 h-3 rounded-full bg-[#FF5F56]" />
                    <div className="w-3 h-3 rounded-full bg-[#FFBD2E]" />
                    <div className="w-3 h-3 rounded-full bg-[#27C93F]" />
                    <div className="flex-1 text-center text-xs font-mono text-slate-400">app.py</div>
                  </div>
                  <div className="p-6 font-mono text-sm leading-relaxed text-slate-300 overflow-x-auto">
                    <div><span className="text-[#ff7b72]">from</span> <span className="text-[#79c0ff]">ez_ragify</span> <span className="text-[#ff7b72]">import</span> EzRagify</div>
                    <div className="mt-1"><span className="text-slate-500"># Initialize with your API key</span></div>
                    <div>client = <span className="text-[#79c0ff]">EzRagify</span>(api_key=<span className="text-[#a5d6ff]">"rag_live_..."</span>)</div>
                    <div className="mt-4"><span className="text-slate-500"># Upload documents</span></div>
                    <div>client.<span className="text-[#d2a8ff]">upload_document</span>(</div>
                    <div>&nbsp;&nbsp;project_id=<span className="text-[#79c0ff]">1</span>,</div>
                    <div>&nbsp;&nbsp;file=<span className="text-[#a5d6ff]">"./docs/policy.pdf"</span></div>
                    <div>)</div>
                    <div className="mt-4"><span className="text-slate-500"># Query with natural language</span></div>
                    <div>result = client.<span className="text-[#d2a8ff]">query</span>(</div>
                    <div>&nbsp;&nbsp;<span className="text-[#a5d6ff]">"What is the refund policy?"</span>,</div>
                    <div>&nbsp;&nbsp;project_id=<span className="text-[#79c0ff]">1</span></div>
                    <div>)</div>
                    <div className="mt-1"><span className="text-[#ff7b72]">print</span>(result.answer)&nbsp;&nbsp;<span className="text-slate-500"># Instant, sourced answer</span></div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* Pricing Section */}
        <section id="pricing" className="py-24 bg-slate-50/50 border-t border-slate-200/50">
          <div className="container mx-auto px-6">
            <div className="text-center mb-16 max-w-3xl mx-auto">
              <h2 className="text-3xl md:text-5xl font-extrabold tracking-tight mb-6 text-slate-900">
                Simple, transparent <span className="text-slate-400">Pricing.</span>
              </h2>
              <p className="text-lg text-slate-600 font-medium">
                Scale your AI applications without worrying about infrastructure costs.
              </p>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-8 max-w-5xl mx-auto">
              {/* Developer */}
              <div className="bg-white rounded-3xl p-8 border border-slate-200 shadow-sm flex flex-col hover:shadow-xl transition-shadow duration-300">
                <h3 className="text-xl font-bold text-slate-900 mb-2">Developer</h3>
                <p className="text-slate-500 text-sm font-medium mb-6">For hobbyists and prototypes.</p>
                <div className="mb-6"><span className="text-4xl font-extrabold text-slate-900">$0</span><span className="text-slate-500 font-medium">/mo</span></div>
                <ul className="space-y-3 mb-8 flex-1">
                  <li className="flex items-center text-sm font-medium text-slate-700">✓ 1,000 queries / month</li>
                  <li className="flex items-center text-sm font-medium text-slate-700">✓ 50 MB document storage</li>
                  <li className="flex items-center text-sm font-medium text-slate-700">✓ Community support</li>
                </ul>
                <Button variant="outline" className="w-full rounded-full border-slate-200 font-semibold py-6 hover:bg-slate-50">Get Started</Button>
              </div>
              {/* Pro */}
              <div className="bg-slate-900 rounded-3xl p-8 border border-slate-800 shadow-2xl flex flex-col relative overflow-hidden transform md:-translate-y-4 hover:-translate-y-6 transition-transform duration-300">
                <div className="absolute top-0 inset-x-0 h-1 bg-gradient-to-r from-emerald-400 to-cyan-400" />
                <h3 className="text-xl font-bold text-white mb-2">Production</h3>
                <p className="text-slate-400 text-sm font-medium mb-6">For scaling applications.</p>
                <div className="mb-6"><span className="text-4xl font-extrabold text-white">$49</span><span className="text-slate-400 font-medium">/mo</span></div>
                <ul className="space-y-3 mb-8 flex-1">
                  <li className="flex items-center text-sm font-medium text-slate-300">✓ 100,000 queries / month</li>
                  <li className="flex items-center text-sm font-medium text-slate-300">✓ 5 GB document storage</li>
                  <li className="flex items-center text-sm font-medium text-slate-300">✓ Priority email support</li>
                  <li className="flex items-center text-sm font-medium text-emerald-400">✓ Sub-50ms latency guarantee</li>
                </ul>
                <Link href={isAuthenticated ? "/dashboard" : "/signup"}>
                  <Button className="w-full rounded-full bg-white text-black hover:bg-slate-200 font-bold py-6">Start Free Trial</Button>
                </Link>
              </div>
              {/* Enterprise */}
              <div className="bg-white rounded-3xl p-8 border border-slate-200 shadow-sm flex flex-col hover:shadow-xl transition-shadow duration-300">
                <h3 className="text-xl font-bold text-slate-900 mb-2">Enterprise</h3>
                <p className="text-slate-500 text-sm font-medium mb-6">For custom deployments.</p>
                <div className="mb-6"><span className="text-4xl font-extrabold text-slate-900">Custom</span></div>
                <ul className="space-y-3 mb-8 flex-1">
                  <li className="flex items-center text-sm font-medium text-slate-700">✓ Unlimited queries</li>
                  <li className="flex items-center text-sm font-medium text-slate-700">✓ Dedicated hardware</li>
                  <li className="flex items-center text-sm font-medium text-slate-700">✓ VPC Peering & SSO</li>
                </ul>
                <Button variant="outline" className="w-full rounded-full border-slate-200 font-semibold py-6 hover:bg-slate-50">Contact Sales</Button>
              </div>
            </div>
          </div>
        </section>

        {/* Testimonials Section */}
        <section className="py-24 bg-white border-b border-slate-200/50">
          <div className="container mx-auto px-6">
            <div className="text-center mb-16 max-w-3xl mx-auto">
              <h2 className="text-3xl md:text-5xl font-extrabold tracking-tight mb-6 text-slate-900">
                Loved by <span className="text-slate-400">Builders.</span>
              </h2>
              <p className="text-lg text-slate-600 font-medium">
                Teams across the world trust RAGify to power their AI applications.
              </p>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-8 max-w-6xl mx-auto">
              {[
                { quote: "RAGify cut our RAG pipeline setup from 3 weeks to a single afternoon. The retrieval accuracy is phenomenal.", name: "Priya Sharma", role: "ML Lead, FinStack AI", avatar: "PS" },
                { quote: "We migrated from a custom Pinecone + LangChain stack to RAGify and haven't looked back. Latency dropped 60%.", name: "Marcus Chen", role: "CTO, NovaBridge", avatar: "MC" },
                { quote: "The model-agnostic approach is a game changer. We hot-swap between GPT-4 and Llama without changing a line of code.", name: "Sarah Kim", role: "Founding Engineer, Cortex Labs", avatar: "SK" },
              ].map((testimonial, i) => (
                <div key={i} className="bg-slate-50/50 rounded-2xl p-8 border border-slate-100 hover:bg-white hover:border-slate-200 hover:shadow-lg transition-all duration-300 flex flex-col">
                  <div className="flex-1">
                    <div className="flex gap-1 mb-4">
                      {[...Array(5)].map((_, j) => (
                        <Sparkles key={j} className="h-4 w-4 text-amber-400 fill-amber-400" />
                      ))}
                    </div>
                    <p className="text-slate-700 text-sm leading-relaxed font-medium italic">"{testimonial.quote}"</p>
                  </div>
                  <div className="flex items-center gap-3 mt-6 pt-6 border-t border-slate-100">
                    <div className="w-10 h-10 rounded-full bg-slate-900 text-white flex items-center justify-center text-xs font-bold">{testimonial.avatar}</div>
                    <div>
                      <p className="text-sm font-bold text-slate-900">{testimonial.name}</p>
                      <p className="text-xs text-slate-500 font-medium">{testimonial.role}</p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* Beautiful Bottom CTA */}
        <section className="py-24">
          <div className="container mx-auto px-6">
            <div className="rounded-[40px] bg-slate-900 text-white p-12 md:p-20 text-center relative overflow-hidden shadow-2xl">
              <div className="absolute top-0 inset-x-0 h-full bg-[radial-gradient(ellipse_at_top,#334155_0%,transparent_80%)] opacity-50" />
              
              <h2 className="text-3xl md:text-5xl font-extrabold tracking-tight mb-6 relative z-10">
                Ready to build something incredible?
              </h2>
              <p className="text-slate-300 text-lg md:text-xl max-w-2xl mx-auto mb-10 relative z-10 font-medium">
                Join top developers building the next generation of intelligent applications with RAGify.
              </p>
              <Link href={isAuthenticated ? "/dashboard" : "/signup"} className="relative z-10 inline-block">
                <Button size="lg" className="h-14 px-10 rounded-full bg-white text-black hover:bg-slate-200 text-base font-bold shadow-lg hover:shadow-xl hover:-translate-y-1 transition-all duration-300 group">
                  {isAuthenticated ? "Go to Dashboard" : "Start Building Free"}
                  <ArrowRight className="ml-2 h-4 w-4 group-hover:translate-x-1 transition-transform" />
                </Button>
              </Link>
            </div>
          </div>
        </section>

        {/* FAQ Section */}
        <section id="faq" className="py-24 bg-slate-50/50 border-t border-slate-200/50">
          <div className="container mx-auto px-6">
            <div className="text-center mb-16 max-w-3xl mx-auto">
              <h2 className="text-3xl md:text-5xl font-extrabold tracking-tight mb-6 text-slate-900">
                Frequently Asked <span className="text-slate-400">Questions.</span>
              </h2>
              <p className="text-lg text-slate-600 font-medium">
                Everything you need to know about RAGify and how it works.
              </p>
            </div>
            <div className="max-w-3xl mx-auto space-y-4">
              {[
                { q: "What is RAG and why do I need it?", a: "Retrieval-Augmented Generation (RAG) enhances LLM responses by grounding them in your own data. Instead of relying solely on a model's training data, RAG retrieves relevant context from your documents in real-time, dramatically improving accuracy and reducing hallucinations." },
                { q: "How does RAGify handle my data security?", a: "Your data is encrypted at rest (AES-256) and in transit (TLS 1.3). We enforce strict tenant isolation — your documents are never shared or accessible across projects. API keys are SHA-256 hashed and never stored in plaintext. Enterprise plans support VPC peering and SSO." },
                { q: "Which LLM providers do you support?", a: "RAGify is model-agnostic. We support OpenAI (GPT-4, GPT-4o), Anthropic (Claude), Meta Llama, DeepSeek, Google Gemini, and any OpenAI-compatible API endpoint. You can switch models per-query without code changes." },
                { q: "What file formats can I ingest?", a: "We support PDF, DOCX, TXT, Markdown, HTML, CSV, JSON, and XLSX out of the box. Our ingestion pipeline automatically handles chunking, metadata extraction, and embedding generation. Custom parsers are available on Enterprise plans." },
                { q: "How is pricing calculated?", a: "Pricing is based on the number of queries per month and document storage. The free Developer tier includes 1,000 queries and 50MB of storage. Production plans start at $49/mo with 100,000 queries. Enterprise plans are fully custom." },
                { q: "Can I self-host RAGify?", a: "Yes! RAGify is available as a Docker-based self-hosted solution. You get the same API interface and SDK support, running entirely within your own infrastructure. Contact our team for self-hosted licensing." },
              ].map((faq, i) => (
                <div key={i} className="bg-white rounded-2xl border border-slate-200 overflow-hidden transition-shadow hover:shadow-md">
                  <button
                    onClick={() => setOpenFaq(openFaq === i ? null : i)}
                    className="w-full flex items-center justify-between px-8 py-5 text-left"
                  >
                    <span className="text-base font-bold text-slate-900 pr-4">{faq.q}</span>
                    <ChevronDown className={`h-5 w-5 text-slate-400 flex-shrink-0 transition-transform duration-200 ${openFaq === i ? 'rotate-180' : ''}`} />
                  </button>
                  {openFaq === i && (
                    <div className="px-8 pb-6">
                      <p className="text-sm text-slate-600 leading-relaxed font-medium">{faq.a}</p>
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        </section>

      </main>

      {/* Complete Footer */}
      <footer className="border-t border-slate-200 bg-white pt-16 pb-8">
        <div className="container mx-auto px-6">
          {/* Main Footer Grid */}
          <div className="grid grid-cols-2 md:grid-cols-6 gap-8 md:gap-12 mb-16">
            {/* Brand Column */}
            <div className="col-span-2">
              <div className="flex items-center gap-2 mb-4">
                <img src="/logo.svg" alt="RAGify Logo" className="h-6 w-auto" />
              </div>
              <p className="text-sm text-slate-500 leading-relaxed font-medium mb-6 max-w-xs">
                The platform for building and scaling next-generation RAG applications. Ship production-ready AI in minutes, not months.
              </p>
              {/* Social Links */}
              <div className="flex items-center gap-3">
                <a href="https://github.com" target="_blank" rel="noopener noreferrer" className="w-9 h-9 rounded-full bg-slate-100 hover:bg-slate-900 hover:text-white text-slate-500 flex items-center justify-center transition-all duration-200">
                  <Github className="h-4 w-4" />
                </a>
                <a href="https://twitter.com" target="_blank" rel="noopener noreferrer" className="w-9 h-9 rounded-full bg-slate-100 hover:bg-slate-900 hover:text-white text-slate-500 flex items-center justify-center transition-all duration-200">
                  <Twitter className="h-4 w-4" />
                </a>
                <a href="https://linkedin.com" target="_blank" rel="noopener noreferrer" className="w-9 h-9 rounded-full bg-slate-100 hover:bg-slate-900 hover:text-white text-slate-500 flex items-center justify-center transition-all duration-200">
                  <Linkedin className="h-4 w-4" />
                </a>
                <a href="mailto:hello@ragify.net" className="w-9 h-9 rounded-full bg-slate-100 hover:bg-slate-900 hover:text-white text-slate-500 flex items-center justify-center transition-all duration-200">
                  <Mail className="h-4 w-4" />
                </a>
              </div>
            </div>

            {/* Product */}
            <div>
              <h4 className="text-xs font-bold mb-5 text-slate-900 uppercase tracking-wider">Product</h4>
              <ul className="space-y-3">
                <li><Link href="#features" className="text-sm font-medium text-slate-500 hover:text-slate-900 transition-colors">Features</Link></li>
                <li><Link href="#use-cases" className="text-sm font-medium text-slate-500 hover:text-slate-900 transition-colors">Use Cases</Link></li>
                <li><Link href="#pricing" className="text-sm font-medium text-slate-500 hover:text-slate-900 transition-colors">Pricing</Link></li>
                <li><Link href="#how-it-works" className="text-sm font-medium text-slate-500 hover:text-slate-900 transition-colors">How It Works</Link></li>
                <li><span className="text-sm font-medium text-slate-400">Changelog</span></li>
              </ul>
            </div>

            {/* Developers */}
            <div>
              <h4 className="text-xs font-bold mb-5 text-slate-900 uppercase tracking-wider">Developers</h4>
              <ul className="space-y-3">
                <li><Link href="#developers" className="text-sm font-medium text-slate-500 hover:text-slate-900 transition-colors">Documentation</Link></li>
                <li><Link href="#developers" className="text-sm font-medium text-slate-500 hover:text-slate-900 transition-colors">API Reference</Link></li>
                <li><a href="https://pypi.org/project/ez-ragify/" target="_blank" rel="noopener noreferrer" className="text-sm font-medium text-slate-500 hover:text-slate-900 transition-colors">Python SDK</a></li>
                <li><span className="text-sm font-medium text-slate-400">TypeScript SDK (Coming Soon)</span></li>
                <li><Link href="#developers" className="text-sm font-medium text-slate-500 hover:text-slate-900 transition-colors">Quick Start Guide</Link></li>
              </ul>
            </div>

            {/* Company */}
            <div>
              <h4 className="text-xs font-bold mb-5 text-slate-900 uppercase tracking-wider">Company</h4>
              <ul className="space-y-3">
                <li><span className="text-sm font-medium text-slate-400">About Us</span></li>
                <li><span className="text-sm font-medium text-slate-400">Blog</span></li>
                <li><span className="text-sm font-medium text-slate-400">Careers</span></li>
                <li><span className="text-sm font-medium text-slate-400">Contact</span></li>
                <li><span className="text-sm font-medium text-slate-400">Partners</span></li>
              </ul>
            </div>

            {/* Legal */}
            <div>
              <h4 className="text-xs font-bold mb-5 text-slate-900 uppercase tracking-wider">Legal</h4>
              <ul className="space-y-3">
                <li><Link href="/privacy" className="text-sm font-medium text-slate-500 hover:text-slate-900 transition-colors">Privacy Policy</Link></li>
                <li><Link href="/terms" className="text-sm font-medium text-slate-500 hover:text-slate-900 transition-colors">Terms of Service</Link></li>
                <li><Link href="/cookies" className="text-sm font-medium text-slate-500 hover:text-slate-900 transition-colors">Cookie Policy</Link></li>
                <li><span className="text-sm font-medium text-slate-400">Security</span></li>
                <li><span className="text-sm font-medium text-slate-400">DPA</span></li>
              </ul>
            </div>
          </div>

          {/* Newsletter */}
          <div className="rounded-2xl bg-slate-50 border border-slate-200 p-8 md:p-10 mb-12 flex flex-col md:flex-row items-center justify-between gap-6">
            <div>
              <h4 className="text-lg font-bold text-slate-900 mb-1">Stay up to date</h4>
              <p className="text-sm text-slate-500 font-medium">Get the latest updates on features, best practices, and AI engineering tips.</p>
            </div>
            <div className="flex items-center gap-3 w-full md:w-auto">
              <input
                type="email"
                placeholder="you@company.com"
                className="h-11 px-4 rounded-full border border-slate-200 bg-white text-sm text-slate-900 placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-slate-900 focus:border-transparent w-full md:w-64 font-medium"
              />
              <Button className="h-11 px-6 rounded-full bg-black text-white hover:bg-slate-800 text-sm font-semibold shrink-0 shadow-md">
                Subscribe
              </Button>
            </div>
          </div>

          {/* Bottom Bar */}
          <div className="border-t border-slate-200 pt-8 flex flex-col md:flex-row justify-between items-center gap-4">
            <span className="text-sm text-slate-500 font-medium">&copy; {new Date().getFullYear()} RAGify Systems, Inc. All rights reserved.</span>
            <div className="flex items-center gap-6">
              <span className="flex items-center gap-1.5 text-xs text-slate-400 font-medium">
                <span className="flex h-2 w-2 rounded-full bg-emerald-500 shadow-[0_0_6px_rgba(16,185,129,0.4)]"></span>
                All systems operational
              </span>
              <span className="text-sm text-slate-400 font-medium">v2.0.4.stable</span>
            </div>
          </div>
        </div>
      </footer>
    </div>
  )
}
