---
title: "Poisson 表面重建的核心思想以及与有限元方法（FEM）的关系"
date: 2025-10-18T22:00:00+08:00
tags: ["Poisson reconstruction", "Finite Element Method", "Surface Reconstruction", "3D Reconstruction"]
excerpt: "从点云法向场出发，逐步说明 Poisson 表面重建如何恢复隐式函数，以及有限元、八叉树和 B-spline 如何参与离散求解。"
draft: false
---

# Poisson 表面重建：从法向场到有限元离散

点云表面重建要解决的问题是：已知一组位于物体表面附近的点，以及每个点的法向量，如何恢复一个连续的三维表面？

Poisson Surface Reconstruction 的思路不是直接把点连接成三角形，而是先在三维空间中寻找一个标量场，使它的梯度整体上符合输入点云提供的法向信息。求出这个标量场之后，再提取一个等值面作为重建结果。

这条思路可以分成四步：

1. 将带法向的点云转成一个连续或离散的向量场；
2. 把向量场看成隐式函数梯度的近似，并得到 Poisson 方程；
3. 用有限元风格的基函数离散这个方程，得到稀疏线性系统；
4. 求出标量场后，用等值面提取方法生成三角网格。

**阅读路线：** 第 1 节说明点云、隐式函数和等值面；第 2 节解释法向场为什么会导出 Poisson 方程；第 3～5 节推导弱形式、有限元离散和线性系统；第 6 节把这些数学对象对应到八叉树实现；第 7 节总结边界条件、FEM 与有限差分的关系。全文使用同一组符号，不再把核心推导和附录重复展开。

## 摘要

设输入点云为

$$
\{(p_i,n_i)\}_{i=1}^{N},
$$

其中 $p_i\in\mathbb R^3$ 是采样点，$n_i$ 是已经定向的法向量。我们希望找到一个标量场 $\chi(\mathbf x)$，使得它的某个等值面能够表示物体表面，并且在表面附近满足

$$
\nabla\chi(\mathbf x)\approx \mathbf V(\mathbf x),
$$

其中 $\mathbf V$ 是由点云法向构造出的向量场。

对这个关系取散度，可以得到

$$
\Delta\chi=\nabla\cdot\mathbf V.
$$

这就是 Poisson 方程。计算机不能直接求解连续函数，于是用局部基函数近似

$$
\chi_h(\mathbf x)=\sum_j c_j\phi_j(\mathbf x),
$$

再通过弱形式得到

$$
A\mathbf c=\mathbf b.
$$

矩阵 $A$ 来自基函数梯度之间的内积，向量 $\mathbf b$ 来自输入法向场。解出系数 $\mathbf c$ 后，对 $\chi_h$ 提取合适的等值面，就得到重建表面。

需要先说明一个容易混淆的点：理想的二值指示函数在表面处是不连续的，它的梯度应理解为分布意义下集中在边界上的量，而不是普通的光滑函数梯度。实际算法求解的是由有限基函数表示的平滑近似场，因此“法向是指示函数的梯度”是一种几何动机，不能按普通点值微分逐字理解。

## 1. 从带法向点云到隐式表面

### 1.1 输入数据和重建目标

点云重建通常提供以下数据：

- 三维采样点 $p_i$；
- 与采样点对应的法向量 $n_i$；
- 法向量的方向已经尽可能统一，例如都指向物体外部。

法向方向非常重要。如果相邻点的法向随意翻转，构造出的向量场会互相抵消，Poisson 方程也就无法得到一致的表面方向。

点云本身只是离散样本，并没有告诉我们物体内部的每个位置属于“内”还是“外”。Poisson 重建引入一个定义在三维空间中的标量场，把表面变成这个场的等值面。这样，复杂的孔洞、分叉和闭合结构都可以用隐式方式表示，不需要把表面写成单值函数 $z=f(x,y)$。

### 1.2 指示函数和它的局限

对一个实体 $M\subset\mathbb R^3$，理想指示函数可以写成

$$
\chi_M(\mathbf x)=
\begin{cases}
1, & \mathbf x\in M,\\
0, & \mathbf x\notin M.
\end{cases}
$$

它记录了空间中每个位置属于物体内部还是外部。实体的边界记作 $\partial M$，这里的 $\partial$ 是“取边界”的算子，不是偏导数符号：

