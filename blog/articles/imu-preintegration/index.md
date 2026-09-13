---
title: "IMU 预积分详解：原理、推导与 C++/Eigen 实现"
date: 2026-09-13
tags: [IMU, Preintegration, ESKF, VIO, SLAM, Factor Graph, Eigen]
excerpt: "从预积分要解决的计算问题出发，详细推导旋转、速度、位置增量、中值积分、bias Jacobian、协方差传播和因子残差，并给出可直接编译运行的 C++/Eigen 示例。"
draft: false
---

# IMU 预积分详解：原理、推导与 C++/Eigen 实现

> 这是一篇系统介绍 IMU 预积分的专题文章。文章从“为什么要把高频积分从优化循环中提取出来”开始，逐步推导预积分增量、中值积分、bias Jacobian、协方差和 IMU 因子；ESKF 只作为误差状态和局部线性化的关联背景出现。

## 摘要：预积分究竟在解决什么问题

在视觉惯性里程计（VIO）或激光惯性里程计（LIO）中，IMU 的频率通常远高于相机和 LiDAR。两个关键帧之间可能有几十甚至几百个 IMU 样本。假设关键帧状态是

$$
\mathbf x_i=(\mathbf R_i,\mathbf p_i,\mathbf v_i,\mathbf b_{g_i},\mathbf b_{a_i}),
$$

如果每次非线性优化都从状态 $i$ 开始，把这一段原始 IMU 重新积分到状态 $j$，优化一次就要重复遍历同一批高频数据。滑动窗口中有很多相邻关键帧，这个代价会迅速变大。

预积分的核心想法可以先用一句话概括：

> **把关键帧 $i$ 到 $j$ 之间的大量 IMU 样本，压缩成一个在关键帧 $i$ 局部坐标系中表达的相对运动测量；优化过程中只用 bias Jacobian 对小的 bias 改变量做一阶修正。**

最后保存的不是一条完整轨迹，而是

$$
\Delta\mathbf R_{ij},\qquad
\Delta\mathbf v_{ij},\qquad
\Delta\mathbf p_{ij},
$$

以及它们对 gyro bias、accelerometer bias 的 Jacobian 和不确定性。

本文不把公式当作需要背诵的矩阵，而是沿着下面的逻辑走完一遍：

1. 先解释普通 IMU 积分为什么不适合直接放进优化；
2. 固定坐标系、旋转方向、误差和噪声约定；
3. 从连续时间运动方程推导相对旋转、相对速度和相对位置；
4. 离散化，得到代码中真正递推的三个增量；
5. 推导 bias Jacobian，说明为什么可以避免重新积分；
6. 推导误差状态和协方差传播；
7. 把预积分量写成 IMU 因子残差并接入 Gauss--Newton/LM 优化；
8. 给出可编译运行的 C++/Eigen 示例。

如果你还不熟悉本文中的误差状态、右侧姿态扰动和噪声密度，可以先阅读：

- [ESKF（误差状态卡尔曼滤波）入门：从状态预测到误差注入](../ekf-again/index.html)
- [ESKF 误差动力学：从 IMU 模型推导 F 和 G](../eskf-error-dynamics/index.html)
- [ESKF 观测更新：从观测模型推导 H 矩阵](../eskf-observation-h/index.html)
- [IMU 噪声参数：噪声密度、角度随机游走、速度随机游走与零偏不稳定性](../imu-noise-allan-variance/index.html)
- [IMU 零偏可观性：静止、运动与姿态激励](../imu-bias-estimation/index.html)

---

## 1. 先建立直觉：为什么不能把每个 IMU 样本都放进优化

### 1.1 普通积分做了什么

IMU 给出角速度和比力。给定初始姿态、速度、位置以及一串测量，可以按照运动方程逐样本传播：

$$
\mathbf R_{k+1}=\mathbf R_k\operatorname{Exp}
\left((\tilde{\boldsymbol\omega}_k-\mathbf b_{g,k})\Delta t_k\right),
$$

$$
\mathbf v_{k+1}=\mathbf v_k+
\left(\mathbf g+\mathbf R_k(\tilde{\mathbf a}_k-\mathbf b_{a,k})\right)\Delta t_k,
$$

$$
\mathbf p_{k+1}=\mathbf p_k+\mathbf v_k\Delta t_k+
\frac12\mathbf R_k(\tilde{\mathbf a}_k-\mathbf b_{a,k})\Delta t_k^2.
$$

这就是惯性导航的基本积分。

### 1.2 优化时的问题

在非线性优化中，状态会不断变化：

- 姿态会变化；
- 关键帧速度和位置会变化；
- gyro bias 和 accelerometer bias 会变化；
- 重力、时间偏移、外参甚至尺度也可能变化。

如果把每一条 IMU 测量都当成优化图中的一个节点，图会非常大；如果每一次 bias 改动都从头积分，又会重复做大量相同工作。

预积分利用了一个事实：

> 从关键帧 $i$ 到 $j$ 的相对运动，可以先在一个固定的局部坐标系中计算；全局的 $\mathbf R_i$、$\mathbf p_i$、$\mathbf v_i$ 和重力在优化时再通过残差公式加入。

因此，预积分不是“忽略 IMU”，也不是“只取两个端点的 IMU”。它是把中间的高频测量进行一次有统计意义的压缩：保存均值结构、bias 敏感性和噪声协方差。

### 1.3 它和 ESKF 有什么关系

ESKF 维护的是当前状态附近的误差协方差，使用

$$
\delta\mathbf x_{k+1}=\mathbf F_k\delta\mathbf x_k+\mathbf G_k\mathbf n_k.
$$

预积分也在做局部线性化，只是它的目标不同：它不直接把当前全局状态向前滤波，而是在关键帧区间内递推

- 相对旋转、速度、位置增量；
- 增量对 bias 的 Jacobian；
- 增量噪声的协方差。

所以可以这样理解：

> **ESKF 把 IMU 用来传播“当前状态的不确定性”；预积分把 IMU 压缩成“两个关键帧之间的约束”。两者共享测量模型、李群误差和局部 Jacobian。**

### 1.4 先回答：IMU 预积分是 ESKF 吗

严格来说，**IMU 预积分既不是 ESKF，也不是一个完整的优化器**。它是一种对高频 IMU 测量进行压缩和建模的方法。它把关键帧 $i$ 到关键帧 $j$ 之间的很多原始测量，整理成一个可以反复使用的相对运动测量及其不确定性。

它通常服务于关键帧优化或因子图。典型的信息流是：

$$
\text{原始 IMU}_{i\rightarrow j}
\xrightarrow{\text{预积分}}
\left(\Delta\mathbf R_{ij},\Delta\mathbf v_{ij},\Delta\mathbf p_{ij},\mathbf\Sigma_{ij}\right)
\xrightarrow{\text{构造}}
\text{IMU 因子}
\xrightarrow{\text{优化}}
\mathbf x_i,\mathbf x_j.
$$

其中 $\mathbf\Sigma_{ij}$ 表示预积分量的不确定性。

ESKF 的典型信息流则是：

$$
\left(\hat{\mathbf x}_k,\mathbf P_k\right)
\xrightarrow{\text{IMU 传播}}
\left(\hat{\mathbf x}_{k+1}^-,\mathbf P_{k+1}^-\right)
\xrightarrow{\text{外部观测}}
\left(\hat{\mathbf x}_{k+1}^+,\mathbf P_{k+1}^+\right).
$$

ESKF 维护当前时刻的一份名义状态和协方差，观测到来后直接用 Kalman 更新修正当前状态；预积分优化则维护多个关键帧状态，把关键帧之间的 IMU 信息作为因子，和视觉、LiDAR、回环等残差一起反复求解。

因此，三者的关系应该这样说：

- **预积分**：压缩关键帧之间 IMU 信息的测量建模方法；
- **ESKF**：在线递推状态和误差协方差的估计器；
- **因子图优化**：组织多个状态和多个约束，并通过非线性最小二乘求解的估计框架。

预积分最常见的使用场景是因子图或滑动窗口优化，例如 VINS、OKVIS 和 GTSAM 中的 IMU factor。理论上，预积分得到的相对测量也可以被其他估计器使用，但本文重点讨论的是“预积分 + 关键帧优化”这条主线，而不是把它当作 ESKF 的另一种名称。

### 1.5 端点与状态节点

本文用“端点”表示预积分区间两侧的状态节点。设区间起点和终点的时间分别为 $t_i$ 和 $t_j$，对应的状态节点记为 $i$ 和 $j$；后文中的“起点端点”和“终点端点”分别指这两个节点。

一个典型的关键帧状态写成

$$
\mathbf x_k
=\left(\mathbf R_k,\mathbf p_k,\mathbf v_k,
\mathbf b_{g_k},\mathbf b_{a_k}\right).
$$

其中：

- $\mathbf R_k$ 是关键帧时刻的姿态；
- $\mathbf p_k$ 是关键帧位置；
- $\mathbf v_k$ 是关键帧速度；
- $\mathbf b_{g_k}$ 和 $\mathbf b_{a_k}$ 是该时刻的 gyro bias 与 accelerometer bias。

预积分因子连接这两个端点状态：

$$
\mathbf x_i
\xleftrightarrow[\text{IMU 预积分因子}]{t_i\rightarrow t_j}
\mathbf x_j.
$$

### 1.6 端点状态从哪里来

这里还需要区分“端点状态的来源”和“端点状态在优化中的角色”。在关键帧优化中，$\mathbf x_i$ 和 $\mathbf x_j$ 最终是优化器维护的状态变量，不属于某一个传感器。不同传感器可以为它们提供初值、绝对约束或相对约束：

| 信息来源 | 能够提供的典型信息 | 在系统中的作用 |
|---|---|---|
| 视觉 | 重投影约束、相对姿态、相对平移方向 | 约束关键帧之间的几何关系，单目时可能存在尺度问题 |
| LiDAR | 点云配准得到的相对位姿、几何残差 | 提供较强的相对位姿和结构约束 |
| 轮速计 | 车体前向速度、平面运动或轮里程 | 约束速度、平面位移和运动学模型 |
| GNSS | 世界系位置，或位置/速度信息 | 提供绝对位置和尺度参考 |
| ESKF | 当前时刻的状态预测和协方差 | 可作为关键帧初值，或作为先验信息进入优化 |
| IMU | 高频角速度和比力 | 通过预积分连接相邻端点，提供动力学约束 |

例如，一个视觉惯性系统可以先用 ESKF 或视觉里程计给出关键帧初值，再把 IMU 预积分因子和视觉重投影因子一起优化；一个 LiDAR 惯性系统可以用点云配准提供端点的相对位姿初值，再用 IMU 因子约束高速运动和短时姿态变化；带 GNSS 的系统还可以把 GNSS 位置因子接到关键帧位置上。

