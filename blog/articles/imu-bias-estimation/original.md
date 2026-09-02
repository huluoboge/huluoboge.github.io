# 加速度计零偏如何影响 SLAM 中的重力对齐

## 摘要

长距离 SLAM 轨迹往往会积累细小的 roll 与 pitch 误差，并将其投影为缓慢变化的高度畸变。IMU 加速度计为世界竖直方向提供了绝对参考，但加速度计零偏使这一问题变得复杂：在运动激励不足时，零偏与世界系倾斜通过同一观测通道进入测量，因此一条发生倾斜的轨迹可能被“解释”为存在一个虚假的零偏，使重力校正悄然失败。

本文系统分析加速度计零偏干扰重力对齐的机制。首先说明重力只能约束两个姿态自由度，即 roll 与 pitch；yaw 和纯平移仍不可观。随后分别推导静止（零加速度）通道和一般 IMU 预积分通道中的零偏—倾斜耦合。在预积分通道中，该耦合表现为一个恒定的机体系零偏与一个随姿态旋转的倾斜投影之间的差。由此可知，可分离性是姿态激励的二值性质，而估计精度则会随正规方程条件数连续退化。时变随机游走零偏还会引入第二种失效模式：当倾斜投影变化速度慢于零偏漂移速度时，倾斜会被零偏吸收并变得不可辨识；拟合零偏的时间平坦性可以揭示这一现象。

在此基础上，本文给出一种预积分因子图实现：在软位姿先验下，利用完整原始 IMU 数据联合估计位姿、速度、零偏和加速度计尺度。我们在 EuRoC、TUM-VI、KITTI 和 UrbanLoco 的十条公开序列上进行验证，并使用四种 SLAM 基线。按照仅 yaw 对齐的评估协议，该方法在所有有效序列上均降低了 roll/pitch RMSE，中位数降幅分别为 $71\%$ 和 $55\%$；消融实验也符合理论预测：在汽车场景的弱激励条件下，零偏建模至关重要，而在激励充分的手持场景中影响较小。

**关键词：** SLAM；重力对齐；加速度计零偏；姿态倾斜；IMU 预积分；可观性

## 1. 引言

视觉、LiDAR 以及融合式 SLAM 轨迹通常具有较好的局部精度，但会出现缓慢的 roll/pitch 漂移，即估计的世界系逐渐偏离真实的重力对齐坐标系。角度误差虽然很小，却会造成明显的位置误差：若水平距离为 $h$，世界系发生 $\lVert\delta\boldsymbol\theta\rVert$ 的倾斜，则高度误差约为

$$
 h\tan\lVert\delta\boldsymbol\theta\rVert\approx h\lVert\delta\boldsymbol\theta\rVert .
$$

因此，长距离运动中的数度倾斜足以产生米级高度畸变。例如，在 KITTI 0009 序列中，LIO-SAM 前端带有约 $4^\circ$ 的固定世界系 roll 偏差，其水平投影造成 $4.23\,\mathrm{m}$ 的高度误差 RMSE。表面症状是高度隆起，真正原因却是旋转误差。

用于协调相对漂移的标准工具是带回环约束的位姿图优化（PGO），但它不能提供世界竖直方向的绝对锚定。回环边是相对约束，对整个世界坐标系施加共同旋转不会改变相对残差；因此，回环可以在一个倾斜的坐标系中完全闭合，同时保留错误的绝对 roll/pitch，并使高度剖面发生畸变 [Kümmerle et al., 2011; Kaess et al., 2012; Grisetti et al., 2010]。

IMU 加速度计提供了缺失的绝对参考：在机体系中，它测量比力；在非加速时间窗内，比力的长期均值指向世界竖直方向。这一性质广泛用于视觉—惯性初始化与在线估计 [Qin et al., 2018; Campos et al., 2021; Forster et al., 2017]。然而，基于 IMU 的重力对齐并非没有代价，主要障碍正是加速度计零偏。零偏是恒定或缓慢变化的机体系偏移，而倾斜是缓慢变化的世界系旋转；二者通过测量模型进入相同方程，在运动激励不足时会彼此混淆。实际结果是：朴素的重力校正可能通过“创造”一个虚假零偏来解释倾斜轨迹，从而保留倾斜并静默失败。

本文围绕以下问题展开：

- **重力能够、也不能观测什么：** 重力恰好约束 roll 与 pitch 两个自由度；只有在姿态变化时，这两个可观方向才能与零偏分离。
- **零偏从何处进入：** 静止通道与一般预积分通道中都存在零偏—倾斜耦合，表现为恒定零偏与旋转倾斜投影之间的机体系差异。
- **何时分离失败：** 弱激励使正规方程病态；时变零偏还会形成慢漂移零空间，吸收变化较慢的倾斜投影。
- **如何诊断：** 失败校正得到的拟合零偏通常具有与输入倾斜相同时间尺度的变化特征。
- **如何实现：** 基于完整原始 IMU 数据的预积分因子图，在软位姿先验下联合估计位姿、速度、零偏和加速度计尺度，无需重新运行 SLAM 前端。

本文假设已有完整的 SLAM 轨迹和同步原始 IMU 数据，并允许对其进行离线后处理。详细推导放在附录中，以保持正文对核心机制的连贯说明。

## 2. 背景与相关工作

视觉—惯性和 LiDAR—惯性系统通常将 IMU 测量与视觉或 LiDAR 因子紧耦合。MSCKF 等滤波器会边缘化路标点；直接式 EKF 将图像强度与 IMU 驱动的状态结合；OKVIS、VINS-Mono 和 ORB-SLAM3 等关键帧优化系统在滑动窗口状态与回环约束中使用惯性残差；LIO-SAM、FAST-LIO 和 FAST-LIO2 则将原始或配准后的 LiDAR 数据与 IMU 状态估计融合。

这些系统都在在线状态中估计重力方向和 IMU 零偏，并使用 IMU 预积分 [Lupton and Sukkarieh, 2012; Forster et al., 2015, 2017]。预积分允许每个关键帧区间只计算一次惯性残差，并在零偏改变时进行一阶修正，这正是本文因子图实现的基础。

需要明确的是，将零偏放入状态向量并不会自动使其可观。可观性取决于测量结构和运动方式：汽车轨迹的航向变化有限，机体系中的世界倾斜投影变化很小，估计零偏会吸收虚假的倾斜分量；滑动窗口边缘化会丢弃早期状态，使后续激励难以追溯修复早期的零偏—倾斜混淆；相对回环只能约束几何关系，不能消除共同世界倾斜；而激励不足的初始化还可能固定错误的零偏—倾斜基底。

