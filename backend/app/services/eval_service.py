from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass

from app.core.config import settings
from app.services.telemetry_models import RAGRunArtifacts

logger = logging.getLogger(__name__)

_eval_semaphore = asyncio.Semaphore(3)  # max 3 concurrent eval jobs


@dataclass
class EvalPayload:
    trace_id: str
    query: str
    response: str
    contexts: list[str]
    project_id: int
    query_tier: str = "balanced"


async def run_ragas_eval(payload: EvalPayload, supabase, langfuse) -> None:
    """Runs RAGAS metrics async in the background.

    Never call this in the request path — schedule with BackgroundTasks.
    Uses Gemini 2.5 Flash as the eval LLM.
    """

    if not payload or not payload.trace_id:
        return

    # If either integration is missing, we can still compute, but most users want at least one sink.
    if not supabase and not langfuse:
        return

    # Lazy import so the API still boots even if deps aren't installed in dev.
    try:
        from ragas import evaluate
        from ragas.metrics import Faithfulness, ResponseRelevancy, LLMContextPrecisionWithoutReference
        from ragas.llms import BaseRagasLLM
        from datasets import Dataset
    except Exception as e:
        logger.error(f"[Eval] Missing RAGAS deps: {e}")
        return

    if not settings.GEMINI_API_KEY:
        logger.warning("[Eval] GEMINI_API_KEY not set — skipping RAGAS eval")
        return

    class GeminiRagasLLM(BaseRagasLLM):
        def __init__(self):
            import google.genai as genai

            self._client = genai.Client(api_key=settings.GEMINI_API_KEY)

        def generate_text(self, prompt: str) -> str:
            # RAGAS may call the sync variant internally.
            response = self._client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt,
            )
            return getattr(response, "text", "") or ""

        async def agenerate_text(self, prompt: str) -> str:
            # Keep eval fully async from the server POV.
            return await asyncio.to_thread(self.generate_text, prompt)

    async with _eval_semaphore:
        try:
            eval_llm = GeminiRagasLLM()

            metrics = [
                Faithfulness(llm=eval_llm),
                ResponseRelevancy(llm=eval_llm),
                LLMContextPrecisionWithoutReference(llm=eval_llm),
            ]

            ds = Dataset.from_dict(
                {
                    "user_input": [payload.query],
                    "response": [payload.response],
                    "retrieved_contexts": [payload.contexts],
                }
            )

            result = evaluate(dataset=ds, metrics=metrics)
            row = result.to_pandas().iloc[0]

            scores = {
                "faithfulness": float(row.get("faithfulness", 0) or 0),
                "answer_relevancy": float(row.get("answer_relevancy", 0) or 0),
                "context_precision": float(
                    row.get("llm_context_precision_without_reference", 0) or 0
                ),
            }

            # Push to Langfuse (attaches to the original trace)
            if langfuse:
                for name, value in scores.items():
                    try:
                        langfuse.create_score(name=name, value=value, trace_id=payload.trace_id)
                    except Exception:
                        # Keep background tasks resilient.
                        pass

            # Push to Supabase for dashboard queries
            if supabase:
                supabase.table("eval_results").insert(
                    {
                        "project_id": payload.project_id,
                        "trace_id": payload.trace_id,
                        "query_text": (payload.query or "")[:500],
                        "faithfulness": scores["faithfulness"],
                        "answer_relevancy": scores["answer_relevancy"],
                        "context_precision": scores["context_precision"],
                        "query_tier": payload.query_tier,
                    }
                ).execute()

            logger.info(f"[Eval] RAGAS eval done for {payload.trace_id}: {scores}")

        except Exception as e:
            logger.error(f"[Eval] RAGAS eval failed for {payload.trace_id}: {e}", exc_info=True)
            # Never raise — background task failure must never surface to users


async def run_ragas_eval_from_artifacts(artifacts: RAGRunArtifacts, supabase, langfuse) -> None:
    """Background-task wrapper: converts RAGRunArtifacts -> EvalPayload and runs eval."""
    if not artifacts or not artifacts.trace_id:
        return

    # If the request failed or was blocked, don't run eval.
    if not (artifacts.response or "").strip():
        return
    if not artifacts.contexts:
        return

    payload = EvalPayload(
        trace_id=artifacts.trace_id,
        query=artifacts.query,
        response=artifacts.response,
        contexts=artifacts.contexts,
        project_id=artifacts.project_id,
        query_tier=artifacts.query_tier,
    )
    await run_ragas_eval(payload, supabase=supabase, langfuse=langfuse)
