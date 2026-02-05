# 3D Tiles爬虫

一个用于下载3D Tiles协议模型文件的Python爬虫。支持递归下载所有引用的child tileset和glb/b3dm文件。

## 功能特性

- ✅ 递归下载tileset.json文件
- ✅ 自动下载引用的模型文件（glb, b3dm, i3dm, pnts, cmpt等）
- ✅ 处理外部tileset引用
- ✅ 支持相对路径和绝对路径解析
- ✅ 避免重复下载
- ✅ 支持glTF关联资源下载（bin文件、纹理等）
- ✅ 进度日志和错误处理
- ✅ 可配置的递归深度限制

## 安装

### 1. 安装Python依赖

```bash
pip install -r requirements.txt
```

### 2. 直接使用（无需安装）

```bash
python download.py --help
```

## 使用方法

### 基本用法

```bash
# 下载单个tileset
python download.py https://example.com/tileset -o ./output

# 指定最大递归深度
python download.py https://example.com/tileset -o ./output -d 5

# 启用详细输出
python download.py https://example.com/tileset -o ./output -v
```

### 参数说明

- `url`: tileset.json的URL或包含tileset.json的目录URL（必需）
- `-o, --output`: 输出目录（默认：`./downloads`）
- `-d, --depth`: 最大递归深度（默认：10）
- `-v, --verbose`: 启用详细输出

### 示例

1. **下载Cesium示例tileset**:
   ```bash
   python download.py https://raw.githubusercontent.com/CesiumGS/3d-tiles-samples/main/1.0/TilesetWithDiscreteLOD -o ./cesium_example
   ```

2. **下载本地服务器上的tileset**:
   ```bash
   python download.py http://localhost:8000/tileset -o ./local_download -d 3
   ```

## 代码结构

```
download.py              # 主爬虫程序
test_download.py         # 测试脚本
requirements.txt         # Python依赖
README.md               # 本文档
```

### 主要类说明

#### `TilesetDownloader`

主下载器类，提供以下功能：

- `__init__(base_url, output_dir, max_depth=10)`: 初始化下载器
- `download_tileset(tileset_url=None, depth=0)`: 下载tileset及其所有引用文件
- `_process_tile(tile_data, parent_url, depth)`: 处理单个tile
- `_process_content(content_data, parent_url)`: 处理tile内容
- `_download_model_file(file_uri, parent_url)`: 下载模型文件
- `_process_gltf_assets(gltf_path, gltf_url)`: 处理glTF关联资源

## 支持的3D Tiles格式

- **glTF/GLB**: 主要3D模型格式
- **B3DM**: Batched 3D Model（批处理3D模型）
- **I3DM**: Instanced 3D Model（实例化3D模型）
- **PNTS**: Point Cloud（点云）
- **CMPT**: Composite（复合格式）
- **外部tileset引用**: 支持嵌套tileset

## 测试

### 运行测试

```bash
# 运行所有测试
python test_download.py

# 只运行本地测试（无需网络）
python -c "from test_download import test_local_tileset; test_local_tileset()"
```

### 测试内容

1. **本地tileset测试**: 创建本地HTTP服务器测试基本功能
2. **示例tileset测试**: 下载Cesium官方示例（需要网络连接）

## 工作原理

1. **解析tileset.json**: 下载并解析tileset JSON文件
2. **递归遍历tile树**: 遍历root tile及其所有children
3. **下载内容文件**: 对于每个tile的content/contents，下载引用的模型文件
4. **处理外部引用**: 如果content引用外部tileset.json，递归下载
5. **处理glTF资源**: 对于glTF文件，下载关联的bin缓冲区和纹理图像
6. **保存文件**: 保持原始目录结构保存所有文件

## 错误处理

- 网络错误：重试并记录错误
- JSON解析错误：跳过无效文件
- 递归深度限制：防止无限递归
- 重复下载：跟踪已下载文件避免重复

## 注意事项

1. **网络要求**: 需要访问目标服务器的网络连接
2. **文件权限**: 确保有写入输出目录的权限
3. **递归深度**: 设置合适的递归深度避免下载过多文件
4. **服务器限制**: 某些服务器可能有速率限制或访问限制
5. **大文件下载**: 对于大文件，确保有足够的磁盘空间

## 扩展开发

### 添加新功能

1. **支持更多文件格式**: 在`_download_model_file`方法中添加对新格式的支持
2. **并行下载**: 使用多线程或异步IO提高下载速度
3. **断点续传**: 添加下载进度保存和恢复功能
4. **验证文件完整性**: 添加MD5/SHA校验

### 代码贡献

欢迎提交Issue和Pull Request！

## 许可证

MIT License

## 参考资源

- [3D Tiles Specification](https://docs.ogc.org/cs/22-025r4/22-025r4.html)
- [Cesium 3D Tiles Samples](https://github.com/CesiumGS/3d-tiles-samples)
- [glTF Specification](https://www.khronos.org/registry/glTF/specs/2.0/glTF-2.0.html)
