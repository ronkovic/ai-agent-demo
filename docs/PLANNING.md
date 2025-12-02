# AI Agent Demo Project - 実装プラン

## 概要

マルチユーザー対応のAIエージェントプラットフォーム。ユーザーは複数のAIエージェントを作成し、Google A2Aプロトコルで連携可能。

## 技術スタック

| レイヤー | 技術 |
|---------|------|
| Backend | Python 3.12+ (uv), FastAPI |
| Frontend | Next.js 16 (App Router), TypeScript |
| 認証 | Supabase Auth |
| DB | PostgreSQL (Supabase) |
| LLM | LiteLLM (Claude, OpenAI, Bedrock対応) |
| Agent連携 | Google A2A Protocol (a2a-sdk) |
| API連携 | OpenAPI 3.1 (自動生成 + TypeScript型生成) |
| UI開発 | Storybook 8 (コンポーネントカタログ) |
| 開発環境 | Docker Compose |

## MVP要件

- [x] 会話型アシスタント
- [x] タスク自動化（ツール呼び出し）
- [x] コード生成/分析
- [x] マルチユーザー対応
- [x] ユーザーごとに複数エージェント作成
- [x] A2Aでエージェント間連携

## MVP外

- RAG/ナレッジベース
- エージェントの公開/非公開設定
- 公開エージェントの共有
- MCPサーバー統合

---

## プロジェクト構成

```text
ai-agent-demo/
├── backend/
│   ├── pyproject.toml          # uv設定
│   ├── src/
│   │   └── agent_platform/
│   │       ├── main.py         # FastAPIエントリポイント
│   │       ├── api/
│   │       │   ├── routes/
│   │       │   │   ├── agents.py    # エージェントCRUD
│   │       │   │   ├── chat.py      # チャットAPI
│   │       │   │   └── a2a.py       # A2Aエンドポイント
│   │       │   └── deps.py          # 依存性注入
│   │       ├── core/
│   │       │   ├── config.py        # 設定
│   │       │   ├── agent.py         # エージェントランタイム
│   │       │   └── executor.py      # ツール実行
│   │       ├── llm/
│   │       │   ├── base.py          # LLMインターフェース
│   │       │   └── provider.py      # LiteLLM統合
│   │       ├── tools/
│   │       │   ├── registry.py      # ツール登録
│   │       │   ├── code.py          # コード実行ツール
│   │       │   └── web.py           # Web検索ツール
│   │       ├── a2a/
│   │       │   ├── server.py        # A2Aサーバー実装
│   │       │   ├── client.py        # A2Aクライアント
│   │       │   └── card.py          # Agent Card生成
│   │       ├── db/
│   │       │   ├── models.py        # SQLAlchemyモデル
│   │       │   └── repository.py    # データアクセス
│   │       └── auth/
│   │           └── supabase.py      # Supabase認証
│   └── tests/
│
├── frontend/
│   ├── package.json
│   ├── .storybook/             # Storybook設定
│   │   ├── main.ts
│   │   └── preview.ts
│   ├── src/
│   │   ├── app/
│   │   │   ├── layout.tsx
│   │   │   ├── page.tsx            # ダッシュボード
│   │   │   ├── agents/
│   │   │   │   ├── page.tsx        # エージェント一覧
│   │   │   │   ├── new/page.tsx    # 新規作成
│   │   │   │   └── [id]/
│   │   │   │       ├── page.tsx    # チャット画面
│   │   │   │       └── settings/page.tsx
│   │   │   ├── auth/
│   │   │   │   └── callback/route.ts
│   │   │   └── api/                # BFF
│   │   ├── components/
│   │   │   ├── chat/
│   │   │   │   ├── ChatMessage.tsx
│   │   │   │   ├── ChatMessage.stories.tsx  # Storybook
│   │   │   │   └── ChatInput.tsx
│   │   │   ├── agent/
│   │   │   └── ui/                 # shadcn/ui
│   │   ├── lib/
│   │   │   ├── supabase.ts
│   │   │   ├── api.ts              # OpenAPI生成クライアント
│   │   │   └── api-client/         # openapi-typescript-codegen出力
│   │   │       ├── index.ts
│   │   │       ├── models/
│   │   │       └── services/
│   │   └── hooks/
│   └── public/
│
├── openapi/
│   └── openapi.json            # FastAPIから自動生成
│
├── docs/
│   └── PLANNING.md
├── docker-compose.yml
├── .env.example
├── .mcp.json                   # 既存
└── CLAUDE.md
```

