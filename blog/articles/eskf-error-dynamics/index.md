---
title: "ESKF 误差动力学推导：从 IMU 模型到 F 和 G"
date: 2026-09-04
tags: [ESKF, IMU, Error State, VINS, FAST-LIO2, State Estimation]
excerpt: "在固定坐标系和右侧姿态扰动约定下，从陀螺仪、加速度计和 bias 随机游走模型逐项推导误差动力学矩阵 F、G 及协方差传播，并说明它们在 VINS 预积分和 FAST-LIO2 IESKF 中分别扮演的角色。"
draft: false
---

# ESKF 误差动力学推导：从 IMU 模型到 F 和 G

> 这是 ESKF 系列的第二篇。第一篇文章介绍了名义状态、误差状态、误差注入和 reset；本文把抽象的“状态传播”落实到 IMU 方程，从每一项物理含义出发推导误差动力学矩阵 $F$ 和噪声输入矩阵 $G$。

## 摘要

ESKF 在传播阶段要同时维护两条信息：按照非线性 IMU 模型前进的名义状态，以及描述局部不确定性的误差状态协方差。后者的连续时间模型通常写成

$$
\dot{\delta x}=F\delta x+Gw.
$$

矩阵看起来像一组需要背诵的 block。实际推导并不依赖记忆：姿态误差来自两个旋转运动的相对变化，位置误差来自速度，速度误差来自姿态和加速度计 bias 对比力的影响，bias 误差则由随机游走噪声驱动。沿着这条因果链，可以逐项得到 $F$ 和 $G$。

本文固定如下约定：$R_{WB}$ 把机体坐标系 $B$ 的向量变换到世界坐标系 $W$；姿态采用右侧扰动 $R=\hat R\operatorname{Exp}([\delta\theta]_\times)$；误差排列为 $[\delta\theta,\delta p,\delta v,\delta b_g,\delta b_a]$。在这个约定下，本文推导出一组 15 维连续时间误差动力学，并区分连续噪声强度 $Q_c$ 和离散过程噪声协方差 $Q_d$。

最后，文章把这组方程放回两个常见系统中理解。VINS-Mono 的主估计器是 IMU 预积分加滑动窗口非线性优化；FAST-LIO2 则采用紧耦合迭代误差状态 Kalman filter。两者都会用到误差传播的 Jacobian 和协方差，但它们在整个估计框架中的位置不同。

**关键词：** ESKF；IMU；误差动力学；协方差传播；IMU 预积分；VINS；FAST-LIO2

## 1. 为什么要专门推导 $F$ 和 $G$

第一篇文章中，ESKF 的传播可以抽象成

$$
\delta x_{k+1}
\approx
\Phi_k\delta x_k+\text{process noise}.
$$

这个式子还没有告诉我们误差如何互相影响。对于 IMU 状态估计，最常见的影响链是：

- 陀螺仪 bias 影响去 bias 后的角速度，角速度又影响姿态误差；
- 姿态误差改变加速度计比力被旋转到世界系后的方向；
- 加速度计 bias 直接改变世界系加速度；
- 速度误差经过积分变成位置误差；
- gyro 和 accelerometer 的随机噪声分别进入姿态与速度；
- bias 随机游走使两个 bias 误差随时间继续变化。

$F$ 描述第一类关系：**已有误差怎样推动其他误差变化**。例如，$F_{\theta b_g}=-I$ 表示 gyro bias 误差会直接改变姿态误差的导数。$G$ 描述第二类关系：**传感器噪声怎样进入误差状态**。例如，加速度计白噪声先出现在机体系比力中，再由 $\hat R$ 旋转到世界系，所以速度行对应 $-\hat R$。

如果坐标方向、姿态扰动方向、bias 的符号或噪声排列改变，矩阵中的符号和旋转矩阵位置也会改变。下面先把这些约定固定下来，再开始计算。

## 2. 坐标系、姿态和误差约定

### 2.1 坐标变换

世界坐标系记为 $W$，机体或 IMU 坐标系记为 $B$。姿态旋转矩阵 $R_{WB}$ 表示从 $B$ 到 $W$ 的变换，因此

$$
\mathbf x_W=R_{WB}\mathbf x_B,
\qquad
\mathbf x_B=R_{WB}^{\top}\mathbf x_W.
$$

重力加速度用世界系向量 $g$ 表示。若世界系 $+Z$ 轴向上，通常有 $g=[0,0,-9.81]^{\top}\,\mathrm{m/s^2}$。本文只要求 $g$ 在世界系中是已知常量，具体正负方向由坐标系定义决定。

对任意三维向量 $u$，定义叉乘矩阵

$$
[u]_\times v=u\times v.
$$

旋转的小量通过指数映射表示：

$$
\operatorname{Exp}([u]_\times)=\exp([u]_\times).
$$

当 $u$ 足够小时，

$$
\operatorname{Exp}([u]_\times)
\approx I+[u]_\times.
$$

