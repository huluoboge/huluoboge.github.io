# 博客（blog/）

部署在 https://huluoboge.top/blog/ 子目录，由 [blog-renderer](https://github.com/huluoboge/huluoboge_blog) 构建。

## 结构

```
blog/
  config.yml                # 站点配置（basePath: /blog）
  home/home/index.md        # 博客首页（含最新文章占位符）
  articles/<slug>/index.md  # 技术文章（front-matter: title/date/tags/excerpt）
  static/                   # 静态资源（KaTeX 字体、highlight.js、mermaid）
  *.html                    # 构建产物（提交到仓库，GitHub Pages 直接发布）
```

## 写文章

1. 新建目录 `blog/articles/<slug>/index.md`
2. front-matter 至少写 `title` 和 `date`，可选 `tags` / `excerpt` / `draft: true`（草稿不发布）
3. 支持：LaTeX 公式（`$...$` / `$$...$$` / equation / align 等）、mermaid 图表（` ```mermaid `）、代码高亮、`.md` 链接互链

## 构建与发布

```bash
./scripts/build-blog.sh          # 构建（自动带 basePath=/blog）
git add blog/ && git commit -m "blog: 新文章 xxx"
git push                         # GitHub Pages 自动发布
```

## 注意

- 静态资源从旧博客继承（static/css、static/js），新增加载项时同步更新
- 构建产物（.html）必须提交——GitHub Pages 发布的是仓库内容，无 CI 构建
