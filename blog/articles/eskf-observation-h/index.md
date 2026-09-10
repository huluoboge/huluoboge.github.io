---
title: "ESKF 观测误差与 H 矩阵：从观测模型到 Jacobian"
date: 2026-09-05
tags: [ESKF, EKF, H Matrix, Observation Model, IMU, LiDAR, State Estimation]
excerpt: "承接 ESKF 的误差动力学，从 z=h(x)+v 出发，逐步推导观测残差、H 矩阵、Kalman 更新，以及位置、速度、姿态、重力和 LiDAR 点到平面观测的 Jacobian。"
draft: false
---

# ESKF 观测误差与 H 矩阵：从观测模型到 Jacobian

> 这是 ESKF 系列的第三篇。上一篇文章已经在固定的坐标系和右侧姿态扰动下推导了 IMU 误差动力学矩阵 $F$、噪声输入矩阵 $G$，并把它们接到了协方差传播。本文继续处理观测更新：一个传感器读数怎样变成残差，残差怎样对 15 维误差状态线性化，最后又怎样通过 $H$ 矩阵回到名义状态。

## 摘要

ESKF 里的观测更新常被压缩成几行代码：计算残差，构造 $H$，计算 Kalman gain，更新误差状态。真正容易出错的地方藏在这几行的前面：观测到底测量了什么，残差采用哪一个方向，姿态误差位于哪个坐标系，某个观测对 15 维状态中的哪些分量敏感。

本文固定上一篇文章的约定。$R_{WB}$ 把机体系 $B$ 的向量变换到世界系 $W$，姿态使用右侧扰动

$$
R_{WB}=\hat R_{WB}\operatorname{Exp}([\delta\theta]_\times),
$$

误差状态排列为

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

文章先从一般观测模型 $z=h(\mathcal X)+n$ 推导残差和 $H$ 的定义，再逐项推导位置、速度、姿态、世界重力和静止加速度计观测。最后用 LiDAR 点到平面约束做一个几何例子，并说明观测更新、误差注入和 reset 如何组成完整闭环。

读完之后，看到一个新的传感器模型，可以按同一套步骤自己写出 $H$，而不是从某篇论文或代码中复制一个看起来相似的 block 矩阵。

**关键词：** ESKF；观测模型；观测残差；H 矩阵；误差状态；姿态 Jacobian；LiDAR 点到平面

## 1. 先回答：下一篇为什么是观测误差和 $H$

上一篇推导了误差状态怎样随 IMU 传播：

$$
\dot{\delta x}=F\delta x+Gw.
$$

它回答的是：在两次外部观测之间，误差会怎样变大、怎样互相影响。

当相机、GNSS、轮速计或 LiDAR 的新数据到来时，滤波器需要回答另一个问题：

> **当前这条观测，对误差状态中的哪些方向敏感？**

这个问题由观测 Jacobian $H$ 描述。若观测维度为 $m$，误差状态维度为 $15$，那么

$$
H\in\mathbb R^{m\times15}.
$$

它的每一列对应一个误差方向，每一行对应一个观测分量。某个 block 为零，表示在当前观测模型和当前线性化点附近，该观测对相应误差的一阶变化不敏感；某个 block 非零，表示这个误差会改变预测观测。

可以把 $F$ 和 $H$ 放在一起比较：

| 矩阵 | 它回答的问题 | 典型形式 |
|---|---|---|
| $F$ | 误差怎样随时间传播 | $\dot{\delta x}=F\delta x+Gw$ |
| $H$ | 观测怎样感受到误差 | $r\approx H\delta x+n$ |

$F$ 是动力学的局部线性化，$H$ 是观测模型的局部线性化。两者都不是凭记忆填写的表格，都是对非线性模型求一阶导数的结果。

## 2. 先把约定固定下来

### 2.1 状态、坐标系和姿态误差

本文使用的完整状态为

$$
\mathcal X=(R_{WB},p_W,v_W,b_g,b_a).
$$

其中 $p_W$、$v_W$ 在世界系中表达，$b_g$、$b_a$ 在 IMU 机体系中表达。姿态矩阵的方向是

$$
q_W=R_{WB}q_B,
\qquad
q_B=R_{WB}^{\top}q_W.
$$

姿态采用右侧小扰动：

$$
R_{WB}=\hat R_{WB}\operatorname{Exp}([\delta\theta]_\times).
$$

因为误差在名义姿态右侧，$\delta\theta$ 的坐标表达位于名义机体系。其余状态采用加性误差：

$$
\begin{aligned}
p_W&=\hat p_W+\delta p,\\
v_W&=\hat v_W+\delta v,\\
b_g&=\hat b_g+\delta b_g,\\
b_a&=\hat b_a+\delta b_a.
\end{aligned}
$$

因此，后文所有观测 Jacobian 都按以下列顺序排列：

$$
H=\begin{bmatrix}H_\theta&H_p&H_v&H_{b_g}&H_{b_a}\end{bmatrix}.
$$

每个 block 的列数都是 $3$，但行数取决于观测维度。

### 2.2 观测噪声不要和旋转矩阵混用同一个符号

观测模型写成

$$
z=h(\mathcal X)+n,
$$

其中 $z\in\mathbb R^m$ 是传感器读数，$h(\mathcal X)$ 是给定状态后预测的读数，$n$ 是观测噪声。为避免和旋转矩阵 $R_{WB}$ 混淆，本文用 $\Sigma_z$ 表示噪声协方差：

$$
 n\sim\mathcal N(0,\Sigma_z).
$$

例如，GNSS 位置观测的 $\Sigma_z$ 是 $3\times3$ 矩阵；点到平面约束的观测是一个标量，$\Sigma_z$ 就是一个 $1\times1$ 的方差。

### 2.3 “观测误差”到底指什么

工程代码中，观测误差可能指两件不同的事：传感器自身的物理测量误差，或者实际测量和预测测量之间的差。本文把后者称为观测残差，也称 innovation：

$$
r\triangleq z-h(\hat{\mathcal X}^-).
$$

这里 $\hat{\mathcal X}^-$ 是融合当前观测之前的预测名义状态。传感器噪声 $n$ 则属于观测模型的一部分，不和残差混为一谈。

这一区分很有用。滤波器并不直接问“这次传感器误差是多少”，因为真实状态未知；它能计算的是“实际读数和当前状态预测出的读数相差多少”。

## 3. 一般观测模型如何得到 $H$

### 3.1 从真实状态到预测状态

非线性观测模型为

$$
z=h(\mathcal X)+n.
$$

实际滤波器手里只有预测名义状态 $\hat{\mathcal X}^-$，先计算预测观测：

$$
\hat z=h(\hat{\mathcal X}^-).
$$

真实状态写成预测名义状态加上误差：

$$
\mathcal X=\hat{\mathcal X}^-\boxplus\delta x.
$$

于是实际测量可以写成

$$
z=h(\hat{\mathcal X}^-\boxplus\delta x)+n.
$$

残差为

$$
\begin{aligned}
r
&=z-h(\hat{\mathcal X}^-)\\
&=h(\hat{\mathcal X}^-\boxplus\delta x)-h(\hat{\mathcal X}^-)+n.
\end{aligned}
$$

### 3.2 一阶展开

在 $\delta x=0$ 附近做一阶 Taylor 展开：

$$
h(\hat{\mathcal X}^-\boxplus\delta x)
\approx
h(\hat{\mathcal X}^-)+H\delta x.
$$

其中

$$
\boxed{
H\triangleq
\left.
\frac{\partial h(\hat{\mathcal X}^-\boxplus\delta x)}
{\partial\delta x}
\right|_{\delta x=0}
}
$$

就是观测模型对误差状态的 Jacobian。代回残差：

$$
\boxed{
r\approx H\delta x+n.}
$$

这就是 ESKF 观测更新使用的线性观测方程。

这里有一个经常被忽略的细节：$H$ 是对误差状态 $\delta x$ 求导，不是简单地对完整状态中的 $R$、$p$、$v$、$b_g$、$b_a$ 做普通偏导。对位置和速度来说，两者看起来一样；对姿态来说，必须先把右侧扰动放进 $R=\hat R\operatorname{Exp}([\delta\theta]_\times)$，再求导。

### 3.3 残差方向和 $H$ 的符号

本文采用

$$
r=z-\hat z.
$$

如果你改用相反的残差

$$
r'=\hat z-z=-r,
$$

那么线性模型必须同时改成

$$
r'\approx -H\delta x-n.
$$

这时如果把残差取反，却继续使用原来的 $H$，滤波器的修正方向会反过来。代码可以选择任意一种残差方向，但残差、$H$ 和噪声项必须保持同一套约定。

### 3.4 从 $H$ 进入 Kalman 更新

有了残差模型

$$
r\approx H\delta x+n,
$$

以及预测误差协方差 $P^-$，先计算残差协方差：

$$
S=HP^-H^\top+\Sigma_z.
$$

Kalman gain 为

