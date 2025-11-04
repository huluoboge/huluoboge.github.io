#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
阿里云机器翻译测试脚本
"""

import sys
import os

# 添加当前目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from translator import AliyunTranslator, TranslationError

def test_aliyun_translation():
    """测试阿里云机器翻译功能"""
    
    # 从环境变量获取AccessKey
    access_key_id = os.getenv('ALIYUN_ACCESS_KEY_ID')
    access_key_secret = os.getenv('ALIYUN_ACCESS_KEY_SECRET')
    
    if not access_key_id or not access_key_secret:
        print("❌ 请设置环境变量: ALIYUN_ACCESS_KEY_ID 和 ALIYUN_ACCESS_KEY_SECRET")
        print("使用方法:")
        print("  export ALIYUN_ACCESS_KEY_ID=your_access_key_id")
        print("  export ALIYUN_ACCESS_KEY_SECRET=your_access_key_secret")
        print("  python test_aliyun.py")
        return
    
    print("🚀 开始测试阿里云机器翻译...")
    
    try:
        # 创建翻译器实例
        translator = AliyunTranslator(access_key_id, access_key_secret)
        
        # 测试文本
        test_texts = [
            "Hello, this is a test for Alibaba Cloud Machine Translation.",
            "The quick brown fox jumps over the lazy dog.",
            "Machine learning is a subset of artificial intelligence.",
            "Natural language processing enables computers to understand human language."
        ]
        
        for i, text in enumerate(test_texts, 1):
            print(f"\n📝 测试 {i}:")
            print(f"原文: {text}")
            
            try:
                # 翻译文本
                result = translator.translate(text, "en", "zh")
                print(f"译文: {result}")
                
            except TranslationError as e:
                print(f"❌ 翻译失败: {e}")
                continue
        
        print("\n✅ 阿里云机器翻译测试完成！")
        
    except Exception as e:
        print(f"❌ 测试过程中出现错误: {e}")

if __name__ == "__main__":
    test_aliyun_translation()