因此，不能简单地说“端点状态来自视觉”或“端点状态来自 IMU”。更准确的说法是：

> **端点状态是待估计的变量；各个传感器通过不同的因子共同约束这些变量。IMU 预积分提供的是端点之间的相对动力学约束。**

端点也不一定只能是相邻的视觉帧。系统可以根据需要选择：

- 相邻关键帧之间的短区间；
- 滑动窗口中的非相邻状态；
- 回环两端的状态；
- GNSS、LiDAR 或其他传感器时间戳对应的状态节点。

只要能够确定区间 $[t_i,t_j]$，并把这段时间内的 IMU 样本归属到该区间，就可以构造一个预积分测量。端点之间的时间间隔越长，预积分包含的 IMU 信息越多，但 bias 线性化距离和噪声累积也可能更大。

### 1.7 残差到底是什么：两种相对运动的比较

理解预积分因子，最重要的是先明确残差不是“某个状态变量本身的误差”，而是**同一个相对运动由两种信息来源计算出来之后，它们之间的不一致**。

在两个端点 $i$ 和 $j$ 之间，有两条路线可以计算相对运动。

**第一条路线：使用当前待优化的端点状态。** 给定优化器当前的

$$
\mathbf x_i=(\mathbf R_i,\mathbf p_i,\mathbf v_i,\mathbf b_{g_i},\mathbf b_{a_i}),
$$

和

$$
\mathbf x_j=(\mathbf R_j,\mathbf p_j,\mathbf v_j,\mathbf b_{g_j},\mathbf b_{a_j}),
$$

可以计算端点状态所暗示的相对运动：

$$
\Delta\mathbf R_{ij}^{\mathrm{state}}
=\mathbf R_i^{\top}\mathbf R_j,
$$

$$
\Delta\mathbf v_{ij}^{\mathrm{state}}
=\mathbf R_i^{\top}
\left(\mathbf v_j-\mathbf v_i-\mathbf g\Delta t_{ij}\right),
$$

$$
\Delta\mathbf p_{ij}^{\mathrm{state}}
=\mathbf R_i^{\top}
\left(\mathbf p_j-\mathbf p_i-\mathbf v_i\Delta t_{ij}
-\frac12\mathbf g\Delta t_{ij}^2\right).
$$

**第二条路线：使用已经预积分的 IMU 测量。** 原始 IMU 在参考 bias 下形成

$$
\Delta\mathbf R_{ij}^{\mathrm{imu}},\qquad
\Delta\mathbf v_{ij}^{\mathrm{imu}},\qquad
\Delta\mathbf p_{ij}^{\mathrm{imu}},
$$

当前端点 bias 偏离参考 bias 时，再用 bias Jacobian 得到修正后的测量。它们是“IMU 认为这段时间发生了什么”。

于是残差就是这两种相对运动的差：

$$
\text{残差}
=\text{端点状态暗示的相对运动}
-\text{IMU 预积分测量}.
$$

旋转不能直接做普通减法，所以使用对数映射；速度和位置可以在关键帧 $i$ 的局部坐标系中直接相减：

$$
\mathbf r_{R,ij}
=\operatorname{Log}\left(
\left(\Delta\mathbf R_{ij}^{\mathrm{imu}}\right)^{\top}
\Delta\mathbf R_{ij}^{\mathrm{state}}
\right),
$$

$$
\mathbf r_{v,ij}
=\Delta\mathbf v_{ij}^{\mathrm{state}}
-\Delta\mathbf v_{ij}^{\mathrm{imu}},
$$

$$
\mathbf r_{p,ij}
=\Delta\mathbf p_{ij}^{\mathrm{state}}
-\Delta\mathbf p_{ij}^{\mathrm{imu}}.
$$

当端点状态和 IMU 测量完全一致时，三类残差都应接近零。优化器做的事情，就是不断调整关键帧状态，使这些残差与视觉、LiDAR、先验等其他残差同时尽可能小。

这里还要区分几个容易都被叫作“误差”的对象：

| 名称 | 含义 | 所在位置 |
|---|---|---|
| IMU 测量噪声 | 原始 gyro/accelerometer 偏离理想测量的随机量 | 测量模型 |
| 预积分误差 | 预积分增量相对其理想值的不确定性 | 协方差 $\mathbf\Sigma_{ij}$ |
| 因子残差 | 端点状态预测和 IMU 预积分测量之间的不一致 | $\mathbf r_{ij}$ |
| 优化增量 | 为减小残差而对关键帧状态施加的局部修正 | $\delta\mathbf x$ |

所以，本文后面出现的 $\mathbf r_{R,ij}$、$\mathbf r_{v,ij}$ 和 $\mathbf r_{p,ij}$ 是**因子残差**；它们不是 ESKF 中的 15 维误差状态 $\delta\mathbf x$。二者都会使用局部线性化，但含义和维度可能不同：残差属于约束输出空间，优化增量属于待更新的状态空间。

---

## 2. 统一符号：先消灭最容易发生的坐标系错误

下面所有公式都使用同一套约定。这一点比某个单独的公式更重要。

### 2.1 坐标系和旋转矩阵

世界坐标系记为 $W$，IMU 机体系记为 $B$。姿态矩阵

$$
\mathbf R_{WB}
$$

表示从机体系到世界系：

$$
\mathbf q_W=\mathbf R_{WB}\mathbf q_B,
\qquad
\mathbf q_B=\mathbf R_{WB}^{\top}\mathbf q_W.
$$

关键帧 $i$ 时刻的姿态、位置和速度写为

$$
\mathbf R_i=\mathbf R_{WB}(t_i),\qquad
\mathbf p_i=\mathbf p_W(t_i),\qquad
\mathbf v_i=\mathbf v_W(t_i).
$$

重力向量 $\mathbf g$ 在世界坐标系中表达，例如世界系 $+Z$ 向上时

$$
\mathbf g=\begin{bmatrix}0\\0\\-9.81\end{bmatrix}\ \mathrm{m/s^2}.
$$

### 2.2 叉乘矩阵和指数映射

对向量 $\mathbf u=[u_x,u_y,u_z]^\top$，定义

$$
[\mathbf u]_\times=
\begin{bmatrix}
0&-u_z&u_y\\
u_z&0&-u_x\\
-u_y&u_x&0
\end{bmatrix},
$$

使得

$$
[\mathbf u]_\times\mathbf v=\mathbf u\times\mathbf v.
$$

旋转向量 $\boldsymbol\phi$ 通过指数映射进入 $SO(3)$：

$$
\operatorname{Exp}(\boldsymbol\phi)
\triangleq\exp([\boldsymbol\phi]_\times).
$$

当 $\|\boldsymbol\phi\|$ 很小时，

$$
\operatorname{Exp}(\boldsymbol\phi)
\approx \mathbf I+[\boldsymbol\phi]_\times.
$$

### 2.3 姿态误差约定

本文沿用 ESKF 系列的右侧扰动：

$$
\mathbf R=\hat{\mathbf R}\operatorname{Exp}(\delta\boldsymbol\theta).
$$

误差 $\delta\boldsymbol\theta$ 在名义机体系中表达。其余变量用加性误差：

$$
\mathbf p=\hat{\mathbf p}+\delta\mathbf p,\quad
\mathbf v=\hat{\mathbf v}+\delta\mathbf v,\quad
\mathbf b_g=\hat{\mathbf b}_g+\delta\mathbf b_g,\quad
\mathbf b_a=\hat{\mathbf b}_a+\delta\mathbf b_a.
$$

预积分本身在关键帧 $i$ 的局部坐标系中计算。为了避免和 ESKF 的“真实状态相对名义状态”混淆，后面会明确区分：

- $\Delta\mathbf R_{ij}$：从 $i$ 到 $j$ 的相对旋转；
- $\Delta\mathbf v_{ij}$：在 $i$ 机体系中表达的相对速度增量；
- $\Delta\mathbf p_{ij}$：在 $i$ 机体系中表达的相对位置增量。

### 2.4 IMU 测量模型和 bias

陀螺仪测量为

$$
\tilde{\boldsymbol\omega}
=\boldsymbol\omega+\mathbf b_g+\mathbf n_g,
$$

加速度计测量为

$$
\tilde{\mathbf a}
=\mathbf R_{WB}^{\top}(\mathbf a_W-\mathbf g)
+\mathbf b_a+\mathbf n_a.
$$

移项后，连续时间运动方程是

$$
\dot{\mathbf R}
=\mathbf R[\tilde{\boldsymbol\omega}-\mathbf b_g-\mathbf n_g]_\times,
$$

$$
\dot{\mathbf v}
=\mathbf g+\mathbf R(\tilde{\mathbf a}-\mathbf b_a-\mathbf n_a),
$$

$$
\dot{\mathbf p}=\mathbf v.
$$

这里的加速度计输出是比力，不是世界系真实线加速度。必须先去 bias，再用姿态旋转到世界系，最后加上重力。

关于 $\mathbf n_g$、$\mathbf n_a$ 的噪声密度、采样频率和单位，可参考 [IMU 噪声参数：噪声密度、角度随机游走、速度随机游走与零偏不稳定性](../imu-noise-allan-variance/index.html)。关于 bias 与重力的耦合，可参考 [IMU 零偏可观性：静止、运动与姿态激励](../imu-bias-estimation/index.html)。

---

## 3. 从连续时间方程得到相对运动公式

设关键帧时间为 $t_i$ 和 $t_j$，总时间间隔为

$$
\Delta t_{ij}=t_j-t_i.
$$

### 3.1 先理解总目标：把高频积分从优化循环中拿出来

在开始推导之前，先不要急着定义 $\Delta\mathbf R$、$\Delta\mathbf v$ 和 $\Delta\mathbf p$。我们先看优化器到底在反复计算什么。

假设关键帧 $i$ 和 $j$ 之间有 $N$ 条 IMU 测量。给定初始状态，普通 IMU 积分需要依次处理这 $N$ 条测量。以速度为例，它包含这样的高频积分：

$$
\int_{t_i}^{t_j}\mathbf R(t)
\left(\tilde{\mathbf a}(t)-\mathbf b_a\right)dt.
$$

这个积分的被积函数中，$\tilde{\mathbf a}(t)$ 和 $\mathbf R(t)$ 随时间变化，所以它确实需要遍历中间的 IMU 数据。

问题在于：在滑动窗口优化中，优化器会反复尝试不同的端点状态。第 $l$ 次迭代可能使用

$$
\left(\mathbf R_i^{(l)},\mathbf p_i^{(l)},\mathbf v_i^{(l)},
\mathbf R_j^{(l)},\mathbf p_j^{(l)},\mathbf v_j^{(l)}\right),
$$

第 $l+1$ 次迭代又会得到另一组状态。原始 IMU 测量没有改变，但如果每次都从 $t_i$ 重新积分到 $t_j$，同一段高频数据就会被重复处理很多遍。

