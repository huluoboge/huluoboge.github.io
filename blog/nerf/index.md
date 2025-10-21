---
title: "NeRF 文章列表"
date: 2025-10-20T22:51:00+08:00
tags:
  [
    "Neural Radiance Fields",
    "NeRF",
    "Renderer",
    "Computer Vision",
    "Computer Graphics",
  ]
excerpt: "总结NeRF 文章列表"
draft: false
---

# Neural Radiance Fields 文献类型 × 年份 矩阵一览表

| 类型 / 年份| 2019| 2020| 2021| 2022| 2023| 2024| 2025|
|--- | --- | --- | --- | --- | --- | --- | --- |
| 原始 / 分析| Local Light Field Fusion (pre) | NeRF (Mildenhall et al.); NeRF++  | Mip-NeRF; NeRF in the Wild| Mip-NeRF 360| —| Baking Neural Radiance Fields (TPAMI 2024) | HR-NeRF (highlight focus) |
| 加速 / 实时 / 显式表征| —| NSVF (Neural Sparse Voxel Fields) | PlenOctrees; KiloNeRF; FastNeRF; DONeRF | Plenoxels; DirectVoxGO; TensoRF; Point-NeRF; Instant-NGP | 3D Gaussian Splatting; Zip-NeRF; MobileNeRF | Baking / Pre-baked pipelines (TPAMI 2024)  | —|
| 泛化 / Few-shot / 条件化    | —| —| pixelNeRF; IBRNet; MVSNeRF; BARF| Dense Depth Priors; NeXT| Zip-NeRF / Mip-VoG (多尺度融合)| Baking & ScanNeRF Benchmarks| —|
| 动态 / 时序 / 变形| —| D-NeRF; Nerfies| TiNeuVox; NSFF| Block-NeRF| —| —| —                         |
| 语义 / 可编辑 / 风格化      | —| —| StylizedNeRF; Ref-NeRF| NeRF-W; StylizedNeRF| —| —| —|
| 大场景 / 工具 / 基准 / 应用 | —| —| ScanNeRF; Block-NeRF| Plenoxels; DirectVoxGO; TensoRF (工程部署)| 3DGS; 实时显式方法| TPAMI Baking Paper| HR-NeRF (特定问题研究)|

---

# Neural Radiance Fields 文献列表

## 1. Mip-NeRF: A Multiscale Representation for Anti-Aliasing Neural Radiance Fields

**作者**: J. Barron and B. Mildenhall and Matthew Tancik and Peter Hedman and Ricardo Martin-Brualla and Pratul P. Srinivasan

**出处**: 2021 IEEE/CVF International Conference on Computer Vision (ICCV), 2021, 卷 null, 页 5835-5844

