---
title: DNS: Linux中的DNS解析是如何工作的
date: 2022-02-10 11:49:00
categories: linux/advance
tags: [dns,resolv.conf,hosts,dnsmasq]
---

### 1. `/etc/hosts`中配置了域名本地解析记录，但是`dig`、`nslookup`、`host`无法识别
在`/etc/hosts`中配置一个本地解析记录

``` bash
cat /etc/hosts | grep "test.localnet"
127.0.0.1 test.localnet
```

使用ping测试是可以成功解析的

``` bash
ping test.localnet -c 1
# OUTPUT:
#PING test.localnet (127.0.0.1) 56(84) bytes of data.
#64 bytes from localhost (127.0.0.1): icmp_seq=1 ttl=64 time=0.042 ms
#
#--- test.localnet ping statistics ---
#1 packets transmitted, 1 received, 0% packet loss, time 0ms
#rtt min/avg/max/mdev = 0.042/0.042/0.042/0.000 ms
```

但是使用`host`、`nslookup`、`dig`却无法找到这个解析

``` bash
host test.localnet
# OUTPUT: 
#Host test.localnet not found: 3(NXDOMAIN)

dig test.localnet
# OUTPUT:
#; <<>> DiG 9.11.4-P2-RedHat-9.11.4-26.P2.el7_9.8 <<>> test.localnet
#;; global options: +cmd
#;; Got answer:
#;; ->>HEADER<<- opcode: QUERY, status: NXDOMAIN, id: 7913
#;; flags: qr rd ra; QUERY: 1, ANSWER: 0, AUTHORITY: 0, ADDITIONAL: 0
#
#;; QUESTION SECTION:
#;test.localnet.			IN	A
#
#;; Query time: 3 msec
#;; SERVER: 192.168.65.5#53(192.168.65.5)
#;; WHEN: Thu Feb 10 06:11:10 UTC 2022
#;; MSG SIZE  rcvd: 31

nslookup test.localnet
# OUTPUT:
#Server:		192.168.65.5
#Address:	192.168.65.5#53
#
#** server can't find test.localnet: NXDOMAIN
```

google之后发现，host、dig、nslookup直接对DNS服务器来请求dns解析，而其他使用[gethostbyname](https://man7.org/linux/man-pages/man3/gethostbyname.3.html)的程序，都是会按照`nsswitch.conf`中配置的host的读取顺序来解析域名或主机名，而默认的nsswitch是将`/etc/hosts`放在第一顺位，所以使用ping可以获取`/etc/hosts`中的dns记录。

> [stackoverflow: Why does the host command not resolve entries in /etc/hosts?](https://serverfault.com/questions/498500/why-does-the-host-command-not-resolve-entries-in-etc-hosts)


但是接着又出现一个问题，`nsswitch.conf`是做什么用的？为什么它会影响域名的解析？

### 2. `nsswitch.conf`

#### 2.1 `nsswitch.conf`是什么？它是做什么用的？

[nsswitch.conf](https://man7.org/linux/man-pages/man5/nsswitch.conf.5.html)是NSS(Name Service Switch)的配置文件，用于给GNU C语言库和某些其他的程序来确定从哪里和以什么顺序来获取名字服务信息（不仅仅包含主机名和域名）。

#### 2.2 `nsswitch.conf`对于DNS解析有什么影响？

NSS(Name Service Switch)不只是配置主机名和域名的解析来源和顺序，它是一个综合的名字解析来源和顺序配置服务，详细可见[man文档](https://man7.org/linux/man-pages/man5/nsswitch.conf.5.html)。

对于主机名和域名的解析，是合并到了一个`hosts`的配置中，举个例子

```
hosts:      files dns myhostname
```

上面的配置含义是`files`(就是/etc/hosts)是第一顺位，`dns`(就是/etc/resolv.conf配置的dns服务器地址)是第二顺位。

让我们来调换`dns`和`files`配置的顺序使用ping来验证一下

``` bash
# 增加google.com的本地解析记录
cat /etc/hosts | grep google.com
# OUTPUT: 
#127.0.0.1 google.com


# "hosts:      files dns myhostname"的情况下，ping的结果是127.0.0.1
ping google.com -c 2
# OUTPUT:
#PING google.com (127.0.0.1) 56(84) bytes of data.
#64 bytes from localhost (127.0.0.1): icmp_seq=1 ttl=64 time=0.025 ms
#64 bytes from localhost (127.0.0.1): icmp_seq=2 ttl=64 time=0.067 ms
#
#--- google.com ping statistics ---
#2 packets transmitted, 2 received, 0% packet loss, time 1040ms
#rtt min/avg/max/mdev = 0.025/0.046/0.067/0.021 ms


# "hosts:      dns files myhostname"的情况下，ping的结果是dns服务器返回的结果
ping google.com -c 2
# OUTPUT:
#PING google.com (142.251.12.102) 56(84) bytes of data.
#64 bytes from se-in-f102.1e100.net (142.251.12.102): icmp_seq=1 ttl=37 time=6.03 ms
#64 bytes from se-in-f102.1e100.net (142.251.12.102): icmp_seq=2 ttl=37 time=6.55 ms
#
#--- google.com ping statistics ---
#2 packets transmitted, 2 received, 0% packet loss, time 1005ms
#rtt min/avg/max/mdev = 6.038/6.298/6.559/0.272 ms
```

#### 2.3 `nsswitch.conf`的应用对象是？
在[nsswitch.conf的man文档](https://man7.org/linux/man-pages/man5/nsswitch.conf.5.html)中可以查到以下说明

```
hosts  Host names and numbers, used by gethostbyname(3) and
              related functions.
```

含义是NSS会被gethostbyname或者相关的functions使用，基本上使用了C语言的这些函数来做名字解析的，都会按照NSS中的`hosts`的配置来解析域名。

### 3. 其他会影响DNS的因素
- JVM中的dns设定，参见[java.security 中的dns超时配置](/java/jvm/jdk_3.1.0_config_java.security.html)
- dnsmasq中的一些dns方面的配置，可以参见[dnsmasq的简要介绍](/service/dnsmasq/dnsmasq_01.01_introduction_and_basic.html)