### 2.2 右侧姿态误差

本文采用右侧扰动：

$$
R=\hat R\operatorname{Exp}([\delta\theta]_\times).
$$

这里 $\hat R$ 是名义姿态，$R$ 是真实姿态，$\delta\theta$ 是三维小角度误差。由于误差矩阵在 $\hat R$ 右侧，$\delta\theta$ 的坐标表达位于名义机体系中。这个细节会决定姿态误差方程中的 $-[\hat\omega]_\times$。

其余状态使用加性误差：

$$
\begin{aligned}
p&=\hat p+\delta p,\\
v&=\hat v+\delta v,\\
b_g&=\hat b_g+\delta b_g,\\
b_a&=\hat b_a+\delta b_a.
\end{aligned}
$$

误差状态按以下顺序排列，共 15 维：

$$
\delta x=
\begin{bmatrix}
\delta\theta\\
\delta p\\
\delta v\\
\delta b_g\\
\delta b_a
\end{bmatrix}.
$$

## 3. IMU 测量模型

### 3.1 陀螺仪和加速度计

陀螺仪测量角速度，加速度计测量比力。采用如下模型：

$$
\tilde\omega=\omega+b_g+n_g,
$$

$$
\tilde a=R^{\top}(a-g)+b_a+n_a.
$$

其中：

- $\tilde\omega$ 是陀螺仪输出；
- $\tilde a$ 是加速度计输出；
- $\omega$ 是机体系中的真实角速度；
- $a=\dot v$ 是世界系中的真实线加速度；
- $b_g$ 和 $b_a$ 分别是 gyro bias 与 accelerometer bias；
- $n_g$ 和 $n_a$ 是测量白噪声。

加速度计输出中的理想部分是 $a-g$ 在机体系中的表达。世界系线加速度 $a$ 需要经过姿态变换并加回重力才能得到。把模型移项后，真实状态的连续时间动力学为

$$
\dot R=R[\tilde\omega-b_g-n_g]_\times,
$$

$$
\dot p=v,
$$

$$
\dot v=g+R(\tilde a-b_a-n_a).
$$

### 3.2 Bias 随机游走

把两个 bias 建模为随机游走：

$$
\dot b_g=n_{wg},
\qquad
\dot b_a=n_{wa},
$$

其中 $n_{wg}$ 和 $n_{wa}$ 是驱动 bias 变化的白噪声。于是本文使用的噪声向量为

$$
w=
\begin{bmatrix}
 n_g\\
 n_a\\
 n_{wg}\\
 n_{wa}
\end{bmatrix}.
$$

这里的符号顺序很重要。后面 $G$ 的四个列 block 会严格按照这个顺序排列。

## 4. 名义状态传播

ESKF 的名义状态把未知噪声设为零，并用当前 IMU 测量推进状态：

$$
\dot{\hat R}=\hat R[\tilde\omega-\hat b_g]_\times,
$$

$$
\dot{\hat p}=\hat v,
$$

$$
\dot{\hat v}=g+\hat R(\tilde a-\hat b_a),
$$

$$
\dot{\hat b}_g=0,
\qquad
\dot{\hat b}_a=0.
$$

定义两个简写：

$$
\hat\omega\triangleq\tilde\omega-\hat b_g,
\qquad
\hat a\triangleq\tilde a-\hat b_a.
$$

它们分别是当前名义 gyro bias 和 accelerometer bias 校正后的 IMU 输入。这里的 $\hat a$ 表示机体系中的名义比力，不表示世界系加速度估计。

名义状态使用零均值噪声传播，协方差通过线性化模型保留噪声对不确定性的影响。ESKF 因而把非线性运动和局部误差不确定性分开处理。

## 5. 从真实方程推导误差动力学

下面逐项计算 $\dot{\delta x}$。所有一阶近似都在 $\delta\theta$、$\delta b_g$、$\delta b_a$ 足够小时成立。

### 5.1 姿态误差：为什么会出现 $-[\hat\omega]_\times$

右侧姿态误差可以写成。$R$ 先把真实机体系中的向量变到世界系，$\hat R^{\top}$ 再把它变回名义机体系，所以 $E$ 表示真实姿态相对名义姿态的局部旋转关系：

$$
E\triangleq\hat R^{\top}R
=\operatorname{Exp}([\delta\theta]_\times).
$$

在直接求导之前，先把真实姿态和名义姿态的运动方程并排写出：

$$
\dot{\hat R}=\hat R[\hat\omega]_\times,
\qquad
\dot R=R[\omega]_\times.
$$

这里的 $\omega$ 和 $\hat\omega$ 都用机体系表达。因为 $R_{WB}$ 把机体系向量变到世界系，机体系角速度出现在旋转矩阵右侧；如果角速度改用世界系表达，动力学会写成 $\dot R=[\omega_W]_\times R$，这时后面的推导形式也会改变。

