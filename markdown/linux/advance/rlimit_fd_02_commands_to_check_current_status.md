---
title: rlimit fd: 状态查看命令
date: 2022-05-01 22:05:00
categories: linux/advance
tags: [fd, rlimit]
---

### 0. fd(文件描述符)限制的项目说明 
- **`/proc/sys/fs/file-max`**是linux内核级别的设定，影响的是linux系统上所有进程可以打开的文件数上限
- **[`ulimit`](/linux/advance/rlimit_ulimit_01_introduce.html)**是用户或用户组级别，通过PAM登录的login shell，fork出的进程可以打开的文件数上限；
- **`/proc/sys/fs/file-nr`**是系统级别当前打开文件状态
- **`/proc/$pid/limits`**是指定进程的资源限制上限

> 参考文档:  
[ulimit设定的是每个进程的属性，而不是该用户所有进程的总限制](https://unix.stackexchange.com/questions/55319/are-limits-conf-values-applied-on-a-per-process-basis)  
[ulimit vs file-max](https://unix.stackexchange.com/questions/447583/ulimit-vs-file-max)  
[如何计算最大文件打开数应该设定多少](https://stackoverflow.com/questions/6180569/need-to-calculate-optimum-ulimit-and-fs-file-max-values-according-to-my-own-se)

### 1. 系统级别，文件打开数状态查看

``` bash
# 查看linux内核级别的文件描述符上限
cat /proc/sys/fs/file-max
97984

# 查看目前系统使用的文件描述符数量
cat /proc/sys/fs/file-nr
512 0 97984
# 512   -> 分配并使用的文件描述符数量
# 0     -> 分配却未使用的文件描述符数量
# 97984 -> 内核级别的最大文件描述符数量
```

### 2. 查看特定进程的最大文件打开数状态

``` bash
cat /proc/397/limits | grep "open files"
Max open files            2048                 2048                 files
```