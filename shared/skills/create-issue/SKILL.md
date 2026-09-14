---
name: create-issue
description: GitHub のイシューを作成するスキル。会話・作業文脈やユーザーの簡潔な一言から、「背景→現状→やりたいこと→受け入れ基準」の単一テンプレートでイシュー本文を起草し、ドラフトを提示して承認を得てから gh issue create で起票する。「イシューを作って」「issue 化して」「これをチケットにして」「起票して」「バグを報告したい」「TODO を issue にまとめて」「issue 立てて」など、GitHub のイシュー/チケット/起票に関わる依頼では明示の指示が無くても必ずこのスキルを使うこと。なお本スキルは issue 専用であり、PR 作成は create-draft-pr、コミットは git-commit に委ねる（混同しないこと）。
allowed-tools: Bash(bash:*), Bash(git remote:*), Bash(git branch:*), Bash(gh repo view:*), Bash(gh issue create:*), Bash(gh issue list:*), Bash(gh label list:*)
model: haiku
---

## Context

- 収集情報（起票先リポジトリ・現在のブランチ・issue テンプレート有無と本文）: `bash "$HOME/.agents/skills/create-issue/scripts/check-context.sh"` を実行して取得する

## Additional resources

- 本文テンプレートは [REFERENCE.md](REFERENCE.md) を参照してください
- タイトルの prefix 規約は [git-guideline.md](~/.agents/rules/git-guideline.md) を参照してください

## Task

イシューは「誰かが後で読んで動ける」ことが価値の源泉です。書いた本人にしか分からない一言メモではなく、
背景・現状・狙い・完了条件が揃った状態まで引き上げることがこのスキルの仕事です。

1. 起票先リポジトリ(nameWithOwner)をユーザーに明示し、ここで合っているか確認する
   - 別リポジトリへ起票したい場合は `--repo [owner/name]` を後続コマンドに付ける

2. issue テンプレートの有無を確認する
   - 収集情報の「issue テンプレート」を参照する（`.github/ISSUE_TEMPLATE/` 配下や `.github/ISSUE_TEMPLATE.md`）
   - 「あり」の場合は同梱されたテンプレート本文の構造を優先して採用する
   - 「なし」の場合は [REFERENCE.md](REFERENCE.md) のテンプレートに従う

3. 入力源を統合してタイトルと本文を起草する
   - `$ARGUMENTS` があればそれを主軸に、無ければ直近の会話・作業文脈（調査結果・発見したバグ・決定事項）を要約して素材にする
   - 本文は前ステップで決めたテンプレート構造に必ず従う。該当が無いセクションは「特になし」と明記し、勝手に省略しない
   - 素材が薄く「現状」や「受け入れ基準」が埋められない場合は、利用可能な質問ツール で不足だけを補完質問する。
     全部を訊き直すのではなく、テンプレートの空欄を埋めるために本当に足りない情報に絞ること
   - タイトルは git-guideline の prefix（`feat:` / `fix:` / `docs:` / `refactor:` / `chore:` など）を内容から推論して付け、
     prefix 以降は日本語で簡潔に書く。本文はすべて日本語

4. 既存ラベルを `gh label list` で確認し、内容に合うものがあれば候補として提示する
   - リポジトリに存在しないラベルは指定しない（`gh issue create` が失敗するため）。該当が無ければラベル無しでよい

5. 起草したドラフト（タイトル + 本文 + ラベル候補）をユーザーに提示し、承認を得る
   - **承認を得るまで `gh issue create` を実行しないこと**。確認を挟むのがこのスキルの約束である
   - 修正要望があれば反映して再提示する

6. 承認後にイシューを作成する
   - 作成コマンド: `gh issue create --title "[title]" --body "[body]"` （ラベルがあれば `--label "[label]"` を付与）

7. 作成後にイシューの URL を表示する

## 規約

- 機密情報（`.env` の値、API キー、トークン、認証情報）を本文・タイトルに含めない
- 承認を得るまで `gh issue create` を実行しない
- タイトルの prefix 以外は日本語で記述する

## User Input

$ARGUMENTS
