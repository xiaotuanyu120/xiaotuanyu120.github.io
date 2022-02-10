---
title: kubernetes 2.1.0 CRI containerd installation
date: 2021-06-17 11:17:00
categories: virtualization/container
tags: [container,containerd,kubernetes]
---

### 1. 准备步骤
``` bash
cat <<EOF | sudo tee /etc/modules-load.d/containerd.conf
overlay
br_netfilter
EOF

sudo modprobe overlay
sudo modprobe br_netfilter

# Setup required sysctl params, these persist across reboots.
cat <<EOF | sudo tee /etc/sysctl.d/99-kubernetes-cri.conf
net.bridge.bridge-nf-call-iptables  = 1
net.ipv4.ip_forward                 = 1
net.bridge.bridge-nf-call-ip6tables = 1
EOF

# Apply sysctl params without reboot
sudo sysctl --system
```

### 2. 安装containerd 和 配置
**从docker官方repo中安装containerd**
``` bash
yum install -y yum-utils
yum-config-manager \
    --add-repo \
    https://download.docker.com/linux/centos/docker-ce.repo
yum install -y containerd.io
```

**创建默认containerd的配置**
``` bash
mkdir -p /etc/containerd
containerd config default > /etc/containerd/config.toml
```

**启动containerd**
``` bash
systemctl start containerd
systemctl enable containerd
```

### 3. 将cgroup driver从cgroupfs切换为systemd
k8s推荐统一使用systemd来管理cgroup，这样不至于同一个系统两个driver造成混乱
``` bash
sed -i '/SystemdCgroup = true/d' /etc/containerd/config.toml
sed -i '/containerd.runtimes.runc.options/a\ \ \ \ SystemdCgroup = true' /etc/containerd/config.toml

systemctl restart containerd
```
> 和docker不同，这里不用关注storage driver(graph driver)，moby项目组已经使用snapshotter来替换原来在docker中的graph driver了。详情请看moby项目的博客: [containerd中的graph drivers在哪里？](https://blog.mobyproject.org/where-are-containerds-graph-drivers-145fc9b7255)。 里面作者的定论为
> ```
> In the end, snapshotters are an evolution of graph drivers. We set out to fix the long standing issues with graph drivers that users were facing and fix them in a way that we can support for years to come.
> ```