$$
\partial M=\text{the boundary of }M.
$$

如果把理想指示函数直接拿来求梯度，那么函数在表面处的跳变会产生分布意义下的表面项。在普通数值计算中，我们更关心一个平滑的近似场 $\chi_h$，让它在表面附近从内部值过渡到外部值。这个近似场不必严格等于 0 或 1，但它可以通过等值面表达表面。

### 1.3 什么是等值面

给定标量场 $f:\mathbb R^3\to\mathbb R$ 和常数 $\tau$，等值集定义为

$$
L_\tau=\{\mathbf x\in\mathbb R^3\mid f(\mathbf x)=\tau\}.
$$

在三维空间中，合适的等值集通常是一张曲面。例如：

$$
f(x,y,z)=x^2+y^2+z^2
$$

的等值集 $f=1$ 是单位球面。

等值面的法向方向来自梯度。若曲面上有一条切向运动 $d\mathbf x$，由于沿等值面移动时函数值不变，有

$$
df=\nabla f\cdot d\mathbf x=0.
$$

因此 $\nabla f$ 与曲面的切平面正交，是曲面的法向方向。Poisson 重建正是利用了这条关系：让求得的标量场梯度在表面附近与输入法向一致。

## 2. 从法向场得到 Poisson 方程

### 2.1 构造向量场

输入只在离散点 $p_i$ 上给出法向 $n_i$。为了写出空间方程，需要把这些离散样本扩展为一个向量场 $\mathbf V(\mathbf x)$。直观地说，点 $p_i$ 的法向会影响它附近的一小片区域，所有点的影响叠加后形成向量场。

可以用核函数、局部基函数或 splatting 等方式完成这个扩展。写成抽象形式就是

$$
\mathbf V(\mathbf x)\approx\sum_{i=1}^{N}n_i\,w_i(\mathbf x),
$$

其中 $w_i(\mathbf x)$ 是以 $p_i$ 为中心的局部权重。实际实现不一定显式构造一个规则体素上的 $\mathbf V$，也可以在积分点处直接评价点云对基函数的贡献。

### 2.2 梯度匹配

我们希望标量场的梯度尽量接近这个向量场：

$$
\nabla\chi\approx\mathbf V.
$$

这个关系不是说每个位置都能精确满足，而是说在点云覆盖的区域内，求得的场要与法向信息整体一致。由于输入点有噪声、采样不均匀且法向只能在有限位置获得，使用一个全局的标量场来解释这些局部向量，实际上也起到了平滑和正则化的作用。

### 2.3 取散度得到 Poisson 方程

对梯度匹配关系取散度：

$$
\nabla\cdot\nabla\chi
\approx
\nabla\cdot\mathbf V.
$$

利用拉普拉斯算子的定义

$$
\Delta\chi=\nabla\cdot(\nabla\chi),
$$

得到 Poisson 方程

$$
\boxed{\Delta\chi=\nabla\cdot\mathbf V.}
$$

这里的正负号取决于法向方向和指示函数的内外约定。如果法向全部反向，右端向量场也会反向，求出的标量场方向和等值面取值会相应变化，但几何表面仍由一致的等值面给出。阅读不同论文或代码时，应先确认它们对法向方向和 Poisson 方程符号的约定。

## 3. 为什么要从强形式转到弱形式

### 3.1 强形式的问题

Poisson 方程的强形式是

$$
\Delta\chi=\nabla\cdot\mathbf V\quad\text{in }\Omega,
$$

其中 $\Omega$ 是包围点云的三维计算域。

如果要求方程在每个点严格成立，就需要对 $\chi$ 求二阶导数。但有限元常用的分片线性基函数在单元内部只有一阶导数，二阶导数并不适合作为普通函数直接计算。因此，有限元不要求方程逐点成立，而是要求它对一组测试函数在积分意义上成立。

### 3.2 乘以测试函数并积分

取一个足够光滑的测试函数 $\psi(\mathbf x)$，将强形式乘上 $\psi$ 并在 $\Omega$ 上积分：

$$
\int_\Omega\psi\,\Delta\chi\,d\mathbf x
=
\int_\Omega\psi\,(\nabla\cdot\mathbf V)\,d\mathbf x.
$$

对左侧使用乘积散度恒等式：

$$
\nabla\cdot(\psi\nabla\chi)
=\nabla\psi\cdot\nabla\chi+\psi\,\Delta\chi.
$$

