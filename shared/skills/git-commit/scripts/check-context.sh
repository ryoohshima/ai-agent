#!/usr/bin/env bash
# git-commit スキル用コンテキスト収集。各コマンドのエラーを握り潰し、
# 取得に失敗してもスキル起動を止めないよう常に終了コード0で返す。
# 俯瞰情報（状態・stat・log）→ 詳細差分の順。
set +e

echo "=== 現在のブランチ ==="
git branch --show-current 2>/dev/null || echo "(取得失敗)"

echo
echo "=== 作業ツリーの状態（追跡外ファイル含む） ==="
git status --short 2>&1

echo
echo "=== 変更ファイルの概要 ==="
git diff --stat HEAD 2>/dev/null || echo "(コミット履歴なし)"

echo
echo "=== ステージ済み差分 ==="
git diff --staged 2>&1

echo
echo "=== 未ステージ差分 ==="
git diff 2>&1

echo
echo "=== 直近コミット（メッセージ様式の参考） ==="
git log --oneline -15 2>/dev/null || echo "(コミット履歴なし)"

exit 0
