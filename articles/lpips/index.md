---
title: "LPIPS:Learned Perceptual Image Patch Similarity"
date: 2025-10-29T22:30:00+08:00
tags: ["SSIM", "Structural similarity index measure"]
excerpt: "LPIPS是一种**感知图像相似度（perceptual similarity）**的度量方法，由 Richard Zhang 等人在 2018 年提出（论文：“The Unreasonable Effectiveness of Deep Features as a Perceptual Metric”，CVPR 2018）。LPIPS 衡量两张图像在深度特征空间中的“感知距离”，比传统的 L2 或 SSIM 更符合人眼主观感受。"
draft: false
---

# LPIPS

LPIPS（Learned Perceptual Image Patch Similarity） 是一种**感知图像相似度（perceptual similarity）**的度量方法，由 Richard Zhang 等人在 2018 年提出（论文：“The Unreasonable Effectiveness of Deep Features as a Perceptual Metric”，CVPR 2018）。

LPIPS 衡量两张图像在深度特征空间中的“感知距离”，比传统的 L2 或 SSIM 更符合人眼主观感受。


--- 
## 背景问题

传统指标如：

- L2（MSE）：逐像素比较 → 对人眼感受不敏感

- SSIM：考虑亮度、对比度、结构，但仍然不完全符合人类主观视觉

LPIPS 想解决的问题是：

> “如何让计算机评估两张图像是否‘看起来’相似，而不是仅仅数值上相似？”

## 核心思想与计算流程

1. **输入两张图像** $x, x'$
    
2. **送入一个预训练网络**（如 VGG、AlexNet、SqueezeNet）
    
3. **提取多层特征图** $f_l(x), f_l(x')$
    
4. 对每一层：
    
    * 计算归一化后的特征差：
        
        $$d_l = \| \hat{f}_l(x) - \hat{f}_l(x') \|_2^2$$
    * 对各通道乘上一个**学习到的权重** $w_l$
        
5. 各层结果加权求和，得到 LPIPS：
    
    $$\text{LPIPS}(x, x') = \sum_l w_l \cdot d_l$$

* * *

## 🎯 特点

| 特性 | 描述 |
| --- | --- |
| 感知一致性 | 结果更接近人类主观判断 |
| 可学习 | 权重 $w_l$ 可训练，用人工评分数据来校准 |
| 模型无关 | 可选不同 backbone（VGG, AlexNet, SqueezeNet） |
| 应用场景 | 图像重建、生成对抗网络（GAN）评估、风格迁移、NeRF重建等 |

* * *

## 🔍 对比示例

| 指标 | 数学意义 | 感知相关性 |
| --- | --- | --- |
| L2 / MSE | 像素差平方 | 差 |
| PSNR | MSE转化 | 差 |
| SSIM | 局部结构相似性 | 中等 |
| **LPIPS** | 深度特征差异 | **高** ✅ |

* * *

## 📦 Python 实现（PyTorch）

```python
import lpips
import torch

# 初始化 LPIPS 模型（使用 VGG backbone）
loss_fn = lpips.LPIPS(net='vgg')

# 两张图像，值范围 [-1, 1]
img0 = torch.randn(1, 3, 256, 256)
img1 = torch.randn(1, 3, 256, 256)

# 计算 LPIPS 距离
dist = loss_fn(img0, img1)
print('LPIPS distance:', dist.item())
```

结果越接近 **0** 表示越相似（感知上一致）。

* * *

## 🧩 参考文献

> Richard Zhang, Phillip Isola, Alexei A. Efros, Eli Shechtman, Oliver Wang.  
> **"The Unreasonable Effectiveness of Deep Features as a Perceptual Metric"**  
> _CVPR 2018_  
> 📄 Paper | [💻 GitHub](https://github.com/richzhang/PerceptualSimilarity)

* * *