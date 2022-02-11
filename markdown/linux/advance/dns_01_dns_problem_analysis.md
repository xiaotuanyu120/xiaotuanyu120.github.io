---
title: DNS解析问题排查实践
date: 2022-02-10 16:49:00
categories: linux/advance
tags: [dns,resolv.conf,hosts,dnsmasq,gethostbyname,nginx,resolver]
---

### 问题背景
调用路径：`service --> public-proxy(nginx) --> public world`

service通过nginx代理访问外网API A域名，A域名解析的IP有两个(RS1 和 RS2)，且都有防火墙白名单限制。A域名的防火墙已经给nginx代理服务器的IP加白。

遇到的问题是，nginx访问A域名时，有报错说connection timeout，进一步查看，发现A域名解析出来的IP并不是RS1 和RS2。

### 初步排查
通过排查，发现服务器使用dnsmasq做了DNS缓存。`/etc/resolv.conf`中配置了dns server为本机的`dnsmasq`，而`dnsmasq`通过`resolv-file=***`指向特定的resolv配置文件，配置使用了四个DNS上游服务器IP地址。使用`dig`指定DNS服务器地址逐个解析排查，将解析结果和RS1 RS2比对，发现是其中两个DNS服务器返回的解析结果和RS1 RS2不匹配。

**找到了问题的直接原因（关于这两台DNS服务器返回的解析结果为什么突然不一致的问题这里先不做讨论），最快的解决方式是修改`/etc/hosts`来固定域名的解析地址。为了尽快恢复故障，于是采用了这个方案。**

### 问题
**但是，写了`/etc/hosts`后，业务反馈错误量并未下降，并且使用`nslookup`解析出来的结果并不是`/etc/hosts`里面本地DNS记录。**

~~基于对`nslookup`结果的信任，这里判断`/etc/hosts`中的DNS记录并未生效。~~

于是产生以下几个疑问

- `dnsmasq`在这个过程中扮演了什么角色，影响了dns解析中的哪些因素？
- linux中的进程是如何进行dns解析过程的？

#### 首先是第一个问题，dnsmasq在这个过程中扮演了什么角色，影响了无dnsmasq中的哪些因素？
大概看了一下dnsmasq，简短一点介绍，它是一个dns缓存器。

启动的时候加载了`/etc/resolv.conf`（获取dns upstream server）和`/etc/hosts`（获取本地dns记录，其实应该叫主机名解析记录，不过也可以用作dns劫持用，而且这里讨论的是dns解析问题，所以这里就以dns记录来表述）。

了解到这里，就意识到，`/etc/hosts`是否是热加载的呢？**会不会是因为不是热加载导致了`/etc/hosts`的修改并没有在`dnsmasq`中生效？**

于是查看了一下文档，发现确实`dnsmasq`对`/etc/hosts`默认不是热加载，如果需要热加载，需要增加启动选项`--hostsdir`指向一个单独的hosts文件所在的目录。并且`dnsmasq`的`no-hosts`选项可以控制`dnsmasq`是否加载hosts文件。

看到这里就去nginx服务器上确认了一下，发现并没有禁止hosts文件加载，并且也没有指向其他的hosts热加载目录

分析到这里，按照逻辑来讲，可能就是上面说的原因。

但是，还有一个问题。前面的假设是所有的dns解析请求是通过`dnsmasq`，因为`/etc/resolv.conf`中指向了本机的`dnsmasq`，那么按照上面的原因推断的话，这台服务器上所有的程序（不仅仅是nginx）访问A域名都会是同样的解析现象。**但是实际情况是，使用`ping`命令来测试A域名的解析时，就是`/etc/hosts`中的结果。**

那么现在就到了第一个问题了，linux中的进程在进行dns解析时，`dnsmasq`、`/etc/hosts`和`/etc/resolv.conf`在里面到底是按照什么逻辑来生效和互相影响的？

#### 第二个问题，linux中的进程是如何进行dns解析过程的？
详细的内容见[linux中的dns解析是如何工作的](/linux/advance/dns_00_how_dns_work_in_linux.html)。

简短的介绍就是，使用C库中`gethostbyname`和其相关functions来做DNS解析时，是按照`NSS(/etc/nsswitch.conf)`中配置的`hosts: files dns`来确定本地DNS解析记录(`/etc/hosts`)和DNS服务器(`/etc/resolv.conf`和`dnsmasq`)的生效顺序，且只要优先度高的解析方式获取到了记录，剩下的解析方式就不会执行。

> 这就是为什么`ping`可以解析`/etc/hosts`的DNS记录，但是`nslookup`无法解析`/etc/hosts`的DNS记录的原因，也是因为这个原因，导致了上面的误判(通过`nslookup`来检测域名解析，推断`/etc/hosts`的修改未生效)。其实不止`nslookup`，`host`和`dig`都是直接向DNS服务器发请求，而不会解析`/etc/hosts`中的记录。

那么问题就很明了了，nginx服务器上的NSS配置是`hosts: files dns myhostname`，那么理论上当使用`gethostbyname`和其他相关functions的程序做DNS解析时候，`/etc/hosts`是第一顺位的解析方式。

如果以上的推导和求证没问题的话，到这里就出现了矛盾：**nginx的DNS解析，理论上`/etc/hosts`应该生效，但是实际上没有生效**

此时就有两个可能：
- 还有其他影响DNS解析的因素未被考虑进来
- nginx和`nslookup`类似，无法解析/etc/hosts中的记录（但这个可能性太小，以前做过很多hosts解析，如果这个假设成立，那么我早就发现这个问题了）

于是先排查第一个可能，仔细检查了nginx的配置，发现了这样的一个配置
```
resolver 127.0.0.1 ipv6=off valid=300s;
```
> [nginx docs: resolver](http://nginx.org/en/docs/http/ngx_http_core_module.html#resolver)

**破案了，之所以修改了`/etc/hosts`的方案未生效（service通过nginx代理访问A域名依旧有问题），是因为nginx的这个配置跳过了`/etc/hosts`而直接使用了DNS服务器(dnsmasq)来做dns解析。**

### 总结
三个需要注意的点：
- 需要了解linux中dns解析参与的因素及其顺序，重点是理解NSS
- 需要了解`nslookup`、`dig`、`hosts`无法解析`/etc/hosts`中的本地DNS记录，可以用`ping`或者`getent hosts`
- 需要了解`dnsmasq`的基本配置