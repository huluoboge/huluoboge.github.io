---
title: "IMU 角速度零偏与加速度零偏：从观测耦合到联合估计"
date: 2026-09-01
tags: [IMU, Bias, Gyroscope, Accelerometer, Observability, Gravity Alignment, SLAM]
excerpt: "静止时陀螺仪零偏可以直接平均，加速度计零偏却与重力投影耦合，姿态误差会等量转化为虚假零偏；运动时陀螺仪需要独立的旋转参考，加速度计需要姿态激励。文章推导两条线的可观测条件与误差量级。"
---

## 摘要

IMU 零偏是惯性估计中最容易被低估、却最难靠单一传感器解决的一类误差。陀螺仪零偏会被积分为姿态漂移；姿态一旦漂移，重力方向就会被错误解释，进一步影响速度、位置和高度。加速度计零偏则与重力投影直接叠加：在静止或弱激励条件下，姿态倾斜和加速度计零偏可以产生几乎相同的观测，导致重力对齐过程把倾斜吸收到一个虚假的零偏中。

本文从统一的 IMU 测量模型出发，分别讨论角速度零偏和加速度零偏的可观性。对于陀螺仪，静止条件给出了真实角速度为零的独立参考，因此零偏可以通过平均直接估计；运动条件下，陀螺仪测量只包含“真实角速度加零偏”，仅凭陀螺仪不存在区分二者的依据，必须引入视觉、LiDAR、回环或其他独立旋转参考。对于加速度计，重力本身提供了绝对方向，但其投影与零偏处在同一个测量通道中；静止时单一姿态无法分离二者，预积分时则通过“机体系固定零偏”和“随姿态变化的重力投影”之间的差异实现分离。

文章进一步推导：共同 yaw 是重力与相对约束共同保留的规范自由度；陀螺仪零偏误差如何累积为姿态误差；加速度计零偏与世界重力倾斜如何形成秩亏；姿态激励如何决定联合估计的条件数；时变随机游走零偏为何会吸收缓慢变化的倾斜。最后给出一套不依赖实验特例的求解方法：以静止段初始化陀螺仪零偏，以外部相对姿态约束陀螺仪，以完整 IMU 预积分因子图联合估计位姿、速度、陀螺仪零偏、加速度计零偏、重力方向和必要的尺度参数，并通过各向异性先验处理不可观方向。

**关键词：** IMU 零偏；陀螺仪零偏；加速度计零偏；重力对齐；预积分；可观性；因子图

## 1. 问题与基本判断

在 SLAM、VIO 和 LIO 中，IMU 常被用来连接相邻时刻的姿态、速度和位置。传感器频率高、短时间内积分稳定，但零偏会把一个很小的恒定误差变成长期漂移。两种零偏的表现不同：

- **角速度零偏** $\mathbf b_g$ 进入姿态积分。若误差近似恒定，经过时间 $T$ 后会产生约 $T\lVert\delta\mathbf b_g\rVert$ 的旋转误差。
- **加速度零偏** $\mathbf b_a$ 进入速度和位置积分，并且会改变对重力方向的判断。倾斜角误差 $\delta\theta$ 在水平距离 $h$ 上产生约 $h\tan\delta\theta\approx h\delta\theta$ 的高度误差。

因此，轨迹出现高度隆起时，原因未必是平移估计本身出错，也可能是 roll/pitch 漂移；而 roll/pitch 漂移又可能源自陀螺仪零偏，也可能来自加速度计零偏与重力方向的错误分配。

两种零偏的核心差别可以先概括如下：

| 问题 | 陀螺仪零偏 $\mathbf b_g$ | 加速度计零偏 $\mathbf b_a$ |
|---|---|---|
| 静止时 | 真实角速度为零，可直接平均 | 测量为重力投影加零偏，不能单靠平均分离 |
| 运动时 | 真实角速度与零偏只以差的形式进入姿态 | 零偏与重力扰动通过机体系投影耦合 |
| 所需参考 | 外部旋转或静止约束 | 姿态变化、重力方向和运动约束 |
| 主要退化 | 没有独立姿态参考时三轴不可观 | 姿态不变或激励不足时水平分量与倾斜混淆 |
| 主要诊断 | 旋转残差随窗口长度的变化 | 拟合零偏的幅值和时间变化是否跟随倾斜 |

下面的分析都采用同一坐标约定，不把两个问题割裂成互不相干的校准步骤。原因很简单：陀螺仪零偏会改变姿态，而姿态又决定重力在机体系中的投影；如果先用错误姿态估计加速度计零偏，两个估计会互相污染。

## 2. 统一测量模型与旋转记号

### 2.1 坐标系和姿态

世界坐标系记为 $W$，机体或 IMU 坐标系记为 $B$。世界系的 $+Z$ 轴向上，姿态旋转 $\mathbf R$ 表示 body-to-world 变换：

$$
\mathbf x_W=\mathbf R\mathbf x_B,
\qquad
\mathbf x_B=\mathbf R^\top\mathbf x_W .
$$

重力加速度和向上的比力方向分别记为

$$
\mathbf g_W=(0,0,-g)^\top,
\qquad
\mathbf u_W=(0,0,g)^\top,
\qquad
g\approx9.81\,\mathrm{m/s^2}.
$$

对任意 $\boldsymbol\phi\in\mathbb R^3$，用 $[\boldsymbol\phi]_\times$ 表示叉乘矩阵：

