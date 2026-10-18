# 博客（blog/）

部署在 https://huluoboge.top/blog/ 子目录，由 [blog-renderer](https://github.com/huluoboge/huluoboge_blog) 构建。

## 结构

```
blog/
  config.yml                # 站点配置（basePath: /blog）
  home/home/index.md        # 博客首页（含最新文章占位符）
  articles/<slug>/index.md  # 文章（front-matter: title/date/categories/tags/excerpt）
  categories/                # 构建生成：分类总览与分类页
  static/                   # 静态资源（KaTeX 字体、highlight.js、mermaid）
  *.html                    # 构建产物（gitignore，发布时由 CI 生成）
```

## 写文章

1. 新建目录 `blog/articles/<slug>/index.md`
2. front-matter 至少写 `title` 和 `date`，建议写 `categories` / `tags` / `excerpt`；`draft: true` 表示草稿不发布
3. `categories` 使用 `config.yml` 中的分类 slug，例如 `categories: [state-estimation]`；一篇文章可以写多个分类
4. 首页提供搜索和紧凑的主题标签，点击主题直接筛选文章，搜索在选中主题内生效；构建器还会生成 `categories/index.html` 及每个主题的详情页
5. 支持：LaTeX 公式（`$...$` / `$$...$$` / equation / align 等）、mermaid 图表（` ```mermaid `）、代码高亮、`.md` 链接互链

基于论文写中文技术博客时，参考 [论文技术博客写作 Skill](skills/write-paper-tech-blog/SKILL.md)。它以 SuperGlue 和重力对齐两篇文章为样例，说明如何组织问题、推导、论文原图与实验解读。

### 主题浏览

主题统一由 `config.yml` 的 `categories` 定义，文章使用同名字段选择一个或多个主题，不另设文章类型字段：

- 论文解读、翻译或围绕具体论文的综述：加入 `paper-reading`，同时保留技术主题，例如 `categories: [paper-reading, local-features, geometry]`。
- 原理推导、专题补充与工程经验：选择相关技术主题。例如 B 样条使用 `[state-estimation, reconstruction]`。
- 生活文章：使用 `life`（生活随记），以后可按实际内容补充主题。

首页展示配置中的全部主题（包括暂时为零的生活随记），允许一篇文章计入多个主题。主题数量表示该主题全部公开文章的数量；搜索后的实际结果数量单独显示。详细关键词留在 `tags`，可被搜索。

`scripts/apply-blog-navigation.js` 在渲染后生成紧凑主题导航，交互脚本位于 `blog/static/js/article-discovery.js`，不改动共享渲染器 submodule。

## 构建与发布

```bash
./scripts/build-blog.sh          # 构建（自动带 basePath=/blog）
git add blog/ && git commit -m "blog: 新文章 xxx"
git push                         # GitHub Pages 自动发布
```

## 注意

- 静态资源从旧博客继承（static/css、static/js），新增加载项时同步更新
- 构建产物（.html）不提交；本地与 GitHub Actions 均运行 `./scripts/build-blog.sh`，包括主题导航、搜索与最近文章片段生成
- 导航与筛选检查：`node scripts/test/blog-navigation.test.js`
- 不建议把文章物理搬进分类文件夹：现有文章使用大量相对路径，元数据分类可以避免 URL、图片和互链一起变化
