---
title: 网络: TCP - tcp连接存活时间查询方法
date: 2019-07-05 11:52:00
categories: linux/advance
tags: [network,tcp]
---

### 1. 如何查看某个tcp连接的存活时间
``` bash
# 使用netstat或者ss等命令定位到自己希望排查的tcp连接信息
tcp        0      0 <server-ipaddress>:2181      <client-ipaddress>:51786    ESTABLISHED 23928/java

# 根据pid号和客户端的随机端口号来定位tcp文件
sudo lsof -p 23928|grep 51786
java    23928 root   32u     IPv4           11125718       0t0       TCP 11-111-11-111.testss.imtests.com:eforward-><client-ipaddress>:51786 (ESTABLISHED)

# 根据上面的32u推断出文件名称是32，然后根据pid和这个文件名称来查看该文件的创建时间
# 根据创建时间和当前时间，即可推算出该tcp的存活时间
sudo ls -l /proc/23928/fd/32
lrwx------ 1 root root 64 Jun 19 14:34 /proc/23928/fd/32 -> socket:[11125718]
```