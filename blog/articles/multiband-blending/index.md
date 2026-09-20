---
title: "图像融合经典算法——多频段融合"
date: 2026-09-17
categories: [image-processing]
tags: [Image Fusion, Laplacian Pyramid, Multi-band Blending, OpenCV, Computer Vision]
excerpt: "先说明单张图像的高斯—拉普拉斯金字塔分解与可逆重建，再解释不同频段处理图像的原因，以及多频段融合缓和拼接接缝的机制。"
draft: false
---

# 图像融合经典算法——多频段融合

> 多频段融合的核心是可重建的多尺度表示。高斯金字塔逐层保留低频结构，拉普拉斯层记录相邻尺度之间的残差；各层经过独立处理后，仍可按照相同的重建关系恢复到像素空间。单张图像的分解与重建体现了表示的可逆性，尺度与频率的关系决定了各层的作用，两幅图像在对应层上的加权形成多频段融合。权值、颜色一致性和层数会影响这一过程的具体表现。

多频段融合建立在可重建的多尺度表示之上。每幅图像经过高斯—拉普拉斯金字塔分解后，各个尺度成分可以分别参与加权，融合结果再通过重建回到像素空间。

> **术语说明** 英文中的 *band* 在这里表示一个频率范围或尺度范围。标题使用“多频段融合”，是为了强调这里处理的是频率和尺度，而不是多光谱图像中的波段。严格来说，拉普拉斯层由相邻尺度差分得到，属于具有带通意义的多尺度子带，并非傅里叶域中彼此完全不重叠的理想频带。

---

## 1. 单张图像的高斯金字塔与拉普拉斯分解

单张图像 $I$ 是这套表示的基本对象。拉普拉斯金字塔将其表示成几个尺度的成分，同时保留恢复原图所需的信息。

### 1.1 高斯金字塔逐层变粗

高斯金字塔从原图开始。第 0 层就是原图。

$$
G_0 = I.
$$

下一层先做低通滤波，再下采样。

$$
G_{i+1} = \operatorname{Down}(\operatorname{Blur}(G_i)).
$$

低通滤波会削弱快速变化的内容，例如细小纹理、锐利边缘和噪声；下采样则把图像放到更粗的空间尺度上。因此，$G_{i+1}$ 的生成包含两个步骤，先去除新采样网格中难以稳定表示的高频，再完成尺寸缩小。

几层高斯图像所保留的内容如下。

| 层 | 表示 | 主要保留的内容 |
| --- | --- | --- |
| $G_0$ | 原始分辨率 | 细节、边缘和整体结构 |
| $G_1$ | 更粗的尺度 | 中等尺度结构，细节减少 |
| $G_2$ | 更粗的尺度 | 轮廓、亮度和大范围形状 |
| $G_N$ | 最粗的尺度 | 最低频的整体信息 |

所以，高斯金字塔提供了一组“逐渐变粗的观察结果”。低层看得细，高层看得概括。

### 1.2 高斯金字塔不能单独还原原图

高斯金字塔本身只保留逐层变粗的图像。每次下采样之前都会进行低通，细纹理和边缘被压低；下采样之后，像素数量也减少了。若只保留最粗的 $G_N$，就无法知道原图在各个位置曾经有哪些细节。

即使把 $G_N$ 重新放大，得到的也只是一个平滑的近似图。放大操作可以插值已有样本，但不能凭空恢复已经丢掉的高频信息。

高斯金字塔描述了不同尺度的图像如何生成，但没有保存从粗尺度回到细尺度所需的高频残差。

### 1.3 拉普拉斯层保存缩小时丢失的内容

对 $G_{i+1}$ 做上采样，回到 $G_i$ 的尺寸，记作下面的结果。

$$
\tilde G_i = \operatorname{Expand}(G_{i+1}).
$$

$\tilde G_i$ 只能描述 $G_i$ 中较粗的部分，于是把两者相减。

$$
L_i = G_i - \tilde G_i.
$$

这个 $L_i$ 就是拉普拉斯金字塔的第 $i$ 层。它保存当前尺度中，下一层的粗略预测没有解释掉的部分。

由定义可以得到下面的关系。

$$
G_i = L_i + \operatorname{Expand}(G_{i+1}).
$$

