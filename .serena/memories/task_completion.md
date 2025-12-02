# Task Completion Checklist

コード変更後、以下を確認してください。

## 必須チェック

### 1. テスト実行
```bash
task test
```
- 全テストがパスすることを確認
- 新機能には対応するテストを追加

### 2. リント・フォーマット
```bash
task lint
task format
```
- リントエラーがないことを確認
- フォーマットが適用されていることを確認

### 3. 型チェック（含まれていない場合）
```bash
# Backend
cd backend && uv run mypy .

# Frontend
cd frontend && npm run type-check  # 設定されている場合
```

## Git コミット前

### PLANNING.md 更新確認
- `docs/PLANNING.md` が更新されているか確認
- 完了したタスクにチェックマークを追加
- Git commit hook が PLANNING.md のステージングを確認

**重要**: コミット時に PLANNING.md がステージングされていないとブロックされます。

```bash
# PLANNING.mdをステージング
git add docs/PLANNING.md

# その後コミット
git commit -m "メッセージ"
```

## ビルド確認（リリース前）

```bash
# Frontend
cd frontend && npm run build

# Docker
task docker:up
```

## Storybook 更新（UIコンポーネント変更時）

```bash
cd frontend && npm run storybook
```
- 新規コンポーネントには Story を追加
- 既存コンポーネントの Story が壊れていないか確認
