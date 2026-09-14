#!/bin/zsh
# UserPromptSubmit hook: 修正/否定/訂正パターンを検出したら lessons.md 更新指示を割り込ませる。
# マッチしない場合は完全無音(stdout 何も出力しない=コンテキスト汚染ゼロ)。
set -u

INPUT=$(cat)
PROMPT=$(printf '%s' "$INPUT" | python3 -c 'import json,sys;print(json.load(sys.stdin).get("prompt",""))')

PROJ="${CLAUDE_PROJECT_DIR:-$PWD}"
LESSONS="$PROJ/tasks/lessons.md"

# 日本語/英語の修正シグナル両対応(誤検知許容、拾い漏れ低減方針)
PATTERN='違う|ちが(う|って)|間違(い|って)|誤り|直して|修正して|やり直|そうじゃ|そうではな|だめ|ダメ|逆だ|惜しい|おしい|wrong|incorrect|mistake|fix\s+(this|that|it)|redo|that[’'"'"']?s\s+not|not\s+what|undo|revert|please\s+correct'

if printf '%s' "$PROMPT" | grep -iqE "$PATTERN"; then
  cat <<EOF
[自己改善ループ・割り込み] ユーザー発話に修正シグナルを検出した。応答後、必ず以下を実行すること:
1. ${LESSONS} が存在しなければ tasks/ ごと作成し、初期テンプレート(状況/ミス/原因/再発防止ルール/関連ファイルの5項目)を書く
2. 今回の修正パターン・原因・再発防止ルールを 1 エントリ追記する(命令形・抽象化・検証可能性を意識)
3. 追記内容を最終応答末尾に「### 教訓の記録」として要約報告する
これは ~/.agents/instructions.md「3. 自己改善ループ」「タスク管理 6.」に基づく強制リマインダである。
EOF
fi
exit 0