$$
[\boldsymbol\phi]_\times\mathbf x
=\boldsymbol\phi\times\mathbf x .
$$

旋转的小量通过指数映射进入：

$$
\operatorname{Exp}(\boldsymbol\phi)
=\exp([\boldsymbol\phi]_\times).
$$

当 $\lVert\boldsymbol\phi\rVert$ 足够小时，

$$
\operatorname{Exp}(\boldsymbol\phi)
\approx\mathbf I+[\boldsymbol\phi]_\times,
\qquad
\operatorname{Exp}(\boldsymbol\phi)^\top
\approx\mathbf I-[\boldsymbol\phi]_\times.
$$

还会反复使用恒等式

$$
[\mathbf x]_\times\mathbf y
=-[\mathbf y]_\times\mathbf x .
$$

### 2.2 IMU 测量方程

陀螺仪测量为

$$
\tilde{\boldsymbol\omega}
=\boldsymbol\omega+\mathbf b_g+\boldsymbol\eta_g,
$$

其中 $\boldsymbol\omega$ 是真实角速度，$\mathbf b_g$ 是角速度零偏，$\boldsymbol\eta_g$ 是测量噪声。

加速度计测量为

$$
\tilde{\mathbf a}
=\mathbf R^\top(\mathbf a_W-\mathbf g_W)
+\mathbf b_a+\boldsymbol\eta_a
=\mathbf R^\top\mathbf a_W
+\mathbf R^\top\mathbf u_W
+\mathbf b_a+\boldsymbol\eta_a,
$$

其中 $\mathbf a_W$ 是 IMU 原点在世界系中的线加速度，$\mathbf b_a$ 是加速度计零偏。

这两个方程的结构差异很重要。陀螺仪中，真实角速度与零偏直接相加；加速度计中，除了运动加速度，还存在一个由姿态决定的重力投影。对于零加速度片段，$\mathbf a_W\approx\mathbf0$，于是

$$
\bar{\mathbf a}
\approx\mathbf R^\top\mathbf u_W+\mathbf b_a .
$$

静止平均可以消除噪声，却不能消除 $\mathbf R^\top\mathbf u_W$。这就是为什么陀螺仪和加速度计不能采用完全相同的“静止取均值”策略。

### 2.3 连续时间动力学

姿态动力学为

$$
\dot{\mathbf R}
=\mathbf R[\boldsymbol\omega]_\times
=\mathbf R[\tilde{\boldsymbol\omega}-\mathbf b_g-\boldsymbol\eta_g]_\times .
$$

速度和位置动力学为

$$
\dot{\mathbf p}=\mathbf v,
\qquad
\dot{\mathbf v}=\mathbf g_W+\mathbf R(\tilde{\mathbf a}-\mathbf b_a-\boldsymbol\eta_a).
$$

从这三式可以看到零偏的传播路径：

1. $\mathbf b_g$ 先改变 $\mathbf R$；
2. $\mathbf R$ 再改变重力投影 $\mathbf R^\top\mathbf u_W$ 和世界系比力 $\mathbf R(\tilde{\mathbf a}-\mathbf b_a)$；
3. $\mathbf b_a$ 直接改变加速度，并通过一次、两次积分分别进入速度和位置。

所以，在联合估计中不能把姿态、陀螺仪零偏和加速度计零偏完全串行处理。串行初始化可以作为起点，但最终需要回到同一个动力学模型中联合修正。

## 3. 陀螺仪零偏的可观性

### 3.1 静止时：真实角速度为零

如果 IMU 真正静止，则

$$
\boldsymbol\omega_k=\mathbf0,
$$

陀螺仪测量退化为

$$
\tilde{\boldsymbol\omega}_k
=\mathbf b_g+\boldsymbol\eta_{g,k} .
$$

对 $N$ 个样本求均值：

$$
\hat{\mathbf b}_g
=\frac1N\sum_{k=1}^N\tilde{\boldsymbol\omega}_k
=\mathbf b_g+\frac1N\sum_{k=1}^N\boldsymbol\eta_{g,k} .
$$

若噪声独立、零均值、每个轴的方差为 $\sigma_g^2$，则

$$
\mathbb E[\hat{\mathbf b}_g]=\mathbf b_g,
\qquad
\operatorname{Cov}(\hat{\mathbf b}_g)=\frac{\sigma_g^2}{N}\mathbf I .
$$

因此均值的标准差按 $1/\sqrt N$ 下降。这个估计不需要知道姿态，因为静止条件直接给出了 $\boldsymbol\omega=\mathbf0$。无论设备朝向如何，静止时真实角速度都为零。

该结论的前提有三个：设备确实没有微旋转，窗口内零偏近似恒定，噪声没有强烈的低频相关性。如果存在振动、缓慢转动或随机游走，均值仍然是一个有用的初值，但不再是严格的恒定零偏估计。

### 3.2 运动时：仅凭陀螺仪存在平移对称性

运动时 $\boldsymbol\omega\neq\mathbf0$，窗口均值为

$$
\frac1N\sum_k\tilde{\boldsymbol\omega}_k
=\frac1N\sum_k\boldsymbol\omega_k
+\mathbf b_g+\bar{\boldsymbol\eta}_g .
$$

平均角速度和零偏都以常量形式出现，无法从这个均值中分开。更强的结论来自姿态动力学：陀螺仪数据只通过

$$
\tilde{\boldsymbol\omega}-\mathbf b_g
$$

进入姿态积分。