因此

$$
\psi\,\Delta\chi
=\nabla\cdot(\psi\nabla\chi)-\nabla\psi\cdot\nabla\chi.
$$

在区域上积分，再使用散度定理

$$
\int_\Omega\nabla\cdot\mathbf F\,dV
=\int_{\partial\Omega}\mathbf F\cdot\mathbf n\,dS,
$$

得到

$$
\int_\Omega\psi\,\Delta\chi\,d\mathbf x
=
\int_{\partial\Omega}\psi\,\frac{\partial\chi}{\partial n}\,dS
-
\int_\Omega\nabla\psi\cdot\nabla\chi\,d\mathbf x.
$$

于是，Poisson 方程的弱形式可以写为

$$
\int_\Omega\nabla\psi\cdot\nabla\chi\,d\mathbf x
=
-\int_\Omega\psi\,(\nabla\cdot\mathbf V)\,d\mathbf x
+\int_{\partial\Omega}\psi\,\frac{\partial\chi}{\partial n}\,dS.
$$

当测试函数在 Dirichlet 边界上为零，或者边界项按照所选边界条件被单独处理时，可以暂时写成

$$
\boxed{
\int_\Omega\nabla\psi\cdot\nabla\chi\,d\mathbf x
=
-\int_\Omega\psi\,(\nabla\cdot\mathbf V)\,d\mathbf x.}
$$

左侧只含 $\chi$ 的一阶导数，这正是有限元离散更方便的原因。

### 3.3 右端项的等价写法

如果对右端的散度也做一次分部积分，则有

$$
-\int_\Omega\psi\,(\nabla\cdot\mathbf V)\,dV
=
\int_\Omega\nabla\psi\cdot\mathbf V\,dV
-
\int_{\partial\Omega}\psi(\mathbf V\cdot\mathbf n)\,dS.
$$

在边界项相容或被忽略的情况下，右端可以改写为

$$
\boxed{
b(\psi)=\int_\Omega\nabla\psi\cdot\mathbf V\,dV.}
$$

这个形式在数值实现中很有用，因为它不要求先显式计算 $\nabla\cdot\mathbf V$。只要能在积分点处评价向量场 $\mathbf V$，就可以直接计算右端贡献。两种写法的符号必须和边界处理、法向方向保持一致，不能在代码中混用。

## 4. 用有限元基函数离散

### 4.1 用基函数表示未知场

有限元的核心是用有限个局部基函数近似连续未知函数：

$$
\chi_h(\mathbf x)=\sum_j c_j\phi_j(\mathbf x).
$$

其中：

- $\phi_j$ 是已知的局部基函数；
- $c_j$ 是待求系数；
- $\chi_h$ 是计算机实际求出的离散近似场。

由于每个基函数只在局部区域内非零，两个基函数的支撑域不相交时，它们对同一个积分的贡献为零。这会使最终矩阵具有稀疏结构。

测试函数也选为同一组基函数，即 $\psi=\phi_i$。将近似式代入弱形式左侧：

$$
\begin{aligned}
\int_\Omega\nabla\phi_i\cdot\nabla\chi_h\,d\mathbf x
&=\int_\Omega\nabla\phi_i\cdot
\nabla\left(\sum_jc_j\phi_j\right)d\mathbf x\\
&=\sum_jc_j\int_\Omega
\nabla\phi_i\cdot\nabla\phi_j\,d\mathbf x.
\end{aligned}
$$

定义

$$
A_{ij}=\int_\Omega\nabla\phi_i\cdot\nabla\phi_j\,d\mathbf x,
$$

以及

$$
b_i=-\int_\Omega\phi_i(\nabla\cdot\mathbf V)\,d\mathbf x,
$$

就得到线性系统

$$
\boxed{A\mathbf c=\mathbf b.}
$$

如果使用不显式计算散度的等价形式，则右端可写成

$$
b_i=\int_\Omega\nabla\phi_i\cdot\mathbf V\,d\mathbf x,
$$

前提仍然是边界项和符号约定已经一致处理。

### 4.2 刚度矩阵从哪里来

矩阵 $A$ 的元素是两个基函数梯度的内积，因此它衡量了不同局部基函数之间的梯度耦合。它通常被称为刚度矩阵：

