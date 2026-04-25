"use client"

import { create } from 'zustand'
import { createClient } from './supabase'
import type { User, Session } from '@supabase/supabase-js'

interface AuthState {
    user: User | null
    session: Session | null
    isAuthenticated: boolean
    isLoading: boolean
    _initialized: boolean
    initialize: () => Promise<void>
    logout: () => Promise<void>
}

export const useAuthStore = create<AuthState>((set, get) => ({
    user: null,
    session: null,
    isAuthenticated: false,
    isLoading: true,
    _initialized: false,

    initialize: async () => {
        if (get()._initialized) return
        set({ _initialized: true })

        // Lazily create the Supabase client — never at module level
        // (module-level createClient breaks Google OAuth cookie session in Next.js)
        const supabase = createClient()

        try {
            // 1. Set up auth state change listener FIRST
            //    onAuthStateChange fires reliably after OAuth redirects — more 
            //    trustworthy than getSession() alone right after a callback redirect
            supabase.auth.onAuthStateChange((_event, session) => {
                set({
                    user: session?.user ?? null,
                    session,
                    isAuthenticated: !!session,
                    isLoading: false,
                })
            })

            // 2. Also call getSession for the initial load (handles page refreshes)
            const { data: { session } } = await supabase.auth.getSession()
            set({
                user: session?.user ?? null,
                session,
                isAuthenticated: !!session,
                isLoading: false,
            })
        } catch (error) {
            console.error("Auth initialization failed:", error)
            set({ isLoading: false })
        }
    },

    logout: async () => {
        const supabase = createClient()
        await supabase.auth.signOut()
        set({ user: null, session: null, isAuthenticated: false, isLoading: false })
        window.location.href = '/login'
    },
}))

