#!/usr/bin/env node

const { renderAll } = require('./render.js');
const fs = require('fs-extra');
const path = require('path');
const yaml = require('yaml');

// 读取配置文件
async function loadConfig() {
  try {
    const configContent = await fs.readFile('config.yml', 'utf8');
    return yaml.parse(configContent);
  } catch (error) {
    console.error('加载配置文件失败:', error);
    // 默认配置
    return {
      navigation: [
        { name: "首页", path: "/", folder: "home", isHome: true, type: "page" },
        { name: "技术文章", path: "/articles/", folder: "articles", type: "articles" },
        { name: "随笔", path: "/blog/", folder: "blog", type: "blog" },
        { name: "开源项目", path: "/projects/", folder: "projects", type: "projects" }
      ]
    };
  }
}

async function buildToDist() {
  console.log('开始构建到dist目录...');
  
  // 加载配置文件
  const config = await loadConfig();
  const navItems = config.navigation || [];
  
  // 清理dist目录
  const distDir = 'dist';
  if (await fs.pathExists(distDir)) {
    await fs.remove(distDir);
  }
  await fs.ensureDir(distDir);
  
  try {
    // 首先在源代码目录运行构建
    console.log('在源代码目录生成HTML文件...');
    await renderAll();
    
    // 从配置中获取需要复制的文件夹
    const foldersToCopy = navItems.map(item => item.folder);
    const itemsToCopy = [
      // HTML文件
      'index.html',
      // 静态资源
      'static',
      // 配置文件夹
      ...foldersToCopy
    ];
    
    console.log('复制文件到dist目录...');
    
    // 复制所有指定的项目和文件夹
    const copyPromises = itemsToCopy.map(async item => {
      if (await fs.pathExists(item)) {
        await fs.copy(item, path.join(distDir, item));
        console.log(`已复制: ${item}`);
      }
    });
    
    await Promise.all(copyPromises);
    
    // 清理源代码目录中的HTML文件
    console.log('清理源代码目录中的构建产物...');
    
    // 从配置中获取需要清理的文件夹
    const foldersToCleanup = navItems.map(item => item.folder);
    const cleanupItems = [
      'index.html',
      ...foldersToCleanup.map(folder => `${folder}/*.html`)
    ];
    
    const cleanupPromises = cleanupItems.map(pattern => {
      return fs.remove(pattern).catch(() => {}); // 忽略不存在的文件
    });
    
    await Promise.all(cleanupPromises);
    
    // 额外清理：递归删除所有文件夹中的HTML文件
    for (const folder of foldersToCleanup) {
      if (await fs.pathExists(folder)) {
        // 递归查找所有HTML文件
        const findHtmlFiles = async (dir) => {
          const items = await fs.readdir(dir);
          const htmlFiles = [];
          
          for (const item of items) {
            const itemPath = path.join(dir, item);
            const stat = await fs.stat(itemPath);
            
            if (stat.isDirectory()) {
              // 递归查找子目录
              const subHtmlFiles = await findHtmlFiles(itemPath);
              htmlFiles.push(...subHtmlFiles);
            } else if (item.endsWith('.html')) {
              htmlFiles.push(itemPath);
            }
          }
          
          return htmlFiles;
        };
        
        const htmlFiles = await findHtmlFiles(folder);
        for (const file of htmlFiles) {
          await fs.remove(file).catch(() => {});
          console.log(`已清理: ${file}`);
        }
      }
    }
    
    console.log('构建完成！构建产物已输出到 dist/ 目录');
    
    // 确保进程正确退出
    process.exit(0);
    
  } catch (error) {
    console.error('构建过程中发生错误:', error);
    process.exit(1);
  }
}

// 执行构建
if (require.main === module) {
  buildToDist().catch(error => {
    console.error('构建失败:', error);
    process.exit(1);
  });
}

module.exports = { buildToDist };
