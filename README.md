# ai-agent

Claude Code と Codex の個人設定を管理するリポジトリ。旧 `claude-code` の Git 履歴を継続しています。

```text
shared/
  instructions.md       日本語・人格・開発方針・CodeGraph の共通指示
  rules/                コーディング・Git ガイドライン
  skills/               両エージェントで使うスキル
  hooks/                lessons.md の読み込み・更新リマインダー
  mcp-servers.json       認証情報を含まない MCP の初期定義
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

Python 3.11 以降が必要です。`~/.claude` と `~/.codex` は実ディレクトリとして使います。

```sh
./install.sh -n          # 変更内容の確認
./install.sh             # 設定を配置
python3 test_install.py   # 仮の HOME で検証
```

既存のファイル・同名スキルは `~/.local/state/ai-agent/install-<日時>/` へバックアップします。
旧構成の `~/.claude` 全体へのリンクは自動で上書きせず停止します。既存マシンは移行済みです。

## 編集と反映

- 共通指示・ルール・スキル・フックのスクリプトは `shared/` を編集します。リンク経由で両方に反映されます。指示は新しいセッションで読み直してください。
- Claude の設定は `claude/` を編集します。マシン固有の上書きは Git 管理外の `~/.claude/settings.local.json` に置きます。
- Codex のモデル・認証付き MCP・アプリ連携は `~/.codex/config.toml` に保持します。リポジトリの `codex/config.toml` と MCP 定義は未設定項目だけを補う初期値です。既存値の変更・削除はローカル設定で行います。
- `codex/hooks.json` はインストール時に既存フックへ重複なく追記します。定義を変更・削除した場合は `~/.codex/hooks.json` の古い定義も調整します。新しいフックは Codex CLI の `/hooks` で確認・信頼してください。既存の Orca / Superset 連携は保持します。
- 新しいスキル・ルール・フックスクリプトの追加後は `./install.sh` を再実行します。アプリ管理の `computer-use` / `orchestration` / `orca-cli` やプラグインは各アプリ側で管理します。

Codex は `~/.agents/skills/<name>`、Claude は `~/.claude/skills/<name>` から同じディレクトリを参照します。
Codex の旧 `~/.codex/skills` にある同名コピーはバックアップに退避し、二重読み込みを解消します。
Codex の既存インポート設定は保持しますが、共通ファイルの同期は上記リンクが担います。

## エージェント間の違い

- モデル名、権限、ステータスライン、プラグインは各エージェント固有です。Claude の設定ファイルをそのまま Codex へは渡しません。
- Codex はプロジェクトに `AGENTS.md` がなければ `CLAUDE.md` を読みます。両方ある場合は `AGENTS.md` が優先されます。
- Claude のコマンド deny/ask を Codex の `.rules` に移植しています。Codex のルールはサンドボックス外での実行を制御するもので、Claude の権限モデルと完全に同じではありません。`.env` の読み取り禁止は Codex の指示にも記載していますが、ファイルアクセス制御と同義ではありません。
- Codex に lessons のリマインダーと完了音を追加しています。Claude の Notification、RTK 自動書き換え、独自ステータスラインは Claude 側に残します。
- 共通スキルの補助スクリプトは明示実行に統一しています。Claude 専用 frontmatter のモデル・ツール指定は Codex に適用しません。

## ローカルデータと復元

認証情報、会話履歴、キャッシュ、プラグインの実体は `~/.claude` / `~/.codex` に置き、Git 管理しません。
2026-09-12 の構成変更前の設定は `~/.local/state/ai-agent/20260912-214708/` に保存しています。
設定を戻す場合は両アプリを終了し、対象のリンクを退避してバックアップの同名ファイルを戻してください。
実行データは `~/.claude` に保持されています。旧 `gitfiles/setup/claude-code` は既存の作業場所を保つため `ai-agent` への互換リンクを残しています。

## 公式仕様

- [共通スキルの配置とシンボリックリンク](https://learn.chatgpt.com/docs/build-skills)
- [AGENTS.md とフォールバック](https://learn.chatgpt.com/docs/agent-configuration/agents-md)
- [Codex フックの信頼確認](https://learn.chatgpt.com/docs/hooks)
- [Codex の実行ルール](https://learn.chatgpt.com/docs/agent-configuration/rules)
