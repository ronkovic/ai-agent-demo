# Directory Structure

```
ai-agent-demo/
├── .claude/                    # Claude Code 設定
│   └── settings.local.json     # ローカル設定（hooks含む）
├── .kiri/                      # Kiri インデックス
│   └── index.duckdb            # DuckDB インデックスファイル
├── .serena/                    # Serena メモリ
│   └── memories/               # プロジェクトメモリファイル
├── backend/                    # Python バックエンド
│   ├── app/
│   │   ├── main.py             # FastAPI エントリーポイント
│   │   ├── config.py           # 設定
│   │   ├── models/             # SQLAlchemy モデル
│   │   ├── schemas/            # Pydantic スキーマ
│   │   ├── routers/            # API ルーター
│   │   └── services/           # ビジネスロジック
│   ├── tests/                  # テスト
│   ├── pyproject.toml          # Python 依存関係・設定
│   └── Dockerfile
├── frontend/                   # Next.js フロントエンド
│   ├── app/                    # App Router ページ
│   ├── components/             # React コンポーネント
│   ├── lib/                    # ユーティリティ・API クライアント
│   ├── types/                  # TypeScript 型定義
│   ├── stories/                # Storybook ストーリー
│   ├── __tests__/              # テスト
│   ├── package.json
│   ├── next.config.ts
│   ├── tsconfig.json
│   └── Dockerfile
├── openapi/                    # OpenAPI 定義
│   └── openapi.yaml            # API スキーマ
├── docs/                       # ドキュメント
│   └── PLANNING.md             # プロジェクト計画・進捗
├── docker-compose.yml          # Docker Compose 設定
├── Taskfile.yml                # タスクランナー定義
├── .mcp.json                   # MCP サーバー設定
└── CLAUDE.md                   # Claude Code 指示
```

## 主要ファイルの場所

| 用途 | ファイル |
|------|---------|
| API エントリー | `backend/app/main.py` |
| API ルート定義 | `backend/app/routers/` |
| DB モデル | `backend/app/models/` |
| フロントページ | `frontend/app/` |
| UI コンポーネント | `frontend/components/` |
| API クライアント | `frontend/lib/api/` |
| 生成型定義 | `frontend/types/generated/` |
| プロジェクト計画 | `docs/PLANNING.md` |
| OpenAPI 定義 | `openapi/openapi.yaml` |