$$
A_{ij}=\langle\nabla\phi_i,\nabla\phi_j\rangle_{L^2(\Omega)}.
$$

对于任意系数向量 $\mathbf c$，有

$$
\mathbf c^\top A\mathbf c
=\int_\Omega\left\|\nabla\chi_h\right\|^2d\mathbf x\ge 0.
$$

因此 $A$ 至少是半正定的。在纯 Neumann 边界条件下，给 $\chi_h$ 加一个常数不会改变梯度，系统会存在常数方向的零空间；固定 Dirichlet 边界、增加约束或去除一个自由度后，才可以得到正定系统。实际 Poisson 重建的边界和域设置承担了消除这种不确定性的作用。

### 4.3 单元分解和局部装配

把计算域分成单元集合 $\mathcal T$：

$$
A_{ij}=\sum_{K\in\mathcal T}
\int_K\nabla\phi_i\cdot\nabla\phi_j\,dV.
$$

在一个单元 $K$ 内，只需要考虑在该单元上非零的局部基函数。先计算局部矩阵

$$
A^K_{ab}=\int_K\nabla\phi_a\cdot\nabla\phi_b\,dV,
$$

再根据局部到全局的索引映射，将 $A^K_{ab}$ 累加到全局矩阵对应位置。这就是有限元中的 local-to-global assembly。

对于线性三角形或四面体基函数，基函数在单元内部是一阶多项式，梯度为常量，因此

$$
A^K_{ab}
=\left(\nabla\phi_a\big|_K\cdot
\nabla\phi_b\big|_K\right)|K|,
$$

其中 $|K|$ 是单元面积或体积。对于 B-spline 或更高阶基函数，梯度可能不是常量，通常在单元内使用高斯积分：

$$
A^K_{ab}
\approx\sum_qw_q\,
\nabla\phi_a(\mathbf x_q)\cdot
\nabla\phi_b(\mathbf x_q).
$$

## 5. 右端如何承载点云法向

### 5.1 直接使用散度形式

如果已经在计算域中构造出向量场 $\mathbf V$，可以先计算 $\nabla\cdot\mathbf V$，再组装

$$
b_i=-\int_\Omega\phi_i(\nabla\cdot\mathbf V)\,dV.
$$

用数值积分近似为

$$
b_i\approx-
\sum_{K\in\mathcal T}\sum_q
w_q\,\phi_i(\mathbf x_q)
(\nabla\cdot\mathbf V)(\mathbf x_q).
$$

这种方法概念直接，但对稀疏、带噪的法向样本，先构造向量场再求散度可能放大噪声。

### 5.2 直接对法向场积分

采用分部积分后的形式，可以直接计算

$$
b_i=\int_\Omega\nabla\phi_i\cdot\mathbf V\,dV.
$$

数值上写成

$$
b_i\approx\sum_{K\in\mathcal T}\sum_q
w_q\,\nabla\phi_i(\mathbf x_q)\cdot
\mathbf V(\mathbf x_q).
$$

如果使用点云样本直接构造贡献，可以把向量场的评价理解为邻域点的加权叠加。对某个基函数 $B_o$，一种抽象的点云贡献形式是

$$
b_o\propto\sum_p n_p\cdot\nabla B_o(p).
$$

比例系数和具体权重取决于基函数、采样密度和实现中的归一化方式，因此这条式子表达的是结构，而不是所有实现都完全相同的公式。

### 5.3 为什么右端是稀疏的

基函数具有局部支撑。一个点 $p$ 只会影响支撑域覆盖它的少数基函数，因此它只会向有限个 $b_i$ 累加贡献。类似地，一个基函数只与附近基函数耦合，所以 $A$ 也是稀疏矩阵。

这两个局部性共同决定了 Poisson 重建可以处理规模较大的点云：不需要存储一个每个节点都和所有节点相连的稠密系统。

## 6. 八叉树、B-spline 与等值面提取

### 6.1 八叉树负责空间自适应

在规则体素网格中，整个空间使用同一分辨率，空旷区域也会消耗大量计算和内存。八叉树通过递归地把一个立方体分成八个子块，让空间分辨率可以随点云分布变化：

- 点云稠密、几何变化快的区域可以细分；
- 空旷或变化平缓的区域保持较粗单元；
- 每个节点或局部区域关联有限个基函数。

