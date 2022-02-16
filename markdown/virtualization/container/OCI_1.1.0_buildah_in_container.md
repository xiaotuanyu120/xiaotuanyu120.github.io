---
title: OCI 1.1.0 在容器中运行buildah
date: 2020-06-05 16:28:00
categories: virtualization/container
tags: [container,podman,docker,buildah,fuse-overlayfs]
---

### 0. 背景说明
目前，CI/CD中容器镜像编译的问题，使用的解决方案是把host上的docker socket映射到dind中，然后实现dind容器中的容器镜像编译。这样做的缺点是牺牲了安全性，毕竟目前版本的docker（19.03之前）还是以root身份启动，dind拥有了docker socket的权限是一个很大的漏洞。

为了解决这样的问题，这个时候就需要引入podman和buildah，它们都是基于OCI规范的容器工具，podman致力于容器的运行，buildah致力于镜像的管理。

### 1. 尝试在容器中运行buildah及遇到的问题
#### 首先，明确思路
基于官方buildah的镜像，增加jdk、node等编译工具，编译成新的buildah-compile镜像。将新镜像用于gitlab-ci中用于编译项目代码(此部分不在此文章中涉猎，仅关注在如何在容器中运行buildah这个问题上)。

#### 第一步，在官方buildah镜像中测试使用buildah编译镜像
在host安装podman和buildah

``` bash
yum install podman buildah -y
```

