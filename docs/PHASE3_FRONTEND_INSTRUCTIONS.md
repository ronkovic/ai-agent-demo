# Phase 3: フロントエンドUI 実装指示書

## プロジェクト概要

マルチユーザー対応AIエージェントプラットフォームのフロントエンド実装。ユーザーは複数のAIエージェントを作成し、チャットで対話できる。

## 技術スタック

| 項目 | 技術 |
|------|------|
| フレームワーク | Next.js 15 (App Router) |
| 言語 | TypeScript 5.x |
| UIライブラリ | shadcn/ui (Radix UI + Tailwind CSS) |
| コンポーネントカタログ | Storybook 8 |
| API通信 | openapi-typescript-codegen 生成クライアント |
| テスト | Vitest |
| パッケージマネージャ | npm |

## プロジェクト構造

```
frontend/
├── src/
│   ├── app/                      # Next.js App Router
│   │   ├── layout.tsx            # ルートレイアウト
│   │   ├── page.tsx              # ダッシュボード (/)
│   │   ├── agents/
│   │   │   ├── page.tsx          # エージェント一覧
│   │   │   ├── new/page.tsx      # 新規作成
│   │   │   └── [id]/
│   │   │       ├── page.tsx      # チャット画面
│   │   │       └── settings/page.tsx  # 設定
│   │   └── globals.css
│   ├── components/
│   │   ├── ui/                   # shadcn/ui コンポーネント (既存)
│   │   ├── chat/                 # チャット関連 (新規作成)
│   │   ├── agent/                # エージェント関連 (新規作成)
│   │   └── layout/               # レイアウト関連 (新規作成)
│   ├── lib/
│   │   ├── api-client/           # OpenAPI生成クライアント (既存)
│   │   │   ├── types.gen.ts      # 型定義
│   │   │   └── sdk.gen.ts        # APIクライアント
│   │   └── utils.ts
│   └── hooks/                    # カスタムフック (新規作成)
├── .storybook/                   # Storybook設定 (既存)
└── package.json
```

---

## 利用可能なAPI

### エージェント管理

| メソッド | エンドポイント | 説明 |
|---------|---------------|------|
| GET | `/api/agents` | エージェント一覧取得 |
| POST | `/api/agents` | エージェント作成 |
| GET | `/api/agents/{agent_id}` | エージェント詳細取得 |
| PATCH | `/api/agents/{agent_id}` | エージェント更新 |
| DELETE | `/api/agents/{agent_id}` | エージェント削除 |

### 会話管理

| メソッド | エンドポイント | 説明 |
|---------|---------------|------|
| GET | `/api/chat/conversations` | 会話一覧取得 |
| POST | `/api/chat/conversations` | 会話作成 |
| GET | `/api/chat/conversations/{id}` | 会話詳細取得 |
| GET | `/api/chat/conversations/{id}/messages` | メッセージ一覧取得 |

### チャット

| メソッド | エンドポイント | 説明 |
|---------|---------------|------|
| POST | `/api/chat/` | チャット送信 (非ストリーミング) |
| POST | `/api/chat/stream` | チャット送信 (SSEストリーミング) |

### 型定義 (参照: `src/lib/api-client/types.gen.ts`)

```typescript
// エージェント作成
interface AgentCreate {
  name: string;
  description?: string | null;
  system_prompt: string;
  llm_provider: string;  // "claude" | "openai" | "bedrock"
  llm_model: string;
  tools?: string[];
  a2a_enabled?: boolean;
}

// エージェントレスポンス
interface AgentResponse {
  id: string;
  user_id: string;
  name: string;
  description: string | null;
  system_prompt: string;
  llm_provider: string;
  llm_model: string;
  tools: string[];
  a2a_enabled: boolean;
  created_at: string;
  updated_at: string;
}

// チャットリクエスト
interface ChatRequest {
  agent_id: string;
  conversation_id?: string | null;
  message: string;
}

// チャットレスポンス
interface ChatResponse {
  conversation_id: string;
  message_id: string;
  content: string;
  role: string;
}
```

---

## 実装タスク

### Task 1: レイアウトコンポーネント

#### 1.1 Sidebar コンポーネント
**ファイル:** `src/components/layout/Sidebar.tsx`

```typescript
interface SidebarProps {
  agents: AgentResponse[];
  selectedAgentId?: string;
  onSelectAgent: (id: string) => void;
  onCreateNew: () => void;
}
```

**要件:**
- エージェント一覧を表示
- 選択中のエージェントをハイライト
- 「新規作成」ボタン
- レスポンシブ対応 (モバイルでは折りたたみ)

**Storybook:** `Sidebar.stories.tsx`
- Default: エージェント3件表示
- Empty: エージェントなし
- Selected: 選択状態

