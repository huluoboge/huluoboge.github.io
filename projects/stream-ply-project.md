---
title: "Ply IO library"
date: 2025-08-23
tags: ["Ply", "point cloud", "Computer Geometry"]
excerpt: "一个ply格式点云读写库"
---

# Ply 格式点云读写库

这是一个使用C++开发Ply格式点云读写库，主要使用宏来控制方便自定义读写的内容，支持ascii和二进制格式，方便自定义属性扩展。

项目地址：[https://github.com/huluoboge/plycloud_io](https://github.com/huluoboge/plycloud_io)

## 项目特性

- ✅ **模板特化**：利用C++模板自动为向PLY文件写入不同属性类型生成代码
- ✅ **灵活的点类型**：支持定义带有浮点型、双精度型、int8_t等属性的自定义点结构体，并注册它们以便在生成PLY文件时自动处理
- ✅ **宏注册**：提供宏（如REGISTER_PLY_WRITE_POINT）简化新点类型及其属性的注册过程
- ✅ **流式写入**：通过PlyPointStreamWriter和PlyPointFileStreamWriter类方便地将点云写入标准或文件流，效率高
- ✅ **二进制与ASCII支持**：可在优化大小和速度的二进制格式与易于人类阅读的ASCII格式之间选择PLY输出
- ✅ **自动更新文件头信息**：动态管理PLY头部部分，在写入点时自动更新，确保记录了正确的顶点计数

### 使用方法

1. **定义你的点类型**：创建一个继承自`PlyPointXYZ`（或直接定义属性）的结构体，并包含所需的字段（如位置、颜色、强度、法线）。
2. **注册点类型**：使用提供的宏来注册你的点类型及其属性。例如写一个点：
```cpp
   struct MyPointType {
       float x, y, z;
       uint8_t r, g, b;
   };
   REGISTER_PLY_WRITE_POINT(MyPointType, (float, x, x)(float, y, y)(float, z, z)(uint8_t, r, r)(uint8_t, g, g)(uint8_t, b, b))
```

## 安装和使用

纯C++泛型，只需要头文件依赖。 
