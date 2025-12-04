#!/bin/bash

# ========== 配置项 ==========
REMOTE_USER="recon"          # 远程用户名
REMOTE_HOST="10.33.207.203"          # 远程机器 IP
REMOTE_PORT=8888                 # 远程 Jupyter 端口
CONDA_ENV="py39"                  # 远程 Python 环境名称
# ============================

# 1️⃣ 建立 SSH 隧道 (本地8888转发到远程8888)
ssh -N -f -L ${REMOTE_PORT}:localhost:${REMOTE_PORT} ${REMOTE_USER}@${REMOTE_HOST}

echo "SSH 隧道已建立: 本地端口 ${REMOTE_PORT} -> 远程 ${REMOTE_HOST}:${REMOTE_PORT}"

# 2️⃣ 在远程启动 Jupyter Notebook
ssh ${REMOTE_USER}@${REMOTE_HOST} "
    source ~/.bashrc
    conda activate ${CONDA_ENV}
    jupyter notebook --no-browser --port=${REMOTE_PORT} --NotebookApp.token=''
" &

echo "远程 Jupyter Notebook 已启动（无需 token）"
echo "请在本地 VSCode 打开 .ipynb 文件，选择远程内核连接 http://localhost:${REMOTE_PORT}"