由此可见，$L_i$ 是当前层相对于更粗层的残差。边缘、纹理和局部亮度变化通常会进入较细的 $L_i$；大范围的亮度、颜色和整体结构则更多地留在更粗的层。

最粗层没有下一层可以用来计算差分，因此直接保留为

$$
L_N = G_N.
$$

于是，拉普拉斯金字塔由以下内容组成。

$$
\{L_0, L_1, \ldots, L_{N-1}, L_N\}.
$$

前面的 $L_i$ 是各个尺度的细节残差，最后的 $L_N$ 是最粗的低频底座。

### 1.4 拉普拉斯层重建原图

重建时从最粗层开始，先把最粗层看作已经恢复的结果。

$$
\hat G_N = L_N.
$$

然后逐层上采样，并加回对应的拉普拉斯残差。

$$
\hat G_i = L_i + \operatorname{Expand}(\hat G_{i+1}),
\qquad i=N-1,\ldots,0.
$$

为了看清楚这个过程，可以假设只有三层 $L_0$、$L_1$ 和 $L_2$。重建顺序如下。

$$
\hat G_2 = L_2,
$$

$$
\hat G_1 = L_1 + \operatorname{Expand}(\hat G_2),
$$

$$
\hat G_0 = L_0 + \operatorname{Expand}(\hat G_1).
$$

因为 $L_1$ 和 $L_0$ 正好保存了每次缩小时丢掉的残差，所以最终有

$$
\hat G_0 = G_0 = I.
$$

这就是“分解以后还能还原”的具体含义。高斯金字塔负责提供粗略预测，拉普拉斯层负责补回预测与真实图像之间的差异。只要分解和重建使用相同的滤波器、边界处理、上采样规则和尺寸约定，重建就可以在数值精度范围内恢复原图。

因此，拉普拉斯金字塔提供了一种可重建的图像表示，各层既可以用于观察，也可以参与原图恢复。

$$
I \longrightarrow \{L_0,L_1,\ldots,L_N\}
\longrightarrow \hat I.
$$

在中间不修改任何 $L_i$ 时，$\hat I$ 与 $I$ 一致；在中间修改某一层或多层时，重建结果就会产生对应尺度的变化。

---

## 2. 这样分解的意义

拉普拉斯分解的价值在于，它把原图中混合的不同尺度信息变成了可以分别处理、之后又能重新合成的成分。这样做的必要性来自图像本身的多尺度结构。

### 2.1 一张图像里同时存在很多尺度

一张自然图像同时包含不同空间范围的变化。

- 像素附近的快速变化，表现为细纹理、噪声和锐利边缘；
- 稍大范围的变化，表现为物体轮廓、局部结构和纹理块；
- 更大范围的缓慢变化，表现为光照、阴影、颜色和整体形状。

这些内容在原图的每个像素中混合在一起。直接修改像素，通常很难只影响其中一种尺度。例如，想让两幅图的亮度缓慢过渡，需要较宽的空间过渡；但同一个宽过渡如果直接作用到边缘，就会把边缘也一起平均掉。

### 2.2 金字塔提供按尺度处理的位置

拉普拉斯金字塔把一张图像改写成多个尺度成分。

- 细层主要承载细纹理和锐利边缘；
- 中间层承载中等尺度的局部结构；
- 粗层承载低频亮度、颜色和大范围形状。

于是，处理可以从“改所有像素”变成“改某一个尺度的成分”。

- 减小细层，可以抑制细小噪声；
- 放大细层，可以增强边缘和纹理；
- 调整粗层，可以改变大范围亮度或颜色过渡；
- 对不同图像的同一层分别加权，可以让不同尺度采用不同的信息来源。

关键在于，这些操作之后仍然可以通过同一个重建过程回到像素空间。分解为图像处理提供了一个可以编辑、也可以恢复的中间表示。

### 2.3 分解所解决的问题

对单张图像来说，拉普拉斯分解解决了**不同尺度信息难以分开处理**的问题，同时保留了重建原图所需的残差。

对图像融合来说，它进一步缓和了**细节保持和大范围平滑之间的冲突**。细层可以在较窄范围内切换，粗层可以在较宽范围内过渡，最后再通过重建把它们合成为一幅图像。