PGO 是协调相对里程计和回环测量的标准工具，但仅含相对约束的 PGO 对共同世界倾斜不敏感。离线地图融合和重新优化框架通常需要原始视觉—惯性地图状态；在本文的后处理场景中，能够获得的主要输入是已有轨迹与原始 IMU，因此重力自然成为约束两个绝对 roll/pitch 自由度的参考。

重力长期以来被用于视觉—惯性初始化。已有工作研究了闭式视觉—惯性初始化、联合陀螺仪零偏初始化、基于旋转的初始化以及姿态—重力—IMU 零偏之间的可观性。本文关心的关键事实是：静止标定中，若不约束重力大小，倾斜姿态可以被加速度计零偏吸收；而零偏—倾斜退化并非静止场景特有，在姿态保持不变时同样存在于一般预积分残差中。

基于图像的重力估计是另一条相互独立的研究路线，例如利用消失点、地平线或学习模型估计全局旋转。此类方法通常估计单个全局旋转，不能描述由零偏—倾斜耦合产生的时变慢倾斜漂移，且依赖线结构丰富的场景或学习先验。本文聚焦于基于 IMU 的重力对齐机制。

## 3. 符号、坐标系与测量模型

### 3.1 位姿与流形约定

令 $\mathrm{SE}(3)$ 表示刚体位姿群，位姿记为
$\mathbf T=(\mathbf R,\mathbf p)$，其中 $\mathbf R\in\mathrm{SO}(3)$、$\mathbf p\in\mathbb R^3$。世界系 $W$ 与重力对齐，机体系 $B$ 固定于传感器平台。采用 body-to-world 约定：

$$
 \mathbf x_W=\mathbf R_{WB}\mathbf x_B .
$$

关键帧位姿写为 $\mathbf T_k=(\mathbf R_k,\mathbf p_k)$，其中 $\mathbf R_k=\mathbf R_{WB,k}$。对 $\boldsymbol\phi\in\mathbb R^3$，$[\boldsymbol\phi]_\times$ 表示反对称矩阵，$\operatorname{Exp}(\cdot)$ 和 $\operatorname{Log}(\cdot)$ 分别表示 $\mathrm{SO}(3)$ 指数映射和主值对数映射。本文的旋转残差均在局部坐标中表达。

### 3.2 重力模型与 IMU 测量

世界系 $+Z$ 轴向上，因此

$$
 \mathbf g_W=(0,0,-g)^\top,\qquad
 \mathbf u_W=(0,0,g)^\top,
 \qquad g=9.81\,\mathrm{m/s^2} .
$$

其中 $\mathbf g_W$ 是重力加速度，$\mathbf u_W$ 是向上的比力方向。对于 body-to-world 旋转 $\mathbf R$，加速度计测量为

$$
 \tilde{\mathbf a}
 =\mathbf R^\top(\mathbf a_W-\mathbf g_W)+\mathbf b_a+\boldsymbol\eta_a
 =\mathbf R^\top\mathbf a_W+\mathbf R^\top\mathbf u_W
   +\mathbf b_a+\boldsymbol\eta_a .
$$

陀螺仪测量为

$$
 \tilde{\boldsymbol\omega}
 =\boldsymbol\omega+\mathbf b_g+\boldsymbol\eta_\omega .
$$

在零加速度片段（静止或匀速运动）中，$\mathbf a_W\approx\mathbf0$，因此均值满足

$$
 \bar{\mathbf a}\approx\mathbf R^\top\mathbf u_W+\mathbf b_a .
$$

这就是静态重力锚：加速度计在机体系中测得重力方向，但观测被加速度计零偏平移。

### 3.3 IMU 预积分

在关键帧 $i$ 与 $j$ 之间，预积分增量为 $\Delta\mathbf R_{ij}$、$\Delta\mathbf v_{ij}$ 和 $\Delta\mathbf p_{ij}$。其一阶零偏 Jacobian 和 IMU 噪声协方差按照 Forster 等人的流形预积分方法计算。本文只需关注以下两个事实：增量在每个关键帧区间内计算一次，零偏变化时可进行线性修正；速度和位置传播包含显式的重力项：

$$
 \mathbf v_j=\mathbf v_i+\mathbf g_W\Delta t+\mathbf R_i\Delta\mathbf v_{ij},
$$

$$
 \mathbf p_j=\mathbf p_i+\mathbf v_i\Delta t+
 \frac12\mathbf g_W\Delta t^2+\mathbf R_i\Delta\mathbf p_{ij} .
$$

绝对重力信息正是通过这两个通道进入基于预积分的估计器。

## 4. 理论分析：零偏—重力耦合机制

给定已经生成的 SLAM 轨迹 $\mathbf T_k=(\mathbf R_k,\mathbf p_k)$、同步的原始 IMU 测量以及可选的回环相对位姿测量。本文不重新运行 SLAM 前端，也不假设存在真值。目标是得到校正后的 $\mathbf T_k^*$，使其 roll/pitch 与绝对重力方向对齐，同时保留输入轨迹和相对约束中的信息。yaw 与纯平移由这些约束继承，因为重力不能提供它们。

### 4.1 重力能够观测什么：秩为二的通道

旋转预积分本身不能提供绝对参考。令

$$
 \mathbf r_{R,ij}=\operatorname{Log}(\Delta\mathbf R_{ij}^{\top}
 \mathbf R_i^{\top}\mathbf R_j) .
$$

对任意共同世界旋转 $\mathbf Q$，令 $\mathbf R'_k=\mathbf Q\mathbf R_k$，则

$$
 \mathbf R_i'^{\top}\mathbf R_j'
 =\mathbf R_i^{\top}\mathbf R_j .
$$

因此，相对旋转残差对共同 roll、pitch 和 yaw 都不敏感。绝对的两个姿态自由度只能通过速度和位置残差中的重力项进入，而不是通过 $\Delta\mathbf R$ 单独进入。

**命题 1（yaw 是全局规范方向）。** 令 $\mathbf R_z(\psi)$ 表示绕世界竖直轴旋转 $\psi$。进行变换

$$
 \mathbf R_k'=\mathbf R_z(\psi)\mathbf R_k,\quad
 \mathbf v_k'=\mathbf R_z(\psi)\mathbf v_k,\quad
 \mathbf p_k'=\mathbf R_z(\psi)\mathbf p_k,
$$

并保持 $\mathbf b_a,\mathbf b_g$ 不变。则所有预积分残差、静态重力锚 $\mathbf R_k^\top\mathbf u_W$ 以及所有回环残差都不变。

原因在于 $\mathbf g_W$ 与 $\mathbf u_W$ 位于旋转轴上，满足 $\mathbf R_z^\top\mathbf g_W=\mathbf g_W$ 和 $\mathbf R_z^\top\mathbf u_W=\mathbf u_W$。完整测量似然对共同 yaw 旋转不敏感，因此 yaw 无论运动激励多么充分都不可观。这是因子图的规范对称性，而不是建模近似。