$$
K=P^-H^\top S^{-1}.
$$

滤波器更新的是局部误差状态均值：

$$
\delta\hat x=Kr.
$$

可以把这三步理解为：$H$ 先把状态误差投影到观测空间，$S$ 衡量这个投影加上噪声后的不确定性，$K$ 再把观测残差送回状态空间。

此时不要把 $\delta\hat x$ 直接加到完整状态上。它还要经过后文的误差注入与 reset。

### 3.5 从概率模型推导 Kalman 更新

前面的公式说明了更新怎么写，下面解释这些公式为什么是这个形式。推导只使用一个线性高斯模型，因此不依赖 ESKF 的具体传感器。ESKF 的作用是先把非线性观测在误差状态附近变成这个模型。

#### 3.5.1 先写出先验和观测的概率模型

在当前观测到来之前，ESKF 已经通过 IMU 传播得到了预测误差协方差 $P^-$。reset 后误差状态的均值被重新定义为零，所以先验可以写成

$$
\delta x\sim\mathcal N(0,P^-).
$$

刚才得到的线性观测模型是

$$
r=H\delta x+n,
\qquad
n\sim\mathcal N(0,\Sigma_z).
$$

给定某个候选误差 $\delta x$，残差的条件分布为

$$
r\mid\delta x
\sim
\mathcal N(H\delta x,\Sigma_z).
$$

滤波器要做的事情可以表述为：看到残差 $r$ 之后，求误差状态的后验分布 $p(\delta x\mid r)$。

#### 3.5.2 由 Bayes 公式得到代价函数

Bayes 公式给出

$$
p(\delta x\mid r)
\propto
p(r\mid\delta x)p(\delta x).
$$

把两个高斯分布的指数部分代入，负对数后验等价于最小化下面的代价函数：

$$
\begin{aligned}
J(\delta x)= {}&
\delta x^\top(P^-)^{-1}\delta x\\
&+(r-H\delta x)^\top
\Sigma_z^{-1}(r-H\delta x).
\end{aligned}
$$

这里采用的概率假设是：预测误差 $\delta x$ 和观测噪声 $n$ 都是零均值高斯向量，并且通常假设二者相互独立：

$$
\delta x\sim\mathcal N(0,P^-),
\qquad
n\sim\mathcal N(0,\Sigma_z),
\qquad
\operatorname{Cov}(\delta x,n)=0.
$$

第一项来自先验。它惩罚误差状态偏离 IMU 传播给出的零均值预测；$P^-$ 越小，偏离的代价越大。第二项来自观测。它惩罚候选误差无法解释当前残差；$\Sigma_z$ 越小，观测约束越强。

这就是一个带先验的加权最小二乘问题。Kalman Filter 可以看成在线递推地求解这类问题，并把历史数据压缩在当前的均值和协方差中。

#### 3.5.3 对代价函数求导

先把第二项展开：

$$
\begin{aligned}
&(r-H\delta x)^\top\Sigma_z^{-1}(r-H\delta x)\\
={}&r^\top\Sigma_z^{-1}r
-r^\top\Sigma_z^{-1}H\delta x\\
&-\delta x^\top H^\top\Sigma_z^{-1}r
+\delta x^\top H^\top\Sigma_z^{-1}H\delta x.
\end{aligned}
$$

因为 $\Sigma_z^{-1}$ 是对称矩阵，中间两个标量相等，可以合并为两倍的一次项：

$$
\begin{aligned}
J(\delta x)= {}&
\delta x^\top
\left((P^-)^{-1}+H^\top\Sigma_z^{-1}H\right)
\delta x\\
&-2\delta x^\top H^\top\Sigma_z^{-1}r
+r^\top\Sigma_z^{-1}r.
\end{aligned}
$$

对 $\delta x$ 求梯度：

$$
\begin{aligned}
\frac{\partial J}{\partial\delta x}
={}&2\left((P^-)^{-1}+H^\top\Sigma_z^{-1}H\right)\delta x\\
&-2H^\top\Sigma_z^{-1}r.
\end{aligned}
$$

令梯度为零，得到正规方程：

$$
\left((P^-)^{-1}+H^\top\Sigma_z^{-1}H\right)
\delta\hat x
=H^\top\Sigma_z^{-1}r.
$$

于是误差状态的后验均值首先可以写成信息形式：

$$
\boxed{
\delta\hat x
=\left((P^-)^{-1}+H^\top\Sigma_z^{-1}H\right)^{-1}
H^\top\Sigma_z^{-1}r.
}
$$

这个形式很能说明信息是如何累加的：先验信息矩阵是 $(P^-)^{-1}$，当前观测提供的信息矩阵是 $H^\top\Sigma_z^{-1}H$，两者相加后再求解误差。

#### 3.5.4 把正规方程改写成 Kalman gain 形式

### 直接定义 Kalman gain

为简化记号，令

$$
A\triangleq (P^-)^{-1}+H^\top\Sigma_z^{-1}H.
$$

信息形式已经写成

$$
\delta\hat x
=A^{-1}H^\top\Sigma_z^{-1}r.
$$

观察这个式子：右边是一个矩阵乘以残差 $r$。前面的矩阵负责把观测残差转换成误差状态修正，因此我们直接把它定义为 Kalman gain：

$$
\boxed{
K\triangleq A^{-1}H^\top\Sigma_z^{-1}.
}
$$

于是更新公式马上变成

$$
\boxed{
\delta\hat x=Kr.
}
$$

因此，$K$ 表示从观测残差到误差状态修正的线性映射。它的数值由先验协方差、观测 Jacobian 和观测噪声共同决定。

### 利用求逆引理得到观测空间形式

前面已经定义了信息形式下的 Kalman gain：

$$
K\triangleq A^{-1}H^\top\Sigma_z^{-1},
\qquad
A=(P^-)^{-1}+H^\top\Sigma_z^{-1}H.
$$

这个定义直接对应

$$
\delta\hat x=Kr.
$$

为了得到更适合工程计算的形式，使用矩阵求逆引理（Woodbury identity）的下面这个形式：

$$
\boxed{
\left(Q^{-1}+C^\top R^{-1}C\right)^{-1}C^\top R^{-1}
=QC^\top\left(CQC^\top+R\right)^{-1}.
}
$$

在当前问题中令

$$
Q=P^-,
\qquad
C=H,
\qquad
R=\Sigma_z.
$$

那么求逆引理的左侧正好是信息形式中的 $K$：

$$
\begin{aligned}
\left(Q^{-1}+C^\top R^{-1}C\right)^{-1}C^\top R^{-1}
&=\left((P^-)^{-1}+H^\top\Sigma_z^{-1}H\right)^{-1}
  H^\top\Sigma_z^{-1}\\
&=A^{-1}H^\top\Sigma_z^{-1}\\
&=K.
\end{aligned}
$$

求逆引理的右侧则变为

$$
QC^\top\left(CQC^\top+R\right)^{-1}
=P^-H^\top\left(HP^-H^\top+\Sigma_z\right)^{-1}.
$$

因此，$K$ 可以直接改写为

$$
\boxed{
K
=P^-H^\top\left(HP^-H^\top+\Sigma_z\right)^{-1}.
}
$$

记残差协方差为

$$
S\triangleq HP^-H^\top+\Sigma_z,
$$

则上式就是熟悉的 Kalman gain 形式：

$$
\boxed{
K=P^-H^\top S^{-1}.
}
$$

这里的关键是：求逆引理没有改变 $K$，只是把原来 $15\times15$ 矩阵 $A$ 的求逆，改写成了观测空间中 $m\times m$ 矩阵 $S$ 的求逆。像素观测通常为 $m=2$，点到平面观测通常为 $m=1$。数值实现中也不需要显式形成 $S^{-1}$，而是通过线性方程求解器计算 $P^-H^\top S^{-1}$。

#### 求逆引理的一个证明

为了证明上面的求逆引理，记

$$
L\triangleq Q^{-1}+C^\top R^{-1}C,
\qquad
M\triangleq CQC^\top+R,
$$

并定义

$$
X\triangleq QC^\top M^{-1}.
$$

将 $X$ 左乘 $L$，逐步展开：

$$
\begin{aligned}
LX
&=\left(Q^{-1}+C^\top R^{-1}C\right)
  QC^\top M^{-1}\\
&=\left(C^\top+C^\top R^{-1}CQC^\top\right)M^{-1}\\
&=C^\top\left(I+R^{-1}CQC^\top\right)M^{-1}\\
&=C^\top R^{-1}\left(R+CQC^\top\right)M^{-1}\\
&=C^\top R^{-1}MM^{-1}\\
&=C^\top R^{-1}.
\end{aligned}
$$

由于 $L$ 可逆，两边左乘 $L^{-1}$，得到

$$
X=L^{-1}C^\top R^{-1}.
$$

再代回 $L$、$M$ 和 $X$ 的定义：

