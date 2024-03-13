---
title: "全景图消影点估计"
collection: projects
type: "计算机视觉，多视图几何"
permalink: /portfolio/pano_vanishing_points
venue: "计算机视觉，多视图几何，单视图几何，射影几何"
date: 2020-03-20
location: "背景, 中国"
---

![](/portfolio/pano_vanishing_points/1.png)

## 主要原理

透视投影的一个显著特征是延伸至无穷远的物体的图像可能出现在有限范围内。例如无穷远线在图像上投影，终止在一个消影点上。例如下图平行的铁道消失于图像中的某个点上。我们可以利用这个特性，如果某个点是多条线段的共同虚交点，那么其极有可能是消影点，因为真实空间平行线非常多，尤其是在城市环境。

![](/portfolio/pano_vanishing_points/0.png)

对于全景图来说，因为其可见范围很广（720度），用来估计消影点非常适合，尤其是基于曼哈顿假设的情况下，可以很稳定求的消影点，从而估计全景图的三个方向。

## 具体方法

![](/portfolio/pano_vanishing_points/5.png)


![](/portfolio/pano_vanishing_points/7.png)

建立球面索引，从而加速搜索可能的消影点
![](/portfolio/pano_vanishing_points/6.png)

### 最终效果：  

红色、绿色、蓝色分别为三个曼哈顿方向。对应的消影点用小圈圈绘出。

![](/portfolio/pano_vanishing_points/2.png)
![](/portfolio/pano_vanishing_points/3.png)
![](/portfolio/pano_vanishing_points/4.png)