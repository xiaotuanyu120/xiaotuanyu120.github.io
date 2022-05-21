---
title: linux内核: 模块 - 启用模块
date: 2021-01-30 15:46:00
categories: linux/advance
tags: [linux,kernel,modprobe]
---

### 1. 启用模块fuse
``` bash
# 手动启用模块
modprobe fuse

# 持久化启用模块
echo "fuse" > /etc/modules-load.d/fuse.conf
systemctl enable systemd-modules-load.service

# 查看模块启用情况
lsmod | grep fuse
```