$$
QC^\top\left(CQC^\top+R\right)^{-1}
=\left(Q^{-1}+C^\top R^{-1}C\right)^{-1}C^\top R^{-1}.
$$

这就证明了前面使用的矩阵求逆引理。

最终，误差状态更新仍然是

$$
\delta\hat x=Kr.
$$

信息形式适合从概率模型推导更新，观测空间形式适合实际计算；二者通过求逆引理完全等价。

#### 3.5.5 $S$ 为什么是残差协方差

Kalman gain 中的矩阵

$$
S=HP^-H^\top+\Sigma_z
$$

也可以直接从残差的随机变量表达式看出来：

$$
r=H\delta x+n.
$$

由于先验误差和观测噪声相互独立，且二者均值为零，

$$
\begin{aligned}
\operatorname{Cov}(r)
&=\operatorname{Cov}(H\delta x+n)\\
&=H\operatorname{Cov}(\delta x)H^\top
+\operatorname{Cov}(n)\\
&=HP^-H^\top+\Sigma_z.
\end{aligned}
$$

所以 $S$ 不是为了让公式看起来完整而添加的中间量。它就是当前残差实际具有的不确定性：一部分来自预测状态误差投影到观测空间，另一部分来自传感器本身的噪声。

如果 $S$ 很大，说明当前残差本身不确定，单次残差对状态的修正会变小；如果 $S$ 较小，说明这条残差更值得信任。

#### 3.5.6 后验协方差从哪里来

代价函数的二次项矩阵就是注入前的后验信息矩阵：

$$
(\widetilde P^+)^{-1}
=(P^-)^{-1}+H^\top\Sigma_z^{-1}H.
$$

因此，误差注入前的后验协方差在信息形式下为

$$
\widetilde P^+
=\left((P^-)^{-1}
+H^\top\Sigma_z^{-1}H\right)^{-1}.
$$

利用和上面相同的矩阵恒等式，可以把它改写成 Kalman 形式：

$$
\boxed{
\widetilde P^+
=P^--P^-H^\top S^{-1}HP^-.
}
$$

这里用 $\widetilde P^+$ 表示误差注入之前的后验协方差。它描述的还是预测名义状态附近那套误差坐标；注入之后还需要通过 reset Jacobian 转换。

还可以从更新后的估计误差直接验证这个结果。定义

$$
e^+=\delta x-\delta\hat x.
$$

由于 $\delta\hat x=Kr$ 且 $r=H\delta x+n$，有

$$
 e^+=(I-KH)\delta x-Kn.
$$

因此

$$
\boxed{
\widetilde P^+
=(I-KH)P^-(I-KH)^\top
+K\Sigma_zK^\top.
}
$$

这就是 Joseph 形式。现在把

$$
S=HP^-H^\top+\Sigma_z,
\qquad
K=P^-H^\top S^{-1}
$$

代入并逐项展开：

$$
\begin{aligned}
\widetilde P^+
&=(I-KH)P^-(I-KH)^\top+K\Sigma_zK^\top\\
&=P^- -KHP^- -P^-H^\top K^\top
  +K\left(HP^-H^\top+\Sigma_z\right)K^\top\\
&=P^- -KHP^- -P^-H^\top K^\top+KSK^\top.
\end{aligned}
$$

关键的一步是利用 Kalman gain 的定义：

$$
KS
=P^-H^\top S^{-1}S
=P^-H^\top.
$$

因此

$$
KSK^\top=P^-H^\top K^\top,
$$

上式中的两项正好抵消：

$$
\begin{aligned}
\widetilde P^+
&=P^- -KHP^-\\
&=P^- -P^-H^\top S^{-1}HP^-.
\end{aligned}
$$

所以，下面三种写法在标准 Kalman gain 条件下是同一个后验协方差：

$$
\boxed{
\begin{aligned}
\widetilde P^+
&=(I-KH)P^-\\
&=P^- -P^-H^\top S^{-1}HP^-\\
&=(I-KH)P^-(I-KH)^\top+K\Sigma_zK^\top.
\end{aligned}
}
$$

这里的等价关系依赖于

$$
K=P^-H^\top S^{-1},
\qquad
S=HP^-H^\top+\Sigma_z.
$$

如果 $K$ 是任意矩阵，而不是这个 Kalman gain，上面的 Joseph 形式一般不能直接简化为 $(I-KH)P^-$。此外，在精确数学中通常假设 $P^-$ 和 $\Sigma_z$ 对称、$S$ 可逆，因此减法形式也保持对称性。

在数学上这些形式等价；在浮点计算中，Joseph 形式通常更适合保持协方差的对称性和半正定性。因此实际实现常用

$$
\widetilde P^+
=(I-KH)P^-(I-KH)^\top
+K\Sigma_zK^\top
$$

而不是直接使用化简后的表达式。

#### 3.5.7 用一维例子理解 Kalman gain

把所有矩阵暂时换成标量。设先验误差方差为 $p$，观测模型为

$$
r=\delta x+n,
\qquad
\operatorname{Var}(n)=\sigma^2.
$$

此时

$$
K=\frac{p}{p+\sigma^2},
\qquad
\delta\hat x=Kr.
$$

如果先验很不确定，$p\gg\sigma^2$，则

$$
K\approx1,
$$

滤波器更相信观测残差；如果传感器噪声很大，$\sigma^2\gg p$，则

$$
K\approx0,
$$

滤波器主要保留 IMU 预测。

多维情况下，$P^-H^\top$ 还会把残差传播回相关的状态方向，$S^{-1}$ 则按照观测空间中的不确定性进行加权。于是 Kalman gain 不是一个固定的“观测权重”，而是由预测协方差、观测 Jacobian 和观测噪声共同决定的矩阵。

## 4. 位置观测：最简单的 $H$

### 4.1 观测模型

假设外部传感器直接给出 IMU 原点在世界系中的位置：

$$
z_p=p_W+n_p.
$$

这是一个三维观测，$z_p\in\mathbb R^3$。预测观测是

$$
\hat z_p=\hat p_W.
$$

残差为

$$
r_p=z_p-\hat p_W.
$$

### 4.2 代入误差状态

真实位置为

$$
p_W=\hat p_W+\delta p.
$$

所以

$$
\begin{aligned}
z_p
&=\hat p_W+\delta p+n_p,\\
r_p
&=z_p-\hat p_W\\
&\approx\delta p+n_p.
\end{aligned}
$$

因此

$$
\boxed{
H_p=
\begin{bmatrix}
0&I&0&0&0
\end{bmatrix}.
}
$$

这里的 $0$ 和 $I$ 都是 $3\times3$ block，因此 $H_p$ 是 $3\times15$。

这个结果很直观：位置观测对位置误差敏感，对姿态、速度和两个 bias 没有直接的一阶敏感性。

### 4.3 “没有直接敏感”不等于“永远不影响”

$H_p$ 中姿态和 bias block 为零，不代表位置观测无法间接修正姿态或 bias。预测协方差 $P^-$ 中通常有交叉协方差，例如位置和姿态、位置和加速度计 bias 之间的相关性：

$$
P^-_{p\theta}\neq0,
\qquad
P^-_{p b_a}\neq0.
$$

Kalman gain 使用的是

$$
K=P^-H_p^\top S^{-1}.
$$

即使 $H_p$ 只直接读取位置，$P^-H_p^\top$ 仍然可能在姿态、速度和 bias 行上非零。因此外部位置观测可以通过传播过程中形成的相关性修正其他状态。

这也是读 $H$ 矩阵时要注意的地方：$H$ 描述当前观测的直接敏感性，$K$ 决定这条信息最终会修正哪些状态。

## 5. 速度观测：把 $p$ 换成 $v$

### 5.1 观测模型和残差

如果轮速计或外部速度估计器给出世界系速度观测：

$$
z_v=v_W+n_v,
$$

则

$$
\hat z_v=\hat v_W,
\qquad
r_v=z_v-\hat v_W.
$$

代入

$$
v_W=\hat v_W+\delta v,
$$

得到

$$
 r_v\approx\delta v+n_v.
$$

所以

$$
\boxed{
H_v=
\begin{bmatrix}
0&0&I&0&0
\end{bmatrix}.
}
$$

同样，$H_v$ 是 $3\times15$。

### 5.2 速度坐标系必须先说清楚

上面的模型假设观测是世界系速度。如果轮速计给出的是机体系前向速度，观测模型就不是 $z_v=v_W+n_v$。

例如，假设传感器测量机体系中的速度：

$$
z_{v_B}=R_{WB}^{\top}v_W+n_{v_B}.
$$

预测值为

$$
\hat z_{v_B}=\hat R_{WB}^{\top}\hat v_W.
$$

把真实状态代入：

$$
\begin{aligned}
R_{WB}^{\top}v_W
&=\operatorname{Exp}(-[\delta\theta]_\times)
\hat R_{WB}^{\top}(\hat v_W+\delta v)\\
&\approx
( I-[\delta\theta]_\times )
(\hat v_B+\hat R_{WB}^{\top}\delta v)\\
&\approx
\hat v_B-[\delta\theta]_\times\hat v_B
+\hat R_{WB}^{\top}\delta v,
\end{aligned}
$$