---

## データモデル

```sql
-- users: Supabase Authが管理

-- agents: ユーザーが作成するAIエージェント
CREATE TABLE agents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    system_prompt TEXT NOT NULL,
    llm_provider VARCHAR(50) NOT NULL,  -- 'claude', 'openai', 'bedrock'
    llm_model VARCHAR(100) NOT NULL,
    tools JSONB DEFAULT '[]',           -- 有効なツール一覧
    a2a_enabled BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- conversations: 会話セッション
CREATE TABLE conversations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    agent_id UUID NOT NULL REFERENCES agents(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES auth.users(id),
    title VARCHAR(255),
    created_at TIMESTAMP DEFAULT NOW()
);

-- messages: チャットメッセージ
CREATE TABLE messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id UUID NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
    role VARCHAR(20) NOT NULL,          -- 'user', 'assistant', 'tool'
    content TEXT NOT NULL,
    tool_calls JSONB,                   -- ツール呼び出し情報
    a2a_source UUID,                    -- A2A経由の場合、送信元agent_id
    created_at TIMESTAMP DEFAULT NOW()
);

-- agent_cards: A2A Agent Card情報
CREATE TABLE agent_cards (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    agent_id UUID NOT NULL REFERENCES agents(id) ON DELETE CASCADE,
    card_json JSONB NOT NULL,           -- A2A Agent Card
    endpoint_url VARCHAR(500),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

---

## A2A統合設計

### Agent Card構造

```json
{
  "name": "CodeAssistant",
  "description": "コード生成・分析を行うエージェント",
  "url": "http://localhost:8000/a2a/agents/{agent_id}",
  "version": "1.0.0",
  "capabilities": {
    "streaming": true,
    "pushNotifications": false
  },
  "skills": [
    {
      "id": "code_generation",
      "name": "Code Generation",
      "description": "指定された仕様に基づいてコードを生成"
    }
  ]
}
```

### A2Aエンドポイント

- `GET /a2a/agents/{id}/.well-known/agent.json` - Agent Card取得
- `POST /a2a/agents/{id}/tasks` - タスク送信
- `GET /a2a/agents/{id}/tasks/{task_id}` - タスク状態取得
- `POST /a2a/agents/{id}/tasks/{task_id}/cancel` - タスクキャンセル

---

## 実装フェーズ

### Phase 1: プロジェクト基盤 ✅

- [x] バックエンドプロジェクト初期化 (`uv init`)
- [x] フロントエンドプロジェクト初期化 (`npx create-next-app`)
- [x] Docker Compose設定 (PostgreSQL, Backend, Frontend)
- [x] Supabase設定 (Auth + DB) - モック認証実装完了、Supabase接続は環境変数で切り替え可能
- [x] 基本的なAPI構造作成
- [x] OpenAPI自動生成設定 (FastAPI → openapi.json → TypeScript型)
- [x] Storybook導入・設定
- [x] Taskfile.yml タスクランナー追加
- [x] vitest ユニットテスト設定 (Frontend)
- [x] pytest テスト設定 (Backend)
- [x] Claude Code hooks設定 (git commit前にPLANNING.md更新リマインダー)
- [x] MCP Kiri/Serena オンボーディング (コード検索・IDE支援)

### Phase 2: エージェント基本機能 ✅

- [x] DBモデル・マイグレーション作成 (SQLAlchemy + Alembic)
- [x] エージェントCRUD API実装
- [x] OpenAPIからフロントエンドクライアント生成
- [x] LLM統合 (LiteLLM)
- [x] チャットAPI実装 (SSEストリーミング)
- [x] テスト追加 (pytest-asyncio)

### Phase 3: フロントエンドUI ✅

- [x] 基本UIコンポーネント作成 + Storybook登録 (Header, Sidebar, AppLayout)
- [x] チャットUIコンポーネント + Storybook (ChatMessage, ChatInput, ChatContainer)
- [x] エージェント管理UI + Storybook (AgentCard, AgentForm)
- [x] カスタムフック (useAgents, useChat with SSE)
- [x] ページ統合・ルーティング (5ページ実装)
- [x] テーマ切り替え (ThemeToggle: システム/ライト/ダーク)
- [x] 認証フロー実装
  - Backend JWT認証 (auth/jwt.py, deps.py)
  - Frontend Supabaseクライアント (@supabase/ssr)
  - AuthContext & useAuth フック
  - 認証ページ (login, signup, callback)
  - 保護ルート & UserMenu
  - モック認証対応 (Supabase未設定時も開発可能)
  - E2E認証テスト追加

### Phase 4: ツール機能 ✅

- [x] ツールレジストリ設計・実装 (BaseTool, ToolDefinition, ToolRegistry)
- [x] コード実行ツール実装 (Dockerコンテナ内でPython/JavaScript安全実行)
- [x] Web検索ツール実装 (抽象プロバイダー + MockSearchProvider)
- [x] ToolExecutor実装 (タイムアウト、並列実行、呼び出し制限)
- [x] LLM拡張 (ToolCall dataclass, OpenAI/Anthropic/LiteLLM形式変換)
- [x] ChatService統合 (chat_stream_with_tools, ChatEvent)
- [x] SSE API拡張 (POST /stream/tools エンドポイント)
- [x] ツール実行UI + Storybook (ToolCallDisplay, ToolCallBadge)
- [x] テスト追加 (test_tools.py: 19テスト, test_executor.py: 7テスト)

### Phase 5: A2A統合 ✅

- [x] A2A SDKセットアップ
- [x] Agent Card生成・公開 (card.py)
- [x] A2Aサーバー実装 (server.py, task_store.py, types.py)
- [x] A2Aクライアント実装 (client.py)
- [x] invoke_agentツール (tools/a2a.py)
- [x] A2A APIルート (api/routes/a2a.py)
- [x] テスト追加 (test_a2a.py: 33テスト)

### Phase 6: 統合・テスト ✅

- [x] E2Eテスト (Playwright + MSW)
  - playwright.config.ts設定
  - MSWハンドラー (e2e/mocks/)
  - E2Eテストケース (home, agents, chat)
- [x] Storybookビルド・デプロイ設定
  - GitHub Actions ワークフロー (.github/workflows/storybook.yml)
  - GitHub Pages デプロイ
  - Taskfile.yml タスク追加 (storybook:serve, test:e2e)
- [x] CI/CD設定
  - GitHub Actions CI (.github/workflows/ci.yml)
  - Backend: ruff lint + pytest (SQLite in-memory, DB不要)
  - Frontend: eslint + typecheck + vitest
  - E2E: Playwright tests (page.route()ネイティブモック)
  - CI lint修正 (ruff I001/F401/N815/F821, eslint setState-in-effect)
  - mainブランチプロテクション設定 (required status checks)
  - jsdom依存追加 (vitest unit tests用)
  - SQLite/PostgreSQL互換対応 (GUID, PortableJSON TypeDecorators)
  - ローカル開発: SQLite自動使用 (DATABASE_URL未設定時)
  - 起動時DBテーブル自動作成 (main.py lifespan)
  - E2Eテスト対応: アクセシビリティ改善 (title, aside, data-testid, aria-label, htmlFor)
  - E2Eテストセレクタ修正 (button vs link, 具体的なボタン名セレクタ)
  - Lint警告修正: useWatch使用 (React Compiler互換), useCallback依存関係修正
- [x] ドキュメント・CLAUDE.md更新
  - CLAUDE.md 包括的更新 (アーキテクチャ、コマンド、ガイドライン)
  - README.md 作成 (ルート、backend、frontend)

---

## 開発コマンド

### Taskfile (推奨)

```bash
task setup          # 開発環境セットアップ (backend + frontend)
task dev            # 開発サーバー起動 (backend + frontend 並列)
task dev:backend    # バックエンド開発サーバーのみ
task dev:frontend   # フロントエンド開発サーバーのみ

