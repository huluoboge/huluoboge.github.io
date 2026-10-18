'use strict';
const { test } = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const { readArticles, decorateHTML } = require('../apply-blog-navigation');
const { buildArticleDiscoveryHTML } = require('../../tools/blog-renderer/src/site/index-pages');
const topics = [{ slug: 'paper-reading', name: '论文解读' }, { slug: 'geometry', name: '几何' }, { slug: 'life', name: '生活随记' }];
const articles = new Map([['sample', { categories: ['paper-reading', 'geometry'], draft: false }]]);
const article = { slug: 'sample', title: '样例', folder: 'articles', date: '2026-10-18', categories: ['paper-reading', 'geometry'] };

test('主题页同时提供博客首页和文章分类入口', () => {
  const source = '<a class="back-button" href="../index.html">← 返回文章分类</a>';
  const result = decorateHTML(source, articles, '', topics);
  assert.match(result, /href="..\/..\/index.html">← 博客首页/);
  assert.match(result, /href="..\/index.html">文章分类/);
  assert.equal(decorateHTML(result, articles, '', topics), result);
});

test('渲染器首页改为搜索加统一主题导航，保留文章与数量，可重复执行', () => {
  const source = buildArticleDiscoveryHTML([article], topics);
  const result = decorateHTML(source, articles, 'static/js/article-discovery.js', topics);
  assert.match(result, /data-topic-navigation/);
  assert.match(result, /data-article-topic="paper-reading" aria-pressed="false">论文解读<span class="topic-count">1/);
  assert.match(result, /data-article-topic="life" aria-pressed="false">生活随记<span class="topic-count">0/);
  assert.match(result, /data-article-topic="geometry"/);
  assert.match(result, /data-article-search/);
  assert.match(result, /aria-live="polite"/);
  assert.match(result, /articles\/sample\/index.html/);
  assert.match(result, /paper-reading\/index.html">论文解读<\/a>/);
  assert.doesNotMatch(result, />paper-reading<\/a>/);
  assert.match(result, /src="static\/js\/article-discovery.js" defer/);
  assert.doesNotMatch(result, /<select|category-card|data-article-type|研究笔记/);
  assert.equal(decorateHTML(result, articles, 'static/js/article-discovery.js', topics), result);
});

test('论文标签与技术主题并存，专题补充保留技术主题', () => {
  const all = readArticles(path.resolve(__dirname, '../../blog'));
  assert.equal(all.get('bspline-continuous-time-slam').categories.includes('paper-reading'), false);
  assert.equal(all.get('superglue-attentional-gnn').categories.includes('paper-reading'), false);
  assert.deepEqual(all.get('superglue').categories, ['paper-reading', 'local-features', 'geometry']);
});

test('点击不同主题切换，搜索在当前主题内生效，空结果与恢复正确', () => {
  function control(value = '') { return { value, events: {}, addEventListener(event, fn) { this.events[event] = fn; } }; }
  const search = control();
  const buttons = ['', 'paper-reading', 'geometry', 'life'].map(value => Object.assign(control(), {
    dataset: { articleTopic: value }, setAttribute(name, value) { this[name] = value; }
  }));
  const click = value => buttons.find(b => b.dataset.articleTopic === value).events.click();
  const count = {}, empty = {};
  const items = [
    { dataset: { search: 'superglue attention', category: 'paper-reading geometry features' } },
    { dataset: { search: 'superglue gnn', category: 'geometry' } },
    { dataset: { search: 'bspline', category: 'state-estimation' } },
  ];
  const controls = { '[data-article-search]': search, '[data-article-count]': count, '[data-article-empty]': empty };
  const root = { querySelector: s => controls[s], querySelectorAll: s => s === '[data-article-topic]' ? buttons : items };
  vm.runInNewContext(fs.readFileSync(path.resolve(__dirname, '../../blog/static/js/article-discovery.js'), 'utf8'), { document: { querySelectorAll: () => [root] } });
  assert.equal(count.textContent, '3 篇文章');
  click('paper-reading');
  assert.deepEqual(items.map(i => i.hidden), [false, true, true]);
  click('geometry');
  assert.deepEqual(items.map(i => i.hidden), [false, false, true]);
  assert.equal(buttons[2]['aria-pressed'], 'true');
  assert.equal(buttons[1]['aria-pressed'], 'false');
  search.value = ' GNN '; search.events.input();
  assert.deepEqual(items.map(i => i.hidden), [true, false, true]);
  click('life');
  assert.equal(count.textContent, '0 篇文章'); assert.equal(empty.hidden, false);
  search.value = ''; click('');
  assert.equal(count.textContent, '3 篇文章'); assert.equal(empty.hidden, true);
});
