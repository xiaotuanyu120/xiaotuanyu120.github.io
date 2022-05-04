---
title: systemd: 系统资源限制
date: 2016-08-23 03:04:00
categories: linux/advance
tags: [linux,fs-max,systemd]
---

## 0. linux系统资源限制简介
单台计算机的资源不可能是无限的，所以linux系统需要对资源进行限制。linux系统中对系统资源的限制设定，提供了三个系统调用
- setrlimit，设定当前进程的rlimit
- getrlimit，设定当前进程的rlimit
- prlimit，update指定pid的进程的rlimit

> 资源限制分为soft limit和hard limit。只有root可以调高hard limit，其他用户可以调整soft limit和hard limit，但无法将其设定为超过hard limit的数值。

## 1. systemd
systemd默认会有一个资源分配值，例如文件打开数的默认值是4096。可以通过修改systemd默认资源分配值或者单个unit文件配置资源分配值这两种方式来修改systemd启动的service的资源限制数值。
- `/etc/systemd/system.conf`：系统进程的默认限制
- `/etc/systemd/user.conf`：用户进程的默认限制

### 1) 修改systemd默认资源分配值
**systemd默认资源限制配置文件：`/etc/systemd/system.conf`**

```
#DefaultLimitCPU=
#DefaultLimitFSIZE=
#DefaultLimitDATA=
#DefaultLimitSTACK=
#DefaultLimitCORE=
#DefaultLimitRSS=
#DefaultLimitNOFILE=
#DefaultLimitAS=
#DefaultLimitNPROC=
#DefaultLimitMEMLOCK=
#DefaultLimitLOCKS=
#DefaultLimitSIGPENDING=
#DefaultLimitMSGQUEUE=
#DefaultLimitNICE=
#DefaultLimitRTPRIO=
#DefaultLimitRTTIME=
```
> 值得注意的是，大部分默认值没有设定。这意味着大部分的设定会继承自kernel，或者如果是容器启动，会继承自容器管理进程。但是也有几个例外，其中一个是`DefaultLimitNOFILE= defaults to "1024:524288".`
> 参考自[systemd-system.conf(5) manual](https://man7.org/linux/man-pages/man5/systemd-system.conf.5.html)

**system.conf重新加载命令**

``` bash
systemctl daemon-reexec
```

### 2) 修改systemd unit文件资源分配值
配置以下项目到unit文件的service配置块中

| Directive        | ulimit equivalent | Unit                       |
| ---------------- | ----------------- | -------------------------- |
| LimitCPU=        | ulimit -t         | Seconds                    |
| LimitFSIZE=      | ulimit -f         | Bytes                      |
| LimitDATA=       | ulimit -d         | Bytes                      |
| LimitSTACK=      | ulimit -s         | Bytes                      |
| LimitCORE=       | ulimit -c         | Bytes                      |
| LimitRSS=        | ulimit -m         | Bytes                      |
| LimitNOFILE=     | ulimit -n         | Number of File Descriptors |
| LimitAS=         | ulimit -v         | Bytes                      |
| LimitNPROC=      | ulimit -u         | Number of Processes        |
| LimitMEMLOCK=    | ulimit -l         | Bytes                      |
| LimitLOCKS=      | ulimit -x         | Number of Locks            |
| LimitSIGPENDING= | ulimit -i         | Number of Queued Signals   |
| LimitMSGQUEUE=   | ulimit -q         | Bytes                      |
| LimitNICE=       | ulimit -e         | Nice Level                 |
| LimitRTPRIO=     | ulimit -r         | Realtime Priority          |
| LimitRTTIME=     | No equivalent     | Microseconds               |

> [manual for systemd.exec](https://www.freedesktop.org/software/systemd/man/systemd.exec.html#Process%20Properties)