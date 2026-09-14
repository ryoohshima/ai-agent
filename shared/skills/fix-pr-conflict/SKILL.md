---
name: fix-pr-conflict
description: PR のコンフリクトを base ブランチ取り込み→解消→push→CI 確認まで自律的に完遂する。Use when PR がコンフリクトしている・マージできないとき。トリガー語は「pr conflict」「コンフリクト修正して」「fix conflict」「#NN がコンフリクト」「/fix-pr-conflict」。
allowed-tools: Bash(git fetch:*), Bash(git status:*), Bash(git log:*), Bash(git diff:*), Bash(gh pr:*)
---

## Context

- 収集情報: `bash "$HOME/.agents/skills/fix-pr-conflict/scripts/check-context.sh"` を実行して取得する

## Additional resources

- 共通ルールは [git ガイドライン](~/.agents/rules/git-guideline.md) を参照

## Task（workflow）

1. 対象 PR を特定する（引数の PR 番号/URL、無ければカレントブランチの PR を `gh pr view` で特定）。
2. `git fetch origin` 後、`git log --oneline --left-right origin/<base>...HEAD` で分岐と重複コミットを確認する。
3. `git diff --name-only` で base 側と自ブランチ側の変更ファイルを比較し、「自ブランチが上位集合か」を判定してから解消方針を決める。
4. base を merge で取り込み、機能の意図を優先してコンフリクトを解消する（機械的な一括 ours/theirs は行わない）。
5. add/add 非対称（HEAD で追加→削除、base で追加維持）はマーカー無しで復活するため、マージ後に `git status` の `A` を必ず点検する。
6. 解消コミットを作成して push する（通常 push は自律実行）。
7. `gh pr checks` で CI を確認し、失敗があれば修正→再 push まで完遂する。
8. 最終状態（mergeable になったか・CI 結果・解消内容の要約）を報告する。

## 規約

- main/develop へ直接コミットしない。解消は PR ブランチ上でのみ行う。
- force push は明示承認なしに行わない（merge 取り込みを既定とし、rebase は事前確認）。
- 本番影響のある設定ファイル（権限・scope・デプロイ設定）のコンフリクトは自動解消せず、差分を提示して判断を仰ぐ。
- 未検証のまま「解消完了」と報告しない（push 結果と CI 状態を確認してから報告）。

## User Input

$ARGUMENTS
