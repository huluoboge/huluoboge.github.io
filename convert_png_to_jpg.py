import os
import re
from PIL import Image
import argparse
import subprocess
# from pathlib import Path

# 设置要处理的目录和图片质量
ARTICLES_DIR = 'articles'
QUALITY = 50

'''
sudo apt install pngquant

'''

def find_markdown_files(root_dir):
    """递归查找所有Markdown文件"""
    md_files = []
    for dirpath, _, filenames in os.walk(root_dir):
        for filename in filenames:
            if filename.endswith('.md'):
                md_files.append(os.path.join(dirpath, filename))
    return md_files

def find_png_images(md_file):
    """从Markdown文件中提取所有PNG图片路径"""
    with open(md_file, 'r', encoding='utf-8') as f:
        content = f.read()
    # 匹配 ![alt](path.png) 或 <img src="path.png">
    pattern = r'!\[.*?\]\(([^\)]+\.png)\)|<img [^>]*src=["\']([^"\']+\.png)["\']'
    matches = re.findall(pattern, content, re.IGNORECASE)
    # 结果是元组，取非空项
    png_paths = [m[0] if m[0] else m[1] for m in matches]
    return png_paths, content

def find_jpg_images(md_file):
    with open(md_file, 'r', encoding='utf-8') as f:
        content = f.read()
    pattern = r'!\[.*?\]\(([^\)]+\.jpg)\)|<img [^>]*src=["\']([^"\']+\.jpg)["\']'
    matches = re.findall(pattern, content, re.IGNORECASE)
    jpg_paths = [m[0] if m[0] else m[1] for m in matches]
    return jpg_paths,content

def convert_png_to_jpg(png_path):
    """将PNG图片转换为JPG"""
    jpg_path = png_path[:-4] + '.jpg'
    try:
        with Image.open(png_path) as im:
            # PNG可能有透明通道，需转换为白色背景
            if im.mode in ('RGBA', 'LA'):
                bg = Image.new('RGB', im.size, (255, 255, 255))
                bg.paste(im, mask=im.split()[-1])
                im = bg
            else:
                im = im.convert('RGB')
            im.save(jpg_path, 'JPEG', quality=QUALITY)
        return jpg_path
    except Exception as e:
        print(f'转换失败: {png_path}, 错误: {e}')
        return None

def compress_png(png_path):
    try:
        with Image.open(png_path) as im:
            im.save(png_path, 'PNG', optimize=True)
        print(f'PNG压缩完成: {png_path}')
    except Exception as e:
        print(f'PNG压缩失败: {png_path}, 错误: {e}')

def compress_png_pngquant(png_path):
    """
    使用 pngquant 压缩 PNG 图片
    
    Args:
        png_path (str): PNG 图片的路径
    """
    try:
        # 检查文件是否存在
        if not os.path.exists(png_path):
            print(f'文件不存在: {png_path}')
            return False
        
        # 记录原始文件大小
        original_size = os.path.getsize(png_path)
        
        # 构建 pngquant 命令
        cmd = [
            'pngquant',
            '--quality=65-80',
            '--force',
            '--ext', '.png',  # 保持原扩展名
            png_path
        ]
        
        # 执行压缩命令
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            # 获取压缩后文件大小
            compressed_size = os.path.getsize(png_path)
            # 计算压缩率
            compression_ratio = (1 - compressed_size / original_size) * 100
            
            print(f'PNG压缩完成: {png_path}')
            print(f'原始大小: {original_size / 1024:.2f} KB')
            print(f'压缩后: {compressed_size / 1024:.2f} KB')
            print(f'压缩率: {compression_ratio:.1f}%')
            if compression_ratio < 0.1:
                print('压缩率过低,不再压缩')
                return False
            return True
        else:
            print(f'PNG压缩失败: {png_path}')
            print(f'错误信息: {result.stderr}')
            return False
            
    except FileNotFoundError:
        print(f'错误: 未找到 pngquant 命令，请先安装 pngquant')
        print('Ubuntu/Debian: sudo apt install pngquant')
        print('macOS: brew install pngquant')
        return False
    except Exception as e:
        print(f'PNG压缩失败: {png_path}, 错误: {e}')
        return False

