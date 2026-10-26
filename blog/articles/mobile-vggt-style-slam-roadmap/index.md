---
title: "Awesome Mobile VGGT-style SLAM"
date: 2026-10-27
categories: [life]
tags: [SLAM, VGGT, Mobile, Visual Odometry, Reading List]
excerpt: "围绕移动端、位姿估计与流式三维重建整理的 VGGT-style SLAM 阅读清单，按重要程度列出论文与站内笔记。"
draft: false
---

# Awesome Mobile VGGT-style SLAM

这份清单围绕三个相连的问题整理资料：**从视频流持续估计位姿、在有限内存中维护地图、让模型在移动设备上运行**。范围包括 VGGT 类几何模型、学习式视觉里程计、局部与全局优化，以及模型压缩。排序表示与这一主题的相关程度，不区分是否已有站内笔记。

**S｜核心必读**：建立问题定义和系统基线。**A｜系统设计**：比较流式状态、地图与后端。**B｜专项深入**：按记忆或效率瓶颈阅读。**C｜基础参考**：需要时查阅。

## S｜核心必读

1. **[DROID-SLAM: Deep Visual SLAM for Monocular, Stereo, and RGB-D Cameras](https://arxiv.org/abs/2108.10869)** · 学习式对应更新与 Dense Bundle Adjustment 交替修正位姿和深度，是理解“预测如何进入几何优化”的起点。
2. **[Deep Patch Visual Odometry（DPVO）](https://arxiv.org/abs/2208.04726)** · 用稀疏 patch 图和可微 BA 做局部位姿估计；重点看稀疏化如何改变精度、速度和内存需求。
3. **[Visual Geometry Grounded Transformer（VGGT）](https://arxiv.org/abs/2503.11651)** · 多视图相机、深度、点图和轨迹的联合预测；重点看交替注意力、相机头、坐标系与各输出之间的关系。[站内笔记](../vggt/index.md)
4. **[Revisiting Local Context for Long-Horizon Streaming 3D Reconstruction（ABot-Recon）](https://arxiv.org/abs/2608.27529)** · 固定 12 帧局部上下文，预测相邻相对位姿和当前相机系点图；重点看旋转精化与多步位姿组合。
5. **[LingBot-Map: Geometric Context Transformer for Streaming 3D Reconstruction](https://arxiv.org/abs/2604.14141)** · 用锚上下文、位姿参考窗口和轨迹记忆组织长期视频信息；适合研究历史状态如何分层保存。[站内笔记](../lingbot-map/index.md)
6. **[StreamRig: Exploiting Intra-Rig Geometry for Streaming Multi-Camera Odometry](https://arxiv.org/abs/2609.40244)** · 冻结多视图前端，压缩特征，再用因果模块估计 rig 位姿；重点看相对位姿监督、KV 缓存与换锚。该方法以已标定多相机 rig 为输入。[站内笔记](../streamrig/index.md)
7. **[Deep Patch Visual SLAM（DPV-SLAM）](https://arxiv.org/abs/2408.01654)** · DPVO 的 SLAM 扩展；关注视觉里程计之外的回环、重定位和地图修正。

## A｜流式系统与 SLAM 后端

8. **[Continuous 3D Perception Model with Persistent State（CUT3R）](https://arxiv.org/abs/2501.12387)** · 循环更新的隐状态和公共坐标系点图；可与固定局部窗口、显式轨迹记忆进行对照。[站内解读](../cut3r/index.md)
9. **[Streaming 4D Visual Geometry Transformer（StreamVGGT）](https://arxiv.org/abs/2507.11539)** · 将 VGGT 类双向处理改成因果推理，并使用缓存与蒸馏；重点关注缓存成本和逐帧输出形式。[站内解读](../streamvggt/index.md)
10. **[STream3R: Scalable Sequential 3D Reconstruction with Causal Transformer](https://arxiv.org/abs/2508.10893)** · Decoder-only 流式重建、KV 缓存和滑动窗口；提供另一种顺序处理结构。[站内解读](../stream3r/index.md)
11. **[MASt3R-SLAM: Real-Time Dense SLAM with 3D Reconstruction Priors](https://arxiv.org/abs/2412.12392)** · Pointmap 匹配与局部、全局几何优化结合；观察学习到的三维先验如何进入完整 SLAM 系统。
12. **[VGGT-SLAM: Dense RGB SLAM Optimized on the SL(4) Manifold](https://arxiv.org/abs/2505.12549)** · 将 VGGT 子图增量对齐并加入回环；重点看未知内参下的重建歧义和子图变换。[站内解读](../vggt-slam/index.md)
13. **[VGGT-SLAM 2.0: Real time Dense Feed-forward Scene Reconstruction](https://arxiv.org/abs/2601.19887)** · 更新子图因子图与回环验证；适合与 VGGT-SLAM 初版并读，理解长序列位姿一致性的改进。
14. **[VGGT-Long: Chunk it, Loop it, Align it](https://arxiv.org/abs/2507.16443)** · 重叠分块、置信度加权对齐、回环和全局 Sim(3) 优化；提供长序列组织方法。[站内笔记](../vggt-long/index.md)
15. **[ICE-BA: Incremental, Consistent and Efficient Bundle Adjustment for Visual-Inertial SLAM](https://openaccess.thecvf.com/content_cvpr_2018/html/Liu_ICE-BA_Incremental_Consistent_CVPR_2018_paper.html)** · 局部与全局 BA 的调度、增量求解和相对边缘化；关注旧状态移出窗口后约束如何保留。
16. **[VINS-Mono: A Robust and Versatile Monocular Visual-Inertial State Estimator](https://arxiv.org/abs/1708.03852)** · 手机 IMU 参与时的初始化、预积分、滑窗优化、尺度与重定位。[IMU 预积分笔记](../imu-preintegration/index.md) · [VINS 等方法比较](../vins-lio-sam-preintegration/index.md)
17. **[Global Structure-from-Motion Meets Feedforward Reconstruction（GLUEMAP）](https://arxiv.org/abs/2605.26103)** · 局部前馈几何、运动平均和增广 BA 的结合；适合补充全局一致性的视角。[站内笔记](../gluemap/index.md)
18. **[SLAM 中的回环鲁棒性](../robust-loop/index.md)** · 站内专题笔记；梳理回环候选、几何验证、错误约束抑制和历史重评估。

## B｜有限内存与移动端效率

19. **[FastVGGT: Fast Visual Geometry Transformer](https://arxiv.org/abs/2509.02560)** · 训练自由的 token 合并；关注全局注意力的计算冗余及几何精度变化。
20. **[Lite3R: A Model-Agnostic Framework for Efficient Feed-Forward 3D Reconstruction](https://arxiv.org/abs/2605.11354)** · 稀疏线性注意力、部分蒸馏和 FP8 感知训练；关注注意力成本与低精度几何稳定性。
21. **[QVGGT: Post-Training Quantized Visual Geometry Grounded Transformer](https://arxiv.org/abs/2605.31124)** · 针对 VGGT 的混合精度量化；关注特殊 token、相机预测和不同几何输出的量化敏感度。
22. **[VGGT-Ω](https://arxiv.org/abs/2605.15195)** · 寄存器注意力与轻量预测头；可用于理解跨帧信息汇总和全局注意力成本。[站内笔记](../vggt-omega/index.md)
23. **[MUSt3R: Multi-view Network for Stereo 3D Reconstruction](https://arxiv.org/abs/2503.01661)** · 共享解码器、逐层记忆和公共坐标系点图；提供另一种顺序重建的特征复用方式。[站内笔记](../must3r/index.md)
24. **[π³: Permutation-Equivariant Visual Geometry Learning](https://arxiv.org/abs/2507.13347)** · 局部点图与相对位姿监督；重点看参考系选择如何影响流式预测目标。[站内笔记](../pi3/index.md)
25. **[Point3R: Streaming 3D Reconstruction with Explicit Spatial Pointer Memory](https://arxiv.org/abs/2507.02863)** · 显式空间指针记忆；关注长期重访时历史几何如何被读取。[站内解读](../point3r/index.md)
26. **[SLAM3R: Real-Time Dense Scene Reconstruction from Monocular RGB Videos](https://arxiv.org/abs/2412.09401)** · 局部 pointmap 与全局配准；提供窗口式稠密重建的参照。
27. **[Depth Anything 3: Recovering the Visual Space from Any Views](https://arxiv.org/abs/2511.10647)** · 深度和射线的统一几何表示；可比较不同预测头对相机估计的作用。[站内笔记](../depth-anything-3/index.md)
28. **[LightGlue: Local Feature Matching at Light Speed](https://arxiv.org/abs/2306.13643)** 与 **[ALIKED](https://arxiv.org/abs/2304.03608)** · 较轻量的局部特征与匹配模块，可用于回环验证和重定位。[LightGlue 笔记](../lightglue/index.md) · [ALIKED 笔记](../aliked/index.md)
29. **[Cameras as Relative Positional Encoding](https://arxiv.org/abs/2507.10496)** · 提出 PRoPE，将相机内外参组成的完整视锥关系编码到多视图注意力中；适合研究相机几何如何影响跨视图 token 交互。
30. **[RayRoPE: Projective Ray Positional Encoding for Multi-view Attention](https://arxiv.org/abs/2601.15275)** · 用射线上预测的三维点构造几何自适应位置编码，并以查询相机坐标实现 SE(3) 不变注意力；关注深度不确定性如何进入编码。

## C｜基础参考

31. **[SuperPoint](https://arxiv.org/abs/1712.07629)**、**[SuperGlue](https://arxiv.org/abs/1911.11763)**、**[Attention Is All You Need](https://arxiv.org/abs/1706.03762)** · 关键点、匹配与注意力机制的基础材料。[SuperPoint 笔记](../superpoint/index.md) · [SuperGlue 笔记](../superglue/index.md) · [Transformer 笔记](../attention-is-all-you-need/index.md)
32. **[InsightAT：Simple Automated SfM](../insightat/index.md)** · 站内项目文章；可回看特征、增量注册和 BA 在完整重建流程中的组织方式。

## 流式重建与端到端 SLAM 解读队列

以下顺序按它们对“有限历史如何形成长期稳定几何”这一综述主线的帮助排序，不代表论文质量排名。已完成的单篇解读不重复写：VGGT、VGGT-Long、VGGT-Ω、ABot-Recon、LingBot-Map、StreamRig、DPVO、DROID-SLAM、DPV-SLAM、GLUEMAP、MUSt3R、π³、Depth Anything 3、StreamVGGT、STream3R、CUT3R、LONG3R、VGGT-SLAM、Spann3R、Point3R 和 LongStream 均已有站内文章。

### 第一优先级：流式状态与长序列重建

1. **[WinT3R: Window-Based Streaming Reconstruction with Camera Token Pool](https://arxiv.org/abs/2509.05296)** · 以滑动窗口交换几何信息，并用全局相机 token 池估计位姿；可对照全历史缓存和显式空间记忆。
2. **[HorizonStream: Long-Horizon Attention for Streaming 3D Reconstruction](https://arxiv.org/abs/2605.23889)** · 以不同时间尺度传播几何证据，面向超长历史和有界状态。
3. **[TTT3R: 3D Reconstruction as Test-Time Training](https://arxiv.org/abs/2509.26645)** · 从在线学习角度调节循环状态更新，研究历史记忆与新观测的平衡。
4. **[InfiniteVGGT: Visual Geometry Grounded Transformer for Endless Streams](https://arxiv.org/abs/2601.02281)** · 用有界自适应 KV cache 处理长时流，并提出约万帧 Long3D 评测。
5. **[LongStream: Long-Sequence Streaming Autoregressive Visual Geometry](https://arxiv.org/abs/2602.13172)** · 用关键帧相对位姿、尺度解耦和缓存刷新处理公里级序列。[站内解读](../longstream/index.md)

### 第二优先级：流式几何如何接入 SLAM 系统

6. **[MASt3R-SLAM: Real-Time Dense SLAM with 3D Reconstruction Priors](https://arxiv.org/abs/2412.12392)** · 覆盖跟踪、稠密局部融合、回环和全局优化，是学习式三维先验进入完整 SLAM 系统的代表。
7. **[SLAM3R: Real-Time Dense Scene Reconstruction from Monocular RGB Videos](https://arxiv.org/abs/2412.09401)** · 通过重叠窗口内重建与跨窗口配准形成全局场景。
8. **[VGGT-SLAM 2.0: Real-time Dense Feed-forward Scene Reconstruction](https://arxiv.org/abs/2601.19887)** · 跟进子图因子图、回环验证和在线机器人运行。
9. **[VGGT-SLAM++](https://arxiv.org/abs/2604.06830)** · 重点比较高频局部 BA 与空间校正后端。
10. **[Multi-Agent Monocular Dense SLAM With 3D Reconstruction Priors](https://arxiv.org/abs/2511.19031)** · 将重建先验 SLAM 扩展到多智能体协同建图，作为系统边界扩展。
11. **[F²-SLAM: Turning Feed-Forward Geometry into Persistent Factors for SLAM](https://arxiv.org/abs/2610.05207)** · 将前馈几何转成可优化的持久稠密因子，适合作为“学习先验如何进入后端”的近期系统代表。
12. **[ICE-BA: Incremental, Consistent and Efficient Bundle Adjustment for Visual-Inertial SLAM](https://openaccess.thecvf.com/content_cvpr_2018/html/Liu_ICE-BA_Incremental_Consistent_CVPR_2018_paper.html)** · 提供滑窗之外保留全局约束的经典优化背景。

### 第三优先级：缓存效率、尺度校正与动态场景

12. **[IncVGGT: Incremental VGGT for Memory-Bounded Long-Range 3D Reconstruction](https://proceedings.iclr.cc/paper_files/paper/2026/hash/0a4096f09ab230082df548f901d4f79e-Abstract-Conference.html)** · 输入侧重叠帧融合与历史侧缓存裁剪。
13. **[OVGGT: O(1) Constant-Cost Streaming Visual Geometry Transformer](https://arxiv.org/abs/2603.05959)** · 探索固定推理成本的流式视觉几何状态。
14. **[RetrieveVGGT: Training-Free Long Context Streaming 3D Reconstruction via Query-Key Similarity Retrieval](https://arxiv.org/abs/2605.09644)** · 以查询键相关性从历史中检索固定数量的帧。
15. **[StreamCacheVGGT: Streaming Visual Geometry Transformers with Robust Scoring and Hybrid Cache Compression](https://arxiv.org/abs/2604.15237)** · 用跨层一致性评分与混合保留、合并策略管理固定预算缓存；补充比较不同缓存压缩方案。
16. **[XStreamVGGT: KV Cache Compression](https://arxiv.org/abs/2602.21780)** · 对 StreamVGGT 的历史键值做剪枝和量化，研究缓存压缩的精度—速度取舍。
17. **[STAC: Plug-and-Play Spatio-Temporal Aware Cache Compression for Streaming 3D Reconstruction](https://arxiv.org/abs/2603.20284)** · 对因果 Transformer 的时空稀疏性做缓存压缩，适合与 XStreamVGGT、StreamCacheVGGT 对照。
18. **[LASER: Layer-wise Scale Alignment for Training-Free Streaming 4D Reconstruction](https://arxiv.org/abs/2512.13680)** · 聚焦流式重建中的尺度对齐问题。
19. **[Stream4D: Streaming 4D Reconstruction with Training-free Motion Decoupling via Causal KV-Cache Attention](https://arxiv.org/abs/2610.31320)** · 讨论动态物体对因果注意力和静态地图的干扰。
20. **[Rethinking the State Update Gate for Long-Sequence Recurrent 3D Reconstruction](https://arxiv.org/abs/2605.16981)** · 在 TTT3R 的逐 token 更新之外增加帧级写入权重，分析循环状态的有效记忆跨度。
21. **[TTSA3R: Training-Free Temporal-Spatial Adaptive Persistent State for Streaming 3D Reconstruction](https://arxiv.org/abs/2601.22615)** · 从时间状态变化和空间观测质量共同调整记忆写入，补充 TTT3R 的测试时更新路线。
22. **[StreamSplat: Towards Online Dynamic 3D Reconstruction from Uncalibrated Video Streams](https://arxiv.org/abs/2506.08862)** · 动态场景与 3D Gaussian 表示的相邻方向；评测对象与以点图和相机轨迹为主的流式模型不同。

### 第四优先级：移动端资源与通用几何基础

22. **[FastVGGT: Fast Visual Geometry Transformer](https://arxiv.org/abs/2509.02560)** · 作为全局视觉几何模型的推理加速参照。
23. **[VGG-T³: Offline Feed-Forward 3D Reconstruction at Scale](https://research.nvidia.com/labs/dvl/projects/vgg-ttt/)** · 通过测试时训练压缩全局场景表示；虽然不是在线 SLAM，可作为长序列离线推理的效率对照。
24. **[Lite3R: A Model-Agnostic Framework for Efficient Feed-Forward 3D Reconstruction](https://arxiv.org/abs/2605.11354)** · 关注线性注意力和低成本重建。
25. **[QVGGT: Post-Training Quantized Visual Geometry Grounded Transformer](https://arxiv.org/abs/2605.31124)** · 关注几何模型的后训练量化和精度影响。
26. **[GVG-SLAM: GNSS/VGGT-SLAM Integrated Navigation Method for Outdoor Environments](https://www.ion.org/publications/abstract.cfm?articleID=20725)** · 将 GNSS 因子接入 VGGT-SLAM 2.0，作为室外多传感器融合扩展。

### 第五优先级：多视图注意力中的相机位置编码

27. **[Cameras as Relative Positional Encoding](https://arxiv.org/abs/2507.10496)** · 对比射线图、相对位姿编码与 PRoPE；关注相机内外参如何共同表达为相对位置关系。
28. **[RayRoPE: Projective Ray Positional Encoding for Multi-view Attention](https://arxiv.org/abs/2601.15275)** · 在射线上预测深度点并用查询帧投影坐标计算多频相似度；关注几何自适应编码、不确定性处理及其与 PRoPE 的联系。

阅读清单中已有专题文章或足以承担基础背景的内容不再单列为待写论文，例如 VINS-Mono 已在 [IMU 预积分与视觉惯性方法笔记](../vins-lio-sam-preintegration/index.md) 中涉及；DROID-SLAM、DPVO、DPV-SLAM 等也已有独立解读。若后续核对发现论文已被站内文章完整覆盖，将标为已完成，不重复创建。
