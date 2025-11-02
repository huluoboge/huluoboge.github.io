# LibreTranslate 自建服务器安装指南

本文档介绍如何安装和配置自建LibreTranslate服务器，以获得更好的翻译体验。

## 安装方式

### 方式一：使用Docker（推荐）

```bash
# 拉取并运行LibreTranslate容器
docker run -ti --rm -p 5000:5000 libretranslate/libretranslate

# 后台运行（生产环境）
docker run -d -p 5000:5000 --name libretranslate libretranslate/libretranslate

# 查看运行状态
docker ps

# 查看日志
docker logs libretranslate
```

### 方式二：使用pip安装

```bash
# 安装LibreTranslate
pip install libretranslate

# 启动服务器
libretranslate --host 0.0.0.0 --port 5000

# 或者使用gunicorn（生产环境）
libretranslate --host 0.0.0.0 --port 5000 --workers 4
```

### 方式三：从源码编译

```bash
# 克隆仓库
git clone https://github.com/LibreTranslate/LibreTranslate
cd LibreTranslate

# 安装依赖
pip install -e .

# 启动服务器
libretranslate --host 0.0.0.0 --port 5000
```

## 首次启动

首次启动时，LibreTranslate会自动下载所需的翻译模型。这可能需要一些时间，具体取决于您的网络速度。

**下载的模型包括：**
- en-zh (英语-中文)
- zh-en (中文-英语)
- 以及其他常用语言对

**下载进度显示：**
```
Downloading translation model en-zh...
Downloading translation model zh-en...
...
```

## 验证安装

启动后，可以通过以下方式验证服务器是否正常工作：

```bash
# 测试API端点
curl -X POST "http://localhost:5000/translate" \
  -H "Content-Type: application/json" \
  -d '{"q": "Hello, world!", "source": "en", "target": "zh", "format": "text"}'
```

预期响应：
```json
{
  "translatedText": "你好，世界！"
}
```

## 配置选项

### 常用启动参数

```bash
# 指定主机和端口
libretranslate --host 0.0.0.0 --port 5000

# 限制加载的语言模型（节省内存）
libretranslate --load-only en,zh

# 启用API密钥验证
libretranslate --req-limit 100 --api-keys

# 使用GPU加速（如果可用）
libretranslate --use-gpu
```

### 环境变量配置

```bash
# 设置环境变量
export LT_LOAD_ONLY="en,zh"
export LT_HOST="0.0.0.0"
export LT_PORT="5000"
export LT_THREADS="4"

# 然后启动
libretranslate
```

## 性能优化

### 内存优化

如果内存有限，可以只加载需要的语言模型：

```bash
# 只加载英-中、中-英翻译模型
libretranslate --load-only en,zh
```

### 多线程配置

```bash
# 使用4个工作线程
libretranslate --threads 4
```

### 使用GPU加速

如果有NVIDIA GPU：

```bash
# 安装CUDA支持
pip install libretranslate[gpu]

# 使用GPU
libretranslate --use-gpu
```

## 与PDF翻译工具集成

### 自动检测

PDF翻译工具会自动优先使用本地实例（localhost:5000），如果本地实例不可用，会自动切换到公共实例。

### 手动配置

如果需要使用其他端口或远程服务器，可以修改 `config.py`：

```python
LIBRETRANSLATE_ENDPOINTS = [
    "http://your-server:5000/translate",  # 自定义服务器
    "http://localhost:5000/translate",    # 本地实例
    "https://libretranslate.com/translate"  # 公共实例
]
```

## 故障排除

### 常见问题

**Q: 启动时提示端口被占用**
A: 更换端口或停止占用该端口的进程
```bash
libretranslate --port 5001
```

**Q: 内存不足**
A: 限制加载的语言模型
```bash
libretranslate --load-only en,zh
```

**Q: 模型下载失败**
A: 检查网络连接，或手动下载模型

**Q: 翻译速度慢**
A: 增加工作线程数或使用GPU加速

### 日志查看

```bash
# Docker方式
docker logs libretranslate

# pip安装方式
libretranslate --debug
```

## 生产环境部署

### 使用systemd服务

创建服务文件 `/etc/systemd/system/libretranslate.service`：

```ini
[Unit]
Description=LibreTranslate Server
After=network.target

[Service]
Type=simple
User=libretranslate
WorkingDirectory=/opt/libretranslate
ExecStart=/usr/local/bin/libretranslate --host 0.0.0.0 --port 5000 --threads 4
Restart=always

[Install]
WantedBy=multi-user.target
```

启用服务：
```bash
sudo systemctl daemon-reload
sudo systemctl enable libretranslate
sudo systemctl start libretranslate
```

### 使用反向代理（Nginx）

```nginx
server {
    listen 80;
    server_name translate.yourdomain.com;
    
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## 资源监控

### 内存使用
- 每个语言模型约占用1-2GB内存
- 建议服务器至少有4GB可用内存

### 磁盘空间
- 模型文件总共约2-4GB
- 确保有足够的磁盘空间

### 网络带宽
- 首次启动需要下载模型（约2-4GB）
- 日常使用带宽需求较低

## 安全考虑

### API密钥保护
```bash
# 启用API密钥验证
libretranslate --api-keys

# 设置API密钥
export LT_API_KEYS="your-secret-key-1,your-secret-key-2"
```

### 请求限制
```bash
# 限制每分钟请求数
libretranslate --req-limit 100
```

通过自建LibreTranslate服务器，您可以获得更好的翻译体验，不受公共实例的速率限制，同时保护您的隐私。
