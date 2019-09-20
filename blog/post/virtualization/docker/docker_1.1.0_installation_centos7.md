---
title: 1.1.0 安装(Centos7)
date: 2015-12-12 16:06:00
categories: virtualization/docker
tags: [docker]
---
### DOCKER 1.1.0 安装(Centos7)

---

[docker安装官方文档](https://docs.docker.com/engine/installation/linux/centos/)
### 0. 环境介绍
``` bash
# 系统版本centos7.2
cat /etc/redhat-release
CentOS Linux release 7.2.1511 (Core)

# 内核版本
uname -r
3.10.0-327.el7.x86_64
```

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
# 创建docker的yum源
yum install -y yum-utils \
  device-mapper-persistent-data \
  lvm2
yum-config-manager \
    --add-repo \
    https://download.docker.com/linux/centos/docker-ce.repo

# 关闭非稳定源(默认为关闭)
yum-config-manager --disable docker-ce-edge
yum-config-manager --disable docker-ce-test
yum-config-manager --disable docker-ce-nightly

# 查看所有可用的版本
yum list docker-ce --showduplicates | sort -r

# 选择要安装的版本，已经安装docker
VERSION_STRING=18.09.1
yum install -y docker-ce-${VERSION_STRING} docker-ce-cli-${VERSION_STRING} containerd.io
```

### 3. install docker-compose
``` bash
curl -L "https://github.com/docker/compose/releases/download/1.24.1/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
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
