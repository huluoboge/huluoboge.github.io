#!/usr/bin/env node

const mume = require("@shd101wyy/mume");
const fs = require("fs-extra");
const path = require("path");
const frontMatter = require("front-matter");
const yaml = require("yaml");

// 读取配置文件
let config = null;
let navItems = [];

async function loadConfig() {
  try {
    const configContent = await fs.readFile("config.yml", "utf8");
    config = yaml.parse(configContent);
    navItems = config.navigation || [];
    console.log("配置文件加载成功");
  } catch (error) {
    console.error("加载配置文件失败，使用默认配置:", error);
    // 默认配置
    config = {
      site: {
        title: "我的博客",
        description: "个人技术博客",
        author: "作者",
      },
      navigation: [
        { name: "首页", path: "/", folder: "home", isHome: true, type: "page" },
        {
          name: "技术文章",
          path: "/articles/",
          folder: "articles",
          type: "articles",
        },
        { name: "博客", path: "/blog/", folder: "blog", type: "blog" },
        {
          name: "开源项目",
          path: "/projects/",
          folder: "projects",
          type: "projects",
        },
      ],
      homepage: {
        latest_articles_count: 3,
        show_projects: true,
        show_blog_posts: false,
      },
    };
    navItems = config.navigation;
  }
}

// 生成导航HTML
function generateNav(currentPath = "") {
  return navItems
    .map((item) => {
      // 特殊处理主页激活状态
      let isActive = false;
      if (item.isHome) {
        isActive =
          currentPath === "/" ||
          currentPath === "" ||
          currentPath === "index.html" ||
          currentPath === "/index.html";
      } else {
        // 改进激活状态判断：检查当前路径是否以导航项的路径开头
        // 例如：当前路径是 "/articles/poisson_understand_1/index.html"
        // 应该匹配 "/articles/" 路径
        isActive =
          currentPath.startsWith(item.path) ||
          currentPath.includes(`/${item.folder}/`) ||
          currentPath === `/${item.folder}/index.html` ||
          currentPath === `/${item.folder}/`;
      }

      // 使用基于根目录的相对路径（以/开头）
      const href = item.isHome ? "/index.html" : `/${item.folder}/index.html`;
      return `<li><a href="${href}" class="${isActive ? "active" : ""}">${
        item.name
      }</a></li>`;
    })
    .join("\n");
}

