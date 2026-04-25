import Link from "next/link"
import { Zap } from "lucide-react"

export const metadata = {
    title: "Terms of Service - RAGify",
    description: "RAGify Terms of Service. Read about the terms governing your use of our platform.",
}

export default function TermsPage() {
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
                <h1 className="text-3xl font-bold mb-2" style={{ fontFamily: 'var(--font-serif), Georgia, serif' }}>Terms of Service</h1>
                <p className="text-sm text-muted-foreground mb-8">Last updated: February 17, 2026</p>

                <div className="prose prose-sm max-w-none text-foreground/90 space-y-6">
                    <section>
                        <h2 className="text-lg font-semibold mb-2">1. Acceptance of Terms</h2>
                        <p className="text-sm leading-relaxed text-muted-foreground">
                            By accessing or using the RAGify platform, APIs, and related services (the &ldquo;Service&rdquo;), you agree to be bound by these Terms of Service (&ldquo;Terms&rdquo;). If you do not agree, do not use the Service. If you are using the Service on behalf of an organization, you represent that you have authority to bind that organization.
                        </p>
                    </section>

                    <section>
                        <h2 className="text-lg font-semibold mb-2">2. Description of Service</h2>
                        <p className="text-sm leading-relaxed text-muted-foreground">
                            RAGify provides a managed Retrieval-Augmented Generation (RAG) platform that allows users to upload documents, generate vector embeddings, and query those documents via REST APIs. The Service includes document processing, vector storage, API key management, and query endpoints.
                        </p>
                    </section>

                    <section>
                        <h2 className="text-lg font-semibold mb-2">3. Account Registration</h2>
                        <p className="text-sm leading-relaxed text-muted-foreground">
                            You must create an account to use the Service. You are responsible for maintaining the confidentiality of your account credentials and for all activities under your account. You must provide accurate and complete information and promptly update it if it changes. You must notify us immediately of any unauthorized use of your account.
                        </p>
                    </section>

                    <section>
                        <h2 className="text-lg font-semibold mb-2">4. Acceptable Use</h2>
                        <p className="text-sm leading-relaxed text-muted-foreground">You agree not to:</p>
                        <ul className="list-disc list-inside text-sm text-muted-foreground space-y-1 mt-2">
                            <li>Use the Service for any unlawful purpose or in violation of any applicable laws</li>
                            <li>Upload content that infringes intellectual property rights of third parties</li>
                            <li>Upload malicious, harmful, or deceptive content</li>
                            <li>Attempt to gain unauthorized access to the Service or its infrastructure</li>
                            <li>Reverse engineer, decompile, or disassemble any part of the Service</li>
                            <li>Use the Service to build a competing product</li>
                            <li>Exceed your plan&rsquo;s rate limits or abuse the API</li>
                            <li>Share API keys or account access with unauthorized parties</li>
                        </ul>
                    </section>

                    <section>
                        <h2 className="text-lg font-semibold mb-2">5. Your Content</h2>
                        <p className="text-sm leading-relaxed text-muted-foreground">
                            You retain ownership of all content you upload to the Service (&ldquo;Your Content&rdquo;). By uploading content, you grant RAGify a limited, non-exclusive license to process, store, embed, and serve Your Content solely for the purpose of providing the Service. We will not use Your Content for training AI models or share it with other users.
                        </p>
                    </section>

                    <section>
                        <h2 className="text-lg font-semibold mb-2">6. API Usage and Rate Limits</h2>
                        <p className="text-sm leading-relaxed text-muted-foreground">
                            API usage is subject to the rate limits and quotas of your subscription plan. We reserve the right to throttle or suspend access if usage significantly exceeds plan limits or threatens the stability of the Service. API keys are confidential and must not be exposed in client-side code or public repositories.
                        </p>
                    </section>

                    <section>
                        <h2 className="text-lg font-semibold mb-2">7. Payment and Billing</h2>
                        <p className="text-sm leading-relaxed text-muted-foreground">
                            Paid plans are billed in advance on a monthly or annual basis. All fees are non-refundable except where required by law. We may change pricing with 30 days&rsquo; notice. Failure to pay may result in suspension or termination of your account. You are responsible for all applicable taxes.
                        </p>
                    </section>

                    <section>
                        <h2 className="text-lg font-semibold mb-2">8. Service Availability</h2>
                        <p className="text-sm leading-relaxed text-muted-foreground">
                            We strive to maintain high availability but do not guarantee uninterrupted access. We may perform scheduled maintenance with advance notice. We are not liable for downtime caused by factors beyond our reasonable control, including internet outages, third-party service failures, or force majeure events.
                        </p>
                    </section>

                    <section>
                        <h2 className="text-lg font-semibold mb-2">9. Intellectual Property</h2>
                        <p className="text-sm leading-relaxed text-muted-foreground">
                            The Service, including its software, design, documentation, and branding, is owned by RAGify Inc. and protected by intellectual property laws. These Terms do not grant you any rights to our trademarks, logos, or brand features. Feedback you provide may be used by us without obligation.
                        </p>
                    </section>

                    <section>
                        <h2 className="text-lg font-semibold mb-2">10. Limitation of Liability</h2>
                        <p className="text-sm leading-relaxed text-muted-foreground">
                            TO THE MAXIMUM EXTENT PERMITTED BY LAW, RAGIFY SHALL NOT BE LIABLE FOR ANY INDIRECT, INCIDENTAL, SPECIAL, CONSEQUENTIAL, OR PUNITIVE DAMAGES, OR ANY LOSS OF PROFITS, DATA, OR BUSINESS OPPORTUNITIES. OUR TOTAL LIABILITY SHALL NOT EXCEED THE AMOUNT YOU PAID US IN THE 12 MONTHS PRECEDING THE CLAIM.
                        </p>
                    </section>

                    <section>
                        <h2 className="text-lg font-semibold mb-2">11. Disclaimer of Warranties</h2>
                        <p className="text-sm leading-relaxed text-muted-foreground">
                            THE SERVICE IS PROVIDED &ldquo;AS IS&rdquo; AND &ldquo;AS AVAILABLE&rdquo; WITHOUT WARRANTIES OF ANY KIND, WHETHER EXPRESS, IMPLIED, OR STATUTORY. WE DISCLAIM ALL WARRANTIES INCLUDING MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE, AND NON-INFRINGEMENT. AI-GENERATED RESPONSES MAY CONTAIN ERRORS AND SHOULD BE VERIFIED.
                        </p>
                    </section>

                    <section>
                        <h2 className="text-lg font-semibold mb-2">12. Termination</h2>
                        <p className="text-sm leading-relaxed text-muted-foreground">
                            Either party may terminate these Terms at any time. We may suspend or terminate your access if you violate these Terms. Upon termination, your right to use the Service ceases. We will make Your Content available for export for 30 days after termination, after which it may be deleted.
                        </p>
                    </section>

                    <section>
                        <h2 className="text-lg font-semibold mb-2">13. Governing Law</h2>
                        <p className="text-sm leading-relaxed text-muted-foreground">
                            These Terms are governed by the laws of the State of Delaware, United States, without regard to conflict of law principles. Any disputes shall be resolved in the courts located in Delaware.
                        </p>
                    </section>

                    <section>
                        <h2 className="text-lg font-semibold mb-2">14. Changes to Terms</h2>
                        <p className="text-sm leading-relaxed text-muted-foreground">
                            We may modify these Terms at any time. Material changes will be notified via email or in-app notice at least 30 days in advance. Continued use after changes constitutes acceptance. If you disagree with the changes, you must stop using the Service.
                        </p>
                    </section>

                    <section>
                        <h2 className="text-lg font-semibold mb-2">15. Contact</h2>
                        <p className="text-sm leading-relaxed text-muted-foreground">
                            For questions about these Terms, contact us at:<br />
                            Email: legal@ragify.com<br />
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