多频段融合就是把这个可重建的表示同时应用到多张图像上。权值和融合公式因此都有明确的作用位置。

---

## 3. 尺度与频率的关系

尺度描述变化所覆盖的空间范围，频率描述变化的快慢。细纹理和锐利边缘属于高频，大范围亮度和颜色变化属于低频。拉普拉斯层正是通过相邻尺度之间的差分，把这些变化组织成具有频率意义的多尺度成分。

### 3.1 空间域模糊对应频率域低通

图像模糊可以写成卷积。

$$
B = h * I,
$$

其中 $h$ 是低通滤波核。根据卷积定理，空间域中的卷积对应频率域中的乘法。

$$
\widehat{B}(\omega) = \widehat{h}(\omega)\,\widehat{I}(\omega).
$$

低通滤波器保留低频、衰减高频，所以模糊图像主要保留大尺度变化。原图与模糊图之差为

$$
D = I - h * I.
$$

在频率域中可以写成

$$
\widehat{D}(\omega) = \left(1 - \widehat{h}(\omega)\right)\widehat{I}(\omega).
$$

当 $\widehat{h}(\omega)$ 是低通响应时，$1-\widehat{h}(\omega)$ 就会强调较高的频率。因此，图像减去低通版本，会留下边缘、纹理和局部快速变化。

### 3.2 拉普拉斯层近似多尺度频段

拉普拉斯层是两个相邻低通尺度之差。

$$
L_i = G_i - \operatorname{Expand}(G_{i+1}).
$$

忽略下采样、上采样和边界处理的细节，可以把它抽象为一个尺度相关的滤波响应。

$$
\widehat{L_i}(\omega) \approx H_i(\omega)\widehat{I}(\omega).
$$

其中 $H_i(\omega)$ 在某个频率范围内响应较强。细层对应较高的空间频率，中间层对应中等频率，最粗层承担剩余的低频信息。

文中的“频段”并不表示每层都对应一个严格切开的、互不重叠的傅里叶区间。更准确的说法是，拉普拉斯金字塔通过空间域的低通、降采样、上采样和差分，构造了一组具有频率意义的多尺度子带。

### 3.3 频率域操作的可能性

有了可重建的多尺度表示，图像处理就可以按频率范围组织。

- 衰减细层，抑制细小噪声；
- 放大细层，增强边缘和纹理；
- 调整粗层，改变低频亮度和颜色过渡；
- 对两张图的同一层分别加权，完成多频段融合。

这里的“在频率域操作”不一定要求显式执行 FFT。拉普拉斯金字塔是在空间域实现的多尺度频率分解；每一层同时保留频率范围和空间位置，因此可以用于接缝、局部区域和权值图的处理。

---

## 4. 可重建分解用于多频段融合

在两幅已经配准的图像上应用这套表示，可以在对应尺度上决定使用哪张图像的信息。

### 4.1 直接混合容易造成模糊

假设有两张已经配准的图像 $A$ 和 $B$，以及一张权值图 $W$。普通的 alpha blending 可以写成

$$
F = W A + (1-W)B.
$$

这张权值图同时作用于所有尺度。为了让大范围亮度变化平滑，$W$ 往往需要有较宽的过渡；但这个宽过渡也会作用到高频边缘和纹理，于是边缘被平均，细节变软。

如果把过渡带做窄，高频细节可以保留，但低频亮度会在接缝处突然变化。直接混合很难同时满足这两个要求，因为它没有把不同尺度分开。

### 4.2 在对应频段上分别混合

对两张图分别构建拉普拉斯金字塔。

$$
\{L_i^A\}, \qquad \{L_i^B\}.
$$

对权值图构建高斯金字塔。

$$
\{W_i\}.
$$

然后在每个尺度上融合。

$$
F_i = W_i L_i^A + (1-W_i)L_i^B.
$$

最后把所有 $F_i$ 当作一组新的拉普拉斯层，从最粗层开始重建，得到输出图像 $F$。

这一步的关键在于，同一张原始权值经过高斯金字塔后，在不同尺度上具有不同的空间过渡范围。

- 细层的 $W_i$ 变化较快，可以在接缝附近较窄地切换，保留边缘和纹理；
- 粗层的 $W_i$ 已经被多次平滑，变化范围更宽，可以缓和低频亮度差；
- 重建把各个尺度的结果重新合成为一幅完整图像。

