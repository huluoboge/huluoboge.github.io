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
    
    def __init__(self, engine: str = "libre", google_api_key: str = None,
                 aliyun_access_key_id: str = None, aliyun_access_key_secret: str = None):
        """
        初始化PDF翻译器
        
        Args:
            engine: 翻译引擎 ("libre", "google" 或 "aliyun")
            google_api_key: Google Cloud Translation API密钥
            aliyun_access_key_id: 阿里云AccessKey ID
            aliyun_access_key_secret: 阿里云AccessKey Secret
        """
        self.pdf_parser = PDFParser()
        # 延迟初始化翻译管理器，只在需要翻译时创建
        self._engine = engine
        self._google_api_key = google_api_key
        self._aliyun_access_key_id = aliyun_access_key_id
        self._aliyun_access_key_secret = aliyun_access_key_secret
        self._translation_manager = None
        self.max_chunk_size = TRANSLATION_CONFIG["max_chunk_size"]
    
    @property
    def translation_manager(self):
        """延迟初始化翻译管理器"""
        if self._translation_manager is None:
            self._translation_manager = TranslationManager(
                self._engine, 
                self._google_api_key, 
                self._aliyun_access_key_id, 
                self._aliyun_access_key_secret
            )
        return self._translation_manager
    
    def extract_pdf_text(self, pdf_path: str, output_path: str = None) -> str:
        """
        第一步：提取PDF文本并保存为中间文件
        
        Args:
            pdf_path: PDF文件路径
            output_path: 输出文件路径
            
        Returns:
            中间文件路径
        """
        print(f"📄 第一步：提取PDF文本: {pdf_path}")
        
        # 提取PDF文本
        print("📄 正在解析PDF...")
        original_text = self.pdf_parser.extract_text_from_pdf(pdf_path)
        
        if not original_text:
            raise ValueError("PDF文件为空或无法提取文本")
        
        print(f"📝 提取到 {len(original_text)} 个字符的文本")
        
        # 生成中间文件路径
        if output_path is None:
            pdf_name = Path(pdf_path).stem
            output_path = f"{pdf_name}_extracted.txt"
        
        # 保存提取的文本
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("# PDF文本提取结果\n\n")
            f.write("> 本文档为PDF文件的原始文本提取结果，保持了原文的结构格式\n\n")
            f.write(original_text)
        
        print(f"✅ 文本提取完成！结果已保存到: {output_path}")
        return output_path
    
    def translate_extracted_text(self, extracted_file: str, output_path: str = None,
                               source_lang: str = DEFAULT_SOURCE_LANG,
                               target_lang: str = DEFAULT_TARGET_LANG) -> str:
        """
        第二步：翻译已提取的文本文件
        
        Args:
            extracted_file: 已提取的文本文件路径
            output_path: 输出文件路径
            source_lang: 源语言代码
            target_lang: 目标语言代码
            
        Returns:
            翻译结果保存路径
        """
        print(f"🌐 第二步：翻译提取的文本: {extracted_file}")
        
        # 读取提取的文本
        with open(extracted_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 跳过文件头信息，只提取实际文本内容
        lines = content.split('\n')
        actual_text_lines = []
        in_content = False
        
        for line in lines:
            if line.startswith('# PDF文本提取结果') or line.startswith('> 本文档为PDF文件的原始文本提取结果'):
                continue
            if line.strip() == '':
                continue
            actual_text_lines.append(line)
        
        original_text = '\n'.join(actual_text_lines)
        
        if not original_text.strip():
            raise ValueError("提取的文本文件为空")
        
        print(f"📝 读取到 {len(original_text)} 个字符的文本")
        
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
        
        # 合并翻译结果，智能处理换行
        translated_text = self._merge_translated_chunks(translated_chunks)
        
        # 生成输出文件路径
        if output_path is None:
            file_name = Path(extracted_file).stem.replace('_extracted', '')
            output_path = f"{file_name}_translated.txt"
        
        # 保存翻译结果
        self._save_translation_result(original_text, translated_text, output_path)
        
        print(f"✅ 翻译完成！结果已保存到: {output_path}")
        return output_path
    
    def translate_pdf(self, pdf_path: str, output_path: str = None, 
                      source_lang: str = DEFAULT_SOURCE_LANG, 
                      target_lang: str = DEFAULT_TARGET_LANG) -> str:
        """
        翻译单个PDF文件（一步完成）
        
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
        
        # 合并翻译结果，智能处理换行
        translated_text = self._merge_translated_chunks(translated_chunks)
        
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
        保存翻译结果（仅保存译文，Markdown格式）
        
        Args:
            original_text: 原文
            translated_text: 译文
            output_path: 输出文件路径
        """
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("# PDF翻译结果\n\n")
            f.write("> 本文档为PDF文件的翻译结果，保持了原文的结构格式\n\n")
            f.write(translated_text)
    
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
    
    def _merge_translated_chunks(self, chunks: list) -> str:
        """
        智能合并翻译块，优化换行排版
        
        Args:
            chunks: 翻译块列表
            
        Returns:
            合并后的文本
        """
        if not chunks:
            return ""
        
        merged_text = ""
        
        for i, chunk in enumerate(chunks):
            # 清理当前块的换行
            cleaned_chunk = chunk.strip()
            
            # 如果是第一个块，直接添加
            if i == 0:
                merged_text = cleaned_chunk
                continue
            
            # 检查前一个块的结尾和当前块的开头
            prev_chunk_ends_with_punctuation = merged_text and merged_text[-1] in '。！？.!?'
            current_chunk_starts_with_space = cleaned_chunk and cleaned_chunk[0].isspace()
            
            # 智能添加分隔符
            if prev_chunk_ends_with_punctuation:
                # 如果前一个块以标点结尾，添加两个换行（新段落）
                merged_text += "\n\n" + cleaned_chunk
            elif current_chunk_starts_with_space:
                # 如果当前块以空格开头，直接连接
                merged_text += cleaned_chunk
            else:
                # 其他情况添加一个换行
                merged_text += "\n" + cleaned_chunk
        
        return merged_text


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="PDF翻译工具 - 将PDF文件翻译为指定语言",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  # 一步翻译单个PDF文件
  python main.py --input paper.pdf --output translated.txt
  
  # 两步翻译：第一步提取文本
  python main.py --step extract --input paper.pdf --output extracted.txt
  
  # 两步翻译：第二步翻译提取的文本
  python main.py --step translate --input extracted.txt --output translated.txt
  
  # 批量翻译目录中的所有PDF文件
  python main.py --input papers/ --output translations/
  
  # 使用阿里云机器翻译（需要AccessKey）
  python main.py --input paper.pdf --engine aliyun --aliyun-access-key-id YOUR_ID --aliyun-access-key-secret YOUR_SECRET
  
  # 指定翻译语言
  python main.py --input paper.pdf --source en --target zh
        """
    )
    
    parser.add_argument("--step", choices=["extract", "translate", "auto"], default="auto",
                       help="翻译步骤: extract(仅提取文本), translate(仅翻译文本), auto(自动完成)")
    parser.add_argument("--input", "-i", required=True, 
                       help="输入PDF文件或目录路径")
    parser.add_argument("--output", "-o", 
                       help="输出文件或目录路径")
    parser.add_argument("--engine", "-e", choices=["libre", "google", "aliyun"], 
                       default="libre", help="翻译引擎 (默认: libre)")
    parser.add_argument("--api-key", 
                       help="Google Cloud Translation API密钥")
    parser.add_argument("--aliyun-access-key-id", 
                       help="阿里云AccessKey ID")
    parser.add_argument("--aliyun-access-key-secret", 
                       help="阿里云AccessKey Secret")
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
        # 只有在需要翻译时才检查阿里云密钥
        if args.step != "extract":
            if not args.aliyun_access_key_id or not args.aliyun_access_key_secret:
                args.aliyun_access_key_id = os.getenv('ALIYUN_ACCESS_KEY_ID')
                args.aliyun_access_key_secret = os.getenv('ALIYUN_ACCESS_KEY_SECRET')
            if not args.aliyun_access_key_id or not args.aliyun_access_key_secret:
                print("❌ 请设置环境变量: ALIYUN_ACCESS_KEY_ID 和 ALIYUN_ACCESS_KEY_SECRET")
                print("使用方法:")
                print("  export ALIYUN_ACCESS_KEY_ID=your_access_key_id")
                print("  export ALIYUN_ACCESS_KEY_SECRET=your_access_key_secret")
                print("  python test_aliyun.py")
                return
        
        translator = PDFTranslator(
            args.engine, 
            args.api_key,
            args.aliyun_access_key_id,
            args.aliyun_access_key_secret
        )
        
        if args.step == "extract":
            # 仅提取文本
            if not os.path.isfile(args.input):
                print(f"❌ 输入路径不是文件: {args.input}")
                return 1
            
            if not args.input.lower().endswith('.pdf'):
                print(f"❌ 输入文件不是PDF格式: {args.input}")
                return 1
            
            translator.extract_pdf_text(args.input, args.output)
            
        elif args.step == "translate":
            # 仅翻译文本
            if not os.path.isfile(args.input):
                print(f"❌ 输入路径不是文件: {args.input}")
                return 1
            
            translator.translate_extracted_text(
                args.input,
                args.output,
                args.source,
                args.target
            )
            
        else:  # auto mode
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
        print(f"❌ 操作失败: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
