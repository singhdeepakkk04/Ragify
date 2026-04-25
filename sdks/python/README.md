# ez-ragify Python SDK

Official Python SDK for the **RAGify** RAG-as-a-Service API. Build retrieval-augmented generation pipelines with a single function call.

## Installation

```bash
pip install ez-ragify
```

Or install from source:

```bash
cd sdks/python
pip install -e ".[dev]"
```

## Quick Start

### API Key Authentication (project-scoped)

```python
from ez_ragify import EzRagify

client = EzRagify(api_key="rag_abc123...")

# Ask a question against your project
response = client.query("What is the refund policy?", project_id=1)
print(response.answer)

for citation in response.citations:
    print(f"  - {citation.filename} p.{citation.page_number}: {citation.snippet}")
```

### Bearer Token Authentication (user-scoped)

```python
client = EzRagify(bearer_token="eyJhbGci...")

# Manage projects
projects = client.list_projects()
```

## Streaming

Stream tokens in real-time for a responsive UX:

```python
client = EzRagify(api_key="rag_abc123...")

for chunk in client.query_stream("Summarize the document", project_id=1):
    if chunk.type == "chunk":
        print(chunk.content, end="", flush=True)
    elif chunk.type == "citations":
        print("\n\nSources:")
        for c in chunk.citations:
            print(f"  - {c.filename}: {c.snippet[:80]}")
```

## Async Support

```python
import asyncio
from ez_ragify import AsyncEzRagify

async def main():
    async with AsyncEzRagify(api_key="rag_abc123...") as client:
        response = await client.query("What are the tax deadlines?", project_id=1)
        print(response.answer)

        # Streaming
        async for chunk in client.query_stream("Summarize", project_id=1):
            if chunk.type == "chunk":
                print(chunk.content, end="")

asyncio.run(main())
```

## API Reference

### Client Initialization

```python
EzRagify(
    api_key="...",          # Project-scoped API key (X-API-Key header)
    bearer_token="...",     # User-scoped JWT (Authorization: Bearer header)
    base_url="http://...",  # Default: http://localhost:8000/api/v1
    timeout=30.0,           # Default request timeout in seconds
)
```

### RAG Queries

| Method | Description |
|--------|-------------|
| `client.query(query, project_id, top_k=4)` | Full response (collects stream) |
| `client.query_stream(query, project_id, top_k=4)` | Generator of `StreamChunk` |

### Projects

| Method | Description |
|--------|-------------|
| `client.create_project(ProjectCreate(...))` | Create project |
| `client.list_projects(skip=0, limit=100)` | List user's projects |
| `client.get_project(project_id)` | Get single project |
| `client.update_project(project_id, ProjectUpdate(...))` | Update config |
| `client.delete_project(project_id)` | Delete project |
| `client.list_models()` | Available LLM models |
| `client.get_api_key(project_id)` | Get API key prefix |
| `client.regenerate_api_key(project_id)` | Regenerate API key |

### Documents

| Method | Description |
|--------|-------------|
| `client.upload_document(project_id, file)` | Upload PDF/DOCX/TXT/MD |
| `client.list_documents(project_id)` | List project documents |
| `client.delete_document(document_id)` | Delete a document |

`file` can be a **file path string** or a **file-like object**:

```python
# From path
doc = client.upload_document(1, "/path/to/report.pdf")

# From file object
with open("report.pdf", "rb") as f:
    doc = client.upload_document(1, f, filename="report.pdf")
```

### Usage & Analytics

| Method | Description |
|--------|-------------|
| `client.get_usage()` | Aggregate usage stats |
| `client.get_project_logs(project_id, limit=50, offset=0)` | Per-project query logs |

### User Profile

| Method | Description |
|--------|-------------|
| `client.get_profile()` | Get current user profile |
| `client.update_profile(display_name="...")` | Update display name |
| `client.delete_account()` | Delete account and all data |

## Error Handling

```python
from ez_ragify import EzRagify, EzRagifyError, AuthenticationError, RateLimitError, NotFoundError

client = EzRagify(api_key="rag_...")

try:
    response = client.query("Hello", project_id=999)
except NotFoundError:
    print("Project not found")
except RateLimitError as e:
    print(f"Rate limited — retry after {e.retry_after}s")
except AuthenticationError:
    print("Invalid API key")
except EzRagifyError as e:
    print(f"API error {e.status_code}: {e.message}")
```

## Types

All response objects are Pydantic models with full type hints:

- `Project`, `ProjectCreate`, `ProjectUpdate`
- `Document`
- `QueryResponse`, `StreamChunk`, `Citation`
- `UsageStats`, `ProjectLog`, `ProjectLogs`
- `UserProfile`
- `Model`
- `APIKey`, `APIKeyWithPlaintext`

## License

MIT
