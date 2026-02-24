# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Backend (Poetry - run in `/backend` directory)
- **Start dev server**: `poetry run uvicorn backend.main:app --reload --host localhost`
- **Run all tests**: `poetry run pytest tests/`
- **Run unit tests only** (no Docker): `poetry run pytest tests/unit/`
- **Run integration tests only** (requires Docker): `poetry run pytest tests/integration/`
- **Lint check**: `poetry run lint`
- **Format code**: `poetry run format`
- **Run single test**: `poetry run pytest tests/path/to/test.py::test_function_name`
- **Database migrations**: `poetry run alembic upgrade head`
- **Generate migration**: `poetry run alembic revision --autogenerate -m "description"`
- **Database seeding**: `poetry run db:seed`
- **Database clear**: `poetry run db:clear`
- **Generate whitelabel client**: `poetry run wl:generate-client`
- **Retry whitelabel sync**: `poetry run wl:retry-sync`

### Frontend (npm - run in `/frontend` directory)
- **Start dev server**: `npm run dev`
- **Build for production**: `npm run build`
- **Lint check**: `npm run lint`
- **Format code**: `npm run format`
- **Generate API client**: `npm run generate-client` (requires backend running on localhost:8000)

### Docker
- **Start dependencies only**: `docker compose up --scale bos-backend=0` (recommended for local dev)
- **Start all services**: `docker compose up`

## Architecture Overview

### Backend (FastAPI + SQLModel + PostgreSQL)
- **Entry point**: `backend/backend/main.py` - FastAPI app with security headers middleware
- **Auth**: `backend/backend/auth.py` - JWT validation (RS256/JWKS), API key verification, user management
- **Config**: `backend/backend/config.py` - Pydantic settings from environment
- **Database**: `backend/backend/db.py` - Session management; models in `backend/backend/models/tables.py`
- **Routers**: `backend/backend/routers/` - API endpoints (users, orders, providers, messages, api)
- **Services**: `backend/backend/services/` - Business logic including whitelabel API integration
- **Whitelabel client**: `backend/backend/whitelabel_client/` - Auto-generated external API client

### Testing (`backend/tests/`)
- **`unit/`** — no DB, no Docker; plain `TestClient`; models, auth, security headers
- **`integration/`** — real PostgreSQL via `pytest-postgresql`; alembic runs once per session; tables truncated between tests
- **`integration/factories.py`** — factory-boy factories for all models; auto-discovered and registered as pytest fixtures via `inspect`
- **`integration/routers/conftest.py`** — role-based client fixtures: `admin_client`, `coordinator_client`, `provider_manager_client`, `mp_user_client`, `api_client`
- Coverage runs automatically on every `pytest` call (`pytest-cov`); report omits `migrations/` and `whitelabel_client/`

### Frontend (React 18 + TypeScript)
- **Routing**: TanStack Router with file-based routing
- **UI**: Chakra UI component library with SCSS theming
- **Auth**: OIDC via react-oidc-context (Keycloak)
- **API Client**: Auto-generated from OpenAPI spec using hey-api/openapi-ts

### Authentication
- **Dual auth**: JWT tokens (frontend users) + API key (external services)
- **RBAC roles**: MP_USER, PROVIDER_MANAGER, COORDINATOR, ADMIN (defined in `UserType` enum)
- **Provider**: Keycloak OAuth2/OIDC

### Domain Models
- **User**: Role-based access with provider relationships
- **Order**: Core entity with status tracking and external references
- **Provider**: Service providers with manager relationships
- **Message**: Communication with public/private scopes
- **Link tables**: Users-Orders, Users-Providers, Orders-Providers (many-to-many)

## Environment Variables

### Backend
| Variable | Default | Description |
|----------|---------|-------------|
| `DB_HOST` | `localhost` | PostgreSQL host |
| `DB_PORT` | `5432` | PostgreSQL port |
| `DB_USER` | `pg` | PostgreSQL user |
| `DB_PASSWORD` | `pg` | PostgreSQL password |
| `DB_NAME` | `postgres` | Database name |
| `API_KEY` | **required** | API key for external access |
| `KEYCLOAK_HOST` | `https://keycloak.docker-fid.grid.cyf-kr.edu.pl` | Keycloak URL |
| `KEYCLOAK_REALM` | `core` | Keycloak realm |
| `KEYCLOAK_CLIENT_ID` | `bos` | Keycloak client |
| `FRONTEND_URL` | `http://localhost:5173` | Frontend URL (CORS) |
| `WHITELABEL_ENDPOINT` | `http://localhost:5000` | Whitelabel API URL |
| `WHITELABEL_CLIENT_KEY` | `""` | Whitelabel API key |

### Frontend
| Variable | Default | Description |
|----------|---------|-------------|
| `VITE_BACKEND_URL` | `http://localhost:8000` | Backend API URL |
| `VITE_KEYCLOAK_HOST` | `https://keycloak.docker-fid.grid.cyf-kr.edu.pl` | Keycloak URL |
| `VITE_KEYCLOAK_REALM` | `core` | Keycloak realm |
| `VITE_KEYCLOAK_CLIENT_ID` | `bos` | Keycloak client |

## Commit Message Convention

**Format**: `<type>: [<scope>] <description>`

**Types**: `feat`, `fix`, `refactor`, `docs`, `test`, `chore`

**Scopes**: `[#<issue_number>]` for GitHub issues, `[AdHoc]` for ad-hoc changes

**Examples**:
- `feat: [#23] Add role based permissions`
- `fix: [AdHoc] Adjust whitelabel API and few UI tweaks`