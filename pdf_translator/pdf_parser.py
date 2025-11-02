#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
PDF解析模块
用于从PDF文件中提取文本内容
"""

import pdfplumber
import os
import re
from typing import List, Tuple, Optional


class PDFParser:
    def __init__(self):
        self.supported_formats = ['.pdf']
    
    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """
        从PDF文件中提取所有文本
        
        Args:
            pdf_path: PDF文件路径
            
        Returns:
            提取的文本内容
        """
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"PDF文件不存在: {pdf_path}")
        
        if not pdf_path.lower().endswith('.pdf'):
            raise ValueError(f"不支持的文件格式: {pdf_path}")
        
        full_text = ""
        
        try:
            with pdfplumber.open(pdf_path) as pdf:
                print(f"📄 正在解析PDF: {pdf_path} (共{len(pdf.pages)}页)")
                
                for page_num, page in enumerate(pdf.pages, 1):
                    page_text = page.extract_text()
                    if page_text:
                        # 清理文本，移除多余的空格和换行
                        cleaned_text = self._clean_text(page_text)
                        full_text += f"\n--- 第{page_num}页 ---\n{cleaned_text}\n"
                    
                    # 显示进度
                    if page_num % 10 == 0 or page_num == len(pdf.pages):
                        print(f"  已解析 {page_num}/{len(pdf.pages)} 页")
        
        except Exception as e:
            raise Exception(f"解析PDF文件失败: {str(e)}")
        
        return full_text.strip()
    
    def _clean_text(self, text: str) -> str:
        """
        清理提取的文本
        
        Args:
            text: 原始文本
            
        Returns:
            清理后的文本
        """
        # 移除多余的换行符和空格
        text = re.sub(r'\n+', '\n', text)
        text = re.sub(r' +', ' ', text)
        
        # 移除页眉页脚等常见噪音
        text = self._remove_header_footer(text)
        
        return text.strip()
    
    def _remove_header_footer(self, text: str) -> str:
        """
        移除可能的页眉页脚内容
        
        Args:
            text: 原始文本
            
        Returns:
            清理后的文本
        """
        lines = text.split('\n')
        cleaned_lines = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # 跳过可能的页码、日期等页眉页脚内容
            if (re.match(r'^\d+$', line) or  # 纯数字（页码）
                re.match(r'^[A-Z\s]+$', line) or  # 全大写（可能是标题）
                len(line) < 3):  # 太短的文本
                continue
            
            cleaned_lines.append(line)
        
        return '\n'.join(cleaned_lines)
    
    def split_text_into_chunks(self, text: str, max_chunk_size: int = 2000) -> List[str]:
        """
        将长文本分割成适合翻译的小块
        
        Args:
            text: 原始文本
            max_chunk_size: 每个块的最大字符数
            
        Returns:
            文本块列表
        """
        if len(text) <= max_chunk_size:
            return [text]
        
        chunks = []
        paragraphs = text.split('\n\n')
        current_chunk = ""
        
        for paragraph in paragraphs:
            paragraph = paragraph.strip()
            if not paragraph:
                continue
            
            # 如果当前块加上新段落不超过限制，则添加
            if len(current_chunk) + len(paragraph) + 2 <= max_chunk_size:
                if current_chunk:
                    current_chunk += '\n\n' + paragraph
                else:
                    current_chunk = paragraph
            else:
                # 当前块已满，保存并开始新块
                if current_chunk:
                    chunks.append(current_chunk)
                
                # 如果单个段落就超过限制，需要进一步分割
                if len(paragraph) > max_chunk_size:
                    # 按句子分割
                    sentences = re.split(r'[.!?]+', paragraph)
                    temp_chunk = ""
                    
                    for sentence in sentences:
                        sentence = sentence.strip()
                        if not sentence:
                            continue
                        
                        if len(temp_chunk) + len(sentence) + 2 <= max_chunk_size:
                            if temp_chunk:
                                temp_chunk += '. ' + sentence
                            else:
                                temp_chunk = sentence
                        else:
                            if temp_chunk:
                                chunks.append(temp_chunk)
                            temp_chunk = sentence
                    
                    if temp_chunk:
                        current_chunk = temp_chunk
                else:
                    current_chunk = paragraph
        
        # 添加最后一个块
        if current_chunk:
            chunks.append(current_chunk)
        
        print(f"📝 文本已分割为 {len(chunks)} 个翻译块")
        return chunks


def main():
    """测试函数"""
    parser = PDFParser()
    
    # 测试文本分割
    test_text = "这是一个测试段落。" * 100
    chunks = parser.split_text_into_chunks(test_text, 100)
    print(f"测试分割结果: {len(chunks)} 个块")
    for i, chunk in enumerate(chunks[:3]):
        print(f"块 {i+1}: {chunk[:50]}...")


if __name__ == "__main__":
    main()
