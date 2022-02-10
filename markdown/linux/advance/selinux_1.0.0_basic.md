---
title: selinux 1.0.0 basic
date: 2016-03-29 09:50:00
categories: linux/advance
tags: [selinux]
---

### 0. selinux
selinux是一个lable系统，每一个文件，每一个目录，每一个进程，每一个用户，每一个资源都有自己的lable

### 1. semanage命令安装
``` bash
yum install -y policycoreutils-python
```

---

### 2. 查看及修改服务状态
``` bash
getenforce

# 临时关闭selinux(数字1是开启)
setenforce 0

# 永久更改selinux
vim /etc/selinux/config
*********************************
# SELINUX= 可以配置以下三个状态:
#     enforcing - SELinux security policy is enforced.
#     permissive - SELinux prints warnings instead of enforcing.
#     disabled - No SELinux policy is loaded.
SELINUX=enforcing
*********************************
```

---

### 3. 查看及修改文件selinux上下文
命令：
- chcon，变更文件的selinux context（用于临时变更，可被还原）
- restorecon，还原文件的selinux context默认值（比如/var/www/html下的文件默认就是httpd_sys_content_t）
- semanage，变更selinux policy

``` bash
# 查看selinux context的user
semanage user -l

# 查看文件和目录的selinux context
ls -lZ /root/anaconda-ks.cfg
-rw-------. root root system_u:object_r:admin_home_t:s0 anaconda-ks.cfg

# 查看进程的selinux context
ps auxZ

# 使用semanage永久修改文件上下文(-a add；-t type)
semanage fcontext -a -t samba_share_t '/common(/.*)?'
semanage fcontext -a -t httpd_sys_content_t '/var/www/virtual(/.*)?'

# 使用chcom临时修改文件上下文
chcon -u system_u /usr/lib/systemd/system/docker.servcie

# 重建文件上下文(-v 过程；-F force；-R recursively)
restorecon -vFR /common/

# 修改端口上下文(给http的tcp协议增加8908端口)
semanage port -a -t http_port_t -p tcp 8908
```

selinux的context保存在
- selinux将所有目录的context储存在`/etc/selinux/targeted/contexts`
- 大多数的file和目录的context信息储存在`/etc/selinux/targeted/contexts/fils/files_contexts`
- 可以将自定义的context添加在`/etc/selinux/targeted/contexts/files/files_contexts.local`