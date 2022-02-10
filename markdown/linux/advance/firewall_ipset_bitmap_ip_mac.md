---
title: firewall: ipset-bitmap:ip,mac
date: 2017-04-05 13:08:00
categories: linux/advance
tags: [linux,iptables,ipset,firewall]
---

### 0. 参考文档
[ipset Man 文档](http://ipset.netfilter.org/ipset.man.html)  
[gentoo 论坛关于ipset bitmap:ip,mac在iptables中规则的讨论](https://forums.gentoo.org/viewtopic-t-962562-start-0.html)  

---

### 1. 基础用法 - ip
``` bash
ipset create foo hash:ip netmask 30
ipset add foo 192.168.1.0/24
ipset test foo 192.168.1.2
```

**iptables规则**
```
-A INPUT -p tcp -m set --match-set foo src --dport 443 -j ACCEPT
-A INPUT -p tcp -m set --match-set foo dst --dport 443 -j ACCEPT
```
> src是匹配source，dst是匹配destination

### 2. 基础用法 - mac
``` bash
ipset create foo hash:mac
ipset add foo 01:02:03:04:05:06
ipset test foo 01:02:03:04:05:06
```

**iptables规则**
```
-A INPUT -p tcp -m set --match-set foo src --dport 443 -j ACCEPT
-A INPUT -p tcp -m set --match-set foo dst --dport 443 -j ACCEPT
```
> src是匹配source，dst是匹配destination

### 3. 基础用法 - ip,mac
``` bash
ipset create foo bitmap:ip,mac range 192.168.0.0/16
ipset add foo 192.168.1.1,12:34:56:78:9A:BC
ipset test foo 192.168.1.1
```

**iptables规则**
```
-A INPUT -p tcp -m set --match-set foo src,src --dport 443 -j ACCEPT
```
> 特别关注"src,src"，因为有ip和mac两个src

### 4. comment用法
``` bash
ipset add foo 192.168.1.1 comment "this is a comment"
```