因此我们希望把计算拆成两部分：

$$
\text{端点状态关系}
=\text{高频 IMU 积分结果}
+\text{当前优化状态的组合方式}.
$$

对于速度，目标形式是

$$
\mathbf v_j
=\underbrace{\mathbf v_i+\mathbf g\Delta t_{ij}}_{
\text{由端点状态和重力决定}}
+\underbrace{\mathbf R_i\Delta\mathbf v_{ij}}_{
\text{由局部 IMU 积分决定}}.
$$

对于位置，目标形式是

$$
\mathbf p_j
=\underbrace{\mathbf p_i+\mathbf v_i\Delta t_{ij}
+\frac12\mathbf g\Delta t_{ij}^2}_{
\text{由端点状态和重力决定}}
+\underbrace{\mathbf R_i\Delta\mathbf p_{ij}}_{
\text{由局部 IMU 积分决定}}.
$$

这就是“把积分项提取出来”的整体思想：先把中间时刻的高频信息压缩成局部增量，优化时只重新计算外面的端点状态组合，而不重复遍历全部 IMU 样本。

这里需要把“独立于优化变量”说准确。预积分量并不是和所有优化变量都无关：

- 它不依赖关键帧的全局位置 $\mathbf p_i$、全局速度 $\mathbf v_i$ 和全局姿态 $\mathbf R_i$；
- 它不把重力 $\mathbf g$ 放进局部积分，而是在端点关系中显式使用；
- 但是 bias $\mathbf b_g$、$\mathbf b_a$ 会影响去 bias 后的 IMU 输入，所以会影响积分结果。

工程上选择一个参考 bias

$$
\bar{\mathbf b}_g,\qquad \bar{\mathbf b}_a,
$$

先把高频积分计算并缓存为

$$
\Delta\bar{\mathbf R}_{ij},\qquad
\Delta\bar{\mathbf v}_{ij},\qquad
\Delta\bar{\mathbf p}_{ij},
$$

同时缓存它们对 bias 的 Jacobian。优化器改变 bias 时，在参考点附近使用一阶修正；改变全局位置、速度、姿态或重力时，则直接把新的状态代入端点关系。

如果一次预积分区间有 $N$ 条 IMU、优化器进行 $K$ 次迭代，那么朴素做法大约需要重复 $K$ 次 $N$ 条测量的积分；预积分做法通常只需要一次 $N$ 条测量的预处理，之后每次迭代只计算常数规模的残差和 Jacobian。这里的“常数规模”是指它不再随区间内 IMU 数量 $N$ 增长。

先暂时假设 bias 是已知的、噪声为零。下面就从姿态、速度和位置三个方程中，把这三个可以缓存的局部积分项逐一提取出来。

把姿态方程从 $t_i$ 积分到 $t_j$：

$$
\mathbf R_j=\mathbf R_i\Delta\mathbf R_{ij}.
$$

其中 $\Delta\mathbf R_{ij}$ 只由这段时间内的角速度决定，并且把相对旋转表达在关键帧 $i$ 的局部系中。

### 3.2 先把“局部坐标中的旋转”定义出来

连续时间方程中的 $\mathbf R(t)$ 是从时刻 $t$ 的机体系变到世界系的旋转。它依赖世界坐标系的选择，也依赖关键帧 $i$ 的全局朝向。为了让预积分结果不依赖这个全局朝向，定义

$$
\boxed{
\Delta\mathbf R_i(t)\triangleq\mathbf R_i^{\top}\mathbf R(t).
}
$$

这个定义可以逐字翻译为：

> 先把向量从当前时刻 $t$ 的机体系变到世界系，再从世界系变到关键帧 $i$ 的机体系。

因此 $\Delta\mathbf R_i(t)$ 是“当前姿态相对于起始姿态”的相对旋转。它满足

$$
\Delta\mathbf R_i(t_i)=\mathbf R_i^{\top}\mathbf R_i=\mathbf I.
$$

另一方面，由姿态运动方程

$$
\dot{\mathbf R}(t)
=\mathbf R(t)[\boldsymbol\omega(t)]_\times,
$$

并且 $\mathbf R_i$ 在积分区间内是常量，有

$$
\begin{aligned}
\dot{\Delta\mathbf R}_i(t)
&=\mathbf R_i^{\top}\dot{\mathbf R}(t)\\
&=\mathbf R_i^{\top}\mathbf R(t)[\boldsymbol\omega(t)]_\times\\
&=\Delta\mathbf R_i(t)[\boldsymbol\omega(t)]_\times.
\end{aligned}
$$

所以，$\Delta\mathbf R_i(t)$ 只需要从初值 $\mathbf I$ 开始，按照区间内的角速度积分。它不需要知道 $\mathbf R_i$ 在世界坐标系中的具体数值。

在理想的无噪声情况下，$\boldsymbol\omega(t)=\tilde{\boldsymbol\omega}(t)-\mathbf b_g$，于是终点相对旋转就是

$$
\Delta\mathbf R_{ij}
\triangleq\Delta\mathbf R_i(t_j)
=\mathbf R_i^{\top}\mathbf R_j.
$$

这就是第一条恢复公式的来源：

$$
\boxed{\mathbf R_j=\mathbf R_i\Delta\mathbf R_{ij}.}
$$

右侧的含义是：$\Delta\mathbf R_{ij}$ 先描述从 $i$ 到 $j$ 的局部旋转，$\mathbf R_i$ 再把这个局部结果放回世界坐标系。

### 3.3 速度：先把重力和起始速度拆出来

为了简化书写，令去除加速度计 bias 后的比力为

$$
\mathbf f(t)\triangleq\tilde{\mathbf a}(t)-\mathbf b_a.
$$

速度方程为

$$
\dot{\mathbf v}(t)=\mathbf g+\mathbf R(t)\mathbf f(t).
$$

从 $t_i$ 积分到 $t_j$：

$$
\mathbf v_j-\mathbf v_i
=\int_{t_i}^{t_j}\dot{\mathbf v}(t)dt.
$$

把右侧的导数换成运动方程：

$$
\mathbf v_j-\mathbf v_i
=\int_{t_i}^{t_j}
\left(\mathbf g+\mathbf R(t)\mathbf f(t)\right)dt.
$$

拆成两个积分：

$$
\mathbf v_j-\mathbf v_i
=\int_{t_i}^{t_j}\mathbf g\,dt
+\int_{t_i}^{t_j}\mathbf R(t)\mathbf f(t)dt.
$$

因为重力在世界系中是常量，第一项直接变成

$$
\int_{t_i}^{t_j}\mathbf g\,dt
=\mathbf g(t_j-t_i)
=\mathbf g\Delta t_{ij}.
$$

再处理第二项。由定义

$$
\Delta\mathbf R_i(t)=\mathbf R_i^{\top}\mathbf R(t)
$$

可得

$$
\mathbf R(t)=\mathbf R_i\Delta\mathbf R_i(t).
$$

代回比力积分：

$$
\begin{aligned}
\int_{t_i}^{t_j}\mathbf R(t)\mathbf f(t)dt
&=\int_{t_i}^{t_j}
\mathbf R_i\Delta\mathbf R_i(t)\mathbf f(t)dt\\
&=\mathbf R_i\int_{t_i}^{t_j}
\Delta\mathbf R_i(t)\mathbf f(t)dt.
\end{aligned}
$$

第二个等号使用了一个简单但关键的事实：$\mathbf R_i$ 与积分变量 $t$ 无关，所以可以从积分号外提出。

于是

$$
\mathbf v_j-\mathbf v_i
=\mathbf g\Delta t_{ij}
+\mathbf R_i\int_{t_i}^{t_j}
\Delta\mathbf R_i(t)\mathbf f(t)dt.
$$

现在定义速度预积分量：

$$
\boxed{
\Delta\mathbf v_{ij}
\triangleq
\int_{t_i}^{t_j}
\Delta\mathbf R_i(t)\mathbf f(t)dt.
}
$$

它的单位是 $\mathrm{m/s}$，表达在关键帧 $i$ 的机体系中。代回上式，就得到

$$
\boxed{
\mathbf v_j
=\mathbf v_i+\mathbf g\Delta t_{ij}
+\mathbf R_i\Delta\mathbf v_{ij}.
}
$$

移项并左乘 $\mathbf R_i^{\top}$，也可以反过来从端点状态定义它：

$$
\boxed{
\Delta\mathbf v_{ij}
=\mathbf R_i^{\top}
\left(\mathbf v_j-\mathbf v_i-\mathbf g\Delta t_{ij}\right).
}
$$

这两个式子是同一件事的正向和反向写法：一个用预积分量恢复 $\mathbf v_j$，另一个用端点状态计算理想预积分量。

### 3.4 位置：为什么会出现 $\mathbf v_i\Delta t$ 和 $\frac12\mathbf g\Delta t^2$

位置满足

$$
\dot{\mathbf p}(t)=\mathbf v(t).
$$

从 $t_i$ 到 $t_j$ 积分：

$$
\mathbf p_j-\mathbf p_i
=\int_{t_i}^{t_j}\mathbf v(t)dt.
$$

为了计算这个积分，先把任意中间时刻 $t$ 的速度写成从 $t_i$ 出发的积分形式。由速度方程：

$$
\begin{aligned}
\mathbf v(t)
&=\mathbf v_i+\int_{t_i}^{t}
\left(\mathbf g+\mathbf R(\tau)\mathbf f(\tau)\right)d\tau\\
&=\mathbf v_i+\mathbf g(t-t_i)
+\int_{t_i}^{t}\mathbf R(\tau)\mathbf f(\tau)d\tau.
\end{aligned}
$$

这里使用 $\tau$ 作为内部积分变量，是为了和外层的位置积分变量 $t$ 区分开。

把它代回位置积分：

$$
\begin{aligned}
\mathbf p_j-\mathbf p_i
&=\int_{t_i}^{t_j}\left[
\mathbf v_i+\mathbf g(t-t_i)
+\int_{t_i}^{t}\mathbf R(\tau)\mathbf f(\tau)d\tau
\right]dt.
\end{aligned}
$$

把三部分分别积分。

第一部分是起始速度在整个时间内持续产生的位移：

$$
\int_{t_i}^{t_j}\mathbf v_i dt
=\mathbf v_i\Delta t_{ij}.
$$

第二部分是恒定重力产生的位移：

$$
\begin{aligned}
\int_{t_i}^{t_j}\mathbf g(t-t_i)dt
&=\mathbf g\int_{t_i}^{t_j}(t-t_i)dt\\
&=\frac12\mathbf g\Delta t_{ij}^2.
\end{aligned}
$$

第三部分是比力产生的位移。交换两层积分的顺序后，一个在时刻 $\tau$ 产生的加速度会从 $\tau$ 作用到 $t_j$，因此被积累的时间长度是 $t_j-\tau$：

