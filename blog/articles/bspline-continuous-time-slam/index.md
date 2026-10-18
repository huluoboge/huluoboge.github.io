---
title: "B 样条的局部平滑曲线构造与应用"
date: 2026-09-25
categories: [state-estimation, reconstruction]
tags: [B-spline, Box filter, Cox-de Boor, Continuous-time, SLAM, Poisson]
excerpt: "从滑动窗口的重叠面积出发，理解 B 样条怎样生成平滑曲线，以及它为什么适合 Poisson 重建和连续时间 SLAM。"
draft: false
---

# B 样条的局部平滑曲线构造与应用

B 样条既出现在 Poisson 表面重建中，也常用于连续时间轨迹。前者用它构造空间中的平滑场，后者用它表示随时间变化的位置和姿态。两种用途看起来相距很远，依赖的却是同样几个性质：局部支撑、分段多项式，以及可控的连续阶数。

几种写法容易让人觉得它们是不同的东西：box 自卷积得到的核、Cox–de Boor 递推定义的基函数，还有轨迹估计中的三次矩阵。这些写法可以顺着同一条构造理解：先从矩形窗口的卷积得到基数核，再沿节点放置基函数，最后写出曲线及其导数。

对轨迹来说，局部性尤其重要。激光点、图像行和 IMU 样本可能处于不同时间，连续曲线允许在各自的时间戳取值；每次求值又只依赖附近几个控制点，不必让一条观测连接整段轨迹。

## 矩形窗口的重复卷积

取两个高度为 1、宽度为 1 的矩形窗口。固定其中一个，让另一个沿横轴移动，记录两者的重叠面积，得到一个三角形核。再用同样的矩形窗口对这个核积分，依次得到分段二次、分段三次的曲线。

三段动画中的蓝色曲线是被积函数，橙色矩形是移动窗口，绿色区域的面积对应输出值。后一段使用前一段的输出作为被积函数。

![两个 box 滑动重叠生成三角形核（动画）](figures/box-to-triangle-animation.svg)

![box 扫过三角形生成二阶核 B₂（动画）](figures/triangle-to-quadratic-animation.svg)

![box 扫过 B₂ 生成三次核 B₃（动画）](figures/quadratic-to-cubic-animation.svg)

两个矩形的重叠长度随位移线性变化，所以第一次卷积得到三角形。后两次积分的被积函数分别为分段一次、分段二次函数，结果的分段次数也各增加一阶。

窗口积分可以写成卷积。三段动画依次对应 $B_1=b*b$、$B_2=B_1*b$、$B_3=B_2*b$。由此得到的是均匀节点下的基数 B 样条核；非均匀节点的基函数稍后用递推定义。

先约定两个记号。

- **支撑** $\operatorname{supp}f$ 是非零点集的闭包。支撑以外函数为零；支撑有界时称为紧支撑。
- **$C^m$** 表示函数直到 $m$ 阶导数都连续。例如标准三次 B 样条为 $C^2$，三阶导数通常在节点处跳变。

---

## 基数 B 样条核

把刚才固定不动的矩形写成函数

$$
b(x)=B_0(x)=\mathbf{1}_{(-1/2,\,1/2)}(x)
=
\begin{cases}
1,& |x|<1/2,\\
0,& \text{otherwise.}
\end{cases}
$$

两个函数的卷积定义为

$$
(f*g)(x)=\int_{-\infty}^{\infty}f(\tau)g(x-\tau)\,\mathrm d\tau.
$$

当 $g=b$ 时，$b(x-\tau)$ 只在 $\tau\in(x-1/2,x+1/2)$ 内为 1，卷积便化为在这个窗口内对 $f(\tau)$ 积分。窗口端点的取值不影响积分。

次数为 $d$ 的基数 B 样条核，是把这个窗口重复卷积 $d+1$ 次得到的结果。

$$
B_d
=
\underbrace{b*b*\cdots*b}_{d+1\text{ 次}},
\qquad
B_0=b,\quad B_d=B_{d-1}*b.
\tag{C1}
$$

由于 $\int b=1$，各阶核也满足 $\int B_d=1$。每增加一次卷积，支撑宽度增加 1，分段次数增加一阶。

### 一次核

$$
B_1(x)=(b*b)(x)=\int b(\tau)\,b(x-\tau)\,\mathrm{d}\tau.
$$

两个被积因子在重叠区内都等于 1，所以积分就是重叠区间的长度。

$x=0$ 时两个窗口重合，面积为 1；$|x|\ge1$ 时没有重叠，面积为 0。中间的重叠长度为 $1-|x|$，因此

$$
B_1(x)=
\begin{cases}
1-|x|,& |x|<1,\\
0,& |x|\ge 1.
\end{cases}
\tag{C2}
$$

支撑 $[-1,1]$，$C^{0}$（在 $0$ 处导数跳跃）。下一阶把固定曲线换成这个三角形。

### 二次核

$$
B_2(x)=(B_1*b)(x)=\int B_1(\tau)\,b(x-\tau)\,\mathrm{d}\tau.
$$

积分区间是 $B_1$ 的支撑与移动窗口的交集，记 $L=\max(-1,x-1/2)$、$U=\min(1,x+1/2)$。当 $L<U$ 时，

$$
B_2(x)=\int_{L}^{U}(1-|\tau|)\,\mathrm{d}\tau.
$$

$|x|\ge 3/2$ 时面积为 0。下面把 $0\le x\le 1/2$ 这一段算完，其余用偶对称与同类分段得到。

此时 $L=x-1/2\in[-1/2,0]$，$U=x+1/2\in[1/2,1]$，积分跨过 $0$，拆成

$$
B_2(x)=\int_{x-1/2}^{0}(1+\tau)\,\mathrm{d}\tau+\int_{0}^{x+1/2}(1-\tau)\,\mathrm{d}\tau.
$$

