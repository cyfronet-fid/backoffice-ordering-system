# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Backend (Poetry - run in `/backend` directory)
- **Start dev server**: `poetry run uvicorn backend.main:app --reload --host localhost`
- **Run tests**: `poetry run pytest tests/`
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

### Docker Dependencies
- **Start dependencies only**: `docker compose up --scale bos-backend=0`
- **Start all services**: `docker compose up`

## Architecture Overview

### Backend Architecture
- **Framework**: FastAPI with SQLModel ORM and PostgreSQL database
- **Authentication**: Keycloak OAuth2/OIDC integration with dual auth (JWT + API key)
- **Database**: PostgreSQL with Alembic migrations
- **API Structure**: Modular routers in `/backend/routers/`
- **Models**: SQLModel-based tables with relationships in `/backend/models/tables.py`
- **Services**: Business logic in `/backend/services/`
- **Configuration**: Environment-based settings via Pydantic in `/backend/config.py`

### Backend Security Features
- **JWT Authentication**: RS256 tokens with JWKS validation and 5-second leeway
- **API Key Authentication**: Constant-time comparison for external API endpoints
- **RBAC**: Role-based access control with UserType enum (MP_USER, PROVIDER_MANAGER, COORDINATOR, ADMIN)
- **Security Headers**: CSP, X-Frame-Options, X-Content-Type-Options, Referrer-Policy
- **CORS**: Configured for specific frontend origin with credentials support
- **Input Validation**: SQLModel field validation with type checking and constraints
- **SQL Injection Protection**: Parameterized queries via SQLModel ORM

### Frontend Architecture
- **Framework**: React 18 with TypeScript
- **Routing**: TanStack Router with file-based routing
- **UI**: Chakra UI component library
- **Authentication**: OIDC integration with react-oidc-context
- **API Client**: Auto-generated from OpenAPI spec using hey-api/openapi-ts
- **State Management**: React hooks and context
- **Styling**: SCSS with Chakra UI theming

### Key Domain Models
- **User**: Role-based access (MP_USER, PROVIDER_MANAGER, COORDINATOR, ADMIN)
- **Order**: Core entity with status tracking and external references
- **Provider**: Service providers with manager relationships
- **Message**: Communication system with public/private scopes
- **Relationships**: Many-to-many links between Users-Orders, Users-Providers, Orders-Providers

### External Integration
- **Whitelabel API**: Client integration in `/backend/whitelabel_client/`
- **Authentication**: Keycloak realm configuration
- **Database**: PostgreSQL with connection pooling

### Development Environment
- **Python**: 3.12+ managed with Poetry
- **Node**: 21+ for frontend
- **Database**: PostgreSQL via Docker Compose
- **Authentication**: Keycloak container setup

### Key Configuration
- **Backend ENV**: Database connection, Keycloak settings, Whitelabel API config
- **Frontend ENV**: `VITE_BACKEND_URL` for API endpoint
- **Database**: Default connection to localhost:5432 with pg/pg credentials

### Backend File Structure
- **`backend/main.py`**: FastAPI app with security headers middleware and router registration
- **`backend/auth.py`**: Authentication logic (JWT validation, API key verification, user management)
- **`backend/config.py`**: Environment configuration with Pydantic settings
- **`backend/db.py`**: Database connection and session management
- **`backend/routers/`**: API endpoints organized by domain (users, orders, providers, messages, api)
- **`backend/models/tables.py`**: SQLModel database models with relationships and validation
- **`backend/services/call_whitelabel.py`**: External API integration with retry logic
- **`backend/whitelabel_client/`**: Auto-generated client for whitelabel API integration

### Testing
- **Backend**: pytest framework with model tests
- **Frontend**: ESLint and Prettier for code quality
- **CI/CD**: GitHub Actions for automated testing and linting

### Commit Message Convention
This project follows **Conventional Commits** specification (https://www.conventionalcommits.org/):

**Format**: `<type>: [<scope>] <description>`

**Types**:
- `feat`: New feature
- `fix`: Bug fix
- `refactor`: Code refactoring
- `docs`: Documentation updates
- `test`: Adding/updating tests
- `chore`: Maintenance tasks

**Scopes**:
- `[#<issue_number>]`: For GitHub issue references (e.g., `[#23]`)
- `[AdHoc]`: For ad-hoc changes not tied to specific issues
- `[adhoc]`: Alternative lowercase format for ad-hoc changes

**Examples**:
- `feat: [#23] Add role based permissions`
- `fix: [#162] Adjust whitelabel API endpoints`
- `fix: [AdHoc] Adjust whitelabel API and few UI tweaks`
- `refactor: [adhoc] Adjust project structure and readme`

### Important Notes
- Always run linting/formatting before commits
- Backend must be running for frontend API client generation
- Use `poetry shell` for backend development
- Database migrations are auto-generated but should be reviewed
- Authentication tokens are handled via Keycloak integration