#!/usr/bin/env bash
# write-a-skill スキル用コンテキスト収集。新規スキル名の衝突回避のため、
# 既存スキル名の一覧を集める。各コマンドのエラーは握り潰し、
# 取得に失敗してもスキル起動を止めないよう常に終了コード0で返す。
set +e

# scripts の1つ上がこのスキルのルート（skills/write-a-skill）、さらに1つ上が
# プロジェクトのスキル群ディレクトリ（skills/）。
skill_dir="$(cd "$(dirname "$0")/.." && pwd 2>/dev/null)"
project_skills="$(cd "${skill_dir}/.." && pwd 2>/dev/null)"

list_skill_names() {
  # 引数: スキル群を格納するディレクトリ。直下の SKILL.md を持つフォルダ名を列挙する。
  local base="$1"
  [ -d "$base" ] || { echo "(なし: $base)"; return; }
  local found=0
  for d in "$base"/*/; do
    if [ -f "${d}SKILL.md" ]; then
      found=1
      echo "- $(basename "$d")"
    fi
  done
  [ "$found" -eq 0 ] && echo "(SKILL.md を持つディレクトリなし)"
}

echo "=== このプロジェクトの既存スキル (${project_skills}) ==="
list_skill_names "$project_skills"

echo
echo "=== 個人スキル (~/.agents/skills) ==="
list_skill_names "${HOME}/.agents/skills"

echo
echo "※ 新規スキル名は上記と衝突しない kebab-case にすること。"

exit 0
