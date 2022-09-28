---
title: 网络: IP - IP地址简介
date: 2022-05-11 11:52:00
categories: linux/advance
tags: [network,tcp]
---


## 1. IP地址简介
- [IANA: Private Use IP](https://www.iana.org/help/abuse-answers)
- [avast: public ip vs private ip](https://www.avast.com/c-ip-address-public-vs-private)

### 1.1 IP地址类型
目前有两种IP网段类型，IPV4和IPV6。

### 1.2 IP地址格式
其中IPV4从1983年1月1日开始使用，直至今日依然被广泛使用。IPV4的格式是用"."分隔开的四段数字，每段数字的取值范围从0-255，于是IPV4的地址范围从0.0.0.0到255.255.255.255。

而IPV6是从1999年开始部署，IPV6的地址是128位数字，通常使用十六进制字符表示，例如`2001:db8::abc:587`

### 1.3 IP地址分配
IP地址的分配和管理，是以Internet Assigned Numbers Authority (IANA)为中心，其与5个Regional Internet Registries (RIRs)合作来管理。

> InterNIC(域名注册)和IANA(DNS root, IP address)都归于ICANNA运营。

RIR：
- AfriNIC (Africa and parts of the Indian Ocean)
- APNIC (Asia/Pacific Region)
- ARIN (North America and parts of the Caribbean)
- LACNIC (Latin America and parts of the Caribbean)
- RIPE NCC (Europe, the Middle East and Central Asia)

RIR是实际的ip分配机构，它们将ip网段分配给不同的ISP。而IANA则作为一个顶层的注册机构，例如下面这条注册信息
```
123/8   APNIC   2006-01 whois.apnic.net ALLOCATED
```
这代表了 123.0.0.0 - 123.255.255.255 在2006年1月分配给了APNIC。如果希望知道这个网段中的一段子网段分配给了谁，需要在whois.apnic.net中查询。

IANA只记录以下信息：
- 已分配给 RIR 或其他用户的IP地址
- 保留用于特殊用途的那些IP地址
- 那些还没有被分配，留作以后分配和使用的

> - 特殊用途的ip地址在IANA显式已经被注册
> - IANA保留了192.0.32.0 - 192.0.47.255自用

## 2. 特殊用途的地址
### 2.1 私有IP地址
这些私有IP地址，可以被任何人使用，无需任何其他人授权。同时，这些地址也永远不可能在互联网上可见。
```
10.0.0.0 - 10.255.255.255     (10.0.0.0/8)
172.16.0.0 - 172.31.255.255   (172.16.0.0/12)
192.168.0.0 - 192.168.255.255 (192.168.0.0/16)
```
> 由上至下，也被成为ABC三类私有网段。详情见[RFC1918](https://www.rfc-editor.org/rfc/rfc1918.html)

### 2.2 自动配置的IP地址
```
169.254.0.0 - 169.254.255.255
```
用于一个联网设备需要ip地址，却没有被分配静态ip，且无法通过dhcp获取到ip时，自动给这个联网设备分配的一个地址。避免出现网络设备没有ip的情况，但需要注意，这个ip的流量会被限制在本地网络。

### 2.3 回环网络IP地址
```
127.0.0.0 - 127.255.255.255 (127.0.0.0/8)
```
用于代表设备本身的网络地址，最常用的是127.0.0.1。

### 2.4 多播地址
```
224.0.0.0 - 239.255.255.255
```
被预留用于在 Internet 中提供多播服务的特殊目的

### 2.5 共享地址段
```
100.64.0.0/10
```
用于运营商给用户提供的NAT解决方案

其他的还有IANA预留给美国政府机构的地址，详细内容可以查阅[iana ipv4 ip address space registry](https://www.iana.org/assignments/ipv4-address-space/ipv4-address-space.xml#note1)