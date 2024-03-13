---
title: "室内结构化重建"
collection: projects
type: "计算机图形学，计算机视觉"
permalink: /portfolio/structure_recon_indoor
venue: "三维重建，结构化重建，室内"
date: 2022-07-07
location: "西安, 中国"
---

![](/portfolio/structure_recon_indoor/1.png)

<font size=2>图1 结构化重建结果</font>

- 室内场景结构化重建一是为了美观度的问题，结构化场景看起来更干净，用户浏览体验更好。另一方面是为了达到家具替换等需求，需要把房间墙面等结构信息提取出来。本算法求解速度快，鲁棒性好，可以适应不同的场景。


![](/portfolio/structure_recon_indoor/2.png)
<font size=2>图2 左边图像是平面分割的结果，不同的平面赋予不同的颜色，右边是结构化的mesh结构</font>


*   上图展示了一个复杂的居住场景，其杂物非常多。经过结构化后非常干净，规整。
    在算法的处理过程中，为了增加鲁棒性，提出了根据几何结构快速分间算法，从而利用分间信息降低结构化重建的复杂度

![](/portfolio/structure_recon_indoor/3.png)
<font size=2>图3 快速分间算法，左边第一张图为初始种子生成，左边第二到第四张图为使用Delaunay算法优化分间结果</font>

*   为了进一步增加算法的鲁棒性，门的识别。根据分间之间的连接为门这一思想，解析门的位置。将门的结构参与到结构化重建中。如图4，展示了门的识别位置和结构化重建的结果。

![](/portfolio/structure_recon_indoor/4.png)
<font size=2>图4 基于语法解析的门的识别以及重建结果</font>