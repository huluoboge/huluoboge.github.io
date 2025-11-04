#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
翻译引擎模块
支持多种翻译服务：LibreTranslate、Google Cloud Translation
"""

import requests
import time
import random
from typing import Optional, Dict, Any
import json

from config import (
    LIBRETRANSLATE_ENDPOINTS,
    GOOGLE_TRANSLATE_ENDPOINT,
    ALIYUN_TRANSLATE_ENDPOINT,
    ALIYUN_TRANSLATE_REGION,
    TRANSLATION_CONFIG,
    DEFAULT_SOURCE_LANG,
    DEFAULT_TARGET_LANG
)


class TranslationError(Exception):
    """翻译错误异常"""
    pass


class BaseTranslator:
    """翻译器基类"""
    
    def __init__(self):
        self.timeout = TRANSLATION_CONFIG["timeout"]
        self.retry_attempts = TRANSLATION_CONFIG["retry_attempts"]
        self.delay_between_retries = TRANSLATION_CONFIG["delay_between_retries"]
    
    def translate(self, text: str, source_lang: str = DEFAULT_SOURCE_LANG, 
                  target_lang: str = DEFAULT_TARGET_LANG) -> str:
        """
        翻译文本
        
        Args:
            text: 要翻译的文本
            source_lang: 源语言代码
            target_lang: 目标语言代码
            
        Returns:
            翻译后的文本
        """
        raise NotImplementedError("子类必须实现此方法")
    
    def _make_request_with_retry(self, request_func, *args, **kwargs) -> Any:
        """
        带重试机制的请求
        
        Args:
            request_func: 请求函数
            *args, **kwargs: 请求参数
            
        Returns:
            请求结果
        """
        last_exception = None
        
        for attempt in range(self.retry_attempts):
            try:
                return request_func(*args, **kwargs)
            except Exception as e:
                last_exception = e
                if attempt < self.retry_attempts - 1:
                    delay = self.delay_between_retries * (2 ** attempt)  # 指数退避
                    delay += random.uniform(0, 1)  # 添加随机延迟避免同步请求
                    print(f"⚠️  请求失败，{delay:.1f}秒后重试... (尝试 {attempt + 1}/{self.retry_attempts})")
                    time.sleep(delay)
        
        raise TranslationError(f"所有重试尝试都失败了: {str(last_exception)}")


class LibreTranslate(BaseTranslator):
    """LibreTranslate翻译器"""
    
    def __init__(self):
        super().__init__()
        self.endpoints = LIBRETRANSLATE_ENDPOINTS.copy()
        random.shuffle(self.endpoints)  # 随机打乱端点顺序
    
    def translate(self, text: str, source_lang: str = DEFAULT_SOURCE_LANG, 
                  target_lang: str = DEFAULT_TARGET_LANG) -> str:
        """
        使用LibreTranslate翻译文本
        
        Args:
            text: 要翻译的文本
            source_lang: 源语言代码
            target_lang: 目标语言代码
            
        Returns:
            翻译后的文本
        """
        if not text.strip():
            return ""
        
        # 尝试所有可用的端点
        for endpoint in self.endpoints:
            try:
                return self._translate_with_endpoint(text, source_lang, target_lang, endpoint)
            except TranslationError:
                print(f"⚠️  端点 {endpoint} 不可用，尝试下一个...")
                continue
        
        raise TranslationError("所有LibreTranslate端点都不可用")
    
    def _translate_with_endpoint(self, text: str, source_lang: str, target_lang: str, 
                                endpoint: str) -> str:
        """
        使用特定端点进行翻译
        
        Args:
            text: 要翻译的文本
            source_lang: 源语言代码
            target_lang: 目标语言代码
            endpoint: API端点
            
        Returns:
            翻译后的文本
        """
        def request_func():
            payload = {
                "q": text,
                "source": source_lang,
                "target": target_lang,
                "format": "text"
            }
            
            headers = {
                "Content-Type": "application/json",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }
            
            response = requests.post(
                endpoint,
                json=payload,
                headers=headers,
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                result = response.json()
                if "translatedText" in result:
                    return result["translatedText"]
                else:
                    raise TranslationError(f"API响应格式错误: {result}")
            else:
                raise TranslationError(f"HTTP错误 {response.status_code}: {response.text}")
        
        return self._make_request_with_retry(request_func)


class GoogleTranslate(BaseTranslator):
    """Google Cloud Translation翻译器"""
    
    def __init__(self, api_key: Optional[str] = None):
        super().__init__()
        self.api_key = api_key
        self.endpoint = GOOGLE_TRANSLATE_ENDPOINT
    
    def translate(self, text: str, source_lang: str = DEFAULT_SOURCE_LANG, 
                  target_lang: str = DEFAULT_TARGET_LANG) -> str:
        """
        使用Google Cloud Translation翻译文本
        
        Args:
            text: 要翻译的文本
            source_lang: 源语言代码
            target_lang: 目标语言代码
            
        Returns:
            翻译后的文本
        """
        if not self.api_key:
            raise TranslationError("Google Cloud Translation需要API密钥")
        
        if not text.strip():
            return ""
        
        def request_func():
            params = {
                "q": text,
                "source": source_lang,
                "target": target_lang,
                "key": self.api_key,
                "format": "text"
            }
            
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }
            
            response = requests.post(
                self.endpoint,
                params=params,
                headers=headers,
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                result = response.json()
                if "data" in result and "translations" in result["data"]:
                    translations = result["data"]["translations"]
                    if translations:
                        return translations[0]["translatedText"]
                raise TranslationError(f"API响应格式错误: {result}")
            else:
                raise TranslationError(f"HTTP错误 {response.status_code}: {response.text}")
        
        return self._make_request_with_retry(request_func)


class AliyunTranslator(BaseTranslator):
    """阿里云机器翻译器"""
    
    def __init__(self, access_key_id: str, access_key_secret: str):
        super().__init__()
        self.access_key_id = access_key_id
        self.access_key_secret = access_key_secret
        
        # 导入阿里云SDK
        try:
            from alibabacloud_alimt20181012.client import Client as AlimtClient
            from alibabacloud_alimt20181012 import models as alimt_models
            from alibabacloud_tea_openapi import models as open_api_models
            from alibabacloud_tea_util import models as util_models
            from alibabacloud_tea_util.client import Client as UtilClient
            
            self.AlimtClient = AlimtClient
            self.alimt_models = alimt_models
            self.open_api_models = open_api_models
            self.util_models = util_models
            self.UtilClient = UtilClient
            
        except ImportError as e:
            raise ImportError("请安装阿里云SDK: pip install alibabacloud-alimt-20181012") from e
    
    def translate(self, text: str, source_lang: str = DEFAULT_SOURCE_LANG, 
                  target_lang: str = DEFAULT_TARGET_LANG) -> str:
        """
        使用阿里云机器翻译翻译文本
        
        Args:
            text: 要翻译的文本
            source_lang: 源语言代码
            target_lang: 目标语言代码
            
        Returns:
            翻译后的文本
        """
        if not self.access_key_id or not self.access_key_secret:
            raise TranslationError("阿里云机器翻译需要AccessKey ID和Secret")
        
        if not text.strip():
            return ""
        
        def request_func():
            # 创建配置对象
            config = self.open_api_models.Config(
                access_key_id=self.access_key_id,
                access_key_secret=self.access_key_secret,
                endpoint=ALIYUN_TRANSLATE_ENDPOINT,
                region_id=ALIYUN_TRANSLATE_REGION
            )
            
            # 创建客户端
            client = self.AlimtClient(config)
            
            # 创建翻译请求
            translate_request = self.alimt_models.TranslateGeneralRequest(
                format_type="text",
                source_language=source_lang,
                target_language=target_lang,
                source_text=text,
                scene="general"
            )
            
            # 执行翻译
            runtime = self.util_models.RuntimeOptions()
            response = client.translate_general_with_options(translate_request, runtime)
            
            if response.status_code == 200:
                if hasattr(response.body, 'data') and hasattr(response.body.data, 'translated'):
                    return response.body.data.translated
                else:
                    raise TranslationError(f"API响应格式错误: {response.body}")
            else:
                raise TranslationError(f"HTTP错误 {response.status_code}: {response.body}")
        
        return self._make_request_with_retry(request_func)


class TranslationManager:
    """翻译管理器"""
    
    def __init__(self, engine: str = "libre", google_api_key: Optional[str] = None,
                 aliyun_access_key_id: Optional[str] = None, 
                 aliyun_access_key_secret: Optional[str] = None):
        """
        初始化翻译管理器
        
        Args:
            engine: 翻译引擎 ("libre", "google" 或 "aliyun")
            google_api_key: Google Cloud Translation API密钥
            aliyun_access_key_id: 阿里云AccessKey ID
            aliyun_access_key_secret: 阿里云AccessKey Secret
        """
        self.engine = engine.lower()
        self.google_api_key = google_api_key
        self.aliyun_access_key_id = aliyun_access_key_id
        self.aliyun_access_key_secret = aliyun_access_key_secret
        
        if self.engine == "libre":
            self.translator = LibreTranslate()
        elif self.engine == "google":
            self.translator = GoogleTranslate(google_api_key)
        elif self.engine == "aliyun":
            self.translator = AliyunTranslator(aliyun_access_key_id, aliyun_access_key_secret)
        else:
            raise ValueError(f"不支持的翻译引擎: {engine}")
    
    def translate_text(self, text: str, source_lang: str = DEFAULT_SOURCE_LANG, 
                       target_lang: str = DEFAULT_TARGET_LANG) -> str:
        """
        翻译文本
        
        Args:
            text: 要翻译的文本
            source_lang: 源语言代码
            target_lang: 目标语言代码
            
        Returns:
            翻译后的文本
        """
        try:
            return self.translator.translate(text, source_lang, target_lang)
        except TranslationError as e:
            # 如果当前引擎失败，尝试切换到备用引擎
            if self.engine == "libre":
                if self.google_api_key:
                    print("🔄 LibreTranslate失败，尝试切换到Google Translate...")
                    backup_translator = GoogleTranslate(self.google_api_key)
                    try:
                        return backup_translator.translate(text, source_lang, target_lang)
                    except TranslationError:
                        pass
                elif self.aliyun_access_key_id and self.aliyun_access_key_secret:
                    print("🔄 LibreTranslate失败，尝试切换到阿里云机器翻译...")
                    backup_translator = AliyunTranslator(self.aliyun_access_key_id, self.aliyun_access_key_secret)
                    try:
                        return backup_translator.translate(text, source_lang, target_lang)
                    except TranslationError:
                        pass
            
            raise e


def main():
    """测试函数"""
    # 测试LibreTranslate
    print("测试LibreTranslate...")
    translator = LibreTranslate()
    
    test_text = "Hello, this is a test for translation service."
    try:
        result = translator.translate(test_text, "en", "zh")
        print(f"原文: {test_text}")
        print(f"译文: {result}")
    except Exception as e:
        print(f"翻译失败: {e}")


if __name__ == "__main__":
    main()
