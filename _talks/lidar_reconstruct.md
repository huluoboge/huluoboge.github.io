---
title: "融合Lidar点云与影像的建筑物三维重建"
collection: projects
type: "摄影测量"
permalink: /talks/lidar_reconstruct
venue: "三维重建，矢量化重建"
date: 2012-06-01
location: "西安, 中国"
---
![](/talks/lidar_reconstruct/s6.png)


机载Lidar一个很重要的应用领域是数字城市，建筑物重建。建筑的矢量化结构重建，单体化重建有着广泛的需求。

整体框架设计如下

![](/talks/lidar_reconstruct/s3.png)


国际上比较流行的Lidar建模软件为TerraSolid，其中TerraModel模块提供了机载Lidar的结构化建模方案。 本方案与其完全不同。在实际作业过程中，尽管自动化算法完成度很高，但通常免不了修改和完善模型。考虑到这个特点，本方案采用构建屋顶平面结构拓扑约束，从而方便作业人员编辑模型。在编辑后自动化生成建筑物三维模型。


下图为全自动生成的三维模型

![](/talks/lidar_reconstruct/s5.png)


![](/talks/lidar_reconstruct/s7.png)


