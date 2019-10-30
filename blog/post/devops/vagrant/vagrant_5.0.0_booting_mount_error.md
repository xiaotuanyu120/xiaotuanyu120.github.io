---
title: vagrant: 5.0.0 开机挂载错误
date: 2016-10-03 13:09:00
categories: devops/vagrant
tags: [devops,vagrant]
---
### vagrant: 5.0.0 开机挂载错误

---

### 1. 错误提示
``` bash
# 开机时提示
/sbin/mount.vboxsf: mounting failed with the error: No such device
```
> 发现登录到虚机里面，/vagrant目录没有内容

---

### 2. 解决办法
``` bash
yum install gcc make kernel kernel-devel kernel-headers -y
cd /opt/VBoxGuestAdditions-*/init
./vboxadd setup
```
> 然后在host中执行"vagrant reload"即可

> 注意查看kernel版本和kernel-headers、kernel-devel的版本是否匹配，如果非匹配，可以查看新安装的kernel是否和其匹配，如果匹配，重启一下系统再次检查即可。
