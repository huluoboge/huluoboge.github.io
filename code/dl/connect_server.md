# 方法一：SSH反向隧道 + 正向隧道（最推荐）
利用目标服务器可以连接你本机的特性，建立反向隧道。

步骤：
1 在目标服务器上建立反向隧道到你的本机
2 在你的本机建立正向隧道完成连接

# 第一步：在目标服务器上执行（将目标服务器的8888端口反向隧道到你本机的8889端口）
```bash
ssh -R 8889:localhost:8888 你的本机用户名@你的本机IP -N -f
#-R: 反向隧道，-f: 后台运行
# 第二步：在你本机执行（将本地的某个端口转发到反向隧道端口）
ssh -L 9999:localhost:8889 你的本机用户名@localhost -N

```

# 方法二：使用 autossh 保持稳定的反向隧道（生产环境推荐）

```bash
# 安装 autossh（如果还没有）
sudo apt install autossh

# 建立稳定的反向隧道
autossh -M 0 -o "ServerAliveInterval 30" -o "ServerAliveCountMax 3" -N -R 8889:localhost:8888 你的本机用户名@你的本机IP -f

```

配置为系统服务（更稳定）：
创建文件 /etc/systemd/system/jupyter-tunnel.service：

```bash
[Unit]
Description=Jupyter Reverse SSH Tunnel
After=network.target

[Service]
User=你的用户名
ExecStart=/usr/bin/autossh -M 0 -o "ServerAliveInterval 30" -o "ServerAliveCountMax 3" -N -R 8889:localhost:8888 你的本机用户名@你的本机IP
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```
启用服务：
```bash
sudo systemctl daemon-reload
sudo systemctl enable jupyter-tunnel.service
sudo systemctl start jupyter-tunnel.service

```

https://yuanbao.tencent.com/chat/naQivTmsDa/d7b19ba2-2a8e-4f58-beb6-f18c3347f33e