其中

$$
\hat v_B\triangleq\hat R_{WB}^{\top}\hat v_W.
$$

利用

$$
-[\delta\theta]_\times\hat v_B
=[\hat v_B]_\times\delta\theta,
$$

可得

$$
r_{v_B}
\approx
[\hat v_B]_\times\delta\theta
+\hat R_{WB}^{\top}\delta v+n_{v_B}.
$$

所以机体系速度观测的 Jacobian 是

$$
\boxed{
H_{v_B}=
\begin{bmatrix}
[\hat v_B]_\times&0&\hat R_{WB}^{\top}&0&0
\end{bmatrix}.
}
$$

同一个“速度观测”，只因为输出坐标系不同，$H$ 就从一个只含速度 block 的矩阵变成了同时含姿态和速度 block 的矩阵。写 Jacobian 前先确认传感器给的是哪个坐标系中的量。

## 6. 姿态观测：不能用矩阵相减

### 6.1 一个适合旋转的观测模型

假设视觉、磁力计或其他外部模块给出姿态观测 $z_R\in SO(3)$。采用右侧旋转噪声模型：

$$
z_R=R_{WB}\operatorname{Exp}([\eta_R]_\times),
$$

其中 $\eta_R\in\mathbb R^3$ 是小角度观测噪声。

旋转没有普通向量意义下的减法，因此残差不能写成

$$
z_R-\hat R_{WB}.
$$

可以把两者相乘得到相对旋转，再取对数映射：

$$
\rho_R
\triangleq
\operatorname{Log}\left(\hat R_{WB}^{\top}z_R\right)^\vee.
$$

这里 $\vee$ 把反对称矩阵转换为对应的三维向量。

### 6.2 代入右侧姿态误差

由

$$
R_{WB}=\hat R_{WB}\operatorname{Exp}([\delta\theta]_\times)
$$

和观测模型，得到

$$
\begin{aligned}
\hat R_{WB}^{\top}z_R
&=\hat R_{WB}^{\top}R_{WB}
\operatorname{Exp}([\eta_R]_\times)\\
&=\operatorname{Exp}([\delta\theta]_\times)
\operatorname{Exp}([\eta_R]_\times).
\end{aligned}
$$

在两个量都足够小时，Baker-Campbell-Hausdorff 展开的一阶结果是

$$
\operatorname{Log}
\left(\operatorname{Exp}([\delta\theta]_\times)
\operatorname{Exp}([\eta_R]_\times)\right)^\vee
\approx\delta\theta+\eta_R.
$$

因此

$$
\rho_R\approx\delta\theta+\eta_R.
$$

姿态观测的 Jacobian 为

$$
\boxed{
H_R=
\begin{bmatrix}
I&0&0&0&0
\end{bmatrix}.
}
$$

### 6.3 乘法顺序改变，结果也会改变

上面的简单结果依赖三个约定：右侧姿态误差、右侧观测噪声，以及残差

$$
\operatorname{Log}(\hat R^{\top}z_R)^\vee.
$$

如果观测噪声改放到左侧，或者残差改成

$$
\operatorname{Log}(z_R^{\top}\hat R)^\vee,
$$

误差向量的坐标系和符号都会变化。不能看到两个旋转矩阵，就直接把 $H_\theta$ 填成 $I$。正确做法是把具体的乘法顺序写出来，再在单位元附近线性化。

## 7. 重力观测：姿态误差 Jacobian 的一个典型来源

重力观测很适合练习右侧姿态扰动，因为它只观测一个世界系方向。设世界系重力加速度为 $g_W$，外部模块给出机体系重力向量：

$$
z_g=R_{WB}^{\top}g_W+n_g.
$$

这里的 $n_g$ 是观测噪声，不是上一篇 IMU 误差动力学中的陀螺仪噪声；符号相同可能造成混淆，实际代码中应使用更具体的命名。

### 7.1 预测观测

定义名义姿态下的重力投影：

$$
\hat g_B\triangleq\hat R_{WB}^{\top}g_W.
$$

预测观测是

$$
\hat z_g=\hat g_B.
$$

### 7.2 展开真实重力投影

由右侧姿态误差

$$
R_{WB}^{\top}
=\operatorname{Exp}(-[\delta\theta]_\times)
\hat R_{WB}^{\top},
$$

有

$$
\begin{aligned}
R_{WB}^{\top}g_W
&=\operatorname{Exp}(-[\delta\theta]_\times)\hat g_B\\
&\approx (I-[\delta\theta]_\times)\hat g_B\\
&=\hat g_B-[\delta\theta]_\times\hat g_B.
\end{aligned}
$$

利用叉乘交换关系：

$$
-[\delta\theta]_\times\hat g_B
=[\hat g_B]_\times\delta\theta,
$$

因此

$$
R_{WB}^{\top}g_W
\approx
\hat g_B+[\hat g_B]_\times\delta\theta.
$$

代回残差：

$$
\begin{aligned}
r_g
&=z_g-\hat g_B\\
&\approx[\hat g_B]_\times\delta\theta+n_g.
\end{aligned}
$$

所以

$$
\boxed{
H_g=
\begin{bmatrix}
[\hat g_B]_\times&0&0&0&0
\end{bmatrix}.
}
$$

这个 $H_g$ 是 $3\times15$，但 $[\hat g_B]_\times$ 的秩最多为 $2$。沿重力方向旋转不会改变重力向量，所以纯重力方向观测不能约束绕重力的 yaw 误差：

$$
[\hat g_B]_\times\hat g_B=0.
$$

这不是数值实现的缺陷，而是观测模型本身的几何退化。

### 7.3 静止加速度计不是同一个符号

上一篇文章使用的加速度计模型为

$$
\tilde a
=R_{WB}^{\top}(a_W-g_W)+b_a+n_a.
$$

静止时 $a_W=0$，所以理想加速度计读数是

$$
z_a=-R_{WB}^{\top}g_W+b_a+n_a.
$$

注意这里是 $-R_{WB}^{\top}g_W$，因为加速度计测量比力，不是重力加速度本身。

定义

$$
\hat a_g\triangleq-\hat R_{WB}^{\top}g_W.
$$

真实观测的一阶展开为

$$
\begin{aligned}
z_a
&=-\operatorname{Exp}(-[\delta\theta]_\times)
\hat R_{WB}^{\top}g_W
+\hat b_a+\delta b_a+n_a\\
&\approx
-\hat R_{WB}^{\top}g_W
-[\hat g_B]_\times\delta\theta
+\hat b_a+\delta b_a+n_a.
\end{aligned}
$$

因此

$$
 r_a
\approx
-[\hat g_B]_\times\delta\theta
+\delta b_a+n_a,
$$

对应的 Jacobian 是

$$
\boxed{
H_a=
\begin{bmatrix}
-[\hat g_B]_\times&0&0&0&I
\end{bmatrix}.
}
$$

这两个矩阵很容易写反：纯重力向量观测的姿态 block 是 $+[\hat g_B]_\times$，静止比力观测的姿态 block 是 $-[\hat g_B]_\times$，并且后者还多了加速度计 bias block $I$。

这也解释了为什么静止时不能仅凭加速度计均值同时精确得到姿态和加速度计 bias。两者都进入同一个观测通道，线性化后会产生耦合。

### 7.4 如果只使用重力方向

有些系统不使用加速度计的幅值，只使用归一化方向：

$$
\bar z_a=\frac{z_a}{\lVert z_a\rVert}.
$$

此时不能直接把未归一化观测的 $H_a$ 当成方向观测的 Jacobian。对归一化函数

$$
\nu(x)=\frac{x}{\lVert x\rVert}
$$

其 Jacobian 为

$$
\frac{\partial\nu}{\partial x}
=\frac{1}{\lVert x\rVert}
\left(I-\nu\nu^\top\right).
$$

若 $H_{a,\mathrm{raw}}$ 是原始比力观测的 Jacobian，则方向观测的 Jacobian 近似为

$$
H_{a,\mathrm{dir}}
=\frac{1}{\lVert\hat a_g\rVert}
\left(I-\hat u\hat u^\top\right)H_{a,\mathrm{raw}},
$$

其中

$$
\hat u=\frac{\hat a_g}{\lVert\hat a_g\rVert}.
$$

投影矩阵 $I-\hat u\hat u^\top$ 会去掉沿向量自身的幅值变化，只保留方向变化。因此归一化后的观测通常只提供两个独立约束。

## 8. LiDAR 点到平面观测：把几何关系写成 $H$

前面的例子直接读取状态中的位置、速度或重力投影。LiDAR 点到平面约束更接近实际 LIO：观测不是状态的某一个分量，而是由姿态、位置和点坐标共同组成的几何量。

### 8.1 几何模型

