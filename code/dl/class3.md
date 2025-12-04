
# CNN参数量

* **卷积层（Conv2d）参数量**（带偏置）：
    

$$\text{Params} = (k_h \times k_w \times C_{in} / G) \times C_{out} \;+\; C_{out}$$

其中 $k_h,k_w$ 是卷积核高度/宽度，$C_{in},C_{out}$ 是输入/输出通道数，$G$ 是 groups（普通卷积 $G=1$，深度卷积 $G=C_{in}$）。偏置项为 $C_{out}$，如果不使用 bias 则去掉最后一项。

* **全连接层（Linear）参数量**（带偏置）：
    

$$\text{Params} = N_{in} \times N_{out} \;+\; N_{out}$$

偏置项为 $N_{out}$。

* **池化（Pool）、激活（ReLU/LeakyReLU）、BatchNorm（不看学习参数除外）**：
    
    * MaxPool、ReLU 等 **无可学习参数**（参数量 = 0）。
        
    * BatchNorm2d 有可学习参数：$\gamma,\beta$ 各 $C$ 个（总 2C），还可能有 running stats（不计入参数量的可训练参数）。
        

# 输出尺寸（常用，帮助确定 FC 输入大小）

二维卷积输出高/宽：

$$H_{out} = \left\lfloor\frac{H_{in} + 2p - d(k-1) -1}{s} \right\rfloor + 1$$

（常见简化：对 kernel=k, padding=p, stride=s, dilation=1 时：$H_{out}=\lfloor (H_{in}+2p-k)/s\rfloor+1$）

# 深度可分离卷积（Separable）

* Depthwise params：$k_h\times k_w \times C_{in}$
    
* Pointwise params：$1\times1\times C_{in}\times C_{out}$  
    总和再加上偏置项（按需）。
    

* * *

# 用你的网络举例（逐层推导，逐位计算）

网络片段：

```py
self.conv1 = nn.Conv2d(3, 32, 3, padding=1)
self.pool = nn.MaxPool2d(2, 2)
self.conv2 = nn.Conv2d(32, 64, 3, padding=1)
self.fc1 = nn.Linear(64*8*8, 128)
self.fc2 = nn.Linear(128, 10)
self.relu = nn.ReLU()
```

假设输入是 CIFAR-10 的 $32\times32$ 图像（3 通道），两次 `MaxPool2d(2,2)` 后空间尺寸变为 $8\times8$，所以 `fc1` 的输入维度写成 `64*8*8` 是合理的。

逐层参数量：

1. **conv1**：kernel $3\times3$，$C_{in}=3$，$C_{out}=32$，groups=1
    
    $$\text{params} = 3\times3\times3\times32 + 32 = 864 + 32 = 896$$
2. **conv2**：kernel $3\times3$，$C_{in}=32$，$C_{out}=64$
    
    $$\text{params} = 3\times3\times32\times64 + 64 = 18432 + 64 = 18496$$
3. **fc1**：$N_{in}=64\times8\times8=4096$，$N_{out}=128$
    
    $$\text{params} = 4096\times128 + 128 = 524288 + 128 = 524416$$
4. **fc2**：$N_{in}=128$，$N_{out}=10$
    
    $$\text{params} = 128\times10 + 10 = 1280 + 10 = 1290$$
5. **pool, relu**：参数量 = 0
    

**总参数量**把上面加起来：

$$896 + 18496 + 524416 + 1290 = 545098$$

所以你的模型大约有 **545,098 个可学习参数**（包含偏置项）。

* * *

# 常用快速方法（实战建议）

1. **用公式直接算**：适合画图或手工估算（上面给的是最小集合）。
    
2. **PyTorch 程序化统计**（最简单最可靠）：
    

```python
sum(p.numel() for p in model.parameters())                     # 总参数
sum(p.numel() for p in model.parameters() if p.requires_grad)  # 可训练参数
```

将这段放到 Notebook 里就会得到精确数字，适合画图时动态计算不同设计的参数量。

3. **注意点**：
    
    * groups、depthwise、pointwise 会显著改变参数量；
        
    * bias=True/False 会略微改变总量；
        
    * BatchNorm 会额外带 2C（gamma,beta）参数；
        
    * 卷积核大小、通道数对参数量影响最大；空间尺寸 **不影响参数量**（只影响计算量 FLOPs 和 FC 输入大小）。
        

* * *

如果你愿意，我可以：

* 帮你 **画一张图** 表示每层参数量占比（条形图或饼图），或者
    
* 给出一个 **小函数**，输入一个 `nn.Module` 的结构（或者一个 layer list），输出每层的参数量与累计和，方便你在设计网络时即时可视化参数分布。
    

你想先看条形图占比，还是要直接把上面的统计函数放进 Notebook？