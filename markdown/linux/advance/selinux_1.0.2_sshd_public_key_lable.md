---
title: selinux 1.0.2 lable sshd public key file
date: 2021-02-16 22:36:00
categories: linux/advance
tags: [selinux]
---

### 0. 背景说明
sshd默认限制如下
- port: ssh_port_t >> tcp 22
- 公钥文件: ssh_home_t >> `/home/[^/]+/.ssh(/.*)?`
> [man docs: sshd selinux lable](https://www.systutorials.com/docs/linux/man/8-sshd_selinux/)

线上常见的现象是，端口不会是22；另外公钥所在的家目录也不一定在/home；此时就需要用到下面的方法来调整

### 1. 增加自定义sshd端口
``` bash
semanage port -m -t ssh_port_t -p tcp 2222

semanage port -l | grep ssh_port_t
ssh_port_t             tcp      2222, 22
```

### 2. 增加自定义的公钥目录位置
``` bash
semanage fcontext -a -t ssh_home_t '/path/to/home/.ssh(/.*)?'
restorecon -vFR /path/to/home/.ssh
```