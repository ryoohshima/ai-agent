# ai-agent

Claude Code と Codex の個人設定を管理するリポジトリ。旧 `claude-code` の Git 履歴を継続しています。

```text
shared/
  instructions.md       日本語・人格・開発方針・CodeGraph の共通指示
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
  AGENTS.md             Codex の個人指示と必要時に読む共通ルール
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
- Codex の指示は `codex/AGENTS.md` を編集します。`~/.codex/AGENTS.md` のリンク経由で反映され、新しいセッションで読み込まれます。共通の `shared/instructions.md` は一括で読まず、開発・Git の共通ルールを必要時に読みます。
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

## Codex の security-guidance フック互換修正

`security-guidance` 2.0.8 の Claude 固有出力（`metrics` / `rewakeSummary`）を Codex 用に変換するパッチです。警告・続行判断は保持し、Claude での出力は変更しません。手元の Codex キャッシュには適用済みです。プラグインの更新・再インストールで上書きされる場合があるため、その際は再確認してください。以下は未適用の 2.0.8 に対して実行します。

```sh
patch --backup -p1 -d "$HOME/.codex/plugins/cache/claude-plugins-official/security-guidance/2.0.8" < codex/patches/security-guidance-2.0.8.patch
python3 test_hook_output.py "$HOME/.codex/plugins/cache/claude-plugins-official/security-guidance/2.0.8/hooks/security_reminder_hook.py"
```

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
