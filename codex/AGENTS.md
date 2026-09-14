# Codex ユーザー設定

作業開始時に `~/.agents/instructions.md`、`~/.agents/rules/coding-guideline.md`、
`~/.agents/rules/git-guideline.md` を読み、共通のユーザー指示として適用する。
参照ファイルはシンボリックリンク先の最新内容を読む。

Claude Code 固有のモデル名・ツール名・frontmatter の権限指定は Codex の設定値として使わない。
共通スキルの `$ARGUMENTS` はユーザーの依頼内容として解釈し、補助スクリプトは明示的に実行する。
モデルと権限は Codex の現在の設定に従う。RTK による自動書き換えを前提にしない。
Claude 側と同様に `.env` の内容を読み取らない。必要な変数名は `.env.example` や設定コードで確認する。
