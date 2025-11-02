#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
PDF翻译工具配置文件
"""

# LibreTranslate 实例端点（优先使用本地实例）
LIBRETRANSLATE_ENDPOINTS = [
    "http://localhost:5000/translate",  # 本地自建实例
    "https://libretranslate.com/translate",  # 公共实例1
    "https://translate.argosopentech.com/translate",  # 公共实例2
    "https://libretranslate.de/translate"  # 公共实例3
]

# Google Cloud Translation API 配置
GOOGLE_TRANSLATE_ENDPOINT = "https://translation.googleapis.com/language/translate/v2"

# 翻译参数
TRANSLATION_CONFIG = {
    "max_chunk_size": 2000,  # 每次翻译的最大字符数
    "timeout": 30,           # 请求超时时间（秒）
    "retry_attempts": 3,     # 重试次数
    "delay_between_retries": 2,  # 重试间隔（秒）
}

# 支持的语言代码
SUPPORTED_LANGUAGES = {
    "en": "English",
    "zh": "Chinese",
    "ja": "Japanese",
    "ko": "Korean",
    "fr": "French",
    "de": "German",
    "es": "Spanish",
    "ru": "Russian"
}

# 默认翻译方向
DEFAULT_SOURCE_LANG = "en"
DEFAULT_TARGET_LANG = "zh"
