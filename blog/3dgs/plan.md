---
title: "3DGS 文章列表"
date: 2025-10-28T20:51:00+08:00
tags:
[
"3DGS",
"Neural Radiance Fields",
"NeRF",
"Renderer",
"Computer Vision",
"Computer Graphics",
]
excerpt: "总结 3DGS 文章列表"
draft: true
---


# 一些思路 

**You:**

我有个想法。如果我有一个特别好的mvs的点云，或者lidar扫描的，甚至是mesh，能不能让我的3DGS的训练更加容易？

* * *

**ChatGPT:**

嘿，这个想法其实非常棒，小白菜 🍃！而且你一语击中了当前很多研究团队正在探索的方向。确实，**高质量几何先验（如LiDAR点云、MVS点云或mesh）**能极大改善3D Gaussian Splatting（3DGS）的训练稳定性、收敛速度和渲染质量。我们可以分几层来看它怎么起作用👇

* * *

### 💡 一、3DGS训练的核心瓶颈

3DGS其实是从SfM或COLMAP那种稀疏点云开始，用高斯点近似真实场景，然后通过梯度优化更新每个高斯的：

* 位置（xyz）
    
* 尺度（covariance）
    
* 方向（rotation）
    
* 颜色（SH参数）
    

所以它一开始的几何质量——取决于SfM重建的稀疏点。  
如果初始化点云有偏（尤其在无纹理、反光、重复纹理场景），那早期阶段的高斯就会学到“错的位置”，导致训练难收敛或ghost artifacts。

* * *

### ⚙️ 二、如果你有高质量点云或mesh

这就像给3DGS打了一针“强心剂”💉，可以在几个方面改进：

#### ✅ 1. 更好的几何初始化

你可以直接用LiDAR或MVS点云来初始化高斯的位置和法线（甚至covariance可以用点云局部PCA近似表面方向）。  
→ 这样early stage的渲染loss收敛更快、伪影更少。

#### ✅ 2. 可直接利用Mesh或深度图投影

如果有mesh，可以在每张训练图像上投影出精确深度图作为监督信号，对高斯中心的位置施加regularization项：  
$L_{depth} = \|D_{rendered} - D_{gt}\|_1$  
→ 控制高斯漂移（drift），提升几何一致性。

#### ✅ 3. 减少冗余点 & 改善高斯分布

高精度点云还能帮助在初始化阶段做**均匀采样**或**表面重采样**（比如Poisson-disk采样），使高斯点分布合理，不至于太稀或太密。

#### ✅ 4. 可以辅助颜色学习

如果点云或mesh带纹理，甚至能初始化颜色/SH参数，加速辐射场拟合。

* * *

### 🧪 三、已有类似方向

其实最近几个月有几个论文/实验在这么干，比如：

* **“LiGS: LiDAR Gaussian Splatting” (2024)**：用激光点云直接初始化3DGS，训练快、渲染稳。
    
* **“Depth-Regularized 3DGS”**：引入深度先验项，让高斯的z一致于估计深度。
    
* **“Mesh-guided Gaussian Splatting”**：把mesh表面转成高斯分布，然后只优化颜色和scale。
    

这些方法都显著减少了训练时间（有的从几小时降到几十分钟）而视觉质量相当甚至更好。

* * *

### 🚀 四、小萝卜建议的落地路线

如果你要自己实验：

1. 用你现有的**高质量点云或mesh** → 均匀采样几万个点。
    
2. 对每个点计算法线（用PCA或mesh面法线），初始化高斯covariance。
    
3. 用这些点代替SfM点作为3DGS初始化输入。
    
4. 保留相机pose不变，正常训练。
    
5. 可选：加一个深度约束 loss 或 smoothness loss。
    

* * *
---