// 生成HTML页面模板
function generateHTML(title, content, currentPath = "") {
    return `<!DOCTYPE html>
  <html lang="zh-CN">
  <head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>${title}</title>
    <!-- <link rel="stylesheet" href="/static/css/highlight-dark.min.css"> -->
    <link rel="stylesheet" href="/static/css/highlight.min.css">
    <script src="/static/js/mermaid.min.js"></script>
    <script src="/static/js/highlight.min.js"></script>
    <link rel="stylesheet" href="/static/css/katex.min.css">
    <script>
      document.addEventListener('DOMContentLoaded', function() {
        // ...existing code...
      });
    </script>
    <style>
      .container {
        max-width: 800px;
        margin: 0 auto;
        padding: 0 20px;
      }
        :root {
            --bg-color: #ffffff;
            --text-color: #333333;
            --code-bg: #f8f9fa;
            --code-text: #333333;
            --border-color: #e9ecef;
            --nav-bg: #f8f9fa;
            --nav-text: #495057;
            --nav-hover: #007bff;
            --article-bg: #ffffff;
            --article-border: #e9ecef;
        }

        [data-theme="dark"] {
            --bg-color: #1a1a1a;
            --text-color: #e6e6e6;
            --code-bg: #2d2d2d;
            --code-text: #e6e6e6;
            --border-color: #444;
            --nav-bg: #2d2d2d;
            --nav-text: #e6e6e6;
            --nav-hover: #4a90e2;
            --article-bg: #2d2d2d;
            --article-border: #444;
        }

        body {
          font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
          margin: 0;
          padding: 20px 0;
          line-height: 1.6;
          background-color: var(--bg-color);
          color: var(--text-color);
          transition: background-color 0.3s ease, color 0.3s ease;
        }
        
        nav {
            background: var(--nav-bg);
            padding: 1rem;
            margin-bottom: 2rem;
            border-radius: 5px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        nav ul {
            list-style: none;
            padding: 0;
            margin: 0;
            display: flex;
            gap: 1rem;
        }
        
        nav a {
            text-decoration: none;
            color: var(--nav-text);
            padding: 0.5rem 1rem;
            border-radius: 3px;
            transition: all 0.3s ease;
        }
        
        nav a:hover, nav a.active {
            background: var(--nav-hover);
            color: white;
        }
        
        .theme-switch {
            background: none;
            border: 1px solid var(--border-color);
            color: var(--text-color);
            padding: 0.5rem 1rem;
            border-radius: 3px;
            cursor: pointer;
            transition: all 0.3s ease;
        }
        
        .theme-switch:hover {
            background: var(--border-color);
        }
        
        .article-list {
            list-style: none;
            padding: 0;
        }
        
        .article-item {
            margin-bottom: 1.5rem;
            padding: 1rem;
            border: 1px solid var(--article-border);
            border-radius: 5px;
            background: var(--article-bg);
            transition: all 0.3s ease;
        }
        
        .article-meta {
            color: var(--text-color);
            opacity: 0.7;
            font-size: 0.9em;
            margin-bottom: 0.5rem;
        }
        
        /* 数学公式响应式样式 */
        .katex { 
            font-size: 1.1em; 
        }

        /* 行内数学公式 */
        .katex-display {
            margin: 1rem 0;
            overflow-x: auto;
            overflow-y: hidden;
            padding: 0.5rem 0;
        }

        /* 数学公式块 */
        .math-block {
            text-align: center;
            margin: 1rem 0;
            overflow-x: auto;
            overflow-y: hidden;
        }
        
        .mermaid { 
            background: var(--code-bg); 
            padding: 1rem; 
            margin: 1rem 0; 
            border-radius: 5px;
            overflow: auto;
        }
        
        pre code.hljs { 
            padding: 1rem; 
            border-radius: 5px; 
            font-size: 0.9em;
            background: var(--code-bg);
            color: var(--code-text);
        }

        pre {
            background: var(--code-bg);
            border-radius: 5px;
            padding: 1rem;
            overflow: auto;
            border: 1px solid var(--border-color);
        }
        
        code:not(.hljs) {
            background: var(--code-bg);
            color: var(--code-text);
            padding: 0.2em 0.4em;
            border-radius: 3px;
            font-size: 0.9em;
        }
        
        .math-block { text-align: center; margin: 1rem 0; }
        .math-inline { display: inline; }
        
        /* 返回按钮样式 */
        .back-button {
            display: inline-block;
            margin: 1rem 0 2rem 0;
            padding: 0.5rem 1rem;
            background: var(--nav-hover);
            color: white;
            text-decoration: none;
            border-radius: 3px;
            transition: all 0.3s ease;
            border: none;
            cursor: pointer;
            font-size: 0.9em;
        }
        
        /* 移动端返回按钮额外间距 */
        @media (max-width: 768px) {
            .back-button {
                margin-top: 1.5rem; /* 在移动端增加上边距，避免被导航栏遮挡 */
            }
        }
        
        .back-button:hover {
            background: var(--nav-text);
            transform: translateY(-1px);
        }
        
        /* 文章图像样式 */
        .article-image {
            width: 100%;
            max-width: 300px;
            height: auto;
            border-radius: 5px;
            margin-bottom: 1rem;
            object-fit: cover;
        }
        
        .article-item-with-image {
            display: grid;
            grid-template-columns: 120px 1fr;
            gap: 1rem;
            align-items: start;
        }
        
        .article-thumbnail {
            width: 100%;
            height: 80px;
            object-fit: cover;
            border-radius: 3px;
        }
        
        /* 汉堡菜单样式 */
        .hamburger {
            display: none;
            background: none;
            border: 1px solid var(--border-color);
            color: var(--text-color);
            padding: 0.5rem;
            border-radius: 3px;
            cursor: pointer;
            font-size: 1.2rem;
            transition: all 0.3s ease;
        }
        
        .hamburger:hover {
            background: var(--border-color);
        }
        
        /* 移动端响应式样式 */
        @media (max-width: 768px) {
            /* 重置所有布局，从头开始设计 */
            html, body {
                width: 100%;
                max-width: 100%;
                overflow-x: hidden;
                margin: 0;
                padding: 0;
            }
            
            body {
                padding-top: 60px !important; /* 为固定导航栏留出空间 */
                padding-left: 15px;
                padding-right: 15px;
                box-sizing: border-box;
            }
            
            /* 导航栏基础样式 - 完全独立于页面内容 */
            nav {
                position: fixed;
                top: 0;
                left: 0;
                width: 100%; /* 使用100%确保与视口一致 */
                height: 60px;
                background: var(--nav-bg);
                box-shadow: 0 2px 8px rgba(0,0,0,0.1);
                z-index: 1001;
                display: flex;
                align-items: center;
                justify-content: space-between;
                padding: 0 15px;
                box-sizing: border-box;
                margin: 0;
                border-radius: 0;
                /* 确保导航栏完全独立于页面内容 */
                overflow: hidden;
            }
            
            /* 汉堡菜单 */
            .hamburger {
                display: block;
                background: none;
                border: 1px solid var(--border-color);
                color: var(--text-color);
                padding: 8px;
                border-radius: 3px;
                cursor: pointer;
                font-size: 1.2rem;
                order: 1;
                flex-shrink: 0;
                /* 确保汉堡菜单位置固定 */
                position: relative;
                z-index: 1002;
            }
            
            /* 导航菜单 - 完全独立于页面内容 */
            .nav-menu {
                display: none;
                position: fixed;
                top: 60px;
                left: 0;
                width: 100%; /* 使用100%确保与视口一致 */
                background: var(--nav-bg);
                padding: 15px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                z-index: 1000;
                max-height: calc(100vh - 60px);
                overflow-y: auto;
                box-sizing: border-box;
                margin: 0;
                /* 确保导航菜单完全独立于页面内容 */
                overflow: hidden;
            }
            
            .nav-menu.active {
                display: flex;
                flex-direction: column;
            }
            
            .nav-menu ul {
                flex-direction: column;
                gap: 10px;
                margin: 0;
                padding: 0;
                width: 100%;
            }
            
            .nav-menu a {
                display: block;
                padding: 10px 15px;
                font-size: 0.9em;
                width: 100%;
                box-sizing: border-box;
            }
            
            /* 主题切换按钮 - 确保位置固定不受表格滚动条影响 */
            .theme-switch {
                margin-left: auto;
                order: 3;
                font-size: 0.9em;
                padding: 8px 12px;
                flex-shrink: 0;
                /* 确保主题切换按钮位置固定 */
                position: relative;
                z-index: 1002;
            }
            
            /* 主内容区域 */
            main {
                margin-top: 0;
                padding-top: 20px;
                width: 100%;
                max-width: 100%;
                box-sizing: border-box;
                /* 确保main内容不会影响导航栏 */
                position: relative;
                z-index: 1;
            }
            
            /* 表格响应式 */
            table {
                display: block;
                overflow-x: auto;
                white-space: nowrap;
                max-width: 100%;
                margin: 1rem 0;
                /* 确保表格滚动条不会影响页面布局 */
                position: relative;
                z-index: 1;
            }
            
            th, td {
                padding: 0.5rem 0.75rem;
                font-size: 0.9em;
            }
            
            /* 数学公式优化 */
            .katex {
                font-size: 1em;
            }
            
            .katex-display {
                font-size: 0.95em;
                margin: 0.75rem 0;
                max-width: 100%;
                overflow-x: auto;
                -webkit-overflow-scrolling: touch;
            }
            
            .math-block {
                font-size: 0.95em;
                margin: 0.75rem 0;
                max-width: 100%;
                overflow-x: auto;
                -webkit-overflow-scrolling: touch;
            }
        }
        
        /* 超小屏幕进一步优化 */
        @media (max-width: 480px) {
            .katex {
                font-size: 0.9em;
            }
            
            .katex-display {
                font-size: 0.85em;
            }
            
            .math-block {
                font-size: 0.85em;
            }
        }
        
        /* 响应式图片样式 */
        main img {
            max-width: 100%;
            height: auto;
            display: block;
            margin: 1rem auto;
            border-radius: 5px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }
        
        /* 图片容器样式 */
        .image-container {
            text-align: center;
            margin: 1.5rem 0;
        }
        
        /* 图片标题样式 */
        .image-caption {
            margin-top: 0.5rem;
            color: var(--text-color);
            opacity: 0.7;
            font-size: 0.9em;
            font-style: italic;
        }
        
        /* 确保所有图片都响应式 */
        .article-thumbnail {
            max-width: 100%;
            height: auto;
        }
        
        .article-image {
            max-width: 100%;
            height: auto;
        }
        
        /* 表格样式 - 统一使用移动端响应式效果 */
        table {
            display: block;
            overflow-x: auto;
            white-space: nowrap;
            max-width: 100%;
            margin: 1rem 0;
            border-collapse: collapse;
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            background: var(--article-bg);
            border: 1px solid var(--border-color);
            -webkit-overflow-scrolling: touch; /* 移动端平滑滚动 */
        }
        
        th, td {
            padding: 0.75rem 1rem;
            text-align: left;
            border-bottom: 1px solid var(--border-color);
            transition: all 0.3s ease;
            font-size: 0.95em;
            min-width: 120px; /* 确保单元格有最小宽度 */
        }
        
        th {
            background: var(--nav-bg);
            color: var(--nav-text);
            font-weight: 600;
            border-bottom: 2px solid var(--border-color);
            position: sticky;
            left: 0; /* 固定表头在滚动时可见 */
            z-index: 1;
        }
        
        tbody tr:hover {
            background: var(--code-bg);
            transform: translateY(-1px);
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }
        
        tbody tr:nth-child(even) {
            background: var(--code-bg);
        }
        
        tbody tr:nth-child(even):hover {
            background: var(--nav-bg);
            transform: translateY(-1px);
        }
        
        /* 响应式表格 - 移动端额外优化 */
        @media (max-width: 768px) {
            body {
                max-width: 100%;
                padding: 15px;
                overflow-x: hidden;
            }
            
            /* 确保表格容器不会导致页面布局问题 */
            main {
                max-width: 100%;
                overflow-x: hidden;
            }
            
            /* 修复导航栏在移动端的布局 */
            nav {
                max-width: 100%;
                overflow-x: hidden;
            }
            
            /* 确保页面内容宽度正确 */
            html, body {
                width: 100%;
                max-width: 100%;
                overflow-x: hidden;
            }
        }
        
        /* 表格标题样式 */
        table + p {
            margin-top: 0.5rem;
            color: var(--text-color);
            opacity: 0.7;
            font-size: 0.9em;
            font-style: italic;
            text-align: center;
        }

        /* Markdown 嵌入样式 */
        .markdown-embed {
            margin: 1.5rem 0;
            border: 1px solid var(--border-color);
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            transition: all 0.3s ease;
        }

        .markdown-embed:hover {
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            transform: translateY(-1px);
        }

        /* 移动端嵌入样式优化 */
        @media (max-width: 768px) {
            .markdown-embed {
                margin: 1rem 0;
                border-radius: 6px;
            }

        }
    </style>
  </head>
<body>
  <div class="container">
    <nav>
      <button class="hamburger" onclick="toggleMenu()">☰</button>
      <ul class="nav-menu">
        ${generateNav(currentPath)}
      </ul>
      <button class="theme-switch" onclick="toggleTheme()"> 切换主题</button>
    </nav>
    <main>
      ${content}
    </main>
  </div>
</body>
</html>`;
}