设 $\mathbf c$ 为任意常向量，同时作变换

$$
\boldsymbol\omega' =\boldsymbol\omega+\mathbf c,
\qquad
\mathbf b_g'=\mathbf b_g-\mathbf c .
$$

则

$$
\boldsymbol\omega'+\mathbf b_g'
=\boldsymbol\omega+\mathbf b_g .
$$

测量不变，而真实角速度与零偏分别改变。因而，仅凭陀螺仪，三维零偏都不可观。这不是噪声过大，而是观测方程本身存在三维对称性。

必须引入一个不依赖同一陀螺仪积分的参考来打破对称性：静止条件把真实角速度钉为零；视觉、LiDAR、外部转台或可靠回环提供姿态变化；联合 IMU—视觉/LiDAR 因子图则通过相对姿态残差约束零偏。

### 3.3 外部旋转参考如何约束零偏

设关键帧区间 $[i,j]$ 上，外部系统给出相对旋转 $\hat{\mathbf R}_{ij}$。以零偏为参数计算 IMU 预积分旋转：

$$
\Delta\mathbf R_{ij}(\mathbf b_g)
=\prod_{k=i}^{j-1}
\operatorname{Exp}\left((\tilde{\boldsymbol\omega}_k-\mathbf b_g)\Delta t_k\right).
$$

构造旋转残差

$$
\mathbf r_{R,ij}
=\operatorname{Log}\left(
\hat{\mathbf R}_{ij}^{\top}
\Delta\mathbf R_{ij}(\mathbf b_g)
\right).
$$

在当前估计 $\bar{\mathbf b}_g$ 附近令

$$
\mathbf b_g=\bar{\mathbf b}_g+\delta\mathbf b_g .
$$

预积分旋转可以写成一阶形式

$$
\Delta\mathbf R_{ij}(\mathbf b_g)
\approx
\Delta\bar{\mathbf R}_{ij}
\operatorname{Exp}\left(\mathbf J_{R,b_g}^{ij}\delta\mathbf b_g\right),
$$

其中 $\mathbf J_{R,b_g}^{ij}\in\mathbb R^{3\times3}$ 是预积分旋转对陀螺仪零偏的 Jacobian。于是

$$
\mathbf r_{R,ij}
\approx\bar{\mathbf r}_{R,ij}
+\mathbf J_{R,b_g}^{ij}\delta\mathbf b_g .
$$

将多个区间堆叠：

$$
\mathbf r_R
\approx\bar{\mathbf r}_R+\mathbf J_R\delta\mathbf b_g .
$$

若

$$
\operatorname{rank}(\mathbf J_R)=3,
$$

则三个轴向的陀螺仪零偏在该批数据中都具备局部可观性。若某一轴的旋转激励不足，$\mathbf J_R$ 在相应方向上的信息变弱，估计会变得病态，即便形式上已经满秩。

### 3.4 零偏误差如何变成姿态误差

先考虑零偏误差近似恒定的简单情形。若估计零偏误差为 $\delta\mathbf b_g$，则校正后的角速度误差约为 $-\delta\mathbf b_g$。在短时间内忽略姿态变化对误差方向的旋转，累计旋转误差满足

$$
\delta\boldsymbol\theta_g(T)
\approx-\int_0^T\delta\mathbf b_g\,dt
=-T\delta\mathbf b_g .
$$

因此

$$
\lVert\delta\boldsymbol\theta_g(T)\rVert
\approx T\lVert\delta\mathbf b_g\rVert .
$$

如果外部旋转参考的误差量级是 $\delta\theta_R$，一个长度为 $T$ 的区间能够约束的零偏误差量级近似为

$$
\lVert\delta\mathbf b_g\rVert
\approx\frac{\delta\theta_R}{T} .
$$

这解释了两个工程事实：窗口太短时，零偏造成的旋转变化小于外部姿态噪声，估计不稳定；在零偏确实恒定的前提下，窗口变长会提高零偏精度。静止是这一关系的极限情形：外部参考告诉我们总旋转为零，因此

$$
\mathbf b_g
\approx\frac1T\operatorname{Log}(\Delta\mathbf R_{\mathrm{IMU}}).
$$

但窗口不能无限变长，因为零偏本身会漂移。

### 3.5 时变陀螺仪零偏与窗口上限

常用的零偏随机游走模型为

$$
\dot{\mathbf b}_g=\mathbf n_{wg},
$$

其中 $\mathbf n_{wg}$ 是白噪声。长度为 $T$ 的窗口内，零偏自身漂移的典型量级约为

$$
\sigma_{wg}\sqrt T .
$$

当窗口继续延长时，固定零偏模型带来的失配会增加。于是窗口长度存在折中：窗口太短，$T\delta\mathbf b_g$ 不足以超过参考噪声；窗口太长，恒定零偏假设失效。

更合理的做法是在关键帧上设置零偏状态 $\mathbf b_g^{(k)}$，并用随机游走因子连接相邻状态：

$$
\mathbf r_{bg,k}
=\mathbf b_g^{(k+1)}-\mathbf b_g^{(k)} .
$$

其加权代价可以写为

$$
\sum_k
\left\|
\mathbf b_g^{(k+1)}-\mathbf b_g^{(k)}
\right\|^2_{\boldsymbol\Sigma_{bg,k}} .
$$

这样既允许真实慢漂移，又避免让整条轨迹共享一个错误的常值零偏。

## 4. 加速度计零偏的可观性

### 4.1 静止时：重力投影与零偏叠加

