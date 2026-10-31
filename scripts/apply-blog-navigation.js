#!/usr/bin/env node
'use strict';

// 站点专用的导航扩展，避免改动共享的 blog-renderer submodule。
const fs = require('node:fs');
const path = require('node:path');
const frontMatter = require('../tools/blog-renderer/node_modules/front-matter');
const YAML = require('../tools/blog-renderer/node_modules/yaml');

function readArticles(blogDir) {
  const articles = new Map();
  for (const entry of fs.readdirSync(path.join(blogDir, 'articles'), { withFileTypes: true })) {
    const source = path.join(blogDir, 'articles', entry.name, 'index.md');
    if (!entry.isDirectory() || !fs.existsSync(source)) continue;
    const { attributes } = frontMatter(fs.readFileSync(source, 'utf8'));
    const raw = attributes.categories ?? attributes.category ?? [];
    const categories = Array.isArray(raw) ? raw : [raw];
    const title = String(attributes.title || entry.name);
    const inferredPaperReading = categories.some(category => ['paper-reading', '论文解读'].includes(String(category).toLowerCase()))
      || /(?:论文解读|论文翻译|文章翻译|论文总结|论文综述)$/.test(title);
    const isPaperReading = attributes.kind === 'paper-reading'
      || (!attributes.kind && inferredPaperReading);
    articles.set(entry.name, {
      title,
      date: attributes.date,
      categories,
      section: attributes.section === 'life' ? 'life' : 'work',
      kind: isPaperReading ? 'paper-reading' : 'technical',
      pinned: attributes.pinned === true,
      draft: attributes.draft === true,
    });
  }
  return articles;
}

function escapeHTML(value) {
  return String(value).replace(/[&<>"']/g, char => ({
    '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;',
  })[char]);
}

function formatDate(value) {
  const raw = String(value || '').trim();
  const iso = raw.match(/^\d{4}-\d{2}-\d{2}/);
  if (iso) return iso[0];
  const parsed = new Date(raw);
  return Number.isNaN(parsed.getTime()) ? raw : parsed.toISOString().slice(0, 10);
}

function buildRecentTechnicalList(articles, limit = 5) {
  const recent = [...articles.entries()]
    .map(([slug, article]) => ({ slug, ...article }))
    .filter(article => !article.draft && article.section === 'work' && article.kind === 'technical' && article.date)
    .sort((a, b) => Number(b.pinned) - Number(a.pinned) || new Date(b.date) - new Date(a.date))
    .slice(0, limit);
  const rows = recent.map(article =>
    `<li><a href="articles/${escapeHTML(article.slug)}/index.html">${escapeHTML(article.title)}</a> - ${escapeHTML(formatDate(article.date))}</li>`
  ).join('\n');
  return `<h2 id="近期技术文章">近期技术文章</h2>\n<ul>${rows}</ul>`;
}

