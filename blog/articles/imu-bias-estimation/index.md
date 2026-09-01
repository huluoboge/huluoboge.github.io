---
title: "IMU 零偏估计：静止平均与运动可观测性"
date: 2026-09-01
tags: [IMU, Bias, Gyroscope, Accelerometer, Observability, SLAM, Gravity Alignment]
excerpt: "陀螺仪零偏静止时直接平均就能估，加速度计零偏却和重力方向缠在一起。到了运动状态，两者都面临可观测性问题：陀螺仪需要独立的旋转参考，加速度计需要姿态激励。"
---

# IMU 零偏估计：静止平均与运动可观测性

做 SLAM 和 VIO 的人都会遇到零偏（bias）问题：陀螺仪明明没转，输出却是 $0.01\ \mathrm{rad/s}$；加速度计明明静止，输出却不指向重力方向。零偏不修，姿态积分会漂，重力对齐会歪，最后轨迹高度整体变形。

这篇文章推导两个问题的答案：零偏在什么条件下可观测、误差多大。一条线是陀螺仪零偏 $b_g$，另一条线是加速度计零偏 $b_a$。结论会不一样：静止时一个能直接平均，另一个不能；运动时一个需要独立的旋转参考，另一个需要姿态激励。

---

## 1. 测量模型与静止估计

### 1.1 陀螺仪：静止时直接平均

陀螺仪的测量模型是

$$
\omega_m = \omega + b_g + n_g
$$

- $\omega$：真实角速度
- $b_g$：零偏，缓慢变化的偏差
- $n_g$：零均值噪声

静止时真实角速度 $\omega = 0$，测量值变成

$$
\omega_m = b_g + n_g
$$

对 $N$ 个采样求平均：

$$
\hat b_g = \frac{1}{N}\sum_{k=1}^{N} \omega_{m,k}
$$

噪声平均后按 $\sigma_{\bar n} = \sigma_n / \sqrt{N}$ 下降。静止 10 秒、100 Hz 采样就是 1000 个样本，噪声压掉 $\sqrt{1000} \approx 32$ 倍。

这个估计的关键前提是 $\omega = 0$：因为真实角速度已知为零，测量中只剩 bias 和噪声，平均自然把噪声滤掉、留下 bias。整个过程不涉及姿态——无论设备朝哪，$\omega = 0$ 都成立。

### 1.2 加速度计：静止时与重力耦合

加速度计的测量模型是

$$
a_m = R^T(g - a^W) + b_a + n_a
$$

其中 $R$ 是姿态，$g$ 是世界系重力向量，$a^W$ 是世界系加速度。静止（或匀速，$a^W \approx 0$）时平均，得到

$$
\bar a \approx R^T g + b_a
$$

平均只能滤掉噪声，得到的是**重力在机体系下的投影 $R^T g$ 加上 bias**。$R^T g$ 和 $b_a$ 通过同一个通道进入测量，不知道姿态 $R$ 就无法把两者分开。这就是与陀螺仪的本质区别：陀螺仪静止时 $\omega = 0$ 是已知的，加速度计静止时 $R^T g$ 是未知的。

姿态误差还会伪装成 bias。设标定使用的姿态带一个小倾斜 $\delta\theta$，即 $\hat R = R\,\operatorname{Exp}([\delta\theta]_\times)$。用 $\hat R$ 去拟合 bias，拟合值会把倾斜吸收进去：

$$
\hat b_a - b_a \approx -R^T [g]_\times \delta\theta, \qquad \|\hat b_a - b_a\| \approx g \sin \|\delta\theta\|
$$

一个 $5^\circ$ 的 roll 漂移产生 $g \sin 5^\circ \approx 0.86\ \mathrm{m/s^2}$ 的虚假 bias——比典型车载 IMU 的真实零偏（约 $0.05\ \mathrm{m/s^2}$ 量级）大一个数量级。这个数值看起来物理上合理，标定流程没有理由怀疑它，于是倾斜被吸收进 bias、原样保留，重力校正静默失败。

> 小结：静止时，陀螺仪零偏 $\hat b_g$ 是纯估计，前提只有 $\omega = 0$；加速度计得到的是 $R^T g + b_a$ 的混合体，而且倾斜会直接污染 bias 估计。

## 2. 运动时：陀螺仪零偏的可观测性

### 2.1 平均为什么在运动时失效

