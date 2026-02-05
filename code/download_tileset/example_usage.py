#!/usr/bin/env python3
"""
3D Tiles爬虫使用示例
"""

import os
import sys
from pathlib import Path

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from download import TilesetDownloader

def example_1_basic_usage():
    """示例1: 基本用法"""
    print("=" * 60)
    print("示例1: 基本用法")
    print("=" * 60)
    
    # 假设我们有一个tileset在以下URL
    tileset_url = "https://example.com/3d-tiles/tileset.json"
    output_dir = "./my_downloads"
    
    print(f"URL: {tileset_url}")
    print(f"输出目录: {output_dir}")
    
    # 创建下载器
    downloader = TilesetDownloader(
        base_url=tileset_url,
        output_dir=output_dir,
        max_depth=5
    )
    
    # 开始下载
    print("开始下载...")
    result = downloader.download_tileset()
    
    if result:
        print(f"✓ 下载完成!")
        print(f"下载文件数: {len(downloader.downloaded_files)}")
    else:
        print("✗ 下载失败")

def example_2_local_server():
    """示例2: 本地服务器"""
    print("\n" + "=" * 60)
    print("示例2: 本地服务器")
    print("=" * 60)
    
    # 本地开发服务器
    local_url = "http://localhost:8000/tiles"
    output_dir = "./local_tiles"
    
    print(f"URL: {local_url}")
    print(f"输出目录: {output_dir}")
    
    # 创建下载器
    downloader = TilesetDownloader(
        base_url=local_url,
        output_dir=output_dir,
        max_depth=3
    )
    
    print("提示: 确保本地服务器正在运行")
    print("命令示例: python -m http.server 8000")

def example_3_custom_settings():
    """示例3: 自定义设置"""
    print("\n" + "=" * 60)
    print("示例3: 自定义设置")
    print("=" * 60)
    
    tileset_url = "https://data.example.com/3d-models"
    output_dir = "./custom_download"
    
    print(f"URL: {tileset_url}")
    print(f"输出目录: {output_dir}")
    
    # 创建下载器，使用浅层递归
    downloader = TilesetDownloader(
        base_url=tileset_url,
        output_dir=output_dir,
        max_depth=2  # 只下载2层深度
    )
    
    print("设置:")
    print("  - 最大递归深度: 2")
    print("  - 输出目录结构: 保持原始结构")
    print("  - 重复文件: 自动跳过")

def example_4_command_line():
    """示例4: 命令行使用"""
    print("\n" + "=" * 60)
    print("示例4: 命令行使用")
    print("=" * 60)
    
    print("命令行示例:")
    print()
    print("1. 基本下载:")
    print("   python download.py https://example.com/tileset -o ./output")
    print()
    print("2. 限制递归深度:")
    print("   python download.py https://example.com/tileset -o ./output -d 3")
    print()
    print("3. 详细输出:")
    print("   python download.py https://example.com/tileset -o ./output -v")
    print()
    print("4. 查看帮助:")
    print("   python download.py --help")

def example_5_real_world():
    """示例5: 真实世界示例"""
    print("\n" + "=" * 60)
    print("示例5: 真实世界示例")
    print("=" * 60)
    
    # Cesium官方示例
    cesium_example = "https://raw.githubusercontent.com/CesiumGS/3d-tiles-samples/main/1.0/TilesetWithDiscreteLOD"
    output_dir = "./cesium_example"
    
    print("真实世界示例: Cesium 3D Tiles示例")
    print(f"URL: {cesium_example}")
    print(f"输出目录: {output_dir}")
    print()
    print("运行命令:")
    print(f"  python download.py {cesium_example} -o {output_dir} -d 3")
    print()
    print("这将下载:")
    print("  - tileset.json (tileset定义文件)")
    print("  - dragon_low.b3dm (低细节模型)")
    print("  - dragon_medium.b3dm (中细节模型)")
    print("  - dragon_high.b3dm (高细节模型)")

def main():
    """主函数"""
    print("3D Tiles爬虫使用示例")
    print("=" * 60)
    
    example_1_basic_usage()
    example_2_local_server()
    example_3_custom_settings()
    example_4_command_line()
    example_5_real_world()
    
    print("\n" + "=" * 60)
    print("总结")
    print("=" * 60)
    print("""
这个3D Tiles爬虫可以:
1. 递归下载tileset.json文件
2. 自动下载引用的3D模型文件(glb, b3dm等)
3. 处理外部tileset引用
4. 保持原始目录结构
5. 避免重复下载
6. 提供详细的进度日志

使用场景:
- 备份3D Tiles数据
- 离线使用3D模型
- 数据分析和处理
- 测试和开发
    """)

if __name__ == '__main__':
    main()
