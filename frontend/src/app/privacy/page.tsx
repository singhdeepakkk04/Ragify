import Link from "next/link"
import { Zap } from "lucide-react"

export const metadata = {
    title: "Privacy Policy - RAGify",
    description: "RAGify Privacy Policy. Learn how we collect, use, and protect your data.",
}

export default function PrivacyPage() {
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
                <h1 className="text-3xl font-bold mb-2" style={{ fontFamily: 'var(--font-serif), Georgia, serif' }}>Privacy Policy</h1>
                <p className="text-sm text-muted-foreground mb-8">Last updated: February 17, 2026</p>

                <div className="prose prose-sm max-w-none text-foreground/90 space-y-6">
                    <section>
                        <h2 className="text-lg font-semibold mb-2">1. Introduction</h2>
                        <p className="text-sm leading-relaxed text-muted-foreground">
                            RAGify Inc. (&ldquo;RAGify&rdquo;, &ldquo;we&rdquo;, &ldquo;us&rdquo;, or &ldquo;our&rdquo;) is committed to protecting your privacy. This Privacy Policy explains how we collect, use, disclose, and safeguard your information when you use our platform, APIs, and services (collectively, the &ldquo;Service&rdquo;).
                        </p>
                    </section>

                    <section>
                        <h2 className="text-lg font-semibold mb-2">2. Information We Collect</h2>
                        <h3 className="text-sm font-semibold mt-3 mb-1">2.1 Account Information</h3>
                        <p className="text-sm leading-relaxed text-muted-foreground">
                            When you create an account, we collect your name, email address, and authentication credentials. If you sign in via a third-party provider (e.g., Google), we receive your name and email from that provider.
                        </p>
                        <h3 className="text-sm font-semibold mt-3 mb-1">2.2 Usage Data</h3>
                        <p className="text-sm leading-relaxed text-muted-foreground">
                            We automatically collect information about your interaction with the Service, including IP address, browser type, device information, pages visited, API call frequency, and timestamps.
                        </p>
                        <h3 className="text-sm font-semibold mt-3 mb-1">2.3 Uploaded Content</h3>
                        <p className="text-sm leading-relaxed text-muted-foreground">
                            When you upload documents for RAG processing, we store and process the content solely to provide the Service. Documents are chunked, embedded, and stored in isolated vector databases associated with your account.
                        </p>
                    </section>

                    <section>
                        <h2 className="text-lg font-semibold mb-2">3. How We Use Your Information</h2>
                        <ul className="list-disc list-inside text-sm text-muted-foreground space-y-1">
                            <li>To provide, maintain, and improve the Service</li>
                            <li>To authenticate your identity and manage your account</li>
                            <li>To process your documents and generate vector embeddings</li>
                            <li>To respond to your inquiries and provide customer support</li>
                            <li>To send you service-related notices and updates</li>
                            <li>To detect, prevent, and address technical issues and abuse</li>
                            <li>To comply with legal obligations</li>
                        </ul>
                    </section>

                    <section>
                        <h2 className="text-lg font-semibold mb-2">4. Data Sharing and Disclosure</h2>
                        <p className="text-sm leading-relaxed text-muted-foreground">
                            We do not sell your personal information. We may share your information with:
                        </p>
                        <ul className="list-disc list-inside text-sm text-muted-foreground space-y-1 mt-2">
                            <li><strong>Service Providers:</strong> Third-party vendors who assist in operating the Service (e.g., Supabase for authentication and database, cloud hosting)</li>
                            <li><strong>AI Model Providers:</strong> When processing queries, document content may be sent to third-party AI providers (e.g., OpenAI for embeddings and generation, Cohere for search reranking) as necessary to generate responses</li>
                            <li><strong>Observability:</strong> Query metadata (user ID, project ID, latency) may be sent to Langfuse for pipeline monitoring and performance analytics</li>
                            <li><strong>Legal Requirements:</strong> When required by law, regulation, or legal process</li>
                            <li><strong>Business Transfers:</strong> In connection with a merger, acquisition, or sale of assets</li>
                        </ul>
                    </section>

                    <section>
                        <h2 className="text-lg font-semibold mb-2">5. Data Security</h2>
                        <p className="text-sm leading-relaxed text-muted-foreground">
                            We implement industry-standard security measures including encryption in transit (TLS 1.3) and at rest (AES-256), row-level security for database isolation, and regular security audits. However, no method of electronic transmission or storage is 100% secure.
                        </p>
                    </section>

                    <section>
                        <h2 className="text-lg font-semibold mb-2">6. Data Retention</h2>
                        <p className="text-sm leading-relaxed text-muted-foreground">
                            We retain your account information for as long as your account is active. Uploaded documents and their embeddings are retained until you delete them or close your account. Usage logs are retained for up to 90 days. You may request deletion of your data at any time by contacting us.
                        </p>
                    </section>

                    <section>
                        <h2 className="text-lg font-semibold mb-2">7. Your Rights</h2>
                        <p className="text-sm leading-relaxed text-muted-foreground">
                            Depending on your jurisdiction, you may have the right to: access your personal data, correct inaccurate data, delete your data, restrict or object to processing, data portability, and withdraw consent. To exercise these rights, contact us at privacy@ragify.com.
                        </p>
                    </section>

                    <section>
                        <h2 className="text-lg font-semibold mb-2">8. International Transfers</h2>
                        <p className="text-sm leading-relaxed text-muted-foreground">
                            Your information may be transferred to and processed in countries other than your own. We ensure appropriate safeguards are in place, including Standard Contractual Clauses where applicable.
                        </p>
                    </section>

                    <section>
                        <h2 className="text-lg font-semibold mb-2">9. Children&rsquo;s Privacy</h2>
                        <p className="text-sm leading-relaxed text-muted-foreground">
                            The Service is not intended for individuals under the age of 16. We do not knowingly collect personal information from children. If we become aware that a child has provided us with personal information, we will take steps to delete it.
                        </p>
                    </section>

                    <section>
                        <h2 className="text-lg font-semibold mb-2">10. Changes to This Policy</h2>
                        <p className="text-sm leading-relaxed text-muted-foreground">
                            We may update this Privacy Policy from time to time. We will notify you of material changes by posting the updated policy and updating the &ldquo;Last updated&rdquo; date. Your continued use of the Service constitutes acceptance of the updated policy.
                        </p>
                    </section>

                    <section>
                        <h2 className="text-lg font-semibold mb-2">11. Contact Us</h2>
                        <p className="text-sm leading-relaxed text-muted-foreground">
                            If you have questions about this Privacy Policy, please contact us at:<br />
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
