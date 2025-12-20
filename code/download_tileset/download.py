#!/usr/bin/env python3
"""
3D Tiles爬虫 - 下载tileset协议模型文件
支持递归下载所有引用的child tileset和glb/b3dm文件
"""

import os
import json
import requests
import argparse
import urllib.parse
from pathlib import Path
from typing import Dict, List, Optional, Set
import logging
from dataclasses import dataclass
import time

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class TileContent:
    """表示tile内容"""
    uri: str
    bounding_volume: Optional[Dict] = None
    group: Optional[int] = None

@dataclass
class Tile:
    """表示一个tile"""
    bounding_volume: Optional[Dict] = None
    geometric_error: Optional[float] = None
    refine: Optional[str] = None
    content: Optional[TileContent] = None
    contents: Optional[List[TileContent]] = None
    children: Optional[List['Tile']] = None
    transform: Optional[List[float]] = None

class TilesetDownloader:
    """3D Tiles下载器"""
    
    def __init__(self, base_url: str, output_dir: str, max_depth: int = 10):
        """
        初始化下载器
        
        Args:
            base_url: tileset.json的基础URL
            output_dir: 输出目录
            max_depth: 最大递归深度
        """
        self.base_url = base_url.rstrip('/')
        self.output_dir = Path(output_dir)
        self.max_depth = max_depth
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
        # 创建输出目录
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # 跟踪已下载的文件避免重复
        self.downloaded_files: Set[str] = set()
        
    def download_tileset(self, tileset_url: Optional[str] = None, depth: int = 0) -> Dict:
        """
        下载tileset及其所有引用的文件
        
        Args:
            tileset_url: tileset.json的URL（如果为None则使用base_url）
            depth: 当前递归深度
            
        Returns:
            解析后的tileset数据
        """
        if depth > self.max_depth:
            logger.warning(f"达到最大递归深度 {self.max_depth}")
            return {}
            
        if tileset_url is None:
            tileset_url = f"{self.base_url}/tileset.json"
        
        logger.info(f"下载tileset: {tileset_url} (深度: {depth})")
        
        try:
            # 下载tileset.json
            tileset_data = self._download_json(tileset_url)
            if not tileset_data:
                return {}
                
            # 保存tileset.json
            relative_path = self._get_relative_path(tileset_url)
            local_path = self.output_dir / relative_path
            local_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(local_path, 'w', encoding='utf-8') as f:
                json.dump(tileset_data, f, indent=2)
            logger.info(f"保存tileset到: {local_path}")
            
            # 处理root tile
            if 'root' in tileset_data:
                self._process_tile(tileset_data['root'], tileset_url, depth)
            
            return tileset_data
            
        except Exception as e:
            logger.error(f"下载tileset失败 {tileset_url}: {e}")
            return {}
    
    def _process_tile(self, tile_data: Dict, parent_url: str, depth: int):
        """处理单个tile及其内容"""
        try:
            # 处理单个content
            if 'content' in tile_data and tile_data['content']:
                content_data = tile_data['content']
                self._process_content(content_data, parent_url)
            
            # 处理多个contents
            if 'contents' in tile_data and tile_data['contents']:
                for content_data in tile_data['contents']:
                    self._process_content(content_data, parent_url)
            
            # 递归处理children
            if 'children' in tile_data and tile_data['children']:
                for child_data in tile_data['children']:
                    self._process_tile(child_data, parent_url, depth)
                    
        except Exception as e:
            logger.error(f"处理tile失败: {e}")
    
    def _process_content(self, content_data: Dict, parent_url: str):
        """处理tile内容"""
        if 'uri' not in content_data:
            return
            
        content_uri = content_data['uri']
        
        # 检查是否是外部tileset引用
        if content_uri.endswith('.json') or 'tileset.json' in content_uri:
            # 递归下载外部tileset
            external_url = self._resolve_url(content_uri, parent_url)
            self.download_tileset(external_url, depth=1)
        else:
            # 下载模型文件 (glb, b3dm, i3dm, pnts, cmpt等)
            self._download_model_file(content_uri, parent_url)
    
    def _download_model_file(self, file_uri: str, parent_url: str):
        """下载模型文件"""
        file_url = self._resolve_url(file_uri, parent_url)
        
        # 检查是否已下载
        if file_url in self.downloaded_files:
            logger.debug(f"文件已下载，跳过: {file_url}")
            return
            
        logger.info(f"下载模型文件: {file_url}")
        
        try:
            response = self.session.get(file_url, stream=True, timeout=30)
            response.raise_for_status()
            
            # 确定文件扩展名
            parsed_url = urllib.parse.urlparse(file_url)
            filename = Path(parsed_url.path).name
            
            # 如果没有扩展名，尝试从Content-Type推断
            content_type = response.headers.get('Content-Type', '')
            if '.' not in filename:
                if 'gltf' in content_type or 'glb' in content_type:
                    filename = f"{filename}.glb"
                elif 'octet-stream' in content_type:
                    filename = f"{filename}.b3dm"
            
            # 保存文件
            relative_path = self._get_relative_path(file_url)
            local_path = self.output_dir / relative_path
            local_path.parent.mkdir(parents=True, exist_ok=True)
            
            total_size = 0
            with open(local_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        total_size += len(chunk)
            
            self.downloaded_files.add(file_url)
            logger.info(f"文件保存到: {local_path} ({total_size} bytes)")
            
            # 如果是glTF JSON文件，可能需要下载关联的bin和纹理文件
            if filename.endswith('.gltf') or filename.endswith('.glb'):
                self._process_gltf_assets(local_path, file_url)
                
        except Exception as e:
            logger.error(f"下载文件失败 {file_url}: {e}")
    
    def _process_gltf_assets(self, gltf_path: Path, gltf_url: str):
        """处理glTF文件的关联资源"""
        try:
            if gltf_path.suffix == '.glb':
                # GLB是二进制格式，不需要额外处理
                return
                
            with open(gltf_path, 'r', encoding='utf-8') as f:
                gltf_data = json.load(f)
            
            base_url = str(Path(gltf_url).parent)
            
            # 下载buffers
            if 'buffers' in gltf_data:
                for buffer in gltf_data['buffers']:
                    if 'uri' in buffer:
                        buffer_uri = buffer['uri']
                        if not buffer_uri.startswith('data:'):  # 跳过data URI
                            self._download_model_file(buffer_uri, base_url)
            
            # 下载images
            if 'images' in gltf_data:
                for image in gltf_data['images']:
                    if 'uri' in image:
                        image_uri = image['uri']
                        if not image_uri.startswith('data:'):  # 跳过data URI
                            self._download_model_file(image_uri, base_url)
                            
        except Exception as e:
            logger.error(f"处理glTF资源失败 {gltf_path}: {e}")
    
    def _download_json(self, url: str) -> Optional[Dict]:
        """下载JSON文件"""
        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"下载JSON失败 {url}: {e}")
            return None
    
    def _resolve_url(self, uri: str, base_url: str) -> str:
        """解析相对URI为完整URL"""
        if uri.startswith(('http://', 'https://')):
            return uri
        
        if uri.startswith('data:'):
            return uri  # data URI，不需要下载
            
        # 处理相对路径
        base_parsed = urllib.parse.urlparse(base_url)
        
        if uri.startswith('/'):
            # 绝对路径
            return f"{base_parsed.scheme}://{base_parsed.netloc}{uri}"
        else:
            # 相对路径
            base_path = str(Path(base_parsed.path).parent)
            resolved_path = str(Path(base_path) / uri).replace('\\', '/')
            return f"{base_parsed.scheme}://{base_parsed.netloc}{resolved_path}"
    
    def _get_relative_path(self, url: str) -> Path:
        """从URL获取相对路径"""
        parsed = urllib.parse.urlparse(url)
        path = parsed.path.lstrip('/')
        
        # 移除查询参数和片段
        path = path.split('?')[0].split('#')[0]
        
        # 如果路径为空，使用默认文件名
        if not path:
            if 'tileset.json' in url:
                path = 'tileset.json'
            else:
                path = 'unknown_file'
        
        return Path(path)

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='3D Tiles爬虫 - 下载tileset协议模型文件')
    parser.add_argument('url', help='tileset.json的URL或包含tileset.json的目录URL')
    parser.add_argument('-o', '--output', default='./downloads', help='输出目录 (默认: ./downloads)')
    parser.add_argument('-d', '--depth', type=int, default=10, help='最大递归深度 (默认: 10)')
    parser.add_argument('-v', '--verbose', action='store_true', help='详细输出')
    
    args = parser.parse_args()
    
    if args.verbose:
        logger.setLevel(logging.DEBUG)
    
    logger.info(f"开始下载: {args.url}")
    logger.info(f"输出目录: {args.output}")
    logger.info(f"最大深度: {args.depth}")
    
    downloader = TilesetDownloader(args.url, args.output, args.depth)
    
    start_time = time.time()
    downloader.download_tileset()
    end_time = time.time()
    
    logger.info(f"下载完成!")
    logger.info(f"总耗时: {end_time - start_time:.2f}秒")
    logger.info(f"下载文件数: {len(downloader.downloaded_files)}")

if __name__ == '__main__':
    main()
