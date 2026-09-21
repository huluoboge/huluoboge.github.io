"use strict";

const test = require("node:test");
const assert = require("node:assert/strict");
const {
  extractArticles,
  extractFromLatestList,
  normalizeDate,
} = require("./inject-recent-posts.js");

const currentCard = `
<div class="article-item" data-article-item data-search="poisson blending" data-category="image-processing">
  <div class="article-content">
    <h3><a href="articles/poisson-blending/index.html">图像融合经典算法——Poisson 融合</a></h3>
    <div class="article-meta">发布于: 2026-09-21 | 标签: Image Fusion, Poisson Blending | 分类: <a href="categories/image-processing/index.html">图像处理与评价</a></div>
    <p>摘要</p>
  </div>
</div>
<div class="article-item" data-article-item data-search="multiband" data-category="image-processing">
  <div class="article-content">
    <h3><a href="articles/multiband-blending/index.html">图像融合经典算法——多频段融合</a></h3>
    <div class="article-meta">发布于: 2026-09-17 | 标签: Image Fusion, Laplacian Pyramid | 分类: <a href="categories/image-processing/index.html">图像处理与评价</a></div>
    <p>摘要</p>
  </div>
</div>
`;

const legacyCard = `
<div class="article-item">
  <div class="article-content">
    <h3><a href="slug/index.html">旧卡片标题</a></h3>
    <div class="article-meta">发布于: 2026-08-01 | 标签: IMU</div>
  </div>
</div>
`;

const latestList = `
<h2 id="最近文章">最近文章 </h2>
<ul><li><a href="articles/poisson-blending/index.html">图像融合经典算法——Poisson 融合</a> - 2026/9/21</li>
<li><a href="articles/multiband-blending/index.html">图像融合经典算法——多频段融合</a> - 2026/9/17</li></ul>
`;

test("normalizeDate 识别 ISO、斜杠日期和 Date toString", () => {
  assert.equal(normalizeDate("2026-09-21"), "2026-09-21");
  assert.equal(normalizeDate("2026/9/21"), "2026-09-21");
  assert.equal(normalizeDate("Sun Aug 30 2026 08:00:00 GMT+0800"), "2026-08-30");
});

test("解析带 data-* 属性的 article-item 卡片", () => {
  const items = extractArticles(currentCard);
  assert.equal(items.length, 2);
  assert.equal(items[0].title, "图像融合经典算法——Poisson 融合");
  assert.equal(items[0].href, "poisson-blending/index.html");
  assert.equal(items[0].date, "2026-09-21");
  assert.equal(items[0].tags, "Image Fusion, Poisson Blending");
  assert.equal(items[1].href, "multiband-blending/index.html");
});

test("兼容旧的无额外属性卡片", () => {
  const items = extractArticles(legacyCard);
  assert.equal(items.length, 1);
  assert.equal(items[0].href, "slug/index.html");
  assert.equal(items[0].date, "2026-08-01");
});

test("没有卡片时回退到最近文章简表", () => {
  const items = extractArticles(latestList);
  assert.equal(items.length, 2);
  assert.equal(items[0].href, "poisson-blending/index.html");
  assert.equal(items[0].date, "2026-09-21");
  assert.equal(items[1].title, "图像融合经典算法——多频段融合");
});

test("extractFromLatestList 单独解析简表", () => {
  const items = extractFromLatestList(latestList);
  assert.equal(items.length, 2);
});

test("空 HTML 返回空列表", () => {
  assert.deepEqual(extractArticles(""), []);
});
