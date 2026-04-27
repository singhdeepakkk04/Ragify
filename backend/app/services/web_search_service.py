import logging
import asyncio
from app.schemas.web_search import WebResult
from app.core.config import settings

logger = logging.getLogger(__name__)

async def search_web_for_context(query: str, max_results: int = 3) -> list[WebResult]:
    """
    Uses Gemini's google_search grounding tool to fetch relevant web content.
    Returns a list of WebResult(title, url, snippet, content) objects.
    """
    if not settings.GEMINI_API_KEY:
        logger.warning("[Web Search] GEMINI_API_KEY not set. Skipping web search.")
        return []

    try:
        import google.genai as genai
        from google.genai import types
    except Exception as e:
        logger.error(f"[Web Search] google-genai not available: {e}")
        return []

    client = genai.Client(api_key=settings.GEMINI_API_KEY)
    
    try:
        # Wrap the call with 3 second timeout
        response = await asyncio.wait_for(
            asyncio.to_thread(
                client.models.generate_content,
                model="gemini-2.5-flash",
                contents=f"Search for information relevant to answering: {query}\n"
                         f"Return the top {max_results} most relevant results with their key facts.",
                config=types.GenerateContentConfig(
                    tools=[types.Tool(google_search=types.GoogleSearch())],
                    max_output_tokens=800,
                )
            ),
            timeout=3.0
        )
    except asyncio.TimeoutError:
        logger.warning("[Web Search] Gemini call timed out after 3 seconds.")
        return []
    except Exception as e:
        logger.error(f"[Web Search] Gemini call failed: {e}")
        return []
    
    # Extract grounding metadata (URLs, titles) from response
    results = []
    if not response.candidates:
        return []
        
    candidate = response.candidates[0]
    
    try:
        chunks = candidate.grounding_metadata.grounding_chunks
        for chunk in chunks:
            web = getattr(chunk, "web", None)
            if web:
                results.append(WebResult(
                    title=getattr(web, "title", "Web Result"),
                    url=getattr(web, "uri", ""),
                    snippet=response.text[:500] if response.text else "",
                    source="web"
                ))
    except Exception as e:
        logger.warning(f"[Web Search] No grounding chunks: {e}")

    # Deduplicate by url
    seen_urls = set()
    unique_results = []
    for res in results:
        if res.url and res.url not in seen_urls:
            unique_results.append(res)
            seen_urls.add(res.url)
            
    return unique_results[:max_results]
