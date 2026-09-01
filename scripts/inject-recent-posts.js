#!/usr/bin/env node
/**
 * 从构建好的博客提取最新文章，注入主页 index.html 的 #recent-posts 区块。
 * 在 blog-renderer build 之后运行（本地脚本与 CI 都用）。
 * 用法: node scripts/inject-recent-posts.js [--limit N] [--blog-dir blog] [--home index.html]
 *
 * 数据来源：blog/articles/index.html（分类索引页，含文章列表）而非首页，
 * 首页列表可能被 homepage.latest_articles_count 截断。
 */

"use strict";

const fs = require("fs");
const path = require("path");

const REPO_ROOT = path.resolve(__dirname, "..");

function parseArgs(argv) {
  const opts = { limit: 3, blogDir: "blog", home: "index.html" };
  for (let i = 0; i < argv.length; i++) {
    if (argv[i] === "--limit" && argv[i + 1]) opts.limit = parseInt(argv[i + 1], 10) || 3;
    else if (argv[i] === "--blog-dir" && argv[i + 1]) opts.blogDir = argv[i + 1];
    else if (argv[i] === "--home" && argv[i + 1]) opts.home = argv[i + 1];
  }
  return opts;
}

/** 规范化日期：Date toString（如 "Sun Aug 30 2026 08:00:00 GMT+0800"）→ "2026-08-30" */
function normalizeDate(raw) {
  const s = String(raw || "").trim();
  // 已是 ISO 或 YYYY-MM-DD
  if (/^\d{4}-\d{2}-\d{2}/.test(s)) return s.slice(0, 10);
  // JS Date toString 格式
  const m = s.match(/(\w{3}) (\w{3}) (\d{2}) (\d{4})/);
  if (!m) return s;
  const months = { Jan: "01", Feb: "02", Mar: "03", Apr: "04", May: "05", Jun: "06",
                   Jul: "07", Aug: "08", Sep: "09", Oct: "10", Nov: "11", Dec: "12" };
  return `${m[4]}-${months[m[2]]}-${m[3]}`;
}

/**
 * 从博客首页/索引页 HTML 提取文章条目 [{title, href, date, tags}]
 * 支持两种结构：
 *   - 分类索引页: <h3><a href="slug/index.html">title</a></h3>
 *   - 博客首页完整列表: <h3><a href="articles/slug/index.html">title</a></h3>
 */
function extractArticles(html) {
  const items = [];
  const itemRe = /<div class="article-item[^"]*">([\s\S]*?)<\/div>\s*<\/div>/g;
  let m;
  while ((m = itemRe.exec(html)) !== null) {
    const block = m[1];
    const linkRe = /<a href="([^"]+)">([^<]+)<\/a>/;
    const l = block.match(linkRe);
    if (!l) continue;
    let href = l[1];
    const title = l[2].trim();
    // 首页完整列表的 href 带 articles/ 前缀，去掉前缀得到相对路径
    if (href.startsWith("articles/")) href = href.slice("articles/".length);
    const metaRe = /发布于:\s*([^<|]+)/;
    const meta = block.match(metaRe);
    const tagsRe = /标签:\s*([^<]+)/;
    const tags = block.match(tagsRe);
    items.push({
      title,
      href: href.replace(/\.md$/, ".html"),
      date: normalizeDate(meta ? meta[1] : ""),
      tags: tags ? tags[1].trim() : "",
    });
  }
  return items;
}

/** 生成主页 note-list 风格 HTML（与 styles.css .note-list 匹配） */
function buildListHTML(items) {
  return items
    .map(
      (item) => `<li>
        <time>${item.date}</time>
        <a href="blog/articles/${item.href}">${item.title}</a>
        ${item.tags ? `<span>${item.tags.split(",")[0].trim()}</span>` : ""}
      </li>`
    )
    .join("\n        ");
}

function main() {
  const opts = parseArgs(process.argv.slice(2));
  // 文章列表来源：优先博客首页（含完整列表 all-articles-placeholder），
  // 回退分类索引页（旧结构，导航含 articles 分类时存在）
  const blogHome = path.join(REPO_ROOT, opts.blogDir, "index.html");
  const legacyIndex = path.join(REPO_ROOT, opts.blogDir, "articles", "index.html");
  const blogIndex = fs.existsSync(blogHome) ? blogHome : legacyIndex;
  const homePath = path.join(REPO_ROOT, opts.home);

  if (!fs.existsSync(blogIndex)) {
    console.error(`[inject] 未找到 ${blogIndex}（先运行构建）`);
    process.exit(1);
  }
  const homeHtml = fs.readFileSync(homePath, "utf8");
  if (!homeHtml.includes('id="recent-posts"')) {
    console.error("[inject] 主页缺少 #recent-posts 占位符");
    process.exit(1);
  }

  const items = extractArticles(fs.readFileSync(blogIndex, "utf8")).slice(0, opts.limit);
  const listHtml = buildListHTML(items);

  const updated = homeHtml.replace(
    /(<div id="recent-posts">)([\s\S]*?)(<\/div>)/,
    `$1\n        <ul class="note-list blog-posts">\n        ${listHtml}\n        </ul>\n      $3`
  );

  fs.writeFileSync(homePath, updated);
  console.log(`[inject] 主页注入 ${items.length} 篇最新文章`);
}

// CLI 入口：仅作为主模块执行时运行（require 导入不触发）
if (require.main === module) {
  main();
}

module.exports = { extractArticles, buildListHTML, normalizeDate };