八叉树本身不是 Poisson 方程，也不是求解器。它提供的是自适应的空间层次和离散支撑结构。

### 6.2 B-spline 或局部基函数负责近似

在八叉树上，可以使用局部 B-spline、box spline 或其他分片基函数表示 $\chi_h$：

$$
\chi_h(\mathbf x)=\sum_i c_iB_i(\mathbf x).
$$

基函数的选择影响三个方面：

1. 标量场的平滑性；
2. 矩阵 $A$ 的稀疏模式；
3. 单元积分和多层求解的计算成本。

“三线性插值”和“B-spline”在具体实现中可能对应不同层次的描述，不能简单地把所有八叉树基函数都称为同一个函数。准确的说法是：实现使用局部、具有有限支撑的基函数，并在自适应八叉树结构上完成积分和装配。

### 6.3 求解线性系统

装配完成后得到

$$
A\mathbf c=\mathbf b.
$$

矩阵 $A$ 通常是大型、稀疏、对称的。根据边界条件和离散化方式，可以使用共轭梯度、预条件共轭梯度、多重网格或其他稀疏线性系统方法求解。

公式中的 $A^{-1}$ 是数学记号，数值实现通常不会显式构造逆矩阵，而是直接求解线性方程组。

### 6.4 从标量场提取表面

解出系数后，在空间中得到近似场 $\chi_h(\mathbf x)$。选择一个等值阈值 $\tau$，目标表面是

$$
S_\tau=\{\mathbf x\mid\chi_h(\mathbf x)=\tau\}.
$$

在体素或局部网格上，Marching Cubes 等算法会检查相邻顶点的标量值，判断等值面穿过哪些边，并据此生成三角形。

阈值不一定严格是 $0.5$。它取决于标量场的归一化、法向方向、边界处理以及实现细节。更稳妥的理解是：算法从求得的隐式场中选择一个与表面对应的等值面，而不是把 $0.5$ 当成所有实现都必须使用的常数。

## 7. 把数学对象和算法步骤对应起来

| 数学对象 | 在重建中的作用 | 典型实现 |
|---|---|---|
| 点 $p_i$ 与法向 $n_i$ | 输入几何和方向信息 | 点云采样 |
| 向量场 $\mathbf V$ | 汇总局部法向约束 | splatting、局部核、基函数积分 |
| 标量场 $\chi_h$ | 表示待恢复的隐式几何 | 基函数系数 $\mathbf c$ |
| Poisson 方程 | 将梯度约束转成可求解的 PDE | $\Delta\chi=\nabla\cdot\mathbf V$ |
| 弱形式 | 避免直接计算二阶导数 | 梯度内积积分 |
| 基函数 $\phi_i$ | 将无限维函数变成有限维向量 | 局部 B-spline 等 |
| 刚度矩阵 $A$ | 描述基函数之间的梯度耦合 | 稀疏矩阵装配 |
| 右端 $\mathbf b$ | 承载点云法向信息 | 散度积分或梯度—向量场积分 |
| 八叉树 | 提供自适应空间分辨率 | 局部细分和邻域关系 |
| 等值面提取 | 将隐式场转换为网格 | Marching Cubes 等 |

因此，完整流程可以写成：

$$
\text{点云法向}
\longrightarrow
\mathbf V
\longrightarrow
\text{弱形式}
\longrightarrow
A\mathbf c=\mathbf b
\longrightarrow
\chi_h
\longrightarrow
\text{等值面网格}.
$$

## 8. FEM 与有限差分有什么区别

两者都可以离散 Poisson 方程，但离散方式不同。

| 比较项 | 有限差分法（FDM） | 有限元法（FEM） |
|---|---|---|
| 基本对象 | 网格点上的函数值 | 局部基函数及其系数 |
| 导数处理 | 用相邻点差分近似 | 通过弱形式和积分得到 |
| 网格适应性 | 规则网格最直接 | 适合局部细分和不规则单元 |
| 矩阵结构 | 来自差分模板 | 来自基函数支撑和局部装配 |
| 边界条件 | 在网格方程中处理 | 通过试探空间、边界项或约束处理 |
| 结果表示 | 网格点值 | 基函数线性组合 |

不能简单地说 FEM 一定比 FDM 更准确或更鲁棒。效果取决于基函数、网格、边界条件、噪声模型和求解器。对 Poisson 表面重建而言，有限元风格的局部基函数和八叉树结构很适合点云密度不均匀的三维场景，但这是一种建模与离散选择，不是所有问题上的绝对优劣结论。