第一段积分给出 $\bigl[\tau+\tau^{2}/2\bigr]_{x-1/2}^{0}=0-\bigl((x-1/2)+(x-1/2)^{2}/2\bigr)=1/2-x-(x-1/2)^{2}/2$。  
第二段积分给出 $\bigl[\tau-\tau^{2}/2\bigr]_{0}^{x+1/2}=(x+1/2)-(x+1/2)^{2}/2$。  
相加并化简得

$$
B_2(x)=\tfrac34-x^{2},\qquad 0\le x\le\tfrac12.
$$

对 $\tfrac12\le x\le\tfrac32$，窗完全落在 $B_1$ 的右半支上，直接积分得 $B_2(x)=(3/2-x)^{2}/2$。再由偶函数补全左边，得到

$$
B_2(x)=
\begin{cases}
\dfrac{(x+3/2)^{2}}{2},& -3/2\le x<-1/2,\\[6pt]
\dfrac{3}{4}-x^{2},& |x|\le 1/2,\\[6pt]
\dfrac{(3/2-x)^{2}}{2},& 1/2<x\le 3/2,\\
0,& |x|>3/2.
\end{cases}
\tag{C3}
$$

支撑 $[-3/2,3/2]$，$C^{1}$。

### 三次核

$$
B_3(x)=(B_2*b)(x)=\int B_2(\tau)\,b(x-\tau)\,\mathrm{d}\tau.
$$

将 (C3) 代入窗口积分，根据窗口与分段边界的相对位置拆开计算。

对 $0\le x\le1$，窗口左端在 $[-1/2,1/2]$ 内，右端在 $[1/2,3/2]$ 内，因此应在积分变量 $\tau=1/2$ 处分开：

$$
B_3(x)=\int_{x-1/2}^{1/2}(3/4-\tau^2)\,\mathrm d\tau
+\int_{1/2}^{x+1/2}\frac{(3/2-\tau)^2}{2}\,\mathrm d\tau
=\frac{4-6x^2+3x^3}{6}.
$$

对 $1\le x\le2$，非零部分只有外侧一段，积分为 $(2-x)^3/6$。利用偶对称可得

$$
B_3(x)=
\begin{cases}
\dfrac{1}{6}(2-|x|)^{3},& 1<|x|<2,\\[8pt]
\dfrac{1}{6}\bigl(4-6x^{2}+3|x|^{3}\bigr),& |x|\le 1,\\
0,& |x|\ge 2.
\end{cases}
\tag{C4}
$$

检查分段连接处，有 $B_3(1)=1/6$、$B_3(2)=0$，左右一阶、二阶导数也相等。

各阶核的形状和连续性如下。

![不同次数的均匀 B 样条基函数](figures/basis-functions.svg)

| 核 | 支撑宽度 | 连续性 | 固定曲线 $f$ | 绿色重叠面积在算 |
|----|----------|--------|--------------|------------------|
| $B_0$ | 1 | 不连续 | — | 矩形窗本身 |
| $B_1$ | 2 | $C^{0}$ | box | 两矩形重叠长度 |
| $B_2$ | 3 | $C^{1}$ | 三角形 $B_1$ | 窗∩三角的面积 |
| $B_3$ | 4 | $C^{2}$ | $B_2$ | 窗∩$B_2$ 的面积 |

对 $d\ge1$，$B_d$ 的支撑宽度为 $d+1$，分段次数为 $d$，连续性为 $C^{d-1}$。

---

## 离散卷积与滑动平均

格点数据上的卷积要用求和计算。输入可以是图像灰度、体素数据，也可以是按固定间隔采集的时间序列。

最直接的做法是用求和近似连续积分。若 $f[n]$ 表示第 $n$ 个格点的数值，离散卷积

$$
(f*g)[n]=\sum_{m\in\mathbb{Z}} f[m]\,g[n-m].
\tag{D1}
$$

在网格上，每个采样值代表一个小区间，连续积分便由这些小区间面积的总和近似。归一化 box 的高度和宽度都为 1，积分为 1；常数函数经过它的卷积后仍保持原值。离散窗口覆盖 $L$ 个格点时，若每个格点的权重都是 1，权重总和会变成 $L$，常数值也随之放大 $L$ 倍。为了保持相同的归一化尺度，窗口中的每个格点取权重 $1/L$，于是离散 box 表现为局部平均。

举个具体例子。假设一维数据依次是

$$
2,\;4,\;8,\;10,\;6.
$$

取一个覆盖 3 个样本的窗口。窗口先盖住 $2,4,8$，输出它们的加权和 $(2+4+8)/3$；向右移动一格后盖住 $4,8,10$，输出变成 $(4+8+10)/3$；再移动一格，得到 $(8+10+6)/3$。窗口每移动一次，就输出一个新的局部平均值，这就是离散的滑动 box。若输入整段数据都等于常数 $c$，每个窗口的输出仍是 $(c+c+c)/3=c$，这正好对应连续归一化 box 的行为。

一般地，若窗口覆盖 $L$ 个样本，第 $n$ 个输出为

$$
y[n]=\frac1L\sum_{r=0}^{L-1}f[n-r].
$$

这里的 $L$ 只是“窗口一次看多少个样本”，不是 B 样条的次数。把这件事写成卷积，只需把窗口记成一个权重数组

$$
\beta_L[r]=
\begin{cases}
1/L,&0\le r<L,\\
0,&\text{otherwise,}
\end{cases}
\qquad y=f*\beta_L.
$$

相同窗口再作用一次，对应 $f*\beta_L*\beta_L$。

为了单独观察卷积后系数的形状，下面暂时去掉归一化因子，取长度为 2 的盒

$$
\beta[n]=
\begin{cases}
1,& n\in\{0,1\},\\
0,& \text{otherwise.}
\end{cases}
$$

它的前几次卷积为

