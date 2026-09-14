#!/bin/zsh
# SessionStart hook: プロジェクト cwd の tasks/lessons.md を要約してコンテキスト注入する。
# ファイルが無ければ「修正を受けたら作成せよ」案内のみを静かに出す。
set -u

PROJ="${CLAUDE_PROJECT_DIR:-$PWD}"
LESSONS="$PROJ/tasks/lessons.md"

emit_json() {
  local body="$1"
  printf '%s' "$body" | python3 -c '
import json,sys
ctx=sys.stdin.read()
print(json.dumps({
  "hookSpecificOutput":{
    "hookEventName":"SessionStart",
    "additionalContext":ctx
  }
}))'
}

if [[ ! -f "$LESSONS" ]]; then
  emit_json "[自己改善ループ] このプロジェクトには tasks/lessons.md がない。修正を受けた際は ${LESSONS} を新規作成し、教訓を記録すること。"
  exit 0
fi

HEADINGS=$(grep -E '^#{1,3} ' "$LESSONS" | head -40)
TAIL=$(tail -n 80 "$LESSONS")

SUMMARY="[自己改善ループ] ${LESSONS} の要約をコンテキストに注入する。

## 見出し一覧
${HEADINGS}

## 直近の教訓 (末尾80行)
${TAIL}

このセッション中、ユーザーから修正を受けたら必ず ${LESSONS} を更新すること。"

emit_json "$SUMMARY"
