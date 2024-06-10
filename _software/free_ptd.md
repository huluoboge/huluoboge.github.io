---
title: "Free PTD"
collection: software
permalink: /software/free_ptd
excerpt: 'Free PTD 是一个免费的机载激光雷达（Lidar)滤波软件，其使用渐进三角网加密算法对点云进行分类，得到地面点和非地面点'
date: 2019-06-03
---

# Free software of Progressive TIN Densification for filtering airborne LiDAR data ----Free PTD  

## 机载LIDAR点云滤波算法之-渐进三角网加密算法免费软件 Free PTD


Free PTD 是一个免费的机载激光雷达（Lidar)滤波软件,使用了自适应版本的渐进三角网加密算法（Progressive TIN Densification）进行点云的滤波。主要原理是通过迭代来计算自适应参数从而适应不同的地形，尤其是在陡峭的山区。为了适应更大的场景，FreePTD内部对点云进行分块处理并把结果合并。

Free PTD 使用简单的命令行操作来提供处理的参数。使用方式可参见<a href="#1">参数设置</a>

Free PTD 

可以使用以下命令来处理一个las点云的滤波
```sh
FreePTD -i input_las.las -o output_las.las -d 1 -a 6 -m 60 -c -s

```

其中 input_las.las为需要处理的las格式的点云文件；
output_las.las 为处理后的结果文件；其他为参数；
因采用命令行方式，可方便的使用批处理。

Free PTD采用CPU并行方式来进行加速，这可能会引起计算机CPU满负荷工作。
如果点云数量较大，可能需要更多的内存


>注意：
Free PTD 不会对点云数据进行外点去除，因为极低点外点会影响滤波结果，所以请确定输入的点云
没有极低点。  
>Free PTD目前版本只提供Windows x64 版本，有其他需求可以email<a href="mailto:3000huyang@163.com">3000huyang@163.com</a>

****
<a name="1"> 参数设置</a>

- -i 输入需要滤波的las文件，支持1.0-1.3
- -o 输出滤波后的las，输入的las数据被分成两类，未分类和地面，在isprs las格式中分类，地面点为2。具体参见LAS格式标准
- -d 点到三角形的距离阈值，默认值1.0  
- -a 点和三角形端点的连线与三角形所在平面最大角阈值，默认值6
- -m 最大建筑物大小，默认值60. 此参数设置过小，建筑物的平顶可能被误认为地形，建筑物屋顶点会被误分为地面点。参数设置过大，会导致初始种子点过少，不利于地面点分类效率及地形起伏剧烈区域分地面点。
- -c 分类标志，如果设置，那么Free PTD会尽量获得地面点。否则Free PTD只会找到一些关键的地形点，这通常地面点数量会比较少，建议开启，但会增加内存使用量
- -s 自适应标志，如果设置，那么Free PTD会采用自适应的算法来适应地形起伏，尤其是山区，建议开启


如果在使用的过程中，发现有任何问题，可及时email <a href="mailto:3000huyang@163.com">3000huyang@163.com</a>

- 下载地址：[百度网盘](https://pan.baidu.com/s/1CZanRgTymTotYv369ycPvQ ) 提取码: giin 

- 参考文献
> (1) Zhao, X.; Guo, Q.; Su, Y.; Xue, B. Improved Progressive TIN Densification Filtering Algorithm for Airborne LiDAR Data in Forested Areas. ISPRS Journal of Photogrammetry and Remote Sensing 2016, 117, 79–91. https://doi.org/10.1016/j.isprsjprs.2016.03.016.



