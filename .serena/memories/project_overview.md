# Project Overview

## プロジェクト名
Agent Platform (AI Agent Demo)

## 目的
マルチユーザー対応AIエージェントプラットフォームの構築

## 主要機能
- **エージェント作成・管理**: ユーザーがカスタムAIエージェントを作成・設定
- **A2A連携**: Google A2A (Agent-to-Agent) プロトコルによるエージェント間通信
- **LLM統合**: LiteLLMを通じた複数LLMプロバイダー対応（Claude, OpenAI, Bedrock）
- **認証・マルチテナント**: Supabase Authによるユーザー認証とテナント分離

## アーキテクチャ概要
- フロントエンド: Next.js SPA
- バックエンド: FastAPI REST API
- データベース: PostgreSQL (Supabase)
- 外部連携: LiteLLM, A2A Protocol

## リポジトリ構成
```
ai-agent-demo/
├── backend/          # Python/FastAPI バックエンド
├── frontend/         # Next.js フロントエンド
├── openapi/          # OpenAPI スキーマ定義
└── docs/             # ドキュメント（PLANNING.md含む）
```
