

# LichtFeld-Studio安装记录




https://github.com/MrNeRF/LichtFeld-Studio


```
docker pull ubuntu:24.04
```

# 安装 GPU 支持的 Docker 运行时
如果没有安装docker container 对应的gpu支持，可以先按照以下步骤进行

- 添加 NVIDIA Container Toolkit 仓库
```
curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey | sudo gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg
curl -s -L https://nvidia.github.io/libnvidia-container/stable/deb/nvidia-container-toolkit.list |   sed 's#deb https://deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg] https://#g' |   sudo tee /etc/apt/sources.list.d/nvidia-container-toolkit.list

sudo apt update

```
- 安装运行时支持
```
sudo apt install -y nvidia-container-toolkit

```
- 配置 Docker 使用它
```
sudo nvidia-ctk runtime configure --runtime=docker
sudo systemctl restart docker
```

- 测试 GPU 是否可见
```
docker run --rm --gpus all nvidia/cuda:12.8.0-base-ubuntu24.04 nvidia-smi
```

## 运行docker

```
docker run -it --gpus all --name LichtFeld-build \
    -v $(pwd):/workspace \
    nvidia/cuda:12.8.0-develop-ubuntu24.04 /bin/bash
```

1️⃣ 进入容器后，更新系统并安装基础工具

```
apt update && apt upgrade -y
apt install -y build-essential gcc-14 g++-14 cmake ninja-build git wget unzip python3 python3-pip
```

2️⃣ 安装 vcpkg（依赖管理）

```
cd /workspace  # 你的挂载目录
git clone https://github.com/microsoft/vcpkg.git
cd vcpkg
./bootstrap-vcpkg.sh
```

3️⃣ 安装 LibTorch 2.7.0（CUDA 12.8 版本）

```
mkdir -p /opt/libtorch && cd /opt/libtorch
wget https://download.pytorch.org/libtorch/cu128/libtorch-cxx11-abi-shared-with-deps-2.7.0%2Bcu128.zip
unzip libtorch-cxx11-abi-shared-with-deps-2.7.0+cu128.zip
```

4️⃣ 克隆 LichtFeld Studio 并创建构建目录

```
cd /workspace
git clone https://github.com/MrNeRF/LichtFeld-Studio.git
cd LichtFeld-Studio
mkdir build && cd build
```

5️⃣ 编译 LichtFeld Studio

```
cmake .. -DCMAKE_C_COMPILER=gcc-14 -DCMAKE_CXX_COMPILER=g++-14 \
         -DCMAKE_PREFIX_PATH=/opt/libtorch \
         -DCMAKE_TOOLCHAIN_FILE=/workspace/vcpkg/scripts/buildsystems/vcpkg.cmake
make -j$(nproc)
```




