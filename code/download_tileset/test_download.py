#!/usr/bin/env python3
"""
测试3D Tiles爬虫
"""

import os
import sys
import tempfile
import shutil
from pathlib import Path

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from download import TilesetDownloader

def test_local_tileset():
    """测试本地tileset文件"""
    print("测试本地tileset文件...")
    
    # 创建临时目录
    temp_dir = tempfile.mkdtemp(prefix="tileset_test_")
    output_dir = os.path.join(temp_dir, "output")
    
    try:
        # 创建一个简单的tileset.json测试文件
        test_tileset = {
            "asset": {
                "version": "1.0"
            },
            "geometricError": 500,
            "root": {
                "boundingVolume": {
                    "box": [0, 0, 0, 10, 0, 0, 0, 10, 0, 0, 0, 10]
                },
                "geometricError": 100,
                "refine": "REPLACE",
                "content": {
                    "uri": "test.glb"
                },
                "children": [
                    {
                        "boundingVolume": {
                            "box": [0, 0, 0, 5, 0, 0, 0, 5, 0, 0, 0, 5]
                        },
                        "geometricError": 50,
                        "content": {
                            "uri": "child.b3dm"
                        }
                    }
                ]
            }
        }
        
        # 保存测试文件
        test_dir = os.path.join(temp_dir, "test_tileset")
        os.makedirs(test_dir, exist_ok=True)
        
        tileset_path = os.path.join(test_dir, "tileset.json")
        with open(tileset_path, 'w', encoding='utf-8') as f:
            import json
            json.dump(test_tileset, f, indent=2)
        
        # 创建测试模型文件
        test_glb = os.path.join(test_dir, "test.glb")
        with open(test_glb, 'wb') as f:
            f.write(b"fake glb data")
        
        test_b3dm = os.path.join(test_dir, "child.b3dm")
        with open(test_b3dm, 'wb') as f:
            f.write(b"fake b3dm data")
        
        # 启动一个简单的HTTP服务器来测试
        import threading
        import http.server
        import socketserver
        import socket
        
        # 使用随机可用端口
        os.chdir(test_dir)
        
        # 查找可用端口
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind(('', 0))
        PORT = sock.getsockname()[1]
        sock.close()
        
        handler = http.server.SimpleHTTPRequestHandler
        httpd = socketserver.TCPServer(("", PORT), handler)
        
        server_thread = threading.Thread(target=httpd.serve_forever)
        server_thread.daemon = True
        server_thread.start()
        
        print(f"测试服务器启动在端口 {PORT}")
        
        # 测试下载器
        base_url = f"http://localhost:{PORT}"
        downloader = TilesetDownloader(base_url, output_dir, max_depth=2)
        
        print(f"开始下载测试tileset...")
        result = downloader.download_tileset()
        
        if result:
            print("✓ 下载成功!")
            print(f"下载文件数: {len(downloader.downloaded_files)}")
            
            # 检查文件是否下载
            expected_files = [
                os.path.join(output_dir, "tileset.json"),
                os.path.join(output_dir, "test.glb"),
                os.path.join(output_dir, "child.b3dm")
            ]
            
            for file_path in expected_files:
                if os.path.exists(file_path):
                    print(f"✓ 文件存在: {file_path}")
                else:
                    print(f"✗ 文件缺失: {file_path}")
        else:
            print("✗ 下载失败")
        
        # 停止服务器
        httpd.shutdown()
        
    finally:
        # 清理临时目录
        shutil.rmtree(temp_dir, ignore_errors=True)
        print(f"清理临时目录: {temp_dir}")

def test_example_tileset():
    """测试示例tileset（需要网络连接）"""
    print("\n测试示例tileset（需要网络连接）...")
    
    # 使用Cesium的示例tileset
    example_url = "https://raw.githubusercontent.com/CesiumGS/3d-tiles-samples/main/1.0/TilesetWithDiscreteLOD"
    
    # 创建临时目录用于示例下载
    import tempfile
    temp_dir = tempfile.mkdtemp(prefix="example_download_")
    output_dir = os.path.join(temp_dir, "output")
    
    try:
        downloader = TilesetDownloader(example_url, output_dir, max_depth=3)
        
        print(f"开始下载示例tileset: {example_url}")
        print(f"输出目录: {output_dir}")
        result = downloader.download_tileset()
        
        if result:
            print("✓ 示例下载成功!")
            print(f"下载文件数: {len(downloader.downloaded_files)}")
            
            # 列出下载的文件
            print("\n下载的文件:")
            for file_url in downloader.downloaded_files:
                print(f"  - {file_url}")
            
            # 检查下载的文件
            import glob
            downloaded_files = glob.glob(os.path.join(output_dir, "**"), recursive=True)
            print(f"\n本地文件列表 ({len(downloaded_files)} 个文件):")
            for file_path in downloaded_files:
                if os.path.isfile(file_path):
                    file_size = os.path.getsize(file_path)
                    print(f"  - {os.path.relpath(file_path, output_dir)} ({file_size} bytes)")
        else:
            print("✗ 示例下载失败")
            
    except Exception as e:
        print(f"示例测试出错: {e}")
        print("注意: 这需要网络连接，如果网络不可用可能会失败")
    finally:
        # 清理临时目录
        import shutil
        shutil.rmtree(temp_dir, ignore_errors=True)
        print(f"\n清理临时目录: {temp_dir}")

def main():
    """主测试函数"""
    print("=" * 60)
    print("3D Tiles爬虫测试")
    print("=" * 60)
    
    # 测试1: 本地tileset
    test_local_tileset()
    
    # 测试2: 示例tileset（可选，需要网络）
    try:
        test_example_tileset()
    except KeyboardInterrupt:
        print("\n测试被用户中断")
    except Exception as e:
        print(f"示例测试跳过: {e}")
    
    print("\n" + "=" * 60)
    print("测试完成!")
    print("=" * 60)

if __name__ == '__main__':
    main()
