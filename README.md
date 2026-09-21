# ai-agent

Claude Code と Codex の個人設定を管理するリポジトリ。旧 `claude-code` の Git 履歴を継続しています。

```text
shared/
  AGENTS.md             日本語・人格・開発方針・CodeGraph の共通指示
  rules/                コーディング・Git ガイドライン
  skills/               両エージェントで使うスキル
  hooks/                lessons.md の読み込み・更新リマインダー
  mcp-servers.json       認証情報を含まない MCP の同期元
claude/
  CLAUDE.md             共通指示の読み込みと Claude 固有指示
  settings.json         Claude の設定・権限・プラグイン・フック
  hooks/                Claude 固有の連携
  RTK.md / statusline.sh
codex/
  AGENTS.md             共通指示の読み込みと Codex 固有指示
  config.toml           Codex の初期設定
  hooks.json            Codex 用フックの追加定義
  rules/                Codex のコマンド実行ポリシー
install.sh / install.py
```

## セットアップ

Python 3.11 以降と `uv` が必要です。`install.sh` は `tomlkit` を隔離環境へ用意します。`~/.claude` と `~/.codex` は実ディレクトリとして使います。

```sh
./install.sh -n          # 変更内容の確認
./install.sh             # 設定を配置
uv run --no-project --with-requirements requirements.txt python3 test_install.py # 仮の HOME で検証
```

既存のファイル・同名スキルは `~/.local/state/ai-agent/install-<日時>/` へバックアップします。
旧構成の `~/.claude` 全体へのリンクは自動で上書きせず停止します。既存マシンは移行済みです。

## 編集と反映

- 共通指示・ルール・スキル・フックのスクリプトは `shared/` を編集します。リンク経由で両方に反映されます。指示は新しいセッションで読み直してください。
- Claude の設定は `claude/` を編集します。マシン固有の上書きは Git 管理外の `~/.claude/settings.local.json` に置きます。
- MCP は両エージェントとも `shared/mcp-servers.json` を正とし、`./install.sh` で同名サーバーの定義全体を上書きします。定義内で削除した項目も反映します。リポジトリにないサーバーは保持するため、サーバー自体を削除する場合はローカル設定からも削除します。認証情報はリポジトリに含めません。
- Codex のモデル・アプリ連携など MCP 以外の既存設定は保持します。`codex/config.toml` は未設定項目だけを補う初期値です。
- 共通の個人指示は `shared/AGENTS.md` を正本とし、Claude の `CLAUDE.md` と Codex の `AGENTS.md` が同じ `~/.agents/AGENTS.md` を読みます。各入口には固有指示だけを置き、開発・Git の詳細ルールは共通指示から必要時に読みます。変更は既存リンク経由で反映され、新しいセッションで読み込まれます。
- Claude は `@~/.agents/AGENTS.md` で共通指示を import し、その下に Claude 固有指示を置きます。`~/.agents/AGENTS.md` は自動探索に頼らず各入口から明示的に読み込みます。旧 `~/.agents/instructions.md` は既存の参照向けに同じ正本への互換リンクとして残します。既存環境でこの改名を取り込んだら、新しいセッションを開始する前に `./install.sh` を再実行してリンクを更新してください。
- 完了音は `codex/config.toml` の `notify` で設定します。既存の `notify` は保持します。
- `codex/hooks.json` はインストール時に既存フックへ重複なく追記します。定義を変更・削除した場合は `~/.codex/hooks.json` の古い定義も調整します。新しいフックは Codex CLI の `/hooks` で確認・信頼してください。既存の Orca / Superset 連携は保持します。
- 新しいスキル・ルール・フックスクリプトの追加後は `./install.sh` を再実行します。アプリ管理の `computer-use` / `orchestration` / `orca-cli` やプラグインは各アプリ側で管理します。
- `shared/` → `~/.agents/`、`claude/` → `~/.claude/`、`codex/` → `~/.codex/` の構造をたどり、ファイルを自動でリンクします。スキルは `SKILL.md` を含むディレクトリ単位、その他のディレクトリは既存ファイルと共存する個別リンクです。共通の `rules/`・`skills/`・`hooks/` は Claude にも配置します。通常のファイル追加で `install.py` の変更は不要です。この3ディレクトリには配置するファイルだけを置いてください。
- 隠しファイル・ディレクトリ、`*.bak`、`*~`、`__pycache__`、`*.pyc` は配置対象から除外します。例外はマージする `codex/config.toml`・`codex/hooks.json`、Claude への配置と両クライアントへの同期に使う `shared/mcp-servers.json`、旧指示パスへの互換リンクです。削除・改名したファイルの配置先リンクは自動削除しません。