先处理真实角速度。由 gyro 测量模型和

$$
 b_g=\hat b_g+\delta b_g
$$

可得

$$
\begin{aligned}
\omega
&=\tilde\omega-b_g-n_g\\
&=\tilde\omega-\hat b_g-\delta b_g-n_g\\
&=\hat\omega-\delta b_g-n_g.
\end{aligned}
$$

接下来对

$$
E=\hat R^{\top}R
$$

使用乘积求导法则：

$$
\dot E=\dot{\hat R}^{\top}R+\hat R^{\top}\dot R.
$$

第一项需要先求 $\hat R^{\top}$ 的导数。由转置运算和叉乘矩阵的反对称性 $[\hat\omega]_\times^{\top}=-[\hat\omega]_\times$，有

$$
\begin{aligned}
\dot{\hat R}^{\top}
&=(\dot{\hat R})^{\top}\\
&=(\hat R[\hat\omega]_\times)^{\top}\\
&=[\hat\omega]_\times^{\top}\hat R^{\top}\\
&=-[\hat\omega]_\times\hat R^{\top}.
\end{aligned}
$$

因此

$$
\begin{aligned}
\dot{\hat R}^{\top}R
&=-[\hat\omega]_\times\hat R^{\top}R\\
&=-[\hat\omega]_\times E.
\end{aligned}
$$

第二项直接代入真实姿态方程：

$$
\begin{aligned}
\hat R^{\top}\dot R
&=\hat R^{\top}R[\omega]_\times\\
&=E[\omega]_\times\\
&=E[\hat\omega-\delta b_g-n_g]_\times.
\end{aligned}
$$

把两项相加，原式就得到

$$
\boxed{
\dot E
=-[\hat\omega]_\times E
+E[\hat\omega-\delta b_g-n_g]_\times.
}
$$

这两个项可以这样读：$-[\hat\omega]_\times E$ 来自名义姿态转置的变化，$E[\hat\omega-\delta b_g-n_g]_\times$ 来自真实姿态的变化。$E=\hat R^{\top}R$ 把真实姿态和名义姿态放到同一个局部坐标关系中，所以两项能够相加。

现在才进行小角度线性化。右侧扰动给出

$$
E=\operatorname{Exp}([\delta\theta]_\times)
\approx I+[\delta\theta]_\times.
$$

将它代入刚才的精确误差方程，并把真实角速度展开：

$$
\begin{aligned}
\dot E
\approx{}&-[\hat\omega]_\times
\left(I+[\delta\theta]_\times\right)\\
&+\left(I+[\delta\theta]_\times\right)
\left([\hat\omega]_\times-[\delta b_g]_\times-[n_g]_\times\right)\\
={}&-[\hat\omega]_\times
-[\hat\omega]_\times[\delta\theta]_\times
+[\hat\omega]_\times\\
&+[\delta\theta]_\times[\hat\omega]_\times
-[\delta b_g]_\times-[n_g]_\times\\
&-[\delta\theta]_\times
\left([\delta b_g]_\times+[n_g]_\times\right).
\end{aligned}
$$

最后一行的乘积包含两个小量相乘，是二阶项，在线性化中舍去；前后两个 $[\hat\omega]_\times$ 正好抵消。因此

$$
\begin{aligned}
\dot E
&\approx-[\hat\omega]_\times[\delta\theta]_\times
+[\delta\theta]_\times[\hat\omega]_\times\\
&\quad-[\delta b_g]_\times-[n_g]_\times.
\end{aligned}
$$

同时，$E\approx I+[\delta\theta]_\times$ 意味着

$$
\dot E\approx[\dot{\delta\theta}]_\times.
$$

下面从这个一阶矩阵等式开始，把它逐步转换成三维向量方程。将前一个 $\dot E$ 展开式的左侧替换成 $[\dot{\delta\theta}]_\times$，得到

$$
\begin{aligned}
[\dot{\delta\theta}]_\times
={}&-[\hat\omega]_\times[\delta\theta]_\times
+[\delta\theta]_\times[\hat\omega]_\times\\
&-[\delta b_g]_\times-[n_g]_\times.
\end{aligned}
$$

先解释交换子恒等式。对任意三维向量 $x$，

$$
\begin{aligned}
\left([u]_\times[v]_\times-[v]_\times[u]_\times\right)x
&=u\times(v\times x)-v\times(u\times x)\\
&=(u\times v)\times x.
\end{aligned}
$$

因为这个等式对任意 $x$ 都成立，所以两个矩阵相同：

$$
[u]_\times[v]_\times-[v]_\times[u]_\times
=[u\times v]_\times.
$$

把 $u=\delta\theta$、$v=\hat\omega$ 代入。注意当前的前两项顺序是

$$
[\delta\theta]_\times[\hat\omega]_\times
-[\hat\omega]_\times[\delta\theta]_\times,
$$

所以

