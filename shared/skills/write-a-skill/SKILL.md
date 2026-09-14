---
name: write-a-skill
description: 新しい AI エージェント共通スキル（SKILL.md ＋補助ファイル）を雛形から対話で起草・生成するスキル。Use when ユーザーが新規スキルを作りたいとき、または繰り返す手順・チェックリストをスキル化したいとき。
allowed-tools: Bash(bash:*), Read, Write
---

## Context

- 既存スキル名一覧（新規名の衝突回避用。リポジトリ `shared/skills/` と個人 `~/.agents/skills/` の両方）: `bash "$HOME/.agents/skills/write-a-skill/scripts/check-context.sh"` を実行して取得する

## Additional resources

- 生成する SKILL.md の雛形は [template.md](template.md) を参照する（`<...>` を埋め、HTML コメントは最終成果物から削除する）
- スキル配置の流儀は既存の `shared/skills/create-issue/`・`shared/skills/git-commit/` が手本になる

### エージェントごとの形式

共通スキルは `name` と `description` を必須とし、補助スクリプトを明示的に実行する。
以下の追加フィールド・変数・読み込み方法は Claude Code 専用。Codex 向けに使う場合は公式仕様を確認し、モデル・権限は Codex の設定で管理する。

### Claude Code の追加フィールド

- `name`（共通スキルでは必須）: 表示名。kebab-case にし、ディレクトリ名と一致させる
- `description`（推奨）: 「何をする」＋「いつ使う（when use）」。`when_to_use` との合算が **1,536 文字で切り捨て**られるため、要点とトリガー語を前方に置く
- `when_to_use`（任意）: トリガー語や例示。`description` に追記される形で扱われ、同じ 1,536 文字制限の対象
- `allowed-tools` / `disallowed-tools`（任意）: スペース or カンマ区切り。許可なしで使わせたい／使わせたくないツール
- `disable-model-invocation: true`（任意）: 自動起動を止め `/name` 手動起動のみにする
- `user-invocable: false`（任意）: `/` メニューから隠す（背景知識用）
- `model` / `effort`（任意）: 省略でセッション継承
- `${CLAUDE_SKILL_DIR}`: スキル同梱ファイル（scripts・template）参照に使う。カレントディレクトリに依存しない
- スキルは `skills/<name>/SKILL.md` が必須。補助は `REFERENCE.md`（テンプレ）・`examples.md`（具体例）・`scripts/check-context.sh`（先回り収集）を任意で添える
- 追加ディレクトリからのスキル読込は `--add-dir` / `/add-dir` のみ対象。`permissions.additionalDirectories` 設定は対象外

## Task

スキルの価値は「曖昧な手順を、誰が起動しても一貫した品質で実行できる形」に固めることにある。
雛形を埋めるだけの作業に矮小化せず、目的・トリガー・守るべき制約まで言語化して引き上げるのがこのスキルの仕事である。

1. スキルの目的・トリガー語・起動方式（自動＋手動か、手動のみか）を把握する
   - `$ARGUMENTS` や直近の会話・作業文脈を主材料にする
   - 目的やトリガーが埋められない場合のみ `利用可能な質問ツール` で不足だけを補完する（全部を訊き直さない）

2. スキル名を決める
   - kebab-case にする
   - 収集済みの既存スキル名一覧と衝突しないか確認する。衝突する場合は別名を提案する

3. **生成先をユーザーに確認する**（`利用可能な質問ツール`）
   - このリポジトリの `shared/skills/`（`install.sh` で両エージェントへリンクされる）
   - 個人 `~/.agents/skills/`（全プロジェクト横断で使える）

4. [template.md](template.md) を雛形に `SKILL.md` を起草する
   - `description` は「何をする＋いつ使う（when use）」を先頭に、トリガー語を前方へ（1,536 文字制限を意識）
   - 手動のみにしたい場合は `disable-model-invocation: true` を付ける
   - 不要な任意フィールドは行ごと削除し、空欄を残さない
   - 本文は簡潔にまとめ、`SKILL.md` 全体を **100 行以内** に収める。冗長な説明や長いテンプレートは補助ファイル（`REFERENCE.md` 等）へ逃がす

5. `## Task`（workflow）を `1. 2. 3. …` の番号付きで簡潔に書く
   - 各ステップは一文。破壊的・外向きの操作やファイル生成の前にはユーザー承認ステップを挟む

6. 補助ファイルが要るか判断し、要れば併せて起草する
   - 長いテンプレート → `REFERENCE.md` ／ 分類などの具体例 → `examples.md` ／ 起動時の先回り収集 → `scripts/check-context.sh`（`set +e`／常に `exit 0`）

7. 起草したドラフト（ディレクトリ構成＋各ファイル本文）をユーザーに提示し、承認を得る
   - **承認を得るまでファイルを生成しない**

8. 承認後、`Write` で `<生成先>/<skill-name>/SKILL.md`（＋補助ファイル）を作成する

9. 生成パスと、Claude Code の `/<skill-name>`、Codex の `$<skill-name>` での呼び出し方をユーザーに案内する
   - トップレベル `skills/` 等の既存ディレクトリ配下なら当該セッション内で即時認識される。新規トップレベルディレクトリを作った場合は再起動が必要な旨を添える

## 規約

- 機密情報（`.env` の値・API キー・トークン・認証情報）を SKILL.md や補助ファイルに含めない
- 承認を得るまでファイルを生成しない
- `name` は kebab-case にし、ディレクトリ名と一致させる
- 生成する `SKILL.md` は 100 行以内に収める（超える分は補助ファイルへ分離する）
- `description` には「いつ使うか（when use）」とトリガー語を必ず含め、前方に置く
- 雛形の `<...>` プレースホルダや説明用 HTML コメントを成果物に残さない

## User Input

$ARGUMENTS
