#!/usr/bin/env node
/**
 * 从已构建的博客索引生成独立的 Recent Posts HTML 片段。
 * 生成文件被 gitignore；首页只加载它，不会被本地构建改写。
 * 用法: node scripts/generate-recent-posts.js [--limit N] [--blog-dir blog] [--output recent-posts.generated.html]
 */

"use strict";

const fs = require("fs");
const path = require("path");

const REPO_ROOT = path.resolve(__dirname, "..");

function parseArgs(argv) {
  const opts = { limit: 8, blogDir: "blog", output: "recent-posts.generated.html" };
  for (let i = 0; i < argv.length; i++) {
    if (argv[i] === "--limit" && argv[i + 1]) opts.limit = parseInt(argv[i + 1], 10) || 8;
    else if (argv[i] === "--blog-dir" && argv[i + 1]) opts.blogDir = argv[i + 1];
    else if (argv[i] === "--output" && argv[i + 1]) opts.output = argv[i + 1];
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
    Jan: "01", Feb: "02", Mar: "03", Apr: "04", May: "05", Jun: "06",
    Jul: "07", Aug: "08", Sep: "09", Oct: "10", Nov: "11", Dec: "12",
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

function extractArticles(html) {
  const fromCards = extractFromArticleItems(html);
  return fromCards.length > 0 ? fromCards : extractFromLatestList(html);
}

function escapeHTML(value) {
  return String(value).replace(/[&<>"']/g, (char) => ({
    "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;",
  })[char]);
}

/** 生成与首页 .note-list 样式匹配的完整 HTML 片段。 */
function buildListHTML(items) {
  const rows = items.map((item) => {
    const tag = item.tags ? `\n        <span>${escapeHTML(item.tags.split(",")[0].trim())}</span>` : "";
    return `      <li>\n        <time>${escapeHTML(item.date)}</time>\n        <a href="blog/articles/${escapeHTML(item.href)}">${escapeHTML(item.title)}</a>${tag}\n      </li>`;
  });
  return `<ul class="note-list blog-posts">\n${rows.join("\n")}\n</ul>\n`;
}

function main() {
  const opts = parseArgs(process.argv.slice(2));
  const blogHome = path.join(REPO_ROOT, opts.blogDir, "index.html");
  const legacyIndex = path.join(REPO_ROOT, opts.blogDir, "articles", "index.html");
  const blogIndex = fs.existsSync(blogHome) ? blogHome : legacyIndex;
  const outputPath = path.resolve(REPO_ROOT, opts.output);

  if (!fs.existsSync(blogIndex)) {
    console.error(`[recent-posts] 未找到 ${blogIndex}（先运行构建）`);
    process.exit(1);
  }

  const items = extractArticles(fs.readFileSync(blogIndex, "utf8")).slice(0, opts.limit);
  if (items.length === 0) {
    console.error("[recent-posts] 未解析到文章，放弃生成片段");
    process.exit(1);
  }

  fs.writeFileSync(outputPath, buildListHTML(items));
  console.log(`[recent-posts] 已生成 ${items.length} 篇文章到 ${path.relative(REPO_ROOT, outputPath)}`);
}

if (require.main === module) main();

module.exports = {
  extractArticles,
  extractFromArticleItems,
  extractFromLatestList,
  buildListHTML,
  escapeHTML,
  normalizeDate,
};
