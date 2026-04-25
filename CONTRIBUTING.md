# Contributing to RAGify

## Setup

```bash
cp .env.example .env          # fill in your secrets
pip install pre-commit && pre-commit install

# Backend
cd backend && python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt

# Frontend
cd frontend && npm install

# Start everything
bash scripts/start_dev.sh
```

## Running tests

```bash
cd backend && pytest tests/unit/ -m unit          # no DB needed
cd backend && pytest tests/integration/ -m integration   # needs DB + Redis
cd frontend && npm test
```

## Code standards

| Tool | What it checks |
|------|---------------|
| Ruff | Python lint + format |
| Mypy | Python types |
| Bandit | Python security |
| ESLint | TypeScript |
| GitLeaks | Secrets |

Pre-commit runs all of these on `git commit`. Manual run: `pre-commit run --all-files`

## Branch strategy

- `main` — protected, PRs only
- `develop` — integration branch
- `feat/<name>`, `fix/<name>`, `chore/<name>` — feature branches

## Migrations

```bash
cd backend
alembic revision --autogenerate -m "describe_your_change"
alembic upgrade head
```
