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

if ! command -v node >/dev/null 2>&1 || ! command -v npm >/dev/null 2>&1; then
  echo "错误: 未找到 node/npm（需要 Node.js 22+）。任选一种方式安装后重试:"
  echo "  # nvm（推荐，无需 sudo）"
  echo "  curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.1/install.sh | bash"
  echo "  nvm install && nvm use"
  echo "  # 或 Ubuntu/Debian 系统包"
  echo "  sudo apt-get update && sudo apt-get install -y nodejs npm"
  exit 1
fi

# node_modules 目录存在但安装不完整时（中断、权限、submodule 重置）也会失败，
# 因此用关键依赖能否 require 成功来决定是否重装，而不是只看目录是否存在。
deps_ok=0
if (cd "$RENDERER_DIR" && node -e "require('fs-extra'); require('crossnote'); require('front-matter'); require('yaml')" >/dev/null 2>&1); then
  deps_ok=1
fi

if [ "$deps_ok" -ne 1 ]; then
  echo "==> 安装渲染器依赖"
  (cd "$RENDERER_DIR" && npm install)
fi

echo "==> 构建博客 (basePath=/blog)"
node "$REPO_ROOT/scripts/build-blog-cached.js"

echo "==> 生成紧凑主题导航与搜索"
node "$REPO_ROOT/scripts/apply-blog-navigation.js"

echo "==> 生成独立的 Recent Posts HTML 片段"
node "$REPO_ROOT/scripts/generate-recent-posts.js"

echo "==> 完成。博客 HTML 产物和 Recent Posts 片段均已生成。"
echo "    片段写入 recent-posts.generated.html（gitignore）；根目录 index.html 保持不变。"
echo "    push 后由 GitHub Actions 重新构建并发布到 https://huluoboge.top/blog/"