// 使用Mume处理单个Markdown文件
async function processMarkdownFile(filePath) {
  try {
    console.log(`处理文件: ${filePath}`);

    const mdFileDir = path.dirname(filePath);
    const content = await fs.readFile(filePath, "utf8");

    // 解析 Front Matter
    const parsed = frontMatter(content);
    const body = parsed.body;
    const attributes = parsed.attributes;

    let title = path.basename(filePath, ".md");
    if (attributes.title) title = attributes.title;

    // 处理 markdown 链接和嵌入 - 在 Mume 渲染之前处理
    const { content: processedBody, filesToProcess } = await processMarkdownLinksAndEmbeds(body, mdFileDir);

    // 处理所有被引用的文件
    for (const referencedFile of filesToProcess) {
      if (referencedFile !== filePath) { // 避免重复处理当前文件
        try {
          await processMarkdownFile(referencedFile);
        } catch (error) {
          console.warn(`处理被引用文件失败: ${referencedFile}`, error);
        }
      }
    }

    // 初始化 Mume 引擎
    const engine = new mume.MarkdownEngine({
      filePath,
      config: {
        mathRenderingOption: "KaTeX",
        codeBlockTheme: null, // 不使用 Mume CSS，使用 highlight.js
        previewTheme: "github.css",
        enableScriptExecution: false,
        enableEmoji: true,
        mathInlineDelimiters: [
          ["$", "$"],
          ["\\(", "\\)"],
        ],
        mathBlockDelimiters: [
          ["$$", "$$"],
          ["\\[", "\\]"],
        ],
        mathRenderer: "KaTeX",
      },
    });

    // 渲染 Markdown
    const result = await engine.parseMD(processedBody, {});
    let htmlContent = result.html;

    // ⚡ 修复代码块高亮 - 处理Prism生成的代码块
    // 处理带语言的代码块 (data-role="codeBlock" 格式)
    htmlContent = htmlContent.replace(
      /<pre data-role="codeBlock" data-info="(.*?)" class="language-(.*?)"><code>/gi,
      (_, info, lang) => {
        const normalizedLang = lang.toLowerCase();
        return `<pre><code class="hljs language-${normalizedLang}">`;
      }
    );

    // 处理不带语言的代码块 (data-role="codeBlock" 格式)
    htmlContent = htmlContent.replace(
      /<pre data-role="codeBlock" data-info=" class="language-"><code>/gi,
      '<pre><code class="hljs">'
    );

    // 处理其他可能的代码块格式
    htmlContent = htmlContent.replace(
      /<pre><code class="language-(.*?)">/gi,
      (_, lang) => {
        const normalizedLang = lang.toLowerCase();
        return `<pre><code class="hljs language-${normalizedLang}">`;
      }
    );

    // 没有语言的 code 也加 hljs - 更精确的匹配
    htmlContent = htmlContent.replace(
      /<pre>\s*<code(?!.*hljs)(?!.*class="[^"]*hljs[^"]*")/g,
      '<pre><code class="hljs"'
    );

    // 处理 <pre data-role="codeBlock" data-info="javascript" class="language-javascript"> 格式
    htmlContent = htmlContent.replace(
      /<pre data-role="codeBlock" data-info="(.*?)" class="language-(.*?)">/gi,
      (_, info, lang) => {
        const normalizedLang = lang.toLowerCase();
        return `<pre><code class="hljs language-${normalizedLang}">`;
      }
    );

    // 🔧 修复代码块闭合标签问题 - 确保所有代码块都有正确的闭合结构
    // 处理没有闭合 </code> 标签的代码块
    htmlContent = htmlContent.replace(
      /<pre><code class="hljs[^"]*">([\s\S]*?)<\/pre>/gi,
      (match, codeContent) => {
        // 确保代码内容被正确包裹在 code 标签内
        return `<pre><code class="hljs">${codeContent}</code></pre>`;
      }
    );

    // 处理带语言的代码块闭合问题
    htmlContent = htmlContent.replace(
      /<pre><code class="hljs language-[^"]*">([\s\S]*?)<\/pre>/gi,
      (match, codeContent) => {
        // 提取语言类名
        const langMatch = match.match(/class="hljs language-([^"]*)"/);
        const langClass = langMatch ? ` language-${langMatch[1]}` : "";
        return `<pre><code class="hljs${langClass}">${codeContent}</code></pre>`;
      }
    );

    // 修复 Mume 引擎可能生成的代码块闭合问题
    htmlContent = htmlContent.replace(
      /<pre[^>]*>([\s\S]*?)<\/pre>/gi,
      (match, preContent) => {
        // 如果 pre 标签内没有 code 标签，则添加 code 标签
        if (!preContent.includes("<code") && !preContent.includes("</code>")) {
          return `<pre><code class="hljs">${preContent}</code></pre>`;
        }
        return match;
      }
    );

    // 处理相对路径，图片和文档的格式。
    htmlContent = htmlContent.replace(
      /file:\/\/\/[^"]*\.(jpg|png|gif|svg|html)/g,
      (absolutePath) => {
        const fileSystemPath = absolutePath.replace("file://", "");
        return path.relative(mdFileDir, fileSystemPath);
      }
    );

    htmlContent = htmlContent.replace(/""/g, '"');

    // 注意：现在只在 Mume 渲染之前处理嵌入和链接，避免双重处理

    // 返回按钮
    const folderName = path.dirname(filePath).split(path.sep).pop();
    const parentFolder = path
      .dirname(filePath)
      .split(path.sep)
      .slice(-2, -1)[0];
    const isArticlePage =
      folderName !== "." &&
      navItems.some((item) => item.folder === parentFolder) &&
      !navItems.find((item) => item.folder === parentFolder)?.isHome;

    let finalContent = htmlContent;
    if (isArticlePage) {
      const backButton = `<a href="../index.html" class="back-button">← 返回${
        navItems.find((item) => item.folder === parentFolder).name
      }</a>`;
      finalContent = backButton + htmlContent;
    }

    const outputPath = filePath.replace(".md", ".html");

    // 修复导航栏激活状态：计算相对于根目录的路径
    const relativePath =
      "/" +
      path
        .relative(process.cwd(), path.dirname(outputPath))
        .replace(/\\/g, "/");

    // 对于根目录下的文件，确保路径以/开头
    const normalizedPath = relativePath === "/." ? "/" : relativePath;

    const fullHTML = generateHTML(title, finalContent, normalizedPath);
    await fs.writeFile(outputPath, fullHTML);
    console.log(`生成成功: ${outputPath}`);

    return {
      title,
      date: attributes.date,
      tags: attributes.tags,
      excerpt: attributes.excerpt,
      image: attributes.image,
    };
  } catch (error) {
    console.error(`处理文件 ${filePath} 时出错:`, error);
    throw error;
  }
}
// 生成目录索引页面
async function generateIndexPage(folder, articles, allArticles = []) {
  const navItem = navItems.find((item) => item.folder === folder);

  // 如果是主页，则生成主页内容
  if (navItem.isHome) {
    // 首页应该和其他文章一样，使用传入的 articles 参数
    if (articles.length === 0) {
      console.log("首页没有找到文章，跳过主页生成");
      return;
    }

    // 处理首页文章（应该只有一个）
    const homeArticle = articles[0];
    const meta = await processMarkdownFile(homeArticle.articlePath);
    if (!meta) {
      console.log("处理首页文章失败");
      return;
    }

    // 读取生成的 HTML 内容
    const homeHtmlPath = homeArticle.articlePath.replace(".md", ".html");
    const indexContent = await fs.readFile(homeHtmlPath, "utf8");

    // 提取main标签内的内容
    const mainContentMatch = indexContent.match(/<main>([\s\S]*?)<\/main>/);
    if (mainContentMatch && mainContentMatch[1]) {
      let mainContent = mainContentMatch[1];

      // 修复相对路径链接
      mainContent = mainContent.replace(/file:\/\/\//g, "./");
      mainContent = mainContent.replace(/file:\/\/\/\//g, "./");

      // 获取最新文章（只从技术文章中获取，按日期排序的前3篇），排除关于我页面
      const allArticlesSorted = allArticles
        .filter((article) => article.date && article.folder === "articles") // 只包含有日期的技术文章，排除关于我页面
        .sort((a, b) => new Date(b.date) - new Date(a.date)) // 按日期降序
        .slice(0, 3); // 取前3篇

      // 移除调试信息

      // 生成最新文章列表HTML
      const latestArticlesHTML = allArticlesSorted
        .map((article) => {
          // 根据文章所在的文件夹生成正确的相对路径（新的文件夹结构）
          let articlePath;
          if (article.folder === "articles") {
            articlePath = `articles/${article.slug}/index.html`;
          } else if (article.folder === "blog") {
            articlePath = `blog/${article.slug}/index.html`;
          } else if (article.folder === "projects") {
            articlePath = `projects/${article.slug}/index.html`;
          } else {
            articlePath = `${article.slug}/index.html`;
          }

          return `<li><a href="${articlePath}">${
            article.title
          }</a> - ${new Date(article.date).toLocaleDateString("zh-CN")}</li>`;
        })
        .join("\n");

      // 获取开源项目（projects文件夹中的所有项目）
      const openSourceProjects = allArticles
        .filter((article) => article.folder === "projects")
        .sort((a, b) => new Date(b.date) - new Date(a.date)); // 按日期排序

      // 生成开源项目列表HTML
      const openSourceProjectsHTML = openSourceProjects
        .map((project) => {
          const projectPath = `projects/${project.file.replace(
            ".md",
            ".html"
          )}`;
          return `<li><a href="${projectPath}">${project.title}</a> - ${
            project.excerpt || "开源项目"
          }</li>`;
        })
        .join("\n");

      // 替换主页中的占位符
      let updatedContent = mainContent;

      // 替换最新文章占位符
      if (
        mainContent.includes('<div id="latest-articles-placeholder"></div>')
      ) {
        updatedContent = updatedContent.replace(
          '<div id="latest-articles-placeholder"></div>',
          `<ul>${latestArticlesHTML}</ul>`
        );
      }

      // 替换开源项目占位符
      if (
        mainContent.includes(
          '<div id="open-source-projects-placeholder"></div>'
        )
      ) {
        updatedContent = updatedContent.replace(
          '<div id="open-source-projects-placeholder"></div>',
          `<ul>${openSourceProjectsHTML}</ul>`
        );
      }

      // 生成主页内容
      const content = updatedContent;
      const outputPath = path.join(folder, "index.html");
      const html = generateHTML(navItem.name, content, "/");

      await fs.outputFile(outputPath, html);
      console.log(`生成主页: ${outputPath}`);

      // 同时复制到根目录作为主页
      await fs.copy(outputPath, "index.html");
      console.log("复制主页到根目录");
    }
  } else {
    // 其他分类的正常索引页面
    // 按日期降序排序（最新的文章在前）
    const sortedArticles = articles.sort((a, b) => {
      // 处理没有日期的情况，将没有日期的文章排在最后
      if (!a.date && !b.date) return 0;
      if (!a.date) return 1;
      if (!b.date) return -1;

      return new Date(b.date) - new Date(a.date);
    });

    const listHTML = sortedArticles
      .map((article) => {
        const hasImage = article.image && article.image.trim() !== "";
        return `
      <div class="article-item ${hasImage ? "article-item-with-image" : ""}">
          ${
            hasImage
              ? `
          <div class="article-thumbnail-container">
              <img src="${article.image}" alt="${article.title}" class="article-thumbnail">
          </div>
          `
              : ""
          }
          <div class="article-content">
              <h3><a href="${article.slug}/index.html">${article.title}</a></h3>
              <div class="article-meta">
                  ${article.date ? `发布于: ${article.date}` : ""}
                  ${article.tags ? ` | 标签: ${article.tags.join(", ")}` : ""}
              </div>
              ${article.excerpt ? `<p>${article.excerpt}</p>` : ""}
          </div>
      </div>
    `;
      })
      .join("\n");

    const content = `
      <h1>${navItem.name}</h1>
      <div class="article-list">
          ${listHTML}
      </div>
    `;

    const outputPath = path.join(folder, "index.html");
    const html = generateHTML(navItem.name, content, `/${folder}/`);

    await fs.outputFile(outputPath, html);
    console.log(`生成索引: ${outputPath}`);
  }
}

// 处理 markdown 链接和嵌入 - 只进行文本替换，返回处理后的内容和需要处理的文件列表
async function processMarkdownLinksAndEmbeds(content, mdFileDir) {
  const processedFiles = new Set();
  const filesToProcess = new Set();

  // 递归处理函数
  async function processRecursively(content, currentDir) {
    // 处理 ![]() 嵌入语法 - 只进行文本替换
    const embedMatches = [];
    content.replace(
      /!\[([^\]]*)\]\(([^)]+\.md)\)/g,
      (match, altText, embedPath, offset) => {
        embedMatches.push({ match, altText, embedPath, offset, isEmbed: true });
        return match;
      }
    );

    // 处理 []() 链接语法 - 只进行文本替换
    const linkMatches = [];
    content.replace(
      /\[([^\]]+)\]\(([^)]+\.md)\)/g,
      (match, text, linkPath, offset) => {
        linkMatches.push({ match, text, linkPath, offset, isEmbed: false });
        return match;
      }
    );

    // 合并所有匹配并按位置排序
    const allMatches = [...embedMatches, ...linkMatches].sort(
      (a, b) => a.offset - b.offset
    );

    let result = content;
    let offsetAdjustment = 0;

    for (const {
      match,
      altText,
      text,
      embedPath,
      linkPath,
      isEmbed,
    } of allMatches) {
      const filePath = isEmbed ? embedPath : linkPath;

      try {
        // 解析相对路径
        const resolvedPath = path.resolve(currentDir, filePath);

        // 检查文件是否存在
        if (!(await fs.pathExists(resolvedPath))) {
          console.warn(`文件不存在: ${resolvedPath}`);
          continue;
        }

        // 检查是否已经处理过，避免无限循环
        if (isEmbed && processedFiles.has(resolvedPath)) {
          console.warn(`检测到循环引用，跳过嵌入: ${resolvedPath}`);
          continue;
        }
        if (isEmbed) {
          processedFiles.add(resolvedPath);
        }

        // 添加到需要处理的文件列表
        filesToProcess.add(resolvedPath);

        if (isEmbed) {
          // 嵌入处理：读取markdown文件内容进行文本替换
          const embedContent = await fs.readFile(resolvedPath, "utf8");
          const embedDir = path.dirname(resolvedPath);

          // 递归处理嵌入内容中的链接和嵌入
          const processedEmbedContent = await processRecursively(
            embedContent,
            embedDir
          );

          // 直接使用嵌入的markdown内容进行文本替换
          const embedReplacement = processedEmbedContent;

          // 替换嵌入内容
          const currentOffset = result.indexOf(match, offsetAdjustment);
          if (currentOffset !== -1) {
            result =
              result.slice(0, currentOffset) +
              embedReplacement +
              result.slice(currentOffset + match.length);
            offsetAdjustment += embedReplacement.length - match.length;
          }
        } else {
          // 链接处理：参考图片相对路径逻辑，将绝对路径转换为相对路径
          let htmlPath;
          if (filePath.startsWith("file://")) {
            // 如果是绝对路径，转换为相对路径
            const fileSystemPath = filePath.replace("file://", "");
            htmlPath = path.relative(currentDir, fileSystemPath).replace(/\.md$/, ".html");
          } else {
            // 如果是相对路径，只替换后缀
            htmlPath = filePath.replace(/\.md$/, ".html");
          }

          // 创建HTML链接
          const linkHtml = `<a href="${htmlPath}">${text}</a>`;

          // 替换链接
          const currentOffset = result.indexOf(match, offsetAdjustment);
          if (currentOffset !== -1) {
            result =
              result.slice(0, currentOffset) +
              linkHtml +
              result.slice(currentOffset + match.length);
            offsetAdjustment += linkHtml.length - match.length;
          }
        }
      } catch (error) {
        console.error(`处理文件失败: ${filePath}`, error);
        // 如果处理失败，保留原始内容
      }
    }

    return result;
  }

  // 开始递归处理
  const processedContent = await processRecursively(content, mdFileDir);
  
  return {
    content: processedContent,
    filesToProcess: Array.from(filesToProcess)
  };
}

