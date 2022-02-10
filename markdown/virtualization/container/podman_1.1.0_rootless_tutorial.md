---
title: podman: 1.1.0 rootless
date: 2021-01-30 15:43:00
categories: virtualization/container
tags: [podman,rootless,container]
---

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

### 7. podman and systemd
podman虽然可以通过`podman generate systemd`来创建unit文件，但是这样创建出来的unit文件并不通用，它必须要求容器实现已经创建。

#### systemd unit file 模板
而很多人的要求可能是想要一个更加灵活和通用的systemd unit file。所以redhat的大神提供了一个下面的模板

```
[Unit]
Description=Podman in Systemd

[Service]
Restart=on-failure
ExecStartPre=/usr/bin/rm -f /%t/%n-pid /%t/%n-cid
ExecStart=/usr/bin/podman run --conmon-pidfile  /%t/%n-pid  --cidfile /%t/%n-cid -d busybox:latest top
ExecStop=/usr/bin/sh -c "/usr/bin/podman rm -f `cat /%t/%n-cid`"
KillMode=none
Type=forking
PIDFile=/%t/%n-pid

[Install]
WantedBy=multi-user.target
```

其中重点在于四个点
- `%t`，容器runtime的根目录`/run/user/$UserID`
- `%n`，service的名称（就是systemd unit file的文件名称）
- `--conmon-pidfile`，conmon进程的pid保存文件
- `--cidfile`，container的id保存文件
通过以上四个点，我们基本上就可以确定了这个容器的systemd unit file的信息，来保证了用固定一个模板，来在不同服务器上管理容器的灵活性
> [redhat - byValentin Rothberg: Running containers with Podman and shareable systemd services](https://www.redhat.com/sysadmin/podman-shareable-systemd-services)

#### 通过systemd管理rootless容器
``` bash
systemctl --user daemon-reload
systemctl --user start foo
systemctl --user restart foo

# 开机启动
systemctl --user enable foo
Created symlink /home/container/.config/systemd/user/multi-user.target.wants/foo.service → /home/container/.config/systemd/user/foo.service.
```