零加速度时

$$
\bar{\mathbf a}=\mathbf R^\top\mathbf u_W+\mathbf b_a .
$$

若姿态 $\mathbf R$ 由外部高精度设备给出，则可以直接计算

$$
\hat{\mathbf b}_a
=\bar{\mathbf a}-\mathbf R^\top\mathbf u_W .
$$

此时加速度计零偏也可以通过长时间平均提高精度。但如果姿态未知，静止测量自身无法同时确定姿态和零偏。

令姿态发生右侧小扰动

$$
\mathbf R'=\mathbf R\operatorname{Exp}(\delta\boldsymbol\theta),
$$

则

$$
\begin{aligned}
\mathbf R'^{\top}\mathbf u_W
&=\operatorname{Exp}(\delta\boldsymbol\theta)^\top
\mathbf R^\top\mathbf u_W\\
&\approx(\mathbf I-[\delta\boldsymbol\theta]_\times)
\mathbf R^\top\mathbf u_W\\
&=\mathbf R^\top\mathbf u_W
+[\mathbf R^\top\mathbf u_W]_\times
\delta\boldsymbol\theta .
\end{aligned}
$$

同时扰动加速度计零偏，得到

$$
\delta\bar{\mathbf a}
=[\mathbf R^\top\mathbf u_W]_\times
\delta\boldsymbol\theta+
\delta\mathbf b_a .
$$

叉乘矩阵 $[\mathbf R^\top\mathbf u_W]_\times$ 的秩为 2，核空间是重力方向。因此：

- 绕机体系竖直轴的旋转不改变静止加速度计观测，yaw 不在其中；
- 沿 $\mathbf R^\top\mathbf u_W$ 的零偏分量，在重力大小已知时可以直接约束；
- 水平零偏的两个自由度与 roll/pitch 的两个自由度混合在同一个二维观测通道中。

单一姿态下，水平部分只有两个有效观测量，却包含四个未知量。于是“静止平均得不到加速度计零偏”不是平均时间不够，而是结构上存在秩亏。

### 4.2 姿态误差如何转化为虚假加速度计零偏

设有 $S$ 个零加速度片段，真实模型为

$$
\bar{\mathbf a}_s
=\mathbf R_s^\top\mathbf u_W
+\mathbf b_a+\mathbf n_s .
$$

如果实际使用的姿态为

$$
\hat{\mathbf R}_s
=\mathbf R_s\operatorname{Exp}
([\delta\boldsymbol\theta_s]_\times),
$$

则等权静态零偏估计为

$$
\hat{\mathbf b}_a
=\frac1S\sum_{s=1}^S
\left(\bar{\mathbf a}_s-
\hat{\mathbf R}_s^\top\mathbf u_W\right).
$$

代入真实模型并忽略均值后的零均值噪声：

$$
\hat{\mathbf b}_a-\mathbf b_a
=\frac1S\sum_{s=1}^S
\left(\mathbf R_s^\top\mathbf u_W-
\hat{\mathbf R}_s^\top\mathbf u_W\right).
$$

由于

$$
\hat{\mathbf R}_s^\top
\approx(\mathbf I-[\delta\boldsymbol\theta_s]_\times)
\mathbf R_s^\top,
$$

所以

$$
\begin{aligned}
\mathbf R_s^\top\mathbf u_W-
\hat{\mathbf R}_s^\top\mathbf u_W
&\approx[\delta\boldsymbol\theta_s]_\times
\mathbf R_s^\top\mathbf u_W\\
&=-[\mathbf R_s^\top\mathbf u_W]_\times
\delta\boldsymbol\theta_s .
\end{aligned}
$$

最终得到

$$
\boxed{
\hat{\mathbf b}_a-\mathbf b_a
\approx -\frac{1}{S}\sum_{s=1}^S
[\mathbf R_s^\top\mathbf u_W]_\times
\delta\boldsymbol\theta_s
} .
$$

对纯 roll/pitch 小倾斜，虚假零偏的幅值近似为

$$
\lVert\delta\mathbf b_a^{\mathrm{false}}\rVert
\approx g\sin\lVert\delta\boldsymbol\theta\rVert
\approx g\lVert\delta\boldsymbol\theta\rVert .
$$

因此，$1^\circ$ 的倾斜约对应

$$
9.81\sin(1^\circ)\approx0.17\,\mathrm{m/s^2},
$$

$5^\circ$ 的倾斜约对应 $0.86\,\mathrm{m/s^2}$ 的水平虚假零偏。若姿态误差来自同一个系统性外参或世界系倾斜，各静止段的误差投影可能同向，平均并不会消除它。

### 4.3 预积分中的加速度计零偏—重力耦合

静止模型只说明了单个姿态下的退化。一般运动中，重力信息通过预积分的速度和位置残差进入。

关键帧 $i$ 到 $j$ 的区间时长记为 $T_{ij}$。标准传播关系为

$$
\mathbf v_j
=\mathbf v_i+\mathbf g_WT_{ij}
+\mathbf R_i\Delta\mathbf v_{ij},
$$

$$
\mathbf p_j
=\mathbf p_i+\mathbf v_iT_{ij}
+\frac12\mathbf g_WT_{ij}^2
+\mathbf R_i\Delta\mathbf p_{ij} .
$$

预积分增量由去除零偏后的加速度计测量计算。速度残差写成

