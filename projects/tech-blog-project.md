---
title: "技术博客模板"
date: 2025-08-23
tags: ["Node.js", "Markdown", "静态网站"]
excerpt: "一个基于Node.js的静态博客模板，支持Markdown格式的文本渲染。"
---

# 技术博客模板

这是一个使用Node.js开发的静态博客模板，主要支持MarkDown格式文章渲染。

项目地址：[https://github.com/huluoboge/blog_demo](https://github.com/huluoboge/blog_demo)

## 项目特性

- ✅ **Markdown支持**：完整的Markdown语法支持
- ✅ **LaTeX数学公式**：行内和块级数学公式渲染
- ✅ **Mermaid图表**：流程图、序列图、类图等多种图表
- ✅ **Front Matter**：支持文章元数据（标题、日期、标签、摘要等）
- ✅ **静态生成**：生成纯静态HTML文件，无需服务器
- ✅ **实时预览**：开发模式下支持文件监听和实时重新生成
- ✅ **响应式设计**：适配各种设备屏幕

## 技术栈

- **Node.js** - 运行时环境
- **Marked** - Markdown解析器
- **Front Matter** - 元数据解析
- **KaTeX** - LaTeX数学公式渲染
- **Mermaid** - 图表生成
- **Chokidar** - 文件监听

## 安装和使用

### 安装依赖
```bash
npm install
```

### 生成静态网站
```bash
npm run build
```

### 开发模式（实时监听）
```bash
npm run dev
```

## 项目结构

```
tech-blog/
├── articles/          # 技术文章
├── blog/             # 博客文章  
├── projects/         # 开源项目
├── about/           # 关于我
├── render.js        # 主渲染脚本
└── package.json     # 项目配置
```

## 文章格式

每篇文章使用YAML front matter来定义元数据：

```yaml
---
title: "文章标题"
date: 2024-01-01
tags: ["标签1", "标签2"]
excerpt: "文章摘要"
image: "lenna.jpg"
---
```



## 贡献指南

欢迎贡献代码！请遵循以下步骤：

1. Fork 本项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建Pull Request



