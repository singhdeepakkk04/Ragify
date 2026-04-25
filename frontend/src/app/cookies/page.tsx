import Link from "next/link"
import { Zap } from "lucide-react"

export const metadata = {
    title: "Cookie Policy - RAGify",
    description: "RAGify Cookie Policy. Learn about how we use cookies and similar technologies.",
}

export default function CookiesPage() {
    return (
        <div className="min-h-screen bg-background">
            <header className="border-b border-border/40 bg-background/95 backdrop-blur">
                <div className="container mx-auto flex h-14 items-center px-6">
                    <Link href="/" className="flex items-center gap-2">
                        <div className="flex h-7 w-7 items-center justify-center rounded-md bg-primary text-primary-foreground">
                            <Zap className="h-4 w-4" />
                        </div>
                        <span className="text-lg font-semibold tracking-tight" style={{ fontFamily: 'var(--font-serif), Georgia, serif' }}>RAGify</span>
                    </Link>
                </div>
            </header>

            <main className="container mx-auto px-6 py-12 max-w-3xl">
                <h1 className="text-3xl font-bold mb-2" style={{ fontFamily: 'var(--font-serif), Georgia, serif' }}>Cookie Policy</h1>
                <p className="text-sm text-muted-foreground mb-8">Last updated: February 17, 2026</p>

                <div className="prose prose-sm max-w-none text-foreground/90 space-y-6">
                    <section>
                        <h2 className="text-lg font-semibold mb-2">1. What Are Cookies</h2>
                        <p className="text-sm leading-relaxed text-muted-foreground">
                            Cookies are small text files placed on your device when you visit a website. They are widely used to make websites work efficiently, provide analytics, and remember your preferences. Similar technologies include local storage, session storage, and web beacons.
                        </p>
                    </section>

                    <section>
                        <h2 className="text-lg font-semibold mb-2">2. How We Use Cookies</h2>
                        <p className="text-sm leading-relaxed text-muted-foreground">RAGify uses the following types of cookies:</p>

                        <h3 className="text-sm font-semibold mt-4 mb-1">2.1 Essential Cookies</h3>
                        <p className="text-sm leading-relaxed text-muted-foreground">
                            These cookies are strictly necessary for the Service to function. They include authentication tokens (managed via Supabase Auth), session identifiers, and CSRF protection tokens. Without these, you cannot use the Service.
                        </p>
                        <div className="overflow-x-auto mt-2">
                            <table className="w-full text-xs border-collapse">
                                <thead>
                                    <tr className="border-b">
                                        <th className="text-left py-2 pr-4 font-semibold text-foreground">Cookie</th>
                                        <th className="text-left py-2 pr-4 font-semibold text-foreground">Purpose</th>
                                        <th className="text-left py-2 font-semibold text-foreground">Duration</th>
                                    </tr>
                                </thead>
                                <tbody className="text-muted-foreground">
                                    <tr className="border-b border-border/40">
                                        <td className="py-2 pr-4 font-mono">sb-access-token</td>
                                        <td className="py-2 pr-4">Authentication session</td>
                                        <td className="py-2">1 hour</td>
                                    </tr>
                                    <tr className="border-b border-border/40">
                                        <td className="py-2 pr-4 font-mono">sb-refresh-token</td>
                                        <td className="py-2 pr-4">Session renewal</td>
                                        <td className="py-2">7 days</td>
                                    </tr>
                                    <tr className="border-b border-border/40">
                                        <td className="py-2 pr-4 font-mono">sb-auth-token</td>
                                        <td className="py-2 pr-4">Auth state persistence</td>
                                        <td className="py-2">Session</td>
                                    </tr>
                                </tbody>
                            </table>
                        </div>

                        <h3 className="text-sm font-semibold mt-4 mb-1">2.2 Analytics Cookies</h3>
                        <p className="text-sm leading-relaxed text-muted-foreground">
                            We may use analytics cookies to understand how visitors interact with the Service. These help us improve performance and user experience. Analytics data is aggregated and does not identify individual users.
                        </p>

                        <h3 className="text-sm font-semibold mt-4 mb-1">2.3 Preference Cookies</h3>
                        <p className="text-sm leading-relaxed text-muted-foreground">
                            These store your settings and preferences, such as theme selection (light/dark mode), language preferences, and dashboard layout configurations.
                        </p>
                    </section>

                    <section>
                        <h2 className="text-lg font-semibold mb-2">3. Third-Party Cookies</h2>
                        <p className="text-sm leading-relaxed text-muted-foreground">
                            Some cookies may be set by third-party services we use:
                        </p>
                        <ul className="list-disc list-inside text-sm text-muted-foreground space-y-1 mt-2">
                            <li><strong>Supabase:</strong> Authentication and session management</li>
                            <li><strong>Google (OAuth):</strong> If you sign in with Google, Google may set cookies related to the authentication flow</li>
                            <li><strong>Analytics providers:</strong> If enabled, for usage analytics</li>
                        </ul>
                        <p className="text-sm leading-relaxed text-muted-foreground mt-2">
                            We do not use advertising cookies or trackers.
                        </p>
                    </section>

                    <section>
                        <h2 className="text-lg font-semibold mb-2">4. Local Storage</h2>
                        <p className="text-sm leading-relaxed text-muted-foreground">
                            In addition to cookies, we use browser local storage to persist authentication state and user preferences. This data remains on your device and is not transmitted to our servers except as part of authenticated API requests.
                        </p>
                    </section>

                    <section>
                        <h2 className="text-lg font-semibold mb-2">5. Managing Cookies</h2>
                        <p className="text-sm leading-relaxed text-muted-foreground">
                            You can control cookies through your browser settings. Most browsers allow you to block or delete cookies. Please note that disabling essential cookies will prevent you from using the Service. Instructions for managing cookies in common browsers:
                        </p>
                        <ul className="list-disc list-inside text-sm text-muted-foreground space-y-1 mt-2">
                            <li>Chrome: Settings &rarr; Privacy and Security &rarr; Cookies</li>
                            <li>Firefox: Settings &rarr; Privacy &amp; Security &rarr; Cookies</li>
                            <li>Safari: Preferences &rarr; Privacy &rarr; Manage Website Data</li>
                            <li>Edge: Settings &rarr; Cookies and Site Permissions</li>
                        </ul>
                    </section>

                    <section>
                        <h2 className="text-lg font-semibold mb-2">6. Updates to This Policy</h2>
                        <p className="text-sm leading-relaxed text-muted-foreground">
                            We may update this Cookie Policy to reflect changes in technology, legislation, or our practices. Changes will be posted on this page with an updated &ldquo;Last updated&rdquo; date.
                        </p>
                    </section>

                    <section>
                        <h2 className="text-lg font-semibold mb-2">7. Contact</h2>
                        <p className="text-sm leading-relaxed text-muted-foreground">
                            If you have questions about our use of cookies, please contact us at:<br />
                            Email: privacy@ragify.com<br />
                            RAGify Inc.
                        </p>
                    </section>
                </div>
            </main>

            <footer className="border-t py-6">
                <div className="container mx-auto px-6 text-center text-xs text-muted-foreground">
                    &copy; 2024 RAGify Inc. All rights reserved. &middot;{' '}
                    <Link href="/privacy" className="hover:text-foreground transition-colors">Privacy</Link> &middot;{' '}
                    <Link href="/terms" className="hover:text-foreground transition-colors">Terms</Link> &middot;{' '}
                    <Link href="/cookies" className="hover:text-foreground transition-colors">Cookies</Link>
                </div>
            </footer>
        </div>
    )
}
