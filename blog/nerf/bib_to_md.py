#!/usr/bin/env python3
"""
BibTeX to Markdown Converter
将BibTeX格式的文献列表转换为Markdown格式，便于在博客或文档中使用
"""

import re
import os
from typing import Dict, List, Optional


class BibTeXToMarkdownConverter:
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

    def generate_markdown(self, entries: List[Dict], output_file: str):
        """生成Markdown格式"""
        with open(output_file, 'w', encoding='utf-8') as f:
            # 写入Markdown标题
            f.write("# 文献列表\n\n")
            f.write("本文档包含以下文献条目：\n\n")
            
            # 写入文献条目
            for i, entry in enumerate(entries, 1):
                f.write(f"## {i}. {entry.get('title', '')}\n\n")
                
                # 作者信息
                authors = entry.get('authors', '')
                if authors:
                    f.write(f"**作者**: {authors}\n\n")
                
                # 期刊和年份信息
                journal = entry.get('journal', '')
                year = entry.get('year', '')
                volume = entry.get('volume', '')
                pages = entry.get('pages', '')
                
                if journal or year:
                    publication_info = []
                    if journal:
                        publication_info.append(journal)
                    if year:
                        publication_info.append(year)
                    if volume:
                        publication_info.append(f"卷 {volume}")
                    if pages:
                        publication_info.append(f"页 {pages}")
                    
                    f.write(f"**出处**: {', '.join(publication_info)}\n\n")
                
                # 链接信息
                url = entry.get('url', '')
                doi = entry.get('doi', '')
                arxivid = entry.get('arxivid', '')
                pmid = entry.get('pmid', '')
                
                links = []
                if url:
                    links.append(f"[原文链接]({url})")
                if doi:
                    links.append(f"[DOI](https://doi.org/{doi})")
                if arxivid:
                    links.append(f"[arXiv](https://arxiv.org/abs/{arxivid})")
                if pmid:
                    links.append(f"[PMID](https://pubmed.ncbi.nlm.nih.gov/{pmid}/)")
                
                if links:
                    f.write(f"**链接**: {' | '.join(links)}\n\n")
                
                # 摘要
                abstract = entry.get('abstract', '')
                if abstract:
                    f.write(f"**摘要**: {abstract}\n\n")
                
                f.write("---\n\n")

    def convert(self, input_file: str, output_file: str):
        """主转换函数"""
        print(f"正在解析文件: {input_file}")
        entries = self.parse_bibtex_file(input_file)
        print(f"成功解析 {len(entries)} 个文献条目")

        print("正在生成Markdown格式...")
        self.generate_markdown(entries, output_file)

        print(f"转换完成！Markdown文件已保存至: {output_file}")


def main():
    """主函数"""
    converter = BibTeXToMarkdownConverter()

    # 输入和输出文件路径
    input_file = "/home/recon/Git/02jones/huluoboge.github.io/blog/nerf/nerf.bib"
    output_file = "nerf_literature.md"

    # 检查输入文件是否存在
    if not os.path.exists(input_file):
        print(f"错误: 输入文件 {input_file} 不存在")
        return

    # 执行转换
    converter.convert(input_file, output_file)


if __name__ == "__main__":
    main()
