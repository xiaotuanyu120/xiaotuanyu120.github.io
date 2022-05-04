---
title: podman config: 系统资源限制
date: 2016-08-23 03:04:00
categories: virtualization/container
tags: [rlimit,podman]
---

## 0. linux系统资源限制简介
单台计算机的资源不可能是无限的，所以linux系统需要对资源进行限制。linux系统中对系统资源的限制设定，提供了三个系统调用
- setrlimit，设定当前进程的rlimit
- getrlimit，设定当前进程的rlimit
- prlimit，update指定pid的进程的rlimit

> 资源限制分为soft limit和hard limit。只有root可以调高hard limit，其他用户可以调整soft limit和hard limit，但无法将其设定为超过hard limit的数值。

## 1. podman（cgroup manager: systemd）
使用podman的rootless模式启动容器时，配置文件是`~/.config/containers/containers.conf`
```
[containers]
default_ulimits = [
 "nproc=65535:65535",
 "nofile=65535:65535",
]
```
> 这里设定的值，不可以高于运行容器普通用户的自身资源限定值