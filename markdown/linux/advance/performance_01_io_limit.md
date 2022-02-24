---
title: performance: 限制进程的IO消耗
date: 2022-02-24 11:56:00
categories: linux/advance
tags: [ionice]
---

### 0. 前言
在管理线上服务器时，因为管理需要，可能要在业务服务之外，运行一些管理服务。如果不对管理服务加以限制，可能会出现管理服务和业务服务争抢计算机资源的情况，从而影响业务服务的正常运营，这样的话，增加管理服务就属于本末倒置了，毕竟管理服务的手段是希望能让业务服务更稳定的运行。

如果管理服务是IO消耗型的，比如定期大日志文件的打包，这时候就要从IO方面来进行限制了，限制了IO，CPU资源相应的就会降低。


### 1. 使用ionice来限制进程的IO消耗
ionice有三种限制模式，详情可见[ionice的man文档](https://linux.die.net/man/1/ionice)，我用自己的话简单的概括一下：
- Idle, 当其他进程没有对IO的请求时执行
- Best effort, 系统尽最大努力分配可用的IO资源
- Real time, 系统优先给IO资源，而不管其他进程的需求

上面三种模式可以用`-c`来指定，其中`0`代表none，`1`代表real time，`2`代表beft effort，`3`代表idle。

其中best effort和real time还可以用`-n 0-7`来指定程度，数字越低，优先级越高。

所以，可以用以下方式来给进程的IO资源消耗做限制

``` bash
# 给执行中的进程，pid为11111，增加限制
ionice -c 3 -p 11111

# 给即将要执行的命令增加限制
ionice -c 2 -n 7 tar Jcf ....
```