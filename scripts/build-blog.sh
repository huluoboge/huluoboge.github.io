#!/usr/bin/env bash
# 构建博客（huluoboge.top/blog/ 子目录）
# 用法：写/改 blog/articles/<slug>/index.md 后运行本脚本
# 渲染器来自 submodule tools/blog-renderer（与 GitHub Actions 构建完全一致）
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BLOG_DIR="$REPO_ROOT/blog"
RENDERER_DIR="$REPO_ROOT/tools/blog-renderer"

if [ ! -f "$RENDERER_DIR/package.json" ]; then
  echo "错误: 渲染器 submodule 未初始化，请先执行:"
  echo "  git submodule update --init --recursive"
  exit 1
fi

if [ ! -d "$RENDERER_DIR/node_modules" ]; then
  echo "==> 安装渲染器依赖 (首次)"
  (cd "$RENDERER_DIR" && npm install)
fi

echo "==> 构建博客 (basePath=/blog)"
node "$RENDERER_DIR/src/cli.js" build --cwd "$BLOG_DIR"

echo "==> 完成。产物在 blog/ 下（已 gitignore，不提交），"
echo "    push 后由 GitHub Actions 重新构建并发布到 https://huluoboge.top/blog/"