def compress_png_with_backup(png_path, backup_suffix='.backup'):
    """
    使用 pngquant 压缩 PNG 图片，并创建备份文件
    
    Args:
        png_path (str): PNG 图片的路径
        backup_suffix (str): 备份文件后缀
    """
    try:
        if not os.path.exists(png_path):
            print(f'文件不存在: {png_path}')
            return False
        
        # 创建备份文件
        backup_path = f"{png_path}{backup_suffix}"
        import shutil
        shutil.copy2(png_path, backup_path)
        
        print(f'已创建备份: {backup_path}')
        
        # 进行压缩
        success = compress_png_pngquant(png_path)
        
        if success:
            # 压缩成功后可以选择删除备份文件，或者保留
            # os.remove(backup_path)  # 取消注释此行以自动删除备份
            pass
        else:
            # 如果压缩失败，恢复备份
            shutil.copy2(backup_path, png_path)
            print(f'已恢复原文件: {png_path}')
        
        os.remove(backup_path)
        return success
        
    except Exception as e:
        print(f'压缩过程出错: {e}')
        return False
            
def update_markdown_image_refs(md_file, content, png_paths):
    """将Markdown中的PNG引用替换为JPG"""
    new_content = content
    for png_path in png_paths:
        jpg_path = png_path[:-4] + '.jpg'
        new_content = new_content.replace(png_path, jpg_path)
    with open(md_file, 'w', encoding='utf-8') as f:
        f.write(new_content)

# def main():
#     md_files = find_markdown_files(ARTICLES_DIR)
#     for md_file in md_files:
#         png_paths, content = find_png_images(md_file)
#         for png_path in png_paths:
#             # 处理相对路径
#             abs_png_path = os.path.join(os.path.dirname(md_file), png_path) if not os.path.isabs(png_path) else png_path
#             if os.path.exists(abs_png_path):
#                 convert_png_to_jpg(abs_png_path)
#         update_markdown_image_refs(md_file, content, png_paths)
#     print('处理完成！所有PNG图片已转换为JPG，并更新Markdown引用。')

def main():
    parser = argparse.ArgumentParser(description='PNG/JPG图片压缩工具')
    parser.add_argument('--mode', choices=['png', 'jpg'], default='png', help='压缩模式: png=压缩PNG, jpg=通过JPG链接找到PNG并压缩')
    parser.add_argument('--dir', choices=['articles', 'blog','home','projects'], default='articles', help='压缩模式: png=压缩PNG, jpg=通过JPG链接找到PNG并压缩')
    args = parser.parse_args()
    ARTICLES_DIR = args.dir
    print(ARTICLES_DIR)
    md_files = find_markdown_files(ARTICLES_DIR)
    if args.mode == 'png':
        for md_file in md_files:
            png_paths, content = find_png_images(md_file)
            for png_path in png_paths:
                abs_png_path = os.path.join(os.path.dirname(md_file), png_path) if not os.path.isabs(png_path) else png_path
                if os.path.exists(abs_png_path):
                    # compress_png(abs_png_path)
                    compress_png_with_backup(abs_png_path)
                    # convert_png_to_jpg(abs_png_path)
            # update_markdown_image_refs(md_file, content, png_paths)
    elif args.mode == 'jpg':
        for md_file in md_files:
            jpg_paths,content = find_jpg_images(md_file)
            for jpg_path in jpg_paths:
                png_path = jpg_path[:-4] + '.png'
                abs_png_path = os.path.join(os.path.dirname(md_file), png_path) if not os.path.isabs(png_path) else png_path
                if os.path.exists(abs_png_path):
                    # compress_png(abs_png_path)
                    convert_png_to_jpg(abs_png_path)
            # update_markdown_image_refs(md_file, content, png_paths)
    print('处理完成！所有PNG图片已转换为JPG，并更新Markdown引用。')
    
if __name__ == '__main__':
    main()
