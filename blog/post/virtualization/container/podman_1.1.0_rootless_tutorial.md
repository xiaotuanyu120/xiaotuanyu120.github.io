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
# 保持selinux为enforcing状态

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
# 有些镜像，类似于redis，会使用非root用户运行，那么根据uid map的规则，我们需要修改宿主机映射文件的属主属组
podman unshare chown -R containeruid.containergid /path/to/dir/on/host/needed/mounted

podman run -it -d -p 80:80 -v /data/www/html:/var/www/html:Z nginx:latest
```
> `:Z`，含义是让selinux挂载本地目录的时候，重新lable一下，使其符合container环境的读写权限
> [user namespaces & selinux & rootless container](https://www.redhat.com/sysadmin/user-namespaces-selinux-rootless-containers)
> [What happens behind the scenes of a rootless Podman container?](https://www.redhat.com/sysadmin/behind-scenes-podman)

> [Error: writing file `/sys/fs/cgroup/user.slice/user-1001.slice/user@1001.service/cgroup.subtree_control`: No such file or directory: OCI runtime command not found error](https://github.com/containers/podman/issues/7768)
```
echo "+pids +memory" >/sys/fs/cgroup/user.slice/cgroup.subtree_control
echo "+pids +memory" >/sys/fs/cgroup/user.slice/user-1001.slice/cgroup.subtree_control
```

### 5. 检查rootless状态
```
podman unshare cat /proc/self/uid_map
```

### 6. rootless podman will not write iptables rules
rootless podman运行的容器，不会写iptables规则，这就是如此设计的，它会启动一个进程专门来监听容器map的port
``` bash
# 运行rootless podman nginx
podman run -it -d --rm --name nginx -p 80:80 nginx:latest

# 查看map的端口
podman port --all
02ede4d6178f    80/tcp -> 0.0.0.0:80

# 检查监听域名进程pid
netstat -lnpt
......
tcp6      0      0 :::80       :::*        LISTEN 2520/containers-roo

# 查看pid
ps aux |grep 2520 |grep -v grep 
contain+    2520  0.0  0.4 1975428 62760 ?       Sl    11:32   0:00 containers-rootlessport
```
> - [question: how to let rootless podman write iptables rule; answer: no](https://www.linode.com/community/questions/20801/rootless-container-in-podman-and-creating-a-private-container-registry-with-lino)
> - [podman issue 5141: its expected](https://github.com/containers/podman/issues/5141#issuecomment-584120613)
> - [podman issue 3981: rootless docker also dont write iptables rules](https://github.com/containers/podman/issues/3981#issuecomment-529950830)