$$
\begin{aligned}
&\int_{t_i}^{t_j}
\left(\int_{t_i}^{t}\mathbf R(\tau)\mathbf f(\tau)d\tau\right)dt\\
&\qquad=\int_{t_i}^{t_j}(t_j-\tau)
\mathbf R(\tau)\mathbf f(\tau)d\tau.
\end{aligned}
$$

这个交换可以用积分区域直观理解：原来的区域是 $t_i\leq\tau\leq t\leq t_j$。固定一个 $\tau$ 后，$t$ 可以从 $\tau$ 取到 $t_j$，区间长度就是 $t_j-\tau$。

所以位置变化为

$$
\begin{aligned}
\mathbf p_j
&=\mathbf p_i+\mathbf v_i\Delta t_{ij}
+\frac12\mathbf g\Delta t_{ij}^2\\
&\quad+\int_{t_i}^{t_j}(t_j-t)
\mathbf R(t)\mathbf f(t)dt.
\end{aligned}
$$

再次使用 $\mathbf R(t)=\mathbf R_i\Delta\mathbf R_i(t)$：

$$
\begin{aligned}
\int_{t_i}^{t_j}(t_j-t)\mathbf R(t)\mathbf f(t)dt
&=\mathbf R_i\int_{t_i}^{t_j}(t_j-t)
\Delta\mathbf R_i(t)\mathbf f(t)dt.
\end{aligned}
$$

定义位置预积分量：

$$
\boxed{
\Delta\mathbf p_{ij}
\triangleq
\int_{t_i}^{t_j}(t_j-t)
\Delta\mathbf R_i(t)\mathbf f(t)dt.
}
$$

它的单位是 $\mathrm{m}$，同样表达在关键帧 $i$ 的机体系中。于是

$$
\boxed{
\mathbf p_j
=\mathbf p_i+\mathbf v_i\Delta t_{ij}
+\frac12\mathbf g\Delta t_{ij}^2
+\mathbf R_i\Delta\mathbf p_{ij}.
}
$$

移项并左乘 $\mathbf R_i^{\top}$，得到端点状态形式：

$$
\boxed{
\Delta\mathbf p_{ij}
=\mathbf R_i^{\top}
\left(\mathbf p_j-\mathbf p_i-\mathbf v_i\Delta t_{ij}
-\frac12\mathbf g\Delta t_{ij}^2\right).
}
$$

### 3.5 为什么预积分结果可以被复用

前面我们已经完成了两件事：定义了局部 IMU 积分量，并推导了它们与关键帧端点状态之间的关系。现在继续回答预积分最核心的工程问题：**为什么优化器改变端点状态之后，已经算好的积分结果仍然可以继续使用？**

答案是，预积分量只保存关键帧之间由 IMU 比力和角速度产生的局部变化；端点的全局位置、速度、姿态以及重力，则被保留在状态关系的外部。它们不是“不重要”，而是被有意拆开了。下面分别看这些量没有保存什么，以及它们在端点公式中的位置。

**第一，$\Delta\mathbf R_{ij}$ 不需要全局朝向。** 它是 $\mathbf R_i^{\top}\mathbf R_j$，表示相对旋转。把整个世界坐标系绕任意方向重新表达，$\mathbf R_i$ 和 $\mathbf R_j$ 会一起变化，但二者的相对关系由 IMU 角速度决定。

**第二，$\Delta\mathbf v_{ij}$ 不包含 $\mathbf v_i$。** 它只记录比力从 $i$ 到 $j$ 造成的局部速度变化。起始速度在整个区间内造成的位移，已经单独写成 $\mathbf v_i\Delta t_{ij}$；因此位置预积分不需要把起始速度重复积分进去。

**第三，$\Delta\mathbf p_{ij}$ 不包含 $\mathbf p_i$。** 预积分只记录从起始点出发、由 IMU 比力造成的局部位移。整个轨迹平移 $\mathbf p_i\mapsto\mathbf p_i+\mathbf c$ 不会改变任何 IMU 测量，所以不应该进入局部预积分结果。

**第四，重力 $\mathbf g$ 没有被积分进 $\Delta\mathbf v_{ij}$ 和 $\Delta\mathbf p_{ij}$。** 这是主动拆分的结果：重力在世界系中是优化变量或已知常量，分别以 $\mathbf g\Delta t$ 和 $\frac12\mathbf g\Delta t^2$ 的形式留在端点公式中。这样优化重力方向时，不需要重新读取和积分原始 IMU。

**第五，$\mathbf R_i$ 也没有被乘进预积分量。** 预积分量在 $i$ 的局部坐标系中保存；只有在把局部增量放回世界系时，才乘上当前优化状态中的 $\mathbf R_i$。

因此，“预积分结果可以被重复使用”的准确含义是：在原始 IMU 区间、时间间隔和参考 bias 不变的情况下，改变关键帧的全局位置、全局速度、全局姿态或重力时，已经计算好的局部增量仍然可以直接代入端点残差；只有参考 bias 改变过大时，才需要用 Jacobian 修正或重新预积分。

### 3.6 一个简单例子：静止 IMU 时端点状态如何恢复

前面已经推导出了三条端点状态关系。现在用一个最简单的场景检查它们：设备在整个区间内保持静止，姿态不变，速度和位置也不应该发生变化。

假设设备静止，姿态也不变，且 $\mathbf R(t)=\mathbf R_i$。静止时世界系线加速度为零，因此加速度计测到的理想比力为

$$
\mathbf f(t)=\mathbf R_i^{\top}(\mathbf 0-\mathbf g)
=-\mathbf R_i^{\top}\mathbf g.
$$

因为 $\Delta\mathbf R_i(t)=\mathbf I$，速度预积分量为

$$
\begin{aligned}
\Delta\mathbf v_{ij}
&=\int_{t_i}^{t_j}
(-\mathbf R_i^{\top}\mathbf g)dt\\
&=-\mathbf R_i^{\top}\mathbf g\Delta t_{ij}.
\end{aligned}
$$

代回速度恢复公式：

$$
\begin{aligned}
\mathbf v_j
&=\mathbf v_i+\mathbf g\Delta t_{ij}
+\mathbf R_i\left(-\mathbf R_i^{\top}\mathbf g\Delta t_{ij}\right)\\
&=\mathbf v_i+\mathbf g\Delta t_{ij}-\mathbf g\Delta t_{ij}\\
&=\mathbf v_i.
\end{aligned}
$$

速度确实保持不变。位置同理：

$$
\Delta\mathbf p_{ij}
=-\frac12\mathbf R_i^{\top}\mathbf g\Delta t_{ij}^2,
$$

所以

$$
\begin{aligned}
\mathbf p_j
&=\mathbf p_i+\mathbf v_i\Delta t_{ij}
+\frac12\mathbf g\Delta t_{ij}^2
-\frac12\mathbf g\Delta t_{ij}^2\\
&=\mathbf p_i+\mathbf v_i\Delta t_{ij}.
\end{aligned}
$$

当 $\mathbf v_i=0$ 时，$\mathbf p_j=\mathbf p_i$，这正是静止设备应该满足的结果。

这个例子验证了前面的拆分方式：加速度计在静止时测到的是反重力比力，它经过 $\mathbf R_i$ 变回世界系后，与端点关系中显式出现的重力项共同构成零净加速度。因此，重力并没有被忽略，也没有被重复计算；它被分别放在局部 IMU 积分和端点状态关系中，最终恢复出正确的静止状态。

---

## 4. 离散预积分：代码中真正递推的公式

### 4.1 零阶保持和状态初始化

把 $[t_i,t_j]$ 切成 $N$ 个小区间。第 $k$ 个样本的时间间隔为

$$
\Delta t_k=t_{k+1}-t_k.
$$

选定一个线性化 bias

$$
\bar{\mathbf b}_g,\qquad \bar{\mathbf b}_a.
$$

去除这两个 bias 后，定义

$$
\hat{\boldsymbol\omega}_k
=\tilde{\boldsymbol\omega}_k-\bar{\mathbf b}_g,
\qquad
\hat{\mathbf a}_k
=\tilde{\mathbf a}_k-\bar{\mathbf b}_a.
$$

预积分初值为

$$
\Delta\mathbf R_{ii}=\mathbf I,
\qquad
\Delta\mathbf v_{ii}=\mathbf 0,
\qquad
\Delta\mathbf p_{ii}=\mathbf 0.
$$

注意：这里没有把 $\mathbf R_i$ 乘进去。$\Delta\mathbf R$、$\Delta\mathbf v$ 和 $\Delta\mathbf p$ 都是局部量。

### 4.2 从连续积分到离散递推：先用 Euler 方法

前面得到的预积分量仍然写成连续时间积分，例如

$$
\Delta\mathbf v_{ij}
=\int_{t_i}^{t_j}\Delta\mathbf R_i(t)\hat{\mathbf a}(t)dt.
$$

但 IMU 程序拿到的是离散样本：$\tilde{\boldsymbol\omega}_k$、$\tilde{\mathbf a}_k$ 和采样间隔 $\Delta t_k$。因此，接下来必须回答一个数值计算问题：**怎样用有限个采样值近似连续积分？**

最直接的做法是把每个小区间 $[t_k,t_{k+1}]$ 内的测量视作常量，并使用区间起点的值。这就是 Euler 离散化。它的优点是公式简单、每一步的来源清晰，适合先理解预积分递推和后面的 Jacobian。

$$
\boxed{
\Delta\mathbf R_{k+1}
=\Delta\mathbf R_k
\operatorname{Exp}(\hat{\boldsymbol\omega}_k\Delta t_k).
}
$$

速度增量使用当前局部姿态：

$$
\boxed{
\Delta\mathbf v_{k+1}
=\Delta\mathbf v_k
+\Delta\mathbf R_k\hat{\mathbf a}_k\Delta t_k.
}
$$

位置增量为

$$
\boxed{
\Delta\mathbf p_{k+1}
=\Delta\mathbf p_k+\Delta\mathbf v_k\Delta t_k
+\frac12\Delta\mathbf R_k\hat{\mathbf a}_k\Delta t_k^2.
}
$$

最终得到

$$
\Delta\mathbf R_{ij}=\Delta\mathbf R_N,
\quad
\Delta\mathbf v_{ij}=\Delta\mathbf v_N,
\quad
\Delta\mathbf p_{ij}=\Delta\mathbf p_N.
$$

### 4.3 区间内测量发生变化：中值积分

Euler 方法把整个区间的测量都近似成起点值。如果角速度或比力在一个采样间隔内变化明显，这个近似会产生离散化误差。一个自然的改进是：同时使用区间两端的测量，用它们的平均值近似区间中间的测量。这就是中值积分。

下面对一个区间 $[t_k,t_{k+1}]$ 完整推导一次。记

