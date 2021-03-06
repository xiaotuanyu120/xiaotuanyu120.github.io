---
title: 18.4.1: 防火墙-C7安装iptables
date: 2016年8月12日
categories: 14:32
---
 
---
title: 防火墙-Centos7使用iptables
date: 2016-08-12 14:45:00
categories: linux
tags: [linux,firewalld,iptables]
---
### Centos7的防火墙改变
centos7上默认没有安装iptables，而是采用了firewalld进行了替代
 
**什么是iptables？**
iptables是一款防火墙软件，基于netfilter机制，用户可以通过此软件来制定不同协议和针对不同表链的规则。
iptables控制ipv4，ip6tables控制ipv6
 
**什么是firewalld**
firewalld是新一代的linux防火墙，也是基于netfilter机制，增加了许多新的特性。
同时支持ipv4和ipv6，还支持bridge，另外增加了zone的新概念，详细信息可以参见下面链接
[firewalld参考链接1](http://www.firewalld.org/)
[firewalld参考链接2](http://www.ibm.com/developerworks/cn/linux/1507_caojh/)
 
但许多情况下，如果还是要用到iptables，可以按照下面操作来替换
 
### 禁用firewalld
``` bash
systemctl disable firewalld
systemctl stop firewalld
```
 
### 安装iptables
``` bash
yum install iptables-services
systemctl enable iptables
systemctl start iptables
```
 
### iptables规则保存和恢复
iptables默认的规则保存文件是**/etc/sysconfig/iptables**
``` bash
iptables-save > iptables.rules
iptables-restore iptables.rules
```
C7上无法使用service iptables save去保存规则了，可以使用iptables-save > /etc/sysconfig/iptables代替
 
