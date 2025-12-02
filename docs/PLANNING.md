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
- [ ] Supabase設定 (Auth + DB)
- [x] 基本的なAPI構造作成
- [x] OpenAPI自動生成設定 (FastAPI → openapi.json → TypeScript型)
- [x] Storybook導入・設定
- [x] Taskfile.yml タスクランナー追加
- [x] vitest ユニットテスト設定 (Frontend)
- [x] pytest テスト設定 (Backend)

### Phase 2: エージェント基本機能

- [ ] DBモデル・マイグレーション作成
- [ ] エージェントCRUD API実装
- [ ] OpenAPIからフロントエンドクライアント生成
- [ ] LLM統合 (LiteLLM)
- [ ] チャットAPI実装 (SSEストリーミング)

### Phase 3: フロントエンドUI

- [ ] 基本UIコンポーネント作成 + Storybook登録
- [ ] チャットUIコンポーネント + Storybook
- [ ] エージェント管理UI + Storybook
- [ ] ページ統合・ルーティング
- [ ] 認証フロー実装

### Phase 4: ツール機能

- [ ] ツールレジストリ設計・実装
- [ ] コード実行ツール実装
- [ ] Web検索ツール実装
- [ ] ツール実行UI + Storybook

### Phase 5: A2A統合

- [ ] A2A SDKセットアップ
- [ ] Agent Card生成・公開
- [ ] A2Aサーバー実装 (タスク受信)
- [ ] A2Aクライアント実装 (他エージェント呼び出し)

### Phase 6: 統合・テスト

- [ ] E2Eテスト
- [ ] Storybookビルド・デプロイ設定
- [ ] ドキュメント・CLAUDE.md更新

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

## 参考リンク

- [Google A2A Protocol](https://github.com/google-a2a/A2A)
- [A2A Python SDK](https://github.com/a2aproject/a2a-python)
- [Supabase Auth](https://supabase.com/auth)
- [LiteLLM](https://github.com/BerriAI/litellm)
- [Storybook](https://storybook.js.org/)