$$
\mathbf r_{v,ij}
=\mathbf R_i^\top
\left(\mathbf v_j-\mathbf v_i-\mathbf g_WT_{ij}\right)
-\Delta\mathbf v_{ij}(\mathbf b_a).
$$

位置残差为

$$
\mathbf r_{p,ij}
=\mathbf R_i^\top
\left(\mathbf p_j-\mathbf p_i-\mathbf v_iT_{ij}
-\frac12\mathbf g_WT_{ij}^2\right)
-\Delta\mathbf p_{ij}(\mathbf b_a).
$$

对加速度计零偏，离散预积分增量的一阶导数近似为

$$
\frac{\partial\Delta\mathbf v_{ij}}
{\partial\mathbf b_a}
\approx-T_{ij}\mathbf I,
\qquad
\frac{\partial\Delta\mathbf p_{ij}}
{\partial\mathbf b_a}
\approx-\frac12T_{ij}^2\mathbf I .
$$

对世界重力方向扰动 $\delta\mathbf g_W$ 和机体系零偏扰动 $\delta\mathbf b_a$ 同时线性化：

$$
\boxed{
\delta\mathbf r_{v,ij}
=T_{ij}\left(\delta\mathbf b_a
-\mathbf R_i^\top\delta\mathbf g_W\right)
}
$$

以及

$$
\boxed{
\delta\mathbf r_{p,ij}
=\frac12T_{ij}^2\left(\delta\mathbf b_a
-\mathbf R_i^\top\delta\mathbf g_W\right)
} .
$$

旋转残差不直接响应这两个扰动：

$$
\delta\mathbf r_{R,ij}=\mathbf0 .
$$

公式中的结构比系数更重要：每个区间观测到的不是 $\delta\mathbf b_a$ 或 $\delta\mathbf g_W$ 各自，而是

$$
\delta\mathbf b_a-\mathbf R_i^\top\delta\mathbf g_W .
$$

前者是固定在机体系中的常量，后者是一个固定在世界系中的方向经过姿态变换后的投影。姿态变化正是二者能够分离的唯一来源。

### 4.4 可观性的几何条件

先只看水平重力扰动。若存在一个非零水平向量 $\mathbf t$，使得

$$
\mathbf R_i^\top\mathbf t
=\mathbf R_j^\top\mathbf t,
\qquad\forall i,j,
$$

则可以取

$$
\delta\mathbf g_W=\mathbf t,
\qquad
\delta\mathbf b_a=\mathbf R_i^\top\mathbf t .
$$

由于右侧对所有区间都是同一个机体系向量，因此每个区间都有

$$
\delta\mathbf b_a-
\mathbf R_i^\top\delta\mathbf g_W=\mathbf0 .
$$

该水平世界方向就被加速度计零偏完全吸收，无法观测。

反过来，如果不存在这样的非零水平向量，堆叠后的 Jacobian 在水平重力扰动和恒定加速度计零偏方向上满秩，二者局部可分离。因此，严格条件是：

> 加速度计零偏与水平重力扰动可分离，当且仅当不存在一个水平世界方向，其机体系投影在整段姿态轨迹上保持不变。

这句话需要避免两个常见误读。

第一，“姿态发生过变化”不一定意味着两个水平自由度都已经被高精度分离。某一种姿态变化可能只消除一个退化方向，或者虽然满秩但条件数很差。

第二，激励不要求一定有线加速度，也不要求一定有 roll/pitch。纯 yaw 旋转就能改变水平世界向量在机体系中的投影，因此对加速度计零偏—重力分离同样有效。

### 4.5 条件数：可分离与分得好是两件事

考虑平台始终近似水平、主要进行航向变化的情况。将水平零偏和水平重力扰动写成二维向量 $\mathbf b,\mathbf g\in\mathbb R^2$，第 $i$ 个区间的线性观测为

$$
\mathbf y_i=\mathbf b-\mathbf R_i^\top\mathbf g,
$$

其中 $\mathbf R_i$ 是二维航向旋转。设计矩阵为

$$
\mathbf A_i=[\mathbf I_2\; -\mathbf R_i^\top].
$$

将 $N$ 个区间堆叠，得到

$$
\mathbf A^\top\mathbf A
=N\begin{bmatrix}
\mathbf I_2&-\bar{\mathbf R}^\top\\
-\bar{\mathbf R}&\mathbf I_2
\end{bmatrix},
\qquad
\bar{\mathbf R}=\frac1N\sum_{i=1}^N\mathbf R_i .
$$

设 $\sigma_1$ 是 $\bar{\mathbf R}$ 的最大奇异值，则该块矩阵的最大和最小特征值分别与 $1+\sigma_1$、$1-\sigma_1$ 成正比，条件数为

$$
\boxed{
\kappa
=\frac{1+\sigma_1}{1-\sigma_1}
} .
$$

- 姿态完全不变时，$\sigma_1=1$，$\kappa=\infty$，法方程奇异。
- 姿态只有小幅摆动时，$\sigma_1$ 接近 1，问题形式上可分，但噪声被显著放大。
- 若航向覆盖范围增大，平均旋转的模长减小，条件数下降。
- 理想的转向—返回动作使平均旋转接近零，条件数接近 1。

因此应把“是否可观”和“估计是否可靠”分开：前者由零空间决定，后者由最小奇异值或条件数决定。

### 4.6 时变加速度计零偏：慢漂移吸收慢倾斜

若加速度计零偏不是常数，而是在每个区间使用 $\delta\mathbf b_a^{(i)}$，则可以令

