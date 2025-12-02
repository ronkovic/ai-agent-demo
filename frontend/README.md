# Frontend - AI Agent Platform

Next.js 15 frontend for the AI Agent Platform.

## Architecture

```
src/
├── app/                    # App Router pages
│   ├── page.tsx            # Home page
│   ├── agents/
│   │   ├── page.tsx        # Agent list
│   │   ├── new/page.tsx    # Create agent
│   │   └── [id]/
│   │       ├── page.tsx    # Agent chat
│   │       └── settings/   # Agent settings
│   └── layout.tsx          # Root layout
├── components/
│   ├── ui/                 # shadcn/ui components
│   ├── layout/             # Layout components
│   ├── chat/               # Chat components
│   └── agents/             # Agent components
├── hooks/                  # Custom React hooks
│   ├── use-agents.ts       # Agent data hook
│   └── use-chat.ts         # Chat functionality
├── lib/
│   ├── api/                # API client (generated)
│   └── utils.ts            # Utility functions
└── types/                  # TypeScript types
```

## Setup

```bash
# Install dependencies
npm install
# or
task setup:frontend
```

## Environment Variables

Create `.env.local` file:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Development

```bash
# Start development server
npm run dev
# or
task dev:frontend
```

Frontend will be available at http://localhost:3000

## Scripts

| Script | Description |
|--------|-------------|
| `npm run dev` | Start development server |
| `npm run build` | Build for production |
| `npm run start` | Start production server |
| `npm run lint` | Run ESLint |
| `npm run type-check` | TypeScript type checking |
| `npm test` | Run unit tests (Vitest) |
| `npm run test:e2e` | Run E2E tests (Playwright) |
| `npm run storybook` | Start Storybook |
| `npm run build-storybook` | Build Storybook |
| `npm run generate-api` | Generate API client |

## Component Library

UI components are built with:
- **Radix UI**: Accessible primitives
- **shadcn/ui**: Pre-styled components
- **Tailwind CSS**: Utility-first styling

### Adding New Components

```bash
# Add shadcn/ui component
npx shadcn-ui@latest add button
```

## State Management

- **Server State**: React Query (via OpenAPI client)
- **Client State**: React hooks + Context
- **Form State**: React Hook Form + Zod

## API Client

API client is auto-generated from OpenAPI schema:

```bash
# Generate client
task openapi
```

Generated files are in `src/lib/api/generated/`.

## Testing

### Unit Tests (Vitest)

```bash
# Run tests
npm test

# Watch mode
npm run test:watch

# Coverage
npm run test:coverage
```

### E2E Tests (Playwright)

```bash
# Run E2E tests
npm run test:e2e

# With UI
npm run test:e2e:ui

# Headed mode
npm run test:e2e:headed
```

E2E tests use MSW for API mocking.

## Storybook

Component documentation and visual testing:

```bash
# Start Storybook
npm run storybook

# Build static Storybook
npm run build-storybook
```

Stories are in `stories/` directory.

## Code Style

- **Linter**: ESLint with Next.js config
- **Formatter**: Prettier
- **Type Checking**: TypeScript strict mode

```bash
# Lint
npm run lint

# Format
npx prettier --write "src/**/*.{ts,tsx}"

# Type check
npm run type-check
```

## Pages

| Route | Description |
|-------|-------------|
| `/` | Home page |
| `/agents` | Agent list |
| `/agents/new` | Create new agent |
| `/agents/[id]` | Agent chat interface |
| `/agents/[id]/settings` | Agent settings |

## Theme

Dark/Light theme support via `next-themes`:

- Theme toggle in header
- System preference detection
- Persistent preference in localStorage