$$
\Delta t_k=t_{k+1}-t_k,
\qquad
t_{k+\frac12}=\frac12(t_k+t_{k+1}).
$$

先定义区间平均的去 bias 测量：

$$
\boldsymbol\omega_k^m
=\frac12(\tilde{\boldsymbol\omega}_k+\tilde{\boldsymbol\omega}_{k+1})
-\bar{\mathbf b}_g,
$$

$$
\mathbf a_k^m
=\frac12(\tilde{\mathbf a}_k+\tilde{\mathbf a}_{k+1})
-\bar{\mathbf b}_a.
$$

上标 $m$ 表示 midpoint。因为 bias 在这个小区间内被视为常量，先平均原始测量再减去参考 bias，与分别去 bias 后再平均是等价的。

#### 第一步：计算区间中点姿态

令

$$
\boldsymbol\phi_k=\boldsymbol\omega_k^m\Delta t_k,
\qquad
\mathbf A_k=\operatorname{Exp}(\boldsymbol\phi_k).
$$

局部姿态在半个时间间隔之后为

$$
\Delta\mathbf R_{k+\frac12}
=\Delta\mathbf R_k
\operatorname{Exp}\left(\frac12\boldsymbol\omega_k^m\Delta t_k\right),
$$

完整走过该区间后为

$$
\Delta\mathbf R_{k+1}=\Delta\mathbf R_k\mathbf A_k.
$$

速度和位置的被积函数依赖区间内的姿态。用半步姿态代表整个区间的姿态，相当于使用中点处的被积函数，因此比始终使用区间起点姿态更准确。

#### 第二步：近似速度积分

连续形式为

$$
\Delta\mathbf v_{k+1}-\Delta\mathbf v_k
=\int_{t_k}^{t_{k+1}}
\Delta\mathbf R_i(t)\mathbf f(t)dt.
$$

中点公式用“区间长度乘以中点被积函数”近似：

$$
\int_{t_k}^{t_{k+1}}
\Delta\mathbf R_i(t)\mathbf f(t)dt
\approx
\Delta\mathbf R_{k+\frac12}\mathbf a_k^m\Delta t_k.
$$

所以

$$
\Delta\mathbf v_{k+1}
=\Delta\mathbf v_k
+\Delta\mathbf R_{k+\frac12}\mathbf a_k^m\Delta t_k,
$$

#### 第三步：近似位置积分

在区间内，局部位置的连续更新为

$$
\Delta\mathbf p_{k+1}-\Delta\mathbf p_k
=\int_{t_k}^{t_{k+1}}\Delta\mathbf v_i(t)dt.
$$

用起点速度加上中点比力造成的近似恒定加速度，得到

$$
\Delta\mathbf p_{k+1}-\Delta\mathbf p_k
\approx\Delta\mathbf v_k\Delta t_k
+\frac12\Delta\mathbf R_{k+\frac12}\mathbf a_k^m\Delta t_k^2.
$$

因此

$$
\Delta\mathbf p_{k+1}
=\Delta\mathbf p_k+\Delta\mathbf v_k\Delta t_k
+\frac12\Delta\mathbf R_{k+\frac12}\mathbf a_k^m\Delta t_k^2.
$$

中值积分的完整递推就是

$$
\Delta\mathbf R_{k+1}
=\Delta\mathbf R_k\mathbf A_k,
$$

$$
\Delta\mathbf v_{k+1}
=\Delta\mathbf v_k
+\Delta\mathbf R_{k+\frac12}\mathbf a_k^m\Delta t_k,
$$

$$
\Delta\mathbf p_{k+1}
=\Delta\mathbf p_k+\Delta\mathbf v_k\Delta t_k
+\frac12\Delta\mathbf R_{k+\frac12}\mathbf a_k^m\Delta t_k^2.
$$

中值积分并没有改变预积分的总体思想：仍然从 $\mathbf I,\mathbf0,\mathbf0$ 开始，只是把每个区间的高频测量用更好的中点近似表示。下面的 bias Jacobian 也必须使用同一个中点姿态，否则均值和敏感性会采用两套不一致的离散模型。

---

## 5. Bias 发生变化时怎么办：用一阶 Jacobian 修正

### 5.1 预积分结果对 bias 的依赖

第 4 节在参考 bias

$$
\bar{\mathbf b}_g,\qquad \bar{\mathbf b}_a
$$

下，把关键帧 $i$ 到 $j$ 之间的高频 IMU 数据预积分并缓存起来。这里的缓存结果对应的是这一组特定的 bias。由于关键帧的 bias 也是非线性优化变量，优化迭代过程中它可能变为

$$
\mathbf b_g=\bar{\mathbf b}_g+\delta\mathbf b_g,
\qquad
\mathbf b_a=\bar{\mathbf b}_a+\delta\mathbf b_a.
$$

因此，原来在 $\bar{\mathbf b}_g,\bar{\mathbf b}_a$ 下计算的 $\Delta\mathbf R$、$\Delta\mathbf v$、$\Delta\mathbf p$，不能直接作为任意 bias 下都成立的固定测量。

不能直接把它们当成完全不变的常量。因为 bias 会进入每一个 IMU 样本的去 bias 操作：

$$
\tilde{\boldsymbol\omega}_k-\mathbf b_g,
\qquad
\tilde{\mathbf a}_k-\mathbf b_a.
$$

gyro bias 的变化会先改变每一步的相对旋转，再通过旋转改变后续所有加速度的方向；accelerometer bias 的变化则直接改变每一步的比力，并经过积分影响速度和位置。因此，新的 bias 一般会改变整段预积分结果。

面对这个问题有两种直接但各有代价的做法：

1. **每次优化迭代都重新积分。** 结果更准确，但每次都要重新遍历 $N$ 条 IMU，预积分节省下来的计算量基本消失。
2. **永远使用参考 bias 下的旧结果。** 计算很快，但当 bias 发生变化时，IMU 因子会使用错误的相对运动测量，进而把 bias 变化误认为位姿、速度或位置误差。

预积分采用第三种做法：**在参考 bias 附近，对预积分结果关于 bias 做一阶 Taylor 展开。** 这样，原始 IMU 的高频积分仍然只做一次；优化器每次改变 bias 时，只需要计算几个 $3\times3$ Jacobian 与 bias 增量的乘法。

### 5.2 线性化 bias 与一阶近似

把预积分结果看成 bias 的函数：

$$
\Delta\mathbf R_{ij}=\Delta\mathbf R_{ij}(\mathbf b_g),
$$

$$
\Delta\mathbf v_{ij}=\Delta\mathbf v_{ij}(\mathbf b_g,\mathbf b_a),
\qquad
\Delta\mathbf p_{ij}=\Delta\mathbf p_{ij}(\mathbf b_g,\mathbf b_a).
$$

在参考 bias $\bar{\mathbf b}_g,\bar{\mathbf b}_a$ 附近，优化器当前的 bias 偏移为 $\delta\mathbf b_g,\delta\mathbf b_a$。对速度和位置这种欧氏空间中的量，普通的一阶 Taylor 展开是

$$
\Delta\mathbf v(\bar{\mathbf b}_g+\delta\mathbf b_g,
\bar{\mathbf b}_a+\delta\mathbf b_a)
\approx\Delta\bar{\mathbf v}
+\frac{\partial\Delta\mathbf v}{\partial\mathbf b_g}
\delta\mathbf b_g
+\frac{\partial\Delta\mathbf v}{\partial\mathbf b_a}
\delta\mathbf b_a,
$$

$$
\Delta\mathbf p(\bar{\mathbf b}_g+\delta\mathbf b_g,
\bar{\mathbf b}_a+\delta\mathbf b_a)
\approx\Delta\bar{\mathbf p}
+\frac{\partial\Delta\mathbf p}{\partial\mathbf b_g}
\delta\mathbf b_g
+\frac{\partial\Delta\mathbf p}{\partial\mathbf b_a}
\delta\mathbf b_a.
$$

旋转属于 $SO(3)$，不能直接做矩阵减法，所以在参考旋转的局部切空间中写成

$$
\Delta\mathbf R(\bar{\mathbf b}_g+\delta\mathbf b_g)
\approx
\Delta\bar{\mathbf R}
\operatorname{Exp}
\left(\mathbf J_{R b_g}\delta\mathbf b_g\right).
$$

为了简化记号，定义五个 bias Jacobian：

$$
\mathbf J_{R b_g}
=\frac{\partial\delta\boldsymbol\theta}{\partial\mathbf b_g},
$$

$$
\mathbf J_{v b_g}
=\frac{\partial\Delta\mathbf v}{\partial\mathbf b_g},
\quad
\mathbf J_{v b_a}
=\frac{\partial\Delta\mathbf v}{\partial\mathbf b_a},
$$

$$
\mathbf J_{p b_g}
=\frac{\partial\Delta\mathbf p}{\partial\mathbf b_g},
\quad
\mathbf J_{p b_a}
=\frac{\partial\Delta\mathbf p}{\partial\mathbf b_a}.
$$

于是上面的 Taylor 展开可以简写为：

$$
\Delta\mathbf R(\mathbf b_g)
\approx\Delta\bar{\mathbf R}
\operatorname{Exp}(\mathbf J_{R b_g}\delta\mathbf b_g),
$$

$$
\Delta\mathbf v(\mathbf b_g,\mathbf b_a)
\approx\Delta\bar{\mathbf v}
+\mathbf J_{v b_g}\delta\mathbf b_g
+\mathbf J_{v b_a}\delta\mathbf b_a,
$$

$$
\Delta\mathbf p(\mathbf b_g,\mathbf b_a)
\approx\Delta\bar{\mathbf p}
+\mathbf J_{p b_g}\delta\mathbf b_g
+\mathbf J_{p b_a}\delta\mathbf b_a.
$$

这些 Jacobian 的作用不是重新估计一套状态，而是告诉我们：**参考 bias 发生一个很小的变化时，已经缓存的预积分测量应该沿哪个方向、变化多少。** 下面从上一节的中值预积分递推出发，逐项推导这五个 Jacobian。

### 5.3 中值积分中的旋转 Jacobian

令整段角增量及其旋转矩阵为

$$
\boldsymbol\phi_k=\boldsymbol\omega_k^m\Delta t_k,
\qquad
\mathbf A_k=\operatorname{Exp}(\boldsymbol\phi_k),
$$

令半段角增量及其旋转矩阵为

$$
\mathbf A_{k+\frac12}
=\operatorname{Exp}\left(\frac12\boldsymbol\phi_k\right).
$$

中值积分同时需要区间终点姿态和区间中点姿态，因此需要两个旋转 bias Jacobian：

$$
\mathbf J_{R b_g,k+1}
=\frac{\partial\delta\boldsymbol\theta_{k+1}}
{\partial\mathbf b_g},
\qquad
\mathbf J_{R b_g,k+\frac12}
=\frac{\partial\delta\boldsymbol\theta_{k+\frac12}}
{\partial\mathbf b_g}.
$$