$$
\delta\mathbf b_a^{(i)}
=\mathbf R_i^\top\delta\mathbf g_W .
$$

这样速度和位置残差中的耦合项为零。随机游走先验惩罚相邻状态变化：

$$
\mathcal C_{rw}
=\sum_i
\frac{\left\|
\delta\mathbf b_a^{(i+1)}-
\delta\mathbf b_a^{(i)}
\right\|^2}
{\sigma_{rw}^2T_i} .
$$

代入上述吸收序列：

$$
\mathcal C_{rw}
=\sum_i
\frac{\left\|
\mathbf R_{i+1}^\top\delta\mathbf g_W-
\mathbf R_i^\top\delta\mathbf g_W
\right\|^2}
{\sigma_{rw}^2T_i} .
$$

当每一步满足

$$
\left\|
\mathbf R_{i+1}^\top\delta\mathbf g_W-
\mathbf R_i^\top\delta\mathbf g_W
\right\|
\lesssim\sigma_{rw}\sqrt{T_i},
$$

零偏跟踪重力投影的代价不大，倾斜便会被吸收到时变零偏中。此时可分离性不再只是“姿态有没有变化”的问题，而是投影变化速率是否超过零偏漂移速率的问题。

该结论也给出一个实用诊断：如果联合优化得到的加速度计零偏具有与倾斜相同时间尺度的缓慢变化，说明倾斜可能没有被消除，而是被零偏吸收。零偏时间上较平坦是分离成功的必要条件，但不是充分条件；恒定倾斜也可能被恒定零偏吸收，因此还要检查零偏量级和独立传感器规格。

## 5. 角速度零偏如何进入重力对齐

前面的两条理论线并不是彼此独立的。角速度零偏会通过姿态积分改变重力投影，从而把误差传递到加速度计零偏估计和高度。

### 5.1 姿态误差对重力投影的影响

设姿态误差为 $\delta\boldsymbol\theta$，则

$$
\mathbf R' = \mathbf R\operatorname{Exp}(\delta\boldsymbol\theta).
$$

重力在机体系中的投影变化为

$$
\delta(\mathbf R^\top\mathbf u_W)
=[\mathbf R^\top\mathbf u_W]_\times
\delta\boldsymbol\theta .
$$

而姿态误差又主要由陀螺仪零偏误差产生：

$$
\delta\boldsymbol\theta_g(T)
\approx-\int_0^T\delta\mathbf b_g(t)\,dt .
$$

因此，陀螺仪零偏误差进入加速度计观测的链路为

$$
\delta\mathbf b_g
\longrightarrow
\delta\boldsymbol\theta
\longrightarrow
\delta(\mathbf R^\top\mathbf u_W)
\longrightarrow
\delta\mathbf b_a^{\mathrm{false}} .
$$

如果使用错误的姿态计算

$$
\hat{\mathbf b}_a
=\bar{\mathbf a}-\hat{\mathbf R}^\top\mathbf u_W,
$$

则由姿态误差带来的加速度计零偏偏差为

$$
\delta\hat{\mathbf b}_a
\approx
-[\mathbf R^\top\mathbf u_W]_\times
\delta\boldsymbol\theta .
$$

所以，“先把陀螺仪零偏固定，再静态标定加速度计零偏”只有在前一步姿态已经足够可靠时才成立。否则，前一步的姿态误差会被后一步重新命名为加速度计零偏。

### 5.2 为什么相对回环不能单独解决共同倾斜

相对旋转约束只涉及

$$
\mathbf R_i^\top\mathbf R_j .
$$

对所有位姿施加共同世界旋转 $\mathbf Q$：

$$
\mathbf R_k'=\mathbf Q\mathbf R_k,
$$

有

$$
\mathbf R_i'^{\top}\mathbf R_j'
=\mathbf R_i^\top\mathbf Q^\top\mathbf Q\mathbf R_j
=\mathbf R_i^\top\mathbf R_j .
$$

因此相对旋转、相对平移和回环都无法确定共同世界姿态。重力方向则是 unary 约束，直接作用于

$$
\mathbf R_k^\top\mathbf u_W .
$$

在重力方向中，yaw 仍不可观，但 roll/pitch 可以被锚定。相对约束负责保持轨迹内部结构，重力负责补充绝对倾斜，二者缺一不可。

## 6. 联合求解方法

### 6.1 求解目标

输入为已有关键帧轨迹、同步原始 IMU 数据，以及可选的视觉、LiDAR 或回环相对位姿约束。输出为校正后的关键帧位姿和零偏轨迹。

目标不是重新运行 SLAM 前端，而是在已有相对几何结构上补充惯性动力学和重力约束。状态设为

$$
\mathbf x_k
=\left(\mathbf R_k,\mathbf p_k,\mathbf v_k,
\mathbf b_{a,k},\mathbf b_{g,k}\right),
$$

并可选地加入全局重力方向扰动 $\delta\mathbf g_W$ 或加速度计尺度 $s$。若世界系的重力模长已知，则约束

$$
\lVert\mathbf g_W\rVert=g .
$$

### 6.2 预积分量

在关键帧区间内，对原始 IMU 样本计算

$$
\tilde{\boldsymbol\omega}_k^\circ
=\tilde{\boldsymbol\omega}_k-\mathbf b_g,
\qquad
\tilde{\mathbf a}_k^\circ
=\frac{\tilde{\mathbf a}_k-\mathbf b_a}{s} .
$$

