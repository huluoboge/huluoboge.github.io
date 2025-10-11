# 博客构建系统说明

## 项目结构

### 源代码目录 (Git管理)
```
blog/
├── about/           # 关于我页面 (Markdown源文件)
├── articles/        # 技术文章 (Markdown源文件)  
├── blog/            # 随笔 (Markdown源文件)
├── projects/        # 开源项目 (Markdown源文件)
├── static/          # 静态资源 (CSS, JS, 图片)
├── render.js        # 博客生成脚本
├── build.js         # 构建到dist目录的脚本
├── package.json     # Node.js依赖配置
└── .gitignore       # Git忽略规则
```

### 构建产物目录 (不纳入Git管理)
```
dist/
├── about/           # 生成的HTML文件
├── articles/        # 生成的HTML文件
├── blog/            # 生成的HTML文件  
├── projects/        # 生成的HTML文件
├── static/          # 静态资源副本
└── index.html       # 主页
```

## 构建命令

### 开发模式 (在源代码目录生成HTML)
```bash
npm run build:clean
```
- 在源代码目录生成HTML文件
- 用于开发和测试
- 生成的文件会与源代码混合

### 生产构建 (输出到dist目录)
```bash
npm run build
```
- 在 `dist/` 目录生成所有构建产物
- 自动清理源代码目录中的HTML文件
- 适合部署使用

### 清理构建产物
```bash
npm run clean
```
- 清理dist目录中的所有文件

## Git管理策略

### 纳入版本控制的文件
- Markdown源文件 (.md)
- JavaScript构建脚本
- 配置文件 (package.json, .gitignore)
- 静态资源文件

### 忽略的文件 (.gitignore)
- 所有HTML文件 (*.html)
- dist/ 目录
- node_modules/ 目录
- 临时文件和IDE文件

## 部署流程

1. **开发阶段**: 编写Markdown内容
2. **构建阶段**: 运行 `npm run build` 生成dist目录
3. **部署阶段**: 将dist目录的内容部署到服务器

## 动态内容功能

博客支持以下动态内容生成：
- ✅ **最新文章**: 自动从articles文件夹获取技术文章
- ✅ **开源项目**: 自动从projects文件夹获取项目信息  
- ✅ **返回按钮**: 所有文章页面都有返回导航按钮

所有内容都是动态生成的，无需手动维护列表。
