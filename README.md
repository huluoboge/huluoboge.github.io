# Hu Yang — huluoboge.top 个人主页

个人主页 + 技术博客。主页为手写静态简历页，博客（`/blog/`）由 [blog-renderer](https://github.com/huluoboge/blog-renderer)
（crossnote 引擎，KaTeX 公式 + mermaid 图表）构建，经 GitHub Actions 在 push 时自动构建部署。

## 目录结构

```
.
├── index.html            # 主页简历（手写；Recent Posts 区块由 CI 注入）
├── styles.css            # 主页样式（博客主题与其同设计语言）
├── blog/                 # 博客：只存 markdown 源 + 静态资源（html 产物 gitignore）
│   ├── config.yml        # 博客配置（basePath: /blog, navigation）
│   ├── home/home/index.md        # 博客首页
│   ├── articles/<slug>/index.md  # 技术文章
│   └── static/           # KaTeX 字体、highlight.js、mermaid（模板引用）
├── tools/blog-renderer/  # 渲染器 submodule（gitlink，独立仓库）
├── scripts/
│   ├── build-blog.sh     # 本地构建博客（与 CI 同命令）
│   └── inject-recent-posts.js  # 注入最新文章到主页（CI 用）
└── .github/workflows/deploy.yml  # CI：构建 + 注入 + 发布 Pages
```

## 快速开始

### 首次准备

```bash
# 1. 拉取渲染器 submodule
git submodule update --init --recursive

# 2. 本地构建会首次自动 npm install 渲染器依赖（crossnote 等，约 1-2 分钟）
```

### 写文章

```bash
# 新建文章：blog/articles/<slug>/index.md
# front-matter:
#   ---
#   title: 文章标题
#   date: 2026-08-30
#   tags: [标签1, 标签2]
#   excerpt: 摘要
#   draft: true        # 草稿（true 时不发布）
#   ---
```

支持：LaTeX 公式（`$...$` / `$$...$$` / equation / align / cases 等）、
mermaid 图表（```` ```mermaid ````）、代码高亮、文章互链（`[文](other.md)`）。

### 本地构建 + 预览

```bash
# 1. 构建博客（生成 html 到 blog/ 下，gitignore 不提交）
./scripts/build-blog.sh

# 2. 起本地 HTTP 服务（必须用 HTTP，file:// 打开静态资源路径会失效）
python3 -m http.server 8977 --bind 127.0.0.1

# 3. 浏览器访问
#    博客首页:   http://127.0.0.1:8977/blog/
#    文章页:     http://127.0.0.1:8977/blog/articles/<slug>/index.html
#    主页:       http://127.0.0.1:8977/
```

> 本地预览主页时，Recent Posts 区块为空占位——该区块由 CI 在部署时自动注入
> 最新 3 篇文章。想本地看效果可手动执行：
> `node scripts/inject-recent-posts.js`（会改写 index.html，看完 `git checkout index.html` 恢复）。

### 发布

```bash
git add blog/articles/<slug> && git commit -m "blog: <标题>"
git push          # CI 自动构建并部署，约 1-2 分钟
```

验证：`curl https://huluoboge.top/blog/articles/<slug>/index.html` 返回 200。

## CI 部署流程（.github/workflows/deploy.yml）

push 到 master 时：

1. checkout（含 submodule）
2. 渲染器目录 `npm ci`
3. `node tools/blog-renderer/src/cli.js build --cwd blog`（md → html）
4. `node scripts/inject-recent-posts.js`（注入最新文章到主页 index.html）
5. upload-pages-artifact → deploy-pages 发布

博客 html 产物不提交仓库（`.gitignore`），CI 构建后随仓库内容一起发布。

## 渲染器更新（submodule bump）

```bash
cd tools/blog-renderer && git pull origin master
cd .. && git add tools/blog-renderer && git commit -m "chore: bump blog-renderer"
git push          # CI 用新渲染器重建全站
```

渲染器开发在独立仓库：<https://github.com/huluoboge/blog-renderer>（175 测试，四项覆盖率 100%）。

## 故障排查

- **本地构建报"找不到渲染器"**：`git submodule update --init --recursive`
- **构建产物没生成**：先删掉残留 `rm -f blog/**/*.html`（旧产物可能干扰），再跑 build 脚本
- **线上静态资源偶发 503**：GitHub Pages 冷缓存，稍等重试即可
- **博客导航/样式不对**：确认 tools/blog-renderer 已 pull 最新（主题在渲染器仓库）