多张图像时，可以写成归一化加权。

$$
F_i = \frac{\sum_k W_i^k L_i^k}{\sum_k W_i^k + \epsilon}.
$$

其中 $\epsilon$ 用来避免权值和为零。实际系统仍然需要保证每个位置至少有一张图像提供有效内容。

![多频段融合的信息流](pyramid-blending-flow.svg)

---

## 5. 多频段融合的作用与边界

### 5.1 结构接缝是主要处理对象

多频段融合把接缝从一个“所有像素都使用同一种混合方式”的问题，变成了多个尺度上的混合问题。细层负责局部边缘和纹理，粗层负责更宽范围的亮度与结构过渡。这样可以缓和硬切换造成的明显接缝，同时避免把所有细节都用一个宽窗口平均掉。

换句话说，它解决的是**如何在保留细节的同时，让两张图在接缝附近平滑过渡**。

### 5.2 几何配准和颜色校正仍需单独处理

如果两张图没有对齐，同一个物体会在不同位置产生重复边缘。多频段融合可以让重复边缘变得柔和，却不能判断哪个位置才是物体的真实位置，也不能从根本上消除重影。

如果两张图存在明显曝光、白平衡或色彩响应差异，这些差异通常属于低频变化。多频段融合可以让颜色变化过渡得更平滑，却不能保证整幅图的颜色统计一致。

因此，一个完整的图像拼接流程通常包括以下步骤。

1. 先做几何配准；
2. 再做曝光补偿或颜色匀色；
3. 然后设计接缝和权值；
4. 最后进行多频段融合与重建。

多尺度表示和融合负责处理结构接缝。几何配准、颜色校正等环节属于独立问题，需要采用相应的处理方法。

---

## 6. 权值设计与尺度化

权值表达的是各个位置对不同图像的信任程度。对于两张图像 $A$ 和 $B$，二值权值可以表示一个明确的空间选择，软权值则允许两幅图像在一段区域内共同参与融合。

权值的平滑作用与视觉上的柔和过渡有关，但作用还包括尺度匹配和频率控制。拉普拉斯层承载的结构尺度不同，同一张硬边界权值直接作用于所有层，会让所有频率在同一个位置发生突变。

如果使用原始权值 $W$ 处理每一层，融合结果可以写成

$$
F_i = W L_i^A + (1-W)L_i^B.
$$

当 $W$ 是二值 mask 时，接缝处会出现跳变。这个跳变来自融合规则，与场景本身的结构无关。它会在每个拉普拉斯层中重复出现，带来两个问题。低频层中的亮度和颜色会在接缝处突然切换，形成可见的明暗边界；高频层中的边缘和纹理也会被硬切断，容易产生断裂或局部异常。

从频率角度看，空间域中的乘法对应频率域中的卷积。硬边界权值包含较强的高频成分，与拉普拉斯层相乘时，会把频谱能量扩散到原本不属于该层的频率范围。权值经过高斯低通后，边界中的高频成分受到抑制，融合过程引入的人工频率成分也会减少。

因此，权值平滑同时承担两个作用。它减弱接缝处的突变，也让权值的变化范围与当前拉普拉斯层的空间尺度相匹配。

对权值建立高斯金字塔

$$
W_0 = W,
$$

$$
W_{i+1} = \operatorname{Down}(\operatorname{Blur}(W_i)).
$$

细层中的 $W_i$ 保留较窄的过渡范围，高频边缘和纹理可以在接缝附近完成切换。随着层数增加，权值经过多次低通并进入更粗的采样网格，映射回原图后对应更宽的空间范围；粗层中的 $W_i$ 因此可以让低频亮度、颜色和大范围结构逐渐过渡。

这种尺度相关的过渡带解决了一个基本冲突。高频成分需要局部切换来保持清晰，低频成分需要较宽过渡来隐藏亮度和颜色差异。高斯权值金字塔把两种过渡范围分配到不同层中，重建时再将它们合成为一幅图像。

权值构造包含三个阶段。

第一步是生成有效区域。图像经过投影或配准后，落在画布上的有效像素记为 1，无效区域记为 0。

