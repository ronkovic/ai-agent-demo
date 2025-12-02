# Suggested Commands

## Taskfile コマンド（推奨）

プロジェクトルートで実行:

```bash
# セットアップ
task setup              # 全体セットアップ（backend + frontend）
task setup:backend      # バックエンドのみ
task setup:frontend     # フロントエンドのみ

# 開発サーバー
task dev                # 全サービス起動（Docker Compose）
task dev:backend        # バックエンドのみ
task dev:frontend       # フロントエンドのみ

# テスト
task test               # 全テスト実行
task test:backend       # バックエンドテスト (pytest)
task test:frontend      # フロントエンドテスト (vitest)

# リント・フォーマット
task lint               # 全リント実行
task lint:backend       # Python リント (ruff + mypy)
task lint:frontend      # TypeScript リント (ESLint)
task format             # 全フォーマット実行
task format:backend     # Python フォーマット (ruff)
task format:frontend    # TypeScript フォーマット (Prettier)

# Docker
task docker:up          # コンテナ起動
task docker:down        # コンテナ停止
task docker:logs        # ログ表示

# OpenAPI
task openapi:generate   # TypeScript型生成
```

## 個別コマンド

### Backend (Python/uv)
```bash
cd backend
uv sync                 # 依存関係インストール
uv run pytest           # テスト実行
uv run ruff check .     # リント
uv run ruff format .    # フォーマット
uv run mypy .           # 型チェック
uv run uvicorn app.main:app --reload  # 開発サーバー
```

### Frontend (Node/npm)
```bash
cd frontend
npm install             # 依存関係インストール
npm run dev             # 開発サーバー (Next.js)
npm run build           # ビルド
npm test                # テスト (vitest)
npm run lint            # ESLint
npm run format          # Prettier
npm run storybook       # Storybook起動
```

### Docker Compose
```bash
docker-compose up -d    # バックグラウンド起動
docker-compose down     # 停止
docker-compose logs -f  # ログフォロー
```