对于静态通道，若姿态发生无穷小扰动 $\mathbf R\leftarrow\mathbf R\operatorname{Exp}([\delta\boldsymbol\phi]_\times)$，则

$$
 \delta\bar{\mathbf a}
 = [\mathbf R^\top\mathbf u_W]_\times\delta\boldsymbol\phi
 +\mathcal O(\lVert\delta\boldsymbol\phi\rVert^2) .
$$

对平移的 Jacobian 为零，对旋转的 Jacobian 秩为二。因此，重力只能使 roll 和 pitch 可观；yaw 以及三个平移分量均不可观。静态锚还要求窗口内世界系线加速度均值近似为零：

$$
 \frac1{|\mathcal W|}\sum_{i\in\mathcal W}\mathbf a_{W,i}\approx\mathbf0 .
$$

持续加速会破坏该条件，并可能被错误解释为重力方向误差。

**要点：** 重力是秩为二的测量，只锚定 roll 和 pitch。任何重力校正流程都必须从轨迹和相对约束中继承 yaw 与纯平移。

### 4.2 静态通道：倾斜被吸收到虚假零偏中

设 $\delta\boldsymbol\theta_W\in\mathbb R^2$ 是小的世界系 roll/pitch 修正，并通过矩阵 $\mathbf S$ 嵌入三维空间：

$$
 \mathbf S\delta\boldsymbol\theta_W
 =(\delta\theta_x,\delta\theta_y,0)^\top .
$$

对静态观测同时关于倾斜和零偏线性化，有

$$
 \delta(\mathbf R_k^\top\mathbf u_W+\mathbf b_a)
 \approx \mathbf R_k^\top[\mathbf u_W]_\times
 \mathbf S\delta\boldsymbol\theta_W+\delta\mathbf b_a .
$$

当姿态恒定时，倾斜投影是固定方向，无法与 $\delta\mathbf b_a$ 区分。

**命题 2（倾斜诱导的虚假加速度计零偏）。** 设有 $S\ge2$ 个零加速度片段，其均值为

$$
 \bar{\mathbf a}_s=\mathbf R_s^\top\mathbf u_W+\mathbf b_a+\mathbf n_s .
$$

若使用姿态 $\hat{\mathbf R}_s=\mathbf R_s\operatorname{Exp}([\delta\boldsymbol\theta_s]_\times)$ 进行最小二乘零偏估计，则一阶近似下

$$
 \hat{\mathbf b}_a-\mathbf b_a
 \approx-\frac1S\sum_{s=1}^S
 [\mathbf R_s^\top\mathbf u_W]_\times\delta\boldsymbol\theta_s .
$$

对于大小为 $\lVert\delta\boldsymbol\theta_s\rVert$ 的纯 roll/pitch 倾斜，虚假零偏分量的大小近似为

$$
 g\sin\lVert\delta\boldsymbol\theta_s\rVert .
$$

例如，$5^\circ$ 倾斜会诱导

$$
 9.81\sin(5^\circ)\approx0.86\,\mathrm{m/s^2}
$$

的虚假零偏，远高于典型汽车级 IMU 的零偏。静态标定无法区分二者：它要么把倾斜吸收到零偏中，要么在信任零偏时报告一个明显不合理的估计值。

### 4.3 预积分通道：零偏固定而投影旋转

在一般预积分通道中，速度和位置残差的一阶变化为

$$
 \delta\mathbf r_{v,ij}
 =\Delta t(\delta\mathbf b_a-\mathbf R_i^\top\delta\mathbf g_W),
$$

$$
 \delta\mathbf r_{p,ij}
 =\frac12\Delta t^2(\delta\mathbf b_a-\mathbf R_i^\top\delta\mathbf g_W),
 \qquad \delta\mathbf r_{R,ij}=\mathbf0 .
$$

其中 $\delta\mathbf g_W$ 是水平世界重力方向的小扰动。该式直接揭示了耦合形式：$\delta\mathbf b_a$ 固定在机体系中，而 $\mathbf R_i^\top\delta\mathbf g_W$ 会随姿态改变。若姿态恒定，任何水平重力扰动都可以被零偏吸收；若姿态变化，投影方向随时间变化，二者才可能分离。

**命题 3（零偏—倾斜分离需要姿态激励）。** 对所有区间而言，两个水平重力扰动自由度能够与机体系零偏联合分离，当且仅当不存在非零水平向量 $\mathbf t$，使得

$$
 \mathbf R_i^\top\mathbf t=\mathbf R_j^\top\mathbf t
$$

对所有区间 $i,j$ 成立。也就是说，不能存在一个水平世界方向，其机体系投影在整段姿态轨迹上始终不变。

这里的激励来自 $\mathbf R^\top\delta\mathbf g_W$ 的变化，而不是来自平移加速度本身，也不要求一定有 roll/pitch 运动。纯 yaw 旋转同样有效：水平世界向量绕世界竖直轴旋转后，其机体系投影会改变。

### 4.4 原理可分离，实践中病态

命题 3 给出的可分离性是二值性质：任意非零姿态变化原则上都可能满足条件。但估计精度是连续变化的：激励很弱时，投影变化缓慢，正规方程病态，传感器噪声会被放大。因此，弱激励轨迹虽然在理论上可分离，实际零偏估计却可能很差。

例如，KITTI 0009 的航向跨度为 $92^\circ$，结构上已经可分离，但正规方程条件数仍然较高，零偏—倾斜耦合只能被部分解除。接近 $180^\circ$ 的转向—返回动作并非可分离性的必要条件，却能使倾斜投影近似翻转，从而改善条件数。

### 4.5 慢漂移陷阱：时变零偏吸收倾斜

真实加速度计零偏会漂移。若在区间 $i$ 使用时变零偏 $\delta\mathbf b_a^{(i)}$，并通过随机游走先验约束，则当

$$
 \left\|\mathbf R_{i+1}^\top\delta\mathbf g_W
 -\mathbf R_i^\top\delta\mathbf g_W\right\|
 \lesssim \sigma_{\mathrm{rw}}\sqrt{\Delta t_i}
$$

时，可以令 $\delta\mathbf b_a^{(i)}\approx\mathbf R_i^\top\delta\mathbf g_W$，使时变零偏跟踪倾斜投影并吸收倾斜。这里 $\sigma_{\mathrm{rw}}$ 是每单位时间的随机游走密度，右侧是每个区间允许的漂移尺度。

这是一种不同于恒定零偏的失效模式：它不是简单比较“是否存在激励”，而是比较“投影变化速度”和“零偏漂移速度”。当 $\sigma_{\mathrm{rw}}\to0$ 时，时变零偏退化为恒定零偏，恢复命题 3。

