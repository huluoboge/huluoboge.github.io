---
title: "BVH tree"
date: 2025-08-27
tags: ["BVH", "point cloud", "Computer Geometry", "Computer graphic", "mesh"]
excerpt: "个高性能的Bounding Volume Hierarchy (BVH) 树库"
---


# BVH Tree Library

一个高性能的Bounding Volume Hierarchy (BVH) 树库，支持面片网格和点云的快速射线相交检测。

**地址**： [https://github.com/huluoboge/bvh](https://github.com/huluoboge/bvh)  

## 特性

- **面片BVH树**: 支持三角形网格的快速射线相交检测
- **点云BVH树**: 支持点云的射线相交检测，包含多点命中功能
- **并行构建**: 使用多线程加速BVH树的构建过程
- **IO支持**: 支持BVH树的序列化和反序列化
- **高性能**: 基于Surface Area Heuristic (SAH) 优化构建

## 安装

### 依赖

- C++11 或更高版本
- 支持多线程的编译器

### 构建

项目使用头文件方式组织，可以直接包含到您的项目中：

```bash
git clone https://github.com/huluoboge/bvh.git
cd bvh
```

或者使用CMake构建：

```cmake
cmake_minimum_required(VERSION 3.10)
project(YourProject)

add_executable(your_app main.cpp)
target_include_directories(your_app PRIVATE path/to/bvh)
```

## 使用示例

### 面片BVH树使用

```cpp
#include "acc/bvh_tree_faces.h"
#include "math/vector.h"

int main() {
    using BVHTree = acc::BVHTree<uint32_t, math::Vec3f>;
    
    // 创建三角形网格数据
    std::vector<uint32_t> faces = {0, 1, 2, 3, 4, 5}; // 三角形索引
    std::vector<math::Vec3f> vertices = {
        {0, 0, 0}, {1, 0, 0}, {0, 1, 0}, // 第一个三角形
        {0, 0, 1}, {1, 0, 1}, {0, 1, 1}  // 第二个三角形
    };
    
    // 构建BVH树
    auto bvh = BVHTree::create(faces, vertices);
    
    // 创建射线
    acc::Ray<math::Vec3f> ray;
    ray.origin = {0, 0, -1};
    ray.dir = {0, 0, 1};
    ray.tmin = 0;
    ray.tmax = 100;
    
    // 射线相交检测
    BVHTree::Hit hit;
    if (bvh->intersect(ray, &hit)) {
        std::cout << "Hit triangle: " << hit.idx << " at distance: " << hit.t << std::endl;
    }
    
    // 保存BVH树到文件
    bvh->saveTo("mesh_bvh.bin");
    
    // 从文件加载BVH树
    auto loaded_bvh = BVHTree::load("mesh_bvh.bin");
    
    return 0;
}
```

### 点云BVH树使用

```cpp
#include "acc/bvh_tree_points.h"
#include "math/vector.h"

int main() {
    using BVHTreePoints = acc::BVHTreePoints<uint32_t, math::Vec3f>;
    
    // 创建点云数据
    std::vector<math::Vec3f> points = {
        {0, 0, 0}, {1, 0, 0}, {0, 1, 0}, {0, 0, 1}
    };
    float point_radius = 0.1f;
    
    // 构建点云BVH树
    auto bvh = BVHTreePoints::create(points, point_radius);
    
    // 创建射线
    acc::Ray<math::Vec3f> ray;
    ray.origin = {0, 0, -1};
    ray.dir = {0, 0, 1};
    ray.tmin = 0;
    ray.tmax = 100;
    
    // 单点命中检测
    BVHTreePoints::Hit hit;
    if (bvh->intersect(ray, &hit)) {
        std::cout << "Hit point: " << hit.idx << " at distance: " << hit.t << std::endl;
    }
    
    // 多点命中检测
    BVHTreePoints::MultiHit multi_hit;
    if (bvh->intersect(ray, &multi_hit)) {
        std::cout << "Hit " << multi_hit.mIdx.size() << " points" << std::endl;
    }
    
    // 保存BVH树到文件
    bvh->saveTo("points_bvh.bin");
    
    // 从文件加载BVH树
    auto loaded_bvh = BVHTreePoints::load("points_bvh.bin");
    
    return 0;
}
```

## API 文档

### BVHTree (面片)

#### 构造函数
- `BVHTree(std::vector<IdxType> const& faces, std::vector<Vec3fType> const& vertices, int max_threads)`

#### 主要方法
- `bool intersect(Ray ray, Hit* hit_ptr) const` - 射线相交检测
- `bool saveTo(const std::string& file) const` - 保存到文件
- `static Ptr load(const std::string& file)` - 从文件加载

### BVHTreePoints (点云)

#### 构造函数
- `BVHTreePoints(std::vector<Vec3fType> const& points, float radius, int max_threads)`

#### 主要方法
- `bool intersect(Ray const& ray, Hit* hit_ptr) const` - 单点命中检测
- `bool intersect(Ray const& ray, MultiHit* hit_ptr) const` - 多点命中检测
- `bool saveTo(const std::string& file) const` - 保存到文件
- `bool loadFrom(const std::string& file)` - 从文件加载
- `static Ptr load(const std::string& file)` - 静态加载方法

## 性能优化

- **SAH优化**: 使用Surface Area Heuristic进行最优分割
- **多线程构建**: 支持多线程并行构建BVH树
- **内存优化**: 紧凑的数据结构设计

## 文件格式

BVH树文件使用二进制格式存储，包含以下数据：

1. 版本号 (int)
2. 索引类型大小 (int)
3. 向量类型大小 (int)
4. 半径 (float, 仅点云)
5. 索引数据
6. 几何数据 (三角形或点)
7. 节点数据

## 许可证

BSD 3-Clause License

## 贡献

欢迎提交Issue和Pull Request来改进这个项目。

## 致谢

此项目基于MVE (Multi-View Environment) 项目的BVH实现，并增加了点云支持和IO功能。
