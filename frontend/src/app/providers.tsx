"use client"

import { QueryClient, QueryClientProvider } from "@tanstack/react-query"
import { Toaster } from "sonner"
import { useState } from "react"
import { ThemeProvider as NextThemesProvider } from "next-themes"
import { CookieConsent } from "@/components/cookie-consent"

export default function Providers({
    children,
}: {
    children: React.ReactNode
}) {
    const [queryClient] = useState(() => new QueryClient({
        defaultOptions: {
            queries: {
                staleTime: 2 * 60 * 1000,        // data stays fresh for 2 min
                gcTime: 10 * 60 * 1000,           // keep cache for 10 min (survive route changes)
                refetchOnWindowFocus: false,       // don't re-fetch just because user switched tabs
                refetchOnReconnect: true,          // do refresh if network was lost & restored
                retry: 1,                          // only 1 retry on failure (default 3 is slow)
            },
        },
    }))

    return (
        <NextThemesProvider
            attribute="class"
            defaultTheme="system"
            enableSystem
            disableTransitionOnChange
        >
            <QueryClientProvider client={queryClient}>
                {children}
                <Toaster richColors position="top-right" />
                <CookieConsent />
            </QueryClientProvider>
        </NextThemesProvider>
    )
}
