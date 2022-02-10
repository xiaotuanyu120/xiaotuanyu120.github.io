---
title: vagrant: 5.0.0 启动错误
date: 2016-10-03 13:09:00
categories: devops/vagrant
tags: [devops,vagrant]
---

### 1.1 启动挂载错误：没有此设备
``` bash
# 开机时提示
/sbin/mount.vboxsf: mounting failed with the error: No such device
```
> 发现登录到虚机里面，/vagrant目录没有内容

### 1.2 解决办法
``` bash
yum install gcc make kernel kernel-devel kernel-headers -y
cd /opt/VBoxGuestAdditions-*/init
./vboxadd setup
```
> 然后在host中执行"vagrant reload"即可

> 注意查看kernel版本和kernel-headers、kernel-devel的版本是否匹配，如果非匹配，可以查看新安装的kernel是否和其匹配，如果匹配，重启一下系统再次检查即可。

---

### 2.1 启动挂载错误：mount变成了rsync
每次vagrant启动时，默认的挂载Vagrantfile目录到/vagrant的动作，被rsync替代

### 2.2 解决办法
参考链接: [github issue](https://github.com/hashicorp/vagrant/issues/7157)
``` ruby
# 增加如下配置到Vagrantfile中
config.vm.synced_folder ".", "/vagrant", type: "virtualbox"
```

---

### 3.1 plugin错误：虚拟机启动，但是初始化报卸载错误
``` bash
The following SSH command responded with a non-zero exit status.
Vagrant assumes that this means the command failed!

umount /mnt

Stdout from the command:



Stderr from the command:

umount: /mnt: not mounted.
```

### 3.2 plugin的问题，可以调整版本解决
- [vagrant github issue：回复说是plugin的问题](https://github.com/hashicorp/vagrant/issues/12084)
- [回退plugin为老版本解决](https://www.devopsroles.com/vagrant-no-virtualbox-guest-additions-installation-found-fixed/)
``` bash
# 卸载最新版本
vagrant plugin uninstall vagrant-vbguest

# 重装老版本
vagrant plugin install vagrant-vbguest --plugin-version 0.21
```

### 4.1 启动错误：如下
按照3.1之中的解决方法，使用centos8镜像的时候，虽然3.1的错误解决了。但又报了另外一个错误，错误的提示是安装的包找不到。最上面有如下这个提示
``` bash
No Virtualbox Guest Additions installation found.
```
所以猜测应该是找不到虚拟机中的vbguest，所以去自动安装，而0.21版本的插件太老，导致安装的包不对，这个问题的解决需要提升vbguest的版本，但是又因为3.1的问题不能升级vbguest。

### 4.2 解决方案：禁用vbguest的自动安装
[如何禁用vbguest自动安装](https://stackoverflow.com/questions/59179637/vagrant-up-causes-guest-additions-to-reinstall-each-time-why)
如上所说，既然虚拟机中的vbguest自动安装会引发问题，那么我们就可以禁用这个自动安装的行为，让虚拟机可以启动，然后后面手动解决虚拟机中的vbguest的安装问题
``` bash
  if Vagrant.has_plugin?("vagrant-vbguest")
    config.vbguest.auto_update = false
  end
```