设一个 LiDAR 点已经转换到 IMU 机体系，坐标为 $q_B$。它在世界系中的位置为

$$
q_W=p_W+R_{WB}q_B.
$$

设该点对应的世界系平面满足

$$
 n_W^\top x_W=d,
$$

其中 $n_W$ 是单位法向量，$d$ 是平面到世界原点的有符号距离。

理想情况下，点落在平面上：

$$
 n_W^\top q_W=d.
$$

把它写成标量观测模型：

$$
z_\pi=d+n_\pi,
$$

$$
h_\pi(\mathcal X)=n_W^\top(p_W+R_{WB}q_B).
$$

残差采用本文统一的“实际观测减预测观测”：

$$
r_\pi=z_\pi-h_\pi(\hat{\mathcal X}).
$$

如果实现中习惯使用点到平面的代数残差 $h_\pi-z_\pi$，只需要把整个残差和整个 Jacobian 同时取反。

### 8.2 位置部分

先展开位置：

$$
 p_W=\hat p_W+\delta p.
$$

位置引起的预测观测变化为

$$
 n_W^\top p_W
=n_W^\top\hat p_W+n_W^\top\delta p.
$$

因此位置 block 是 $n_W^\top$。

### 8.3 姿态部分

再处理旋转后的点。由

$$
R_{WB}=\hat R_{WB}\operatorname{Exp}([\delta\theta]_\times)
$$

和一阶近似，

$$
\begin{aligned}
R_{WB}q_B
&\approx\hat R_{WB}(I+[\delta\theta]_\times)q_B\\
&=\hat R_{WB}q_B+\hat R_{WB}[\delta\theta]_\times q_B.
\end{aligned}
$$

利用

$$
[\delta\theta]_\times q_B
=-[q_B]_\times\delta\theta,
$$

得到

$$
R_{WB}q_B
\approx
\hat R_{WB}q_B-\hat R_{WB}[q_B]_\times\delta\theta.
$$

定义名义世界系点坐标

$$
\hat q_W\triangleq\hat R_{WB}q_B.
$$

则点到平面预测值的一阶展开为

$$
\begin{aligned}
h_\pi(\mathcal X)
&\approx n_W^\top(\hat p_W+\hat q_W)\\
&\quad+n_W^\top\delta p
-n_W^\top\hat R_{WB}[q_B]_\times\delta\theta.
\end{aligned}
$$

因此，按照 $r=z-h(\hat{\mathcal X})$ 的约定，残差满足

$$
 r_\pi
\approx
-n_W^\top\hat R_{WB}[q_B]_\times\delta\theta
+n_W^\top\delta p+n_\pi.
$$

对应的 $1\times15$ Jacobian 为

$$
\boxed{
H_\pi=
\begin{bmatrix}
-n_W^\top\hat R_{WB}[q_B]_\times
&n_W^\top
&0
&0
&0
\end{bmatrix}.
}
$$

### 8.4 这个 Jacobian 的几何意义

姿态 block

$$
-n_W^\top\hat R_{WB}[q_B]_\times
$$

表示：机体绕一个小角度转动时，点的位置如何移动，以及这个移动在平面法向方向上有多少分量。

位置 block $n_W^\top$ 表示：沿平面法向移动一点，点到平面的距离就会改变；沿平面切向移动，一阶距离不变。确实，如果 $t_W$ 是平面内的切向量，满足 $n_W^\top t_W=0$，那么

$$
H_p t_W=n_W^\top t_W=0.
$$

这说明单个平面约束不能约束沿平面切向的平移。多个方向不同的平面，或者连续帧中的运动，才能逐渐消除这些退化方向。

### 8.5 外参不能被悄悄省略

上面把 $q_B$ 当作已知的 IMU 系点坐标。实际 LiDAR 点通常首先位于 LiDAR 系 $L$，需要通过外参变换：

$$
q_B=t_{BL}+R_{BL}q_L.
$$

这里的具体下标含义必须由定义确认。若外参固定，$q_B$ 可以在构造观测时先算好；若外参也在状态中估计，$H$ 还要增加对应的外参 block。

最容易出错的做法是：法向量用世界系、点用 LiDAR 系、旋转矩阵却按 IMU 到世界系套公式。每一项放入点到平面方程前，都必须已经在同一个坐标系中。

### 8.6 视觉重投影误差：从世界点到像素坐标

视觉观测是 ESKF 中最经典的一类观测。相机并不直接测量位置或姿态，而是测量一个世界点在图像上的像素位置。这个观测模型包含坐标变换和透视除法，正好可以把前面的姿态误差、位置误差和链式求导串起来。

下面先使用一个简化但完整的模型：地图点在世界系中已知，相机内参和 IMU-相机外参已知，状态中暂时不估计地图点和外参。最后再说明这些假设改变后 $H$ 如何扩展。

#### 8.6.1 相机观测模型

设世界系中的地图点为 $P_W$。相机坐标系记为 $C$，从 IMU 系 $B$ 到相机系 $C$ 的固定外参为

$$
p_C=R_{CB}p_B+t_{CB},
$$

其中 $R_{CB}$ 把机体系向量变换到相机系，$t_{CB}$ 是 IMU 原点在相机系中的坐标。

先把世界点变换到 IMU 系。由于 $R_{WB}$ 是 body-to-world 旋转，

$$
\ell_B=R_{WB}^{\top}(P_W-p_W).
$$

再变换到相机系：

$$
\ell_C=R_{CB}\ell_B+t_{CB}.
$$

记

$$
\ell_C=
\begin{bmatrix}
X_C\\Y_C\\Z_C
\end{bmatrix},
\qquad Z_C>0.
$$

采用理想针孔模型，像素预测为

$$
\pi(\ell_C)=
\begin{bmatrix}
 f_xX_C/Z_C+c_x\\
 f_yY_C/Z_C+c_y
\end{bmatrix}.
$$

实际相机观测为

$$
z_u=\pi(\ell_C)+n_u,
$$

其中 $z_u=[u,v]^\top$ 是二维像素观测，$n_u$ 是像素噪声。预测名义状态下的点坐标和像素为

$$
\hat\ell_B=\hat R_{WB}^{\top}(P_W-\hat p_W),
$$

$$
\hat\ell_C=R_{CB}\hat\ell_B+t_{CB},
$$

$$
\hat z_u=\pi(\hat\ell_C).
$$

本文继续采用实际观测减预测观测的残差：

$$
 r_u=z_u-\hat z_u.
$$

#### 8.6.2 先求相机系点坐标对状态误差的导数

这一步先不做像素投影，只研究 $\ell_C$ 如何变化。将真实状态代入 IMU 系点坐标：

$$
\begin{aligned}
\ell_B
&=R_{WB}^{\top}(P_W-p_W)\\
&=\operatorname{Exp}(-[\delta\theta]_\times)
\hat R_{WB}^{\top}(P_W-\hat p_W-\delta p).
\end{aligned}
$$

定义名义 IMU 系点坐标

$$
\hat\ell_B\triangleq
\hat R_{WB}^{\top}(P_W-\hat p_W).
$$

于是

$$
\ell_B
=\operatorname{Exp}(-[\delta\theta]_\times)
\left(\hat\ell_B-\hat R_{WB}^{\top}\delta p\right).
$$

使用

$$
\operatorname{Exp}(-[\delta\theta]_\times)
\approx I-[\delta\theta]_\times,
$$

得到

$$
\begin{aligned}
\ell_B
&\approx
\left(I-[\delta\theta]_\times\right)
\left(\hat\ell_B-\hat R_{WB}^{\top}\delta p\right)\\
&\approx
\hat\ell_B
-[\delta\theta]_\times\hat\ell_B
-\hat R_{WB}^{\top}\delta p.
\end{aligned}
$$

最后一项中的

$$
[\delta\theta]_\times\hat R_{WB}^{\top}\delta p
$$

包含两个误差量，是二阶项，需要舍去。再使用叉乘交换关系

$$
-[\delta\theta]_\times\hat\ell_B
=[\hat\ell_B]_\times\delta\theta,
$$

可得

$$
\boxed{
\ell_B
\approx
\hat\ell_B
+[\hat\ell_B]_\times\delta\theta
-\hat R_{WB}^{\top}\delta p.
}
$$

因此，IMU 系点坐标的一阶变化为

$$
\delta\ell_B
=[\hat\ell_B]_\times\delta\theta
-\hat R_{WB}^{\top}\delta p.
$$

接着通过固定外参变到相机系：

$$
\begin{aligned}
\ell_C
&=R_{CB}\ell_B+t_{CB}\\
&\approx
\hat\ell_C
+R_{CB}[\hat\ell_B]_\times\delta\theta
-R_{CB}\hat R_{WB}^{\top}\delta p.
\end{aligned}
$$

所以

$$
\boxed{
\delta\ell_C
=R_{CB}[\hat\ell_B]_\times\delta\theta
-R_{CB}\hat R_{WB}^{\top}\delta p.
}
$$

