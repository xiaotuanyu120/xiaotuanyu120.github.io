---
title: 1.1.0 安装(Centos7)
date: 2015-12-12 16:06:00
categories: virtualization/docker
tags: [docker]
---

[docker安装官方文档](https://docs.docker.com/engine/installation/linux/centos/)
### 0. 环境介绍

``` bash
# 开启内核的ip forward特性
echo "net.ipv4.ip_forward = 1" >> /etc/sysctl.conf
sysctl -p
```
> net.ipv4.ip_forward = 1的配置确保了可以通过映射docker容器端口到外网，否则我们无法通过外网ip访问容器

### 1. 删除老版本的docker
``` bash
# 如果曾经在redhat的源中安装过老版的docker，删除它
yum remove docker \
                  docker-client \
                  docker-client-latest \
                  docker-common \
                  docker-latest \
                  docker-latest-logrotate \
                  docker-logrotate \
                  docker-engine
```

### 2. yum安装docker
``` bash
id docker >/dev/null 2>&1 || useradd -r -s /sbin/nologin docker

# 创建docker的yum源
yum install -y yum-utils
yum-config-manager \
    --add-repo \
    https://download.docker.com/linux/centos/docker-ce.repo

yum install docker-ce docker-ce-cli containerd.io
```


**若希望安装指定版本**
``` bash
# 查看所有可用的版本
yum list docker-ce --showduplicates | sort -r

# 选择要安装的版本，已经安装docker
VERSION_STRING=19.03.5
yum install -y docker-ce-${VERSION_STRING} docker-ce-cli-${VERSION_STRING} containerd.io
```

**配置storage driver和cgroup driver**
```
# 满足overlay2(docker recommanded storage driver)的内核版本要求
# - linux 4.0或者以上内核版本
# - 或者，CENTOS或RHEL上的3.10.0-514或以上内核版本
# centos7.7默认的内核版本已经满足了需要
# 修改storage driver为overlay2

# 修改cgroup driver设定(只需要在kubeadm的控制节点上执行)
# 目前的主流linux发行版基本都使用systemd来作为系统的init程序，systemd此时会充当cgroup的管理器。
# 而docker默认的cgroup驱动是cgroupfs，我们可以不修改它，但是这样意味着我们会有两个不同的cgroup管理器
# 会在某些情况下检视和管理资源时发生疑惑，所以最好是改成统一的，都使用systemd。
# 修改docker的cgroup driver
[[ -d /etc/docker ]] || mkdir /etc/docker
cat > /etc/docker/daemon.json << EOF
{
  "exec-opts": ["native.cgroupdriver=systemd"],
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "100m"
  },
  "storage-driver": "overlay2",
  "storage-opts": [
    "overlay2.override_kernel_check=true"
  ]
}
EOF
```

> 如果安装的是`18.09`，需要额外执行以下步骤，来解决docker服务启动失败的问题
> 问题详情参照：https://github.com/docker/for-linux/issues/475
> ``` bash
> IS_1809=18.09.*
> [[ ${VERSION_STRING} =~ ${IS_1809} ]] && (
>   [[ ! -d /etc/systemd/system/containerd.service.d ]] && /usr/bin/mkdir /etc/systemd/system/containerd.service.d;
>   [[ ! -f /etc/systemd/system/containerd.service.d/override.conf ]] && echo -e '[Service]\nExecStartPre=' > /etc/systemd/system/containerd.service.d/override.conf;)
> ```

### 3. install docker-compose
``` bash
curl -L "https://github.com/docker/compose/releases/download/1.29.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod 755 /usr/local/bin/docker-compose
ln -s /usr/local/bin/docker-compose /usr/bin/docker-compose
```
> [docker-compose installation](https://docs.docker.com/compose/install/)

### 4. 启动docker服务
``` bash
# 启动docker服务
systemctl daemon-reload
systemctl enable docker
systemctl start docker

# 查看docker版本
docker version
```

### 5. 查看服务是否正常
``` bash
# 测试docker是否正常
docker run hello-world

# 查看近期docker进程
docker ps -a
```