第 1.1 节的估计能用，前提是 $\omega = 0$。运动时 $\omega \neq 0$，对 $N$ 个采样平均得到

$$
\frac{1}{N}\sum_{k=1}^{N}\omega_{m,k}
= \underbrace{\frac{1}{N}\sum_{k=1}^{N}\omega_k}_{\text{平均角速度}}
+ b_g + \frac{1}{N}\sum_{k=1}^{N} n_{g,k}
$$

平均角速度这一项混进来了，而它和 bias 一样是常数，平均无法区分两者。剩下的出路只有姿态信息：用姿态积分把 $\omega$ 从测量里消掉。这正是本节要做的。

### 2.2 姿态动力学：观测只依赖 $\omega_m - b_g$

真实角速度从测量中减去 bias 得到（忽略噪声）：

$$
\omega(t) = \omega_m(t) - b_g(t)
$$

姿态动力学 $\dot R = R[\omega]_\times$ 变成

$$
\dot R = R\,[\omega_m - b_g]_\times
$$

对区间 $[t_i, t_j]$ 积分，假设 $b_g$ 在该区间内为常数：

$$
R_j = R_i \operatorname{Exp}\left(\int_{t_i}^{t_j} (\omega_m(t) - b_g)\, dt\right)
$$

观测到的相对旋转 $\Delta R_{ij} = R_i^T R_j$ 完全由 $\omega_m - b_g$ 决定。

### 2.3 不可观测性：一个对称性论证

由 2.2 的结论——姿态观测 $\Delta R_{ij}$ 完全由 $\omega_m - b_g$ 决定——立即得到：对任意常数向量 $c$，把真实角速度和 bias 同时平移：

$$
(\omega, b_g) \longrightarrow (\omega + c,\ b_g + c)
$$

$\omega_m - b_g$ 不变，于是**每一个姿态观测 $\Delta R_{ij}$ 都不变**。也就是说，陀螺仪数据无法区分「设备真的在转 $\omega$ 且 bias 为 $b_g$」和「设备在转 $\omega + c$ 且 bias 为 $b_g + c$」——存在一个三维的自由度，$\omega$ 和 $b_g$ 沿同一个方向平移时完全不可分辨。

这不是数值精度问题，而是测量结构决定的：**仅凭陀螺仪，$b_g$ 不可观测**。要打破这个对称性，必须有独立的信息把 $\omega$ 或 $R$ 钉住。

### 2.4 独立旋转参考使 bias 可观测

假设外部（视觉、LiDAR、SfM、回环）给出相对旋转 $\hat R_{ij}$，构造残差：

$$
r_R = \operatorname{Log}\left(\hat R_{ij}^{-1}\, \Delta R_{ij}(b_g)\right)
$$

其中 IMU 预积分旋转

$$
\Delta R_{ij}(b_g) = \prod_{k=i}^{j-1} \operatorname{Exp}\left[(\omega_{m,k} - b_g)\Delta t\right]
$$

在标称 bias $\bar b_g$ 附近线性化。预积分旋转对 bias 的一阶近似是

$$
\Delta R_{ij}(b_g) \approx \Delta \bar R_{ij}\, \operatorname{Exp}\left(J_{R,b_g}\,\delta b_g\right), \qquad J_{R,b_g} = \frac{\partial \Delta R_{ij}}{\partial b_g}
$$

残差因此是

$$
r_R \approx r_R^0 + J_{R,b_g}\,\delta b_g
$$

把所有区间堆叠起来做最小二乘：

$$
\min_{\delta b_g}\ \sum_{ij} \left\| r_{R,ij}^0 + J_{R,b_g}^{ij}\,\delta b_g \right\|^2
$$

如果堆叠 Jacobian 满足 $\operatorname{rank}(\mathbf J) = 3$，三个轴的 bias 都进入可观测集合。**外部旋转参考正是打破 2.3 平移对称性的关键：参考越准，bias 越能被估出来。**

### 2.5 误差传播：$\delta b_g \approx \delta\theta_R / T$

外部参考不是完美的，旋转观测误差 $\delta\theta_R$ 会直接传导到 bias。推导：bias 误差 $\delta b_g$ 在窗口 $T$ 内累积的旋转误差，来自 $\Delta R = \operatorname{Exp}(b_g T)$ 对 bias 的一阶展开：

$$
\delta\theta_b \approx T\, \delta b_g
$$

