---
title: ftp: 1.0.0 ftp是什么？
date: 2015-01-22 02:54:00
categories: service/ftp
tags: [ftp]
---
### ftp: 1.0.0 ftp是什么？

### 1. FTP简介
介绍：  
文件传输协议（英文：File Transfer Protocol，缩写：FTP）是用于在网络上进行文件传输的一套标准协议。

使用端口：  
- 命令通道-port 21
- 数据传输-port 20

ftp缺点
1. 明文传输（被sftp改善）
2. 防火墙存在时的响应困难（被主动被动模式的区分改善）
3. 稳定性差，传大量小文件时易断线，需要工具支持才能断点续传