预积分旋转为

$$
\Delta\mathbf R_{ij}
=\prod_{k=i}^{j-1}
\operatorname{Exp}
(\tilde{\boldsymbol\omega}_k^\circ\Delta t_k).
$$

速度和位置增量为

$$
\Delta\mathbf v_{ij}
=\sum_k\Delta\mathbf R_{ik}
\tilde{\mathbf a}_k^\circ\Delta t_k,
$$

$$
\Delta\mathbf p_{ij}
=\sum_k\Delta\mathbf v_{ik}\Delta t_k
+\frac12\sum_k\Delta\mathbf R_{ik}
\tilde{\mathbf a}_k^\circ\Delta t_k^2 .
$$

实际实现中，增量不必在每次优化迭代中从头计算；保留对 $\mathbf b_a$、$\mathbf b_g$ 的一阶 Jacobian，即可在当前线性化点附近快速更新：

$$
\Delta\mathbf R_{ij}(\mathbf b_g+\delta\mathbf b_g)
\approx
\Delta\bar{\mathbf R}_{ij}
\operatorname{Exp}
(\mathbf J_{R,b_g}^{ij}\delta\mathbf b_g),
$$

$$
\Delta\mathbf v_{ij}
\approx\Delta\bar{\mathbf v}_{ij}
+\mathbf J_{v,b_a}^{ij}\delta\mathbf b_a
+\mathbf J_{v,b_g}^{ij}\delta\mathbf b_g,
$$

$$
\Delta\mathbf p_{ij}
\approx\Delta\bar{\mathbf p}_{ij}
+\mathbf J_{p,b_a}^{ij}\delta\mathbf b_a
+\mathbf J_{p,b_g}^{ij}\delta\mathbf b_g .
$$

### 6.3 因子残差

旋转残差为

$$
\mathbf r_{R,ij}
=\operatorname{Log}\left(
\Delta\mathbf R_{ij}^{\top}
\mathbf R_i^\top\mathbf R_j
\right).
$$

速度残差为

$$
\mathbf r_{v,ij}
=\mathbf R_i^\top
(\mathbf v_j-\mathbf v_i-\mathbf g_WT_{ij})
-\Delta\mathbf v_{ij} .
$$

位置残差为

$$
\mathbf r_{p,ij}
=\mathbf R_i^\top
\left(\mathbf p_j-\mathbf p_i-\mathbf v_iT_{ij}
-\frac12\mathbf g_WT_{ij}^2\right)
-\Delta\mathbf p_{ij} .
$$

相邻关键帧的相对位姿、视觉或 LiDAR 约束可以作为外部因子。例如给定相对旋转 $\hat{\mathbf R}_{ij}$ 和相对平移 $\hat{\mathbf t}_{ij}$，可加入

$$
\mathbf r_{\mathrm{rel},ij}^{R}
=\operatorname{Log}\left(
\hat{\mathbf R}_{ij}^{\top}
\mathbf R_i^\top\mathbf R_j
\right),
$$

以及相应的平移残差。回环因子只用来约束相对结构，不应被误认为是重力绝对参考。

### 6.4 先验与规范自由度

由于重力不能观测 yaw 和全局纯平移，优化问题必须处理规范自由度。可采用固定首帧的部分状态，或使用软先验。对于后处理重力对齐，推荐各向异性先验：

- roll/pitch 使用较弱先验，让 IMU 重力证据能够改变输入倾斜；
- yaw 使用较强先验或固定输入 yaw，因为重力无法提供 yaw；
- 平移使用较松先验，避免把原有高度隆起强行固定；
- 速度使用动力学和相邻状态约束；
- 零偏使用初值先验与随机游走约束。

联合目标函数可以写成

$$
\begin{aligned}
\mathcal C(\mathbf x)=
&\sum_{(i,j)\in\mathcal I}
\left\|\mathbf r_{ij}^{\mathrm{imu}}\right\|^2_{\boldsymbol\Sigma_{ij}}\\
&+\sum_k
\left\|\mathbf r_k^{\mathrm{pose\ prior}}\right\|^2_{\boldsymbol\Sigma_k^{\mathrm{prior}}}\\
&+\sum_k
\left\|\mathbf b_{a,k+1}-\mathbf b_{a,k}\right\|^2_{\boldsymbol\Sigma_{ba,k}}\\
&+\sum_k
\left\|\mathbf b_{g,k+1}-\mathbf b_{g,k}\right\|^2_{\boldsymbol\Sigma_{bg,k}}\\
&+\sum_{(i,j)\in\mathcal E}
\rho\left(\left\|\mathbf r_{ij}^{\mathrm{rel}}\right\|^2_{\boldsymbol\Sigma_{ij}^{\mathrm{rel}}}\right).
\end{aligned}
$$

其中 $\mathbf r_{ij}^{\mathrm{imu}}$ 包含旋转、速度和位置残差，$\rho$ 可以使用 Cauchy 等鲁棒核抑制错误回环或异常惯性区间。

### 6.5 初始化顺序

初始化顺序应遵循可观性，而不是把所有状态同时从任意值开始。

**第一步：静止估计陀螺仪零偏。** 设备真正静止时，直接平均 $\tilde{\boldsymbol\omega}$。这一步不需要姿态参考，是最可靠的零偏初值。

**第二步：建立初始重力方向。** 对静止加速度计均值使用已知重力模长，得到初始重力锚。此时只把它当作方向和初值，不要在单一姿态上把水平加速度计零偏强行解释出来。

