#!/usr/bin/env node
/**
 * 从构建好的博客提取最新文章，注入主页 index.html 的 #recent-posts 区块。
 * 在 blog-renderer build 之后运行（本地脚本与 CI 都用）。
 * 用法: node scripts/inject-recent-posts.js [--limit N] [--blog-dir blog] [--home index.html]
 *
 * 数据来源：优先 blog/index.html 里的 article-item 卡片（按日期排序的完整列表），
 * 解析失败时回退到「最近文章」简表；再回退 blog/articles/index.html。
 */

"use strict";

const fs = require("fs");
const path = require("path");

const REPO_ROOT = path.resolve(__dirname, "..");

function parseArgs(argv) {
  const opts = { limit: 8, blogDir: "blog", home: "index.html" };
  for (let i = 0; i < argv.length; i++) {
    if (argv[i] === "--limit" && argv[i + 1]) opts.limit = parseInt(argv[i + 1], 10) || 8;
    else if (argv[i] === "--blog-dir" && argv[i + 1]) opts.blogDir = argv[i + 1];
    else if (argv[i] === "--home" && argv[i + 1]) opts.home = argv[i + 1];
  }
  return opts;
}

/** 规范化日期：ISO、斜杠日期或 Date toString → "YYYY-MM-DD" */
function normalizeDate(raw) {
  const s = String(raw || "").trim();
  if (/^\d{4}-\d{2}-\d{2}/.test(s)) return s.slice(0, 10);
  const slash = s.match(/^(\d{4})\/(\d{1,2})\/(\d{1,2})/);
  if (slash) {
    return `${slash[1]}-${slash[2].padStart(2, "0")}-${slash[3].padStart(2, "0")}`;
  }
  const m = s.match(/(\w{3}) (\w{3}) (\d{2}) (\d{4})/);
  if (!m) return s;
  const months = {
    Jan: "01",
    Feb: "02",
    Mar: "03",
    Apr: "04",
    May: "05",
    Jun: "06",
    Jul: "07",
    Aug: "08",
    Sep: "09",
    Oct: "10",
    Nov: "11",
    Dec: "12",
  };
  return `${m[4]}-${months[m[2]]}-${m[3]}`;
}

function articleHref(href) {
  let value = String(href || "").replace(/\.md$/, ".html");
  if (value.startsWith("articles/")) value = value.slice("articles/".length);
  return value;
}

function extractFromArticleItems(html) {
  const items = [];
  const itemRe =
    /<div class="article-item\b[^"]*"[^>]*>[\s\S]*?<h3><a href="([^"]+)">([^<]+)<\/a><\/h3>[\s\S]*?<div class="article-meta">([\s\S]*?)<\/div>/g;
  let m;
  while ((m = itemRe.exec(html)) !== null) {
    const meta = m[3];
    const date = meta.match(/发布于:\s*([^<|]+)/);
    const tags = meta.match(/标签:\s*([^<|]+)/);
    items.push({
      title: m[2].trim(),
      href: articleHref(m[1]),
      date: normalizeDate(date ? date[1] : ""),
      tags: tags ? tags[1].trim() : "",
    });
  }
  return items;
}

function extractFromLatestList(html) {
  const section = html.match(/<h2[^>]*>\s*最近文章[\s\S]*?<ul>([\s\S]*?)<\/ul>/);
  if (!section) return [];
  const items = [];
  const itemRe = /<li><a href="([^"]+)">([^<]+)<\/a>\s*[-–—]\s*([^<]+)<\/li>/g;
  let m;
  while ((m = itemRe.exec(section[1])) !== null) {
    items.push({
      title: m[2].trim(),
      href: articleHref(m[1]),
      date: normalizeDate(m[3]),
      tags: "",
    });
  }
  return items;
}

/**
 * 从博客首页/索引页 HTML 提取文章条目 [{title, href, date, tags}]
 * 卡片列表按日期降序；简表本身已是最新若干篇。
 */
function extractArticles(html) {
  const fromCards = extractFromArticleItems(html);
  if (fromCards.length > 0) return fromCards;
  return extractFromLatestList(html);
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
  if (items.length === 0) {
    console.error("[inject] 未解析到文章，放弃改写主页");
    process.exit(1);
  }
  const listHtml = buildListHTML(items);

  const updated = homeHtml.replace(
    /(<div id="recent-posts">)([\s\S]*?)(<\/div>)/,
    `$1\n        <ul class="note-list blog-posts">\n        ${listHtml}\n        </ul>\n      $3`
  );

  fs.writeFileSync(homePath, updated);
  console.log(`[inject] 主页注入 ${items.length} 篇最新文章`);
}

if (require.main === module) {
  main();
}

module.exports = {
  extractArticles,
  extractFromArticleItems,
  extractFromLatestList,
  buildListHTML,
  normalizeDate,
};
