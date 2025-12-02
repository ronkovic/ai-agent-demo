# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is an AI Agent Platform - a full-stack application for creating, managing, and interacting with AI agents. The platform supports multiple LLM providers (OpenAI, Anthropic, Google) and includes A2A (Agent-to-Agent) protocol integration for multi-agent orchestration.

## Architecture

```
ai-agent-demo/
├── backend/          # Python FastAPI backend
│   ├── src/agent_platform/
│   │   ├── api/      # REST API endpoints
│   │   ├── core/     # Core business logic
│   │   ├── models/   # SQLAlchemy models
│   │   ├── schemas/  # Pydantic schemas
│   │   └── services/ # Business services
│   └── tests/        # pytest tests
├── frontend/         # Next.js 15 frontend
│   ├── src/
│   │   ├── app/      # App Router pages
│   │   ├── components/ # React components
│   │   ├── hooks/    # Custom React hooks
│   │   ├── lib/      # Utilities
│   │   └── types/    # TypeScript types
│   ├── e2e/          # Playwright E2E tests
│   └── stories/      # Storybook stories
├── docs/             # Project documentation
└── Taskfile.yml      # Task runner commands
```

## Tech Stack

### Backend
- **Framework**: FastAPI
- **ORM**: SQLAlchemy with SQLite
- **Package Manager**: uv
- **LLM Integration**: litellm (multi-provider support)
- **Testing**: pytest

### Frontend
- **Framework**: Next.js 15 (App Router)
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **UI Components**: Radix UI + shadcn/ui
- **State Management**: React hooks + Context
- **Testing**: Vitest (unit), Playwright (E2E)
- **Documentation**: Storybook 10

## Development Commands

All commands are run via Taskfile (`task <command>`):

### Setup
```bash
task setup              # Setup all (backend + frontend)
task setup:backend      # Setup backend (uv sync)
task setup:frontend     # Setup frontend (npm install)
```

### Development Servers
```bash
task dev                # Start both servers
task dev:backend        # Backend only (port 8000)
task dev:frontend       # Frontend only (port 3000)
task storybook          # Storybook (port 6006)
```

### Testing
```bash
task test               # Run all unit tests
task test:backend       # Backend tests (pytest)
task test:frontend      # Frontend tests (vitest)
task test:e2e           # E2E tests (playwright)
task test:e2e:ui        # E2E tests with UI
task test:all           # All tests (unit + E2E)
```

### Code Quality
```bash
task lint               # Run all linters
task lint:backend       # Backend lint (ruff)
task lint:frontend      # Frontend lint (eslint)
task format             # Format all code
task format:backend     # Format backend (ruff)
task format:frontend    # Format frontend (prettier)
```

### Build
```bash
task build              # Build frontend
task storybook:build    # Build Storybook
task openapi            # Generate OpenAPI schema + client
```

### Docker
```bash
task docker:up          # Start containers
task docker:down        # Stop containers
task docker:logs        # View logs
```

## MCP Servers

The project has MCP servers configured in `.mcp.json`:

- **filesystem**: Access to Desktop, Downloads, and workspace directories
- **context7**: Documentation retrieval via @upstash/context7-mcp
- **kiri**: Code indexing with DuckDB (index stored in `.kiri/`)
- **chrome-devtools**: Browser automation and DevTools integration
- **next-devtools**: Next.js development tools
- **aws-mcp**: AWS services integration (configured for ap-northeast-1 region)
- **serena**: IDE assistant functionality

## Coding Guidelines

### Backend (Python)
- Use type hints for all function parameters and return values
- Follow PEP 8 style guide (enforced by ruff)
- Use async/await for I/O operations
- Place business logic in `services/`, API routes in `api/`
- Use Pydantic models for request/response validation

### Frontend (TypeScript)
- Use functional components with hooks
- Prefer named exports over default exports
- Use `'use client'` directive only when necessary
- Follow component structure: props interface → component → export
- Use Tailwind CSS for styling, avoid inline styles
- Place reusable components in `components/ui/`