| 卷积次数 | 非零值（从左到右） | 支撑长度 |
|----------|--------------------|----------|
| $\beta$ | $1,1$ | 2 |
| $\beta*\beta$ | $1,2,1$ | 3 |
| $\beta*\beta*\beta$ | $1,3,3,1$ | 4 |

这些是重复离散 box 卷积的系数，归一化后可用作平滑滤波器。这里记 $B_d^{\mathrm d}$ 为这组离散卷积核：

$$
B_0^{\mathrm{d}}=\beta,\qquad B_d^{\mathrm{d}}=B_{d-1}^{\mathrm{d}}*\beta
\tag{D2}
$$

上标 $\mathrm d$ 区分离散序列与连续函数，下标 $d$ 对应在初始 box 上追加的卷积次数。例子暂时保留整数系数；用于平均滤波时，还需除以系数总和。这些离散系数不等于连续 $B_d$ 在整数点上的直接采样。

实现时，长度为 $L$ 的滑动和不必每次重新加 $L$ 个数。令前缀和 $s[n]=\sum_{k<n}f[k]$，窗口和就是

$$
s[n+1]-s[n+1-L].
$$

前缀和预先算好后，每个窗口只需两次查表和一次减法。二维的积分图也是同一思路，矩形区域的和由四个角点的累计值相减得到。重复 box 滤波因此可以避免对每个窗口重新求和。

这里先沿一维坐标理解卷积和离散化。推广到二维或三维时，常用各坐标方向的一维核做张量积。对这里的标量函数来说，张量积就是把各维的函数值相乘；例如三维网格上的权重由 $x$、$y$、$z$ 三个方向的一维权重相乘得到。离散数组中，这种组合对应外积或 Kronecker 积，而不是两个同形数组的逐元素相乘。在三维空间中，可分离的核写成

$$
B_d(\mathbf x)=B_d(x)B_d(y)B_d(z),
$$

于是三维滤波可以拆成沿 $x,y,z$ 三个方向的 1D 操作，避免直接处理一个三维卷积核。三维体素场上的一个具体应用是 Poisson 表面重建，后文会简要说明，也可以参见 [Poisson 表面重建专文](../poisson_recon_box_filter/index.html)。网格步长 $h\to 0$ 且适当归一化时，离散多次 box 一致逼近前面的连续卷积。

| | 连续 $B_d$ | 离散 $B_d^{\mathrm{d}}$ |
|--|------------|-------------------------|
| 定义 | 函数卷积 (C1) | 序列卷积 (D2) |
| 典型角色 | 解析性质、理论核 | 格点快速平滑 |
| 求值 | 分段多项式 / 递推 | 积分图多次 box |

离散滤波处理格点数据，基函数展开则用有限个系数表示连续曲线。两者都用到局部核，但需要区分采样值与展开系数。

---

## 节点、基函数与控制系数

设在时刻 $t_k$ 得到带噪观测 $y_k$，用有限个系数构造连续曲线 $f(t)$，使 $f(t_k)$ 尽量接近这些观测。

在参数轴上选取节点序列 $\{t_i\}$。相邻节点形成区间 $[t_i,t_{i+1})$，决定分段多项式的切换位置。节点属于曲线表示的参数网格，不必与观测时刻重合。

为每个基函数 $N_{i,d}$ 配置系数 $c_i$，曲线写成

$$
f(t)=\sum_i c_iN_{i,d}(t).
$$

固定节点后，$N_{i,d}(t)$ 已知，拟合只需调整 $c_i$。查询时刻 $t$ 代入基函数得到权重，再与系数相乘求和。均匀节点下，各基函数来自同一模板的平移；曲线的幅值变化由系数决定。

对无重复节点的 $d$ 次样条，一个区间内只有 $d+1$ 个基函数参与。图中采用均匀节点 $t_i=i\Delta t$，查询位置为 $t^*=t_3+0.35\Delta t$，因此局部坐标为 $u=0.35$。

下图上层是七个基函数，中层是各项 $c_iN_{i,d}(t)$，底层为它们的和。黑点是观测，拟合时通过调整系数让合成曲线接近黑点。

![7 个基函数、局部稀疏贡献与合成曲线（动画）](figures/global-basis-fit-animation.svg)

局部放大后，可以看到四个权重在同一区间内怎样变化，以及各项贡献如何相加。改变节点间距会伸缩时间轴上的支撑宽度；在一次固定网格的拟合中，这个间距保持不变。

![均匀三次基函数及其加权和形成一维曲线（动画）](figures/basis-weighted-curve-animation.svg)

$B_d$ 的横坐标是无量纲的，而时间 $t$ 带有秒这个单位，所以先用 $t/\Delta t$ 把时间换成“经过了多少个节点间隔”。这里 $d$ 表示次数，$d+1$ 表示阶数，也等于一个位置上可能参与加权的基函数数量。前面定义的中心化核 $B_d(x)$ 支撑宽度为 $d+1$；把它写成节点形式时，需要把这个中心化坐标换成以节点区间为参考的坐标。于是

$$
N_{i,d}(t)=B_d\Bigl(\frac{t}{\Delta t}-i-\frac{d+1}{2}\Bigr)
$$

这里的 $(d+1)/2$ 是一个固定偏移量，表示支撑宽度的一半，不是随 $t$ 变化的局部坐标。以无量纲坐标 $q=t/\Delta t$ 表示，中心化核真正接收的自变量是

$$
\xi=q-i-\frac{d+1}{2}.
$$

它可能非零的范围对应 $q\in[i,i+d+1)$，也就是从第 $i$ 个节点开始的 $d+1$ 个节点区间；右端点不包含在内。实际求值时还常在当前小区间内使用

$$
u=\frac{t-t_j}{\Delta t}\in[0,1),
$$

