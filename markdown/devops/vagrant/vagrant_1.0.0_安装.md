---
title: vagrant: 1.0.0 多平台安装
date: 2016-08-27 14:04:00
categories: devops/vagrant
tags: [devops,vagrant]
---

### 1. mac上安装vagrant
``` bash
# 安装wget
sudo brew install wget

# 下载vagrant
wget https://releases.hashicorp.com/vagrant/1.8.5/vagrant_1.8.5.dmg

# 挂载dmg镜像
hdiutil attach vagrant_1.8.5.dmg

# 安装vagrant
cd /Volumes/Vagrant/
sudo installer -package ./Vagrant.pkg -target /
installer: Package name is Vagrant
installer: Installing at base path /
installer: The install was successful.

# 检查安装结果
vagrant -v
Vagrant 1.8.5
which vagrant
/usr/local/bin/vagrant

# 卸载dmg镜像
hdiutil detach /Volumes/Vagrant/
```
> 其实也有图形界面的程序下载和安装

#### 1.1 mac m1版本
mac m1版本上只有parallels可用，但注意要是pro和bussiness版本才可以

``` bash
# 安装parallels provider插件
vagrant plugin install vagrant-parallels
```
> [parallels vagrant文档](https://parallels.github.io/vagrant-parallels/docs/)

> 选择镜像的时候到[vagrant boxes](https://app.vagrantup.com/boxes/search?page=1&provider=parallels&q=arm&sort=downloads&utf8=✓)搜索parallels的arm镜像即可，我目前使用的是`mattburnett/fedora-35-m1-arm64`

---

### 2. 在centos上安装vagrant
``` bash
# 安装环境包
yum upgrade
yum install wget epel-release
yum install kernel-devel-`uname -r`

# 安装virtualbox
cd /etc/yum.repos.d
wget http://download.virtualbox.org/virtualbox/rpm/rhel/virtualbox.repo
# 安装DKMS（Dynamic Kernel Module Support）
yum --enablerepo=epel install dkms -y
yum install VirtualBox-5.1 -y

# 下载vagrant
wget https://releases.hashicorp.com/vagrant/1.8.5/vagrant_1.8.5_x86_64.rpm

# 安装vagrant
rpm -ivh vagrant_1.8.5_x86_64.rpm

# 查看vagrant状态
vagrant -v
Vagrant 1.8.5
which vagrant
/usr/bin/vagrant
```

---

### 3. windows上安装
直接去官网下载exe文件安装，此处不赘述