第二步是选择接缝或主导区域。最简单的情况使用二值 mask，左侧使用图像 $A$，右侧使用图像 $B$。更实际的做法会根据距离边界的远近、视角夹角、清晰度、曝光或局部纹理，选择更适合成为主导图像的区域。

第三步是把权值归一化。两张图时可以直接使用 $W$ 和 $1-W$；多张图时先计算

$$
\tilde W^k = \frac{W^k}{\sum_j W^j + \epsilon}.
$$

随后对 $\tilde W^k$ 构建高斯金字塔。权值表示混合比例，需要随尺度逐渐变平滑，因此只保留低通后的权值，不保存类似拉普拉斯层的差分残差。

权值需要满足以下条件。

- 权值应当非负，多图权值通常需要归一化；
- 接缝尽量避开明显运动物体、人脸、文字和强边缘；
- 原始 mask 的过渡带不必过宽，粗尺度会自然扩大过渡范围；
- 层数越多，最低频的融合范围越大，但过多层数会把大范围色差扩散到更远区域；
- 对齐误差较大时，不能依靠权值和金字塔完全补救，应先改善配准或调整接缝位置。

---

## 7. 金字塔层数的选择

层数决定了最粗频段的空间范围。每下采样一层，像素尺度大约扩大 2 倍。如果希望最低频在几十到几百像素范围内完成平滑过渡，下面的关系可以作为初始估计。

$$
2^N \approx \text{希望低频平滑覆盖的像素宽度}.
$$

例如，希望低频过渡覆盖约 64 像素，可以从 $N=6$ 附近开始尝试。这个关系不是严格公式，因为滤波核、图像尺寸、mask 形状和重建实现都会影响实际过渡范围。

层数选择可以参考以下经验。

- 小图或局部贴图使用较少层数，避免最粗层过小；
- 全景拼接、纹理拼接可以先尝试 5 层，再根据接缝宽度调整；
- 对齐误差明显时，增加层数只能让重影更柔，不会消除重影；
- 曝光差明显时，先做匀色，再调整金字塔层数。

---

## 8. OpenCV 实现

完整数据流由拉普拉斯分解、逐层加权和重建组成。拉普拉斯金字塔提供可重建的尺度成分，逐层加权得到融合频段，重建过程将结果恢复到原图尺寸。

下面的示例接收两张已经对齐、尺寸相同或接近的图像，以及一张 mask。mask 使用 255 表示左图，使用 0 表示右图，中间灰度表示软权值。

实现包含三个关键步骤。

1. 构建两张图像的 Laplacian Pyramid；
2. 构建 mask 的 Gaussian Pyramid，并在每个频段上加权；
3. 对融合后的频段执行拉普拉斯重建。

颜色匹配选项只是一个轻量的低频匀色示例，实际应用还需结合重叠区域、曝光模型和全局补偿策略。

编译方式如下。

```bash
g++ -std=c++17 multiband_blending_demo.cpp -o multiband_blending_demo `pkg-config --cflags --libs opencv4`
```

运行方式如下。

```bash
./multiband_blending_demo left.png right.png mask.png blended.png 6 1
```

最后一个参数为 1 时，会启用均值方差颜色匹配；传入 0 则只执行多频段融合。

配套源代码位于 [`multiband_blending_demo.cpp`](multiband_blending_demo.cpp)。完整的输入图像、mask、示例输出和编译说明可以通过 [下载多频段融合 demo 数据与代码（ZIP）](./multiband_blending_demo.zip) 获取。

