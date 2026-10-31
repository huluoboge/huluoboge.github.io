# 博客（blog/）

部署在 https://huluoboge.top/blog/ 子目录，由 [blog-renderer](https://github.com/huluoboge/huluoboge_blog) 构建。

## 结构

```
blog/
  config.yml                # 站点配置（basePath: /blog）
  papers_to_read.md         # 仓库内维护的待读论文清单
  home/home/index.md        # 博客首页（含最新文章占位符）
  articles/<slug>/index.md  # 文章（front-matter: title/date/section/kind/categories/tags/excerpt）
  categories/                # 构建生成：分类总览与分类页
  static/                   # 静态资源（KaTeX 字体、highlight.js、mermaid）
  *.html                    # 构建产物（gitignore，发布时由 CI 生成）
```

## 写文章

待读论文和选题想法记在 [待读论文清单](papers_to_read.md) 中。清单供仓库维护，不属于博客导航或渲染生成的页面；因为仓库是公开的，部署后也可以通过源文件路径访问。

1. 新建目录 `blog/articles/<slug>/index.md`
2. front-matter 至少写 `title` 和 `date`；`section` 默认为 `work`，生活文章写 `section: life`；`kind` 默认为 `technical`，论文解读系列写 `kind: paper-reading`；`draft: true` 表示草稿不发布
3. `categories` 记录技术主题，使用 `config.yml` 中的主题 slug，例如 `categories: [state-estimation, reconstruction]`；一篇文章可以写多个主题
4. 首页按“工作 / 生活”区分；工作内容再分“技术文章 / 论文解读”，并可继续按技术主题筛选。列表按时间倒序，近期技术文章单独展示
5. 支持：LaTeX 公式（`$...$` / `$$...$$` / equation / align 等）、mermaid 图表（` ```mermaid `）、代码高亮、`.md` 链接互链

写博客正文时先读[博客写作 Skill](skills/blog-writing/SKILL.md)；单篇论文解读或多篇综述再按其中指引阅读论文写作细则。

### 文章组织

文章按两个维度组织：`section` 表示工作或生活，`kind` 表示工作内容属于技术文章还是论文解读系列，`categories` 表示技术主题。论文解读可以同时标注一个或多个技术主题。旧文章中的 `paper-reading` 分类会被兼容识别；新文章应使用 `kind: paper-reading`。

近期技术文章按时间展示，完整列表也按时间倒序；主题标签用于交叉浏览，详细关键词留在 `tags` 并可被搜索。

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
