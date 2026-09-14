---
name: git-commit
allowed-tools: Bash(bash:*), Bash(git branch:*), Bash(git status:*), Bash(git log:*), Bash(git diff:*), Bash(git add:*), Bash(git commit:*)
description: 変更をチェックして内容ごとに細かくコミットする
model: haiku
---

## コンテキスト

最初に以下の補助スクリプトを実行して収集し、分析へ進めること。
俯瞰情報（状態・stat・log）→ 詳細差分の順に並べてある。

- 収集情報（ブランチ・状態・stat・ステージ/未ステージ差分・直近 log）: `bash "$HOME/.agents/skills/git-commit/scripts/check-context.sh"` を実行して取得する

`git diff` は新規（追跡外）ファイルを映さないため、`git status --short` に出た未追跡ファイルは中身を別途 `git diff --no-index /dev/null [file]` 等で確認してから分類する。

## Additional resources

- Git 規約は [git-guideline.md](~/.agents/rules/git-guideline.md) を参照してください
- 分類の具体例は [examples.md](examples.md) を参照してください

## Task

1. 現在のブランチを確認する。以下のブランチの場合は必ず別のブランチを作成する。その際にブランチ元が現在のブランチのままで問題ないかユーザーに確認する
   - master
   - main
   - develop

2. 収集済みの状態・stat・差分を使い、追跡外ファイルも含めて全体の変更を分析し、論理的なグループに分類する
   - 機能追加、バグ修正、リファクタリングなど種類ごと
   - 関連するファイル同士でグループ化
   - 独立した変更は別コミットに
   - 直近コミットの log を見て、既存の prefix・書式・粒度に揃える

3. 各グループごとに以下を繰り返す：
   - 該当ファイルのみをステージング: `git add [file]`
   - 適切なコミットメッセージを生成
   - コミット実行: `git commit -m [commit message]`

4. 完了後、作成したコミット一覧を表示

5. Skills: create-draft-pr の使用をユーザーにレコメンドする

## 規約

- `.env` や認証情報を含むファイルはコミットしない
- commit は可能な限り細かく、1コミットに対して1つの関連する変更になるようにする
- コミットメッセージは「How（どう変えたか）」に焦点を当てた簡潔なメッセージにする。What（何を）はコード自体で表現する
- コミットメッセージには prefix をつける
- ユーザーへの確認が必要な場面（ブランチ作成の可否、判断が割れる分類など）では 利用可能な質問ツール を使う

## User Input

$ARGUMENTS