$$
\begin{aligned}
&-[\hat\omega]_\times[\delta\theta]_\times
+[\delta\theta]_\times[\hat\omega]_\times\\
&\qquad=[\delta\theta\times\hat\omega]_\times.
\end{aligned}
$$

接下来只处理叉乘向量本身：

$$
\begin{aligned}
\delta\theta\times\hat\omega
&=-(\hat\omega\times\delta\theta)\\
&=-[\hat\omega]_\times\delta\theta.
\end{aligned}
$$

因此

$$
-[\hat\omega]_\times[\delta\theta]_\times
+[\delta\theta]_\times[\hat\omega]_\times
=\left[-[\hat\omega]_\times\delta\theta\right]_\times.
$$

噪声和 bias 项也可以合并，因为叉乘矩阵对向量是线性的：

$$
-[\delta b_g]_\times-[n_g]_\times
=\left[-\delta b_g-n_g\right]_\times.
$$

把两部分放回姿态误差方程：

$$
\begin{aligned}
[\dot{\delta\theta}]_\times
&=\left[-[\hat\omega]_\times\delta\theta\right]_\times
+\left[-\delta b_g-n_g\right]_\times\\
&=\left[-[\hat\omega]_\times\delta\theta
-\delta b_g-n_g\right]_\times.
\end{aligned}
$$

最后使用叉乘矩阵的逆操作，也就是

$$
([q]_\times)^\vee=q,
$$

从矩阵两边取 $\vee$，得到

$$
\boxed{
\dot{\delta\theta}
=-[\hat\omega]_\times\delta\theta
-\delta b_g-n_g.
}
$$

整个转换可以压缩成一条链：

$$
\begin{aligned}
[\dot{\delta\theta}]_\times
&=[\delta\theta\times\hat\omega]_\times
+[-\delta b_g-n_g]_\times\\
&=[-[\hat\omega]_\times\delta\theta-\delta b_g-n_g]_\times\\
&\Longrightarrow\quad
\dot{\delta\theta}
=-[\hat\omega]_\times\delta\theta-\delta b_g-n_g.
\end{aligned}
$$

每一项都有直接含义：

- $-[\hat\omega]_\times\delta\theta$：右侧误差用机体系表达，而机体系正在以 $\hat\omega$ 旋转，所以误差坐标本身会变化；
- $-\delta b_g$：gyro bias 误差被从角速度测量中减去，因而它以负号进入姿态误差导数；
- $-n_g$：gyro 测量噪声同样出现在校正后的角速度中。

如果改用左侧姿态扰动，误差坐标位于世界系，姿态 block 的形式会不同。这个结果不能脱离扰动约定单独使用。

### 5.2 位置误差：来自速度误差

位置和速度采用加性误差：

$$
\delta p=p-\hat p,
\qquad
\delta v=v-\hat v.
$$

由 $\dot p=v$ 和 $\dot{\hat p}=\hat v$，直接得到

$$
\boxed{\dot{\delta p}=\delta v.}
$$

因此位置误差行的 $F_{pv}$ block 是 $I$。连续时间模型里，位置没有直接的 IMU 白噪声输入；噪声先影响速度，再通过积分影响位置。

### 5.3 速度误差：姿态和 accelerometer bias 如何进入

真实速度动力学可以用误差变量改写为

$$
\begin{aligned}
\dot v
&=g+R(\tilde a-b_a-n_a)\\
&=g+\hat R\operatorname{Exp}([\delta\theta]_\times)
(\hat a-\delta b_a-n_a).
\end{aligned}
$$

名义速度动力学为

$$
\dot{\hat v}=g+\hat R\hat a.
$$

两式相减，并使用

$$
\operatorname{Exp}([\delta\theta]_\times)\hat a
\approx
\hat a+[\delta\theta]_\times\hat a
=\hat a-[\hat a]_\times\delta\theta,
$$

得到

$$
\begin{aligned}
\dot{\delta v}
&=\hat R\left(-[\hat a]_\times\delta\theta
-\delta b_a-n_a\right)\\
&= -\hat R[\hat a]_\times\delta\theta
-\hat R\delta b_a
-\hat R n_a.
\end{aligned}
$$

所以

$$
\boxed{
\dot{\delta v}
=-\hat R[\hat a]_\times\delta\theta
-\hat R\delta b_a
-\hat R n_a.
}
$$

这里最容易出现符号错误。姿态误差对向量 $\hat a$ 的一阶影响是

$$
[\delta\theta]_\times\hat a
=-[\hat a]_\times\delta\theta,
$$

所以速度误差中的姿态 block 是 $-\hat R[\hat a]_\times$。负号来自上面的叉乘矩阵关系。

这条方程也解释了为什么姿态误差会造成平移误差：加速度计给出的比力先经过一个错误的姿态旋转，随后被积分为速度和位置误差。

### 5.4 Bias 误差：随机游走噪声直接进入

由于名义 bias 在传播时保持不变，真实 bias 按随机游走变化：

