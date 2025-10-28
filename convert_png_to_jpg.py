import os
import re
from PIL import Image
import argparse

# 设置要处理的目录和图片质量
ARTICLES_DIR = 'articles'
QUALITY = 50



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
                    convert_png_to_jpg(abs_png_path)
            update_markdown_image_refs(md_file, content, png_paths)
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