#### 1.2 Header コンポーネント
**ファイル:** `src/components/layout/Header.tsx`

```typescript
interface HeaderProps {
  title?: string;
  showBackButton?: boolean;
  onBack?: () => void;
}
```

---

### Task 2: チャットコンポーネント

#### 2.1 ChatMessage コンポーネント
**ファイル:** `src/components/chat/ChatMessage.tsx`

```typescript
interface ChatMessageProps {
  role: "user" | "assistant";
  content: string;
  timestamp?: string;
  isStreaming?: boolean;
}
```

**要件:**
- ユーザーメッセージは右寄せ、青背景
- アシスタントメッセージは左寄せ、グレー背景
- Markdownレンダリング対応 (react-markdown)
- コードブロックはシンタックスハイライト
- ストリーミング中はタイピングインジケーター表示

**Storybook:** `ChatMessage.stories.tsx`
- UserMessage: ユーザーメッセージ
- AssistantMessage: アシスタントメッセージ
- WithCode: コードブロック含む
- Streaming: ストリーミング中

#### 2.2 ChatInput コンポーネント
**ファイル:** `src/components/chat/ChatInput.tsx`

```typescript
interface ChatInputProps {
  onSend: (message: string) => void;
  disabled?: boolean;
  placeholder?: string;
}
```

**要件:**
- テキストエリア (複数行対応)
- Enter送信 (Shift+Enterで改行)
- 送信ボタン
- 送信中は無効化

**Storybook:** `ChatInput.stories.tsx`
- Default: 通常状態
- Disabled: 無効状態
- WithText: テキスト入力済み

#### 2.3 ChatContainer コンポーネント
**ファイル:** `src/components/chat/ChatContainer.tsx`

```typescript
interface ChatContainerProps {
  messages: Array<{role: string; content: string; id: string}>;
  onSendMessage: (message: string) => void;
  isLoading?: boolean;
}
```

**要件:**
- メッセージ一覧をスクロール表示
- 新規メッセージ時に自動スクロール
- ローディング状態表示

---

### Task 3: エージェント管理コンポーネント

#### 3.1 AgentCard コンポーネント
**ファイル:** `src/components/agent/AgentCard.tsx`

```typescript
interface AgentCardProps {
  agent: AgentResponse;
  onClick?: () => void;
  onEdit?: () => void;
  onDelete?: () => void;
}
```

**要件:**
- エージェント名、説明、LLMプロバイダー表示
- クリックでチャット画面へ
- 編集・削除ボタン (ドロップダウンメニュー)

**Storybook:** `AgentCard.stories.tsx`
- Default: 通常表示
- WithDescription: 説明あり
- Claude/OpenAI: プロバイダー別

#### 3.2 AgentForm コンポーネント
**ファイル:** `src/components/agent/AgentForm.tsx`

```typescript
interface AgentFormProps {
  initialData?: Partial<AgentCreate>;
  onSubmit: (data: AgentCreate) => void;
  onCancel: () => void;
  isLoading?: boolean;
}
```

**要件:**
- 名前 (必須)
- 説明 (任意)
- システムプロンプト (必須、複数行)
- LLMプロバイダー選択 (claude/openai/bedrock)
- LLMモデル選択 (プロバイダーに応じて変更)
- バリデーション (react-hook-form + zod)

**LLMモデル選択肢:**
```typescript
const LLM_MODELS = {
  claude: [
    { value: "claude-3-5-sonnet-20241022", label: "Claude 3.5 Sonnet" },
    { value: "claude-3-opus-20240229", label: "Claude 3 Opus" },
    { value: "claude-3-haiku-20240307", label: "Claude 3 Haiku" },
  ],
  openai: [
    { value: "gpt-4o", label: "GPT-4o" },
    { value: "gpt-4-turbo", label: "GPT-4 Turbo" },
    { value: "gpt-3.5-turbo", label: "GPT-3.5 Turbo" },
  ],
  bedrock: [
    { value: "anthropic.claude-3-5-sonnet-20241022-v2:0", label: "Claude 3.5 Sonnet (Bedrock)" },
    { value: "anthropic.claude-3-haiku-20240307-v1:0", label: "Claude 3 Haiku (Bedrock)" },
  ],
};
```

**Storybook:** `AgentForm.stories.tsx`
- Create: 新規作成モード
- Edit: 編集モード (初期データあり)
- Loading: 送信中

---

### Task 4: カスタムフック

#### 4.1 useAgents
**ファイル:** `src/hooks/useAgents.ts`

```typescript
function useAgents() {
  return {
    agents: AgentResponse[],
    isLoading: boolean,
    error: Error | null,
    createAgent: (data: AgentCreate) => Promise<AgentResponse>,
    updateAgent: (id: string, data: AgentUpdate) => Promise<AgentResponse>,
    deleteAgent: (id: string) => Promise<void>,
    refetch: () => void,
  }
}
```