### Testing
- Backend: pytest with fixtures in `conftest.py`
- Frontend: Vitest for unit tests, Playwright for E2E
- E2E tests use Playwright `page.route()` for API mocking (not MSW - see CI Notes below)
- Test files should be named `*.test.ts` or `*.spec.ts`

## CI Notes (重要)

### コミット前チェック
- **PLANNING.md必須**: コミット時に `docs/PLANNING.md` がステージングされていないとフックでブロックされる
- 変更がなくても `git add docs/PLANNING.md` してからコミット

### E2Eテスト (Playwright)
- **APIモック**: `page.route()` を使用（`frontend/e2e/fixtures.ts`）
  - MSWはブラウザレベルのモックだが、Next.jsのrewritesはサーバーサイドでプロキシするため、MSWでは捕捉できない
  - CIではバックエンドが起動しないため、Playwrightのネイティブモックが必須
- **セレクタ**: 実際のUI要素に合わせる
  - `getByRole('button', ...)` vs `getByRole('link', ...)` を正確に
  - 複数マッチする場合は具体的な名前を指定（例: `/エージェントを保存/i`）
- **アクセシビリティ属性必須**:
  - `data-testid` - テスト識別用
  - `aria-label` - アクセシビリティ
  - `htmlFor` + `id` - ラベルとinputの関連付け
  - セマンティック要素 (`<aside>`, `<header>`, `<nav>`)

### バックエンドテスト (pytest)
- **SQLite互換**: CIではSQLiteを使用（PostgreSQL不要）
  - `GUID` TypeDecorator - UUID型の互換性
  - `PortableJSON` TypeDecorator - JSON型の互換性
  - `backend/src/agent_platform/db/types.py` 参照

### Lint
- Backend: `uv run ruff check --fix`
- Frontend: `npm run lint`
- 警告は許容、エラーはブロック

## API Endpoints

### Agents API
- `GET /api/agents` - List all agents
- `POST /api/agents` - Create new agent
- `GET /api/agents/{id}` - Get agent details
- `PUT /api/agents/{id}` - Update agent
- `DELETE /api/agents/{id}` - Delete agent

### Chat API
- `POST /api/chat/stream` - Stream chat messages (SSE)

### A2A Protocol
- `POST /api/a2a/{agent_id}/tasks/send` - Send task to agent
- `GET /api/a2a/{agent_id}/tasks/{task_id}` - Get task status

## Debugging Tips

### Backend
1. Check logs in terminal running `task dev:backend`
2. Use `/docs` endpoint for Swagger UI
3. Database is SQLite at `backend/agent_platform.db`

### Frontend
1. Check browser DevTools console
2. Use React DevTools for component inspection
3. Network tab for API request/response debugging

### Common Issues
- **CORS errors**: Ensure backend is running on port 8000
- **API not found**: Check if OpenAPI client is generated (`task openapi`)
- **Type errors**: Run `npm run type-check` in frontend

## Common Tasks

### Adding a New Agent Feature
1. Add model field in `backend/src/agent_platform/models/`
2. Update Pydantic schema in `schemas/`
3. Add API endpoint in `api/`
4. Regenerate client: `task openapi`
5. Update frontend components

### Adding a New UI Component
1. Create component in `frontend/src/components/`
2. Add Storybook story in `frontend/stories/`
3. Write unit test in same directory
4. Export from component index if reusable

### Running E2E Tests Locally
```bash
cd frontend
npm run test:e2e:headed  # Watch tests run in browser
```

## Maintenance Reminders

### Copyright Year Update (著作権年更新)
When making updates in a new calendar year, update the copyright year in the following files:

**Current format**: `Copyright (c) 2024-2025`
- `2024` = First published year (固定)
- `2025` = Last updated year (更新時に変更)

**Files to update**:
1. `LICENSE` - Line 5 and lines 253-255
2. `COPYRIGHT` - Line 5 and source file header templates
3. `README.md` - License section
4. `docs/PLANNING.md` - License section

**Example**: In 2026, change `2024-2025` → `2024-2026`