// 复制静态资源到输出目录
async function copyStaticAssets(outputDir = ".") {
  console.log("复制静态资源...");
  const staticSource = "static";
  const staticDest = path.join(outputDir, "static");

  // 如果源和目标路径相同，跳过复制
  if (staticSource === staticDest) {
    console.log("静态资源已存在，跳过复制");
    return;
  }

  if (await fs.pathExists(staticSource)) {
    await fs.copy(staticSource, staticDest);
    console.log("静态资源复制完成");
  } else {
    console.log("静态资源目录不存在，跳过复制");
  }
}

// 查找子目录中的 index.md 文件
async function discoverArticles(folderPath) {
  const articles = [];

  if (!(await fs.pathExists(folderPath))) {
    return articles;
  }

  const items = await fs.readdir(folderPath);

  for (const item of items) {
    const itemPath = path.join(folderPath, item);
    const stat = await fs.stat(itemPath);

    // 只处理子目录
    if (stat.isDirectory()) {
      const indexPath = path.join(itemPath, "index.md");

      if (await fs.pathExists(indexPath)) {
        try {
          // 读取文件内容解析 Front Matter
          const content = await fs.readFile(indexPath, "utf8");
          const parsed = frontMatter(content);
          const attributes = parsed.attributes;

          // 检查草稿状态，默认发布（draft: false 或没有 draft 字段）
          if (attributes.draft === true) {
            console.log(`跳过草稿文章: ${item}`);
            continue;
          }

          articles.push({
            path: indexPath,
            folder: itemPath,
            slug: item,
            attributes: attributes,
          });

          console.log(`发现文章: ${item}`);
        } catch (error) {
          console.error(`解析文章 ${item} 失败:`, error);
        }
      }
    }
  }

  return articles;
}

