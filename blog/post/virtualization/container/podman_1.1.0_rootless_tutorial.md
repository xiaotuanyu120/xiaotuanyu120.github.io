---
title: podman: 1.1.0 rootless
date: 2021-01-30 15:43:00
categories: virtualization/container
tags: [podman,rootless,container]
---
### podman: 1.1.0 rootless

### 1. [启用cgroup v2](/linux/advance/kernel_1.1.4_cgroup.html)

### 2. 系统环境准备
``` bash
# 关闭selinux
sed -i "s/^SELINUX=.*/SELINUX=disabled/g" /etc/selinux/config

# 创建用户
useradd -d /data/container container

# USER NAMESPACE最大数优化
echo "user.max_user_namespaces=28633" > /etc/sysctl.d/userns.conf
sysctl -p /etc/sysctl.d/userns.conf

# check uid and gid map setting of user namespace
cat /etc/subuid
cat /etc/subgid
# 正常应该是有username uid mapuidstart maprange
```

### 3. 安装podman
``` bash
# install podman
dnf -y install podman buildah crun fuse3
```
> 安装fuse3后，记得[启用此内核模块](/linux/advance/kernel_1.1.5_enable_module.html)


### 4. ROOTLESS 配置文件
- image storage: $HOME/.local/share/containers/storage
- rootless配置文件：
  - $HOME/.config/containers/containers.conf
  - $HOME/.config/containers/storage.conf
  - $HOME/.config/containers/registries.conf

``` bash
# ROOTLESS CONFIGURE
mkdir -p /data/container/.config/containers
cp /usr/share/containers/containers.conf /data/container/.config/containers/containers.conf
chown -R container.container /data/container/.config/containers
# 修改ociruntime为crun来支持cgroup v2："runtime = "crun"
# 确保cgroup用的是systemd
```

### 4. 运行rootless容器
``` bash
podman run -it -d -p 80:80 nginx:latest
```
> [Error: writing file `/sys/fs/cgroup/user.slice/user-1001.slice/user@1001.service/cgroup.subtree_control`: No such file or directory: OCI runtime command not found error](https://github.com/containers/podman/issues/7768)
```
echo "+pids +memory" >/sys/fs/cgroup/user.slice/cgroup.subtree_control
echo "+pids +memory" >/sys/fs/cgroup/user.slice/user-1001.slice/cgroup.subtree_control
```

### 5. 检查rootless状态
```
podman unshare cat /proc/self/uid_map
```