先得到这一步很重要。透视投影只是把三维相机点再映射到二维像素；如果坐标变换的 Jacobian 已经写错，后面的投影矩阵再正确也没有用。

#### 8.6.3 再求像素对相机点的导数

对针孔投影

$$
\pi(\ell_C)=
\begin{bmatrix}
 f_xX_C/Z_C+c_x\\
 f_yY_C/Z_C+c_y
\end{bmatrix}
$$

求一阶导数。对第一行分别求 $X_C$、$Y_C$、$Z_C$ 的偏导：

$$
\frac{\partial u}{\partial X_C}=\frac{f_x}{Z_C},
\qquad
\frac{\partial u}{\partial Y_C}=0,
\qquad
\frac{\partial u}{\partial Z_C}=-\frac{f_xX_C}{Z_C^2}.
$$

对第二行：

$$
\frac{\partial v}{\partial X_C}=0,
\qquad
\frac{\partial v}{\partial Y_C}=\frac{f_y}{Z_C},
\qquad
\frac{\partial v}{\partial Z_C}=-\frac{f_yY_C}{Z_C^2}.
$$

在名义相机点 $\hat\ell_C=[\hat X_C,\hat Y_C,\hat Z_C]^\top$ 处，投影 Jacobian 为

$$
\boxed{
J_\pi(\hat\ell_C)
=\begin{bmatrix}
\dfrac{f_x}{\hat Z_C}&0&-\dfrac{f_x\hat X_C}{\hat Z_C^2}\\[6pt]
0&\dfrac{f_y}{\hat Z_C}&-\dfrac{f_y\hat Y_C}{\hat Z_C^2}
\end{bmatrix}.
}
$$

它是一个 $2\times3$ 矩阵，把相机系中的三维点误差转换为像素误差：

$$
\delta z_u
=J_\pi(\hat\ell_C)\delta\ell_C.
$$

这里出现的 $1/\hat Z_C$ 和 $1/\hat Z_C^2$ 来自透视除法。点越靠近相机，像素对三维位置变化越敏感；当 $\hat Z_C$ 接近零时，线性化会变得非常不稳定，这也是投影前必须检查点在相机前方且深度足够的原因。

#### 8.6.4 用链式法则组装 $H$

将相机点对误差状态的导数和投影 Jacobian 相乘：

$$
\begin{aligned}
\delta z_u
&=J_\pi(\hat\ell_C)
\left(
R_{CB}[\hat\ell_B]_\times\delta\theta
-R_{CB}\hat R_{WB}^{\top}\delta p
\right)\\
&=J_\pi(\hat\ell_C)R_{CB}[\hat\ell_B]_\times\delta\theta\\
&\quad-J_\pi(\hat\ell_C)R_{CB}\hat R_{WB}^{\top}\delta p.
\end{aligned}
$$

因为当前假设下像素观测不直接依赖速度和两个 IMU bias，所以

$$
\boxed{
H_u
=\begin{bmatrix}
J_\pi(\hat\ell_C)R_{CB}[\hat\ell_B]_\times
&-J_\pi(\hat\ell_C)R_{CB}\hat R_{WB}^{\top}
&0
&0
&0
\end{bmatrix}.
}
$$

矩阵尺寸为

$$
H_u\in\mathbb R^{2\times15}.
$$

将它代回观测残差：

$$
\boxed{
 r_u\approx H_u\delta x+n_u.
}
$$

这就是固定路标点的视觉重投影观测 Jacobian。它由两段组成：

$$
\underbrace{J_\pi R_{CB}[\hat\ell_B]_\times}_{\text{姿态误差到像素误差}}
\qquad
\underbrace{-J_\pi R_{CB}\hat R_{WB}^{\top}}_{\text{位置误差到像素误差}}.
$$

姿态误差先让点在 IMU 系中发生旋转位移，位置误差则先通过 $\hat R_{WB}^{\top}$ 转到 IMU 系；两者最后都经过外参和针孔投影到像素平面。

#### 8.6.5 为什么没有速度和 bias block

在这个观测时刻，单个图像像素由当前相机位姿和地图点决定。给定位姿不变，速度、陀螺仪 bias、加速度计 bias 不会直接改变当前像素预测，因此 $H_u$ 的后三个 block 为零。

这和位置观测的情况相同：$H$ 中某个 block 为零，只表示当前观测没有直接的一阶敏感性。经过 IMU 传播后，姿态、位置、速度和 bias 之间会形成交叉协方差，视觉残差仍然可以通过

$$
K=P^-H_u^\top
\left(H_uP^-H_u^\top+\Sigma_u\right)^{-1}
$$

间接修正速度和 bias。

#### 8.6.6 如果地图点也在状态中

上面的 $P_W$ 被当作已知地图点。如果地图点也需要估计，真实点写成

$$
P_W=\hat P_W+\delta P_W.
$$

由

$$
\ell_B=R_{WB}^{\top}(P_W-p_W)
$$

可得新增的一阶项

$$
\delta\ell_C
\supset
R_{CB}\hat R_{WB}^{\top}\delta P_W.
$$

因此，若扩展状态包含地图点，视觉观测 Jacobian 还要增加

$$
H_{P_W}
=J_\pi(\hat\ell_C)R_{CB}\hat R_{WB}^{\top}.
$$

完整的视觉 SLAM 系统通常还会处理地图点参数化、逆深度、滑动窗口边缘化和相机外参。那些内容会改变状态维度和 Jacobian 的列，但不会改变这里的推导顺序。

#### 8.6.7 相机外参和畸变模型

如果 $R_{CB}$、$t_{CB}$ 也作为状态估计，$\delta\ell_C$ 对外参误差的导数需要继续计算，$H_u$ 会增加外参对应的列。若相机使用径向畸变或切向畸变，针孔投影 $\pi$ 应替换为带畸变的投影函数，链式法则仍然是

$$
H_u
=\frac{\partial\pi}{\partial\ell_C}
\frac{\partial\ell_C}{\partial\delta x}.
$$

工程实现中可以先用无畸变模型验证坐标和符号，再把畸变 Jacobian 接到投影部分。不要同时改变坐标变换、外参方向和畸变公式，否则很难判断误差来自哪一层。

#### 8.6.8 重投影误差中最容易错的三个符号

第一，世界点到 IMU 系使用的是

$$
R_{WB}^{\top}(P_W-p_W),
$$

不是 $R_{WB}(P_W-p_W)$。第二，右侧姿态扰动产生

$$
\delta\ell_B
=[\hat\ell_B]_\times\delta\theta
-\hat R_{WB}^{\top}\delta p.
$$

第三，本文残差是实际像素减预测像素。如果代码使用预测减实际，整个 $H_u$ 也要取反。把这三个地方逐一写在纸上，通常比直接检查最终的 $2\times15$ 矩阵更容易发现问题。

## 9. 这些例子可以归纳成一个写 $H$ 的流程

面对一个新观测，可以按下面的顺序操作。

### 第一步：写出物理观测模型

先不要考虑 Kalman Filter，直接写传感器理想情况下应该读到什么：

$$
z=h(\mathcal X)+n.
$$

例如：

- GNSS 位置：$h=p_W$；
- 世界系速度：$h=v_W$；
- 机体系重力：$h=R_{WB}^{\top}g_W$；
- LiDAR 点到平面：$h=n_W^\top(p_W+R_{WB}q_B)$。

如果这一步的坐标系或符号没有说清楚，后面很难得到可靠的 Jacobian。

### 第二步：写出预测观测和残差

用预测名义状态计算

$$
\hat z=h(\hat{\mathcal X}^-),
$$

再固定残差方向

$$
 r=z-\hat z.
$$

姿态等流形观测需要选择合适的 $\boxminus$，不能强行使用普通减法。

### 第三步：把真实状态替换成名义状态加误差

统一代入

$$
\begin{aligned}
R&=\hat R\operatorname{Exp}([\delta\theta]_\times),\\
p&=\hat p+\delta p,\\
v&=\hat v+\delta v,\\
b_g&=\hat b_g+\delta b_g,\\
b_a&=\hat b_a+\delta b_a.
\end{aligned}
$$

对旋转至少记住两条一阶公式：

$$
\operatorname{Exp}([\delta\theta]_\times)
\approx I+[\delta\theta]_\times,
$$

$$
\operatorname{Exp}(-[\delta\theta]_\times)x
\approx x+[x]_\times\delta\theta.
$$

### 第四步：只保留误差的一阶项

展开后，保留只含一个误差量的项，舍去

$$
\delta\theta\,\delta p,
\quad
\delta\theta\,\delta b_a,
\quad
\delta\theta^2
$$

等二阶项。

### 第五步：按状态排列组装 block

最后把残差写成

$$
 r\approx
H_\theta\delta\theta
+H_p\delta p
+H_v\delta v
+H_{b_g}\delta b_g
+H_{b_a}\delta b_a+n.
$$