$$
\dot{\delta b}_g
=\dot b_g-\dot{\hat b}_g
=n_{wg},
$$

$$
\dot{\delta b}_a
=\dot b_a-\dot{\hat b}_a
=n_{wa}.
$$

bias 误差行在 $F$ 中没有确定性 block，在 $G$ 中分别对应单位矩阵。随机游走噪声用于推动 bias 误差随时间变化。

## 6. 组装 $F$ 和 $G$

把上面的五组方程按照

$$
\delta x=
\begin{bmatrix}
\delta\theta\\
\delta p\\
\delta v\\
\delta b_g\\
\delta b_a
\end{bmatrix},
\qquad
w=
\begin{bmatrix}
 n_g\\
 n_a\\
 n_{wg}\\
 n_{wa}
\end{bmatrix}
$$

排列，得到

$$
\dot{\delta x}=F\delta x+Gw,
$$

其中

$$
\boxed{
F=
\begin{bmatrix}
-[\hat\omega]_\times & 0 & 0 & -I & 0\\
0 & 0 & I & 0 & 0\\
-\hat R[\hat a]_\times & 0 & 0 & 0 & -\hat R\\
0 & 0 & 0 & 0 & 0\\
0 & 0 & 0 & 0 & 0
\end{bmatrix}
}
$$

以及

$$
\boxed{
G=
\begin{bmatrix}
-I & 0 & 0 & 0\\
0 & 0 & 0 & 0\\
0 & -\hat R & 0 & 0\\
0 & 0 & I & 0\\
0 & 0 & 0 & I
\end{bmatrix}.
}
$$

这里每个 $0$ 或 $I$ 都是合适大小的 $3\times3$ block。$F$ 是 $15\times15$ 矩阵，$G$ 是 $15\times12$ 矩阵。

### 6.1 逐个查看 $F$ 的 block

| block | 来源 | 物理含义 |
|---|---|---|
| $F_{\theta\theta}=-[\hat\omega]_\times$ | 右侧姿态误差的相对运动 | 名义机体系旋转时，机体系中的姿态误差坐标随之变化 |
| $F_{\theta b_g}=-I$ | $\tilde\omega-\hat b_g-\delta b_g$ | gyro bias 误差直接变成角速度误差 |
| $F_{pv}=I$ | $\dot p=v$ | 速度误差是位置误差的导数 |
| $F_{v\theta}=-\hat R[\hat a]_\times$ | 姿态扰动作用于比力 | 姿态误差改变比力旋转到世界系后的方向 |
| $F_{v b_a}=-\hat R$ | $\tilde a-\hat b_a-\delta b_a$ | accelerometer bias 误差直接改变世界系加速度 |
| bias 行 | bias 随机游走 | 在本文模型中没有确定性漂移项 |

有两个容易被矩阵的零 block 误导的地方：

1. $F_{v p}=0$ 并不表示位置永远与速度无关。本文的 IMU 运动模型在局部平坦空间中不使用位置；位置会通过 $F_{pv}$ 受到速度影响。
2. $F_{p\theta}=0$ 并不表示姿态不会影响位置。姿态先进入速度，再经过离散时间积分影响位置；连续时间的一阶状态方程把这条影响拆成了两步。

### 6.2 逐个查看 $G$ 的 block

| block | 来源 | 物理含义 |
|---|---|---|
| $G_{\theta n_g}=-I$ | gyro 测量模型 | 角速度噪声直接进入姿态误差，负号来自去除噪声的动力学表达 |
| $G_{v n_a}=-\hat R$ | 加速度计测量模型 | 机体系加速度噪声先进入比力，再由名义姿态旋转到世界系 |
| $G_{b_g n_{wg}}=I$ | gyro bias 随机游走 | 随机游走噪声直接改变 gyro bias |
| $G_{b_a n_{wa}}=I$ | accelerometer bias 随机游走 | 随机游走噪声直接改变 accelerometer bias |
| 位置行 | 连续模型中没有直接位置噪声 | 位置噪声通过速度积分间接产生 |

矩阵中噪声的正负号会影响误差状态的具体表达，但在独立、零均值噪声的协方差传播中，单个直接输入 block 的整体正负号会在 $GQG^{\top}$ 中消失。推导观测 Jacobian 或比较不同误差定义时，仍然必须保留正确符号。

## 7. 从误差动力学到协方差传播

### 7.1 连续时间协方差

假设噪声是连续时间白噪声，满足

$$
\mathbb E[w(t)w(s)^{\top}]
=Q_c\,\delta(t-s),
$$

其中 $Q_c$ 是连续时间噪声强度矩阵。若四类噪声相互独立，可以写成

$$
Q_c=\operatorname{diag}(Q_g,Q_a,Q_{wg},Q_{wa}).
$$

在本文的 $G$ 下，直接噪声注入项为

