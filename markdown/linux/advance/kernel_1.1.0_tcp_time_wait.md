---
title: 内核调优: 1.1.0 优化TCP来解决TIME_WAIT状态过多
date: 2017-02-07 16:56:00
categories: linux/advance
tags: [linux,tcp,time_wait]
---

### 1. 关于TIME_WAIT
#### 1) 什么是TIME_WAIT?
TIME_WAIT是TCP连接中的一个状态，每一个TCP连接都会在内存中维护一个控制块TCB(Transmission Control Block），用来记录TCP连接的IP和端口等信息。TIME_WAIT状态会维持一小段时间(最大分段使用期的2倍，2MSL)，以确保这段时间内不会有相同的IP和端口号的新连接，目的是为了预防，上一个连接的分组包延迟到达，而被新的连接接受而导致TCP流被破坏。  
但是处于TIME_WAIT状态的TCP连接过多也会造成性能问题，比如我们的可用源端口只有60000个，而在2MSL(Maximum Segment Lifetime, 时间根据不同系统不一样，大概2分钟左右)内是无法被重用的，也就是说我们的tcp连接率就限制在了在60000/120 = 500次/秒。  
即使没有遇到端口耗尽的问题，在有大量TCP连接及TCB占用内存比例过大时，也会严重影响系统的性能。  

#### 2) TIME_WAIT的用处
- 避免延迟的tcp片段被新的不相干的tcp连接接收，由此新的tcp连接遭到破坏
- 保证TCP四次挥手中的最后一个ACK能顺利到达，若最后一个ACK丢失，当再次使用同一个端口上发起SYN时，则对方的LAST_ACK状态会返回RST。


### 2. 计算TCP并发数
因为每一个tcp连接是由<local-ip>:<local-port> <remote-ip>:<remote-port>确定的，此处限定<local-ip>,<remote-ip>,<remote-port>三项不变，只有<local-port>一个变量的情况下的tcp并发计算方法
``` bash
# 查看可用端口数目
cat /proc/sys/net/ipv4/ip_local_port_range
32768	60999

# TIME_WAIT状态tcp存活时间，默认是2倍的MSL，在linux内核源码中，这个值是个常量TCP_TIMEWAIT_LEN=60s，是不可以改变的。

# 计算tcp并发数
echo "(60999-32768)/60"|bc
470
```


### 3. TCP针对TIME_WAIT过多可以进行的优化
#### 1) 增加可用的端口范围
根据上面的tcp并发算法能看出来，针对于同一个服务端口，tcp并发随着可用的端口范围的增加而增加。

#### 2) 使用不同的服务端口来提供服务
所谓tcp连接，是由<local-ip>:<local-port> <remote-ip>:<remote-port>四段确定的一个tcp连接，在不考虑其他三段的情况下，监听一个80和同时监听80和81，能提供的tcp并发理论上直接是相差了一倍

#### 3) 对tcp进行优化(做这些优化前，确认知道这些优化的含义)
``` bash
vim /etc/sysctl.conf
***************************************
# 启用tcp的时间戳配置，只有启用这个，下面reuse和recycle才生效。
net.ipv4.tcp_timestamps = 1

# 允许TIME_WAIT SOCKETS重新用于新的TCP连接，依赖开启tcp优化中的tcp_timestamp
# tcp_tw_reuse - INTEGER
# 	  Enable reuse of TIME-WAIT sockets for new connections when it is
# 	  safe from protocol viewpoint.
# 	  0 - disable
# 	  1 - global enable
# 	  2 - enable for loopback traffic only
# 	  It should not be changed without advice/request of technical
# 	  experts.
# 	  Default: 2
net.ipv4.tcp_tw_reuse = 1

# ！！！网上很多人转载这个，但是这个配置不要用于nat网络里面，详情可以自己谷歌此配置和nat关键字！！！
# 开启TCP连接中的TIME_WAIT SOCKETS快速回收，依赖开启tcp优化中的tcp_timestamp
net.ipv4.tcp_tw_recycle = 1
# ！！！nat网络下不建议开！！！

# 修改FIN_WAIT2状态tcp的超时时间为30s，默认等于TCP_TIMEWAIT_LEN，是60s
# tcp_fin_timeout - INTEGER
# 	  The length of time an orphaned (no longer referenced by any
# 	  application) connection will remain in the FIN_WAIT_2 state
# 	  before it is aborted at the local end.  While a perfectly
# 	  valid "receive only" state for an un-orphaned connection, an
# 	  orphaned connection in FIN_WAIT_2 state could otherwise wait
# 	  forever for the remote to close its end of the connection.
# 	  Cf. tcp_max_orphans
# 	  Default: 60 seconds
net.ipv4.tcp_fin_timeout = 30
***************************************

# 使配置立即生效
sysctl -p
```


### 3. 扩展连接
- [sysctl configuration in linux kernel docs](https://www.kernel.org/doc/Documentation/networking/ip-sysctl.txt)，这里面可以查看sysctl每一项优化的官方文档说明
- [RFC 793: TCP](https://tools.ietf.org/html/rfc793)，这里可以查看TCP的相关原理说明
- [RFC 6191: 采用tcp timestamp来降低TIME_WAIT的设计说明](https://tools.ietf.org/html/rfc6191#page-3)
- [TIMEWAIT精品文章 - 强烈推荐](https://vincent.bernat.ch/en/blog/2014-tcp-time-wait-state-linux#fn-outgoing)