### 4.6 失败校正的时间特征

慢变残余倾斜会诱导具有相同时间尺度的虚假零偏。由命题 2，虚假零偏的幅值近似为

$$
 g\sin\lVert\delta\boldsymbol\theta_k\rVert .
$$

因此，拟合零偏若随输入倾斜同步缓慢变化，便是倾斜被零偏吸收的指纹。相反，时间上近似恒定的校正后零偏可以排除这一特定失效模式，但不能排除恒定倾斜被恒定零偏吸收的情况。

在弱激励的 KITTI 序列中，拟合加速度计零偏包含约
$[-0.50,\ 0.34,\ -0.03]$ \(\mathrm{m/s^2}\) 的虚假分量，并吸收了输入的 $4^\circ$ 倾斜；激励充分的手持序列则得到接近零的拟合零偏。

### 4.7 从倾斜到高度：耦合为何重要

在发生倾斜的世界系中，水平距离 $h$ 会产生约

$$
 h\tan\lVert\delta\boldsymbol\theta\rVert
 \approx h\lVert\delta\boldsymbol\theta\rVert
$$

的高度投影误差。仅 $2^\circ$ 的倾斜在每 $100\,\mathrm m$ 水平运动中就可能产生约 $3.5\,\mathrm m$ 的高度误差。

回环不能独立消除该误差，因为回环是相对约束，对共同世界变换不敏感；静态对齐也不能独立完成任务，因为单一姿态下 $\delta\mathbf g_W$ 与 $\mathbf b_a$ 只通过固定投影进入观测。真正的校正需要重力提供 roll/pitch 绝对约束，同时由里程计与回环保留相对 yaw 和平移结构。

## 5. 方法：预积分因子图

本文采用一种紧耦合的 Forster 预积分因子图，在原始 IMU 数据上联合估计关键帧状态、速度、逐帧零偏和全局加速度计尺度。静止片段标定得到的零偏（若存在）只用于初始化。因子图直接建模完整姿态，因此不要求匀速运动或倾斜平滑先验；零偏—倾斜分离由实际姿态激励完成。

### 5.1 流程概述

可选的预标定阶段检测零加速度片段。若这些片段覆盖多个不同姿态，则直接估计零偏并以此初始化因子图；否则从零偏为零开始。核心阶段对完整 IMU 序列进行预积分因子图优化，联合估计每个关键帧的位姿、速度和零偏，以及全局加速度计尺度。最终只校正 roll/pitch，yaw 与纯平移继承自输入轨迹和相对约束。

### 5.2 可选静态标定

当满足

$$
 \lVert\bar{\boldsymbol\omega}_k\rVert<0.02\,\mathrm{rad/s},
 \qquad
 \left|\lVert\bar{\mathbf a}_k\rVert-g\right|<0.4\,\mathrm{m/s^2}
$$

且片段持续至少 $0.5\,\mathrm s$ 时，将其视为零加速度片段。在多个不同姿态上联合求解世界倾斜 $\delta\mathbf g_W$、加速度计零偏和陀螺仪零偏：

$$
\begin{aligned}
\min_{\delta\mathbf g_W,\mathbf b_a,\mathbf b_g}\quad
&\sum_{k=1}^{S}\left(
\left\|\bar{\mathbf a}_k-
\mathbf R_k^\top(\mathbf u_W-\delta\mathbf g_W)-\mathbf b_a\right\|^2 \\
&\qquad+\left\|\bar{\boldsymbol\omega}_k-\mathbf b_g\right\|^2
\right),\\
\text{s.t.}\quad &\lVert\mathbf u_W-\delta\mathbf g_W\rVert=g .
\end{aligned}
$$

陀螺仪零偏可直接由静止均值获得；只有加速度计零偏需要多个不同姿态。范数约束固定重力尺度，否则重力大小与零偏竖直分量混淆，条件数会明显恶化。诊断时，可计算

$$
 \hat{\mathbf u}_W^k=
 \frac{\mathbf R_k(\bar{\mathbf a}_k-\mathbf b_a)}
 {\lVert\mathbf R_k(\bar{\mathbf a}_k-\mathbf b_a)\rVert}
$$

以及锚点倾斜

$$
 \theta_k=\arccos\frac{\hat{\mathbf u}_W^k\cdot\mathbf u_W}
 {\lVert\mathbf u_W\rVert} .
$$

若没有静止片段，或所有片段姿态相同，则跳过该阶段。

### 5.3 因子图目标函数

关键帧状态为

$$
 \mathbf x_k=(\mathbf R_k,\mathbf p_k,\mathbf v_k,
 \mathbf b_a^{(k)},\mathbf b_g^{(k)}),
$$

并估计全局加速度计尺度 $s$。目标函数为

$$
\begin{aligned}
\mathcal C(\mathbf x,s)=
&\sum_{(i,j)\in\mathcal I}
\left\|\mathbf r_{ij}^{\mathrm{preint}}\right\|^2_{\boldsymbol\Sigma_{ij}} \\
&+\sum_k\left\|\mathbf r_k^{\mathrm{prior}}\right\|^2_{\boldsymbol\Sigma_k^{\mathrm{prior}}}
+\sum_k\left\|\mathbf r_k^{\mathrm{odom}}\right\|^2_{\boldsymbol\Sigma^{\mathrm{odom}}}\\
&+\sum_{(a,b)\in\mathcal L}
\rho\left(\left\|\mathbf r_{ab}^{\mathrm{loop}}\right\|^2_{\boldsymbol\Sigma^{\mathrm{loop}}}\right),
\end{aligned}
$$

其中 $\rho$ 为 Cauchy 鲁棒核。加速度模型为

$$
 \mathbf a_{\mathrm{true}}=\frac{\tilde{\mathbf a}-\mathbf b_a}{s},
$$

因此尺度作用于去零偏后的速度和位置预积分增量。

输入位姿先验采用各向异性设计：roll/pitch 的标准差为 $30^\circ$，仅用于在数据不充分时保持解靠近输入；yaw 的标准差为 $1^\circ$，用于固定重力不可观的航向规范；平移标准差为 $20\,\mathrm m$，避免过紧地锚定由漂移造成的高度隆起。相邻关键帧使用 $0.03\,\mathrm m$ 的平移里程计先验，回环边使用 $0.5^\circ$ 和 $0.05\,\mathrm m$ 的旋转/平移标准差；加速度计和陀螺仪随机游走密度分别为 $10^{-3}$ 和 $10^{-4}$。优化后，将首帧平移重新对齐到输入位姿。

