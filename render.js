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
    const configContent = await fs.readFile('config.yml', 'utf8');
    config = yaml.parse(configContent);
    navItems = config.navigation || [];
    console.log('配置文件加载成功');
  } catch (error) {
    console.error('加载配置文件失败，使用默认配置:', error);
    // 默认配置
    config = {
      site: {
        title: "我的博客",
        description: "个人技术博客",
        author: "作者"
      },
      navigation: [
        { name: "首页", path: "/", folder: "home", isHome: true, type: "page" },
        { name: "技术文章", path: "/articles/", folder: "articles", type: "articles" },
        { name: "随笔", path: "/blog/", folder: "blog", type: "blog" },
        { name: "开源项目", path: "/projects/", folder: "projects", type: "projects" }
      ],
      homepage: {
        latest_articles_count: 3,
        show_projects: true,
        show_blog_posts: false
      }
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
          currentPath === "index.html";
      } else {
        isActive = currentPath.startsWith(item.path);
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
            // 初始化Mermaid - 根据主题设置不同的配置
            function initMermaid() {
                const isDark = document.documentElement.getAttribute('data-theme') === 'dark';
                mermaid.initialize({ 
                    startOnLoad: true, 
                    theme: isDark ? 'dark' : 'default',
                    securityLevel: 'loose',
                    flowchart: { useMaxWidth: false },
                    themeVariables: isDark ? {
                        primaryColor: '#4a5568',
                        primaryTextColor: '#e6e6e6',
                        primaryBorderColor: '#4a5568',
                        lineColor: '#e6e6e6',
                        tertiaryColor: '#2d3748',
                        tertiaryBorderColor: '#4a5568'
                    } : {}
                });
            }
            
            // 初始化和主题变化时重新初始化Mermaid
            initMermaid();
            
            // 处理静态资源链接
            const links = document.querySelectorAll('a[href$=".md"]');
            links.forEach(link => {
                link.href = link.href.replace('.md', '.html');
            });
            
            // 延迟执行Mermaid渲染，确保DOM完全加载
            setTimeout(function() {
                try {
                    mermaid.init(undefined, '.mermaid');
                } catch (error) {
                    console.error('Mermaid渲染错误:', error);
                }
            }, 500);
            
            // 主题切换功能
            window.toggleTheme = function() {
                const html = document.documentElement;
                const currentTheme = html.getAttribute('data-theme');
                const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
                
                // 防止闪烁：先设置过渡属性
                html.style.transition = 'none';
                html.setAttribute('data-theme', newTheme);
                localStorage.setItem('theme', newTheme);
                
                // 重新初始化Mermaid以适应新主题
                initMermaid();
                
                // 重新渲染Mermaid图表
                setTimeout(function() {
                    try {
                        mermaid.init(undefined, '.mermaid');
                    } catch (error) {
                        console.error('Mermaid渲染错误:', error);
                    }
                    // 恢复过渡效果
                    html.style.transition = '';
                }, 100);
            }
            
            // 初始化主题
            const savedTheme = localStorage.getItem('theme') || 'light';
            document.documentElement.setAttribute('data-theme', savedTheme);
            
            // 汉堡菜单功能
            window.toggleMenu = function() {
                const navMenu = document.querySelector('.nav-menu');
                navMenu.classList.toggle('active');
            }
            
            // 点击页面其他区域关闭菜单
            document.addEventListener('click', function(event) {
                const navMenu = document.querySelector('.nav-menu');
                const hamburger = document.querySelector('.hamburger');
                
                if (navMenu.classList.contains('active') && 
                    !navMenu.contains(event.target) && 
                    !hamburger.contains(event.target)) {
                    navMenu.classList.remove('active');
                }
            });
            
            // 点击导航链接后关闭菜单
            const navLinks = document.querySelectorAll('.nav-menu a');
            navLinks.forEach(link => {
                link.addEventListener('click', function() {
                    const navMenu = document.querySelector('.nav-menu');
                    navMenu.classList.remove('active');
                });
            });
            
            // document.querySelectorAll('pre code.hljs').forEach(block => {
            //     hljs.highlightElement(block);
            // });
            // if (typeof hljs !== 'undefined') {
            //     hljs.highlightAll(); // 自动高亮所有代码块
            // } else {
            //     console.error('highlight.js 未加载');
            // }
            // 初始化代码高亮
            function initHighlight() {
                if (typeof hljs !== 'undefined') {
                    // 高亮所有代码块
                    // document.querySelectorAll('pre code').forEach((block) => {
                    //     hljs.highlightElement(block);
                    // });
                    hljs.highlightAll(); // 自动高亮所有代码块
                } else {
                    console.error('highlight.js not loaded');
                }
            }
            
            // 立即执行代码高亮
            initHighlight();
            
            // 延迟执行代码高亮，确保DOM完全加载
            setTimeout(initHighlight, 1000);
            
            // 主题切换时重新高亮代码
            const originalToggleTheme = window.toggleTheme;
            window.toggleTheme = function() {
                originalToggleTheme();
                setTimeout(initHighlight, 200);
            };
            
            // // 初始化KaTeX数学公式渲染
            // function renderMath() {
            //     renderMathInElement(document.body, {
            //         delimiters: [
            //             {left: '$$', right: '$$', display: true},
            //             {left: '$', right: '$', display: false},
            //             {left: '\\(', right: '\\)', display: false},
            //             {left: '\\[', right: '\\]', display: true}
            //         ],
            //         throwOnError: false
            //     });
            // }
            
            // // 延迟渲染数学公式，确保DOM完全加载
            // setTimeout(renderMath, 100);
            
            // // 主题切换时重新渲染数学公式
            // const originalToggleTheme = window.toggleTheme;
            // window.toggleTheme = function() {
            //     originalToggleTheme();
            //     setTimeout(renderMath, 200);
            // };
        });
    </script>
    <style>
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
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
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
        
        .katex { font-size: 1.1em; }
        
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

        // pre code[class*="language-"] {
        //     white-space: pre;
        //     word-break: normal;
        //     overflow: auto;
        // }

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
            .hamburger {
                display: block;
            }
            
            .nav-menu {
                display: none;
                flex-direction: column;
                position: absolute;
                top: 100%;
                left: 0;
                right: 0;
                background: var(--nav-bg);
                padding: 1rem;
                border-radius: 0 0 5px 5px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                z-index: 1000;
            }
            
            .nav-menu.active {
                display: flex;
            }
            
            nav ul {
                flex-direction: column;
                gap: 0.5rem;
            }
            
            nav {
                position: relative;
                flex-wrap: wrap;
            }
            
            .theme-switch {
                margin-left: auto;
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
    </style>
</head>
<body>
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
</body>
</html>`;
}

// 使用Mume处理单个Markdown文件
async function processMarkdownFile_bk(filePath) {
  try {
    console.log(`处理文件: ${filePath}`);

    // 获取Markdown文件所在目录
    const mdFileDir = path.dirname(filePath);
    // 读取文件内容
    const content = await fs.readFile(filePath, "utf8");

    // 解析Front Matter
    const parsed = frontMatter(content);
    const body = parsed.body;
    const attributes = parsed.attributes;

    let title = path.basename(filePath, ".md");
    if (attributes.title) {
      title = attributes.title;
    }

    // 初始化Mume引擎
    const engine = new mume.MarkdownEngine({
      filePath: filePath,
      config: {
        mathRenderingOption: "KaTeX",
        // codeBlockTheme: "default.css",  // 使用默认主题，让highlight.js自动检测语言
        // previewTheme: "github-dark.css",
        codeBlockTheme: null, // 不使用Mume内置CSS
        previewTheme: "github.css", // 页面主题
        enableScriptExecution: false,
        breakOnSingleNewLine: false,
        enableTypographer: false,
        enableEmoji: true,
        mathInlineDelimiters: [
          ["$", "$"],
          ["\\(", "\\)"],
        ],
        mathBlockDelimiters: [
          ["$$", "$$"],
          ["\\[", "\\]"],
        ],
        mathRenderingOnServerSide: false,
        usePandocParser: false,
        protocolsWhiteList: "http,https,file,data",
        mathRenderer: "KaTeX",
      },
    });

    // 在Markdown渲染前预处理相对路径
    // 提取所有相对路径的图像引用，避免Mume转换为绝对路径
    const relativeImageRegex = /!\[.*?\]\(((?:\.\/)?.*?\.(jpg|png|gif|svg))\)/g;
    const imageMatches = [];
    let match;

    while ((match = relativeImageRegex.exec(body)) !== null) {
      imageMatches.push(match[1]);
    }

    // 渲染Markdown为HTML
    const result = await engine.parseMD(body, {});
    // 给代码块加上 hljs 类
    // let htmlContent = result.html.replace(
    //   /<pre><code class="language-(.*?)">/g,
    //   '<pre><code class="hljs language-$1">'
    // );
    let htmlContent = result.html;

    // 恢复原始的相对路径 - 使用通用方法处理所有图片路径
    htmlContent = htmlContent.replace(
      /file:\/\/\/[^"]*\.(jpg|png|gif|svg)/g,
      (absolutePath) => {
        // 移除file://前缀
        const fileSystemPath = absolutePath.replace("file://", "");

        // 计算相对于Markdown文件所在目录的相对路径
        const relativePath = path.relative(mdFileDir, fileSystemPath);

        return relativePath;
      }
    );

    // 修复双引号问题
    htmlContent = htmlContent.replace(/""/g, '"');

    // 包装到我们的模板中
    const outputPath = filePath.replace(".md", ".html");
    const relativePath = path.relative(path.dirname(outputPath), "");

    // 为文章页面添加返回按钮（不是索引页，也不是主页）
    const folderName = path.dirname(filePath).split(path.sep).pop();
    const isArticlePage =
      folderName !== "." &&
      navItems.some((item) => item.folder === folderName) &&
      !navItems.find((item) => item.folder === folderName)?.isHome;

    let finalContent = htmlContent;
    if (isArticlePage) {
      // 在文章内容开头添加返回按钮
      const backButton = `<a href="index.html" class="back-button">← 返回${
        navItems.find((item) => item.folder === folderName).name
      }</a>`;
      finalContent = backButton + htmlContent;
    }

    const fullHTML = generateHTML(title, finalContent, relativePath);

    await fs.writeFile(outputPath, fullHTML);
    console.log(`生成成功: ${outputPath}`);

    return {
      title,
      date: attributes.date,
      tags: attributes.tags,
      excerpt: attributes.excerpt,
      image: attributes.image, // 添加image字段
    };
  } catch (error) {
    console.error(`处理文件 ${filePath} 时出错:`, error);
    throw error;
  }
}

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
    const result = await engine.parseMD(body, {});
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

    // 没有语言的 code 也加 hljs
    htmlContent = htmlContent.replace(
      /<pre><code(?!.*hljs)/g,
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

    // 处理相对路径图片
    htmlContent = htmlContent.replace(
      /file:\/\/\/[^"]*\.(jpg|png|gif|svg)/g,
      (absolutePath) => {
        const fileSystemPath = absolutePath.replace("file://", "");
        return path.relative(mdFileDir, fileSystemPath);
      }
    );

    htmlContent = htmlContent.replace(/""/g, '"');

    // 返回按钮
    const folderName = path.dirname(filePath).split(path.sep).pop();
    const parentFolder = path.dirname(filePath).split(path.sep).slice(-2, -1)[0];
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
    const relativePath = path.relative(path.dirname(outputPath), "");

    const fullHTML = generateHTML(title, finalContent, relativePath);
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
    const homeHtmlPath = homeArticle.articlePath.replace('.md', '.html');
    const indexContent = await fs.readFile(homeHtmlPath, "utf8");

    // 提取main标签内的内容
    const mainContentMatch = indexContent.match(/<main>([\s\S]*?)<\/main>/);
    if (mainContentMatch && mainContentMatch[1]) {
      let mainContent = mainContentMatch[1];

      // 修复相对路径链接
      mainContent = mainContent.replace(
        /file:\/\/\//g,
        "./"
      );
      mainContent = mainContent.replace(
        /file:\/\/\/\//g,
        "./"
      );

      // 获取最新文章（只从技术文章中获取，按日期排序的前3篇），排除关于我页面
      const allArticlesSorted = allArticles
        .filter(
          (article) =>
            article.date &&
            article.folder === "articles"
        ) // 只包含有日期的技术文章，排除关于我页面
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
      const indexPath = path.join(itemPath, 'index.md');
      
      if (await fs.pathExists(indexPath)) {
        try {
          // 读取文件内容解析 Front Matter
          const content = await fs.readFile(indexPath, 'utf8');
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
            attributes: attributes
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
              file: 'index.md', // 统一使用 index.md
              folder: folderPath,
              articlePath: articleInfo.path,
              articleFolder: articleInfo.folder
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

      console.log(
        `生成文件夹 ${folderPath} 的页面: ${articles.length} 篇文章`
      );

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