Codex は `~/.agents/skills/<name>`、Claude は `~/.claude/skills/<name>` から同じディレクトリを参照します。
旧通知フックと `~/.codex/skills` の共通スキルの重複コピーは移行済みです。これらの移行処理はインストーラーから除去しています。
Codex の既存インポート設定は保持しますが、共通ファイルの同期は上記リンクが担います。

`write-a-skill` は標準の `skill-creator` に置き換え、`coding-standards` の必要な規約は `shared/rules/coding-guideline.md` に集約しました。インストーラーは廃止した2スキルの共有リンクをバックアップに退避します。個人作成の同名ディレクトリや無関係なリンクは保持します。

`skill-creator` は Codex 標準版を残し、重複する同期版は `~/.codex/config.toml` で無効化します。

Codex では旧 `sandbox-sdk` を無効化し、`sandbox-stable`・`sandbox-next`・`sandbox-migrate-to-next` を用途別に使います。文書系は公式プラグインを優先し、重複する同期版 `docx`・`pptx`・`xlsx`・`pdf` は `~/.codex/config.toml` の `[[skills.config]]` で各 `SKILL.md` の絶対パスを指定して `enabled = false` にします。同期先やプラグインキャッシュは直接編集しません。Ponytail・Orca は維持します。

## エージェント間の違い

- モデル名、権限、ステータスライン、プラグインは各エージェント固有です。Claude の設定ファイルをそのまま Codex へは渡しません。
- Codex はプロジェクトに `AGENTS.md` がなければ `CLAUDE.md` を読みます。両方ある場合は `AGENTS.md` が優先されます。
- Claude のコマンド deny/ask を Codex の `.rules` に移植しています。Codex のルールはサンドボックス外での実行を制御するもので、Claude の権限モデルと完全に同じではありません。`.env` の読み取り禁止は共通指示に記載していますが、ファイルアクセス制御と同義ではありません。
- Codex に lessons のリマインダーと `notify` による完了音（Bottle.aiff）を追加しています。Claude の Notification、RTK 自動書き換え、独自ステータスラインは Claude 側に残します。
- 共通スキルの補助スクリプトは明示実行に統一しています。Claude 専用 frontmatter のモデル・ツール指定は Codex に適用しません。

## Codex のセキュリティレビュー

監査は OpenAI 提供の Codex Security プラグインを優先し、重複するローカル `security-audit` は無効化します。

OpenAI 公式の `security-best-practices` を `~/.codex/skills/` に導入しています。Python・JavaScript/TypeScript・Go の安全な実装や明示的なレビュー依頼で使うスキルで、Claude の `security-guidance` の自動フックとは実行方式が異なります。新しい環境では Skill Installer に `openai/skills` の `skills/.curated/security-best-practices` を指定して導入してください。

## ローカルデータと復元

認証情報、会話履歴、キャッシュ、プラグインの実体は `~/.claude` / `~/.codex` に置き、Git 管理しません。
2026-09-12 の構成変更前の設定は `~/.local/state/ai-agent/20260912-214708/` に保存しています。
設定を戻す場合は両アプリを終了し、対象のリンクを退避してバックアップの同名ファイルを戻してください。
実行データは `~/.claude` に保持されています。旧 `gitfiles/setup/claude-code` は既存の作業場所を保つため `ai-agent` への互換リンクを残しています。

## 公式仕様

- [GPT-6 Astra 向けのスキル・指示の見直し](https://developers.openai.com/blog/rethinking-skills-and-prompts-for-gpt-6-astra)
- [共通スキルの配置とシンボリックリンク](https://learn.chatgpt.com/docs/build-skills)
- [AGENTS.md とフォールバック](https://learn.chatgpt.com/docs/agent-configuration/agents-md)
- [Codex フックの信頼確認](https://learn.chatgpt.com/docs/hooks)
- [Codex の実行ルール](https://learn.chatgpt.com/docs/agent-configuration/rules)
- [Claude の共通指示 import と固有指示](https://code.claude.com/docs/en/memory#share-one-file-with-other-coding-tools)