// 主渲染函数
async function renderAll() {
  console.log("开始使用Mume生成博客...");

  try {
    // 加载配置文件
    await loadConfig();

    // 初始化Mume
    console.log("初始化Mume...");
    await mume.init();

    // 复制静态资源
    await copyStaticAssets();

    const allArticles = [];

    // 第一步：收集所有文章信息
    for (const navItem of navItems) {
      const folderPath = navItem.folder;

      // 使用新的文章发现逻辑
      const discoveredArticles = await discoverArticles(folderPath);

      console.log(
        `收集文件夹 ${folderPath}: 找到 ${discoveredArticles.length} 篇文章`
      );

      for (const articleInfo of discoveredArticles) {
        try {
          const meta = await processMarkdownFile(articleInfo.path);
          if (meta) {
            allArticles.push({
              ...meta,
              slug: articleInfo.slug,
              file: "index.md", // 统一使用 index.md
              folder: folderPath,
              articlePath: articleInfo.path,
              articleFolder: articleInfo.folder,
            });
          }
        } catch (error) {
          console.error(`处理文章 ${articleInfo.slug} 失败:`, error);
        }
      }
    }

    console.log("所有文章收集完成，共", allArticles.length, "篇文章");

    // 第二步：生成所有页面，传递完整的文章列表
    for (const navItem of navItems) {
      const folderPath = navItem.folder;

      const articles = allArticles.filter(
        (article) => article.folder === folderPath
      );

      console.log(`生成文件夹 ${folderPath} 的页面: ${articles.length} 篇文章`);

      // 生成索引页面
      if (articles.length > 0) {
        await generateIndexPage(navItem.folder, articles, allArticles);
      }
    }

    console.log("博客生成完成！");
  } catch (error) {
    console.error("渲染过程中发生错误:", error);
    throw error;
  }
}

// 主程序
async function main() {
  const args = process.argv.slice(2);
  const isWatchMode = args.includes("--watch");

  try {
    await renderAll();

    if (isWatchMode) {
      console.log("监视模式已启动，文件变化时将自动重新生成...");
      // 这里可以添加文件监视逻辑
    }
  } catch (error) {
    console.error("程序执行失败:", error);
    process.exit(1);
  }
}

// 执行主程序
if (require.main === module) {
  main();
}

module.exports = { renderAll };
