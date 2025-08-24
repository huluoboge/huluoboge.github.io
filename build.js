#!/usr/bin/env node

const { renderAll } = require('./render.js');
const fs = require('fs-extra');
const path = require('path');

async function buildToDist() {
  console.log('开始构建到dist目录...');
  
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
    
    // 定义需要复制的文件和文件夹
    const itemsToCopy = [
      // HTML文件
      'index.html',
      // 文件夹
      'about',
      'articles', 
      'blog',
      'projects',
      'static'
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
    const cleanupItems = [
      'index.html',
      'about/*.html',
      'articles/*.html',
      'blog/*.html', 
      'projects/*.html'
    ];
    
    const cleanupPromises = cleanupItems.map(pattern => {
      return fs.remove(pattern).catch(() => {}); // 忽略不存在的文件
    });
    
    await Promise.all(cleanupPromises);
    
    // 额外清理：删除所有文件夹中的HTML文件
    const folders = ['about', 'articles', 'blog', 'projects'];
    for (const folder of folders) {
      if (await fs.pathExists(folder)) {
        const files = await fs.readdir(folder);
        const htmlFiles = files.filter(file => file.endsWith('.html'));
        for (const file of htmlFiles) {
          await fs.remove(path.join(folder, file)).catch(() => {});
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
