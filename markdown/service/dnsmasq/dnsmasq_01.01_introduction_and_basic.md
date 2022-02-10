---
title: dnsmasq基础知识
date: 2022-02-08 22:12:00
categories: service/dnsmasq
tags: [dns,dnsmasq]
---

### 0. dnsmasq是什么？
dnsmasq是一个轻量级的DHCP和DNS缓存服务器。常用于本地的DNS解析服务器。

> 参考文档：
>
> - [dnsmasq man page](https://thekelleys.org.uk/dnsmasq/docs/dnsmasq-man.html)
> - [dnsmasq config example](https://thekelleys.org.uk/dnsmasq/docs/dnsmasq.conf.example)
> - [dnsmasq setup docs](https://thekelleys.org.uk/dnsmasq/docs/setup.html)

### 1. 如何安装dnsmasq
#### 1.1 源码安装
源码安装的步骤很简单，通常执行下面的命令就足够了

``` bash
# 提前下载好源码，解压，然后进入源码目录，执行以下命令
make install
```

> 二进制文件: `/usr/local/sbin/dnsmasq`


#### 1.2 启动
启动方式也很简单，直接执行dnsmasq命令即可
``` bash
dnsmasq
```
进程默认是`daemon模式`后台运行，并监听53端口

> 可以使用`-d, --no-daemon`选项来切换`daemon模式`为`debug模式`

``` bash
dnsmasq -d
dnsmasq: started, version 2.86 cachesize 150
dnsmasq: compile time options: IPv6 GNU-getopt no-DBus no-UBus no-i18n no-IDN DHCP DHCPv6 no-Lua TFTP no-conntrack ipset auth no-cryptohash no-DNSSEC loop-detect inotify dumpfile
dnsmasq: reading /etc/resolv.conf
dnsmasq: using nameserver 192.168.65.5#53
dnsmasq: read /etc/hosts - 7 addresses
```

dnsmasq进程需要使用root身份启动，因为它需要使用特权端口53，启动后进程会抛弃root，使用nobody用户运行进程。

### 2. 基本配置
一般情况下，一台已经使用`/etc/resolv.conf`和`/etc/hosts`配置好dns解析的服务器，可以在没有配置文件的情况下，直接启动`dnsmasq`进程来提供dns服务。

在简单的通过`无配置的dnsmasq`启动服务的情况下，dnsmasq提供dns服务是通过读取`/etc/resolv.conf`来获取dns上游服务器，还有通过`/etc/hosts`获取本地dns解析。

#### 2.1 DNS上游服务器地址获取 - `/etc/resolv.conf`
首先，我们需要创建一个`新的nameserver文件`来替代`/etc/resolv.conf`

``` bash
cat << EOF > /etc/dnsmasq.resolv.conf
#DNS UPSTREAM SERVER
nameserver 8.8.8.8
nameserver 4.4.4.4
EOF
```

然后创建dnsmasq启动时加载的配置文件

``` bash
# Change this line if you want dns to get its upstream servers from
# somewhere other that /etc/resolv.conf
resolv-file=/etc/dnsmasq.resolv.conf
```

> dnsmasq默认加载的配置文件是`/etc/dnsmasq.conf`，如果需要加载其他位置的配置文件，启动`dnsmasq`时需要使用`--conf-file=/path/to/dnsmasq.conf`

重新启动`dnsmasq`即可

#### 2.2 本地DNS解析信息获取 - `/etc/hosts`
可以禁用本地DNS解析，取消对`/etc/hosts`的加载

``` bash
# If you don't want dnsmasq to read /etc/hosts, uncomment the
# following line.
no-hosts
```

或者需要从`/etc/hosts`之外的文件来读取本地DNS解析记录

``` bash
# or if you want it to read another file, as well as /etc/hosts, use
# this.
addn-hosts=/etc/dnsmasq.hosts
```

**值得注意的是**，hosts记录修改后，需要重启dnsmasq才会生效。如果希望热加载hosts文件，需要在启动dnsmasq时增加如下选项。增加下面的选项后，dnsmasq会加载该目录下的所有hosts文件，新增文件或者修改原有文件会触发hosts的重新加载

``` bash
# Read all the hosts files contained in the directory. New or changed files are read automatically. See --dhcp-hostsdir for details.
dnsmasq --hostsdir=<path/to/hosts-file-dir>
```

#### 2.3 指定部分域名使用固定的DNS上游服务器
将所有对`*.yourhostname.com`的dns解析请求发送到`114.114.114.114`

``` bash
server=/.yourhostname.com/114.114.114.114
```

#### 2.4 指定部分域名解析记录
将所有`*.yourhostname.com`的请求，解析到`127.0.0.1`

``` bash
# Add domains which you want to force to an IP address here.
# The example below send any host in double-click.net to a local
# web-server.
address=/double-click.net/127.0.0.1
```

### 3. 使用dnsmasq作为dns解析服务器
只需要将`/etc/resolv.conf`中原有配置删除，增加如下内容即可

```
nameserver <ip-of-dnsmasq-listen>
```