其中 $\mathbf J_r$ 是 $SO(3)$ 的右 Jacobian：

$$
\mathbf J_r(\boldsymbol\phi)
=\mathbf I
-\frac{1-\cos\theta}{\theta^2}[\boldsymbol\phi]_\times
+\frac{\theta-\sin\theta}{\theta^3}[\boldsymbol\phi]_\times^2,
\qquad \theta=\|\boldsymbol\phi\|.
$$

对完整区间，右侧局部旋转误差满足

$$
\delta\boldsymbol\theta_{k+1}
\approx\mathbf A_k^{\top}\delta\boldsymbol\theta_k
-\mathbf J_r(\boldsymbol\phi_k)\Delta t_k\delta\mathbf b_g.
$$

因此

$$
\boxed{
\mathbf J_{R b_g,k+1}
=\mathbf A_k^{\top}\mathbf J_{R b_g,k}
-\mathbf J_r(\boldsymbol\phi_k)\Delta t_k.
}
$$

速度和位置使用中点姿态，所以同一个推导只走半个时间间隔：

$$
\boxed{
\mathbf J_{R b_g,k+\frac12}
=\mathbf A_{k+\frac12}^{\top}\mathbf J_{R b_g,k}
-\mathbf J_r\left(\frac12\boldsymbol\phi_k\right)
\frac12\Delta t_k.
}
$$

初值是 $\mathbf J_{R b_g,0}=0$。完整步 Jacobian 用于下一段区间的起点；半步 Jacobian 用于当前区间的中点。两个式子的负号都来自去 bias 操作 $\boldsymbol\omega_k^m=\text{测量角速度}-\mathbf b_g$。

### 5.4 中值积分中的速度 Jacobian

中值积分的速度递推是

$$
\Delta\mathbf v_{k+1}
=\Delta\mathbf v_k
+\Delta\mathbf R_{k+\frac12}\mathbf a_k^m\Delta t_k.
$$

对 gyro bias 求导。中点姿态的一阶变化为

$$
\delta\left(\Delta\mathbf R_{k+\frac12}\mathbf a_k^m\right)
=-\Delta\mathbf R_{k+\frac12}[\mathbf a_k^m]_\times
\delta\boldsymbol\theta_{k+\frac12},
$$

并且

$$
\delta\boldsymbol\theta_{k+\frac12}
\approx\mathbf J_{R b_g,k+\frac12}\delta\mathbf b_g.
$$

所以

$$
\boxed{
\mathbf J_{v b_g,k+1}
=\mathbf J_{v b_g,k}
-\Delta\mathbf R_{k+\frac12}[\mathbf a_k^m]_\times
\mathbf J_{R b_g,k+\frac12}\Delta t_k.
}
$$

这里必须使用半步 Jacobian，而不是完整步的 $\mathbf J_{R b_g,k+1}$，因为当前速度更新使用的是中点姿态。

对 accelerometer bias，因为

$$
\frac{\partial\mathbf a_k^m}{\partial\mathbf b_a}=-\mathbf I,
$$

所以

$$
\boxed{
\mathbf J_{v b_a,k+1}
=\mathbf J_{v b_a,k}
-\Delta\mathbf R_{k+\frac12}\Delta t_k.
}
$$

### 5.5 中值积分中的位置 Jacobian

中值位置递推是

$$
\Delta\mathbf p_{k+1}
=\Delta\mathbf p_k+\Delta\mathbf v_k\Delta t_k
+\frac12\Delta\mathbf R_{k+\frac12}\mathbf a_k^m\Delta t_k^2.
$$

因此对 gyro bias 求导：

$$
\boxed{
\mathbf J_{p b_g,k+1}
=\mathbf J_{p b_g,k}
+\mathbf J_{v b_g,k}\Delta t_k
-\frac12\Delta\mathbf R_{k+\frac12}[\mathbf a_k^m]_\times
\mathbf J_{R b_g,k+\frac12}\Delta t_k^2.
}
$$

对 accelerometer bias 求导：

$$
\boxed{
\mathbf J_{p b_a,k+1}
=\mathbf J_{p b_a,k}
+\mathbf J_{v b_a,k}\Delta t_k
-\frac12\Delta\mathbf R_{k+\frac12}\Delta t_k^2.
}
$$

这些式子展示了中值积分下的误差传播路径：gyro bias 先影响半步姿态，再影响中点比力方向，最后影响速度和位置；accelerometer bias 直接进入中点比力，一次积分影响速度，两次积分影响位置。均值使用中点姿态时，Jacobian 也必须使用同一个中点姿态和半步敏感性。

### 5.6 一阶修正什么时候不够

一阶 bias 修正是局部近似。如果

$$
\|\delta\mathbf b_g\|\quad\text{或}\quad\|\delta\mathbf b_a\|
$$

已经很大，或者关键帧间隔很长、旋转很剧烈，那么线性化误差可能明显增大。工程上通常有三种处理方式：

1. 优化若干轮后更新参考 bias，并重新预积分；
2. 在滑动窗口中保持每个预积分因子的线性化点，超过阈值时重新计算；
3. 使用更完整的 manifold preintegration 和高阶 Jacobian。

“预积分不需要重新积分”是一个有条件的说法。准确的说法是：**在参考 bias 附近的小范围优化内，不需要每一轮都重新积分。**

---

## 6. 协方差传播：把 IMU 噪声也压缩进去

仅有 $\Delta\mathbf R$、$\Delta\mathbf v$、$\Delta\mathbf p$ 的均值还不够。优化器还需要知道这条 IMU 约束有多可靠，因此要递推协方差。

### 6.1 预积分误差状态

这里使用 15 维误差状态，排列为

$$
\delta\mathbf x_k^{\mathrm{pre}}
=\begin{bmatrix}
\delta\boldsymbol\theta_k\\
\delta\mathbf v_k\\
\delta\mathbf p_k\\
\delta\mathbf b_{g,k}\\
\delta\mathbf b_{a,k}
\end{bmatrix}.
$$

噪声向量排列为

$$
\mathbf n_k
=\begin{bmatrix}
\mathbf n_{g,k}\\
\mathbf n_{a,k}\\
\mathbf n_{wg,k}\\
\mathbf n_{wa,k}
\end{bmatrix}.
$$

这里的预积分 bias 状态不是说 bias 一定要作为这条 15 维因子的端点测量；它主要是一个方便推导和传播协方差的局部误差坐标。最终 IMU 因子通常从其中取出旋转、速度、位置的 $9\times9$ 协方差，并另外保留 bias Jacobian。

### 6.2 一阶离散误差传播矩阵

令

$$
\mathbf A_k=\operatorname{Exp}(\boldsymbol\omega_k^m\Delta t_k),
\qquad
\mathbf A_{k+\frac12}=\operatorname{Exp}
\left(\frac12\boldsymbol\omega_k^m\Delta t_k\right),
$$

$$
\Delta\mathbf R_{k+\frac12}=\Delta\mathbf R_k\mathbf A_{k+\frac12},
\qquad
\mathbf a_k^m
=\frac12(\tilde{\mathbf a}_k+\tilde{\mathbf a}_{k+1})
-\bar{\mathbf b}_a.
$$

在与中值积分一致的一阶离散近似下，误差传播可以写成

$$
\delta\mathbf x_{k+1}
=\mathbf F_k\delta\mathbf x_k
+\mathbf G_k\mathbf n_k,
$$

其中中点旋转误差的半步传播为

$$
\delta\boldsymbol\theta_{k+\frac12}
\approx
\mathbf A_{k+\frac12}^{\top}\delta\boldsymbol\theta_k
-\mathbf J_r\left(\frac12\boldsymbol\omega_k^m\Delta t_k\right)
\frac12\Delta t_k\delta\mathbf b_g.
$$

把它代入中值速度和位置递推，可以得到

$$
\mathbf F_k=\begin{bmatrix}
\mathbf A_k^\top & 0 & 0 & -\mathbf J_r(\boldsymbol\omega_k^m\Delta t_k)\Delta t_k & 0\\
-\Delta\mathbf R_{k+\frac12}[\mathbf a_k^m]_\times\mathbf A_{k+\frac12}^\top\Delta t_k & \mathbf I & 0 & \frac12\Delta\mathbf R_{k+\frac12}[\mathbf a_k^m]_\times\mathbf J_r(\frac12\boldsymbol\omega_k^m\Delta t_k)\Delta t_k^2 & -\Delta\mathbf R_{k+\frac12}\Delta t_k\\
-\frac12\Delta\mathbf R_{k+\frac12}[\mathbf a_k^m]_\times\mathbf A_{k+\frac12}^\top\Delta t_k^2 & \mathbf I\Delta t_k & \mathbf I & \frac14\Delta\mathbf R_{k+\frac12}[\mathbf a_k^m]_\times\mathbf J_r(\frac12\boldsymbol\omega_k^m\Delta t_k)\Delta t_k^3 & -\frac12\Delta\mathbf R_{k+\frac12}\Delta t_k^2\\
0&0&0&\mathbf I&0\\
0&0&0&0&\mathbf I
\end{bmatrix}.
$$

与 Euler 版本相比，速度和位置行先把起点姿态误差传播到中点，再通过中点比力进入速度和位置；因此出现了 $\mathbf A_{k+\frac12}^{\top}$ 和半步右 Jacobian。

在相同的中值离散约定下，噪声输入矩阵的一阶形式为

$$
\mathbf G_k=\begin{bmatrix}
-\mathbf J_r(\boldsymbol\omega_k^m\Delta t_k)\Delta t_k&0&0&0\\
\frac12\Delta\mathbf R_{k+\frac12}[\mathbf a_k^m]_\times\mathbf J_r(\frac12\boldsymbol\omega_k^m\Delta t_k)\Delta t_k^2&-\Delta\mathbf R_{k+\frac12}\Delta t_k&0&0\\
\frac14\Delta\mathbf R_{k+\frac12}[\mathbf a_k^m]_\times\mathbf J_r(\frac12\boldsymbol\omega_k^m\Delta t_k)\Delta t_k^3&-\frac12\Delta\mathbf R_{k+\frac12}\Delta t_k^2&0&0\\
0&0&\mathbf I&0\\
0&0&0&\mathbf I
\end{bmatrix}.
$$

如果使用连续时间噪声强度矩阵 $\mathbf Q_c$，则一阶离散协方差为

$$
\mathbf Q_{d,k}
\approx\mathbf G_{c,k}\mathbf Q_c\mathbf G_{c,k}^{\top}\Delta t_k,
$$

其中 $\mathbf G_c$ 是不含 $\Delta t$ 的连续噪声输入矩阵。若代码把每个采样周期的噪声直接定义成离散随机量，则也会看到

