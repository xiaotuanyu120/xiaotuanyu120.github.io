---
title: 内核调优: 1.1.2 TIMEWAIT销毁时间是否可以通过tcp_fin_timeout优化？
date: 2019-08-21 14:56:00
categories: linux/advance
tags: [linux,tcp,time_wait,fin_timeout]
---

### 1. 关于TIMEWAIT
参见[TIMEWAIT优化篇](/linux/advance/optimize_1.1.0_kernel_tcp_time_wait.html)


### 2. 关于MSL
优化TIMEWAIT的方法中，有一种论调是在tcp优化时，因为TIMEWAIT的存活时间是2MSL，所以我们需要缩短MSL来达到快速回收TIMEWAIT状态的tcp的目的。  
那么这里引出几个问题，MSL在linux中，是否可以调优？网上普遍流传的tcp_fin_timeout是否可以控制MSL的时间长短呢？

#### 1) 关于MSL是否可以调优
首先，我们的目的是要调优TIMEWAIT，因此，才会关注MSL这个时间。而在linux的内核源码的[tcp.h](https://github.com/torvalds/linux/blob/master/include/net/tcp.h)中，有这样一段
``` c
#define TCP_TIMEWAIT_LEN (60*HZ) /* how long to wait to destroy TIME-WAIT
				  * state, about 60 seconds	*/
```
这里可以看出，TIMEWAIT的销毁时间，是由TCP_TIMEWAIT_LEN来控制的，而其是个常量，是60s，是无法被调优的。


#### 2) 网上为何流传tcp_fin_timeout是2MSL呢？
**个人猜测**是两个原因:
- 第一是因为默认情况下，TCP_FIN_TIMEOUT就等于TCP_TIMEWAIT_LEN
``` c
#define TCP_FIN_TIMEOUT	TCP_TIMEWAIT_LEN
                                 /* BSD style FIN_WAIT2 deadlock breaker.
				  * It used to be 3min, new value is 60sec,
				  * to combine FIN-WAIT-2 timeout with
				  * TIME-WAIT timer.
				  */
```
- 第二是因为，tcp_fin_timeout本身就是设定处于FIN_WAIT2状态下的tcp连接等待最后一个FIN的超时时间，这个超时时间越短，就越快加速等不到FIN的情况下FIN_WAIT2到下一步的过程，也是能一定程度上加快tcp的生命周期，所以才和TIMEWAIT的销毁时间等同来讲。

> 以上两个原因，都是个人猜测，个人猜测，请在未验证之前，不要拿来作为依据。


### 3. 验证一波fin_timeout和TIMEWAIT的销毁时间确实没关系
``` bash
# 1. 搭建一个tomcat，用于测试，此处忽略

# 2. 首先设定fin_timeout为一个极短的时间
echo "3" > /proc/sys/net/ipv4/tcp_fin_timeout
# 验证一下
cat /proc/sys/net/ipv4/tcp_fin_timeout
3

# 3. curl一下tomcat，创建几个tcp连接
curl 127.0.0.1:8080 -I

# 4. 使用ss检查处于timewait状态的连接，使用-o来检查其时间
ss -n -o state time-wait
Netid  Recv-Q Send-Q Local Address:Port               Peer Address:Port              
tcp    0      0      127.0.0.1:42924              127.0.0.1:8080                timer:(timewait,55sec,0)
tcp    0      0      127.0.0.1:42922              127.0.0.1:8080                timer:(timewait,54sec,0)
# 发现初始化时间就是60s
# 再次检查，发现时间减少，直到时间为0，tcp连接消失
ss -n -o state time-wait
Netid  Recv-Q Send-Q Local Address:Port               Peer Address:Port              
tcp    0      0      127.0.0.1:42924              127.0.0.1:8080                timer:(timewait,34sec,0)
tcp    0      0      127.0.0.1:42922              127.0.0.1:8080                timer:(timewait,33sec,0)
```
> 以上的操作实际上验证了，修改`tcp_fin_timeout`是无法修改TIMEWAIT的销毁时间的。