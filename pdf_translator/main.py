#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
PDF翻译工具主程序
"""

import os
import sys
import argparse
import time
from pathlib import Path
from tqdm import tqdm

# 添加当前目录到Python路径，确保可以导入模块
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from pdf_parser import PDFParser
from translator import TranslationManager, TranslationError
from config import (
    TRANSLATION_CONFIG,
    DEFAULT_SOURCE_LANG,
    DEFAULT_TARGET_LANG,
    SUPPORTED_LANGUAGES
)


class PDFTranslator:
    """PDF翻译器主类"""
    
    def __init__(self, engine: str = "libre", google_api_key: str = None):
        """
        初始化PDF翻译器
        
        Args:
            engine: 翻译引擎 ("libre" 或 "google")
            google_api_key: Google Cloud Translation API密钥
        """
        self.pdf_parser = PDFParser()
        self.translation_manager = TranslationManager(engine, google_api_key)
        self.max_chunk_size = TRANSLATION_CONFIG["max_chunk_size"]
    
    def translate_pdf(self, pdf_path: str, output_path: str = None, 
                      source_lang: str = DEFAULT_SOURCE_LANG, 
                      target_lang: str = DEFAULT_TARGET_LANG) -> str:
        """
        翻译单个PDF文件
        
        Args:
            pdf_path: PDF文件路径
            output_path: 输出文件路径
            source_lang: 源语言代码
            target_lang: 目标语言代码
            
        Returns:
            翻译结果保存路径
        """
        print(f"🚀 开始翻译PDF: {pdf_path}")
        
        # 提取PDF文本
        print("📄 正在解析PDF...")
        original_text = self.pdf_parser.extract_text_from_pdf(pdf_path)
        
        if not original_text:
            raise ValueError("PDF文件为空或无法提取文本")
        
        print(f"📝 提取到 {len(original_text)} 个字符的文本")
        
        # 分割文本为适合翻译的块
        text_chunks = self.pdf_parser.split_text_into_chunks(original_text, self.max_chunk_size)
        
        # 翻译每个文本块
        print("🌐 开始翻译...")
        translated_chunks = []
        
        with tqdm(total=len(text_chunks), desc="翻译进度", unit="块") as pbar:
            for i, chunk in enumerate(text_chunks):
                try:
                    # 添加延迟避免请求过于频繁
                    if i > 0:
                        time.sleep(1)  # 1秒延迟
                    
                    translated_chunk = self.translation_manager.translate_text(
                        chunk, source_lang, target_lang
                    )
                    translated_chunks.append(translated_chunk)
                    pbar.update(1)
                    
                except TranslationError as e:
                    print(f"\n❌ 翻译块 {i+1} 失败: {e}")
                    # 保存已翻译的部分
                    translated_chunks.append(f"[翻译失败] {chunk}")
                    pbar.update(1)
                    continue
        
        # 合并翻译结果
        translated_text = "\n\n".join(translated_chunks)
        
        # 生成输出文件路径
        if output_path is None:
            pdf_name = Path(pdf_path).stem
            output_path = f"{pdf_name}_translated.txt"
        
        # 保存结果（原文+译文对照）
        self._save_translation_result(original_text, translated_text, output_path)
        
        print(f"✅ 翻译完成！结果已保存到: {output_path}")
        return output_path
    
    def _save_translation_result(self, original_text: str, translated_text: str, output_path: str):
        """
        保存翻译结果（原文+译文对照）
        
        Args:
            original_text: 原文
            translated_text: 译文
            output_path: 输出文件路径
        """
        # 分割原文和译文为段落
        original_paragraphs = [p.strip() for p in original_text.split('\n\n') if p.strip()]
        translated_paragraphs = [p.strip() for p in translated_text.split('\n\n') if p.strip()]
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("=" * 60 + "\n")
            f.write("PDF翻译结果 - 原文与译文对照\n")
            f.write("=" * 60 + "\n\n")
            
            # 确保段落数量一致
            min_paragraphs = min(len(original_paragraphs), len(translated_paragraphs))
            
            for i in range(min_paragraphs):
                f.write(f"【原文 {i+1}】\n")
                f.write(original_paragraphs[i])
                f.write("\n\n")
                f.write(f"【译文 {i+1}】\n")
                f.write(translated_paragraphs[i])
                f.write("\n\n")
                f.write("-" * 40 + "\n\n")
            
            # 如果有剩余的段落
            if len(original_paragraphs) > min_paragraphs:
                f.write("【剩余原文】\n")
                for i in range(min_paragraphs, len(original_paragraphs)):
                    f.write(original_paragraphs[i])
                    f.write("\n\n")
            
            if len(translated_paragraphs) > min_paragraphs:
                f.write("【剩余译文】\n")
                for i in range(min_paragraphs, len(translated_paragraphs)):
                    f.write(translated_paragraphs[i])
                    f.write("\n\n")
    
    def batch_translate(self, input_dir: str, output_dir: str = None,
                       source_lang: str = DEFAULT_SOURCE_LANG,
                       target_lang: str = DEFAULT_TARGET_LANG):
        """
        批量翻译目录中的所有PDF文件
        
        Args:
            input_dir: 输入目录
            output_dir: 输出目录
            source_lang: 源语言代码
            target_lang: 目标语言代码
        """
        input_path = Path(input_dir)
        
        if not input_path.exists():
            raise FileNotFoundError(f"输入目录不存在: {input_dir}")
        
        # 查找所有PDF文件
        pdf_files = list(input_path.glob("*.pdf"))
        
        if not pdf_files:
            print(f"❌ 在目录 {input_dir} 中未找到PDF文件")
            return
        
        print(f"📁 找到 {len(pdf_files)} 个PDF文件")
        
        # 创建输出目录
        if output_dir is None:
            output_dir = input_path / "translations"
        else:
            output_dir = Path(output_dir)
        
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # 批量翻译
        success_count = 0
        for pdf_file in pdf_files:
            try:
                output_file = output_dir / f"{pdf_file.stem}_translated.txt"
                self.translate_pdf(
                    str(pdf_file),
                    str(output_file),
                    source_lang,
                    target_lang
                )
                success_count += 1
                
                # 文件间添加较长延迟
                time.sleep(3)
                
            except Exception as e:
                print(f"❌ 翻译文件 {pdf_file.name} 失败: {e}")
                continue
        
        print(f"🎉 批量翻译完成！成功翻译 {success_count}/{len(pdf_files)} 个文件")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="PDF翻译工具 - 将PDF文件翻译为指定语言",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  # 翻译单个PDF文件
  python main.py --input paper.pdf --output translated.txt
  
  # 批量翻译目录中的所有PDF文件
  python main.py --input papers/ --output translations/
  
  # 使用Google翻译引擎（需要API密钥）
  python main.py --input paper.pdf --engine google --api-key YOUR_KEY
  
  # 指定翻译语言
  python main.py --input paper.pdf --source en --target zh
        """
    )
    
    parser.add_argument("--input", "-i", required=True, 
                       help="输入PDF文件或目录路径")
    parser.add_argument("--output", "-o", 
                       help="输出文件或目录路径")
    parser.add_argument("--engine", "-e", choices=["libre", "google"], 
                       default="libre", help="翻译引擎 (默认: libre)")
    parser.add_argument("--api-key", 
                       help="Google Cloud Translation API密钥")
    parser.add_argument("--source", "-s", default=DEFAULT_SOURCE_LANG,
                       help=f"源语言代码 (默认: {DEFAULT_SOURCE_LANG})")
    parser.add_argument("--target", "-t", default=DEFAULT_TARGET_LANG,
                       help=f"目标语言代码 (默认: {DEFAULT_TARGET_LANG})")
    
    args = parser.parse_args()
    
    # 验证语言代码
    if args.source not in SUPPORTED_LANGUAGES:
        print(f"❌ 不支持的源语言代码: {args.source}")
        print(f"支持的语言: {', '.join(SUPPORTED_LANGUAGES.keys())}")
        return 1
    
    if args.target not in SUPPORTED_LANGUAGES:
        print(f"❌ 不支持的目标语言代码: {args.target}")
        print(f"支持的语言: {', '.join(SUPPORTED_LANGUAGES.keys())}")
        return 1
    
    try:
        translator = PDFTranslator(args.engine, args.api_key)
        
        if os.path.isfile(args.input):
            # 单个文件翻译
            translator.translate_pdf(
                args.input, 
                args.output,
                args.source,
                args.target
            )
        elif os.path.isdir(args.input):
            # 批量翻译
            translator.batch_translate(
                args.input,
                args.output,
                args.source,
                args.target
            )
        else:
            print(f"❌ 输入路径不存在: {args.input}")
            return 1
            
    except Exception as e:
        print(f"❌ 翻译失败: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
