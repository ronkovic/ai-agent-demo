# AI Agent Platform

A full-stack application for creating, managing, and interacting with AI agents. Supports multiple LLM providers and includes A2A (Agent-to-Agent) protocol integration for multi-agent orchestration.

## Features

- **Multi-Provider LLM Support**: OpenAI, Anthropic (Claude), Google (Gemini)
- **Agent Management**: Create, configure, and manage AI agents with custom system prompts
- **Real-time Chat**: SSE-based streaming chat interface
- **A2A Protocol**: Agent-to-Agent communication for multi-agent workflows
- **Tool Integration**: Extensible tool system for agent capabilities
- **Dark/Light Theme**: Customizable UI with theme support

## Tech Stack

| Layer | Technology |
|-------|------------|
| Backend | Python, FastAPI, SQLAlchemy, litellm |
| Frontend | Next.js 15, TypeScript, Tailwind CSS, Radix UI |
| Database | SQLite |
| Testing | pytest, Vitest, Playwright |
| Documentation | Storybook |

## Quick Start

### Prerequisites

- Node.js 20+
- Python 3.12+
- [uv](https://docs.astral.sh/uv/) (Python package manager)
- [Task](https://taskfile.dev/) (Task runner)

### Setup

```bash
# Clone the repository
git clone https://github.com/your-org/ai-agent-demo.git
cd ai-agent-demo

# Install all dependencies
task setup
```

### Environment Variables

Create `.env` files:

**Backend** (`backend/.env`):
```env
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
GOOGLE_API_KEY=...
```

**Frontend** (`frontend/.env.local`):
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### Development

```bash
# Start both backend and frontend
task dev

# Or start individually
task dev:backend   # http://localhost:8000
task dev:frontend  # http://localhost:3000
```

### View Storybook

```bash
task storybook     # http://localhost:6006
```

## Project Structure

```
ai-agent-demo/
├── backend/              # Python FastAPI backend
│   ├── src/agent_platform/
│   │   ├── api/          # REST API endpoints
│   │   ├── core/         # Core business logic
│   │   ├── models/       # SQLAlchemy models
│   │   ├── schemas/      # Pydantic schemas
│   │   └── services/     # Business services
│   └── tests/            # pytest tests
├── frontend/             # Next.js frontend
│   ├── src/
│   │   ├── app/          # App Router pages
│   │   ├── components/   # React components
│   │   ├── hooks/        # Custom hooks
│   │   └── lib/          # Utilities
│   ├── e2e/              # Playwright E2E tests
│   └── stories/          # Storybook stories
├── docs/                 # Documentation
├── Taskfile.yml          # Task runner commands
└── docker-compose.yml    # Docker configuration
```

## Available Commands

| Command | Description |
|---------|-------------|
| `task setup` | Install all dependencies |
| `task dev` | Start development servers |
| `task test` | Run all unit tests |
| `task test:e2e` | Run E2E tests |
| `task lint` | Run linters |
| `task format` | Format code |
| `task build` | Build for production |
| `task storybook` | Start Storybook |

## API Documentation

When the backend is running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      Frontend (Next.js)                     │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │
│  │   Pages     │  │ Components  │  │   API Client        │  │
│  │ (App Router)│  │ (shadcn/ui) │  │ (OpenAPI Generated) │  │
│  └─────────────┘  └─────────────┘  └─────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼ HTTP/SSE
┌─────────────────────────────────────────────────────────────┐
│                     Backend (FastAPI)                        │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │
│  │  REST API   │  │  Services   │  │    LLM Provider     │  │
│  │  Endpoints  │  │ (Business)  │  │     (litellm)       │  │
│  └─────────────┘  └─────────────┘  └─────────────────────┘  │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │
│  │ A2A Protocol│  │    Tools    │  │  Agent Execution    │  │
│  │   Handler   │  │   System    │  │     Engine          │  │
│  └─────────────┘  └─────────────┘  └─────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                      Database (SQLite)                       │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │
│  │   Agents    │  │  Messages   │  │    Conversations    │  │
│  └─────────────┘  └─────────────┘  └─────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

MIT License - see [LICENSE](LICENSE) for details.