task storybook      # Storybook起動 (port 6006)
task openapi        # OpenAPIスキーマとクライアント生成

task test           # 全テスト実行
task test:backend   # バックエンドテスト (pytest)
task test:frontend  # フロントエンドテスト (vitest)

task lint           # 全リント実行
task format         # 全フォーマット実行

task docker:up      # Dockerコンテナ起動
task docker:down    # Dockerコンテナ停止
task docker:logs    # Dockerログ表示
```

### 個別コマンド

```bash
# Backend
cd backend
uv sync --all-extras             # 依存関係インストール (dev含む)
uv run fastapi dev src/agent_platform/main.py  # 開発サーバー
uv run pytest                    # テスト

# Frontend
cd frontend
npm install                      # 依存関係インストール
npm run dev                      # 開発サーバー (port 3000)
npm run test                     # ユニットテスト
npm run storybook                # Storybook起動 (port 6006)
npm run generate-api             # OpenAPIからTypeScriptクライアント生成

# Docker
docker-compose up -d             # 全サービス起動
docker-compose logs -f backend   # ログ確認
```

---

## OpenAPI連携フロー

```text
┌─────────────┐     自動生成      ┌──────────────────┐
│   FastAPI   │ ──────────────▶  │  openapi.json    │
│  (Backend)  │                   │  (openapi/)      │
└─────────────┘                   └────────┬─────────┘
                                           │
                                           ▼ openapi-typescript-codegen
                                  ┌──────────────────┐
                                  │  TypeScript型    │
                                  │  APIクライアント │
                                  │  (frontend/src/  │
                                  │   lib/api-client)│
                                  └──────────────────┘
