---
name: create-draft-pr
description: 実装差分を検知して PR 作成を実行するスキル
allowed-tools: Bash(git remote:*), Bash(git status), Bash(git diff:*), Bash(git push -u origin:*), Bash(git log:*), Bash(gh pr:*), Bash(gh repo:*), Bash(bash:*)
model: haiku
---

## Context

- 収集情報（デフォルトブランチ・git ステータス・PR テンプレート有無と本文）: `bash "$HOME/.agents/skills/create-draft-pr/scripts/check-context.sh"` を実行して取得する

## Additional resources

- Git 規約は [git-guideline.md](~/.agents/rules/git-guideline.md) を参照してください

## Task

1. デフォルトブランチと現在のブランチの変更差分を確認する
   - 確認コマンド: `git diff [default branch]...`
   - コミットログの確認コマンド: `git log --oneline [default branch]..HEAD`

2. 現在のブランチを確認する。以下のブランチの場合は必ず別のブランチを作成する。ブランチ作成の際にはデフォルトブランチと現在のブランチの差分を元に規約に沿った適切な命名をする
   - master, main, develop

3. git ステータスを確認する。もしコミットされていないファイルが存在している場合は この Skills の終了と Skills: git-commit の利用をユーザーにレコメンドする

4. 必要な差分がすべて commit されていることを確認したら push する
   - push コマンド: `git push -u origin [branch name]`

5. PR テンプレートの有無を確認する
   - 収集情報の「PR テンプレート」を参照する（`.github/PULL_REQUEST_TEMPLATE.md` 等）
   - 「あり」の場合は同梱されたテンプレート本文の構造に沿って本文を組み立てる
   - 「なし」の場合は変更差分から本文を構成する

6. 変更差分とテンプレート方針を元にタイトルと本文を考え、ドラフト PR を作成する
   - PR作成コマンド: `gh pr create --draft  --title "[title]"  --body "[description]"`

7. PR 作成後に PR の URL を表示する

## User Input

$ARGUMENTS