参照[Best practices for running Buildah in a container](https://developers.redhat.com/blog/2019/08/14/best-practices-for-running-buildah-in-a-container/)，使用官方buildah镜像有以下注意点

- 运行普通的root容器，不增加任何特权（不增加capibility）
  - 使用fuse-overlayfs，需要host的/dev/fuse
- buildah的运行，默认需要chroot，默认不用user namespace

``` bash
podman run -it --rm --device /dev/fuse quay.io/buildah/stable bash
cd
echo -e "FROM quay.io/buildah/stable\nRUN dnf -y update;dnf -y install java-1.8.0-openjdk-devel nodejs maven;dnf -y clean all" > Dockerfile
buildah bud -t buildah-compile .
Error during unshare(CLONE_NEWUSER): Invalid argument
User namespaces are not enabled in /proc/sys/user/max_user_namespaces.
ERRO error parsing PID "": strconv.Atoi: parsing "": invalid syntax 
ERRO (unable to determine exit status) 
```
这个错误信息是提示需要启用user namespaces，默认`/proc/sys/user/max_user_namespaces`是0，也就是disable。在git上提过issue，答复是[虽然buildah在此镜像中不需要使用user namespace，但是依然需要创建user namespace获取capabilities](https://github.com/containers/buildah/issues/2393#issuecomment-639414566)。
``` bash
echo 15000 > /proc/sys/user/max_user_namespaces
```
``` bash
podman run -it --rm --device /dev/fuse quay.io/buildah/stable bash
cd
echo -e "FROM quay.io/buildah/stable\nRUN dnf -y update;dnf -y install java-1.8.0-openjdk-devel nodejs maven;dnf -y clean all" > Dockerfile
buildah bud -t buildah-compile .
STEP 1: FROM quay.io/buildah/stable
Getting image source signatures
Copying blob 2d8f327dcfdd done  
Copying blob 03c837e31708 done  
Copying blob 98d006c204b6 done  
Copying blob 177f1feb6e39 done  
Copying blob f85e6dec1a0b done  
Copying config e03a232aae done  
Writing manifest to image destination
Storing signatures
STEP 2: RUN dnf -y update;dnf -y install java-1.8.0-openjdk-devel nodejs maven;dnf -y clean all
error building at STEP "RUN dnf -y update;dnf -y install java-1.8.0-openjdk-devel nodejs maven;dnf -y clean all": error mounting container "f830cbd673885c0da5511a1b5422ff77532195e60989eeae9d2dd80ecc779cd1": error mounting build container "f830cbd673885c0da5511a1b5422ff77532195e60989eeae9d2dd80ecc779cd1": failed to canonicalise path for "/var/lib/containers/storage/overlay/a9df41225f6b2c802b51e7aca7ca43ef7f89509a769d7091a6081764b3f8c771/merged": lstat /var/lib/containers/storage/overlay/a9df41225f6b2c802b51e7aca7ca43ef7f89509a769d7091a6081764b3f8c771/merged: invalid argument
ERRO exit status 1
```
这个错误查看了一下，是一个fuse-overlayfs的问题，字面意思是没挂载上存储。如果`--storage-driver vfs`是可以执行通过的，但是vfs性能太差，最好别用。于是在[github的issue](https://github.com/containers/buildah/issues/1831#issuecomment-528247444)里看到了一个这样的讨论，大意是，一个人认为fuse-overlayfs是不可以运行在本身已经是overlay的容器中的，所以必须要挂载host目录到/var/lib/containers，避免overlay top on overlay。但是另外一个哥们答复说，fuse-overlayfs是可以在overlay之上运行的，但是至于为啥这里不行，它也不太清楚，暂时也同意挂载host目录到/var/lib/containers来解决这个问题。总之，不管如何，挂载host的目录到容器中再试试吧。
``` bash
mkdir storage
podman run -it --rm --device /dev/fuse -v ./storage:/var/lib/containers quay.io/buildah/stable bash
cd
echo -e "FROM quay.io/buildah/stable\nRUN dnf -y update;dnf -y install java-1.8.0-openjdk-devel nodejs maven;dnf -y clean all" > Dockerfile
buildah bud -t buildah-compile .
STEP 1: FROM quay.io/buildah/stable
STEP 2: RUN dnf -y update;dnf -y install java-1.8.0-openjdk-devel nodejs maven;dnf -y clean all
error building at STEP "RUN dnf -y update;dnf -y install java-1.8.0-openjdk-devel nodejs maven;dnf -y clean all": error mounting container "d068b5f32f26e11bf0057f33afe0acfc9ed21df4ee4c2d484e410785921ae535": error mounting build container "d068b5f32f26e11bf0057f33afe0acfc9ed21df4ee4c2d484e410785921ae535": failed to canonicalise path for "/var/lib/containers/storage/overlay/26556401814a0483015367e8c56c39ddb5af3af12d9504b67a66e7f0ba6a03d9/merged": lstat /var/lib/containers/storage/overlay/26556401814a0483015367e8c56c39ddb5af3af12d9504b67a66e7f0ba6a03d9/merged: invalid argument
ERRO exit status 1 
```
这里我是很疑惑的，查了很多资料，很多人提到了各式各样的问题，总之就集中在两点：
1. /dev/fuse设备，host内核中启用fuse模块`yum install fuse3 fuse3-devel;modprobe fuse; lsmod |grep fuse`
2. 挂载host目录到/var/lib/containers

可是这两点我都做了，还是依旧不可以。而且，我也不是用rootless的方式启动podman，没理由不可以的。既然网上查不到，只能github提交issue来解决了。关于这个[issue](https://github.com/containers/buildah/issues/2393)，我是从那个user namespace的错误提交的，是因为我要确认下，为啥buildah明确不用user namespace，还提示那个要启用user namespace的提示。得到无论是否使用user namespace都需要启用内核功能之后，后续聊到了之后的报错，源码的维护者还是坚持在我已经关注过的两点上指点我进行尝试。

最后无果后，只能自力更生来尝试复盘。用到的所有工具

- centos7
- quay.io/buidlah/stable(base on fedora 32)
- buildah
- podman
- fuse-overlayfs

看过工具清单之后，感觉可以从两个方向入手

- centos7 update到最新;kernel update到最新
- 基于fedora的镜像自定义成基于centos的(因为宿主机和容器共享一个内核，所以我担心是fedora镜像中的软件和方案本身搭配的是fedora的高版本内核，而我不可能线上用fedora，所以只能把镜像的基础系统版本降级到centos的环境)

#### 第二步，尝试自定义镜像（基于centos7）

系统先不升级，尝试自定义镜像

``` bash
# env
uname -a
Linux localhost.localdomain 3.10.0-693.5.2.el7.x86_64 #1 SMP Fri Oct 20 20:32:50 UTC 2017 x86_64 x86_64 x86_64 GNU/Linux

cat /etc/redhat-release 
CentOS Linux release 7.4.1708 (Core)

# 安装fuse ；内核加载fuse模块；开启user namespace内核功能；安装podman和buildah
yum install fuse3 fuse3-devel
modprobe fuse
echo 15000 > /proc/sys/user/max_user_namespaces
yum install podman buildah -y

yum list installed |grep fuse
Failed to set locale, defaulting to C
fuse.x86_64                      2.9.2-11.el7                   @base           
fuse-overlayfs.x86_64            0.7.2-6.el7_8                  @extras         
fuse3.x86_64                     3.6.1-4.el7                    @extras         
fuse3-devel.x86_64               3.6.1-4.el7                    @extras         
fuse3-libs.x86_64                3.6.1-4.el7                    @extras    

# 使用root身份来在宿主机创建一个自定义版本的buildah镜像
cd /root
mkdir -p buildah-test/build && cd buildah-test/build
cat > Dockerfile << EOF
# stable/Dockerfile
#
# Build a Buildah container image from the latest
# stable version of Buildah on the Fedoras Updates System.
# https://bodhi.fedoraproject.org/updates/?search=buildah
# This image can be used to create a secured container
# that runs safely with privileges within the container.
#
# change fedora:latest to centos:7
FROM centos:7

# Don't include container-selinux and remove
# directories used by yum that are just taking
# up space.
# remove --exclude container-selinux
RUN useradd build; yum -y update; yum -y reinstall shadow-utils; yum -y install buildah fuse-overlayfs ; rm -rf /var/cache /var/log/dnf* /var/log/yum.*;

RUN echo -e '[engine]\ncgroup_manager = "cgroupfs"' > /etc/containers/containers.conf

# Adjust storage.conf to enable Fuse storage.
RUN chmod 644 /etc/containers/containers.conf; sed -i -e '/size = ""/amount_program = "/usr/bin/fuse-overlayfs"' -e '/additionalimage.*/a "/var/lib/shared",' -e 's|^mountopt[[:space:]]*=.*$|mountopt = "nodev,fsync=0"|g' /etc/containers/storage.conf
RUN mkdir -p /var/lib/shared/overlay-images /var/lib/shared/overlay-layers; touch /var/lib/shared/overlay-images/images.lock; touch /var/lib/shared/overlay-layers/layers.lock

# Set an environment variable to default to chroot isolation for RUN
# instructions and "buildah run".
ENV BUILDAH_ISOLATION=chroot
EOF

# note of the changes of customized image:
# 1. change fedora:latest to centos:7
# 2. remove --exclude container-selinux

buildah -t buildah-centos7 bud .


# 使用自定义镜像来执行，成功
cd ~/buildah-test
mkdir storage

podman run -it --rm --device /dev/fuse:rw -v ./storage:/var/lib/containers:Z buildah-centos7 bash
cd
echo -e "FROM quay.io/buildah/stable\nRUN dnf -y update;dnf -y install java-1.8.0-openjdk-devel nodejs maven;dnf -y clean all" > Dockerfile
buildah bud -t buildah-compile .
```

升级系统后，再来试试自定义镜像
``` bash
yum update

# 重启系统，自动从最新的内核启动

echo 15000 > /proc/sys/user/max_user_namespaces

# 使用自定义镜像，成功
podman run -it --rm --device /dev/fuse:rw -v ./storage:/var/lib/containers:Z buildah-centos7 bash
cd
echo -e "FROM quay.io/buildah/stable\nRUN dnf -y update;dnf -y install java-1.8.0-openjdk-devel nodejs maven;dnf -y clean all" > Dockerfile
buildah bud -t buildah-compile .
```

最终，原因还真有可能是我猜想的，基于fedora的buildah镜像中的fuse-overlayfs和centos内核配合出现问题。换成centos基础的buildah安装的fuse-overlayfs搭配centos版本的内核就okay了。暂时先提交给了buildah的源码维护者，等他们排查了。

这里补充一下两个镜像中的fuse-overlayfs的版本
``` bash
podman run -it --rm --device /dev/fuse -v ./storage:/var/lib/containers quay.io/buildah/stable fuse-overlayfs --version
fuse-overlayfs: version 1.0.0
FUSE library version 3.9.1
using FUSE kernel interface version 7.31
fusermount3 version: 3.9.1

podman run -it --rm --device /dev/fuse:rw -v ./storage:/var/lib/containers:Z buildah-centos7 fuse-overlayfs --version
fuse-overlayfs: version 0.7.2
FUSE library version 3.6.1
using FUSE kernel interface version 7.29
```