```

**使用ツール:**

- Backend: FastAPI組み込みOpenAPI生成
- Frontend: `openapi-typescript-codegen` (型安全なAPIクライアント自動生成)

---

## CI/CD 注意事項

### コミット前チェック

- `docs/PLANNING.md` がステージングされていないとコミットがブロックされる（pre-commit hook）
- 内容変更がなくても `git add docs/PLANNING.md` が必要

### E2Eテスト (Playwright)

| 項目 | 注意点 |
|------|--------|
| APIモック | `page.route()` を使用（`frontend/e2e/fixtures.ts`）。MSWはNext.jsのrewritesをモックできない |
| セレクタ | `button` vs `link` を正確に。複数マッチする場合は具体的な名前を指定 |
| アクセシビリティ | `data-testid`, `aria-label`, `htmlFor`+`id`, セマンティック要素（`<aside>`, `<header>`）が必須 |

### バックエンドテスト (pytest)

- CIではSQLite使用（PostgreSQL不要）
- UUID/JSON型は `GUID`, `PortableJSON` TypeDecoratorで互換性確保
- 参照: `backend/src/agent_platform/db/types.py`

### Lint

- Backend: `uv run ruff check` - I001(import順), F401(未使用import), N815(変数名) など
- Frontend: `npm run lint` - react-hooks/rules-of-hooks, exhaustive-deps など
- 警告は許容、エラーはブロック

### 環境変数セットアップ

新しい開発環境では以下のファイルを作成:

```bash
# Frontend
cp frontend/.env.example frontend/.env.local
# Backend
cp backend/.env.example backend/.env
```

Supabaseダッシュボードから値を取得:
- `SUPABASE_URL`: Settings > API > Project URL
- `SUPABASE_ANON_KEY`: Settings > API > anon public
- `SUPABASE_JWT_SECRET`: Settings > JWT Keys > Legacy JWT Secret

---

## 参考リンク

- [Google A2A Protocol](https://github.com/google-a2a/A2A)
- [A2A Python SDK](https://github.com/a2aproject/a2a-python)
- [Supabase Auth](https://supabase.com/auth)
- [LiteLLM](https://github.com/BerriAI/litellm)
- [Storybook](https://storybook.js.org/)
