#!/usr/bin/env bash
# create-issue スキル用コンテキスト収集。各コマンドのエラーを握り潰し、
# 取得に失敗してもスキル起動を止めないよう常に終了コード0で返す。
set +e

echo "=== 起票先リポジトリ ==="
gh repo view --json nameWithOwner -q .nameWithOwner 2>/dev/null || echo "(取得失敗: GitHub 未連携の可能性)"

echo
echo "=== 現在のブランチ ==="
git branch --show-current 2>/dev/null || echo "(取得失敗)"

echo
echo "=== issue テンプレート ==="
found=0
for p in .github/ISSUE_TEMPLATE/*.md .github/ISSUE_TEMPLATE/*.yml \
         .github/ISSUE_TEMPLATE.md .github/issue_template.md; do
  if [ -f "$p" ]; then
    found=1
    echo "あり: $p"
    echo "--- テンプレート本文 ---"
    cat "$p" 2>/dev/null
    echo
  fi
done
[ "$found" -eq 0 ] && echo "なし（REFERENCE.md のテンプレートを使う）"

exit 0
