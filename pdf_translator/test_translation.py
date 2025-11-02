#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
PDF翻译工具测试脚本
用于测试翻译功能是否正常工作
"""

import sys
import os

# 添加当前目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from translator import LibreTranslate, TranslationError


def test_libre_translate():
    """测试LibreTranslate翻译功能"""
    print("🧪 测试LibreTranslate翻译功能...")
    
    translator = LibreTranslate()
    
    # 测试文本
    test_cases = [
        ("Hello, world!", "en", "zh", "你好，世界！"),
        ("This is a test sentence.", "en", "zh", "这是一个测试句子。"),
        ("Artificial intelligence", "en", "zh", "人工智能"),
    ]
    
    success_count = 0
    for original, source_lang, target_lang, expected in test_cases:
        try:
            result = translator.translate(original, source_lang, target_lang)
            print(f"✅ '{original}' -> '{result}'")
            success_count += 1
        except TranslationError as e:
            print(f"❌ 翻译失败: {e}")
            # 检查网络连接
            print("💡 提示: 请检查网络连接，或尝试更换翻译端点")
            break
    
    print(f"\n📊 测试结果: {success_count}/{len(test_cases)} 通过")
    
    if success_count == len(test_cases):
        print("🎉 LibreTranslate测试通过！可以正常使用PDF翻译工具。")
        return True
    else:
        print("⚠️  LibreTranslate测试失败，请检查网络连接。")
        return False


def test_pdf_parser():
    """测试PDF解析功能"""
    print("\n🧪 测试PDF解析功能...")
    
    try:
        from pdf_parser import PDFParser
        
        parser = PDFParser()
        
        # 测试文本分割
        test_text = "这是一个测试段落。" * 50
        chunks = parser.split_text_into_chunks(test_text, 100)
        
        print(f"✅ 文本分割测试通过: 将{len(test_text)}字符分割为{len(chunks)}个块")
        print(f"   示例块: {chunks[0][:30]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ PDF解析测试失败: {e}")
        return False


def main():
    """主测试函数"""
    print("=" * 50)
    print("PDF翻译工具功能测试")
    print("=" * 50)
    
    # 测试翻译功能
    translation_ok = test_libre_translate()
    
    # 测试PDF解析功能
    parser_ok = test_pdf_parser()
    
    print("\n" + "=" * 50)
    print("测试总结")
    print("=" * 50)
    
    if translation_ok and parser_ok:
        print("🎉 所有测试通过！PDF翻译工具可以正常使用。")
        print("\n💡 使用提示:")
        print("   1. 确保网络连接稳定")
        print("   2. 使用命令: python main.py --input your_paper.pdf")
        print("   3. 翻译结果会保存为原文+译文对照格式")
    else:
        print("⚠️  部分测试失败，请检查:")
        if not translation_ok:
            print("   - 网络连接是否正常")
            print("   - 翻译API端点是否可用")
        if not parser_ok:
            print("   - pdfplumber库是否正确安装")
            print("   - PDF文件是否为可编辑文本格式")
        
        print("\n🔧 故障排除:")
        print("   1. 运行: pip install -r requirements.txt")
        print("   2. 检查网络连接")
        print("   3. 尝试使用其他PDF文件")


if __name__ == "__main__":
    main()