#### 4.2 useChat
**ファイル:** `src/hooks/useChat.ts`

```typescript
function useChat(agentId: string, conversationId?: string) {
  return {
    messages: Message[],
    isLoading: boolean,
    isStreaming: boolean,
    sendMessage: (content: string) => Promise<void>,
    conversationId: string | null,
  }
}
```

**SSEストリーミング実装:**
```typescript
const sendMessageWithStream = async (content: string) => {
  const response = await fetch('/api/chat/stream', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      agent_id: agentId,
      conversation_id: conversationId,
      message: content,
    }),
  });

  const reader = response.body?.getReader();
  const decoder = new TextDecoder();

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;

    const chunk = decoder.decode(value);
    // SSEイベントをパース
    const lines = chunk.split('\n');
    for (const line of lines) {
      if (line.startsWith('data: ')) {
        const data = JSON.parse(line.slice(6));
        // メッセージを更新
      }
    }
  }
};
```

---

### Task 5: ページ実装

#### 5.1 ダッシュボード (/)
**ファイル:** `src/app/page.tsx`

- エージェント一覧をカード形式で表示
- 「新規エージェント作成」ボタン
- 空状態の表示

#### 5.2 エージェント一覧 (/agents)
**ファイル:** `src/app/agents/page.tsx`

- エージェント一覧 (グリッド表示)
- 検索・フィルター機能

#### 5.3 エージェント作成 (/agents/new)
**ファイル:** `src/app/agents/new/page.tsx`

- AgentFormを使用
- 作成成功後、チャット画面へリダイレクト

#### 5.4 チャット画面 (/agents/[id])
**ファイル:** `src/app/agents/[id]/page.tsx`

- サイドバー: 会話履歴一覧
- メイン: ChatContainer
- SSEストリーミング対応

#### 5.5 エージェント設定 (/agents/[id]/settings)
**ファイル:** `src/app/agents/[id]/settings/page.tsx`

- AgentFormを編集モードで使用
- 削除ボタン (確認ダイアログ付き)

---

## デザインガイドライン

### カラーパレット (Tailwind CSS)

```css
/* プライマリ */
--primary: hsl(222.2 47.4% 11.2%);

/* アクセント */
--accent: hsl(210 40% 96.1%);

/* メッセージ背景 */
--user-message: hsl(217 91% 60%);      /* blue-500 */
--assistant-message: hsl(220 14% 96%);  /* gray-100 */
```

### スペーシング

- コンポーネント間: `gap-4` (16px)
- セクション間: `gap-8` (32px)
- パディング: `p-4` (16px)

### レスポンシブブレークポイント

- Mobile: < 768px
- Tablet: 768px - 1024px
- Desktop: > 1024px

---

## 開発コマンド

```bash
# 開発サーバー起動
npm run dev

# Storybook起動
npm run storybook

# 型チェック
npm run typecheck

# リント
npm run lint

# テスト
npm run test

# API型再生成 (バックエンドOpenAPI変更時)
npm run generate-api
```

---

## 注意事項

1. **既存コードの確認**
   - `src/components/ui/` には shadcn/ui コンポーネントが既にインストール済み
   - `src/lib/api-client/` にはOpenAPI生成クライアントが存在

2. **Storybook必須**
   - 各コンポーネントには必ず `.stories.tsx` ファイルを作成
   - 主要なバリエーションをカバー

3. **型安全性**
   - `any` 型の使用禁止
   - API型は `types.gen.ts` からインポート

4. **エラーハンドリング**
   - API呼び出しには try-catch を使用
   - ユーザーフレンドリーなエラーメッセージ表示

5. **アクセシビリティ**
   - 適切な aria-label の設定
   - キーボードナビゲーション対応

---

## 実装順序

1. レイアウトコンポーネント (Sidebar, Header)
2. チャットコンポーネント (ChatMessage, ChatInput, ChatContainer)
3. エージェントコンポーネント (AgentCard, AgentForm)
4. カスタムフック (useAgents, useChat)
5. ページ統合 (各ページの実装)
6. Storybook整備

---

## バックエンドAPI接続設定

開発環境では、Next.js の `next.config.ts` でプロキシ設定が必要:

```typescript
// next.config.ts
const nextConfig = {
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: 'http://localhost:8000/api/:path*',
      },
    ];
  },
};
```

---

## 参考リソース

- [Next.js App Router](https://nextjs.org/docs/app)
- [shadcn/ui](https://ui.shadcn.com/)
- [Storybook](https://storybook.js.org/docs)
- [Tailwind CSS](https://tailwindcss.com/docs)
- [React Hook Form](https://react-hook-form.com/)
- [Zod](https://zod.dev/)
