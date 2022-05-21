---
title: linux内核: cgroup
date: 2021-01-30 15:27:00
categories: linux/advance
tags: [linux,kernel,cgroup]
---

### 1. activate cgroup v2
#### 检查cgroup v2
需要kernel 4.12.0-rc5以上，发行版需要rhel/centos8，检查是否启用cgroup v2使用以下命令

``` bash
# 检查系统内核，内核必须要在4.12，0-rc5以上才可以
uname -r

# 检查系统是否支持cgroup v2
grep cgroup /proc/filesystems

# 检查是否已经启用cgroup v2
mount|grep cgroup
```

#### 启用cgroup v2
``` bash
sed -i 's/^GRUB_CMDLINE_LINUX=.*$/GRUB_CMDLINE_LINUX="console=ttyS0,115200n8 console=tty0 net.ifnames=0 rd.blacklist=nouveau nvme_core.io_timeout=4294967295 crashkernel=auto systemd.unified_cgroup_hierarchy=1"/g' /etc/default/grub
grub2-mkconfig -o /boot/grub2/grub.cfg
reboot
```
> [how to activate cgroup v2](https://www.redhat.com/en/blog/world-domination-cgroups-rhel-8-welcome-cgroups-v2)