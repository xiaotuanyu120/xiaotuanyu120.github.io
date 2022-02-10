---
title: php 1.3.0: 性能调优 - backlog
date: 2015-12-10 17:24:00
categories: service/php
tags: [php,linux,nginx]
---

### 1. backlog（影响并发数目）
backlog的意思是，超出目前程序对于请求处理能力最大值，之后可以准许排队的请求数量。对于linux+nginx+php的组合来讲，需要合理的搭配这三者的处理能力（处理中的连接数最大值+backlog排队数值），综合调优。

nginx的backlog配置(nginx.conf)
```
listen 80  backlog=8192;
listen 443 backlog=8192;
```
> 默认值`-1`，即处理中的连接队列满了就拒绝; 处理中的连接队列最大值请查看`worker_connections`配置

> PS: `最大连接数`+`backlog`不能一味追求过大，要考虑后端php的处理能力，也要考虑linux系统的资源情况（主要是内存）

php-fpm的backlog配置(php-fpm.conf)
```
listen.backlog = 8192
```
> 关于此配置的默认值，可以打开默认配置文件查看(5.6.40版本是65536);关于处理中的连接队列最大值请查看[php进程管理配置说明](/service/php/php_1.2.2_configuration_process.html)

> PS: php-fpm的backlog不能一味追求大，需要看硬件处理水平而定。
> - 如果`最大进程数`+`backlog`设置过大，php的处理性能跟不上，超出了nginx等待时间，则会返回504，而php会报错broken pipeline
> - 如果`最大进程数`+`backlog`设置过小，nginx的请求过多，则会返回502

linux系统内核配置(/etc/sysctl.conf)
```
# 系统全局参数：每一个listen() socket的最大backlog上限
net.core.somaxconn = 655360

# 每个网络接口，允许后台排队队列数据包的最大数目
net.core.netdev_max_backlog = 1048576

# 尚未收到客户端确认信息的连接请求的最大值
net.ipv4.tcp_max_syn_backlog = 1048576
```

查看效果
``` bash
# 修改完之后检查状态
ss -ln
State      Recv-Q Send-Q        Local Address:Port          Peer Address:Port
LISTEN     0      8192              127.0.0.1:9000                     *:*
LISTEN     0      8192                      *:80                       *:*
```

---

### 2. 系统环境优化
除了backlog是为了应对突发能力的额外队列之外
- 因为每个tcp连接都是一个文件，所以需要优化系统的最大文件打开数
- 还因为系统对进程数量有限制，还需要优化系统的进程数量上限。

此处的配置，可以参考[linux limit 配置](/linux/advance/linux_optimize_ulimit.html)