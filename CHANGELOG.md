# Changelog

## [Unreleased]

### Added
- Industry-standard repo structure: `scripts/`, `docs/`, `infrastructure/`, `.github/`
- GitHub Actions CI for backend (ruff + mypy + pytest) and frontend (eslint + tsc + build)
- Security scan workflow: Bandit, pip-audit, GitLeaks
- pytest test scaffold: conftest.py, unit tests, integration tests
- `pyproject.toml` with ruff, mypy, pytest, bandit config
- `.pre-commit-config.yaml`
- `CONTRIBUTING.md`, `CHANGELOG.md`, PR template

### Changed
- `start_app.sh` → `scripts/start_dev.sh`: fixed `xargs` secret leak
- `docker-compose.yml` → `infrastructure/docker/docker-compose.yml`
- `deploy/nginx/` → `infrastructure/nginx/`
- `create_admin.py`, `migrate_supabase_to_docker.py` → `scripts/`
- `ARCHITECTURE_REPORT.md` → `docs/architecture.md`
- `SECURITY_REPORT.md` → `docs/security.md`
- `GOOGLE_SETUP.md` → `docs/google-oauth-setup.md`
- README rewritten

### Removed
- `backend/app/rag/ingestion.py` — dead code, replaced by `indexing.py`

## [0.1.0] — 2026-03-07

### Added
- Initial RAGify platform: hybrid search, multi-tenant RAG, streaming NDJSON, dual auth