$$
GQ_cG^{\top}
=
\operatorname{diag}
\left(
Q_g,
0,
\hat RQ_a\hat R^{\top},
Q_{wg},
Q_{wa}
\right).
$$

这个矩阵当前是 block diagonal，但 $F$ 的状态耦合仍会让完整协方差 $P$ 在传播过程中出现姿态、速度、位置和 bias 之间的相关性。连续时间 Riccati 方程为

$$
\boxed{
\dot P=FP+PF^{\top}+GQ_cG^{\top}.
}
$$

这条式子里的三部分分别表示：已有不确定性被动力学搬运、转置项保持协方差对称，以及新的过程噪声不断注入。

### 7.2 离散时间传播

采样间隔记为 $\Delta t$。若在一个小时间段内把 $F$ 视为常量，状态转移矩阵为

$$
\Phi=\exp(F\Delta t).
$$

离散过程噪声协方差的连续白噪声表达为

$$
Q_d
=\int_0^{\Delta t}
\exp(F\tau)GQ_cG^{\top}
\exp(F\tau)^{\top}\,d\tau.
$$

于是

$$
\boxed{
P_{k+1}=\Phi_kP_k\Phi_k^{\top}+Q_{d,k}.
}
$$

最简单的一阶近似是

$$
\Phi_k\approx I+F_k\Delta t,
$$

$$
Q_{d,k}\approx G_kQ_cG_k^{\top}\Delta t.
$$

工程实现中还可以使用矩阵指数、Van Loan 方法或更高阶数值积分来计算 $\Phi$ 和 $Q_d$。选择哪种方法，需要和 IMU 采样周期、角速度大小以及系统精度要求一起考虑。

### 7.3 为什么有时会看到 $\Delta t^2$

“过程噪声到底乘一个 $\Delta t$ 还是 $\Delta t^2$？”这个问题不能只看公式，还要先看噪声的定义。

若 $w(t)$ 是连续白噪声，$Q_c$ 的单位是噪声强度，积分白噪声得到的离散协方差在一阶近似下是

$$
Q_d\approx GQ_cG^{\top}\Delta t.
$$

若把一个采样周期内的噪声视为常量随机变量 $w_k$，并定义

$$
\operatorname{Cov}(w_k)=Q_{\mathrm{sample}},
$$

则离散状态增量是 $G w_k\Delta t$，相应协方差为

$$
Q_d\approx
(G\Delta t)Q_{\mathrm{sample}}(G\Delta t)^{\top}.
$$

两种写法对应两种噪声约定，不能在没有单位和采样定义的情况下直接比较。VINS-Mono 论文在预积分协方差递推中写出了 $(G_t\delta t)Q(G_t\delta t)^{\top}$ 的形式；阅读这类公式时，需要结合它对离散采样噪声的定义理解 $Q$，不能把符号名称直接等同于连续时间的 $Q_c$。

## 8. 这组方程和 VINS 预积分是什么关系

### 8.1 VINS 的主框架

VINS-Mono 的主估计器是紧耦合滑动窗口非线性优化。它把相邻图像帧之间的大量 IMU 测量预积分成一组相对运动量，再把这些量与视觉特征残差一起放进窗口优化问题。

VINS-Mono 的主流程可以概括为：

1. 在两个关键帧之间读取高频 IMU 测量；
2. 在局部参考系中递推预积分量，例如位置变化、速度变化和相对旋转；
3. 同时递推预积分量的 bias Jacobian、状态转移 Jacobian 和协方差；
4. 将预积分结果作为关键帧之间的 IMU 残差，和视觉残差共同参与非线性优化。

VINS-Mono 论文 Section IV-B 给出的预积分误差状态排列是 $[\delta\alpha,\delta\beta,\delta\theta,\delta b_a,\delta b_g]$。其中 $\delta\alpha$ 和 $\delta\beta$ 分别对应预积分的位置与速度误差，$\delta\theta$ 对应预积分旋转误差。它的连续线性化方程同样可以写成

$$
\dot{\delta z}=F_t\delta z+G_t n_t,
$$

并通过

$$
J_{t+\delta t}=(I+F_t\delta t)J_t
$$

递推初始状态到当前预积分量的 Jacobian，通过协方差递推保存 IMU 约束的不确定性。

### 8.2 共同的数学基础

本文 15 维 ESKF 与 VINS 预积分的状态排列不相同，使用的姿态参考系也可能不同，但它们共享同一条推导链：

- 先写出 IMU 非线性运动模型；
- 选择局部姿态误差；
- 对误差动力学一阶线性化；
- 得到状态 Jacobian $F$ 和噪声 Jacobian $G$；
- 用它们递推状态转移关系、bias Jacobian 和协方差。

本文的 $F$ 描述“误差如何在连续时间流动”。预积分再把这条连续流动压缩到两个关键帧之间，形成一个可以被优化器反复使用的相对约束。

### 8.3 两者在系统中的位置不同