```cpp
#include <opencv2/opencv.hpp>

#include <algorithm>
#include <iostream>
#include <stdexcept>
#include <string>
#include <vector>

namespace {

cv::Mat ReadColor32F(const std::string& path) {
  cv::Mat image_u8 = cv::imread(path, cv::IMREAD_COLOR);
  if (image_u8.empty()) {
    throw std::runtime_error("failed to read image: " + path);
  }
  cv::Mat image_f;
  image_u8.convertTo(image_f, CV_32FC3, 1.0 / 255.0);
  return image_f;
}

cv::Mat ReadWeight32F(const std::string& path, const cv::Size& size) {
  cv::Mat mask_u8 = cv::imread(path, cv::IMREAD_GRAYSCALE);
  if (mask_u8.empty()) {
    throw std::runtime_error("failed to read mask: " + path);
  }
  if (mask_u8.size() != size) {
    cv::resize(mask_u8, mask_u8, size, 0.0, 0.0, cv::INTER_LINEAR);
  }
  cv::Mat mask_f;
  mask_u8.convertTo(mask_f, CV_32FC1, 1.0 / 255.0);
  cv::max(mask_f, 0.0, mask_f);
  cv::min(mask_f, 1.0, mask_f);
  return mask_f;
}

cv::Mat To3Channels(const cv::Mat& gray) {
  std::vector<cv::Mat> channels(3, gray);
  cv::Mat color;
  cv::merge(channels, color);
  return color;
}

int MaxPyramidLevels(cv::Size size) {
  int levels = 1;
  while (size.width > 1 && size.height > 1) {
    size.width = (size.width + 1) / 2;
    size.height = (size.height + 1) / 2;
    ++levels;
  }
  return levels;
}

std::vector<cv::Mat> BuildGaussianPyramid(const cv::Mat& image, int levels) {
  std::vector<cv::Mat> pyramid;
  pyramid.reserve(levels);
  pyramid.push_back(image.clone());
  for (int i = 1; i < levels; ++i) {
    cv::Mat down;
    cv::pyrDown(pyramid.back(), down);
    pyramid.push_back(down);
  }
  return pyramid;
}

std::vector<cv::Mat> BuildLaplacianPyramid(const cv::Mat& image, int levels) {
  std::vector<cv::Mat> gaussian = BuildGaussianPyramid(image, levels);
  std::vector<cv::Mat> laplacian(levels);

  for (int i = 0; i + 1 < levels; ++i) {
    cv::Mat up;
    cv::pyrUp(gaussian[i + 1], up, gaussian[i].size());
    laplacian[i] = gaussian[i] - up;
  }
  laplacian.back() = gaussian.back();
  return laplacian;
}

cv::Mat ReconstructFromLaplacianPyramid(const std::vector<cv::Mat>& pyramid) {
  cv::Mat current = pyramid.back().clone();
  for (int i = static_cast<int>(pyramid.size()) - 2; i >= 0; --i) {
    cv::Mat up;
    cv::pyrUp(current, up, pyramid[i].size());
    current = up + pyramid[i];
  }
  return current;
}

cv::Mat MatchMeanStdNearSeam(const cv::Mat& source,
                             const cv::Mat& reference,
                             const cv::Mat& soft_mask) {
  // Optional low-frequency harmonization. The best mask is the real overlap or
  // seam transition band. If the input mask is binary and no transition exists,
  // the demo falls back to global mean/std matching.
  cv::Mat seam_mask;
  cv::inRange(soft_mask, cv::Scalar(0.05), cv::Scalar(0.95), seam_mask);
  const bool has_enough_seam_pixels = cv::countNonZero(seam_mask) > 100;

  cv::Scalar src_mean, src_std, ref_mean, ref_std;
  if (has_enough_seam_pixels) {
    cv::meanStdDev(source, src_mean, src_std, seam_mask);
    cv::meanStdDev(reference, ref_mean, ref_std, seam_mask);
  } else {
    cv::meanStdDev(source, src_mean, src_std);
    cv::meanStdDev(reference, ref_mean, ref_std);
  }

  std::vector<cv::Mat> channels;
  cv::split(source, channels);
  for (int c = 0; c < 3; ++c) {
    const double scale = (src_std[c] > 1e-6) ? ref_std[c] / src_std[c] : 1.0;
    channels[c] = (channels[c] - src_mean[c]) * scale + ref_mean[c];
  }

  cv::Mat matched;
  cv::merge(channels, matched);
  cv::max(matched, 0.0, matched);
  cv::min(matched, 1.0, matched);
  return matched;
}

cv::Mat MultiBandBlend(const cv::Mat& image_a,
                       const cv::Mat& image_b,
                       const cv::Mat& weight_a,
                       int levels) {
  if (image_a.size() != image_b.size() || image_a.size() != weight_a.size()) {
    throw std::runtime_error("image and mask sizes must match");
  }
  if (image_a.type() != CV_32FC3 || image_b.type() != CV_32FC3 ||
      weight_a.type() != CV_32FC1) {
    throw std::runtime_error("expected CV_32FC3 images and CV_32FC1 mask");
  }

  levels = std::clamp(levels, 2, MaxPyramidLevels(image_a.size()));

  std::vector<cv::Mat> lap_a = BuildLaplacianPyramid(image_a, levels);
  std::vector<cv::Mat> lap_b = BuildLaplacianPyramid(image_b, levels);
  std::vector<cv::Mat> weight_pyr = BuildGaussianPyramid(weight_a, levels);

  std::vector<cv::Mat> blended_pyr(levels);
  for (int i = 0; i < levels; ++i) {
    cv::Mat w3 = To3Channels(weight_pyr[i]);
    cv::Mat one(w3.size(), w3.type(), cv::Scalar::all(1.0));
    blended_pyr[i] = lap_a[i].mul(w3) + lap_b[i].mul(one - w3);
  }

  return ReconstructFromLaplacianPyramid(blended_pyr);
}

}  // namespace

int main(int argc, char** argv) {
  if (argc < 5) {
    std::cerr << "usage: " << argv[0]
              << " left.png right.png mask.png output.png [levels=6] [match_color=0]\n"
              << "mask uses 255 for the left image and 0 for the right image.\n";
    return 1;
  }

  try {
    const std::string left_path = argv[1];
    const std::string right_path = argv[2];
    const std::string mask_path = argv[3];
    const std::string output_path = argv[4];
    const int requested_levels = argc > 5 ? std::max(2, std::stoi(argv[5])) : 6;
    const bool match_color = argc > 6 ? std::stoi(argv[6]) != 0 : false;

    cv::Mat left = ReadColor32F(left_path);
    cv::Mat right = ReadColor32F(right_path);
    if (left.size() != right.size()) {
      cv::resize(right, right, left.size(), 0.0, 0.0, cv::INTER_LINEAR);
    }
    cv::Mat weight_left = ReadWeight32F(mask_path, left.size());

    if (match_color) {
      right = MatchMeanStdNearSeam(right, left, weight_left);
    }

    cv::Mat blended = MultiBandBlend(left, right, weight_left, requested_levels);
    cv::max(blended, 0.0, blended);
    cv::min(blended, 1.0, blended);

    cv::Mat blended_u8;
    blended.convertTo(blended_u8, CV_8UC3, 255.0);
    if (!cv::imwrite(output_path, blended_u8)) {
      throw std::runtime_error("failed to write output: " + output_path);
    }
    std::cout << "wrote " << output_path << "\n";
  } catch (const std::exception& e) {
    std::cerr << "error: " << e.what() << "\n";
    return 2;
  }
  return 0;
}
```

