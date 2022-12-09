---
title: 网络: TCP - RST简介
date: 2022-12-09 21:24:00
categories: linux/advance
tags: [linux,tcp]
---
> 主要参考资料：[不恰当的RST是有害的](https://www.ietf.org/rfc/rfc3360.html)

## 0. 前提
探究TCP的RST状态之前，确保你对TCP的三次握手和四次挥手有一个基本的了解。[linux的三次握手和四次挥手浅谈](/linux/advance/network_tcp-handshake-and-close.html)

## 1. TCP状态RST
### 1.1 RST是什么？以及它的用途是什么？
RST(reset)是TCP头部中的一个标记位，用于重置一个tcp连接。恰当的做法是，接收端收到了一个对不存在的tcp连接的请求，tcp返回RST给请求方，告诉对方取消这次访问。

所以基本上的理解是，如果收到或者发送了一个RST，代表的基本上是，一个tcp连接已经关闭了，但是双方有一端因网络问题未同步到tcp连接已经关闭的状态，或者这个tcp连接关闭前的一个tcp包在tcp连接后延迟收到，为了快速同步状态，有一端主动回应RST告诉对方，之前的连接已经关闭了，如果还想通话，那么请开启一个新的请求。

### 1.2 RST的实际应用情况
根据[不恰当的RST是有害的](https://www.ietf.org/rfc/rfc3360.html)中的说法，若抓包时，发现SYN的返回是一个RST，有时候可能是因为防火墙或者负载均衡使用了不恰当的RST的实现。大白话的意思就是，本来RST只是用于收到一个对不存在的tcp连接的请求的一个恰当回应用途，但是有些实现曲解了它的用途，将它用于对SYN握手的拒绝用途使用。所以实际RST的原因，需要抓包来观察。

### 1.3 其他RST需要注意的地方
[不恰当的RST是有害的](https://www.ietf.org/rfc/rfc3360.html)中还详细介绍了RST的历史，特别值得去看，会加深对RST的理解。