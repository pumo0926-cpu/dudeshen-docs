#!/usr/bin/env bash
# 一键发布：由项目根目录的 Markdown 重建静态站 → 提交 → 推送到
# pumo0926-cpu/dudeshen-docs（GitHub Pages 自动部署，约 1 分钟后生效）
#
#   用法：./publish.sh "提交说明"
#
set -euo pipefail

SITE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(dirname "$SITE")"
MSG="${1:-更新文档}"

# 1. 重建（读 $ROOT/*.md 与 $ROOT/content/，写 $SITE）
python3 "$SITE/tools/build_site.py"

# 2. 提交并推送
cd "$SITE"
git add -A
if git diff --cached --quiet; then
  echo "站点无变化，跳过提交"
else
  git commit -q -m "$MSG"
  git pull --rebase -q origin main
  git push -q origin main
  echo "已发布 → https://pumo0926-cpu.github.io/dudeshen-docs/"
fi

# 3. 提醒：两个 H5 Demo 是独立仓库，有改动时需各自提交
for d in h5-dudeshen h5-month-demo; do
  if [ -d "$ROOT/$d/.git" ] && [ -n "$(git -C "$ROOT/$d" status --porcelain)" ]; then
    echo "⚠️  $d 有未提交的改动（独立仓库，需单独 git commit && git push）"
  fi
done