这些设计直接对应理论：预积分残差承载零偏—倾斜耦合；姿态状态通过激励改变投影方向，使零偏和倾斜在可激励处实现分离；随机游走因子实现慢漂移速率比较；roll/pitch 与 yaw 的不同先验则反映了二者在可观性上的根本差异。

## 6. 实验验证

### 6.1 数据集与基线

实验使用十条带有度量真值的公开序列：EuRoC MH_01--05（VINS-Fusion）、TUM-VI room1/room2/corridor2（ORB-SLAM3 视觉—惯性）、KITTI 0009（LIO-SAM）以及 UrbanLoco CA-84706（FAST-LIO2）。所有基线均不使用 GNSS/RTK；输入仅包含图像、IMU 和 LiDAR 点云。

### 6.2 评估指标

报告 roll、pitch、倾斜角 RMSE，绝对轨迹误差（ATE）以及高度误差。高度指标采用每个时间戳处注册后的估计高度与插值真值高度之差，并报告 z-error RMSE 和起止高度漂移。由于高度误差是时间分布，单独的起止漂移可能掩盖中间的大幅误差，因此同时观察完整高度曲线。

所有基于 IMU 的公开轨迹均使用仅 yaw 的 4-DOF 对齐：绕世界竖直轴旋转一个 yaw，再进行三维平移。不能使用完整 SE(3) 对齐，因为自由 roll/pitch 会吸收本文要消除的倾斜误差，并可能把水平误差重新旋转到竖直方向。评估窗口噪声底约为 $0.7^\circ$。

### 6.3 可观性数值验证

合成实验使用

$$
 \bar{\mathbf a}_i=\mathbf R_i^\top(\mathbf u_W-\delta\mathbf g_W)
 +\mathbf b_a^{(i)}
$$

并注入噪声。结果验证了三点：任意姿态变化原则上都能分离零偏和倾斜，但激励趋近于零时条件数可增长约 17 个数量级；可分离性是速率比较，$360^\circ$ 激励在 $\sigma_{\mathrm{rw}}=10^{-2}$ 下仍可分离，而 $20^\circ$ 激励会在漂移超过投影变化时失效；虚假零偏符合 $g\sin\delta\theta$ 定律，误差小于 $0.1\%$。

| 激励跨度 | 条件数 | 倾斜误差 |
|---:|---:|---:|
| $0^\circ$ | $10^{17}$ | $0.27$ |
| $2^\circ$ | $3.8\times10^4$ | $0.01$ |
| $20^\circ$ | $3.8\times10^2$ | $0.02$ |
| $90^\circ$ | $19$ | $0.008$ |
| $360^\circ$ | $1.3$ | $0.001$ |

慢漂移速率实验：

| 激励 / $\sigma_{\mathrm{rw}}$ | 投影变化/漂移比 | 倾斜误差 |
|---:|---:|---:|
| $360^\circ/10^{-2}$ | $5.4$ | $0.011$ |
| $20^\circ/10^{-2}$ | $0.3$ | $0.134$ |
| $2^\circ/10^{-3}$ | $0.3$ | $0.131$ |

虚假零偏幅值验证：

| 倾斜角 | 虚假零偏 | $g\sin\theta$ |
|---:|---:|---:|
| $0.5^\circ$ | $0.086$ | $0.086$ |
| $2^\circ$ | $0.342$ | $0.342$ |
| $5^\circ$ | $0.856$ | $0.855$ |

在注入 $5^\circ$ 缓慢 roll/pitch 漂移的 $200\,\mathrm{Hz}$ 行走轨迹上，完整因子图将 roll/pitch 恢复到 $0.3^\circ$ 以下，高度误差降低 $87.7\%$；拟合零偏与注入真值一致，并恢复了加速度计尺度。零偏—漂移时间特征的 Pearson 相关系数高于 $0.9$，幅值误差低于 $20\%$。

### 6.4 公开序列结果

位置结果如下。`输入` 表示基线轨迹，`方法` 表示本文因子图结果。

| 序列 | 基线 | ATE RMSE 输入 (m) | ATE RMSE 方法 (m) | Z 误差 RMSE 输入 (m) | Z 误差 RMSE 方法 (m) |
|---|---|---:|---:|---:|---:|
| EuRoC MH_01 | VINS-Fusion | 0.197 | 0.203 | 0.033 | 0.038 |
| EuRoC MH_02 | VINS-Fusion | 0.114 | 0.127 | 0.018 | 0.029 |
| EuRoC MH_03 | VINS-Fusion | 0.154 | 0.179 | 0.030 | 0.035 |
| EuRoC MH_04 | VINS-Fusion | 0.236 | 0.253 | 0.034 | 0.050 |
| EuRoC MH_05 | VINS-Fusion | 0.341 | 0.305 | 0.094 | 0.110 |
| TUM-VI room1 | ORB-SLAM3 VI | 0.052 | 0.043 | 0.034 | 0.008 |
| TUM-VI room2 | ORB-SLAM3 VI | 0.110 | 0.112 | 0.017 | 0.023 |
| TUM-VI corridor2 | ORB-SLAM3 VI | 12.967 | 12.984 | 0.652 | 0.102 |
| KITTI 0009 | LIO-SAM | 4.464 | 4.096 | 4.232 | 3.119 |
| UrbanLoco CA-84706 | FAST-LIO2 | 446.8 | 446.8 | 16.31 | 16.31 |

旋转结果如下：

| 序列 | roll 输入 | roll 方法 | pitch 输入 | pitch 方法 | tilt 输入 | tilt 方法 |
|---|---:|---:|---:|---:|---:|---:|
| EuRoC MH_01 | 0.72 | 0.12 | 0.30 | 0.14 | 0.22 | 0.14 |
| EuRoC MH_02 | 0.42 | 0.28 | 0.40 | 0.39 | 0.34 | 0.31 |
| EuRoC MH_03 | 0.44 | 0.06 | 0.28 | 0.06 | 0.30 | 0.07 |
| EuRoC MH_04 | 0.37 | 0.04 | 0.36 | 0.06 | 0.46 | 0.06 |
| EuRoC MH_05 | 0.90 | 0.27 | 1.58 | 0.36 | 1.37 | 0.44 |
| TUM-VI room1 | 3.15 | 0.77 | 0.83 | 0.34 | 2.32 | 0.66 |
| TUM-VI room2 | 0.60 | 0.46 | 1.06 | 0.51 | 0.78 | 0.42 |
| TUM-VI corridor2 | 26.42 | 26.66 | 12.91 | 12.64 | 24.30 | 23.98 |
| KITTI 0009 | 4.02 | 1.15 | 1.50 | 1.41 | 2.49 | 0.44 |
| UrbanLoco CA-84706 | 5.60 | 3.54 | 5.79 | 5.02 | 2.24 | 2.64 |