估计时把残差里所有旋转偏差都算到 bias 头上，所以 bias 误差由旋转观测误差除以窗口长度决定：

$$
\delta b_g \approx \frac{\delta\theta_R}{T}
$$

代入数字，外部旋转误差 $0.1^\circ = 1.745\times10^{-3}\ \mathrm{rad}$：

- 窗口 $T = 10\ \mathrm{s}$：$\delta b_g \approx 1.7\times10^{-4}\ \mathrm{rad/s} \approx 0.01^\circ/\mathrm{s}$
- 窗口 $T = 100\ \mathrm{s}$：$\delta b_g \approx 0.001^\circ/\mathrm{s}$

在「bias 是常数」的假设下，**长时间窗口 + 高精度旋转约束**最有利。这个公式的极限情形是：若窗口内真实无旋转，外部参考给出 $\Delta \hat R = I$，则 $\operatorname{Log}(\Delta R_{\text{IMU}}) \approx b_g T$，直接得到 $b_g \approx \operatorname{Log}(\Delta R_{\text{IMU}})/T$——静止/低动态反而是 bias 最容易观测的情形。

### 2.6 窗口的物理上限：bias 会漂移

按 2.5 的误差公式，窗口越长越好，但 bias 不是真常数，通常建模成随机游走：

$$
\dot b_g = n_{wg}
$$

窗口 $T$ 内 bias 自身漂移约 $\sigma_{wg}\sqrt{T}$，随 $T$ 增长。于是两个约束互相制约：

- **下限**：$T$ 太短，bias 累积的旋转误差 $T\delta b_g$ 低于噪声水平，测不出来；
- **上限**：$T$ 太长，bias 漂移超过估计精度，「常数」假设破裂。

这就是 VIO/SLAM 不给整条序列一个 $b_g$ 的原因：每个关键帧一个 bias 状态，相邻帧之间用随机游走因子 $r_{b_g} = b_{g,j} - b_{g,i}$ 约束——既允许慢漂移，又不让一个错误的常数值污染整条轨迹。

> 小结：运动时陀螺仪零偏的估计问题归结为——观测只有 $\omega_m - b_g$，需要一个独立旋转参考钉住姿态，误差 $\delta b_g \approx \delta\theta_R / T$，窗口受随机游走限制。

## 3. 运动时：加速度计零偏与重力投影的分离

### 3.1 预积分通道的耦合结构

加速度计的问题和陀螺仪不同：重力方向这个参考始终在测量里，但它和 bias 纠缠在一起，能不能分开取决于姿态是否运动。重力信息通过预积分的速度、位置残差进入估计，具体耦合从速度传播推出。对水平重力偏差 $\delta g_w$ 和 bias 偏差 $\delta b_a$ 做一阶展开，速度残差和位置残差分别响应为

$$
\delta r_{v,ij} = \Delta t\left(\delta b_a - R_i^T \delta g_w\right), \qquad
\delta r_{p,ij} = \frac{1}{2}\Delta t^2\left(\delta b_a - R_i^T \delta g_w\right)
$$

两个残差是同一个结构：**恒定的机体系 bias $\delta b_a$，减去随姿态旋转的重力投影 $R_i^T \delta g_w$**。bias 在所有区间取值相同，投影则随姿态变化——能不能分离，取决于这个差别是否被观测到。

### 3.2 可分性：姿态激励的条件

把问题限制在水平面上（重力扰动的垂直分量直接可观测，不参与耦合）。设 $\delta b \in \mathbb{R}^2$ 为 bias 的水平分量，$\delta g \in \mathbb{R}^2$ 为水平重力扰动，残差的一阶近似是

$$
y_i = \delta b - R_i^T \delta g, \qquad i = 1, \ldots, N
$$

堆叠成最小二乘，法方程为

$$
A^T A = N \begin{bmatrix} I & -\bar R^T \\ -\bar R & I \end{bmatrix}, \qquad \bar R = \frac{1}{N}\sum_{i=1}^{N} R_i
$$

$\bar R$ 是姿态序列在水平面上的**平均旋转**。法方程奇异当且仅当 $\bar R$ 的最大奇异值 $\sigma_1 = 1$。姿态恒定不变时所有 $R_i$ 相等，$\bar R$ 是纯旋转，奇异值全为 1，$\delta b$ 和 $\delta g$ 完全耦合、不可分；姿态有任何变化，$\bar R$ 收缩，法方程满秩。

