# 博客（blog/）

部署在 https://huluoboge.top/blog/ 子目录，由 [blog-renderer](https://github.com/huluoboge/huluoboge_blog) 构建。

## 结构

```
blog/
  config.yml                # 站点配置（basePath: /blog）
  home/home/index.md        # 博客首页（含最新文章占位符）
  articles/<slug>/index.md  # 技术文章（front-matter: title/date/categories/tags/excerpt）
  categories/                # 构建生成：分类总览与分类页
  static/                   # 静态资源（KaTeX 字体、highlight.js、mermaid）
  *.html                    # 构建产物（提交到仓库，GitHub Pages 直接发布）
```

## 写文章

1. 新建目录 `blog/articles/<slug>/index.md`
2. front-matter 至少写 `title` 和 `date`，建议写 `categories` / `tags` / `excerpt`；`draft: true` 表示草稿不发布
3. `categories` 使用 `config.yml` 中的分类 slug，例如 `categories: [state-estimation]`；一篇文章可以写多个分类
4. 首页提供关键词搜索和分类筛选；构建器还会生成 `categories/index.html` 及每个分类的详情页
5. 支持：LaTeX 公式（`$...$` / `$$...$$` / equation / align 等）、mermaid 图表（` ```mermaid `）、代码高亮、`.md` 链接互链

## 构建与发布

```bash
./scripts/build-blog.sh          # 构建（自动带 basePath=/blog）
git add blog/ && git commit -m "blog: 新文章 xxx"
git push                         # GitHub Pages 自动发布
```

## 注意

- 静态资源从旧博客继承（static/css、static/js），新增加载项时同步更新
- 构建产物（.html）必须提交——GitHub Pages 发布的是仓库内容，无 CI 构建
- 不建议把文章物理搬进分类文件夹：现有文章使用大量相对路径，元数据分类可以避免 URL、图片和互链一起变化