主要发现如下：

1. 在有效序列上，roll RMSE 中位数下降 $71\%$，pitch RMSE 中位数下降 $55\%$，ATE 中位数代价为 $+1\%$。
2. 完整预积分模型不依赖短窗口重力平均，因此在具有持续线加速度的 EuRoC MH 序列上仍可工作。
3. TUM-VI room1 的 roll/pitch RMSE 分别从 $3.15^\circ/0.83^\circ$ 降到 $0.77^\circ/0.34^\circ$，z-error RMSE 从 $0.034\,\mathrm m$ 降到 $0.008\,\mathrm m$。
4. KITTI 0009 仅覆盖 $92^\circ$ 航向变化，属于弱激励场景；方法将 roll 偏差从 $4.02^\circ$ 降到 $1.15^\circ$，将 z-error RMSE 从 $4.232\,\mathrm m$ 降到 $3.119\,\mathrm m$，但仍受病态条件限制。
5. UrbanLoco CA-84706 的 FAST-LIO2 结果带有约 $5$--$6^\circ$ 的固定外参 roll/pitch 偏差，因此属于初步结果，方法不应被宣称为对该问题有效。

### 6.5 消融实验

姿态建模消融将 roll/pitch 固定在输入 SLAM 值，仅保留其他约束。结果表明，显式建模两个绝对姿态未知量是产生校正效果的关键：

| 序列 | 指标 | 姿态自由 | roll/pitch 固定 |
|---|---|---:|---:|
| KITTI 0009 | roll RMSE ($^\circ$) | 1.15 | 4.03 |
| KITTI 0009 | ATE RMSE (m) | 4.10 | 6.53 |
| TUM-VI room1 | roll RMSE ($^\circ$) | 0.77 | 3.15 |
| TUM-VI room1 | z-error RMSE (m) | 0.008 | 0.034 |

零偏建模消融中，KITTI 弱激励场景将零偏固定为静态标定值后，roll 误差由 $1.15^\circ$ 增至 $4.01^\circ$，z-error RMSE 由 $3.12\,\mathrm m$ 增至 $10.73\,\mathrm m$；TUM-VI room1 中该消融基本无影响，说明其静态标定已经接近最优。

关闭全局尺度估计（令 $s\equiv1$）后，KITTI 的 z-error RMSE 从 $4.08\,\mathrm m$ 降为 $3.12\,\mathrm m$ 的优势消失，roll RMSE 为 $1.64^\circ$ 而不是 $1.15^\circ$；该序列估计尺度为 $0.915$，偏离单位值最明显。

将里程计先验参数化为

$$
 \sigma_{\mathrm{odom}}=\alpha\bar d
$$

其中 $\bar d$ 为中位关键帧位移。实验显示 $\alpha\in[0.03,0.1]$ 在三类平台上较稳健；$\alpha=0.1$ 时 KITTI z-error RMSE 从 $3.39\,\mathrm m$ 降至 $2.41\,\mathrm m$，而 $\alpha>0.3$ 后 IMU 预积分噪声导致各序列退化。固定的 $0.03\,\mathrm m$ 默认值在不同平台上对应 $\alpha\in[0.003,0.08]$，对高速平台可能过紧。

### 6.6 运行时间

在包含 $1631$ 个关键帧的序列上，因子图总求解时间约为 $3.4\,\mathrm s$；不含回环时 Ceres 求解约 $2.9\,\mathrm s$，包含精选回环边时约 $2.4\,\mathrm s$。

## 7. 讨论与局限

完整的 $\Delta\mathbf R$、$\Delta\mathbf v$ 和 $\Delta\mathbf p$ 约束使方法不要求匀速或准静态运动，但这并不保证任意数据都能得到唯一校正。在长时间恒姿态、恒速度片段中，倾斜、加速度计零偏以及自由速度/位置修正仍会高度耦合；仅使用旋转预积分也无法消除共同世界倾斜。因此，因子图仍需要重力、零偏和几何约束共同作用。

静止片段并不会自动改善零偏—倾斜的可观性。静止片段提供的是估计精度：它消除了未知运动项，并通过均值降低噪声；真正的分离仍然要求多个静止片段具有不同姿态。激烈的动态运动则应由完整预积分增量建模，而不是简单地窗口平均。

yaw 漂移不在本文方法处理范围内，必须由里程计一致性或回环约束在上游修正；纯平移误差也不属于重力可观集合。高度修复是消除倾斜投影后的结果，并不意味着真实的平移误差能够被重力观测和修复。

### 7.1 数据采集建议

采集开始或结束时的短暂停止片段可用于估计陀螺仪零偏、噪声和重力锚。在运动过程中，应尽量包含多航向转弯、转向返回和闭合路径，即使平台基本保持水平也有帮助：固定世界倾斜会随着航向变化而在机体系中旋转，而机体系零偏不会。若不改变机体航向，仅反向平移并不能产生同等的零偏—倾斜分离效果。起步、停车、转弯、坡面和适度 roll/pitch 变化都能进一步丰富速度与位置预积分约束。

KITTI 汽车轨迹的 yaw/roll/pitch 覆盖率约为 $26\%/3\%/1\%$，航向跨度 $92^\circ$，远小于能够翻转倾斜投影符号的理想转向—返回动作；静态标定条件数为 $19.7$，所得零偏 $[-0.50,0.34,-0.03]$ \(\mathrm{m/s^2}\) 吸收了输入倾斜。相反，手持序列覆盖更充分，因此零偏建模消融基本中性。这支持如下因果链：角度分布 → 条件数 → 零偏质量 → 消融结果。

### 7.2 跨平台适用性

离线处理能够同时看到完整轨迹和全部原始 IMU 数据，不存在滑动窗口边缘化造成的历史信息损失；早期形成的零偏—倾斜混淆可以在后续出现更强激励后被重新修正，代价是无法在线增量运行。离线处理也不能创造数据中不存在的信息：若整段序列始终激励不足，耦合仍只能部分解析。

该流程是黑盒后处理层，只需要已有关键帧位姿、时间戳和同步原始 IMU 数据，原则上与视觉、LiDAR 或融合式前端无关。公开实验覆盖 MAV、手持、汽车 LiDAR 和城市 LiDAR—惯性平台，验证了这一跨传感器迁移性；但更长的汽车序列和 RTK 级竖直真值仍是后续验证方向。

## 8. 结论

加速度计零偏不是一个校准后即可遗忘的 nuisance parameter，而是 SLAM 重力对齐的核心障碍。本文得到以下结论：

