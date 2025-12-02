# Code Style Guide

## Python (Backend)

### 命名規則
- **変数・関数**: `snake_case`
- **クラス**: `PascalCase`
- **定数**: `UPPER_SNAKE_CASE`
- **プライベート**: `_leading_underscore`

### コーディング規約
- 型ヒント必須（全ての関数引数・戻り値）
- docstring必須（Google style）
- 行の最大長: 88文字 (ruff default)
- インポート順: 標準ライブラリ → サードパーティ → ローカル

### ツール設定
- **ruff**: リンター + フォーマッター
- **mypy**: 型チェック (strict mode)
- 設定ファイル: `pyproject.toml`

## TypeScript (Frontend)

### 命名規則
- **変数・関数**: `camelCase`
- **クラス・型・インターフェース**: `PascalCase`
- **定数**: `UPPER_SNAKE_CASE` または `camelCase`
- **コンポーネント**: `PascalCase`

### コーディング規約
- strict mode有効
- 明示的な型注釈を推奨
- `any`使用禁止
- `null`より`undefined`を優先

### ツール設定
- **ESLint**: リンター
- **Prettier**: フォーマッター
- 設定ファイル: `eslint.config.mjs`, `.prettierrc`

## ファイル構成パターン

### React コンポーネント
```
components/
└── Button/
    ├── Button.tsx           # メインコンポーネント
    ├── Button.test.tsx      # テスト
    ├── Button.stories.tsx   # Storybook
    └── index.ts             # re-export
```

### Python モジュール
```
module/
├── __init__.py
├── models.py        # Pydantic/SQLAlchemy モデル
├── schemas.py       # API スキーマ
├── service.py       # ビジネスロジック
├── router.py        # FastAPI ルーター
└── tests/
    └── test_service.py
```