---

## 9. 小结

这套方法可以概括为**先分解，后操作，再重建**。

一张图像先通过高斯金字塔得到逐层变粗的低频表示，再用相邻尺度之间的残差构成拉普拉斯金字塔。高斯层提供粗略预测，拉普拉斯层保存预测没有解释掉的细节；从最粗层开始逐层上采样相加，就能回到原图。

这套表示解决了一个基础问题。图像中的细纹理、局部结构和大范围亮度不必再混在同一组像素操作里，它们可以在不同频段被分别处理，之后仍然通过重建回到像素空间。

多频段融合只是这个思想在两张图像上的直接应用。对两张图的对应拉普拉斯层分别加权，再把融合后的各层重建回来。细层保留边缘和纹理，粗层负责较宽范围的过渡，权值金字塔让不同频段使用不同的空间过渡尺度。

这套方法的处理框架可以写成下面的形式。

$$
\text{图像} \longrightarrow \text{多尺度频段} \longrightarrow \text{频段操作} \longrightarrow \text{重建图像}.
$$

多频段融合擅长处理结构接缝，但不能替代几何配准，也不能单独解决大范围曝光和颜色不一致。理解这一点以后，权值设计、颜色匀色和层数选择就都有了清楚的位置。

## 参考

- Peter J. Burt and Edward H. Adelson, “A Multiresolution Spline with Application to Image Mosaics”, ACM Transactions on Graphics, 1983.
- Peter J. Burt and Edward H. Adelson, “The Laplacian Pyramid as a Compact Image Code”, IEEE Transactions on Communications, 1983.
- Richard Szeliski, “Computer Vision: Algorithms and Applications”, 2nd edition, 2022.