| 方面 | ESKF | VINS-Mono 预积分与优化 |
|---|---|---|
| IMU 的作用 | 高频传播名义状态和误差协方差 | 高频压缩为关键帧之间的预积分量 |
| $F$、$G$ 的用途 | 构造当前误差状态的状态转移和过程噪声 | 递推预积分 Jacobian、bias 修正和协方差 |
| 观测融合 | 观测到达后直接更新当前滤波状态 | 视觉和 IMU 残差一起进入滑动窗口非线性优化 |
| 线性化管理 | 围绕当前名义状态进行局部误差更新 | 优化器围绕窗口状态反复重线性化，旧状态通过边缘化处理 |
| 主要估计形式 | 在线滤波 | 有限窗口的 MAP/非线性优化 |

VINS 也可以在优化结果基础上继续做 IMU 前向传播，产生更高频的状态输出。这一步服务于实时输出和控制，不能把 VINS 的主估计器改称为全局 EKF。判断一个系统属于哪类方法，要看它如何组织主要状态、残差和不确定性，而不只是看它是否出现了 $F$、$G$ 或“Kalman”这些词。

## 9. 这组方程和 FAST-LIO2 IESKF 是什么关系

### 9.1 FAST-LIO2 的滤波框架

FAST-LIO2 使用 IMU 和 LiDAR 进行紧耦合状态估计。论文 Section IV 将它描述为 on-manifold iterated Kalman filter：

- IMU 到达时，传播名义状态；
- 同时使用状态 Jacobian 和噪声 Jacobian 传播协方差；
- LiDAR 扫描到达后，利用点到局部平面的几何残差建立观测模型；
- 在同一帧 LiDAR 更新内反复线性化和更新，直到状态增量收敛。

这种结构属于迭代误差状态 Kalman filter（IESKF）一类。FAST-LIO2 论文和相关实现中使用的具体术语有“tightly-coupled iterated Kalman filter”“on-manifold iterated Kalman filter”等不同写法，描述的是同一类滤波结构。

### 9.2 状态比本文更大

本文为了清楚推导 IMU 核心，使用了

$$
(R,p,v,b_g,b_a)
$$

这组 15 自由度状态。FAST-LIO2 还把重力和 LiDAR-IMU 外参放进状态，典型状态可以写成

$$
\mathcal X=
(R_{WI},p_{WI},v_{WI},b_g,b_a,g_W,R_{IL},p_{IL}).
$$

由此，FAST-LIO2 的误差状态维度会比本文大。扩展后，速度误差方程还会多出重力误差项：

$$
\delta\dot v
=\cdots+\delta g_W.
$$

对应的 $F_{v g}$ block 是 $I$；若重力被视为常量，重力误差行的确定性导数仍为零。LiDAR-IMU 外参也会产生自己的误差 block 和观测 Jacobian。

本文的 15 维 $F$、$G$ 可以看作这类系统中 IMU 核心传播模型的一个简化子块。FAST-LIO2 的完整推导还要处理 LiDAR 点的采样时间、运动畸变补偿、外参和点到平面残差，这些内容留到后续文章。

### 9.3 ESKF 和 FAST-LIO2 的直接对应

| 本文的 ESKF 部分 | FAST-LIO2 中的对应位置 |
|---|---|
| 名义 IMU 状态传播 | 每个 IMU 测量到达时的 forward propagation |
| $F$ | 状态误差对上一时刻误差的 Jacobian |
| $G$ | 状态误差对 IMU 过程噪声的 Jacobian |
| $P$ 的传播 | IMU 传播阶段的协方差更新 |
| 观测 Jacobian $H$ | LiDAR 点到平面隐式残差的线性化 Jacobian |
| 误差更新 | 每个 LiDAR 扫描内的迭代 Kalman update |
| 姿态流形处理 | on-manifold 的状态加法与误差定义 |

所以 FAST-LIO2 和本文的 ESKF 在“IMU 传播—误差线性化—协方差传播—观测更新”这条链路上非常接近。差别主要出现在状态扩展、观测模型和迭代更新方式，而非 $F$、$G$ 是否存在。

## 10. 推导时最容易混淆的几件事

### 10.1 $R_{WB}$ 和 $R_{BW}$ 写反

本文使用 $R_{WB}$ 把机体系向量变到世界系，所以速度方程中的比力是

$$
\hat R(\tilde a-\hat b_a).
$$

如果使用的是世界系到机体系的旋转，公式中会出现转置，姿态误差 block 也需要重新推导。看到论文中的 $R^w_b$、$R^b_w$ 或下标排列时，先确认它表示哪个方向。

### 10.2 右扰动和左扰动混用

右扰动

$$
R=\hat R\operatorname{Exp}([\delta\theta]_\times)
$$

让 $\delta\theta$ 在名义机体系表达；左扰动则把误差放在旋转矩阵左侧，误差通常在世界系表达。两者的姿态动力学和 bias Jacobian 不能混写。

### 10.3 把测量噪声和 bias 随机游走混成一类

