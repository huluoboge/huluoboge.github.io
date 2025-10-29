
# 可微高斯渲染器

https://github.com/graphdeco-inria/diff-gaussian-rasterization


# 3D 高斯点染简介

https://huggingface.co/blog/zh/gaussian-splatting

# Meshing

## SuGaR
SuGaR: Surface‑Aligned Gaussian Splatting for Efficient 3D Mesh Reconstruction and High‑Quality Mesh Rendering (Guédon & Lepetit, 2024)

这篇论文专门针对从 3DGS 生成或优化 Mesh 的问题。主要贡献：

在 3D 高斯点云优化过程中引入 表面对齐（surface-alignment） 的正则项，使得高斯更靠近真实场景表面。 
arXiv
+1

利用该对齐结构，抽取点样本并以 Poisson surface reconstruction 的方式重建 Mesh，而不是传统的 Marching Cubes，从而更快、规模更大、细节保留更好。 
GitHub
+1

最终组合了一个 Mesh + 高斯混合（hybrid） 表示，这样既可用于编辑、动画、组合，也保留高斯渲染优势。 
arXiv


## 3D Gaussian Splatting with Normal Information for Mesh Extraction and Improved Rendering (Krishnan et al., 2025)
这篇工作进一步推进了 Mesh 优化方向：

引入法线监督（从 SDF/高斯估计的法线梯度）来改善几何重建质量，特别是在高曲率或细节丰富区域。 
arXiv

虽然直接不是“从高斯优化网格”的完全方案，但在从高斯→Mesh 的路径上提供了很有价值的正则项／损失函数思路。

## GausSurf: Geometry-Guided 3D Gaussian Splatting for Surface Reconstruction

https://jiepengwang.github.io/GausSurf/

3D高斯散射技术在具有实时渲染能力的新型视图合成方面取得了令人瞩目的性能。然而，利用3D高斯函数重建具有精细细节的高质量表面仍然是一项具有挑战性的任务。本文提出了一种名为GausSurf的新型高质量表面重建方法。该方法利用场景中纹理丰富区域的多视图一致性几何指导和纹理稀疏区域的法线先验信息。我们观察到，场景可以主要分为两个区域：1）纹理丰富区域和2）纹理稀疏区域。为了在纹理丰富区域实现多视图一致性，我们通过引入传统的基于块匹配的多视图立体（MVS）方法来指导几何优化，从而提高重建质量。该方法实现了高斯函数优化和块匹配细化之间的相互促进，显著提升了重建结果并加速了训练过程。同时，对于纹理稀疏区域，我们利用预训练的法线估计模型提供的法线先验信息来指导优化。在 DTU 和 Tanks and Temples 数据集上进行的大量实验表明，我们的方法在重建质量和计算时间方面都优于最先进的方法。

## HDGS: Textured 2D Gaussian Splatting for Enhanced Scene Rendering


# 工程／优化方向

DashGaussian: Optimizing 3D Gaussian Splatting in 200 Seconds（Chen et al., 2025）聚焦于加速 3DGS 优化，但其方法同样可为 Mesh 优化场景提供更快收敛的基础。 
CVF开放获取

还有 3DGS‑LM: Faster Gaussian‑Splatting Optimization with Levenberg‑Marquardt（Höllein et al., 2025），提供更高效的优化器替代思路。