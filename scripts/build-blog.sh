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

echo "==> 生成紧凑主题导航与搜索"
node "$REPO_ROOT/scripts/apply-blog-navigation.js"

echo "==> 生成独立的 Recent Posts HTML 片段"
node "$REPO_ROOT/scripts/generate-recent-posts.js"

echo "==> 完成。博客 HTML 产物和 Recent Posts 片段均已生成。"
echo "    片段写入 recent-posts.generated.html（gitignore）；根目录 index.html 保持不变。"
echo "    push 后由 GitHub Actions 重新构建并发布到 https://huluoboge.top/blog/"