这里 $j$ 表示 $t$ 所在的节点区间。$u$ 是区间内的局部坐标，$(d+1)/2$ 则是固定的中心化偏移，两者不是同一个量。不同文献有时直接使用非中心化的基函数，或把下标整体平移，因此公式外观会不同；关键是支撑区间、基函数编号和控制点编号必须采用同一套约定。

非均匀节点不能再靠同一模板的等距平移获得全部基函数，需要按节点位置计算各自的形状。Cox–de Boor 递推同时适用于这两种情况。

---

## Cox–de Boor 递推

Cox–de Boor 递推从区间指示函数开始，用相邻的低次基构造高次基。节点间距直接进入权重，因此不要求节点等距。

对任意节点序列 $\{t_i\}$ 与次数 $d$，先规定零次基

$$
N_{i,0}(t)=
\begin{cases}
1,& t_i\le t<t_{i+1},\\
0,& \text{otherwise,}
\end{cases}
$$

$$
N_{i,d}(t)
=
\frac{t-t_i}{t_{i+d}-t_i}\,N_{i,d-1}(t)
+
\frac{t_{i+d+1}-t}{t_{i+d+1}-t_{i+1}}\,N_{i+1,d-1}(t).
\tag{R1}
$$

两个低次基各自乘上线性因子后相加，得到高一次的基函数。线性因子在对应基非零的范围内非负，但两者之和一般不等于 1。分母为零时，对应项按 0 处理。

把递推得到的基函数代回前面的曲线表示，仍然得到一维标量曲线

$$
f(t)=\sum_i c_iN_{i,d}(t)
\tag{R2}
$$