**第三步：引入外部姿态或相对位姿。** 视觉、LiDAR 或已有 SLAM 轨迹提供相对旋转，使运动中的陀螺仪零偏获得约束。没有独立姿态参考时，不能指望陀螺仪自身在任意运动中估计出三轴零偏。

**第四步：使用姿态激励分离加速度计零偏。** 通过转弯、多航向运动或其他姿态变化，使 $\mathbf R_i^\top\delta\mathbf g_W$ 发生变化。姿态变化不足时，先验只能稳定数值，不能凭空创造可观性。

**第五步：联合迭代。** 重新估计姿态会改变重力投影，重新估计零偏又会改变预积分，因此需要在同一个因子图中迭代优化，而不是固定某一方后永久使用。

### 6.6 诊断量

求解后至少检查以下量：

1. **陀螺仪零偏的时间变化：** 是否符合随机游走模型，是否出现与姿态残差同步的突变。
2. **加速度计零偏的幅值：** 是否远超传感器规格。远超规格通常意味着姿态倾斜被吸收进零偏。
3. **加速度计零偏的时间平坦性：** 若零偏缓慢跟随输入 tilt 曲线，说明慢漂移陷阱可能发生。
4. **姿态激励的条件数：** 计算堆叠 Jacobian 的最小奇异值或条件数，而不是只记录“是否转过弯”。
5. **重力模长：** 检查 $\lVert\mathbf g_W\rVert$ 是否维持在物理合理范围；若同时估计尺度，应避免尺度、重力模长和加速度计零偏形成新的退化。
6. **残差分解：** 分别查看旋转、速度、位置和相对几何残差，避免用位置先验掩盖惯性模型错误。

## 7. 采集与工程使用建议

### 7.1 采集阶段

如果任务允许设计运动，建议采用以下顺序：

1. 开始时保持设备稳定数秒，估计陀螺仪零偏和噪声；
2. 完成视觉或其他外部姿态初始化；
3. 进行多航向旋转，最好包含转向—返回动作；
4. 正常运动时保持一定转弯密度，避免整段轨迹只有长距离直行；
5. 结束时再次静止，用于检查陀螺仪零偏是否发生明显漂移。

对加速度计零偏而言，转动不一定要伴随剧烈线加速度。只要姿态改变，固定世界倾斜在机体系中的投影就会改变。对汽车或轮式平台，航向变化通常比 roll/pitch 变化更容易获得，也足以提供水平重力分离信息。

### 7.2 不应采用的简化

以下做法容易产生看似合理、实际上错误的结果：

- 将整段运动加速度计均值直接当成零偏；
- 用单一静止姿态同时估计水平加速度计零偏和 roll/pitch；
- 先用可能含有倾斜漂移的姿态标定加速度计零偏，再把该零偏固定；
- 只使用相对回环，希望回环自动恢复绝对重力方向；
- 为了让优化收敛，把 roll/pitch 设很强的先验，使重力因子无法修正输入姿态；
- 给逐帧零偏过大的随机游走自由度，使零偏能够无代价地追踪重力投影；
- 用完整 SE(3) 对齐评估重力校正，把要测的 roll/pitch 漂移在评估时吸收掉。

### 7.3 在线与离线的取舍

在线滑动窗口估计器需要在有限窗口内完成零偏—姿态分离。早期如果激励不足，相关状态被边缘化后，后续激励难以完全追溯修正。离线全序列优化可以保留完整的姿态激励和原始 IMU 信息，适合已有 SLAM 轨迹的后处理，但代价是计算延迟和更高的状态规模。

无论在线还是离线，信息不足都无法被优化器弥补。姿态始终不变时，加速度计零偏与水平重力倾斜就是结构性不可分；没有外部旋转参考时，运动中的陀螺仪零偏也无法仅靠陀螺仪自身确定。

## 8. 结语

角速度零偏和加速度零偏都叫 bias，但它们的可观性完全不同。

陀螺仪零偏的问题是缺少真实角速度参考。静止时，真实角速度为零，零偏可以直接平均；运动时，测量只包含真实角速度和零偏的和，必须借助外部姿态或相对旋转打破三维对称性。零偏误差以时间积分为姿态误差，短期近似满足

$$
\delta\boldsymbol\theta_g(T)\approx-T\delta\mathbf b_g .
$$

加速度计零偏的问题不是没有重力参考，而是重力投影和零偏叠加在同一个通道中。静止单姿态只能观察二者的组合；在预积分中，观测结构变成

$$
\delta\mathbf b_a-\mathbf R_i^\top\delta\mathbf g_W .
$$

只有当姿态变化使第二项改变，而第一项保持机体系恒定时，二者才可能分离。姿态激励越弱，问题越病态；零偏随机游走越自由，越容易吸收缓慢变化的倾斜。

因此，可靠的 IMU 零偏处理不应是两个互相独立的校准脚本，而应是一个受可观性约束的联合估计问题：静止段提供陀螺仪零偏初值，外部旋转约束建立运动中的角速度参考，完整预积分连接姿态、速度、位置和加速度计零偏，重力约束提供 roll/pitch 的绝对方向，随机游走先验限制零偏随时间的变化，yaw 和全局平移则由相对轨迹约束或规范选择处理。

只要把“零偏是什么”和“什么信息能够区分它”分开，很多看似神秘的高度漂移、姿态慢漂和异常 bias 估计，都可以还原为明确的观测结构问题。



