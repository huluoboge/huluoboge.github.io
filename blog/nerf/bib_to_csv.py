#!/usr/bin/env python3
"""
BibTeX to CSV Converter
将BibTeX格式的文献列表转换为CSV格式，便于后续加工
"""

import re
import os
import csv
from typing import Dict, List, Optional


class BibTeXToCSVConverter:
    def __init__(self):
        self.entries = []

    def parse_bibtex_file(self, file_path: str) -> List[Dict]:
        """解析BibTeX文件"""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        entries = []
        # 分割不同的条目
        article_entries = re.findall(r'@article{([\s\S]*?)\n}', content, re.DOTALL)
        
        for entry in article_entries:
            # 提取字段
            def extract_field(field):
                match = re.search(rf'{field}\s*=\s*{{(.*?)}}', entry, re.DOTALL)
                return match.group(1).replace('\n', ' ').strip() if match else ""

            entry_data = {
                'title': extract_field("title"),
                'authors': extract_field("author"),
                'year': extract_field("year"),
                'journal': extract_field("journal"),
                'url': extract_field("url"),
                'doi': extract_field("doi"),
                'abstract': extract_field("abstract"),
                'volume': extract_field("volume"),
                'pages': extract_field("pages"),
                'arxivid': extract_field("arxivid"),
                'pmid': extract_field("pmid")
            }
            
            entries.append(entry_data)
        
        return entries

    def generate_csv(self, entries: List[Dict], output_file: str):
        """生成CSV格式"""
        # CSV表头
        fieldnames = [
            '序号', '标题', '作者', '年份', '期刊/会议', 
            '卷号', '页码', 'DOI', 'arXiv ID', 'PMID', 
            '原文链接', '摘要'
        ]
        
        with open(output_file, 'w', encoding='utf-8', newline='') as f:
            writer = csv.writer(f)
            # 写入表头
            writer.writerow(fieldnames)
            
            # 写入数据
            for i, entry in enumerate(entries, 1):
                row = [
                    i,  # 序号
                    entry.get('title', ''),
                    entry.get('authors', ''),
                    entry.get('year', ''),
                    entry.get('journal', ''),
                    entry.get('volume', ''),
                    entry.get('pages', ''),
                    entry.get('doi', ''),
                    entry.get('arxivid', ''),
                    entry.get('pmid', ''),
                    entry.get('url', ''),
                    entry.get('abstract', '')
                ]
                writer.writerow(row)

    def convert(self, input_file: str, output_file: str):
        """主转换函数"""
        print(f"正在解析文件: {input_file}")
        entries = self.parse_bibtex_file(input_file)
        print(f"成功解析 {len(entries)} 个文献条目")

        print("正在生成CSV格式...")
        self.generate_csv(entries, output_file)

        print(f"转换完成！CSV文件已保存至: {output_file}")


def main():
    """主函数"""
    converter = BibTeXToCSVConverter()

    # 输入和输出文件路径
    input_file = "/home/recon/Git/02jones/huluoboge.github.io/blog/nerf/nerf.bib"
    output_file = "nerf_literature.csv"

    # 检查输入文件是否存在
    if not os.path.exists(input_file):
        print(f"错误: 输入文件 {input_file} 不存在")
        return

    # 执行转换
    converter.convert(input_file, output_file)


if __name__ == "__main__":
    main()