注意分离由 $R_i^T \delta g$ 的变化驱动，而不是由加速度或 roll/pitch 运动本身驱动：$\delta g$ 是水平向量，纯航向（yaw）旋转就会改变它在机体系下的投影，所以任何姿态变化都足够，yaw 变化和 roll/pitch 变化同样有效。

### 3.3 精度：法方程的条件数

可分性是二元的（姿态动没动过），精度是连续的。$\bar R$ 的奇异值决定法方程的特征值 $1 \pm \sigma_k$，条件数为

$$
\kappa = \frac{1 + \sigma_1}{1 - \sigma_1}
$$

- **弱激励**：姿态几乎不变，$\bar R$ 接近纯旋转，$\sigma_1 \to 1$，$\kappa \to \infty$，同样的测量噪声被放大成很大的 bias 误差——可分，但分不干净。
- **强激励**：姿态把水平方向充分扫开，平均旋转互相抵消，$\sigma_1 \to 0$，$\kappa \to 1$，病态消失。

考虑 turn-and-return——先转 $180^\circ$ 再转回原航向：水平面上的旋转恰好是 $-I$，前后两半时间相等时 $\bar R = (I + (-I))/2 = 0$，$\kappa = 1$，bias 和倾斜完全解耦——这是最优观测。反过来，汽车那种直行多、转弯少的轨迹，$\bar R$ 非常接近纯旋转，$\sigma_1$ 接近 1，即使结构上可分，条件数也很大，分离精度很差。

> 诊断一个轨迹分离得好不好，看 $\kappa = (1+\sigma_1)/(1-\sigma_1)$，而不是看有没有转过弯。

### 3.4 时变 bias 的陷阱：慢漂移吸收倾斜

前面的分析假设 bias 是常数。若建模成随机游走，出现第二个失败模式：**姿态引起的投影变化慢于 bias 漂移时，倾斜会被吸收进 bias，变成不可辨识的**。投影变化率是 $R_i^T \delta g$ 的时间导数，bias 漂移率是 $\sigma_{wg}\sqrt{\Delta t}$ 量级；前者小于后者时，因子图把倾斜解释成 bias 的缓慢漂移，重力校正失败。

这给出一个诊断方法：**看拟合出的 bias 的时间特征**。一次成功的重力校正拟合出的 bias 应当平稳；如果它带着明显的缓慢漂移，倾斜很可能没有被去掉，而是被 bias 吸收掉了。

## 4. 总结

| | 陀螺仪零偏 $b_g$ | 加速度计零偏 $b_a$ |
|---|---|---|
| 静止观测 | $\omega_m = b_g + n_g$，平均即可，**不需姿态** | $\bar a = R^T g + b_a$，**与重力投影耦合** |
| 静止平均得到 | 纯 $b_g$ | $R^T g + b_a$ 的混合 |
| 运动观测结构 | $\omega_m - b_g$ 进入姿态积分，与 $\omega$ 不可分 | $\delta b_a - R_i^T \delta g_w$，恒定 bias vs 旋转投影 |
| 可分性条件 | 需独立旋转参考打破 $\omega \leftrightarrow b_g$ 对称性 | 需姿态激励（任何姿态变化，纯 yaw 即可） |
| 误差主导因素 | $\delta b_g \approx \delta\theta_R / T$ | 条件数 $\kappa = (1+\sigma_1)/(1-\sigma_1)$ |
| 最优观测场景 | 静止/低动态（$\operatorname{Log}(\Delta R)/T$） | turn-and-return（$\bar R = 0$，$\kappa = 1$） |
| 时变 bias | 随机游走 → 关键帧级 bias + 漂移因子 | 慢漂移吸收倾斜，拟合 bias 的时间特征可诊断 |

两条线的结论可以合成一句：**零偏可观测，当且仅当存在一个与 bias 无关的独立参考**。陀螺仪的这个参考是姿态（来自视觉、LiDAR 或回环的相对旋转），观测越准、窗口越长，bias 估计越准；加速度计的这个参考是姿态变化本身（把重力投影方向扫开），激励越充分，条件数越小。静止之所以特殊，是因为 $\omega = 0$ 和（已知姿态下的）$R^T g$ 本身就是直接的参考——但静止加速度计仍然绕不开姿态，这是两个 bias 在估计难度上的差别。
