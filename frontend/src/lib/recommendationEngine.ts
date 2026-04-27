
export function getRecommendation(answers: any) {
    // Start with sensible defaults
    let config: any = {
        llm_model: "gpt-3.5-turbo",
        embedding_provider: "openai",
        embedding_model: "text-embedding-3-small",
        temperature: 0.3,
        chunk_size: 1000,
        chunk_overlap: 200,
        top_k: 4,
        is_public: false,
        project_type: "byor",
    }

    // ── 1. Goal → project type & top_k ──
    switch (answers.goal) {
        case "chatbot":
            config.project_type = "chatbot"
            config.top_k = 5
            break
        case "search":
            config.project_type = "search"
            config.top_k = 10
            break
        case "assistant":
            config.project_type = "assistant"
            config.top_k = 6
            break
        case "api":
            config.project_type = "api"
            config.top_k = 4
            break
    }

    // ── 2. Document types → chunking strategy (handles multi-select array) ──
    const docs: string[] = Array.isArray(answers.documents)
        ? answers.documents
        : [answers.documents || "pdf"]

    if (docs.length > 1 || docs.includes("mixed")) {
        // Multiple types → larger overlap for better cross-chunk context
        config.chunk_size = 1000
        config.chunk_overlap = 250
    } else if (docs.includes("code")) {
        config.chunk_size = 500
        config.chunk_overlap = 100
    } else if (docs.includes("text")) {
        config.chunk_size = 800
        config.chunk_overlap = 150
    } else {
        config.chunk_size = 1000
        config.chunk_overlap = 200
    }

    // ── 3. Volume → embedding quality ──
    if (answers.volume === "large") {
        config.embedding_model = "text-embedding-3-large"
    }

    // ── 4. Accuracy vs Speed → base model selection ──
    switch (answers.accuracy) {
        case "speed":
            config.llm_model = "groq-llama-3.1-8b"
            break
        case "balanced":
            config.llm_model = "gpt-4o-mini"
            break
        case "accuracy":
            config.llm_model = "gpt-4-turbo"
            config.top_k = Math.min(config.top_k + 2, 10)
            break
    }

    // ── 5. Audience → public flag ──
    if (answers.audience === "public") {
        config.is_public = true
    }

    // ── 6. Data sensitivity → deployment & model upgrade ──
    switch (answers.sensitivity) {
        case "public":
            config.deployment_environment = "dev"
            break
        case "internal":
            config.deployment_environment = "staging"
            break
        case "confidential":
            config.deployment_environment = "production"
            if (config.llm_model === "groq-llama-3.1-8b" || config.llm_model === "groq-mixtral-8x7b") {
                config.llm_model = "gpt-4o-mini"
            }
            break
    }

    // ── 7. Creativity → temperature ──
    switch (answers.creativity) {
        case "strict":
            config.temperature = 0.0
            break
        case "moderate":
            config.temperature = 0.3
            break
        case "creative":
            config.temperature = 0.7
            if (config.llm_model === "groq-llama-3.1-8b") {
                config.llm_model = "gpt-4o-mini"
            }
            break
    }

    // ── 8. Budget → final model override ──
    switch (answers.budget) {
        case "free":
            if (config.llm_model === "gpt-4-turbo" || config.llm_model === "gpt-4o-mini") {
                config.llm_model = "groq-mixtral-8x7b"
            }
            config.embedding_provider = "openai"
            config.embedding_model = "text-embedding-3-small"
            break
        case "moderate":
            if (config.llm_model === "gpt-4-turbo") {
                config.llm_model = "gpt-4o-mini"
            }
            break
        case "premium":
            config.llm_model = "gpt-4-turbo"
            config.embedding_model = "text-embedding-3-large"
            break
    }

    // ── Optional: Gemini embeddings (storage-optimized) ──
    // If you have a lot of documents, Gemini embeddings are smaller (768-dim) and cheaper to store.
    if (answers.volume === "large" && answers.budget !== "premium") {
        config.embedding_provider = "gemini"
        config.embedding_model = "gemini-embedding-2-preview"
    }

    // ── 9. Language-aware model adjustment ──
    // Only override to Sarvam if language is PURELY Indian (not multilingual)
    if (answers.language === "indian") {
        // Pure Indian language → Sarvam is the best choice
        if (answers.budget !== "premium") {
            config.llm_model = "sarvam-m"
            config._model_reason = "Sarvam-M is purpose-built for Indian languages like Hindi, Tamil, Telugu"
        }
    } else if (answers.language === "multilingual") {
        // Multilingual (mixed) → GPT-4o Mini handles many languages well
        // Only suggest it if currently on a weaker model
        if (config.llm_model === "gpt-3.5-turbo" || config.llm_model === "groq-llama-3.1-8b") {
            config.llm_model = "gpt-4o-mini"
        }
        config._model_reason = "GPT-4o Mini recommended for strong multilingual support across many languages"
    }

    // ── Build human-readable recommendation reason ──
    const MODEL_REASONS: Record<string, string> = {
        "gpt-3.5-turbo": "Fast and affordable for general English use",
        "gpt-4o-mini": "Best balance of quality, speed, and cost",
        "gpt-4-turbo": "Most capable — best for complex reasoning and accuracy",
        "sarvam-m": "Purpose-built for Indian languages (Hindi, Tamil, Telugu, etc.)",
        "groq-llama-3.1-8b": "Blazing fast free inference via Groq",
        "groq-mixtral-8x7b": "Free 32K context — great for large document RAG on a budget",
        "gemini-2.5-flash": "Fast Gemini model — good for low-latency reasoning",
        "gemini-2.5-pro": "Most capable Gemini model — best for complex reasoning",
    }
    if (!config._model_reason) {
        config._model_reason = MODEL_REASONS[config.llm_model] || ""
    }

    return config
}
