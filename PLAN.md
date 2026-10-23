# Product development plan

Each round completes one feature or repair. Future items are planned, not implemented claims.

## Current round

project-skeleton

## Roadmap

### project-skeleton — Project Skeleton with FastAPI/React Foundation

Status: done

Acceptance:
- Backend FastAPI app with health endpoint
- Frontend React+TypeScript+Vite app with build script
- Dockerfiles for both services
- docker-compose with Keycloak and persistent volumes
- Basic CI workflow
- Portfolio.json, README, LICENSE, CHANGELOG, pyproject.toml, .gitignore, .env.example

Implementation: `backend/app/main.py`, `backend/app/core/config.py`, `backend/app/core/database.py`, `backend/app/api/health.py`, `backend/Dockerfile`, `backend/requirements.txt`, `frontend/src/main.tsx`, `frontend/src/App.tsx`, `frontend/src/App.css`, `frontend/src/index.css`, `frontend/package.json`, `frontend/Dockerfile`, `frontend/nginx.conf`, `frontend/vite.config.ts`, `frontend/tsconfig.json`, `compose.yaml`, `.github/workflows/ci.yml`, `portfolio.json`, `README.md`, `LICENSE`, `CHANGELOG.md`, `pyproject.toml`, `.gitignore`, `.env.example`, `keycloak/realm.json`

Tests: `backend/tests/test_health.py`, `frontend/src/App.test.tsx`

### prompt-management — Prompt Template Management (CRUD + Search)

Status: planned

Acceptance:
- Create/read/update/delete prompt templates via API
- Search/filter prompts by model, tags, category
- Pagination support
- SQLite persistence with UTC timestamps

### model-specific-prompts — Model-Specific Prompt Swapping

Status: planned

Acceptance:
- Different prompts per model (default: '小码辉')
- Prompt selection by model identifier
- Fallback to default when model-specific not found

### jailbreak-evaluation — Jailbreak Evaluation Engine

Status: planned

Acceptance:
- Deterministic evaluation of prompt effectiveness
- Test suite with labeled dataset
- Metrics: success rate, refusal rate, token usage
- Export results (JSON/CSV)

### oidc-auth — OIDC Authentication with Keycloak

Status: planned

Acceptance:
- Authorization code flow with PKCE
- HttpOnly SameSite cookies + CSRF protection
- Role-based access (viewer/operator/admin)
- Demo mode (localhost only, refuses in production)

### llm-adapters — LLM Provider Adapters

Status: planned

Acceptance:
- OpenAI-compatible, Anthropic, Gemini, Ollama adapters
- Configurable provider/model/endpoint
- Bounded timeouts, redacted errors
- Keys server-side only

### frontend-workflows — Frontend Dashboard and Workflows

Status: planned

Acceptance:
- Prompt library dashboard with create/import/search/detail/export
- Model-specific prompt editor
- Jailbreak evaluation runner with results view
- Loading/error/empty states