$n_g$ 和 $n_a$ 是当前 gyro、accelerometer 输出的快速噪声；$n_{wg}$ 和 $n_{wa}$ 是驱动 bias 变化的噪声。前两者进入姿态与速度方程，后两者进入 bias 方程。它们的噪声密度、单位和离散化方式也可能不同。

### 10.4 看到 $F$、$G$ 就认为两个系统是同一个滤波器

F/G 是局部线性化的通用工具。ESKF 用它们传播当前滤波器的协方差，VINS 用它们递推预积分量的 Jacobian 与协方差，FAST-LIO2 用它们完成 IESKF 的 IMU 预测。相同的局部动力学可以服务于不同的全局估计架构。

### 10.5 直接复制别人的矩阵

至少需要重新确认以下五点：

1. 姿态矩阵的变换方向；
2. 姿态误差放在左侧还是右侧；
3. 误差状态和噪声向量的排列；
4. 重力符号与 accelerometer 测量定义；
5. bias 是随机游走、常量还是一阶 Gauss–Markov 过程。

这五点中任意一点不同，都可能让一个看似熟悉的 block 失去原来的含义。

## 11. 本文得到的结果与适用边界

本文在明确的 15 维状态和右侧姿态扰动约定下，完成了以下闭环：

1. 从 gyro、accelerometer 和 bias 随机游走模型写出真实动力学；
2. 用零均值噪声传播得到名义状态；
3. 通过 $R=\hat R\operatorname{Exp}([\delta\theta]_\times)$ 定义局部姿态误差；
4. 逐项推导姿态、位置、速度和 bias 误差方程；
5. 组装连续时间 $F$、$G$；
6. 用 $F$、$G$ 推导连续和离散协方差传播；
7. 解释同一套误差动力学如何进入 VINS 预积分与 FAST-LIO2 IESKF。

这组矩阵适用于重力在世界系已知、IMU 外参暂不作为状态、bias 采用随机游走的基本模型。实际系统需要根据任务扩展：FAST-LIO2 会估计重力和 LiDAR-IMU 外参；VINS 会把相邻关键帧的预积分量、视觉特征和 bias 一起放进窗口优化；有些惯性导航系统还会估计地球自转、尺度、时间偏移或杆臂效应。

这些扩展会增加状态和 Jacobian block，但推导方法没有改变：先写非线性动力学，再定义流形误差，最后对误差和噪声分别求一阶导数。

## 12. 结论

$F$ 和 $G$ 不需要靠背诵获得。固定坐标系和姿态误差约定后，每个 block 都能从一条具体的物理关系追溯出来：

- 姿态误差由角速度和 gyro bias 驱动；
- 位置误差由速度误差驱动；
- 速度误差由姿态误差、 accelerometer bias 和加速度计噪声驱动；
- bias 误差由随机游走噪声驱动。

对本文的右侧姿态扰动，误差动力学为

$$
\dot{\delta x}=F\delta x+Gw,
$$

其中 $F$ 负责描述误差之间的传播，$G$ 负责把 IMU 噪声送入误差状态。协方差传播再把这两部分组合为

$$
\dot P=FP+PF^{\top}+GQ_cG^{\top}.
$$

VINS-Mono 和 FAST-LIO2 都会使用这类局部线性化，但系统架构不同：前者把 IMU 信息预积分成优化因子，后者把 IMU 传播和 LiDAR 迭代更新组织成误差状态 Kalman filter。理解这个区别，才能正确阅读论文中形式相似的 $F$、$G$、Jacobian 和 covariance 公式。

## 参考文献

1. Joan Solà, *Quaternion kinematics for the error-state Kalman filter*, arXiv:1711.02508, 2017. <https://arxiv.org/abs/1711.02508>
2. Joachim Hertzberg, René Wagner, Uwe Frese, and Lutz Schröder, *Integrating Generic Sensor Fusion Algorithms with Sound State Representations through Encapsulation of Manifolds*, Information Fusion, 2013. Preprint: <https://arxiv.org/abs/1107.1119>
3. Tong Qin, Peiliang Li, and Shaojie Shen, *VINS-Mono: A Robust and Versatile Monocular Visual-Inertial State Estimator*, IEEE Transactions on Robotics, 34(4):1004–1020, 2018. <https://arxiv.org/abs/1708.03852>
4. Wei Xu, Yixi Cai, Dongjiao He, Jiarong Lin, and Fu Zhang, *FAST-LIO2: Fast Direct LiDAR-inertial Odometry*, IEEE Transactions on Robotics, 38(4):2053–2070, 2022. <https://arxiv.org/abs/2107.06829>
5. HKUST Aerial Robotics Group, *VINS-Mono*, official repository. <https://github.com/HKUST-Aerial-Robotics/VINS-Mono>
6. hku-mars, *FAST_LIO*, official repository. <https://github.com/hku-mars/FAST_LIO>
