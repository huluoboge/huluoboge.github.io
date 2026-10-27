# 待读论文清单

记录计划写成博客的论文。此文件仅供仓库维护，不属于博客导航或渲染生成的页面；公开仓库的部署产物中可能通过源文件路径访问。

状态：`待评估` → `待读` → `写作中` → `已发布`（发布后可移到已发布记录，或直接从清单删除）。

## 计划选题

| 状态 | 类型 | 标签 | 论文 | 链接 | 想写的角度 / 备注 |
| --- | --- | --- | --- | --- | --- |
| 待评估 | 新视角合成 | 多视图；潜在几何；实时渲染 | LagerNVS: Latent Geometry for Fully Neural Real-time Novel View Synthesis | [arXiv:2603.20176](https://arxiv.org/abs/2603.20176) | CVPR 2026；3D 感知潜特征与实时新视角合成 |
| 待评估 | 新视角合成 | 多视图扩散；几何基础模型；条件生成 | Repurposing Geometric Foundation Models for Multi-view Diffusion | [arXiv:2603.22275v1](https://arxiv.org/abs/2603.22275v1) | ECCV 2026 |
| 待评估 | 新视角合成 | 稀疏视角；几何条件；视频扩散 | VGGT-Diff: Visual Geometry Meets Diffusion for Sparse-View Novel View Synthesis | [arXiv:2609.33253](https://arxiv.org/abs/2609.33253) | 稀疏视角新视角合成；视觉几何与扩散模型结合 |
| 待评估 | 新视角合成 | 隐式重建；联合训练；视频生成 | RoGe: Novel View Synthesis via End-to-End Implicit Reconstruction and Generation | [arXiv:2609.02847](https://arxiv.org/abs/2609.02847) | 端到端联合隐式重建与生成 |
| 待评估 | 多视图立体 | MVS；极线 Transformer；深度估计 | MVSTER: Epipolar Transformer for Efficient Multi-View Stereo | [arXiv:2204.07346](https://arxiv.org/abs/2204.07346) | ECCV 2022；极线 Transformer 与高效多视图立体匹配 |
| 待评估 | SfM 与定位 | Bundle Adjustment；多视图匹配；单目先验 | BLASt3R: Bundle Adjustment of Any Image Set with Multi-View Matching and Monocular Priors | [arXiv:2609.05210](https://arxiv.org/abs/2609.05210) | ECCV 2026；多视图匹配、单目先验与 Bundle Adjustment |
| 已发布 | 视觉惯性 SLAM | 增量优化；Bundle Adjustment；全局一致性 | ICE-BA: Incremental, Consistent and Efficient Bundle Adjustment for Visual-Inertial SLAM | [CVPR 2018](https://openaccess.thecvf.com/content_cvpr_2018/html/Liu_ICE-BA_Incremental_Consistent_CVPR_2018_paper.html) | 高效增量式视觉惯性 BA 与全局一致性；[论文解读](articles/ice-ba/index.md) |
| 已发布 | SfM 与定位 | MASt3R；基础模型；全局对齐 | MASt3R-SfM: a Fully-Integrated Solution for Unconstrained Structure-from-Motion | [arXiv:2409.19152](https://arxiv.org/abs/2409.19152)；[论文解读](articles/mastr-sfm/index.md) | 3DV 2025；基于 3D 视觉基础模型的无约束 SfM |
| 待评估 | 视觉表征学习 | 自监督；掩码建模；ViT | Masked Autoencoders Are Scalable Vision Learners | [arXiv:2111.06377](https://arxiv.org/abs/2111.06377) | CVPR 2022；掩码自编码器与视觉自监督预训练 |
| 待评估 | 视觉表征学习 | ResNet；残差连接；图像识别 | Deep Residual Learning for Image Recognition | [arXiv:1512.03385](https://arxiv.org/abs/1512.03385) | CVPR 2016；残差学习与深层网络优化 |
| 待评估 | 图像重建与编辑 | 梯度域；强度约束；基础结构 | Gradient-Domain Image Reconstruction Framework with Intensity-Range and Base-Structure Constraints | [CVPR 2016](https://openaccess.thecvf.com/content_cvpr_2016/html/Shibata_Gradient-Domain_Image_Reconstruction_CVPR_2016_paper.html) | 梯度域图像重建；强度范围与基础结构约束 |
| 待评估 | 图像重建与编辑 | Poisson 编辑；图像克隆；闭式求解 | Seamless Image Cloning by a Closed Form Solution of a Modified Poisson Problem | [DOI: 10.1145/2407156.2407173](https://doi.org/10.1145/2407156.2407173) | SIGGRAPH Asia 2012 Posters；改进 Poisson 问题的闭式求解 |
| 待评估 | 图像重建与编辑 | 梯度域；四叉树；图像合成 | Efficient Gradient-Domain Compositing Using Quadtrees | [DOI: 10.1145/1276377.1276495](https://doi.org/10.1145/1276377.1276495) | SIGGRAPH 2007；用四叉树降低梯度域合成的求解规模 |
| 待评估 | 多视图重建 | 广角相机；鱼眼；相机模型条件化 | Wid3R: Wide Field-of-View 3D Reconstruction via Camera Model Conditioning | [arXiv:2602.05321](https://arxiv.org/abs/2602.05321) | ECCV 2026；广角相机模型条件化的多视图 3D 重建 |
| 待评估 | 单目重建 | 度量点云；鱼眼；全景相机 | OmniPoint: Universal Monocular Metric Pointcloud from Any Camera | [arXiv:2609.09394](https://arxiv.org/abs/2609.09394) | ECCV 2026；面向多种相机模型的单目度量点云重建 |
| 待评估 | 多视图重建 | 测试时训练；线性扩展；视觉几何 | VGG-T³: Offline Feed-Forward 3D Reconstruction at Scale | [arXiv:2602.23361](https://arxiv.org/abs/2602.23361) | CVPR 2026；通过测试时训练扩展离线前馈重建的规模 |
| 待评估 | 模型压缩与加速 | VGGT；后训练量化；边缘推理 | QVGGT: Post-Training Quantized Visual Geometry Grounded Transformer | [arXiv:2605.31124](https://arxiv.org/abs/2605.31124) | CVPR 2026；报告最高 2.8×硬件加速；未据此声称已实现手机 NPU 部署 |
| 待评估 | 模型压缩与加速 | 稀疏线性注意力；FP8-aware QAT；代码已公开 | Lite3R: A Model-Agnostic Framework for Efficient Feed-Forward 3D Reconstruction | [arXiv:2605.11354](https://arxiv.org/abs/2605.11354) | 用稀疏线性注意力和 FP8 感知量化训练提升前馈 3D 重建效率 |
| 待评估 | 多视图重建 | VGGT；训练自由加速；Token Pruning | FastVGGT: Fast Visual Geometry Transformer | [ICLR 2026](https://proceedings.iclr.cc/paper_files/paper/2026/hash/9f5b159f2c1d216d73bc0c289763dbfc-Abstract-Conference.html) | 训练自由地削减 VGGT 全局注意力计算冗余 |
| 待评估 | 多视图重建 | 几何先验；多任务；前馈模型 | WorldMirror: Universal 3D World Reconstruction with Any-Prior Prompting | [arXiv:2510.10726](https://arxiv.org/abs/2510.10726) | ICML 2026；融合多种几何先验的通用前馈 3D 重建 |
| 待评估 | SfM 与定位 | 大规模 SfM；场景回归；视觉定位 | SAIL-Recon: Large SfM by Augmenting Scene Regression with Localization | [arXiv:2508.17972](https://arxiv.org/abs/2508.17972) | 3DV 2026 Oral；扩展到大规模图像集的场景回归与视觉定位 |
| 已发布 | 流式多视图重建 | 因果注意力；KV Cache；4D 重建 | StreamVGGT: Streaming Visual Geometry Transformer | [arXiv:2507.11539](https://arxiv.org/abs/2507.11539) | ICLR 2026；[论文解读](articles/streamvggt/index.md)；通过因果 Transformer 与历史 KV Cache 实现逐帧重建 |
| 已发布 | 流式多视图重建 | Decoder-only；因果注意力；滑动窗口 | STream3R: Scalable Sequential 3D Reconstruction with Causal Transformer | [arXiv:2508.10893](https://arxiv.org/abs/2508.10893) | ICLR 2026；[论文解读](articles/stream3r/index.md)；支持 KV Cache 与滑动窗口推理 |
| 已发布 | 流式多视图重建 | 时空缓存压缩；体素记忆；KV Cache | STAC: Plug-and-Play Spatio-Temporal Aware Cache Compression for Streaming 3D Reconstruction | [arXiv:2603.20284](https://arxiv.org/abs/2603.20284) | CVPR 2026；[论文解读](articles/stac/index.md)；双缓存压缩与分块推理 |
| 已发布 | 流式多视图重建 | 最近 11 帧；相邻帧相对位姿；旋转精化 | ABot-Recon: Revisiting Local Context for Long-Horizon Streaming 3D Reconstruction | [arXiv:2608.27529](https://arxiv.org/abs/2608.27529) | 优先级：极高；[论文解读](articles/abot-recon/index.md)；固定局部上下文、逐步组合相对位姿与局部几何 |
| 已发布 | 流式多视图重建 | 滑动窗口；Sim(3) 注册；深度层尺度传播 | LASER: Layer-wise Scale Alignment for Training-Free Streaming 4D Reconstruction | [arXiv:2512.13680v3](https://arxiv.org/abs/2512.13680) | CVPR 2026；[论文解读](articles/laser/index.md)；训练自由复用离线重建主干 |
| 已发布 | 流式多视图重建 | 动态分割；因果 KV Cache；4D 重建 | Stream4D: Streaming 4D Reconstruction with Training-free Motion Decoupling via Causal KV-Cache Attention | [arXiv:2610.31320v1](https://arxiv.org/abs/2610.31320) | 第一优先级；[论文解读](articles/stream4d/index.md)；从因果注意力和深度先验估计动态区域并调制历史 Key |
| 已发布 | 流式多视图重建 | 循环状态；帧级门控；长序列漂移 | Rethinking the State Update Gate for Long-Sequence Recurrent 3D Reconstruction | [arXiv:2605.16981v3](https://arxiv.org/abs/2605.16981) | NeurIPS 2026；[论文解读](articles/rethinking-state-update-gate/index.md)；用已有特征差计算帧级写入权重，与逐 token 门控互补 |
| 已发布 | 流式多视图重建 | 持久状态；时空自适应门控；免训练推理 | TTSA3R: Training-Free Temporal-Spatial Adaptive Persistent State for Streaming 3D Reconstruction | [arXiv:2601.22615v4](https://arxiv.org/abs/2601.22615) | [论文解读](articles/ttsa3r/index.md)；用候选状态变化与图像空间上下文调节逐 token 写入 |
| 已发布 | 动态视觉 SLAM | 通用三维先验；运动物体分割；不确定性感知 BA | Dynamic Visual SLAM using a General 3D Prior | [CVPR 2026](https://openaccess.thecvf.com/content/CVPR2026/html/Zhong_Dynamic_Visual_SLAM_using_a_General_3D_Prior_CVPR_2026_paper.html) | [论文解读](articles/dynamic-visual-slam-general-3d-prior/index.md)；扩展 π³ 的运动分割头，并将深度先验、批次尺度对齐与在线 patch BA 结合 |
| 已发布 | 动态三维重建 | 无标定视频流；Gaussian Splatting；概率位置采样 | StreamSplat: Towards Online Dynamic 3D Reconstruction from Uncalibrated Video Streams | [arXiv:2506.08862v2](https://arxiv.org/abs/2506.08862) | ICLR 2026；[论文解读](articles/streamsplat/index.md)；以双向变形和透明度生命周期在线融合动态 Gaussian，不显式估计相机轨迹 |
| 已发布 | 在线三维重建 | 无位姿图像流；Gaussian Splatting；跨帧合并 | StreamGS: Online Generalizable Gaussian Splatting Reconstruction for Unposed Image Streams | [ICCV 2025](https://openaccess.thecvf.com/content/ICCV2025/html/Li_StreamGS_Online_Generalizable_Gaussian_Splatting_Reconstruction_for_Unposed_Image_Streams_ICCV_2025_paper.html) | [论文解读](articles/streamgs/index.md)；DUSt3R 初始化、匹配驱动细化与前馈高斯密度控制 |
| 已发布 | 动态场景重建与三维跟踪 | 时间相关点图；世界坐标；测试时适配 | St4RTrack: Simultaneous 4D Reconstruction and Tracking in the World | [ICCV 2025](https://openaccess.thecvf.com/content/ICCV2025/html/Feng_St4RTrack_Simultaneous_4D_Reconstruction_and_Tracking_in_the_World_ICCV_2025_paper.html) | [论文解读](articles/st4rtrack/index.md)；用双分支点图统一逐帧动态重建与首帧点的世界坐标轨迹 |
| 已发布 | 动态场景重建 | 高阶运动；因果窗口；语言对齐语义 | SLARM: Streaming and Language-Aligned Reconstruction Model for Dynamic Scenes | [CVPR 2026](https://openaccess.thecvf.com/content/CVPR2026/html/Qiu_SLARM_Streaming_and_Language-Aligned_Reconstruction_Model_for_Dynamic_Scenes_CVPR_2026_paper.html) | [论文解读](articles/slarm/index.md)；已知相机位姿下联合预测动态 Gaussian、场景流与语义 |
| 已发布 | 视觉 SLAM 与重建 | XFeat 跟踪；前馈子图；双层闭环 | EC3R-SLAM: Efficient and Consistent Monocular Dense SLAM with Feed-Forward 3D Reconstruction | [arXiv:2510.02080](https://arxiv.org/abs/2510.02080) | [论文解读](articles/ec3r-slam/index.md)；以关键帧缓冲控制 VGGT 子图推理，并将局部/全局闭环加入 Sim(3) 位姿图 |
| 已发布 | 视觉 SLAM 与重建 | Gaussian BA；相机自标定；子图尺度对齐 | VGGT-GS SLAM: Uncalibrated Monocular Gaussian Splatting SLAM with Feed-Forward Priors | [arXiv:2609.19628v1](https://arxiv.org/abs/2609.19628) | [论文解读](articles/vggt-gs-slam/index.md)；联合优化 Gaussian 地图、位姿与畸变，并用 GNA 对齐子图、验证回环 |
| 已发布 | 动态流式四维重建 | Motion-aligned attention；分组因果注意力；相机 token 聚合 | MoRe: Motion-aware Feed-forward 4D Reconstruction Transformer | [arXiv:2603.05078v2](https://arxiv.org/abs/2603.05078v2) | [论文解读](articles/more/index.md)；逐帧几何预测后以全序列相机 token 做 BA-like 精化 |
| 待读 | 视觉 SLAM 与重建 | RGB-D；点图先验；公制尺度 | VGGT-Geo: Probabilistic Geometric Fusion of Visual Geometry Grounded Transformer Priors for Robust Dense Indoor SLAM | [MDPI 15(2), 85](https://www.mdpi.com/2220-9964/15/2/85) | 当前 PDF 来源返回 403，取得并核验原文后再写；暂不以网页摘要代替论文 |
| 已发布 | 视觉 SLAM 与重建 | 学习式匹配更新；Dense Bundle Adjustment；因子图 | DROID-SLAM: Deep Visual SLAM for Monocular, Stereo, and RGB-D Cameras | [arXiv:2108.10869](https://arxiv.org/abs/2108.10869) | 优先级：极高；通过 DBA 迭代更新位姿和深度；[论文解读](articles/droid-slam/index.md) |
| 已发布 | 视觉 SLAM 与重建 | 动态场景；不确定性感知；Differentiable Bundle Adjustment | DROID-SLAM in the Wild | [CVPR 2026](https://openaccess.thecvf.com/content/CVPR2026/html/Li_DROID-SLAM_in_the_Wild_CVPR_2026_paper.html) | [论文解读](articles/droid-slam-in-the-wild/index.md)；用多视图特征不一致估计逐像素不确定性，增强动态环境下的跟踪与重建 |
| 已发布 | 视觉里程计与 SLAM | Patch 跟踪；可微 BA；Patch 图；关键帧 | Deep Patch Visual Odometry (DPVO) | [arXiv:2208.04726](https://arxiv.org/abs/2208.04726) | [论文解读](articles/dpvo/index.md) |
| 已发布 | 视觉 SLAM 与重建 | Pointmap 匹配；几何优化；局部与全局图 | MASt3R-SLAM: Real-Time Dense SLAM with 3D Reconstruction Priors | [arXiv:2412.12392](https://arxiv.org/abs/2412.12392) | CVPR 2025；优先级：很高；融合 Pointmap 匹配与局部、全局几何优化；[论文解读](articles/mast3r-slam/index.md) |
| 已发布 | 视觉 SLAM 与重建 | 前馈几何；持久因子图；Dense Bundle Adjustment | F²SLAM: Turning Feed-Forward Geometry into Persistent Factors for SLAM | [arXiv:2610.05207](https://arxiv.org/abs/2610.05207) | 将前馈几何转成持久因子图中的优化约束；[论文解读](articles/f2-slam/index.md) |
| 已发布 | 视觉 SLAM 与重建 | RGB-D；点图条件化；度量深度锚定 | Pow3R-SLAM: Real-Time RGB-D SLAM with 3D Reconstruction Priors | [arXiv:2609.38054v1](https://arxiv.org/abs/2609.38054) | [论文解读](articles/pow3r-slam/index.md)；深度作为网络条件、尺度来源与后端约束 |
| 已发布 | 流式多视图重建 | 持久状态；循环 Transformer；在线 Pointmap | Continuous 3D Perception Model with Persistent State (CUT3R) | [arXiv:2501.12387](https://arxiv.org/abs/2501.12387) | CVPR 2025；[论文解读](articles/cut3r/index.md)；用持续更新的隐式状态维护场景记忆 |
| 已发布 | 流式多视图重建 | 空间指针记忆；显式地图；历史融合 | Point3R: Streaming 3D Reconstruction with Explicit Spatial Pointer Memory | [arXiv:2507.02863](https://arxiv.org/abs/2507.02863) | NeurIPS 2025；让新图像特征与带三维位置的空间记忆交互；[论文解读](articles/point3r/index.md) |
| 已发布 | 视觉 SLAM 与重建 | 滑动窗口；局部 Pointmap；全局配准 | SLAM3R: Real-Time Dense Scene Reconstruction from Monocular RGB Videos | [arXiv:2412.09401](https://arxiv.org/abs/2412.09401) | CVPR 2025；论文报告 20+ FPS，属于论文测试硬件结果；[论文解读](articles/slam3r/index.md) |
| 待评估 | 多视图重建 | 循环 Transformer；迭代细化；推理计算 | Déjà View: Looping Transformers for Multi-View 3D Reconstruction | [arXiv:2605.30215](https://arxiv.org/abs/2605.30215) | NeurIPS 2026 Oral；循环共享 Transformer 模块进行多视图重建 |
| 已发布 | 特征匹配 | 稠密匹配；DINOv3；亚像素精度 | RoMa v2: Harder Better Faster Denser Feature Matching | [arXiv:2511.15706](https://arxiv.org/abs/2511.15706) | 改进困难场景下的鲁棒稠密匹配，并提升速度与匹配密度；[论文解读](articles/roma-v2/index.md) |
| 已发布 | 特征匹配 | 前馈 3D 模型；VGGT-Ω；稠密匹配 | RoMa-Ω: What Feed-Forward 3D Models Know About Image Matching | [arXiv:2609.09507](https://arxiv.org/abs/2609.09507) | 分析前馈 3D 表征的匹配能力，并将 VGGT-Ω 特征用于 RoMa v2；[论文解读](articles/roma-omega/index.md) |
| 已发布 | 特征匹配 | 稠密匹配；核回归；几何估计 | DKM: Dense Kernelized Feature Matching for Geometry Estimation | [CVPR 2023](https://openaccess.thecvf.com/content/CVPR2023/html/Edstedt_DKM_Dense_Kernelized_Feature_Matching_for_Geometry_Estimation_CVPR_2023_paper.html) | 通过核回归全局匹配、warp 细化与稠密置信度估计进行两视图几何匹配；[论文解读](articles/dkm/index.md) |
| 待评估 | 特征匹配 | 全景图像；等距柱状投影；球面几何 | EDM: Equirectangular Projection-Oriented Dense Kernelized Feature Matching | [CVPR 2025](https://openaccess.thecvf.com/content/CVPR2025/html/Jung_EDM_Equirectangular_Projection-Oriented_Dense_Kernelized_Feature_Matching_CVPR_2025_paper.html) | 面向全景图像的稠密匹配；以球面相机模型和测地流细化处理投影畸变 |
| 待评估 | 特征匹配 | ERP 全景匹配；球面一致性；RoMa | SCCM: Spherically Consistent Coarse Matching for ERP Dense Feature Correspondence | [arXiv:2609.36545](https://arxiv.org/abs/2609.36545) | 在粗匹配阶段建模 ERP 的球面拓扑、度量与面积畸变 |
| 已发布 | 特征匹配 | Detector-free；Transformer；低纹理匹配 | LoFTR: Detector-Free Local Feature Matching with Transformers | [CVPR 2021](https://openaccess.thecvf.com/content/CVPR2021/html/Sun_LoFTR_Detector-Free_Local_Feature_Matching_With_Transformers_CVPR_2021_paper.html) | 通过 Transformer 建立粗到细对应关系，在低纹理区域也能产生稠密匹配；[论文解读](articles/loftr/index.md) |
| 待评估 | 特征匹配 | 轻量局部特征；半稠密匹配；实时推理 | XFeat: Accelerated Features for Lightweight Image Matching | [CVPR 2024](https://openaccess.thecvf.com/content/CVPR2024/html/Potje_XFeat_Accelerated_Features_for_Lightweight_Image_Matching_CVPR_2024_paper.html) | 兼顾稀疏与半稠密匹配的轻量特征模型；也是 Tiny RoMa 的基础之一 |

## 使用方式

- 想法先记在表格里；确定要写后更新状态并补充阅读笔记。
- 开始写作时，在 `blog/articles/<slug>/index.md` 新建文章，并按 [博客写作 Skill](skills/blog-writing/SKILL.md) 中的论文写作要求撰写。
- 发布完成后，将条目标为已发布或从待写清单移除。
