# PDF翻译工具

一个免费的PDF翻译工具，支持将PDF文件翻译为多种语言，使用LibreTranslate、Google Cloud Translation和阿里云机器翻译三种翻译引擎。

## 功能特点

- ✅ **完全免费** - 使用LibreTranslate公共实例，无需付费
- ✅ **多引擎支持** - 支持LibreTranslate、Google Cloud Translation和阿里云机器翻译
- ✅ **批量处理** - 支持单个文件和批量翻译
- ✅ **智能分段** - 自动分割长文本，避免API限制
- ✅ **进度显示** - 实时显示翻译进度
- ✅ **错误恢复** - 网络错误自动重试
- ✅ **多语言支持** - 支持中、英、日、韩等多种语言
- ✅ **国内友好** - 阿里云机器翻译国内访问稳定快速

## 安装依赖

```bash
pip install -r requirements.txt
```

## 使用方法

### 基本使用

```bash
# 翻译单个PDF文件（使用默认的LibreTranslate引擎）
python main.py --input paper.pdf

# 指定输出文件
python main.py --input paper.pdf --output translated.txt

# 批量翻译目录中的所有PDF文件
python main.py --input papers/ --output translations/
```

### 高级选项

```bash
# 使用Google翻译引擎（需要API密钥）
python main.py --input paper.pdf --engine google --api-key YOUR_API_KEY

# 使用阿里云机器翻译（需要AccessKey）
python main.py --input paper.pdf --engine aliyun --aliyun-access-key-id YOUR_ID --aliyun-access-key-secret YOUR_SECRET

# 指定翻译语言（英译中）
python main.py --input paper.pdf --source en --target zh

# 指定翻译语言（中译英）
python main.py --input paper.pdf --source zh --target en
```

### 支持的语言

- `en` - English
- `zh` - Chinese
- `ja` - Japanese
- `ko` - Korean
- `fr` - French
- `de` - German
- `es` - Spanish
- `ru` - Russian

## 费用说明

### LibreTranslate
- **完全免费**，无任何费用
- 使用公共实例，可能有速率限制
- 适合个人和小规模使用

### Google Cloud Translation
- **免费额度**：每月50万字符
- **超出费用**：$20/百万字符（标准版）
- **适合场景**：需要更高翻译质量的场景

### 阿里云机器翻译
- **免费额度**：每月200万字符（通用版）
- **超出费用**：约¥15/百万字符
- **适合场景**：国内访问稳定，专业术语支持较好

## 项目结构

```
pdf_translator/
├── main.py           # 主程序
├── pdf_parser.py     # PDF解析模块
├── translator.py     # 翻译引擎模块
├── config.py         # 配置文件
├── requirements.txt  # 依赖包
└── README.md         # 说明文档
```

## 技术细节

### PDF解析
- 使用 `pdfplumber` 库提取文本
- 智能清理页眉页脚等噪音
- 保持原文段落结构

### 文本处理
- 自动分割长文本（最大2000字符/块）
- 按段落和句子智能分割
- 避免翻译API的长度限制

### 翻译引擎
- **LibreTranslate**：主要引擎，完全免费
- **Google Cloud Translation**：备用引擎，质量更高
- **阿里云机器翻译**：国内访问稳定，专业术语支持好
- 自动引擎切换机制
- 错误重试和指数退避

## 注意事项

1. **网络连接**：需要稳定的网络连接访问翻译API
2. **PDF质量**：扫描版PDF可能无法正确提取文本
3. **速率限制**：免费服务可能有请求频率限制
4. **翻译质量**：学术论文的专业术语可能需要人工校对

## 故障排除

### 常见问题

**Q: 翻译失败，显示网络错误**
A: 检查网络连接，或尝试更换翻译引擎

**Q: PDF无法解析**
A: 确保PDF文件不是扫描版，可以尝试其他PDF阅读器测试

**Q: 翻译结果质量不佳**
A: 尝试使用Google翻译引擎，或对关键段落进行人工校对

**Q: 请求过于频繁被限制**
A: 增加请求间隔时间，或使用多个翻译端点轮询

## 许可证

MIT License

## 贡献

欢迎提交Issue和Pull Request来改进这个工具！