$$
\mathbf Q_{d,k}=\mathbf G_k\mathbf Q_{\mathrm{sample}}
\mathbf G_k^{\top}.
$$

这两种公式都可能正确，关键是不要混淆“连续噪声密度”和“每个采样的噪声协方差”。

### 6.3 协方差递推

设 $\mathbf P_k$ 是当前预积分误差协方差，则

$$
\boxed{
\mathbf P_{k+1}
=\mathbf F_k\mathbf P_k\mathbf F_k^{\top}+\mathbf Q_{d,k}.
}
$$

初始协方差通常为零矩阵，或者根据起始时刻的不确定性设定。递推后取出前 9 维：

$$
\mathbf\Sigma_{\Delta,ij}
=\mathbf P_{ij}[0:9,0:9],
$$

它对应 $[\delta\boldsymbol\theta,\delta\mathbf v,\delta\mathbf p]$ 的协方差。

实际系统还会考虑 IMU 轴间相关噪声、时间间隔不确定性、测量插值、连续时间精确离散化和 bias 的随机游走。本文示例把每个区间的两端测量压缩成一个有效中点噪声，并采用独立轴噪声和一阶离散化；这样每一个 block 都能与中值递推逐项对应。若严格建模两个端点测量的独立噪声，还需要在 $\mathbf Q_{\mathrm{sample}}$ 中显式加入两次测量平均的协方差。

---

## 7. 从宏观残差到可优化的 IMU 因子

第 1.7 节已经先定义了残差的宏观含义：它比较两种对同一段相对运动的描述。一种来自当前待优化的端点状态，另一种来自原始 IMU 的预积分测量。本节把这个概念落实成可以放进非线性最小二乘的具体因子，并补上参考 bias 修正、bias 随机游走和协方差白化。

先记住一个统一的形式：

$$
\boxed{
\text{IMU 因子残差}
=\text{端点状态预测的相对运动}
-\text{bias 修正后的预积分测量}.
}
$$

残差的目标不是直接“估计一个误差状态”，而是告诉优化器：当前这组关键帧状态是否能够解释这段 IMU 数据。如果残差不为零，优化器就计算残差对关键帧状态的 Jacobian，求出一个状态增量，使下一次迭代更符合 IMU 约束。

### 7.1 参考 bias 与预积分测量

优化器中有关键帧 $i$ 和 $j$ 的状态：

$$
\mathbf x_i=(\mathbf R_i,\mathbf p_i,\mathbf v_i,\mathbf b_{g_i},\mathbf b_{a_i}),
$$

$$
\mathbf x_j=(\mathbf R_j,\mathbf p_j,\mathbf v_j,\mathbf b_{g_j},\mathbf b_{a_j}).
$$

预积分是在参考 bias $\bar{\mathbf b}_{g_i},\bar{\mathbf b}_{a_i}$ 下得到的。定义当前端点 bias 相对线性化点的变化：

$$
\delta\mathbf b_{g_i}=\mathbf b_{g_i}-\bar{\mathbf b}_{g_i},
\qquad
\delta\mathbf b_{a_i}=\mathbf b_{a_i}-\bar{\mathbf b}_{a_i}.
$$

修正后的增量记为

$$
\widehat{\Delta\mathbf R}_{ij}
=\Delta\bar{\mathbf R}_{ij}
\operatorname{Exp}(\mathbf J_{R b_g}^{ij}\delta\mathbf b_{g_i}),
$$

$$
\widehat{\Delta\mathbf v}_{ij}
=\Delta\bar{\mathbf v}_{ij}
+\mathbf J_{v b_g}^{ij}\delta\mathbf b_{g_i}
+\mathbf J_{v b_a}^{ij}\delta\mathbf b_{a_i},
$$

$$
\widehat{\Delta\mathbf p}_{ij}
=\Delta\bar{\mathbf p}_{ij}
+\mathbf J_{p b_g}^{ij}\delta\mathbf b_{g_i}
+\mathbf J_{p b_a}^{ij}\delta\mathbf b_{a_i}.
$$

上式第二行和第三行中，$\Delta\bar{\mathbf v}_{ij}$、$\Delta\bar{\mathbf p}_{ij}$ 是参考 bias 下保存的预积分量。实现时不要把修正后的 bias 再次从原始测量中减一遍。

### 7.2 将两种相对运动写成残差

前面已经分别写过两种相对运动。这里再次列出它们，是为了让后面的残差公式可以逐项对照，而不是重新引入新的定义。

由端点状态得到的相对运动是

$$
\Delta\mathbf R_{ij}^{\mathrm{state}}
=\mathbf R_i^{\top}\mathbf R_j,
$$

$$
\Delta\mathbf v_{ij}^{\mathrm{state}}
=\mathbf R_i^{\top}
\left(\mathbf v_j-\mathbf v_i-\mathbf g\Delta t_{ij}\right),
$$

$$
\Delta\mathbf p_{ij}^{\mathrm{state}}
=\mathbf R_i^{\top}
\left(\mathbf p_j-\mathbf p_i-\mathbf v_i\Delta t_{ij}
-\frac12\mathbf g\Delta t_{ij}^2\right).
$$

由参考 bias 下的 IMU 预积分，并经过本节前面给出的 bias Jacobian 修正，得到

$$
\Delta\mathbf R_{ij}^{\mathrm{imu}}=\widehat{\Delta\mathbf R}_{ij},
\qquad
\Delta\mathbf v_{ij}^{\mathrm{imu}}=\widehat{\Delta\mathbf v}_{ij},
\qquad
\Delta\mathbf p_{ij}^{\mathrm{imu}}=\widehat{\Delta\mathbf p}_{ij}.
$$

因此，残差就是“状态预测”减去“IMU 测量”。

#### 旋转残差

由预测的相对旋转 $\mathbf R_i^{\top}\mathbf R_j$ 与预积分测量比较：

$$
\boxed{
\mathbf r_{R,ij}
=\operatorname{Log}\left(
\widehat{\Delta\mathbf R}_{ij}^{\top}
\mathbf R_i^{\top}\mathbf R_j
\right).
}
$$

其中 $\operatorname{Log}:SO(3)\rightarrow\mathbb R^3$ 是对数映射，返回一个小旋转向量。

#### 速度残差

$$
\boxed{
\mathbf r_{v,ij}
=\mathbf R_i^{\top}
\left(\mathbf v_j-\mathbf v_i-\mathbf g\Delta t_{ij}\right)
-\widehat{\Delta\mathbf v}_{ij}.
}
$$

#### 位置残差

$$
\boxed{
\mathbf r_{p,ij}
=\mathbf R_i^{\top}
\left(\mathbf p_j-\mathbf p_i-\mathbf v_i\Delta t_{ij}
-\frac12\mathbf g\Delta t_{ij}^2\right)
-\widehat{\Delta\mathbf p}_{ij}.
}
$$

这三个残差加起来是 9 维。它们的坐标系也很清楚：旋转、速度和位置增量都在 $i$ 的局部坐标系中表达。

### 7.3 Bias 随机游走残差

如果把每个关键帧 bias 作为优化变量，还需要连接相邻 bias：

$$
\mathbf r_{b_g,ij}=\mathbf b_{g_j}-\mathbf b_{g_i},
\qquad
\mathbf r_{b_a,ij}=\mathbf b_{a_j}-\mathbf b_{a_i}.
$$

它们的协方差来自 bias random walk。于是完整 IMU 因子残差可以写为

$$
\mathbf r_{ij}^{\mathrm{imu}}=\begin{bmatrix}
\mathbf r_{R,ij}\\
\mathbf r_{v,ij}\\
\mathbf r_{p,ij}\\
\mathbf r_{b_g,ij}\\
\mathbf r_{b_a,ij}
\end{bmatrix}.
$$

常见实现会把前 9 维残差和 bias random walk 残差组织成 15 维，也有实现把 bias random walk 单独作为一个 factor。两种组织方式在信息含义上是一致的。

### 7.4 白化和最小二乘目标

若残差协方差为 $\mathbf\Sigma_{ij}$，白化残差为

$$
\tilde{\mathbf r}_{ij}
=\mathbf L_{ij}^{-1}\mathbf r_{ij},
\qquad
\mathbf\Sigma_{ij}=\mathbf L_{ij}\mathbf L_{ij}^{\top}.
$$

也可以写成 Mahalanobis 范数：

$$
\|\mathbf r_{ij}\|^2_{\mathbf\Sigma_{ij}}
=\mathbf r_{ij}^{\top}\mathbf\Sigma_{ij}^{-1}\mathbf r_{ij}.
$$

整个滑动窗口的目标函数是

$$
\min_{\mathcal X}
\sum_{(i,j)\in\mathcal E_{\mathrm{imu}}}
\|\mathbf r_{ij}^{\mathrm{imu}}\|^2_{\mathbf\Sigma_{ij}}
+\sum\|\mathbf r^{\mathrm{vision}}\|^2
+\sum\|\mathbf r^{\mathrm{lidar}}\|^2
+\sum\|\mathbf r^{\mathrm{prior}}\|^2.
$$

预积分只是提供其中的 IMU 因子；它不会单独决定全局位置、yaw、尺度或所有 bias。其他传感器因子、先验和规范固定共同决定优化问题。

---

## 8. 优化器如何使用这些公式

### 8.1 Gauss--Newton 的一次迭代

把所有关键帧状态堆叠成 $\mathcal X$。在当前估计 $\mathcal X^{(l)}$ 附近，对残差线性化：

$$
\mathbf r(\mathcal X^{(l)}\boxplus\delta\mathbf x)
\approx\mathbf r(\mathcal X^{(l)})+\mathbf J\delta\mathbf x.
$$

白化后，最小二乘子问题是

$$
\min_{\delta\mathbf x}
\|\mathbf A\delta\mathbf x-\mathbf b\|^2,
\qquad
\mathbf A=\mathbf W\mathbf J,
\quad
\mathbf b=-\mathbf W\mathbf r.
$$

正规方程为

$$
\mathbf H\delta\mathbf x=\mathbf g,
\qquad
\mathbf H=\mathbf A^{\top}\mathbf A,
\quad
\mathbf g=\mathbf A^{\top}\mathbf b.
$$

解出增量后更新：

$$
\mathbf R_k\leftarrow\mathbf R_k\operatorname{Exp}(\delta\boldsymbol\theta_k),
$$

$$
\mathbf p_k\leftarrow\mathbf p_k+\delta\mathbf p_k,
\quad
\mathbf v_k\leftarrow\mathbf v_k+\delta\mathbf v_k,
$$

$$
\mathbf b_{g_k}\leftarrow\mathbf b_{g_k}+\delta\mathbf b_{g_k},
\quad
\mathbf b_{a_k}\leftarrow\mathbf b_{a_k}+\delta\mathbf b_{a_k}.
$$

姿态不能用普通向量加法更新。这个更新正是前面 ESKF 文章中“误差注入”的优化版本。

