#!/bin/bash
# fix-pr-conflict: 起動時に PR・分岐状況を先回り収集する（失敗しても常に exit 0）
set +e

echo "=== カレントブランチ ==="
git branch --show-current

echo "=== カレントブランチの PR ==="
gh pr view --json number,title,baseRefName,mergeable,url \
  --template '#{{.number}} {{.title}} (base: {{.baseRefName}}, mergeable: {{.mergeable}}) {{.url}}' 2>/dev/null \
  || echo "(カレントブランチに紐づく PR が見つからない。引数の PR 番号を使うこと)"
echo ""

echo "=== fetch ==="
git fetch origin --quiet 2>/dev/null && echo "origin を fetch 済み" || echo "(fetch 失敗)"

BASE=$(gh pr view --json baseRefName --jq '.baseRefName' 2>/dev/null)
if [ -n "$BASE" ]; then
  echo "=== 分岐状況 (origin/${BASE}...HEAD 上位30件) ==="
  git log --oneline --left-right "origin/${BASE}...HEAD" 2>/dev/null | head -30
  echo "=== base 側の変更ファイル (merge-base 比較) ==="
  MB=$(git merge-base "origin/${BASE}" HEAD 2>/dev/null)
  [ -n "$MB" ] && git diff --name-only "$MB" "origin/${BASE}" 2>/dev/null | head -40
fi

echo "=== working tree ==="
git status --short

exit 0
