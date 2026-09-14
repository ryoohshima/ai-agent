#!/usr/bin/env bash
# create-draft-pr スキル用コンテキスト収集。各コマンドのエラーを握り潰し、
# 取得に失敗してもスキル起動を止めないよう常に終了コード0で返す。
set +e

echo "=== デフォルトブランチ ==="
def="$(git symbolic-ref --short refs/remotes/origin/HEAD 2>/dev/null)"; def="${def#origin/}"
echo "${def:-main}"

echo
echo "=== git ステータス ==="
git status 2>&1 || echo "(取得失敗)"

echo
echo "=== PR テンプレート ==="
tmpl=""
for p in .github/PULL_REQUEST_TEMPLATE.md .github/pull_request_template.md \
         .github/PULL_REQUEST_TEMPLATE/*.md docs/PULL_REQUEST_TEMPLATE.md PULL_REQUEST_TEMPLATE.md; do
  [ -f "$p" ] && { tmpl="$p"; break; }
done
if [ -n "$tmpl" ]; then
  echo "あり: $tmpl"
  echo "--- テンプレート本文 ---"
  cat "$tmpl" 2>/dev/null
else
  echo "なし（変更差分から本文を構成する）"
fi

exit 0
