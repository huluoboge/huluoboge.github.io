#!/usr/bin/env node
"use strict";

// Keep the renderer's normal discovery and index generation, while caching only
// crossnote's expensive Markdown-to-HTML step for unchanged source content.
const crypto = require("node:crypto");
const fs = require("node:fs");
const path = require("node:path");

const repoRoot = path.resolve(__dirname, "..");
const rendererDir = path.join(repoRoot, "tools/blog-renderer");
const cacheDir = path.join(repoRoot, ".cache/blog-renderer");
const siteDir = path.join(repoRoot, "blog");
const renderer = require("../tools/blog-renderer/src/core/renderer");
const { renderAll } = require("../tools/blog-renderer/src/site/build");

function hash(value) {
  return crypto.createHash("sha256").update(value).digest("hex");
}

function engineFingerprint() {
  return [
    "cache-v2",
    fs.readFileSync(path.join(rendererDir, "package-lock.json")),
    fs.readFileSync(path.join(rendererDir, "src/core/renderer.js")),
    fs.readFileSync(path.join(rendererDir, "src/core/config.js")),
    fs.readFileSync(path.join(rendererDir, "src/core/codeblock.js")),
  ].map((part) => Buffer.isBuffer(part) ? part.toString("base64") : part).join("\n");
}

async function main() {
  const fingerprint = hash(engineFingerprint());
  const originalRenderMarkdown = renderer.renderMarkdown;
  let cacheHits = 0;
  let cacheMisses = 0;

  await fs.promises.mkdir(cacheDir, { recursive: true });
  renderer.renderMarkdown = async (options) => {
    const sourcePath = path.resolve(options.filePath);
    const sourceId = hash(sourcePath);
    const entryPath = path.join(cacheDir, `${sourceId}.json`);
    const key = hash(JSON.stringify({
      fingerprint,
      sourcePath,
      content: options.content,
      config: options.config || {},
      parseOptions: options.parseOptions || {},
      notebookPath: options.notebookPath || "",
    }));

    try {
      const cached = JSON.parse(await fs.promises.readFile(entryPath, "utf8"));
      if (cached.key === key && typeof cached.result?.html === "string") {
        cacheHits += 1;
        return cached.result;
      }
    } catch {
      // Missing or invalid cache entries are rendered normally below.
    }

    const result = await originalRenderMarkdown(options);
    await fs.promises.writeFile(entryPath, JSON.stringify({ key, result }));
    cacheMisses += 1;
    return result;
  };

  try {
    await renderAll({ cwd: siteDir });
  } finally {
    renderer.renderMarkdown = originalRenderMarkdown;
  }

  console.log(`[blog-cache] Markdown 渲染缓存：命中 ${cacheHits}，重新渲染 ${cacheMisses}`);
}

main().catch((error) => {
  console.error("[blog-cache] 构建失败:", error);
  process.exitCode = 1;
});
