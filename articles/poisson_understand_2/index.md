---
title: "Poisson表面重建与有限元方法（FEM）的关系"
date: 2025-10-18T22:00:00+08:00
tags: ["Poisson reconstruction", "Finite Element Method", "Surface Reconstruction", "3D Reconstruction"]
excerpt: "Poisson 表面重建的本质是一种有限元离散化的 Poisson 方程求解。Kazhdan 等人使用八叉树与局部基函数形式实现了自适应的 FEM 求解，使其成为连接 PDE 与几何重建的典型案例。本篇文章详细介绍了 Poisson 表面重建与有限元方法之间的关系。"
draft: false
---

# Poisson 表面重建与有限元（FEM）方法之间的关系

**Poisson Surface Reconstruction** 本质上是用 **有限元方法（Finite Element Method, FEM）** 离散求解一个 **Poisson 方程**。  
这听起来很数学，但其实直观地说就是：

> “用一堆局部的小积木（基函数）拼出一个连续函数，并让它在平均意义上满足方程。”

---

## 一、为什么要用有限元？

我们要求解的偏微分方程（PDE）为(Poisson方程）：


$$
\begin{equation}
\Delta \chi = \nabla \cdot \mathbf{v}
\end{equation}
$$

其中 $\Delta$ 是拉普拉斯算子（包含二阶导数）。

其中：
- $\chi(\mathbf{x})$ 是隐函数；
- $\mathbf{v}(\mathbf{x})$ 是由点云法线方向定义的向量场。

计算机不能处理连续函数，只能处理有限维向量，因此必须**离散化**这个 PDE。  
常见的两种离散化思路如下：

| 方法 | 基本思想 | 特点 |
| ---- | ---------- | ---- |
| **有限差分法（FDM）** | 在规则格点上用差分近似导数 | 只能用均匀网格，结构固定 |
| **有限元法（FEM）** | 用局部基函数拼成连续近似 | 可用不规则、自适应网格（如八叉树） |

有限元法可以看作差分法的更灵活版本——它允许网格大小与形状根据数据密度自适应调整。

---

## 二、有限元的基本思想

设要求解的未知函数为 $\chi(\mathbf{x})$。  
我们用一组基函数 $\{\phi_i(\mathbf{x})\}$ 近似它：

$$
\begin{equation}
\chi(\mathbf{x}) \approx \sum_i c_i \, \phi_i(\mathbf{x}),
\end{equation}
$$

其中：
- $\phi_i(\mathbf{x})$ 为**局部形函数（shape function）**；
- $c_i$ 为对应系数（待求未知量）；
- 每个 $\phi_i$ 仅在局部单元上非零，因此称为“分片函数（piecewise function）”。

例如在一维中，每个基函数形如三角形：


```
       /\
      /  \
-----/----\-----
   i-1   i   i+1
```
在三维中，这些“积木”则对应于立方体、四面体或八叉树节点上的局部基。

---

## 三、从强形式到弱形式

Poisson 方程的强形式为：
$$\Delta \chi = \nabla \cdot \mathbf{v}.$$


直接对每个点要求方程成立（强形式）会遇到问题：

- $\Delta \chi$ 要求函数二阶可导；
- 而有限元中的分片线性函数二阶导数为零。

因此我们转化为“弱形式（weak form）”，即方程在**积分意义上**成立。

对任意测试函数 $\psi(\mathbf{x})$，要求：


$$
\begin{equation}
\int_\Omega \psi \, \Delta \chi \,  d\mathbf{x} = \int_\Omega \psi \, (\nabla \cdot \mathbf{v}) \,  d\mathbf{x}
\end{equation}
$$


这称为“弱形式”或“变分形式”（Weak / Variational Form）。


应用**分部积分（Integration by Parts）** 可将左式中的二阶导数转为一阶导数。下面是详细过程。 

我们利用下面的**分部积分（integration by parts）[推导详见附录A](#附录A)**
$$
\begin{equation}
\boxed{\displaystyle
\int_\Omega ψ\,\Delta χ \,d\mathbf{x}
= \int_{\partial\Omega} ψ\,\frac{\partial χ}{\partial n}\,dS
\;-\;
\int_\Omega \nabla ψ\cdot\nabla χ\,d\mathbf{x}}
\end{equation}
$$
对左边进行替换，得到： 

$$
\int_{\partial\Omega} ψ\,\frac{\partial χ}{\partial n}\,dS \;-\; \int_\Omega \nabla ψ\cdot\nabla χ\,d\mathbf{x} = \int_\Omega \psi \, (\nabla \cdot \mathbf{v}) \, d\mathbf{x}
$$

进一步整理后，得到：
$$
\begin{equation}
\int_\Omega \nabla ψ\cdot\nabla χ\,d\mathbf{x}  = - \int_\Omega \psi \, (\nabla \cdot \mathbf{v}) \, d\mathbf{x} + \int_{\partial\Omega} ψ\,\frac{\partial χ}{\partial n}\,dS 
\end{equation}
$$

右边第二项就是边界项，假设边界项消失（通常取 Dirichlet 边界或自然边界条件），就得到：

$$
\begin{equation}
\int_\Omega \nabla ψ\cdot\nabla χ\,d\mathbf{x}  = - \int_\Omega \psi \, (\nabla \cdot \mathbf{v}) \, d\mathbf{x}
\end{equation}
$$

这就是 **Poisson 方程的弱形式**。
这个形式有好处：只含一阶导数，更容易离散。

---
## 四、离散化并形成线性系统

令 $\chi = \sum_j c_j \phi_j$，取测试函数 $\psi = \phi_i$，代入公式（6）：

$$
\int_{\Omega} \nabla \phi_i \cdot \sum_j c_j \nabla \phi_j \, d\mathbf{x}
= - \int_{\Omega} \phi_i \, (\nabla \cdot \mathbf{v}) \, d\mathbf{x}.
$$

整理为矩阵形式：

$$
\sum_j \underbrace{\left( \int_{\Omega} \nabla \phi_i \cdot \nabla \phi_j \, d\mathbf{x} \right)}_{A_{ij}} c_j
= \underbrace{- \int_{\Omega} \phi_i \, (\nabla \cdot \mathbf{v}) \, d\mathbf{x}}_{b_i},
$$

即：

$$
A \, \mathbf{c} = \mathbf{b}.
$$

其中矩阵 $A$ 对称、正定，因此可通过共轭梯度（CG）或多重网格等高效方法求解。

---

## 五、 **边界项的物理/数学含义**

边界项 $\int_{\partial\Omega} ψ\,\frac{\partial χ}{\partial n}\,dS$ 表示“流”（或通量）穿过边界对弱等式的贡献：

- 如果你固定了 χ 在边界（Dirichlet），测试函数通常取为零在边界（消去边界项）。
- 如果你指定了法向导数（Neumann）值，则该边界项会包含已知的边界贡献并进入右端项 $b$。
- 在 Poisson 重建常见做法：把域设大并把 χ 在边界置 0（或用自然边界），实际计算中通常能安全忽略或处理该项。
---

## 六、Poisson Surface Reconstruction 的有限元实现

在 Kazhdan 等人的方法（2006, 2007）中：

- 基函数 $\phi_i(\mathbf{x})$ 选用 **分片三线性 B-spline**；
- 网格结构采用 **八叉树（Octree）**，可自适应细化；
- 向量场 $\mathbf{v}$ 来源于输入点云的法线；
- 方程求得的 $\chi(\mathbf{x})$ 是隐函数场；
- 最终通过提取等值面 $\chi = \text{iso}$ 得到三维表面。

这一过程正是一个 **有限元 Poisson 方程求解**：

> FEM 离散 → 解稀疏线性系统 → 取等值面。

---

## 七、与有限差分法的对比

| 比较项 | 有限差分 (FDM) | 有限元 (FEM) |
| ------- | ---------------- | -------------- |
| 网格类型 | 均匀体素格点 | 任意结构（如八叉树） |
| 导数计算 | 直接差分 | 基函数积分 |
| 可变分辨率 | 不支持 | 自适应 refinement |
| 精度 | 低阶 | 更高阶近似可扩展 |
| 内存效率 | 较差 | 仅在局部单元非零 |
| 稳定性 | 易受噪声影响 | 更平滑、鲁棒 |

因此，**FEM 更适合稀疏、不规则点云的 Poisson 重建**。

---

## 八、Poisson 图像融合的关系

Poisson 图像融合（Poisson Image Editing）同样解的是 Poisson 方程：

$$
\Delta I = \nabla \cdot \mathbf{v},
$$

只是定义域变成了 **二维图像域**，边界条件来自已知图像像素。  
Poisson Surface Reconstruction 则是在 **三维体素域** 上进行相同的数学操作。  
两者共享完全相同的 PDE 基础，只是应用场景与基函数不同。

---

## 九、直观理解与总结

你可以把 FEM 想象成：

> 用乐高积木（基函数）拼出一个连续曲面，  
> 调节每块的高度（系数 $c_i$），  
> 让整体尽量满足 Poisson 方程。

最终，有限元法让 Poisson Surface Reconstruction 具备：

- 数学上严格的 PDE 背景；
- 自适应空间分辨率；
- 高效的稀疏矩阵求解特性；
- 更鲁棒的噪声容忍性。

---

## 十、小结

> 有限元方法（FEM）通过基函数近似、弱形式求解，使得连续 Poisson 方程可在离散网格上高效求解。  
> Poisson Surface Reconstruction 正是利用 FEM 思想在三维空间上重建连续隐函数，从而生成高质量的表面。

---

**参考文献：**

- Kazhdan, M., Bolitho, M., & Hoppe, H. (2006). *Poisson Surface Reconstruction*.  
- Kazhdan, M. & Hoppe, H. (2013). *Screened Poisson Surface Reconstruction*.  
- Zienkiewicz, O. C., *The Finite Element Method: Its Basis and Fundamentals*.  
- Botsch, M. et al., *Polygon Mesh Processing*.




## 附录A：分部积分 {#附录A}

1 对任意标量场 $ψ(\mathbf{x})$ 和 $χ(\mathbf{x})$，有下面恒等式（乘积求散度的向量恒等式） [附录C](#附录C)：

$$
\nabla\cdot(ψ\,\nabla χ) = \nabla ψ \cdot \nabla χ + ψ\,\Delta χ
$$

这是从乘积求导（类似一维的 $(fg)'=f'g+fg'$）在向量形式下的推广。  
把它重排得到：

$$
ψ\,\Delta χ = \nabla\cdot(ψ\nabla χ) - \nabla ψ\cdot\nabla χ
$$

2 对区域积分并用散度定理（Divergence theorem）

把上式在区域 $\Omega$ 上积分：

$$
\int_\Omega ψ\,\Delta χ \,d\mathbf{x}
= \int_\Omega \nabla\cdot(ψ\nabla χ)\,d\mathbf{x} \;-\; \int_\Omega \nabla ψ\cdot\nabla χ\,d\mathbf{x}
$$

利用散度定理（Gauss theorem）[附录B](#附录B)把第一个体积分换成边界积分：

$$
\int_\Omega \nabla\cdot(ψ\nabla χ)\,d\mathbf{x}
= \int_{\partial\Omega} ψ\,(\nabla χ\cdot \mathbf{n})\,dS,
$$

其中 $\partial\Omega$ 是域的边界，$\mathbf{n}$ 是外法向，$\nabla χ\cdot\mathbf{n}=\frac{\partial χ}{\partial n}$（法向导数）。

因此合并得：

$$
\boxed{\displaystyle
\int_\Omega ψ\,\Delta χ \,d\mathbf{x}
= \int_{\partial\Omega} ψ\,\frac{\partial χ}{\partial n}\,dS
\;-\;
\int_\Omega \nabla ψ\cdot\nabla χ\,d\mathbf{x}}
$$

可以看到，分部积分后出现边界项＋内积项。

分部积分的意义在于我们把一个二阶方程转换成一阶方程。


---

## 附录B 散度定理 {#附录B}

对于一个任意的光滑向量场 $\mathbf{F}$：

$$\int_{\Omega} \nabla \cdot \mathbf{F} \, dV = \int_{\partial \Omega} \mathbf{F} \cdot \mathbf{n} \, dS$$





其中：

- $\Omega$：积分域（比如三维空间中的一个体积）
- $\partial \Omega$：这个体积的边界面
- $\mathbf{n}$：边界面上外法向量
- $\mathbf{F}$：任意向量场

**左边**是一个$\nabla \cdot \mathbf{F}$体积积分（volume integral）
$\nabla \cdot \mathbf{F}$（读作 divergence of F）表示这一点是不是“流的源头或汇点”。
- 如果 $\nabla \cdot \mathbf{F} > 0$：  
   表示流体从这个点“源源不断流出” —— 有点像喷泉口；
- 如果 $\nabla \cdot \mathbf{F} < 0$：  
   表示流体“流入”这个点 —— 像吸进去；
- 如果 $\nabla \cdot \mathbf{F} = 0$：  
   表示进出相等，局部守恒。

**右边**是一个$\mathbf{F} \cdot \mathbf{n}$边界面积积分（surface integral）
在边界面上，$\mathbf{F} \cdot \mathbf{n}$表示在该点上，流体“穿出”表面的量
- 如果 F 与 n 同方向 → 表示流出；  
- 如果反方向 → 表示流入；  
- 如果垂直 → 表示不穿出。


整个散度定理的意思是：


> “体积内的散度积分 = 表面积上通量积分”

**直觉解释一句话总结**

> “所有点内部流出的总量 = 实际从表面流出去的量”

或者说：

> “体积里的源汇之和 = 边界上的通量之和”

这就是散度定理。

---

## 附录C 乘积求散度的向量恒等式 {#附录C}

这个公式是：

$$
\nabla \cdot (\psi \nabla \chi)
= \nabla \psi \cdot \nabla \chi + \psi \, \Delta \chi
$$

我们要弄懂每个符号是什么意思，然后一步步推导。


**符号说明**

| 符号| 名称| 含义 | 类比（一维）|
| ---| ---| ---- | ---|
| $\psi(\mathbf{x})$| 测试函数| 任意光滑的标量函数 | $ψ(x)$ |
| $\chi(\mathbf{x})$  | 待求函数（隐函数）| 我们要求的场（例如 Poisson 方程的未知量）| $χ(x)$|
| $\nabla$| 梯度算子 (gradient)| $\nabla = \left(\frac{\partial}{\partial x}, \frac{\partial}{\partial y}, \frac{\partial}{\partial z}\right)$| $\frac{d}{dx}$|
| $\nabla \cdot$| 散度算子 (divergence)| 把向量场转成标量场| 在 1D 中就是$\frac{d}{dx}$ |
| $\nabla \chi$ | 取梯度 | 得到 $\chi$ 在各方向的偏导组成的向量 | $χ'(x)$|
| $\Delta \chi$ | 拉普拉斯算子 (Laplacian) | $\Delta \chi = \nabla \cdot (\nabla \chi) = \frac{\partial^2 \chi}{\partial x^2} + \frac{\partial^2 \chi}{\partial y^2} + \frac{\partial^2 \chi}{\partial z^2}$ | $χ''(x)$ |
| $\nabla \psi \cdot \nabla \chi$ | 向量点积 | 各方向偏导乘积之和 | $ψ'(x)χ'(x)$ |

**推导（从最基本定义出发）**

我们从三维坐标展开：

$$
\nabla \cdot (\psi \nabla \chi)
= \frac{\partial}{\partial x}(\psi \frac{\partial \chi}{\partial x}) + \frac{\partial}{\partial y}(\psi \frac{\partial \chi}{\partial y})  + \frac{\partial}{\partial z}(\psi \frac{\partial \chi}{\partial z})
$$

用**一维乘积法则**展开每一项：

$$
\frac{\partial}{\partial x}(\psi \frac{\partial \chi}{\partial x})
= \frac{\partial \psi}{\partial x} \frac{\partial \chi}{\partial x}  + \psi \frac{\partial^2 \chi}{\partial x^2},
$$

同理对 $y, z$ 方向。

把所有加起来：

$$
\nabla \cdot (\psi \nabla \chi)
= \left(
\frac{\partial \psi}{\partial x} \frac{\partial \chi}{\partial x}+ \frac{\partial \psi}{\partial y} \frac{\partial \chi}{\partial y}+ \frac{\partial \psi}{\partial z} \frac{\partial \chi}{\partial z}
\right)+ \\ \psi \left(\frac{\partial^2 \chi}{\partial x^2} + \frac{\partial^2 \chi}{\partial y^2} + \frac{\partial^2 \chi}{\partial z^2} \right)
$$

用向量符号重新写：

$$
\boxed{
\nabla \cdot (\psi \nabla \chi)
= \underbrace{\nabla \psi \cdot \nabla \chi}_{\text{梯度点积项}} + \underbrace{\psi \, \Delta \chi}_{\text{乘上拉普拉斯项}}
}
$$

---