**链接**: [原文链接](https://www.semanticscholar.org/paper/21336e57dc2ab9ae2171a0f6c35f7d1aba584796) | [DOI](https://doi.org/10.1109/ICCV48922.2021.00580) | [arXiv](https://arxiv.org/abs/2103.13415)

**摘要**: 神经辐射场（NeRF）使用的渲染过程对每个像素使用单条射线进行场景采样，因此在训练或测试图像以不同分辨率观察场景内容时，可能会产生过度模糊或锯齿化的渲染结果。通过每个像素渲染多条射线进行超采样的直接解决方案对于 NeRF 来说是不切实际的，因为渲染每条射线需要查询多层感知器数百次。我们的解决方案（我们称之为"mip-NeRF"，类似于"mipmap"）将 NeRF 扩展为在连续值尺度上表示场景。通过高效渲染抗锯齿的圆锥截头体而不是射线，mip-NeRF 减少了令人不快的锯齿伪影，并显著提高了 NeRF 表示精细细节的能力，同时比 NeRF 快 7%且体积小一半。与 NeRF 相比，mip-NeRF 在 NeRF 呈现的数据集上平均错误率降低了 17%，在我们呈现的具有挑战性的多尺度变体数据集上降低了 60%。Mip-NeRF 还能够在我们多尺度数据集上匹配暴力超采样 NeRF 的精度，同时速度快 22 倍。

---

## 2. ScanNeRF: a Scalable Benchmark for Neural Radiance Fields

**作者**: Luca De Luigi and Damiano Bolognini and Federico Domeniconi and Daniele De Gregorio and Matteo Poggi and L. D. Stefano

**出处**: 2023 IEEE/CVF Winter Conference on Applications of Computer Vision (WACV), 2022, 卷 null, 页 816-825

**链接**: [原文链接](https://www.semanticscholar.org/paper/c751c9edfcfc62cdb40c3a6c652708ef05302e24) | [DOI](https://doi.org/10.1109/WACV56688.2023.00088) | [arXiv](https://arxiv.org/abs/2211.13762)

**摘要**: 在本文中，我们提出了第一个专门用于评估神经辐射场（NeRFs）以及一般神经渲染（NR）框架的真实基准。我们设计并实现了一个有效的管道，用于大量且轻松地扫描真实物体。我们的扫描站硬件预算不到 500 美元，可以在短短 5 分钟内收集扫描对象的大约 4000 张图像。该平台用于构建 ScanNeRF，这是一个具有多个训练/验证/测试分割的数据集，旨在在不同条件下对现代 NeRF 方法的性能进行基准测试。相应地，我们在其上评估了三种最先进的 NeRF 变体，以突出它们的优势和劣势。该数据集可在我们的项目页面上获得，同时还有一个在线基准来促进更好 NeRF 的开发。

---

## 3. Volume Rendering of Neural Implicit Surfaces

**作者**: Lior Yariv and Jiatao Gu and Yoni Kasten and Y. Lipman

**出处**: 2021

**链接**: [原文链接](https://www.semanticscholar.org/paper/eded1f3acaba853499fd5a6b3de63fa9d5e0cef2) | [arXiv](https://arxiv.org/abs/2106.12052)

**摘要**: 神经体积渲染最近因其在从稀疏输入图像集合中合成场景新视图方面的成功而变得越来越受欢迎。到目前为止，神经体积渲染技术学习的几何形状是使用通用密度函数建模的。此外，几何本身是使用密度函数的任意水平集提取的，导致噪声大、通常保真度低的重建。本文的目标是改进神经体积渲染中的几何表示和重建。我们通过将体积密度建模为几何的函数来实现这一点。这与先前将几何建模为体积密度函数的工作形成对比。更详细地说，我们将体积密度函数定义为应用于有符号距离函数（SDF）表示的拉普拉斯累积分布函数（CDF）。这种简单的密度表示有三个好处：（i）它为神经体积渲染过程中学习的几何提供了有用的归纳偏置；（ii）它促进了不透明度近似误差的界限，导致对视线的精确采样。精确采样对于提供几何和辐射度的精确耦合很重要；（iii）它允许在体积渲染中高效无监督地解耦形状和外观。将这种新的密度表示应用于具有挑战性的场景多视图数据集产生了高质量的几何重建，优于相关基线。此外，由于两者的解耦，可以在场景之间切换形状和外观。

---

## 4. 3D Gaussian Splatting for Real-Time Radiance Field Rendering

**作者**: Bernhard Kerbl and Georgios Kopanas and Thomas Leimkuehler and G. Drettakis

**出处**: ACM Transactions on Graphics (TOG), 2023, 卷 42, 页 1 - 14

**链接**: [原文链接](https://www.semanticscholar.org/paper/2cc1d857e86d5152ba7fe6a8355c2a0150cc280a) | [DOI](https://doi.org/10.1145/3592433) | [arXiv](https://arxiv.org/abs/2308.04079)

**摘要**: 辐射场方法最近彻底改变了从多张照片或视频捕获的场景的新视图合成。然而，实现高视觉质量仍然需要训练和渲染成本高昂的神经网络，而最近的更快方法不可避免地以质量换取速度。对于无界和完整场景（而不是孤立对象）以及 1080p 分辨率渲染，目前没有方法能够实现实时显示速率。我们引入了三个关键元素，使我们能够实现最先进的视觉质量，同时保持有竞争力的训练时间，更重要的是允许在 1080p 分辨率下进行高质量实时（≥ 30 fps）新视图合成。首先，从相机校准期间产生的稀疏点开始，我们用 3D 高斯表示场景，这些高斯保留了连续体积辐射场用于场景优化的理想特性，同时避免了在空空间中进行不必要的计算；其次，我们对 3D 高斯执行交错优化/密度控制，特别是优化各向异性协方差以实现场景的准确表示；第三，我们开发了一种快速可见性感知渲染算法，支持各向异性溅射，既加速了训练又允许实时渲染。我们在几个已建立的数据集上展示了最先进的视觉质量和实时渲染。

---

## 5. Nerfies: Deformable Neural Radiance Fields

**作者**: Keunhong Park and U. Sinha and J. Barron and Sofien Bouaziz and Dan B. Goldman and S. Seitz and Ricardo Martin-Brualla

**出处**: 2021 IEEE/CVF International Conference on Computer Vision (ICCV), 2020, 卷 null, 页 5845-5854

**链接**: [原文链接](https://www.semanticscholar.org/paper/0f1af3f94f4699cd70a554f68f8f9e2c8e3d53dd) | [DOI](https://doi.org/10.1109/ICCV48922.2021.00581) | [arXiv](https://arxiv.org/abs/2011.12948)

**摘要**: 我们提出了第一种能够使用从手机随意捕获的照片/视频逼真地重建可变形场景的方法。我们的方法通过优化一个额外的连续体积变形场来增强神经辐射场（NeRF），该变形场将每个观察点扭曲到一个规范的 5D NeRF 中。我们观察到这些类似 NeRF 的变形场容易陷入局部最小值，并提出了一种用于基于坐标模型的从粗到精优化方法，允许更鲁棒的优化。通过将几何处理和物理模拟的原理适应于类似 NeRF 的模型，我们提出了变形场的弹性正则化，进一步提高了鲁棒性。我们展示了我们的方法可以将随意捕获的自拍照片/视频转换为可变形 NeRF 模型，允许从任意视点对主体进行逼真渲染，我们称之为"nerfies"。我们通过使用带有两部手机的装置收集时间同步数据来评估我们的方法，产生在不同视点下相同姿势的训练/验证图像。我们展示了我们的方法忠实地重建了非刚性变形场景，并以高保真度再现了未见过的视图。

---

## 6. DONeRF: Towards Real‐Time Rendering of Compact Neural Radiance Fields using Depth Oracle Networks

**作者**: Thomas Neff and P. Stadlbauer and Mathias Parger and A. Kurz and J. H. Mueller and C. R. A. Chaitanya and Anton Kaplanyan and M. Steinberger

**出处**: Computer Graphics Forum, 2021, 卷 40, 页 null

**链接**: [原文链接](https://www.semanticscholar.org/paper/792f25e5a2f167df962e0d25b6bee5474a86605f) | [DOI](https://doi.org/10.1111/cgf.14340) | [arXiv](https://arxiv.org/abs/2103.03231)

**摘要**: 最近围绕隐式神经表示（如 NeRF）的研究爆炸表明，在紧凑神经网络中隐式存储高质量场景和照明信息具有巨大潜力。然而，阻止 NeRF 在实时渲染应用中使用的一个主要限制是沿每条视线进行过多网络评估的禁止性计算成本，需要数十 petaFLOPS。在这项工作中，我们将紧凑神经表示更接近实际渲染合成内容的实时应用，如游戏和虚拟现实。我们展示了当样本放置在场景表面周围时，每条视线所需的样本数量可以显著减少，而不会影响图像质量。为此，我们提出了一个深度预言网络，通过单次网络评估预测每条视线的射线样本位置。我们展示了在对数离散化和球面扭曲深度值周围使用分类网络对于编码表面位置至关重要，而不是直接估计深度。这些技术的结合产生了 DONeRF，我们的紧凑双网络设计，其中深度预言网络作为第一步，局部采样着色网络用于射线累积。使用 DONeRF，在有可用地面真实深度信息的情况下，我们将推理成本比 NeRF 降低了高达 48 倍。与基于射线行进神经表示的并发加速方法相比，DONeRF 不需要额外的内存用于显式缓存或加速结构，并且可以在单个 GPU 上交互式渲染（每秒 20 帧）。

---

## 7. Depth-supervised NeRF: Fewer Views and Faster Training for Free

**作者**: Kangle Deng and Andrew Liu and Jun-Yan Zhu and Deva Ramanan

**出处**: 2022 IEEE/CVF Conference on Computer Vision and Pattern Recognition (CVPR), 2021, 卷 null, 页 12872-12881

**链接**: [原文链接](https://www.semanticscholar.org/paper/988952b0e737c8ab9b6c1fbd6d54db86e299d270) | [DOI](https://doi.org/10.1109/CVPR52688.2022.01254) | [arXiv](https://arxiv.org/abs/2107.02791)

**摘要**: 神经辐射场（NeRF）的一个常见观察到的失败模式是在给定不足数量的输入视图时拟合错误的几何形状。一个潜在原因是标准体积渲染没有强制执行大多数场景几何由空空间和不透明表面组成的约束。我们通过 DS-NeRF（深度监督神经辐射场）形式化了上述假设，这是一种学习辐射场的损失，利用了容易获得的深度监督。我们利用当前 NeRF 管道需要具有已知相机姿态的图像这一事实，这些姿态通常通过运行运动结构（SFM）来估计。关键的是，SFM 还产生稀疏的 3D 点，可以在训练期间用作"免费"深度监督：我们添加了一个损失来鼓励射线终止深度的分布与给定的 3D 关键点匹配，并纳入深度不确定性。DS-NeRF 可以在给定较少训练视图的情况下渲染更好的图像，同时训练速度快 2-3 倍。此外，我们展示了我们的损失与其他最近提出的 NeRF 方法兼容，证明了深度是一种廉价且易于消化的监督信号。最后，我们发现 DS-NeRF 可以支持其他类型的深度监督，如扫描深度传感器和 RGB-D 重建输出。

---

## 8. FastNeRF: High-Fidelity Neural Rendering at 200FPS

**作者**: Stephan J. Garbin and Marek Kowalski and Matthew Johnson and J. Shotton and Julien P. C. Valentin

**出处**: 2021 IEEE/CVF International Conference on Computer Vision (ICCV), 2021, 卷 null, 页 14326-14335

**链接**: [原文链接](https://www.semanticscholar.org/paper/c0ccfbaf073c91e68ccbc57af2114c72c0d0427d) | [DOI](https://doi.org/10.1109/ICCV48922.2021.01408) | [arXiv](https://arxiv.org/abs/2103.10380)

**摘要**: 最近关于神经辐射场（NeRF）的工作展示了如何使用神经网络编码复杂的 3D 环境，这些环境可以从新视点逼真地渲染。渲染这些图像的计算需求非常高，最近的改进距离实现交互速率还有很长的路要走，即使是在高端硬件上。受移动和混合现实设备场景的启发，我们提出了 FastNeRF，第一个能够在高端消费级 GPU 上以 200Hz 渲染高保真逼真图像的基于 NeRF 的系统。我们方法的核心是一个图形启发的分解，允许（i）在每个空间位置紧凑地缓存深度辐射图，（ii）使用射线方向高效查询该图以估计渲染图像中的像素值。广泛的实验表明，所提出的方法比原始 NeRF 算法快 3000 倍，比现有加速 NeRF 的工作快至少一个数量级，同时保持视觉质量和可扩展性。

---

## 9. Ref-NeRF: Structured View-Dependent Appearance for Neural Radiance Fields

**作者**: Dor Verbin and Peter Hedman and B. Mildenhall and Todd Zickler and J. Barron and Pratul P. Srinivasan

**出处**: 2022 IEEE/CVF Conference on Computer Vision and Pattern Recognition (CVPR), 2021, 卷 null, 页 5481-5490

**链接**: [原文链接](https://www.semanticscholar.org/paper/40c8c8d8a41c16a0e017cc0d059fae9d346795f0) | [DOI](https://doi.org/10.1109/CVPR52688.2022.00541) | [arXiv](https://arxiv.org/abs/2112.03907) | [PMID](https://pubmed.ncbi.nlm.nih.gov/38289850/)

**摘要**: 神经辐射场（NeRF）是一种流行的视图合成技术，它将场景表示为连续体积函数，由多层感知器参数化，提供每个位置的体积密度和视图相关发射辐射度。虽然基于 NeRF 的技术在表示具有平滑变化视图相关外观的精细几何结构方面表现出色，但它们通常无法准确捕获和再现光泽表面的外观。我们通过引入 Ref-NeRF 来解决这个限制，它用反射辐射度的表示替换了 NeRF 的视图相关出射辐射度参数化，并使用一组空间变化的场景属性来结构化这个函数。我们展示了与法向量正则化器一起，我们的模型显著提高了镜面反射的真实感和准确性。此外，我们展示了我们模型的出射辐射度内部表示是可解释的，并且对场景编辑有用。

---

## 10. Dense Depth Priors for Neural Radiance Fields from Sparse Input Views

**作者**: Barbara Roessle and J. Barron and B. Mildenhall and Pratul P. Srinivasan and M. Nießner

**出处**: 2022 IEEE/CVF Conference on Computer Vision and Pattern Recognition (CVPR), 2021, 卷 null, 页 12882-12891

**链接**: [原文链接](https://www.semanticscholar.org/paper/26b1c7ba30879b54c42eef91ee58fa906d7e26cb) | [DOI](https://doi.org/10.1109/CVPR52688.2022.01255) | [arXiv](https://arxiv.org/abs/2112.03288)

**摘要**: 神经辐射场（NeRF）将场景编码为神经表示，能够从新视图进行逼真渲染。然而，从 RGB 图像成功重建需要大量在静态条件下捕获的输入视图——对于房间大小的场景通常需要几百张图像。我们的方法旨在从数量级更少的图像合成整个房间的新视图。为此，我们利用密集深度先验来约束 NeRF 优化。首先，我们利用从用于估计相机姿态的运动结构（SfM）预处理步骤中免费获得的稀疏深度数据。其次，我们使用深度补全将这些稀疏点转换为密集深度图和不确定性估计，用于指导 NeRF 优化。我们的方法能够在具有挑战性的室内场景上实现数据高效的新视图合成，对于整个场景仅使用 18 张图像。

---

## 11. MVSNeRF: Fast Generalizable Radiance Field Reconstruction from Multi-View Stereo

**作者**: Anpei Chen and Zexiang Xu and Fuqiang Zhao and Xiaoshuai Zhang and Fanbo Xiang and Jingyi Yu and Hao Su

**出处**: 2021 IEEE/CVF International Conference on Computer Vision (ICCV), 2021, 卷 null, 页 14104-14113

**链接**: [原文链接](https://www.semanticscholar.org/paper/169971b60749264cbbe2b577dc4d2ad23ca4f46c) | [DOI](https://doi.org/10.1109/ICCV48922.2021.01386) | [arXiv](https://arxiv.org/abs/2103.15595)

**摘要**: 我们提出了 MVSNeRF，一种新颖的神经渲染方法，可以高效地重建用于视图合成的神经辐射场。与先前在密集捕获图像上考虑每场景优化的神经辐射场工作不同，我们提出了一个通用的深度神经网络，可以通过快速网络推理仅从三个附近输入视图重建辐射场。我们的方法利用平面扫描成本体积（广泛用于多视图立体）进行几何感知场景推理，并将其与基于物理的体积渲染相结合用于神经辐射场重建。我们在 DTU 数据集上的真实对象上训练我们的网络，并在三个不同的数据集上测试它以评估其有效性和泛化能力。我们的方法可以跨场景泛化（即使是室内场景，与我们的对象训练场景完全不同），并且仅使用三个输入图像生成逼真的视图合成结果，显著优于并发的一般化辐射场重建工作。此外，如果捕获了密集图像，我们估计的辐射场表示可以轻松微调；这导致比 NeRF 更快的每场景重建，具有更高的渲染质量和显著减少的优化时间。

## 12. D-NeRF: Neural Radiance Fields for Dynamic Scenes

**作者**: Albert Pumarola and Enric Corona and Gerard Pons-Moll and F. Moreno-Noguer

**出处**: 2021 IEEE/CVF Conference on Computer Vision and Pattern Recognition (CVPR), 2020, 卷 null, 页 10313-10322

**链接**: [原文链接](https://www.semanticscholar.org/paper/694bdf6e5906992dad2987a3cc8d1a176de691c9) | [DOI](https://doi.org/10.1109/CVPR46437.2021.01018) | [arXiv](https://arxiv.org/abs/2011.13961)

**摘要**: 将机器学习与几何推理相结合的神经渲染技术已成为从稀疏图像集合合成场景新视图的最有前途的方法之一。其中，神经辐射场（NeRF）[31]脱颖而出，它训练一个深度网络将 5D 输入坐标（表示空间位置和观察方向）映射到体积密度和视图相关发射辐射度。然而，尽管在生成图像上达到了前所未有的照片真实感水平，NeRF 仅适用于静态场景，其中可以从不同图像查询相同的空间位置。在本文中，我们介绍了 D-NeRF，一种将神经辐射场扩展到动态领域的方法，允许从围绕场景移动的单个相机重建和渲染刚性和非刚性运动对象的新图像。为此，我们将时间视为系统的额外输入，并将学习过程分为两个主要阶段：一个将场景编码到规范空间，另一个将此规范表示映射到特定时间的变形场景。两个映射都使用全连接网络同时学习。一旦网络训练完成，D-NeRF 可以渲染新图像，控制相机视图和时间变量，从而控制对象运动。我们在具有刚性、关节和非刚性运动对象的场景上展示了我们方法的有效性。代码、模型权重和动态场景数据集将在[1]提供。

---

## 13. NeRF++: Analyzing and Improving Neural Radiance Fields

**作者**: Kai Zhang and Gernot Riegler and Noah Snavely and V. Koltun

**出处**: ArXiv, 2020, 卷 abs/2010.07492, 页 null

**链接**: [原文链接](https://www.semanticscholar.org/paper/5b0ea2c92ee16fa2f5a3dbc9315cd5c1e4ec1d88) | [arXiv](https://arxiv.org/abs/2010.07492)

**摘要**: 神经辐射场（NeRF）在各种捕获设置下实现了令人印象深刻的视图合成结果，包括有界场景的 360 度捕获和有界及无界场景的前向捕获。NeRF 将表示视图不透明度和视图相关颜色体积的多层感知器（MLPs）拟合到一组训练图像，并基于体积渲染技术采样新视图。在本技术报告中，我们首先评论辐射场及其潜在模糊性，即形状-辐射度模糊性，并分析 NeRF 在避免此类模糊性方面的成功。其次，我们解决了在大型无界 3D 场景中应用 NeRF 到对象 360 度捕获时涉及的参数化问题。我们的方法在这种具有挑战性的场景中提高了视图合成保真度。代码可在此 https URL 获得。

---

## 14. NeuS: Learning Neural Implicit Surfaces by Volume Rendering for Multi-view Reconstruction

**作者**: Peng Wang and Lingjie Liu and Yuan Liu and C. Theobalt and T. Komura and Wenping Wang

**出处**: ArXiv, 2021, 卷 abs/2106.10689, 页 null

**链接**: [原文链接](https://www.semanticscholar.org/paper/cf5647cb2613f5f697729eab567383006dcd4913) | [arXiv](https://arxiv.org/abs/2106.10689)

**摘要**: 我们提出了一种新颖的神经表面重建方法，称为 NeuS，用于从 2D 图像输入高保真地重建对象和场景。现有的神经表面重建方法，如 DVR 和 IDR，需要前景掩码作为监督，容易陷入局部最小值，因此在重建具有严重自遮挡或薄结构的对象时遇到困难。同时，最近的神经新视图合成方法，如 NeRF 及其变体，使用体积渲染来产生神经场景表示，具有优化的鲁棒性，即使对于高度复杂的对象也是如此。然而，从这种学习的隐式表示中提取高质量表面是困难的，因为表示中没有足够的表面约束。在 NeuS 中，我们提出将表面表示为有符号距离函数（SDF）的零水平集，并开发了一种新的体积渲染方法来训练神经 SDF 表示。我们观察到传统的体积渲染方法会导致表面重建的固有几何误差（即偏差），因此提出了一种在一阶近似中无偏差的新公式，从而即使没有掩码监督也能实现更准确的表面重建。在 DTU 数据集和 BlendedMVS 数据集上的实验表明，NeuS 在高质量表面重建方面优于最先进的方法，特别是对于具有复杂结构和自遮挡的对象和场景。

---

## 15. MobileNeRF: Exploiting the Polygon Rasterization Pipeline for Efficient Neural Field Rendering on Mobile Architectures

**作者**: Zhiqin Chen and T. Funkhouser and Peter Hedman and A. Tagliasacchi

**出处**: 2023 IEEE/CVF Conference on Computer Vision and Pattern Recognition (CVPR), 2022, 卷 null, 页 16569-16578

**链接**: [原文链接](https://www.semanticscholar.org/paper/b31c2967451722780e92604532e19cdd3f0f49fb) | [DOI](https://doi.org/10.1109/CVPR52729.2023.01590) | [arXiv](https://arxiv.org/abs/2208.00277)

**摘要**: 神经辐射场（NeRFs）已经展示了从新视图合成 3D 场景图像的惊人能力。然而，它们依赖于基于光线行进的专业体积渲染算法，这与广泛部署的图形硬件能力不匹配。本文介绍了一种基于纹理多边形的新 NeRF 表示，可以使用标准渲染管线高效合成新图像。NeRF 被表示为一组具有表示二进制不透明度和特征向量的纹理的多边形。使用 z 缓冲器对多边形进行传统渲染会产生每个像素都有特征的图像，这些特征由在片段着色器中运行的小型视图相关 MLP 解释以产生最终像素颜色。这种方法使 NeRF 能够使用传统的多边形光栅化管线进行渲染，该管线提供大规模像素级并行性，在包括移动电话在内的各种计算平台上实现交互式帧率。项目页面：https://mobile-nerf.github.io

---

## 16. Fast Dynamic Radiance Fields with Time-Aware Neural Voxels

**作者**: Jiemin Fang and Taoran Yi and Xinggang Wang and Lingxi Xie and Xiaopeng Zhang and Wenyu Liu and M. Nießner and Qi Tian

**出处**: SIGGRAPH Asia 2022 Conference Papers, 2022, 卷 null, 页 null

**链接**: [原文链接](https://www.semanticscholar.org/paper/8f01dff0485488c02b567dac44cdfe9f708cfe70) | [DOI](https://doi.org/10.1145/3550469.3555383) | [arXiv](https://arxiv.org/abs/2205.15285)

**摘要**: 神经辐射场（NeRF）在建模 3D 场景和合成新视图图像方面取得了巨大成功。然而，大多数先前的 NeRF 方法需要花费大量时间来优化单个场景。显式数据结构，例如体素特征，显示出加速训练过程的巨大潜力。然而，体素特征在应用于动态场景时面临两个重大挑战，即建模时间信息和捕获不同尺度的点运动。我们提出了一个辐射场框架，通过使用时间感知体素特征表示场景，命名为 TiNeuVox。引入了一个微小的坐标变形网络来建模粗略运动轨迹，并在辐射网络中进一步增强了时间信息。提出了一种多距离插值方法并应用于体素特征，以建模小运动和大运动。我们的框架显著加速了动态辐射场的优化，同时保持了高渲染质量。在合成和真实场景上都进行了实证评估。我们的 TiNeuVox 仅需 8 分钟训练时间和 8MB 存储成本即可完成训练，同时显示出与先前动态 NeRF 方法相似甚至更好的渲染性能。代码可在https://github.com/hustvl/TiNeuVox获得。

---

## 17. Multiscale Representation for Real-Time Anti-Aliasing Neural Rendering

**作者**: Dongting Hu and Zhenkai Zhang and Tingbo Hou and Tongliang Liu and Huan Fu and Mingming Gong

**出处**: 2023 IEEE/CVF International Conference on Computer Vision (ICCV), 2023, 卷 null, 页 17726-17737

**链接**: [原文链接](https://www.semanticscholar.org/paper/969af2970b58f9d2edc08144fc7493e7c0edb0e5) | [DOI](https://doi.org/10.1109/ICCV51070.2023.01629) | [arXiv](https://arxiv.org/abs/2304.10075)

**摘要**: 神经辐射场（NeRF）中的渲染方案通过将光线投射到场景中来渲染像素是有效的。然而，当训练图像以非均匀尺度捕获时，NeRF 会产生模糊的渲染结果，如果测试图像在远距离视图中拍摄，则会产生混叠伪影。为了解决这个问题，Mip-NeRF 提出了一种多尺度表示作为圆锥截头体来编码尺度信息。然而，这种方法仅适用于离线渲染，因为它依赖于集成位置编码（IPE）来查询多层感知器（MLP）。为了克服这个限制，我们提出了 mip 体素网格（Mip-VoG），一种具有延迟架构的显式多尺度表示，用于实时抗混叠渲染。我们的方法包括用于场景几何的密度 Mip-VoG 和具有小型 MLP 用于视图相关颜色的特征 Mip-VoG。Mip-VoG 使用从光线微分导出的细节层次（LOD）表示场景尺度，并使用四线性插值将查询的 3D 位置映射到其来自两个相邻下采样体素网格的特征和密度。据我们所知，我们的方法是第一个同时提供多尺度训练和实时抗混叠渲染的方法。我们在多尺度数据集上进行了实验，结果表明我们的方法优于最先进的实时渲染基线。

---

## 18. Baking Neural Radiance Fields for Real-Time View Synthesis

**作者**: Peter Hedman and Pratul P. Srinivasan and B. Mildenhall and Christian Reiser and Jonathan T. Barron and Paul E. Debevec

**出处**: IEEE Transactions on Pattern Analysis and Machine Intelligence, 2024, 卷 47, 页 3310-3321

**链接**: [原文链接](https://www.semanticscholar.org/paper/085f76d008a11a07347367e6acefa79fdb891a0d) | [DOI](https://doi.org/10.1109/TPAMI.2024.3381001) | [arXiv](https://arxiv.org/abs/2103.14645) | [PMID](https://pubmed.ncbi.nlm.nih.gov/38526902/)

**摘要**: null

---

## 19. Neural Sparse Voxel Fields

**作者**: Lingjie Liu and Jiatao Gu and Kyaw Zaw Lin and Tat-Seng Chua and C. Theobalt

**出处**: ArXiv, 2020, 卷 abs/2007.11571, 页 null

**链接**: [原文链接](https://www.semanticscholar.org/paper/17d7767a6ea87f4ab24d9cfaa5039160af9cad76) | [arXiv](https://arxiv.org/abs/2007.11571)

**摘要**: 使用经典计算机图形技术实现真实世界场景的照片级真实感自由视点渲染具有挑战性，因为它需要捕获详细外观和几何模型的困难步骤。最近的研究通过学习的场景表示展示了有希望的结果，这些表示隐式编码几何和外观，无需 3D 监督。然而，现有方法在实践中通常显示模糊渲染，这是由于有限的网络容量或难以找到相机光线与场景几何的准确交点。从这些表示合成高分辨率图像通常需要耗时的光学光线行进。在这项工作中，我们介绍了神经稀疏体素场（NSVF），一种用于快速高质量自由视点渲染的新神经场景表示。NSVF 定义了一组体素边界隐式场，组织在稀疏体素八叉树中，以建模每个单元中的局部属性。我们通过可微分光线行进操作从仅一组姿态 RGB 图像逐步学习底层体素结构。通过稀疏体素八叉树结构，可以通过跳过不包含相关场景内容的体素来加速渲染新视图。我们的方法在推理时比最先进的方法（即 NeRF）快 10 倍以上，同时实现更高质量的结果。此外，通过利用显式稀疏体素表示，我们的方法可以轻松应用于场景编辑和场景组合。我们还演示了几个具有挑战性的任务，包括多场景学习、移动人类的自由视点渲染和大规模场景渲染。

---

## 20. PlenOctrees for Real-time Rendering of Neural Radiance Fields

**作者**: Alex Yu and Ruilong Li and Matthew Tancik and Hao Li and Ren Ng and Angjoo Kanazawa

**出处**: 2021 IEEE/CVF International Conference on Computer Vision (ICCV), 2021, 卷 null, 页 5732-5741

**链接**: [原文链接](https://www.semanticscholar.org/paper/5744fcc21b40327f7ad710de7d947d4584c53012) | [DOI](https://doi.org/10.1109/ICCV48922.2021.00570) | [arXiv](https://arxiv.org/abs/2103.14024)

**摘要**: 我们介绍了一种使用 PlenOctrees 实时渲染神经辐射场（NeRFs）的方法，PlenOctrees 是一种基于八叉树的 3D 表示，支持视图相关效果。我们的方法可以以超过 150 FPS 的速度渲染 800×800 图像，比传统 NeRFs 快 3000 倍以上。我们在不牺牲质量的情况下做到这一点，同时保留了 NeRFs 执行具有任意几何形状和视图相关效果的场景的自由视点渲染能力。实时性能通过将 NeRF 预制成 PlenOctree 来实现。为了保留如镜面反射等视图相关效果，我们通过闭式球面基函数分解外观。具体来说，我们展示了可以训练 NeRFs 来预测辐射度的球谐表示，从神经网络输入中移除观察方向。此外，我们展示了 PlenOctrees 可以直接优化以进一步最小化重建损失，这导致与竞争方法相比相等或更好的质量。而且，这个八叉树优化步骤可用于减少训练时间，因为我们不再需要等待 NeRF 训练完全收敛。我们的实时神经渲染方法可能潜在地启用新的应用，如 6 自由度工业和产品可视化，以及下一代 AR/VR 系统。PlenOctrees 也适用于浏览器内渲染；请访问项目页面以获取交互式在线演示，以及视频和代码：https://alexyu.net/plenoctrees。

---

## 21. KiloNeRF: Speeding up Neural Radiance Fields with Thousands of Tiny MLPs

**作者**: Christian Reiser and Songyou Peng and Yiyi Liao and Andreas Geiger

**出处**: 2021 IEEE/CVF International Conference on Computer Vision (ICCV), 2021, 卷 null, 页 14315-14325

**链接**: [原文链接](https://www.semanticscholar.org/paper/c041aaed581616e122e790dd2769337216df3d8d) | [DOI](https://doi.org/10.1109/ICCV48922.2021.01407) | [arXiv](https://arxiv.org/abs/2103.13744)

**摘要**: NeRF 通过将神经辐射场拟合到 RGB 图像，以前所未有的质量合成场景的新视图。然而，NeRF 需要查询深度多层感知器（MLP）数百万次，导致渲染时间缓慢，即使在现代 GPU 上也是如此。在本文中，我们证明了通过使用数千个微小 MLP 而不是单个大型 MLP 可以实现实时渲染。在我们的设置中，每个单独的 MLP 只需要表示场景的部分，因此可以使用更小且评估更快的 MLP。通过将这种分而治之策略与进一步优化相结合，与原始 NeRF 模型相比，渲染加速了三个数量级，而不会产生高存储成本。此外，使用师生蒸馏进行训练，我们展示了这种加速可以在不牺牲视觉质量的情况下实现。

---

## 22. Zip-NeRF: Anti-Aliased Grid-Based Neural Radiance Fields

**作者**: J. Barron and B. Mildenhall and Dor Verbin and Pratul P. Srinivasan and Peter Hedman

**出处**: 2023 IEEE/CVF International Conference on Computer Vision (ICCV), 2023, 卷 null, 页 19640-19648

**链接**: [原文链接](https://www.semanticscholar.org/paper/9eafa581e0268d471b9c61c87db79710dab9274e) | [DOI](https://doi.org/10.1109/ICCV51070.2023.01804) | [arXiv](https://arxiv.org/abs/2304.06706)

**摘要**: 神经辐射场训练可以通过在 NeRF 从空间坐标到颜色和体积密度的学习映射中使用基于网格的表示来加速。然而，这些基于网格的方法缺乏对尺度的显式理解，因此通常引入混叠，通常以锯齿或缺失场景内容的形式出现。抗混叠先前已由 mip-NeRF 360 解决，它沿着圆锥而不是沿着射线的点推理子体积，但这种方法与当前基于网格的技术不原生兼容。我们展示了如何利用渲染和信号处理的思想构建一种技术，将 mip-NeRF 360 和基于网格的模型（如 Instant NGP）结合起来，产生的错误率比任一先前技术低 8% - 77%，并且训练速度比 mip-NeRF 360 快 24 倍。

---

## 23. Direct Voxel Grid Optimization: Super-fast Convergence for Radiance Fields Reconstruction

**作者**: Cheng Sun and Min Sun and Hwann-Tzong Chen

**出处**: 2022 IEEE/CVF Conference on Computer Vision and Pattern Recognition (CVPR), 2021, 卷 null, 页 5449-5459

**链接**: [原文链接](https://www.semanticscholar.org/paper/4f7eb65f8d3c1eeb97e30f7ac68977ff16e1e942) | [DOI](https://doi.org/10.1109/CVPR52688.2022.00538) | [arXiv](https://arxiv.org/abs/2111.11215)

**摘要**: 我们提出了一种超快速收敛的方法，用于从一组以已知姿态捕获场景的图像重建每场景辐射场。这项任务通常应用于新视图合成，最近被神经辐射场（NeRF）以其最先进的质量和灵活性彻底改变。然而，NeRF 及其变体需要数小时到数天的长时间训练单个场景。相比之下，我们的方法实现了与 NeRF 相当的质量，并在单个 GPU 上从零开始快速收敛，时间少于 15 分钟。我们采用了一种表示，包括用于场景几何的密度体素网格和具有浅层网络用于复杂视图相关外观的特征体素网格。使用显式和离散化体积表示建模并不新鲜，但我们提出了两种简单但非平凡的技术，有助于快速收敛速度和高质量输出。首先，我们引入了体素密度的后激活插值，能够在较低网格分辨率下产生锐利表面。其次，直接体素密度优化容易产生次优几何解，因此我们通过施加几个先验来鲁棒化优化过程。最后，在五个向内基准测试上的评估表明，我们的方法匹配（如果不超越）NeRF 的质量，但对于新场景从零开始训练仅需约 15 分钟。代码：https://github.com/sunset1995/DirectVoxGO。

---

## 24. Block-NeRF: Scalable Large Scene Neural View Synthesis

**作者**: Matthew Tancik and Vincent Casser and Xinchen Yan and Sabeek Pradhan and B. Mildenhall and Pratul P. Srinivasan and J. Barron and Henrik Kretzschmar

**出处**: 2022 IEEE/CVF Conference on Computer Vision and Pattern Recognition (CVPR), 2022, 卷 null, 页 8238-8248

**链接**: [原文链接](https://www.semanticscholar.org/paper/d7d1bbade9453f0348fac8a5c60d131528b87fcf) | [DOI](https://doi.org/10.1109/CVPR52688.2022.00807) | [arXiv](https://arxiv.org/abs/2202.05263)

**摘要**: 我们提出了 Block-NeRF，一种神经辐射场的变体，可以表示大规模环境。具体来说，我们证明了当扩展 NeRF 以渲染跨越多个街区的城市规模场景时，将场景分解为单独训练的 NeRF 至关重要。这种分解将渲染时间与场景大小解耦，使渲染能够扩展到任意大的环境，并允许环境的每块更新。我们采用了几个架构更改，使 NeRF 对在不同环境条件下捕获数月的数据具有鲁棒性。我们为每个单独的 NeRF 添加了外观嵌入、学习的姿态细化和可控曝光，并引入了一种在相邻 NeRF 之间对齐外观的程序，以便它们可以无缝组合。我们从 280 万张图像构建了一个 Block-NeRF 网格，创建了迄今为止最大的神经场景表示，能够渲染旧金山的整个街区。

---

## 25. NeXT: Towards High Quality Neural Radiance Fields via Multi-skip Transformer

**作者**: Yunxiao Wang and Yanjie Li and Peidong Liu and Tao Dai and Shutao Xia

**出处**: 2022

**链接**: [原文链接](https://www.semanticscholar.org/paper/06d113db9bf4490b25bf8dfb3c469ffa0debf41a) | [DOI](https://doi.org/10.1007/978-3-031-19824-3_5)

**摘要**: null

---

## 26. Plenoxels: Radiance Fields without Neural Networks

**作者**: Alex Yu and Sara Fridovich-Keil and Matthew Tancik and Qinhong Chen and B. Recht and Angjoo Kanazawa

**出处**: 2022 IEEE/CVF Conference on Computer Vision and Pattern Recognition (CVPR), 2021, 卷 null, 页 5491-5500

**链接**: [原文链接](https://www.semanticscholar.org/paper/e91f73aaef155391b5b07e6612f5346dea888f64) | [DOI](https://doi.org/10.1109/CVPR52688.2022.00542) | [arXiv](https://arxiv.org/abs/2112.05131)

**摘要**: 我们介绍了 Plenoxels（全光体素），一个用于照片级真实感视图合成的系统。Plenoxels 将场景表示为具有球谐函数的稀疏 3D 网格。这种表示可以通过梯度方法和正则化从校准图像优化，无需任何神经组件。在标准基准任务上，Plenoxels 的优化速度比神经辐射场快两个数量级，且视觉质量没有损失。有关视频和代码，请参见https://alexyu.net/plenoxels。

---

## 27. Mip-NeRF 360: Unbounded Anti-Aliased Neural Radiance Fields

**作者**: J. Barron and B. Mildenhall and Dor Verbin and Pratul P. Srinivasan and Peter Hedman

**出处**: 2022 IEEE/CVF Conference on Computer Vision and Pattern Recognition (CVPR), 2021, 卷 null, 页 5460-5469

**链接**: [原文链接](https://www.semanticscholar.org/paper/ec90ffa017a2cc6a51342509ce42b81b478aefb3) | [DOI](https://doi.org/10.1109/CVPR52688.2022.00539) | [arXiv](https://arxiv.org/abs/2111.12077)

**摘要**: 尽管神经辐射场（NeRF）在对象和小型有界空间区域上展示了令人印象深刻的视图合成结果，但它们在"无界"场景上遇到困难，其中相机可能指向任何方向，内容可能存在于任何距离。在这种设置下，现有的类似 NeRF 的模型通常产生模糊或低分辨率渲染（由于附近和远处对象的细节和尺度不平衡），训练速度慢，并且可能由于从少量图像重建大场景任务的固有模糊性而表现出伪影。我们提出了 mip-NeRF（一种解决采样和混叠的 NeRF 变体）的扩展，它使用非线性场景参数化、在线蒸馏和一种新颖的基于失真的正则化器来克服无界场景带来的挑战。我们的模型，我们称之为"mip-NeRF 360"，因为我们针对相机围绕一个点旋转 360 度的场景，与 mip-NeRF 相比，均方误差减少了 57%，并且能够为高度复杂的无界真实世界场景产生逼真的合成视图和详细的深度图。

---

## 28. Local Light Field Fusion: Practical View Synthesis with Prescriptive Sampling Guidelines

**作者**: B. Mildenhall

**出处**: 2019

**链接**: [原文链接](https://www.semanticscholar.org/paper/af39e137818ef8304ccea2ada546700de1dd2f8c)

**摘要**: null

---

## 29. pixelNeRF: Neural Radiance Fields from One or Few Images

**作者**: Alex Yu and Vickie Ye and Matthew Tancik and Angjoo Kanazawa

**出处**: 2021 IEEE/CVF Conference on Computer Vision and Pattern Recognition (CVPR), 2020, 卷 null, 页 4576-4585

**链接**: [原文链接](https://www.semanticscholar.org/paper/4365f51fc270c55005adb794002685078a6fca1d) | [DOI](https://doi.org/10.1109/CVPR46437.2021.00455) | [arXiv](https://arxiv.org/abs/2012.02190)

**摘要**: 我们提出了 pixelNeRF，一个学习框架，预测基于一个或几个输入图像的条件化连续神经场景表示。构建神经辐射场[27]的现有方法涉及独立优化每个场景的表示，需要许多校准视图和大量计算时间。我们通过引入一种以全卷积方式将 NeRF 条件化于图像输入的架构，朝着解决这些缺点迈出了一步。这允许网络在多个场景上进行训练以学习场景先验，使其能够从稀疏视图集（少至一个）以前馈方式执行新视图合成。利用 NeRF 的体积渲染方法，我们的模型可以直接从图像训练，无需显式 3D 监督。我们在 ShapeNet 基准上进行了广泛实验，用于单图像新视图合成任务，包括保留对象以及整个未见类别。我们通过在多对象 ShapeNet 场景和 DTU 数据集的真实场景上演示 pixelNeRF，进一步展示了其灵活性。在所有情况下，pixelNeRF 在新视图合成和单图像 3D 重建方面都优于当前最先进的基线。有关视频和代码，请访问项目网站：https://alexyu.net/pixelnerf。

---

## 30. BARF: Bundle-Adjusting Neural Radiance Fields

**作者**: Chen-Hsuan Lin and Wei-Chiu Ma and A. Torralba and S. Lucey

**出处**: 2021 IEEE/CVF International Conference on Computer Vision (ICCV), 2021, 卷 null, 页 5721-5731

**链接**: [原文链接](https://www.semanticscholar.org/paper/33cc02f23c97a3daa835953b9d2784d0e1abf16e) | [DOI](https://doi.org/10.1109/ICCV48922.2021.00569) | [arXiv](https://arxiv.org/abs/2104.06405)

**摘要**: 神经辐射场（NeRF）[31]最近在计算机视觉社区中因其合成真实世界场景照片级真实感新视图的能力而获得了激增的兴趣。然而，NeRF 的一个限制是其需要准确的相机姿态来学习场景表示。在本文中，我们提出了束调整神经辐射场（BARF），用于从不完美（甚至未知）相机姿态训练 NeRF——学习神经 3D 表示和配准相机帧的联合问题。我们建立了与经典图像对齐的理论联系，并展示了从粗到精的配准也适用于 NeRF。此外，我们展示了在 NeRF 中天真地应用位置编码对基于合成的目标的配准有负面影响。在合成和真实世界数据上的实验表明，BARF 可以有效地优化神经场景表示，同时解决大的相机姿态错位。这使得能够从未知相机姿态的视频序列进行视图合成和定位，为视觉定位系统（例如 SLAM）和密集 3D 映射和重建的潜在应用开辟了新途径。

---

## 31. StylizedNeRF: Consistent 3D Scene Stylization as Stylized NeRF via 2D-3D Mutual Learning

**作者**: Yihua Huang and Yue He and Yu-Jie Yuan and Yu-Kun Lai and Lin Gao

**出处**: 2022 IEEE/CVF Conference on Computer Vision and Pattern Recognition (CVPR), 2022, 卷 null, 页 18321-18331

**链接**: [原文链接](https://www.semanticscholar.org/paper/6d987103091666709cacfb825278763e49df60cc) | [DOI](https://doi.org/10.1109/CVPR52688.2022.01780) | [arXiv](https://arxiv.org/abs/2205.12183)

**摘要**: 3D 场景风格化旨在从任意新视图生成遵循给定风格示例集的场景风格化图像，同时确保从不同视图渲染时的一致性。直接将图像或视频风格化方法应用于 3D 场景无法实现这种一致性。得益于最近提出的神经辐射场（NeRF），我们能够以一致的方式表示 3D 场景。一致的 3D 场景风格化可以通过风格化相应的 NeRF 来有效实现。然而，风格示例（2D 图像）和 NeRF（隐式体积表示）之间存在显著的领域差距。为了解决这个问题，我们提出了一个新颖的 3D 场景风格化互学习框架，结合 2D 图像风格化网络和 NeRF，将 2D 风格化网络的风格化能力与 NeRF 的 3D 一致性融合。我们首先预训练要风格化的 3D 场景的标准 NeRF，并用风格网络替换其颜色预测模块以获得风格化 NeRF。随后，通过引入的一致性损失，将空间一致性的先验知识从 NeRF 蒸馏到 2D 风格化网络。我们还引入了模仿损失来监督 NeRF 风格模块的互学习，并微调 2D 风格化解码器。为了进一步使我们的模型处理 2D 风格化结果的模糊性，我们引入了服从以风格为条件的概率分布的可学习潜在代码。它们作为条件输入附加到训练样本上，以更好地学习我们新颖风格化 NeRF 中的风格模块。实验结果表明，我们的方法在视觉质量和长距离一致性方面都优于现有方法。

---

## 32. NeRF in the Wild: Neural Radiance Fields for Unconstrained Photo Collections

**作者**: Ricardo Martin-Brualla and Noha Radwan and Mehdi S. M. Sajjadi and J. Barron and Alexey Dosovitskiy and Daniel Duckworth

**出处**: 2021 IEEE/CVF Conference on Computer Vision and Pattern Recognition (CVPR), 2020, 卷 null, 页 7206-7215

**链接**: [原文链接](https://www.semanticscholar.org/paper/691eddbfaebbc71f6a12d3c99d5c155042459434) | [DOI](https://doi.org/10.1109/CVPR46437.2021.00713) | [arXiv](https://arxiv.org/abs/2008.02268)

**摘要**: 我们提出了一种基于学习的方法，仅使用非结构化野外照片集合合成复杂场景的新视图。我们基于神经辐射场（NeRF）构建，它使用多层感知器的权重将场景的密度和颜色建模为 3D 坐标的函数。虽然 NeRF 在受控设置下捕获的静态主体图像上效果良好，但它无法建模非受控图像中许多普遍存在的真实世界现象，如可变照明或瞬态遮挡物。我们引入了一系列对 NeRF 的扩展来解决这些问题，从而能够从互联网获取的非结构化图像集合进行准确重建。我们将我们的系统（称为 NeRF-W）应用于著名地标的互联网照片集合，并展示了时间一致的新视图渲染，比先前最先进的技术更接近照片真实感。

---

## 33. Alma Mater Studiorum Università di Bologna Archivio istituzionale della ricerca

**出处**: null

**链接**: [原文链接](https://www.semanticscholar.org/paper/a18a15ce73d2999b99f6973a1af78959dc0f04cf)

**摘要**: null

---

## 34. IBRNet: Learning Multi-View Image-Based Rendering

**作者**: Qianqian Wang and Zhicheng Wang and Kyle Genova and Pratul P. Srinivasan and Howard Zhou and J. Barron and Ricardo Martin-Brualla and Noah Snavely and T. Funkhouser

**出处**: 2021 IEEE/CVF Conference on Computer Vision and Pattern Recognition (CVPR), 2021, 卷 null, 页 4688-4697

**链接**: [原文链接](https://www.semanticscholar.org/paper/7cbc3dd0280b8c4551ac934af42dc227d43754f7) | [DOI](https://doi.org/10.1109/CVPR46437.2021.00466) | [arXiv](https://arxiv.org/abs/2102.13090)

**摘要**: 我们提出了一种方法，通过插值稀疏的附近视图集来合成复杂场景的新视图。我们方法的核心是一个网络架构，包括一个多层感知器和一个射线变换器，该变换器在连续的 5D 位置（3D 空间位置和 2D 观察方向）估计辐射和体积密度，从多个源视图动态提取外观信息。通过在渲染时利用源视图，我们的方法回归到经典的基于图像的渲染（IBR）工作，并允许我们渲染高分辨率图像。与优化每个场景渲染函数的神经场景表示工作不同，我们学习一个通用的视图插值函数，可以泛化到新场景。我们使用经典体积渲染来渲染图像，这是完全可微分的，允许我们仅使用多视图姿态图像作为监督进行训练。实验表明，我们的方法优于最近也寻求泛化到新场景的新视图合成方法。此外，如果在每个场景上进行微调，我们的方法与最先进的单场景神经渲染方法具有竞争力。

---

## 35. NeRF

**作者**: B. Mildenhall and Pratul P. Srinivasan and Matthew Tancik and J. Barron and R. Ramamoorthi and Ren Ng

**出处**: Communications of the ACM, 2020, 卷 65, 页 99 - 106

**链接**: [原文链接](https://www.semanticscholar.org/paper/428b663772dba998f5dc6a24488fff1858a0899f) | [DOI](https://doi.org/10.1145/3503250) | [arXiv](https://arxiv.org/abs/2003.08934)

**摘要**: 我们提出了一种方法，通过使用稀疏输入视图集优化底层连续体积场景函数，在合成复杂场景的新视图方面实现了最先进的结果。我们的算法使用全连接（非卷积）深度网络表示场景，其输入是单个连续 5D 坐标（空间位置（x, y, z）和观察方向（θ, φ）），其输出是该空间位置的体积密度和视图相关发射辐射。我们通过沿相机射线查询 5D 坐标来合成视图，并使用经典体积渲染技术将输出颜色和密度投影到图像中。由于体积渲染本质上是可微分的，优化我们表示所需的唯一输入是一组具有已知相机姿态的图像。我们描述了如何有效优化神经辐射场以渲染具有复杂几何和外观的场景的照片级真实感新视图，并展示了优于先前神经渲染和视图合成工作的结果。

---

## 36. TensoRF: Tensorial Radiance Fields

**作者**: Anpei Chen and Zexiang Xu and Andreas Geiger and Jingyi Yu and Hao Su

**出处**: ArXiv, 2022, 卷 abs/2203.09517, 页 null

**链接**: [原文链接](https://www.semanticscholar.org/paper/b4a9437302411abde0c9de784a14bfc6a5d950cf) | [DOI](https://doi.org/10.48550/arXiv.2203.09517) | [arXiv](https://arxiv.org/abs/2203.09517)

**摘要**: 我们提出了 TensoRF，一种建模和重建辐射场的新方法。与纯粹使用 MLP 的 NeRF 不同，我们将场景的辐射场建模为 4D 张量，表示具有每体素多通道特征的 3D 体素网格。我们的核心思想是将 4D 场景张量分解为多个紧凑的低秩张量分量。我们证明了在我们的框架中应用传统的 CP 分解——将张量分解为具有紧凑向量的秩一分量——相对于原始 NeRF 带来了改进。为了进一步提高性能，我们引入了一种新颖的向量-矩阵（VM）分解，它放宽了张量两个模式的低秩约束，并将张量分解为紧凑的向量和矩阵因子。除了卓越的渲染质量外，我们的 CP 和 VM 分解模型与直接优化每体素特征的先前和并发工作相比，内存占用显著降低。实验上，我们证明了具有 CP 分解的 TensoRF 实现了快速重建（<30 分钟），与 NeRF 相比具有更好的渲染质量甚至更小的模型大小（<4 MB）。此外，具有 VM 分解的 TensoRF 进一步提高了渲染质量，并优于先前的最先进方法，同时减少了重建时间（<10 分钟）并保持了紧凑的模型大小（<75 MB）。

---

## 37. Point-NeRF: Point-based Neural Radiance Fields

**作者**: Qiangeng Xu and Zexiang Xu and J. Philip and Sai Bi and Zhixin Shu and Kalyan Sunkavalli and U. Neumann

**出处**: 2022 IEEE/CVF Conference on Computer Vision and Pattern Recognition (CVPR), 2022, 卷 null, 页 5428-5438

**链接**: [原文链接](https://www.semanticscholar.org/paper/055e87ce418a83d6fd555b73aea0d838385dfa85) | [DOI](https://doi.org/10.1109/CVPR52688.2022.00536) | [arXiv](https://arxiv.org/abs/2201.08845)

**摘要**: 像 NeRF [34]这样的体积神经渲染方法生成高质量视图合成结果，但针对每个场景进行优化，导致重建时间过长。另一方面，深度多视图立体方法可以通过直接网络推断快速重建场景几何。Point-NeRF 通过使用神经 3D 点云（具有相关的神经特征）来建模辐射场，结合了这两种方法的优势。Point-NeRF 可以通过在基于射线行进的渲染管道中聚合场景表面附近的神经点特征来高效渲染。此外，Point-NeRF 可以通过预训练深度网络的直接推断进行初始化以产生神经点云；这个点云可以进行微调，以超越 NeRF 的视觉质量，同时训练时间快 30 倍。Point-NeRF 可以与其他 3D 重建方法结合，并通过新颖的修剪和增长机制处理此类方法中的错误和异常值。

---

## 38. Instant neural graphics primitives with a multiresolution hash encoding

**作者**: T. Müller and Alex Evans and Christoph Schied and A. Keller

**出处**: ACM Transactions on Graphics (TOG), 2022, 卷 41, 页 1 - 15

**链接**: [原文链接](https://www.semanticscholar.org/paper/60e69982ef2920596c6f31d6fd3ca5e9591f3db6) | [DOI](https://doi.org/10.1145/3528223.3530127) | [arXiv](https://arxiv.org/abs/2201.05989)

**摘要**: 由全连接神经网络参数化的神经图形基元在训练和评估时可能成本高昂。我们通过一种多功能的新输入编码来减少这种成本，该编码允许使用较小的网络而不牺牲质量，从而显著减少浮点运算和内存访问操作的数量：一个小型神经网络通过一个多分辨率哈希表进行增强，该表包含可通过随机梯度下降优化的可训练特征向量。多分辨率结构允许网络消除哈希冲突，形成一个简单的架构，在现代 GPU 上可以轻松并行化。我们通过使用完全融合的 CUDA 内核实现整个系统来利用这种并行性，重点是最小化浪费的带宽和计算操作。我们实现了几个数量级的组合加速，能够在几秒钟内训练高质量的神经图形基元，并在 1920×1080 分辨率下在几十毫秒内进行渲染。

---

## 39. HR-NeRF: advancing realism and accuracy in highlight scene representation

**作者**: Shufan Dai and Shanqin Wang

**出处**: Frontiers in Neurorobotics, 2025, 卷 19, 页 null

**链接**: [原文链接](https://www.semanticscholar.org/paper/8dbb5416a83b0ac7941dc838d2ccc7e0bd8c3d6d) | [DOI](https://doi.org/10.3389/fnbot.2025.1558948) | [PMID](https://pubmed.ncbi.nlm.nih.gov/40308477/)

**摘要**: NeRF 及其变体在新视图合成方面表现出色，但在具有镜面高光的场景中遇到困难。为了解决这个限制，我们引入了高光恢复网络（HRNet），一种增强 NeRF 捕捉镜面场景能力的新架构。HRNet 集成了 Swish 激活函数、仿射变换、多层感知器（MLP）和残差块，这些共同实现了平滑的非线性变换、自适应特征缩放和分层特征提取。残差连接有助于缓解梯度消失问题，确保稳定的训练。尽管 HRNet 的组件简单，但在恢复镜面高光方面取得了令人印象深刻的结果。此外，密度体素网格增强了模型效率。在四个向内基准上的评估表明，我们的方法优于 NeRF 及其变体，在每个数据集上实现了 3-5 dB 的 PSNR 改进，同时准确捕捉场景细节。此外，我们的方法有效保留图像细节，无需位置编码，在 NVIDIA RTX 3090 Ti GPU 上渲染单个场景约需 18 分钟。

---

## 40. Neural Scene Flow Fields for Space-Time View Synthesis of Dynamic Scenes

**作者**: Zhengqi Li and Simon Niklaus and Noah Snavely and Oliver Wang

**出处**: 2021 IEEE/CVF Conference on Computer Vision and Pattern Recognition (CVPR), 2020, 卷 null, 页 6494-6504

**链接**: [原文链接](https://www.semanticscholar.org/paper/13034a395d5c6728c9b11e777828d9998018cbf6) | [DOI](https://doi.org/10.1109/CVPR46437.2021.00643) | [arXiv](https://arxiv.org/abs/2011.13084)

**摘要**: 我们提出了一种方法，用于执行动态场景的新视图和时间合成，仅需要具有已知相机姿态的单目视频作为输入。为此，我们引入了神经场景流场，一种将动态场景建模为外观、几何和 3D 场景运动的时间变体连续函数的新表示。我们的表示通过神经网络优化以拟合观察到的输入视图。我们展示了我们的表示可以用于各种野外场景，包括薄结构、视图相关效应和复杂程度的运动。我们进行了多项实验，证明我们的方法显著优于最近的单目视图合成方法，并展示了在各种真实世界视频上的时空视图合成的定性结果。

---

## 41. RegNeRF: Regularizing Neural Radiance Fields for View Synthesis from Sparse Inputs

**作者**: Michael Niemeyer and J. Barron and B. Mildenhall and Mehdi S. M. Sajjadi and Andreas Geiger and Noha Radwan

**出处**: 2022 IEEE/CVF Conference on Computer Vision and Pattern Recognition (CVPR), 2021, 卷 null, 页 5470-5480

**链接**: [原文链接](https://www.semanticscholar.org/paper/7163d171d4671ab8c0fd342e5280db532700999a) | [DOI](https://doi.org/10.1109/CVPR52688.2022.00540) | [arXiv](https://arxiv.org/abs/2112.00724)

**摘要**: 神经辐射场（NeRF）因其简单性和最先进的性能而成为新视图合成任务的有力表示。虽然 NeRF 在有许多输入视图可用时可以产生未见视点的照片级真实感渲染，但当这个数量减少时，其性能显著下降。我们观察到稀疏输入场景中的大多数伪影是由估计场景几何中的错误以及训练开始时的发散行为引起的。我们通过正则化从未观察视点渲染的补丁的几何和外观，并在训练期间退火射线采样空间来解决这个问题。我们还使用归一化流模型来正则化未观察视点的颜色。我们的模型不仅优于其他优化单个场景的方法，而且在许多情况下也优于在大规模多视图数据集上广泛预训练的条件模型。

---
