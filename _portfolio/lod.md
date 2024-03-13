---
title: "大场景LOD模型生成"
collection: projects
type: "摄影测量，计算机图形学"
permalink: /portfolio/lod
venue: "LOD"
date: 2024-03-01
location: "北京, 中国"
---
![](/portfolio/lod/1.png)


大场景三维重建需要解决两方面主要问题，一是数据量大，需要突破计算资源本身的限制条件，比如说内存的限制。二是能够流畅的渲染可视化。

重建这一部分整体需要能够分治。处理流程包括点云分块、点云网格重建，网格拓扑缝合，网格简化，纹理映射，纹理匀色，LOD生成等。目前来说在倾斜摄影测量领域。常用的方案并没有缝合网格的拓扑结构，比如Context Capture建立的LOD模型。在倾斜摄影或者室外空间三维重建过程中，视点相对于室内空间来说比较远，模型是‘一层皮’，网格通过一定Buffer重叠是可以掩盖网格拓扑没有缝合带来的裂缝问题的。但是对于室内空间来说，观察距离比较近，室内空间通常结构更加复杂，网格拓扑必须缝合。同时，对于室内空间的加载来说，其局部网格密度更大，对于浏览来说压力更大。另外在一些场景中，首次加载时长和渲染速度对于用户体验来说非常重要。综上，需要对于网格处理，带纹理的网格简化有更高的要求。

本项目创新提出平面引导的网格合并技术，同时解决了带纹理的网格简化的技术难题。

下面是一些场景重建的案例：

[https://www.realsee.com/website/customer/dataSpace](https://www.realsee.com/website/customer/dataSpace)

* 有些案例由于一些业务原因没有开LOD


下面是一些LOD的案例

[https://realsee.cn/VpvvVKbm](https://realsee.cn/VpvvVKbm)

[https://realsee.cn/vePPEkyl](https://realsee.cn/vePPEkyl)


<video src="/portfolio/lod/22.mp4" controls="controls" preload="auto" width="100%" height="100%"></video>