1. 重力恰好约束两个姿态自由度，即 roll 和 pitch；yaw 是全局规范方向，纯平移不可观。
2. 在静态通道中，倾斜姿态与大小约为 $g\sin\lVert\delta\theta\rVert$ 的虚假加速度计零偏在观测上等价。
3. 在预积分通道中，耦合表现为恒定机体系零偏与旋转倾斜投影之差；包括纯航向变化在内的任意姿态变化都可能提供分离激励。
4. 可分离性是二值性质，而精度是连续性质；弱激励会使正规方程病态，导致耦合只能部分解除。
5. 时变零偏会产生慢漂移零空间，当倾斜投影变化慢于零偏漂移时吸收倾斜。
6. 拟合零偏是校正过程的直接见证者，其时间特征可以诊断倾斜究竟被消除还是被吸收。

基于完整原始 IMU 序列联合估计位姿、速度、零偏和加速度计尺度的预积分因子图，是实现上述机制的一种直接方式。在十条公开序列和四种不使用 GNSS/RTK 的 SLAM 基线上，该方法在仅 yaw 对齐协议下将有效序列的 roll/pitch RMSE 中位数分别降低 $71\%/55\%$，ATE 中位数代价为 $+1\%$；消融结果也符合弱激励与强激励场景的理论预测。

对 SLAM 使用者而言，最重要的实践信息有两点。第一，当轨迹出现高度隆起时，应先检查 roll/pitch 漂移，而不是直接归咎于平移；高度误差可能只是小倾斜的长距离投影，拟合零偏还能判断重力校正是否真正分离了二者。第二，若采集的数据将来需要重力对齐，应主动设计足够激励：多航向转弯和闭合路径不是可有可无的附加动作，而是使零偏具备可观性的关键条件。里程计先验尺度的残余平台依赖、加速度计尺度异常值以及超出传感器规格的零偏估计，提示未来需要研究面向可观性的自适应调度和长序列 RTK 级高度验证。

## 附录 A：详细推导

### A.1 Hamilton 四元数

Hamilton 四元数记为 $\mathbf q=(q_w,q_x,q_y,q_z)$。令 $\mathbf q_v=(q_x,q_y,q_z)$，则

$$
\mathbf q_1\otimes\mathbf q_2=
\begin{pmatrix}
q_{1w}q_{2w}-\mathbf q_{1v}\cdot\mathbf q_{2v}\\
q_{1w}\mathbf q_{2v}+q_{2w}\mathbf q_{1v}+\mathbf q_{1v}\times\mathbf q_{2v}
\end{pmatrix}.
$$

单位四元数的逆为 $\mathbf q^{-1}=(q_w,-q_x,-q_y,-q_z)$。将 $\mathbf x\in\mathbb R^3$ 视为纯四元数 $(0,\mathbf x)$，则

$$
 \mathbf R(\mathbf q)\mathbf x
 =\mathbf q\otimes(0,\mathbf x)\otimes\mathbf q^{-1} .
$$

### A.2 指数与对数映射

对 $\boldsymbol\phi\in\mathbb R^3$，令 $\theta=\lVert\boldsymbol\phi\rVert$、$\hat{\boldsymbol\phi}=\boldsymbol\phi/\theta$，则 Rodrigues 公式为

$$
\operatorname{Exp}(\boldsymbol\phi)
=\exp([\boldsymbol\phi]_\times)
=\mathbf I+\sin\theta[\hat{\boldsymbol\phi}]_\times
 +(1-\cos\theta)[\hat{\boldsymbol\phi}]_\times^2 .
$$

主值对数在 $\lVert\boldsymbol\phi\rVert<\pi$ 的开球内为其逆映射。右 Jacobian 为

$$
\mathbf J_r(\boldsymbol\phi)=\mathbf I
-\frac{1-\cos\theta}{\theta^2}[\boldsymbol\phi]_\times
+\frac{\theta-\sin\theta}{\theta^3}[\boldsymbol\phi]_\times^2 .
$$

### A.3 Forster IMU 预积分要点

在关键帧 $i,j$ 之间，以去除零偏后的测量

$$
 \tilde{\boldsymbol\omega}_k^\circ=\tilde{\boldsymbol\omega}_k-\mathbf b_g,
 \qquad
 \tilde{\mathbf a}_k^\circ=\tilde{\mathbf a}_k-\mathbf b_a
$$

计算

$$
 \Delta\mathbf R_{ij}
 =\prod_{k=i}^{j-1}\operatorname{Exp}
 (\tilde{\boldsymbol\omega}_k^\circ\Delta t),
$$

$$
 \Delta\mathbf v_{ij}
 =\sum_k\Delta\mathbf R_{ik}\tilde{\mathbf a}_k^\circ\Delta t,
$$

$$
 \Delta\mathbf p_{ij}
 =\sum_k\Delta\mathbf v_{ik}\Delta t
 +\frac12\sum_k\Delta\mathbf R_{ik}	ilde{\mathbf a}_k^\circ\Delta t^2 .
$$

初值为 $\Delta\mathbf R_{ii}=\mathbf I$、$\Delta\mathbf v_{ii}=\Delta\mathbf p_{ii}=\mathbf0$。零偏 Jacobian 和噪声协方差通过标准线性递推得到；零偏变化时对增量进行一阶修正。

### A.4 yaw 规范的证明要点

对所有位姿施加共同 yaw 旋转 $\mathbf R_z$：

$$
 \mathbf R_i'^{\top}\mathbf R_j'
 =(\mathbf R_z\mathbf R_i)^\top(\mathbf R_z\mathbf R_j)
 =\mathbf R_i^\top\mathbf R_j .
$$

由于 $\mathbf R_z^\top\mathbf g_W=\mathbf g_W$，速度残差中的世界重力项在变换后保持不变；位置残差同理。静态锚满足

$$
 (\mathbf R_z\mathbf R_k)^\top\mathbf u_W
 =\mathbf R_k^\top\mathbf u_W .
$$

回环残差对共同世界变换不变，因此完整残差具有一维连续规范对称性，yaw 不可观。

### A.5 倾斜—零偏分离的 Jacobian

将速度残差 Jacobian 在所有区间堆叠，忽略共享尺度后得到

$$
 \mathbf J=\Delta t
 \begin{bmatrix}
 \mathbf R_1^\top & \mathbf I_2\\
 \mathbf R_2^\top & \mathbf I_2\\
 \vdots & \vdots
 \end{bmatrix} .
$$

若存在非零 $[\mathbf t^\top\ \mathbf s^\top]^\top\in\ker\mathbf J$，则对所有区间有

$$
 \mathbf R_i^\top\mathbf t+\mathbf s=\mathbf0 .
$$

这意味着一个固定的水平世界方向在所有姿态下都具有相同的机体系投影。恒定姿态时该条件对所有水平向量成立；随着姿态变化，退化方向逐渐消失，直到不存在这样的方向。