function decorateHTML(html, articles, scriptPath, topics) {
  // 共享渲染器的卡片仅内置旧主题名称，补齐站点新增主题的显示名称。
  for (const topic of topics) {
    html = html.split(`>${escapeHTML(topic.slug)}</a>`).join(`>${escapeHTML(topic.name)}</a>`);
  }
  html = html.replace(
    '<a class="back-button" href="../index.html">← 返回文章分类</a>',
    '<nav class="article-back-links" aria-label="返回导航"><a class="back-button" href="../../index.html">← 博客首页</a><a class="back-button" href="../index.html">文章分类</a></nav>'
  );
  html = html.replace(/<h2[^>]*id="(?:最近文章|近期技术文章)"[^>]*>[\s\S]*?<\/h2>\s*<ul>[\s\S]*?<\/ul>/, buildRecentTechnicalList(articles));
  if (!html.includes('data-article-discovery') || html.includes('data-topic-navigation')) return html;

  const discovery = /<section class="article-discovery"[\s\S]*?<\/section>\s*<script>[\s\S]*?<\/script>/;
  const original = html.match(discovery)?.[0];
  if (!original) throw new Error('文章筛选结构已变化，请更新导航扩展');
  const list = original.match(/<div class="article-list" data-article-list>([\s\S]*)<\/div>\s*<p class="discovery-empty"/);
  if (!list) throw new Error('未找到文章列表');

  // 根据当前页面实际列出的文章计数，主题数量不随搜索变化。
  const listed = [...list[1].matchAll(/<h3><a href="[^\"]*\/([^/\"]+)\/index\.html">/g)].map(match => {
    const article = articles.get(match[1]);
    if (!article || article.draft) throw new Error(`列表文章缺少有效元数据: ${match[1]}`);
    return article;
  });
  const workArticles = listed.filter(article => article.section === 'work');
  const lifeArticles = listed.filter(article => article.section === 'life');
  const technicalArticles = workArticles.filter(article => article.kind === 'technical');
  const topicDefinitions = [{ slug: '', name: '全部主题' }, ...topics.filter(topic => !['paper-reading', 'life'].includes(topic.slug))];
  const sectionButtons = [
    { slug: 'work', name: '工作', count: workArticles.length },
    { slug: 'life', name: '生活', count: lifeArticles.length },
  ].map(section =>
    `<button type="button" data-article-section="${section.slug}" aria-pressed="${section.slug === 'work'}">${section.name}<span class="topic-count">${section.count}</span></button>`
  ).join('\n');
  const kindButtons = [
    { slug: 'technical', name: '技术文章' },
    { slug: 'paper-reading', name: '论文解读' },
  ].map(kind => {
    const count = workArticles.filter(article => article.kind === kind.slug).length;
    return `<button type="button" data-article-kind="${kind.slug}" aria-pressed="${kind.slug === 'technical'}">${kind.name}<span class="topic-count">${count}</span></button>`;
  }).join('\n');
  const topicButtons = topicDefinitions.map(topic => {
    const count = !topic.slug ? technicalArticles.length : technicalArticles.filter(article =>
      (article.categories.length ? article.categories : ['uncategorized']).includes(topic.slug)).length;
    return `<button type="button" data-article-topic="${escapeHTML(topic.slug)}" aria-pressed="${!topic.slug}">${escapeHTML(topic.name)}<span class="topic-count">${count}</span></button>`;
  }).join('\n');
  let articleIndex = 0;
  const articleList = list[1].replace(/<div class="article-item\b[^>]*data-article-item[^>]*>/g, opening => {
    const article = listed[articleIndex++];
    if (!article) throw new Error('文章卡片与元数据数量不一致');
    const hidden = article.section !== 'work' || article.kind !== 'technical' ? ' hidden' : '';
    return `${opening.slice(0, -1)} data-section="${escapeHTML(article.section)}" data-kind="${escapeHTML(article.kind)}"${hidden}>`;
  });
  if (articleIndex !== listed.length) throw new Error('文章元数据与卡片数量不一致');

  return html.replace(discovery, `<section class="article-discovery" data-article-discovery>
    <div class="discovery-toolbar">
      <label class="discovery-search"><span>搜索文章</span><input type="search" data-article-search placeholder="标题、摘要、标签" autocomplete="off"></label>
      <span class="discovery-count" data-article-count aria-live="polite">${technicalArticles.length} 篇文章</span>
    </div>
    <nav class="topic-navigation" aria-label="按内容分类">
      <span class="topic-navigation-label">内容分类</span>
      <div class="topic-buttons" role="group" aria-label="工作或生活">${sectionButtons}</div>
    </nav>
    <nav class="topic-navigation" data-kind-navigation aria-label="按文章类型">
      <span class="topic-navigation-label">工作内容</span>
      <div class="topic-buttons" role="group" aria-label="技术文章或论文解读">${kindButtons}</div>
    </nav>
    <nav class="topic-navigation" data-topic-navigation aria-label="按主题浏览">
      <span class="topic-navigation-label">按主题浏览</span>
      <div class="topic-buttons" role="group" aria-label="筛选主题">${topicButtons}</div>
    </nav>
    <div class="article-list" data-article-list>${articleList}</div>
    <p class="discovery-empty" data-article-empty hidden>没有匹配的文章。</p>
  </section>
  <script src="${scriptPath}" defer></script>`);
}

function main(blogDir = path.resolve(__dirname, '../blog')) {
  const articles = readArticles(blogDir);
  const topics = YAML.parse(fs.readFileSync(path.join(blogDir, 'config.yml'), 'utf8')).categories || [];
  const script = path.join(blogDir, 'static/js/article-discovery.js');
  function visit(dir) {
    for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
      const file = path.join(dir, entry.name);
      if (entry.isDirectory()) {
        if (!['static', 'figures', 'skills', 'references'].includes(entry.name)) visit(file);
      } else if (entry.name.endsWith('.html') && file !== path.join(blogDir, 'template.html')) {
        const relative = path.relative(blogDir, file).split(path.sep).join('/');
        const slug = relative.match(/^articles\/([^/]+)\/index\.html$/);
        if (slug && articles.get(slug[1])?.draft) continue;
        const html = fs.readFileSync(file, 'utf8');
        const result = decorateHTML(html, articles, path.relative(dir, script).split(path.sep).join('/'), topics);
        if (result !== html) fs.writeFileSync(file, result);
      }
    }
  }
  visit(blogDir);
  console.log('[blog-navigation] 已生成紧凑主题导航与搜索');
}

if (require.main === module) main();
module.exports = { readArticles, decorateHTML };