节点固定时，$N_{i,d}(t)$ 决定系数 $c_i$ 在各位置的作用范围和权重。这一[递推定义](https://docs.scipy.org/doc/scipy/reference/generated/scipy.interpolate.BSpline.html)也直接用于非均匀节点。

(R1) 在均匀节点下与 box 卷积构造相容。为与前面的中心化核区分，记非中心化核 $\mathcal B_d(x)=B_d(x-(d+1)/2)$，其支撑为 $[0,d+1]$。它满足

$$
\mathcal B_d(x)=\frac{x}{d}\mathcal B_{d-1}(x)+\frac{d+1-x}{d}\mathcal B_{d-1}(x-1),\qquad d\ge1,
$$

这对应整数均匀节点上的递推式。

固定节点与 $d\ge 0$ 时，可以由 (R1) 归纳得到下面几个性质。

**非负。** 系数非负，故 $N_{i,d}\ge 0$。

**局部支撑。**

$$
\operatorname{supp}N_{i,d}\subseteq[t_i,\,t_{i+d+1}],
\tag{R3}
$$

第 $i$ 个基函数最多覆盖 $d+1$ 个节点区间。这可由 (R1) 中两个低次基的支撑取并集得到。递推求值采用半开区间，支撑作为非零点集的闭包则写成闭区间。

**单位分解。** 在节点覆盖内部 $\sum_i N_{i,d}(t)=1$。对 (R1) 求和并改下标后，每个 $N_{\ell,d-1}$ 前两系数之和为

$$
\frac{t-t_\ell}{t_{\ell+d}-t_\ell}+\frac{t_{\ell+d}-t}{t_{\ell+d}-t_\ell}=1.
$$

**分段多项式。** 在每个开区间 $(t_j,t_{j+1})$ 上，$N_{i,d}$ 是次数 $\le d$ 的多项式。

---

## 局部支撑与节点连续性

支撑公式固定基函数编号 $i$，给出它影响的时间范围。查询曲线时，则要固定区间 $[t_j,t_{j+1})$，找出覆盖它的基函数。对严格递增节点，非零范围要求

$$
t_i\le t_j,\qquad t_{i+d+1}>t_j,
$$

因而 $i\le j$ 且 $i+d\ge j$，即

$$
j-d\le i\le j.
$$

所以该区间内的活跃基函数为 $N_{j-d,d},\ldots,N_{j,d}$。例如三次样条在 $[t_5,t_6)$ 内使用 $N_{2,3},N_{3,3},N_{4,3},N_{5,3}$。改动其中一个系数，只影响该基函数的支撑范围；在均匀网格中，影响宽度为 $4\Delta t$。

![三次 B 样条的局部支撑](figures/local-support.svg)

每个开区间内部都是多项式，光滑性的问题出现在区间连接处。对单重节点，$d$ 次样条的函数值及前 $d-1$ 阶导数连续；最高阶导数通常仍会跳变。三次样条因此是 $C^2$，位置的二阶导数在节点处连续。

如果希望把这件事写成计算规则，可以对递推式求导。在分母非零时有

$$
\frac{\mathrm d}{\mathrm dt}N_{i,d}(t)
=
\frac{d}{t_{i+d}-t_i}N_{i,d-1}(t)
-
\frac{d}{t_{i+d+1}-t_{i+1}}N_{i+1,d-1}(t).
$$

右侧只含 $(d-1)$ 次基函数。一次基函数本身是连续的，作为归纳起点；如果 $(d-1)$ 次基函数已经是 $C^{d-2}$，那么上式说明 $d$ 次基函数的一阶导数具有 $C^{d-2}$ 连续性，于是 $d$ 次基函数本身就是 $C^{d-1}$。这就是“每升一次次数，连续阶数增加一阶”的具体来源。

三次是连续时间轨迹中常用的选择：既能给出连续速度，也能给出连续线加速度。更低次的表示仍可使用，但需要检查相应导数在节点处的连续性。

内部节点重复 $r$ 次时，通常降为 $C^{d-r}$ 连续。端点重复 $d+1$ 次的夹持节点向量可使曲线经过首尾控制点。重复节点仍按 (R1) 计算，只是零分母对应项取 0；内部的高重数节点则允许降低连接处的光滑程度。

非负与单位分解还意味着曲线值处于活跃控制点的凸包内。它一般不经过控制点；插值需要通过端点条件或额外约束实现。拟合中的控制点是待估系数，残差约束的是曲线值。

---

## 均匀三次样条的矩阵形式

将标量系数 $c_i$ 换成向量控制点 $\mathbf p_i$，同一组基函数就可表示二维或三维位置。基函数值仍是标量权重。

按前面的下标约定，区间 $[t_\ell,t_{\ell+1})$ 使用 $\mathbf p_{\ell-3},\ldots,\mathbf p_\ell$。进入下一区间后，最左控制点退出，最右补入一个；其余三个继续参与。控制点由拟合确定，查询时只改变权重。

均匀节点使每个区间共用相同的局部多项式，求值可写成固定矩阵。有些轨迹实现将首个活跃控制点重新编号为 $i$，写作 $\mathbf p_i,\ldots,\mathbf p_{i+3}$；这里保留区间编号 $\ell$。

设 $t\in[t_\ell,t_{\ell+1})$，$u=(t-t_\ell)/\Delta t$。三次时每个区间恰有 4 个活跃控制点。

$$
\mathbf p(t)=\sum_{r=0}^{3}b_r(u)\,\mathbf p_{\ell-3+r}.
\tag{M1}
$$

这四个权重可以从 $B_3$ 的四片平移在单位区间上读出来，也可以由 (R1) 在均匀节点上展开。与 (C4) 对齐并限制到 $u\in[0,1)$ 后，标准结果是

$$
\begin{aligned}
b_0(u)&=\tfrac16(1-u)^{3},\\
b_1(u)&=\tfrac16(3u^{3}-6u^{2}+4),\\
b_2(u)&=\tfrac16(-3u^{3}+3u^{2}+3u+1),\\
b_3(u)&=\tfrac16 u^{3}.
\end{aligned}
\tag{M2}
$$

例如最右控制点的权重为 $b_3(u)=u^3/6$，对应中心化核 $B_3(u-2)$ 在 $u\in[0,1)$ 上的那一片。其余权重也由相邻平移得到。

令 $\mathbf u^{\top}=[1,u,u^{2},u^{3}]$，把 (M2) 写成

$$
\begin{aligned}
b_0&=\tfrac16(1-3u+3u^{2}-u^{3}),\\
b_1&=\tfrac16(4-6u^{2}+3u^{3}),\\
b_2&=\tfrac16(1+3u+3u^{2}-3u^{3}),\\
b_3&=\tfrac16 u^{3},
\end{aligned}
$$

第 $r$ 列存 $b_r$ 的系数，得

$$
\mathbf M^{(4)}
=
\frac16
\begin{bmatrix}
1&4&1&0\\
-3&0&3&0\\
3&-6&3&0\\
-1&3&-3&1
\end{bmatrix},
\qquad
[b_0\ b_1\ b_2\ b_3]=\mathbf u^{\top}\mathbf M^{(4)}.
\tag{M3}
$$

令 $\mathbf P=[\mathbf p_{\ell-3}\ \mathbf p_{\ell-2}\ \mathbf p_{\ell-1}\ \mathbf p_\ell]$，则

$$
\mathbf p(t)=\mathbf P\,\mathbf M^{(4)\top}\mathbf u.
\tag{M4}
$$

$\mathbf M$ 的元素是基的固有系数，不是估计量。易验 $b_0+b_1+b_2+b_3=1$。

$\mathrm{d}u/\mathrm{d}t=1/\Delta t$，$\mathbf u'=[0,1,2u,3u^{2}]^{\top}$，$\mathbf u''=[0,0,2,6u]^{\top}$，于是

$$
\dot{\mathbf p}=\frac{1}{\Delta t}\mathbf P\mathbf M^{(4)\top}\mathbf u',
\qquad
\ddot{\mathbf p}=\frac{1}{(\Delta t)^{2}}\mathbf P\mathbf M^{(4)\top}\mathbf u''.
\tag{M5}
$$

取 $u=1/2$、$\Delta t=1$，权重为 $[1,23,23,1]/48$。若一维控制点为 $[0,1,2,3]$，则 $p(t)=3/2$。它处于控制点的凸包内，并不等于某个控制点。速度和加速度需要将 $b_r$ 换成相应导数，并分别乘 $1/\Delta t$ 与 $1/\Delta t^2$。

### 累积形式

利用权重和为 1，可以将控制点加权和改写为基准点与相邻差分的和。先记

$$
\Delta\mathbf p_1=\mathbf p_{\ell-2}-\mathbf p_{\ell-3},\qquad
\Delta\mathbf p_2=\mathbf p_{\ell-1}-\mathbf p_{\ell-2},\qquad
\Delta\mathbf p_3=\mathbf p_{\ell}-\mathbf p_{\ell-1}.
$$

利用单位分解 $b_0+b_1+b_2+b_3=1$，可以把 (M1) 逐项重新整理。第一步先把所有项都写成相对于最左控制点的形式

$$
\begin{aligned}
\mathbf p(t)
&=(b_0+b_1+b_2+b_3)\mathbf p_{\ell-3}\\
&\quad +(b_1+b_2+b_3)(\mathbf p_{\ell-2}-\mathbf p_{\ell-3})\\
&\quad +(b_2+b_3)(\mathbf p_{\ell-1}-\mathbf p_{\ell-2})\\
&\quad +b_3(\mathbf p_{\ell}-\mathbf p_{\ell-1}).
\end{aligned}
$$

于是定义累积权重

$$
\tilde\lambda_1=b_1+b_2+b_3,
\qquad
\tilde\lambda_2=b_2+b_3,
\qquad
\tilde\lambda_3=b_3,
$$

就得到

$$
\mathbf p(t)=\mathbf p_{\ell-3}
 +\tilde\lambda_1\Delta\mathbf p_1
 +\tilde\lambda_2\Delta\mathbf p_2
 +\tilde\lambda_3\Delta\mathbf p_3.
\tag{M6}
$$

代入 (M2)，得到

$$
\begin{aligned}
\tilde\lambda_1(u)&=\frac{5+3u-3u^2+u^3}{6},\\
\tilde\lambda_2(u)&=\frac{1+3u+3u^2-2u^3}{6},\\
\tilde\lambda_3(u)&=\frac{u^3}{6}.
\end{aligned}
\tag{M7}
$$

累积权重由原来的基函数尾和构成。平移中两种形式等价，而相邻增量的写法也适合推广到旋转群。

对 (M6) 求导时，控制点差分在一个区间内保持不变，变化只来自 $\tilde\lambda_r(u)$。因为 $\mathrm du/\mathrm dt=1/\Delta t$，有

$$
\dot{\mathbf p}(t)=\frac{1}{\Delta t}
\left(
\tilde\lambda_1'(u)\Delta\mathbf p_1+
\tilde\lambda_2'(u)\Delta\mathbf p_2+
\tilde\lambda_3'(u)\Delta\mathbf p_3
\right),
$$

其中

$$
\tilde\lambda_1'=\frac{(1-u)^2}{2},
\qquad
\tilde\lambda_2'=\frac{1+2u-2u^2}{2},
\qquad
\tilde\lambda_3'=\frac{u^2}{2}.
$$

二阶导数进一步给出

$$
\ddot{\mathbf p}(t)=\frac{1}{(\Delta t)^2}
\left[
(u-1)\Delta\mathbf p_1+(1-2u)\Delta\mathbf p_2+u\Delta\mathbf p_3
\right].
$$

把相邻差分再次相减，还能看出加速度实际上是在两个二阶差分之间做线性插值

$$
\ddot{\mathbf p}(t)=\frac{1}{(\Delta t)^2}
\left[(1-u)(\Delta\mathbf p_2-\Delta\mathbf p_1)
      +u(\Delta\mathbf p_3-\Delta\mathbf p_2)\right].
\tag{M8}
$$

位置的一阶导数依赖控制点一阶差分，二阶导数依赖二阶差分。这个关系有助于分析速度、加速度观测分别约束哪些轨迹参数。

### 旋转样条及其导数

旋转控制量不能做普通的向量加法。两个姿态 $\mathbf R_a,\mathbf R_b\in SO(3)$ 之间的相对旋转写成

$$
\boldsymbol\phi=\operatorname{Log}(\mathbf R_a^\top\mathbf R_b)^\vee,
$$

其中 $\operatorname{Log}$ 把旋转矩阵映到李代数，右上角的 $\vee$ 把反对称矩阵还原成三维旋转向量。于是三次区间内的三个相邻相对旋转为

$$
\boldsymbol\phi_1=\operatorname{Log}(\mathbf R_{\ell-3}^\top\mathbf R_{\ell-2})^\vee,
\quad
\boldsymbol\phi_2=\operatorname{Log}(\mathbf R_{\ell-2}^\top\mathbf R_{\ell-1})^\vee,
\quad
\boldsymbol\phi_3=\operatorname{Log}(\mathbf R_{\ell-1}^\top\mathbf R_{\ell})^\vee.
$$

旋转累积式将位置差分换成相对旋转，并用矩阵乘积组合。下文取 $\mathbf R$ 为机体系到参考系的旋转，约定按顺序右乘各增量：

$$
\mathbf R(u)=\mathbf R_{\ell-3}
 \operatorname{Exp}(\tilde\lambda_1(u)\boldsymbol\phi_1^\wedge)
 \operatorname{Exp}(\tilde\lambda_2(u)\boldsymbol\phi_2^\wedge)
 \operatorname{Exp}(\tilde\lambda_3(u)\boldsymbol\phi_3^\wedge),
\tag{M9}
$$

这里 $\boldsymbol\phi^\wedge$ 表示把向量写成反对称矩阵。指数映射保证每个因子仍属于 $SO(3)$，所以整个乘积始终是合法旋转。由于 B 样条通常不经过控制姿态，$u=0$ 时也不应把 $\mathbf R(u)$ 理解成某一个控制姿态；控制姿态只是决定局部形状的参数。

三个指数因子分别由相邻控制姿态的相对旋转加权得到。矩阵乘法不满足交换律，因子顺序属于轨迹定义的一部分。

令

$$
\mathbf A_r(u)=\operatorname{Exp}(\tilde\lambda_r(u)\boldsymbol\phi_r^\wedge),
$$

并采用机体系角速度定义

$$
\boldsymbol\omega^B=\bigl(\mathbf R^\top\dot{\mathbf R}\bigr)^\vee,
$$

对 (M9) 求导，得到

$$
\boldsymbol\omega^B(t)=\frac{1}{\Delta t}
\left[
\mathbf A_3^\top\mathbf A_2^\top\tilde\lambda_1'\boldsymbol\phi_1
 +\mathbf A_3^\top\tilde\lambda_2'\boldsymbol\phi_2
 +\tilde\lambda_3'\boldsymbol\phi_3
\right].
\tag{M10}
$$

第一项先经过后面两段旋转的坐标变换，第二项只经过最后一段变换，第三项已经处在当前机体系。这正是旋转和欧氏位置的区别，旋转增量不能直接按标量权重相加后当作姿态。

如果还需要角加速度，就继续对 (M10) 求导。为避免把每一项都写得过长，先记

$$
\mathbf q_r=\tilde\lambda_r'\boldsymbol\phi_r,
\qquad
\mathbf h_r=\tilde\lambda_r''\boldsymbol\phi_r,
$$

其中

$$
\tilde\lambda_1''=u-1,
\qquad
\tilde\lambda_2''=1-2u,
\qquad
\tilde\lambda_3''=u.
$$

再定义

$$
\mathbf y_1=\mathbf A_3^\top\mathbf A_2^\top\mathbf q_1,
\qquad
\mathbf y_2=\mathbf A_3^\top\mathbf q_2,
\qquad
\boldsymbol\eta_{23}=\mathbf y_2+\mathbf q_3.
$$

对任意一段旋转都有

$$
\frac{\mathrm d}{\mathrm du}(\mathbf A^\top\mathbf v)
=-(\mathbf A^\top\mathbf A')^\vee\times(\mathbf A^\top\mathbf v)
 +\mathbf A^\top\mathbf v'.
$$

因此

$$
\dot{\boldsymbol\omega}^{B}(t)
=\frac{1}{(\Delta t)^2}
\left[
\mathbf A_3^\top\mathbf A_2^\top\mathbf h_1
 +\mathbf A_3^\top\mathbf h_2
 +\mathbf h_3
 -\boldsymbol\eta_{23}\times\mathbf y_1
 -\mathbf q_3\times\mathbf y_2
\right].
$$

叉乘项来自坐标变换矩阵的导数。相比位置的二阶导数，旋转求导还需计入表达坐标系的转动。

普通 IMU 直接提供角速度与比力；角加速度通常不作为直接观测。上式可用于需要更高阶运动约束的场合。

在优化中，控制姿态通常用李代数扰动更新，例如

$$
\mathbf R_i\leftarrow \mathbf R_i\operatorname{Exp}(\delta\boldsymbol\theta_i^\wedge).
$$

对 (M9) 和 (M10) 线性化后，每一个时间观测只会关联局部的四个控制姿态。角速度观测可以写成

$$
\mathbf r_{\omega,k}
=\boldsymbol\omega^B(t_k)-\bigl(\boldsymbol\omega_{m,k}-\mathbf b_g\bigr),
$$

平移加速度观测写成

$$
\mathbf r_{a,k}
=\mathbf R(t_k)^\top
\bigl(\ddot{\mathbf p}(t_k)-\mathbf g\bigr)
-\bigl(\mathbf a_{m,k}-\mathbf b_a\bigr).
$$

如果传感器还提供位置观测，位置残差就是

$$
\mathbf r_{p,k}=\mathbf p(t_k)-\mathbf z^p_k,
$$

其中 $\mathbf z^p_k$ 是时间 $t_k$ 处的外部位置观测。视觉观测通常先把连续时间位姿写成 $\mathbf T(t_k)$，再通过相机投影函数 $\pi(\cdot)$ 投到像平面，得到重投影残差

$$
\mathbf r_{\mathrm{img},k}
=\pi\bigl(\mathbf T(t_k)^{-1}\mathbf P_k\bigr)-\mathbf z^{\mathrm{img}}_k.
$$

这里 $\mathbf T(t_k)$ 为相机到参考系的位姿，$\mathbf P_k$ 是参考系中的空间点，需先用逆变换转到相机系再投影；$\mathbf z^{\mathrm{img}}_k$ 是像素观测。各传感器的残差可以通过共享轨迹联合优化。

堆叠残差及其信息矩阵：

$$
\mathbf r=
\begin{bmatrix}
\mathbf r_p\\
\mathbf r_\omega\\
\mathbf r_a\\
\mathbf r_{\mathrm{img}}
\end{bmatrix},
\qquad
\mathbf W=\operatorname{diag}(\mathbf W_p,\mathbf W_\omega,\mathbf W_a,\mathbf W_{\mathrm{img}}),
$$

对轨迹控制量而言，每一条观测只落在它所在节点区间附近的四个控制量上。例如 $t_k\in[t_\ell,t_{\ell+1})$ 时，对应的雅可比行可以画成

$$
\mathbf J_k=
\begin{bmatrix}
\mathbf 0&\cdots&\mathbf J_{k,\ell-3}&\mathbf J_{k,\ell-2}&\mathbf J_{k,\ell-1}&\mathbf J_{k,\ell}&\mathbf 0&\cdots&\mathbf 0
\end{bmatrix}.
$$

设所有控制点、控制姿态和偏置组成增量向量 $\delta\mathbf x$，其中旋转部分使用李代数的小扰动，记作 $\boxplus$。在当前估计附近一阶展开

$$
\mathbf r(\mathbf x\boxplus\delta\mathbf x)
\approx \mathbf r(\mathbf x)+\mathbf J\,\delta\mathbf x.
$$

加权最小二乘的线性方程就是

$$
\left(\mathbf J^\top\mathbf W\mathbf J+\mathbf H_{\mathrm{prior}}\right)\delta\mathbf x
=-\mathbf J^\top\mathbf W\mathbf r-\mathbf g_{\mathrm{prior}}.
\tag{M11}
$$

$\mathbf H_{\mathrm{prior}}$ 与 $\mathbf g_{\mathrm{prior}}$ 分别是先验在当前估计处的 Hessian 近似和梯度；没有先验时都取零。解出增量后，位置控制点相加更新，控制姿态通过指数映射更新，再计算新的残差。稀疏性针对轨迹控制量成立，偏置、外参等共享变量还会连接相应的多条观测。

![标准形式与累积形式](figures/cumulative-form.svg)

## 两类应用

### Poisson 表面重建

Poisson 表面重建通过 $\Delta\chi=\nabla\cdot\mathbf V$ 求隐式函数，$\mathbf V$ 来自有向点的法向。[原始方法](https://hhoppe.com/poissonrecon.pdf)在输入点处估计合适的等值水平后提取表面；只有减去该等值后，才可将表面称为零等值面。用局部基展开时，例如

$$
\chi(\mathbf x)=\sum_i c_i\,B(\mathbf x-\mathbf x_i).
$$

以三次张量积核为例，可取 $B(\mathbf x)=B_3(x)B_3(y)B_3(z)$，并按网格层级加入尺度。紧支撑限制基函数重叠，使弱形式中梯度内积组成的矩阵稀疏。具体核的次数、网格层级与滤波实现则取决于离散方案。

法向场构造、离散求解与等值面提取的关系见 [Poisson 专文](../poisson_recon_box_filter/index.html)。局部基展开与重复 box 平滑可以出现在同一条计算流程中，但不能将所有 Poisson 实现都归结为同一种积分图滤波。


### 连续时间 SLAM 与标定

连续时间轨迹将不同传感器的残差连接到同一组控制量。在每个时间戳求位姿或导数，就能处理逐点激光、卷帘图像与惯性测量，无需为每个观测单独增加一份轨迹状态。

![离散关键帧与连续时间 B 样条轨迹](figures/discrete-vs-continuous.svg)

常用的拆分表示分别在 $\mathbb R^3$ 与 $SO(3)$ 上描述位置和旋转，便于直接计算线加速度。联合 $SE(3)$ 样条则以刚体增量累积，平移与旋转发生耦合。两者描述的插值运动不同，需要结合运动类型与残差选择。

![拆分表示与 SE(3) 联合表示](figures/split-vs-se3.svg)

![样条接入连续时间 SLAM / 标定](figures/slam-pipeline.svg)

[LI-Calib](../li-calib-continuous-time/index.html)给出了直接使用轨迹导数的标定实例。[预积分](../imu-preintegration/index.html)则将一段 IMU 测量组织成离散状态之间的约束。两者的区别主要在于轨迹参数化与惯性测量的使用方式，不能仅用是否在线来划分。

## 小结

box 卷积给出均匀节点下的基数核，Cox–de Boor 递推将基函数定义推广到一般节点。局部支撑决定哪些系数参与求值，节点重数决定连接处的连续阶数。

均匀三次样条在一个区间内使用四个控制点，矩阵形式便于求值和求导；累积形式则显出一阶、二阶差分，并能推广到旋转轨迹。重建中的空间基与状态估计中的时间基，都是这些性质的具体使用。

## 符号约定

粗体小写为向量，粗体大写为矩阵或李群元素。

### 卷积核与一维函数

| 符号 | 含义 |
|------|------|
| $b(x)$、$B_0(x)$ | 单位宽度 box / 0 次基数 B 样条 |
| $B_d(x)$ | 次数 $d$ 的基数核：$b$ 自卷积 $d+1$ 次 |
| $*$ | 连续卷积 |
| $b_{\mathrm{d}}[n]$、$B_d^{\mathrm{d}}[n]$、$\beta[n]$ | 离散 box；离散 $d$ 次核；长度 2 的离散门 |
| $\operatorname{supp} f$ | 支撑集 |
| $C^{m}$ | $m$ 阶连续可微 |

### 节点、基函数与矩阵

| 符号 | 含义 |
|------|------|
| $t$、$t_i$、$\{t_i\}$ | 参数；节点；节点向量 |
| $\Delta t$、$u$ | 均匀间距；局部坐标 $u=(t-t_i)/\Delta t\in[0,1)$ |
| $d$、$k=d+1$ | 次数；阶数（部分文献的 order $k$） |
| $N_{i,d}(t)$ | 第 $i$ 个 $d$ 次基；支撑 $[t_i,t_{i+d+1}]$ |
| $\mathbf p_i$、$\mathbf p(t)$ | 控制点；曲线 $\sum_i\mathbf p_i N_{i,d}(t)$ |
| $b_j(u)$、$\mathbf u$、$\mathbf M^{(4)}$、$\mathbf P$ | 局部权重；单项式向量；均匀三次基矩阵；活跃控制点 |
| $\tilde\lambda_j$、$\tilde{\mathbf M}^{(4)}$ | 累积权重与累积矩阵 |

**下标习惯：** de Boor 常写「$[t_j,t_{j+1})$ 依赖 $\mathbf p_{j-d},\ldots,\mathbf p_j$」；轨迹实现常标成 $\mathbf p_i,\ldots,\mathbf p_{i+d}$。活跃个数均为 $d+1$。

### 刚体与 Poisson

| 符号 | 含义 |
|------|------|
| $SO(3)$、$SE(3)$ | 旋转群；刚体位姿群 |
| $\mathbf R(t)$、$\mathbf T(t)$、$\mathbf R_i$ | 旋转轨迹；位姿；旋转控制点 |
| $\mathrm{Exp}/\mathrm{Log}$ | 李群指数/对数 |
| $\boldsymbol\omega$、$\mathbf a$、$\mathbf g$ | 角速度；加速度相关量；重力 |
| $\chi$、$\mathbf V$、$c_i$ | 指示函数；引导梯度场；基系数 |

---

## 参考文献

1. Carl de Boor. *A Practical Guide to Splines*. Springer-Verlag, 1978.
2. Michael Unser, Akram Aldroubi, Murray Eden. *B-Spline Signal Processing*. IEEE Transactions on Signal Processing, 1993.
3. M. Kazhdan, M. Bolitho, H. Hoppe. *Poisson Surface Reconstruction*. SGP, 2006.
4. Hannes Ovrén, Per-Erik Forssén. *Trajectory Representation and Landmark Projection for Continuous-Time Structure from Motion*. IJRR, 2019.
5. Adrian Haarbach, Tolga Birdal, Slobodan Ilić. *Survey of Higher Order Rigid Body Motion Interpolation Methods…*. 3DV, 2018.
6. Christiane Sommer et al. *Efficient Derivative Computation for Cumulative B-Splines on Lie Groups*. CVPR, 2020.
7. Myoung-Jun Kim et al. *A General Construction Scheme for Unit Quaternion Curves…*. SIGGRAPH, 1995.
8. Jiajun Lv et al. *Targetless Calibration of LiDAR-IMU System Based on Continuous-time Batch Estimation*. IROS, 2020.
9. 本站：[Poisson 表面重建——B-spline 核函数和 box filter](../poisson_recon_box_filter/index.html).
10. 本站：[LI-Calib 论文解读](../li-calib-continuous-time/index.html).