将五个 block 横向拼接，才得到完整的 $H$。很多代码中的 bug 不是导数算错，而是 block 顺序和协方差的状态顺序不一致。

### 9.1 视觉重投影误差完整走一遍流程

视觉重投影误差可以把上面的五步完整串起来。假设世界系地图点 $P_W$ 已知，相机内参和 IMU-相机外参也已知，状态中暂时不估计地图点和外参。

#### 9.1.1 写观测模型、预测观测和残差

世界点先从世界系变到 IMU 系，再变到相机系：

$$
\ell_B=R_{WB}^{\top}(P_W-p_W),
$$

$$
\ell_C=R_{CB}\ell_B+t_{CB}.
$$

设

$$
\ell_C=
\begin{bmatrix}
X_C\\Y_C\\Z_C
\end{bmatrix},
$$

理想针孔投影为

$$
\pi(\ell_C)=
\begin{bmatrix}
 f_xX_C/Z_C+c_x\\
 f_yY_C/Z_C+c_y
\end{bmatrix}.
$$

因此观测模型是

$$
z_u=\pi(\ell_C)+n_u.
$$

用预测名义状态计算

$$
\hat\ell_B=\hat R_{WB}^{\top}(P_W-\hat p_W),
$$

$$
\hat\ell_C=R_{CB}\hat\ell_B+t_{CB},
\qquad
\hat z_u=\pi(\hat\ell_C),
$$

并采用实际像素减预测像素的残差：

$$
 r_u=z_u-\hat z_u.
$$

#### 9.1.2 代入误差状态并展开坐标变换

按照本文的右侧姿态误差和加性位置误差：

$$
R_{WB}=\hat R_{WB}\operatorname{Exp}([\delta\theta]_\times),
\qquad
p_W=\hat p_W+\delta p.
$$

真实的 IMU 系点坐标为

$$
\begin{aligned}
\ell_B
&=R_{WB}^{\top}(P_W-p_W)\\
&=\operatorname{Exp}(-[\delta\theta]_\times)
\hat R_{WB}^{\top}(P_W-\hat p_W-\delta p)\\
&=\operatorname{Exp}(-[\delta\theta]_\times)
\left(\hat\ell_B-\hat R_{WB}^{\top}\delta p\right).
\end{aligned}
$$

使用

$$
\operatorname{Exp}(-[\delta\theta]_\times)
\approx I-[\delta\theta]_\times
$$

并舍去姿态误差与位置误差的乘积，得到

$$
\begin{aligned}
\ell_B
&\approx \hat\ell_B
-[\delta\theta]_\times\hat\ell_B
-\hat R_{WB}^{\top}\delta p\\
&=\hat\ell_B
+[\hat\ell_B]_\times\delta\theta
-\hat R_{WB}^{\top}\delta p.
\end{aligned}
$$

经过固定外参变换：

$$
\begin{aligned}
\delta\ell_C
&=\ell_C-\hat\ell_C\\
&=R_{CB}[\hat\ell_B]_\times\delta\theta
-R_{CB}\hat R_{WB}^{\top}\delta p.
\end{aligned}
$$

这一步给出三维相机点对误差状态的 Jacobian：

$$
\frac{\partial\ell_C}{\partial\delta x}
=\begin{bmatrix}
R_{CB}[\hat\ell_B]_\times
&-R_{CB}\hat R_{WB}^{\top}
&0&0&0
\end{bmatrix}.
$$

#### 9.1.3 展开透视投影并用链式法则组装

针孔投影对相机点的 Jacobian 为

$$
J_\pi(\hat\ell_C)
=\begin{bmatrix}
\dfrac{f_x}{\hat Z_C}&0&-\dfrac{f_x\hat X_C}{\hat Z_C^2}\\[6pt]
0&\dfrac{f_y}{\hat Z_C}&-\dfrac{f_y\hat Y_C}{\hat Z_C^2}
\end{bmatrix}.
$$

于是像素误差的一阶项为

$$
\begin{aligned}
\delta z_u
&=J_\pi(\hat\ell_C)\delta\ell_C\\
&=J_\pi(\hat\ell_C)R_{CB}[\hat\ell_B]_\times\delta\theta
-J_\pi(\hat\ell_C)R_{CB}\hat R_{WB}^{\top}\delta p.
\end{aligned}
$$

因此，按

$$
\delta x=
\begin{bmatrix}
\delta\theta\\\delta p\\\delta v\\\delta b_g\\\delta b_a
\end{bmatrix}
$$

排列，视觉重投影观测的 Jacobian 为

$$
\boxed{
H_u=\begin{bmatrix}
J_\pi(\hat\ell_C)R_{CB}[\hat\ell_B]_\times
&-J_\pi(\hat\ell_C)R_{CB}\hat R_{WB}^{\top}
&0&0&0
\end{bmatrix}.
}
$$

因此，视觉残差的线性化形式为

$$
r_u\approx H_u\delta x+n_u.
$$

它是一个 $2\times15$ 矩阵。这里的两个非零 block 分别来自：姿态误差改变世界点在 IMU 系中的方向，位置误差改变世界点相对 IMU 原点的位置；$J_\pi$ 再把三维相机点变化映射为二维像素变化。

如果地图点也在状态中，只需继续对

$$
\ell_C=R_{CB}R_{WB}^{\top}(P_W-p_W)+t_{CB}
$$

对 $\delta P_W$ 求导，并在 $H_u$ 后面增加对应的地图点 block：

$$
H_{P_W}=J_\pi(\hat\ell_C)R_{CB}\hat R_{WB}^{\top}.
$$

相机外参或畸变参数进入状态时，也沿着同一条链式法则继续增加对应 block。由此可见，复杂观测并没有改变写 $H$ 的流程，只是中间函数更多：坐标变换、姿态扰动、透视投影和可能的畸变函数依次求导，再按状态顺序拼接。

## 10. 观测更新之后：误差注入和 reset

### 10.1 先更新局部误差

使用残差和 $H$ 得到

$$
\delta\hat x=Kr.
$$

把它展开为

$$
\delta\hat x=
\begin{bmatrix}
\delta\hat\theta\\
\delta\hat p\\
\delta\hat v\\
\delta\hat b_g\\
\delta\hat b_a
\end{bmatrix}.
$$

这些量仍然属于预测名义状态附近的局部坐标。

### 10.2 注入名义状态

对于右侧姿态误差，姿态注入为

$$
\hat R^+
=\hat R^-
\operatorname{Exp}([\delta\hat\theta]_\times).
$$

其余状态直接相加：

$$
\begin{aligned}
\hat p^+&=\hat p^-+\delta\hat p,\\
\hat v^+&=\hat v^-+\delta\hat v,\\
\hat b_g^+&=\hat b_g^-+\delta\hat b_g,\\
\hat b_a^+&=\hat b_a^-+\delta\hat b_a.
\end{aligned}
$$

不能把 $H$ 的某一行直接加到状态，也不能把旋转的三维误差直接和旋转矩阵相加。$H$ 是灵敏度矩阵，$\delta\hat x$ 才是需要注入的局部修正。

### 10.3 为什么还需要 reset

误差注入后，名义状态已经移动。误差状态的零点也随之改变。对加性状态，一阶近似下有

$$
\delta x_{\mathrm{new}}
\approx
\delta x_{\mathrm{old}}-\delta\hat x.
$$

姿态则需要使用旋转复合：

$$
\operatorname{Exp}([\delta\theta_{\mathrm{new}}]_\times)
=
\operatorname{Exp}(-[\delta\hat\theta]_\times)
\operatorname{Exp}([\delta\theta_{\mathrm{old}}]_\times).
$$

因此

$$
\delta\theta_{\mathrm{new}}
=\operatorname{Log}\left(
\operatorname{Exp}(-[\delta\hat\theta]_\times)
\operatorname{Exp}([\delta\theta_{\mathrm{old}}]_\times)
\right)^\vee.
$$

对小角度，常见的一阶近似是

$$
\delta\theta_{\mathrm{new}}
\approx
\delta\theta_{\mathrm{old}}-\delta\hat\theta.
$$

### 10.4 协方差也要换坐标

Kalman 更新得到的协方差通常对应注入前的误差坐标，记为 $\widetilde P^+$。reset 后的新误差坐标需要通过 reset Jacobian 转换：

$$
\boxed{
P^+=J_{\mathrm{reset}}\widetilde P^+J_{\mathrm{reset}}^\top.
}
$$

对普通加性状态，相关 Jacobian 常近似为单位矩阵；旋转部分则取决于误差定义、注入方式和采用的近似阶数。不能因为当前的 $\delta\hat\theta$ 很小，就默认所有实现中的 reset 都可以完全省略。

这一步和 $H$ 有直接关系：下一次观测更新的 $H$ 是在新的名义状态和新的误差坐标附近重新计算的。如果注入了状态却没有同步转换协方差，$P$ 和 $H$ 描述的就不是同一个局部坐标系统。