## 9. 边界项和容易混淆的概念

### 9.1 计算域边界不等于物体表面

Poisson 方程定义在计算域 $\Omega$ 上，$\partial\Omega$ 是计算域的外边界；物体表面是 $\partial M$，或更具体地说是隐式场的某个等值面。这两个边界不是同一个概念：

$$
\partial\Omega\ne\partial M.
$$

通常把计算域设在包含点云的较大包围盒中，避免外边界过近地影响重建表面。

### 9.2 Dirichlet 和 Neumann 边界条件

弱形式中的边界项为

$$
\int_{\partial\Omega}
\psi\frac{\partial\chi}{\partial n}\,dS.
$$

两类常见边界条件是：

- Dirichlet 条件：直接指定边界上的 $\chi$；相应测试函数通常在该边界上为零；
- Neumann 条件：指定法向导数 $\partial\chi/\partial n$；边界项会进入右端项。

“忽略边界项”不是无条件成立的代数规则，而是对测试函数、边界条件或足够大的计算域作出假设后的简写。实现时必须让边界处理与矩阵、右端项保持一致。

### 9.3 $\partial M$ 不是偏导数

在几何记号中，$\partial M$ 表示实体 $M$ 的边界。它和 $\partial/\partial x$ 中的偏导符号形状相同，但含义不同：

| 记号 | 含义 |
|---|---|
| $\partial M$ | 集合 $M$ 的边界 |
| $\partial f/\partial x$ | 函数 $f$ 对 $x$ 的偏导数 |
| $\nabla f$ | 标量场的梯度 |
| $\Delta f$ | 拉普拉斯算子 |

### 9.4 指示函数梯度不是普通光滑梯度

理想指示函数在表面处发生跳变，它的梯度集中在边界上，需要用分布或测度理解。实际有限元计算使用的是有限基函数展开的平滑近似 $\chi_h$，所以数值上计算的是 $\nabla\chi_h$。把输入法向视为梯度信息，是从理想几何关系得到的建模动机，而不是说二值函数可以在表面处直接用普通微分规则计算。

## 10. 与 Poisson 图像融合的关系

Poisson 图像融合也会出现类似方程：

$$
\Delta I=\nabla\cdot\mathbf v,
$$

其中 $I$ 是二维图像域中的像素强度，$\mathbf v$ 是希望保留的梯度场。它与 Poisson 表面重建共享同一个 PDE 结构：根据梯度约束恢复标量场。

区别在于：

- 图像融合的定义域通常是二维区域，边界像素往往是已知的；
- 表面重建的定义域是三维空间，输入约束来自点云法向；
- 两者使用的离散网格、基函数、边界条件和等值面提取步骤不同。

所以可以说它们共享数学骨架，但不能把两个应用的所有边界条件和实现细节直接互换。

## 11. 总结

Poisson 表面重建的主线可以概括为：

1. 点云采样点和法向量提供局部几何约束；
2. 这些法向被组织成向量场 $\mathbf V$；
3. 假设 $\mathbf V$ 近似某个隐式标量场的梯度，得到

$$
\Delta\chi=\nabla\cdot\mathbf V;
$$

4. 对 Poisson 方程写弱形式，把二阶导数变成一阶梯度内积；
5. 用局部基函数近似 $\chi$，组装稀疏线性系统

$$
A\mathbf c=\mathbf b;
$$

6. 求出系数后得到隐式场 $\chi_h$，再提取对应等值面。

有限元、八叉树和等值面提取分别解决不同问题：有限元负责把连续 PDE 变成有限维系统，八叉树负责提供自适应的空间结构，Marching Cubes 等算法负责把标量场转换为三角网格。把这几层职责分开，Poisson 表面重建的整体流程就不会变成一组需要背诵的公式。

## 参考资料

- Kazhdan, M., Bolitho, M., & Hoppe, H. (2006). *Poisson Surface Reconstruction*.
- Kazhdan, M. & Hoppe, H. (2013). *Screened Poisson Surface Reconstruction*.
- Zienkiewicz, O. C. et al. *The Finite Element Method: Its Basis and Fundamentals*.
- Botsch, M. et al. *Polygon Mesh Processing*.