### A.6 慢漂移零空间

若速度残差为零，则要求

$$
 \delta\mathbf b_a^{(i)}=\mathbf R_i^\top\delta\mathbf g_W .
$$

随机游走先验惩罚

$$
 \sum_i\frac{\lVert\delta\mathbf b_a^{(i+1)}-
 \delta\mathbf b_a^{(i)}\rVert^2}
 {\sigma_{\mathrm{rw}}^2\Delta t_i} .
$$

当相邻投影变化位于 $\sigma_{\mathrm{rw}}\sqrt{\Delta t_i}$ 允许范围内时，零偏能够以较小代价跟踪倾斜投影；反之，零偏无法跟踪快速变化的投影，边际信息中会保留可观的倾斜分量。

### A.7 倾斜诱导零偏命题的推导

等权最小二乘估计为

$$
 \hat{\mathbf b}_a=\frac1S\sum_s
 (\bar{\mathbf a}_s-\hat{\mathbf R}_s^\top\mathbf u_W).
$$

代入真实模型后，得到

$$
 \hat{\mathbf b}_a-\mathbf b_a
 =\frac1S\sum_s(\mathbf R_s^\top\mathbf u_W
 -\hat{\mathbf R}_s^\top\mathbf u_W).
$$

又因为

$$
 \hat{\mathbf R}_s^\top
 \approx(\mathbf I-[\delta\boldsymbol\theta_s]_\times)\mathbf R_s^\top,
$$

所以

$$
 \mathbf R_s^\top\mathbf u_W-\hat{\mathbf R}_s^\top\mathbf u_W
 \approx-[\mathbf R_s^\top\mathbf u_W]_\times
 \delta\boldsymbol\theta_s,
$$

从而得到命题 2。对于纯 roll/pitch 倾斜，重力向量端点移动的弦长为
$2g\sin(\lVert\delta\boldsymbol\theta\rVert/2)$，小角度下约为 $g\lVert\delta\boldsymbol\theta\rVert$，与 $g\sin\lVert\delta\boldsymbol\theta\rVert$ 一致。

## 参考文献

1. C. Forster, L. Carlone, F. Dellaert, and D. Scaramuzza. *On-Manifold Preintegration for Real-Time Visual-Inertial Odometry*. IEEE Transactions on Robotics, 2017. DOI: 10.1109/TRO.2016.2597321.
2. C. Forster, L. Carlone, F. Dellaert, and D. Scaramuzza. *IMU Preintegration on Manifold for Efficient Visual-Inertial Maximum-a-Posteriori Estimation*. Robotics: Science and Systems, 2015. DOI: 10.15607/RSS.2015.XI.006.
3. C. Campos et al. *ORB-SLAM3: An Accurate Open-Source Library for Visual, Visual-Inertial, and Multimap SLAM*. IEEE Transactions on Robotics, 2021.
4. T. Qin, P. Li, and S. Shen. *VINS-Mono: A Robust and Versatile Monocular Visual-Inertial State Estimator*. IEEE Transactions on Robotics, 2018.
5. T. Shan et al. *LIO-SAM: Tightly-Coupled Lidar Inertial Odometry via Smoothing and Mapping*. IROS, 2020.
6. M. Burri et al. *The EuRoC Micro Aerial Vehicle Datasets*. IJRR, 2016.
7. D. Schubert et al. *The TUM VI Benchmark for Evaluating Visual-Inertial Odometry*. IROS, 2018.
8. A. Geiger et al. *Vision Meets Robotics: The KITTI Dataset*. IJRR, 2013.
9. W. Wen et al. *UrbanLoco: A Full Sensor Suite Dataset for Mapping and Localization in Urban Scenes*. ICRA, 2020.
10. M. Ramezani et al. *The Newer College Dataset: Handheld LiDAR, Inertial and Vision with Ground Truth*. IROS, 2020.
11. A. I. Mourikis and S. I. Roumeliotis. *A Multi-State Constraint Kalman Filter for Vision-Aided Inertial Navigation*. ICRA, 2007.
12. S. Leutenegger et al. *Keyframe-Based Visual-Inertial Odometry Using Nonlinear Optimization*. IJRR, 2015.
13. M. Bloesch et al. *Robust Visual Inertial Odometry Using a Direct EKF-Based Approach*. IROS, 2015.
14. W. Xu et al. *FAST-LIO: A Fast Robust LiDAR-Inertial Odometry Package by Tightly-Coupled Iterated Kalman Filter*. RA-L, 2022.
15. W. Xu et al. *FAST-LIO2: Fast Direct LiDAR-Inertial Odometry*. IEEE T-RO, 2022.
16. J. Zhang and S. Singh. *Low-Drift and Real-Time LiDAR Odometry and Mapping*. Autonomous Robots, 2017.
17. T. Lupton and S. Sukkarieh. *Visual-Inertial-Aided Navigation for High-Dynamic Motion in Built Environments Without Initial Conditions*. IEEE T-RO, 2012.
18. R. Kümmerle et al. *g2o: A General Framework for Graph Optimization*. ICRA, 2011.
19. M. Kaess et al. *iSAM2: Incremental Smoothing and Mapping Using the Bayes Tree*. IJRR, 2012.
20. F. Dellaert and M. Kaess. *Factor Graphs for Robot Perception*. Foundations and Trends in Robotics, 2017.
21. G. Grisetti et al. *A Tutorial on Graph-Based SLAM*. IEEE Intelligent Transportation Systems Magazine, 2010.
22. T. Schneider et al. *maplab: An Open Framework for Research in Visual-Inertial Mapping and Localization*. RA-L, 2018.
23. A. Martinelli. *Closed-Form Solution of Visual-Inertial Structure from Motion*. IJCV, 2014.
24. J. Kaiser et al. *Simultaneous State Initialization and Gyroscope Bias Calibration in Visual Inertial Aided Navigation*. RA-L, 2017.
25. L. Carlone et al. *Initialization Techniques for 3D SLAM: A Survey on Rotation Estimation and Its Use in Pose Graph Optimization*. ICRA, 2015.
26. J. Zhang, M. Kaess, and S. Singh. *On Degeneracy of Optimization-Based State Estimation Problems*. ICRA, 2016.
27. J. A. Hesch et al. *Camera-IMU-Based Localization: Observability Analysis and Consistency Improvement*. IJRR, 2014.
28. A. Veicht et al. *GeoCalib: Learning Single-image Calibration with Geometric Optimization*. arXiv:2409.06704, 2024.
29. B. R. N. Kani and N. Snavely. *G3T Up!: Gravity Aligned Coordinate Frames Simplify Pointmap Processing*. arXiv:2605.27372, 2026.