## 11. 用三个数值检查发现大多数符号错误

推导完成后，不妨用有限差分检查 $H$。这比盯着一长串叉乘矩阵更可靠。

### 11.1 有限差分检查

对误差状态的第 $j$ 个方向取一个很小的 $\epsilon$，构造单位向量 $e_j$。分别计算

$$
h_+=h(\hat{\mathcal X}\boxplus\epsilon e_j),
\qquad
h_-=h(\hat{\mathcal X}\boxplus(-\epsilon e_j)).
$$

则数值 Jacobian 的第 $j$ 列可以近似为

$$
H_{:,j}^{\mathrm{num}}
\approx
\frac{h_+-h_-}{2\epsilon}.
$$

姿态观测不能直接对旋转矩阵做减法。需要先把两个预测观测转换为同一个观测残差坐标，再做中心差分。对于普通向量观测，上式可以直接使用。

比较解析 Jacobian 和数值 Jacobian：

$$
\lVert H^{\mathrm{analytic}}-H^{\mathrm{num}}\rVert
$$

应该在合理的数值误差范围内较小。$\epsilon$ 太大时会混入高阶项，太小时又会受到浮点误差影响，可以测试一组不同量级的 $\epsilon$。

### 11.2 重力观测的 yaw 检查

对于纯重力向量观测，应该满足

$$
[\hat g_B]_\times\hat g_B=0.
$$

如果代码声称重力观测能够约束绕重力方向的旋转，通常说明观测模型或可观性判断出了问题。

### 11.3 点到平面的切向检查

对平面内切向量 $t_W$，应该有

$$
 n_W^\top t_W=0.
$$

因此点到平面观测对沿平面切向平移的一阶 Jacobian 为零。这个检查可以快速发现法向量是否被错误地转到了别的坐标系，或者点到平面的残差符号是否混乱。

### 11.4 维度和单位检查

每次构造观测 Jacobian 时至少检查：

1. $H$ 是否为 $m\times15$；
2. 残差维度是否为 $m$；
3. $\Sigma_z$ 是否为 $m\times m$；
4. $S=HP^-H^\top+\Sigma_z$ 是否为 $m\times m$；
5. 残差的单位是否和观测噪声协方差一致。

例如，点到平面残差是米，姿态残差是弧度，不能把它们混在一个残差向量中却不给出相应的噪声尺度。

## 12. 最容易混淆的几件事

### 12.1 把 $H$ 当成状态转移矩阵

$F$ 描述时间传播，$H$ 描述当前观测。$F$ 通常是 $15\times15$，$H$ 的行数取决于观测维度。二者都叫 Jacobian，但物理含义不同。

### 12.2 只看观测名称，不看输出坐标系

“速度观测”可能是世界系速度，也可能是机体系前向速度；“位置观测”可能是 IMU 原点，也可能是相机或 LiDAR 原点。传感器名称不能替代观测模型。

### 12.3 对旋转做普通减法

姿态残差应先构造相对旋转，再通过 $\operatorname{Log}$ 映射到局部三维坐标。使用哪一边乘逆、噪声放在哪一侧，都必须和姿态误差定义一致。

### 12.4 把静止加速度计读数当成重力加速度

加速度计测量的是比力。按照本文模型，静止时理想读数为

$$
-R_{WB}^{\top}g_W+b_a,
$$

而不是 $R_{WB}^{\top}g_W$。符号取决于世界系重力向量和加速度计测量定义，但不能不看模型就套用“加速度计指向重力”的口头说法。

### 12.5 忘记 bias 是否在观测模型中出现

纯位置观测的 $H$ 没有 bias block；静止加速度计观测的 $H$ 有 $H_{b_a}=I$。一个 bias 是否可观，不是由它“属于 IMU”决定的，而是由当前观测模型、运动激励和协方差相关性共同决定的。

### 12.6 用错误的残差方向，却只修改一处

如果残差从 $z-\hat z$ 改为 $\hat z-z$，$H$、噪声符号以及后续修正方向必须一起检查。只在代码里对残差加一个负号，通常会留下一个隐蔽的系统性错误。

### 12.7 忘记 reset 协方差

误差注入改变了姿态误差的切空间。只更新名义状态、不转换 $P$，会让下一轮的协方差和误差定义不匹配。小角度系统可能一段时间内看不出问题，但长期运行时会出现不稳定或一致性变差。

## 13. 把一轮观测更新串起来

现在可以把 ESKF 的观测阶段完整写出来。

### 第一步：IMU 传播到观测时刻

上一篇得到的 $F$、$G$ 用于传播预测协方差：

$$
P^-\approx\Phi P^+\Phi^\top+Q_d.
$$

同时，名义状态按照非线性 IMU 方程传播到 $\hat{\mathcal X}^-$。

### 第二步：根据当前传感器写 $h$

例如位置观测：

$$
h_p(\hat{\mathcal X}^-)=\hat p^-.
$$

点到平面观测：

$$
h_\pi(\hat{\mathcal X}^-)
=n_W^\top(\hat p^-+\hat R^-q_B).
$$

### 第三步：计算残差和 $H$

$$
 r=z-h(\hat{\mathcal X}^-),
$$

$$
 H=\left.
\frac{\partial h(\hat{\mathcal X}^-\boxplus\delta x)}
{\partial\delta x}
\right|_0.
$$

$H$ 必须在当前预测名义状态处重新计算。姿态、点坐标、法向量和外参的当前值都会进入 Jacobian。

### 第四步：更新误差状态

$$
S=HP^-H^\top+\Sigma_z,
$$

$$
K=P^-H^\top S^{-1},
$$

$$
\delta\hat x=Kr.
$$

### 第五步：注入并 reset

$$
\hat{\mathcal X}^+=\hat{\mathcal X}^-\boxplus\delta\hat x,
$$

再把注入前的后验协方差转换到新的误差坐标：

$$
P^+=J_{\mathrm{reset}}\widetilde P^+J_{\mathrm{reset}}^\top.
$$

这样，下一次 IMU 到来时，新的名义状态和新的协方差正好位于同一个局部坐标约定下。

## 14. 从一条新观测到一块正确的 $H$

本文最值得留下的不是某个单独的矩阵，而是下面这条推导路线：

1. 明确状态和所有坐标系的方向；
2. 写出理想观测模型 $z=h(\mathcal X)+n$；
3. 用预测名义状态计算 $\hat z=h(\hat{\mathcal X}^-)$；
4. 选定残差方向，例如 $r=z-\hat z$；
5. 把 $R=\hat R\operatorname{Exp}([\delta\theta]_\times)$ 和其他加性误差代入 $h$；
6. 舍去二阶小量，保留误差的一阶项；
7. 按 $[\delta\theta,\delta p,\delta v,\delta b_g,\delta b_a]$ 拼出 $H$；
8. 用有限差分、秩和几何退化检查结果；
9. 更新局部误差，注入名义状态，再 reset 协方差。

位置观测给出

$$
H_p=\begin{bmatrix}0&I&0&0&0\end{bmatrix},
$$

世界系速度观测给出

$$
H_v=\begin{bmatrix}0&0&I&0&0\end{bmatrix},
$$

纯重力向量观测给出

$$
H_g=\begin{bmatrix}[\hat g_B]_\times&0&0&0&0\end{bmatrix},
$$

静止加速度计比力观测给出

$$
H_a=\begin{bmatrix}-[\hat g_B]_\times&0&0&0&I\end{bmatrix},
$$

点到平面观测给出

$$
H_\pi=
\begin{bmatrix}
-n_W^\top\hat R_{WB}[q_B]_\times
&n_W^\top
&0&0&0
\end{bmatrix}.
$$

这些矩阵的形式看起来不同，但来源完全相同：先让误差状态改变预测观测，再读取预测观测的一阶变化。

下一步如果继续写 ESKF 系列，可以在这套观测 Jacobian 的基础上推导具体的视觉重投影误差，或者把 LiDAR 的点到平面观测扩展到 IESKF 的迭代更新。无论观测来自相机还是 LiDAR，先把观测模型和误差坐标写清楚，后面的矩阵就不会只剩下记忆。

## 参考文章

1. [ESKF 误差动力学推导：从 IMU 模型到 $F$ 和 $G$](../eskf-error-dynamics/index.md)
2. Joan Solà, *Quaternion kinematics for the error-state Kalman filter*, arXiv:1711.02508, 2017. <https://arxiv.org/abs/1711.02508>
3. Joan Solà, Jérémie Deray, and Dinesh Atchuthan, *A micro Lie theory for state estimation in robotics*, arXiv:1812.01537, 2018. <https://arxiv.org/abs/1812.01537>
4. Wei Xu, Yixi Cai, Dongjiao He, Jiarong Lin, and Fu Zhang, *FAST-LIO2: Fast Direct LiDAR-inertial Odometry*, IEEE Transactions on Robotics, 38(4):2053–2070, 2022. <https://arxiv.org/abs/2107.06829>
