---
title: linux内核: listen()中的backlog
date: 2015-12-10 16:06:00
categories: linux/advance
tags: [linux,kernel]
---

## 0. listen()的backlog含义？
listen man文档中的description：

```
listen() marks the socket referred to by sockfd as a passive socket, that is, as a socket that will be used to accept incoming connection requests using accept(2).
The sockfd argument is a file descriptor that refers to a socket of type SOCK_STREAM or SOCK_SEQPACKET.
 
The backlog argument defines the maximum length to which the queue of pending connections for sockfd may grow. If a connection request arrives when the queue is full, the client may receive an error with an indication of ECONNREFUSED or, if the underlying protocol supports retransmission, the request may be ignored so that a later reattempt at connection succeeds.
```

总结来说，由backlog定义了等待连接（因为连接已经达到上限）的队列的长度。每个socket开始调用listen()时，系统会分配一个backlog参数给socket。如果等待连接的请求数超过了这个最大值，会返回给客户端一个ECONNREFUSED。

简单的一个比喻就是，socket是一个餐厅，listen()相当于开始营业的动作，餐厅内部最多可以招待一定数量的客人（accept()处理的最大的连接数）。然后当餐厅满了，后面的客人可以在餐厅外排队，这个队伍的长度由backlog来定义，队伍超过最大长度后，服务员会直接拒绝后面的客人继续排队。

## 1. backlog的长度限制
可以通过调整下面参数来调整

``` bash
net.core.somaxconn = 655360
```

但是从linux 2.2开始，backlog变更为指定已建立的等待accept的套接字队列长度，而不再是未完全建立连接的请求。未完全建立连接的请求的队列长度需要通过`/proc/sys/net/ipv4/tcp_max_syn_backlog`来指定。
> 但是当syncookies启用时，上面这个配置会被忽略，不会存在syn队列的最大长度。

``` bash
net.core.netdev_max_backlog = 1048576
# 每个网络接口，允许后台排队队列数据包的最大数目

net.ipv4.tcp_max_syn_backlog = 1048576
# 尚未收到客户端确认信息的连接请求的最大值
```