### 8.2 为什么通常使用 LM 或 Dogleg

Gauss--Newton 在初值较好、残差接近线性时很有效；如果初值差或问题病态，$\mathbf H$ 可能不稳定。Levenberg--Marquardt 在正规方程中加入阻尼：

$$
(\mathbf H+\lambda\operatorname{diag}(\mathbf H))\delta\mathbf x=\mathbf g.
$$

当步长使目标下降时减小 $\lambda$，否则增大 $\lambda$ 并重试。Ceres、GTSAM 等库已经处理了稀疏线性求解、流形状态、阻尼、鲁棒核和边缘化，工程上通常只需要正确实现 factor 的 residual 和 Jacobian。

### 8.3 实际工程中的优化建议

1. **预积分按关键帧区间缓存。** 原始 IMU 只在新建关键帧或参考 bias 变化过大时重新处理。
2. **使用解析 Jacobian 或可靠自动微分。** 姿态残差的 Log、Exp 和右 Jacobian 是最容易出错的地方。
3. **先检查单位。** gyro 是 rad/s，acc 是 m/s²，bias random walk 和 noise density 不能直接混用。
4. **对协方差使用 Cholesky。** 白化时不要显式求逆，使用 `LLT.solve()`。
5. **处理规范自由度。** 固定首帧位置和 yaw，或者加入合理的先验；否则 Hessian 会有零空间。
6. **对异常视觉/LiDAR 因子使用鲁棒核。** IMU 因子自身通常不应该被随意 robust 化到失去动力学约束。
7. **监控 bias 线性化距离。** 当 $\|\mathbf b-\bar{\mathbf b}\|$ 超过阈值时重新预积分。
8. **边缘化时保留先验。** 滑动窗口删除旧状态后，不能简单丢弃旧 IMU 因子提供的信息。

### 8.4 预积分和 ESKF 的适用场景

ESKF 更像在线递推：每来一条 IMU 就传播一次，每来一个外部观测就更新一次当前状态。预积分因子图更像批量或滑动窗口优化：先把两个关键帧之间的 IMU 压缩，再与多个传感器约束一起反复重线性化。

二者并不是“谁取代谁”：

| 方法 | 状态组织 | IMU 信息的使用方式 | 优点 |
|---|---|---|---|
| ESKF | 当前时刻状态和协方差 | 高频传播、观测到达即更新 | 延迟低、内存小 |
| 预积分优化 | 多个关键帧状态 | 关键帧之间形成 IMU factor | 能反复利用窗口内约束 |
| IESKF | 当前状态的迭代误差更新 | IMU 传播加几何观测迭代 | 适合紧耦合 LiDAR 惯导 |

共同的底层仍是同一件事：测量模型、坐标系、扰动定义和一阶线性化。

---

## 9. 可运行的 C++/Eigen 示例

本文配套源文件位于：[`imu_preintegration.cpp`](./imu_preintegration.cpp)。它只依赖 Eigen，不依赖 ROS、Ceres 或 GTSAM，包含：

- `SO(3)` 指数映射和右 Jacobian；
- 中值 IMU 预积分；
- $\Delta R$、$\Delta v$、$\Delta p$ 的 bias Jacobian；
- 15 维误差协方差传播；
- 一段合成静止 IMU 数据；
- 用两个端点状态计算 9 维 IMU 残差。

### 9.1 编译和运行

Linux 下如果 Eigen 安装在 `/usr/include/eigen3`，可以直接运行：

```bash
g++ -std=c++17 -O2 -Wall -Wextra -pedantic \\
  -I/usr/include/eigen3 \\
  blog/articles/imu-preintegration/imu_preintegration.cpp \\
  -o /tmp/imu_preintegration
/tmp/imu_preintegration
```

也可以在仓库根目录执行。程序会输出预积分时间、相对旋转、速度/位置增量、bias Jacobian 的范数、协方差对角线和一个接近零的自洽残差。

### 9.2 代码与公式的对应关系

代码中的 `delta_R`、`delta_v`、`delta_p` 就是

$$
\Delta\mathbf R,\quad\Delta\mathbf v,\quad\Delta\mathbf p.
$$

`J_R_bg`、`J_v_bg`、`J_v_ba`、`J_p_bg`、`J_p_ba` 对应第 5 节的五个 bias Jacobian。`covariance` 使用

$$
\mathbf P_{k+1}=\mathbf F_k\mathbf P_k\mathbf F_k^\top+\mathbf Q_{d,k}.
$$

示例中的 `Residual()` 使用第 7 节的旋转、速度和位置残差。为了让文件短而易运行，它没有实现完整的稀疏非线性优化器；真实项目可以把这个 residual 和 Jacobian 封装成 Ceres cost function 或 GTSAM factor。代码采用第 4.3 节的中值递推，速度和位置使用半步姿态，bias Jacobian 也使用半步姿态敏感性。程序最后用中心有限差分重新预积分，并输出五个解析 Jacobian 的误差，用于检查符号、坐标系和离散化是否一致。

---

## 10. 常见错误：看到结果不对时先检查什么

### 10.1 把 $R_{WB}$ 和 $R_{BW}$ 写反

本文使用 $\mathbf R_{WB}$ 把 body 向量变到 world。于是速度方程中是

$$
\mathbf g+\mathbf R_{WB}(\tilde{\mathbf a}-\mathbf b_a).
$$

如果代码里的旋转表示相反方向，所有转置位置都要重新检查。

### 10.2 把重力重复加了一次

预积分的 $\Delta\mathbf v$ 和 $\Delta\mathbf p$ 只积分去 bias 后的比力，不在局部增量中加重力。重力在残差端点公式中出现：

$$
\mathbf v_j-\mathbf v_i-\mathbf g\Delta t,
$$

以及

$$
\mathbf p_j-\mathbf p_i-\mathbf v_i\Delta t
-\frac12\mathbf g\Delta t^2.
$$

如果预积分时加了重力，残差时又减重力，就会重复处理。

### 10.3 把加速度计读数当成真实加速度

静止时加速度计通常测到约 $+9.81$ 或 $-9.81$，取决于坐标系和传感器定义。它测的是比力，不是“静止时真实加速度等于 0，所以读数也应为 0”。必须先确认数据手册的符号约定。

### 10.4 bias Jacobian 的符号和坐标系错位

gyro bias 的负号来自 $\tilde\omega-\mathbf b_g$；accelerometer bias 的负号来自 $\tilde a-\mathbf b_a$。同时，$\mathbf J_{R b_g}$ 的列和旋转误差必须处在同一个局部坐标约定中。不能把左扰动论文里的 Jacobian 直接复制到右扰动代码中。

### 10.5 噪声密度直接当成每个采样的标准差

噪声密度的单位通常包含 $\sqrt{\mathrm{Hz}}$。如果采样频率是 $f_s$，简单白噪声离散标准差通常与

$$
\sigma_{\mathrm{sample}}=\text{noise density}\times\sqrt{f_s}
$$

有关，但还要确认数据手册给的是 one-sided 还是 two-sided PSD，以及驱动代码采用的是连续还是离散噪声定义。不要只复制一个数字而忽略单位。

### 10.6 用一个很强的先验掩盖不可观性

重力不能确定 yaw，纯相对 IMU 也不能确定全局平移。加很强的先验可以让数值求解器“看起来收敛”，但不会凭空创造信息。先明确规范自由度，再决定固定首帧还是使用软先验。

### 10.7 只看残差，不看协方差和条件数

一个残差小不代表估计可靠。还需要检查：

- 协方差是否正定；
- Hessian 是否接近奇异；
- bias 是否跑到不合理范围；
- 线性化点是否离当前 bias 太远；
- 不同传感器的单位和权重是否平衡。

---

## 11. 总结：预积分的完整思路

现在可以把 IMU 预积分的完整过程压缩成下面几步。

**第一步：固定约定。** 明确 $R_{WB}$ 的方向、重力方向、姿态扰动在左还是右、误差和噪声的排列。

**第二步：选定线性化 bias。** 在 $\bar b_g,\bar b_a$ 下读取关键帧之间的原始 IMU。

**第三步：递推增量。** 从 $I,0,0$ 开始更新 $\Delta R,\Delta v,\Delta p$。

**第四步：同时递推敏感性。** 更新 $J_{R b_g}$、$J_{v b_g}$、$J_{v b_a}$、$J_{p b_g}$、$J_{p b_a}$。

**第五步：同时传播不确定性。** 使用 $F$、$G$ 或等价的递推式更新 covariance。

**第六步：构造因子。** 用端点状态和预积分测量计算 $r_R,r_v,r_p$，再加 bias random walk 残差。

**第七步：白化并优化。** 将 IMU 因子与视觉、LiDAR、先验等残差放到同一个 Gauss--Newton/LM 问题中。

**第八步：检查线性化距离。** bias 改变太大时重新预积分；边缘化时保留先验；发现残差异常时回到坐标系、重力和单位检查。

最终的核心公式只有三层：

$$
\text{运动积分：}
\quad
\Delta R,\Delta v,\Delta p;
$$

$$
\text{局部敏感性：}
\quad
J_{R b_g},J_{v b_g},J_{v b_a},J_{p b_g},J_{p b_a};
$$

$$
\text{不确定性：}
\quad
P_{k+1}=F_kP_kF_k^\top+Q_{d,k}.
$$

理解这三层，就不必把 VINS、OKVIS、GTSAM 或 LIO 系统中的预积分代码看成一堆互不相关的矩阵。它们只是对同一套运动模型、李群局部坐标和概率传播做了不同的工程组织。

## 参考文献

1. Christian Forster, Luca Carlone, Frank Dellaert, and Davide Scaramuzza, *On-Manifold Preintegration for Real-Time Visual-Inertial Odometry*, IEEE Transactions on Robotics, 2017. <https://arxiv.org/abs/1512.02363>
2. Christian Forster, Luca Carlone, Frank Dellaert, and Davide Scaramuzza, *IMU Preintegration on Manifold for Efficient Visual-Inertial Maximum-a-Posteriori Estimation*, RSS, 2015. <https://www.roboticsproceedings.org/rss11/p06.html>
3. Tong Qin, Peiliang Li, and Shaojie Shen, *VINS-Mono: A Robust and Versatile Monocular Visual-Inertial State Estimator*, IEEE Transactions on Robotics, 2018. <https://arxiv.org/abs/1708.03852>
4. Joan Solà, *Quaternion kinematics for the error-state Kalman filter*, arXiv:1711.02508, 2017. <https://arxiv.org/abs/1711.02508>
5. [ESKF 误差动力学：从 IMU 模型推导 F 和 G](../eskf-error-dynamics/index.html)
6. [IMU 噪声参数：噪声密度、角度随机游走、速度随机游走与零偏不稳定性](../imu-noise-allan-variance/index.html)
