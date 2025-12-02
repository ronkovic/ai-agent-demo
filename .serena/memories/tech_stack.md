# Technology Stack

## Backend
- **言語**: Python 3.13
- **パッケージ管理**: uv (uvx)
- **フレームワーク**: FastAPI
- **ORM**: SQLAlchemy (非同期)
- **バリデーション**: Pydantic v2
- **テスト**: pytest, pytest-asyncio
- **リンター/フォーマッター**: ruff, mypy

## Frontend
- **フレームワーク**: Next.js 16 (App Router)
- **言語**: TypeScript (strict mode)
- **UI**: React 19
- **スタイリング**: Tailwind CSS
- **状態管理**: TanStack Query
- **テスト**: Vitest, React Testing Library
- **コンポーネントカタログ**: Storybook
- **リンター/フォーマッター**: ESLint, Prettier

## インフラ・サービス
- **データベース**: PostgreSQL (Supabase)
- **認証**: Supabase Auth
- **コンテナ**: Docker, Docker Compose
- **タスクランナー**: Taskfile

## LLM・AI連携
- **LLM Gateway**: LiteLLM
- **対応プロバイダー**: 
  - Anthropic Claude
  - OpenAI GPT
  - AWS Bedrock
- **エージェント連携**: Google A2A Protocol

## 開発ツール
- **API仕様**: OpenAPI 3.1
- **コード生成**: openapi-generator (TypeScript型生成)
- **MCP**: Kiri (コード検索), Serena (IDE支援)
