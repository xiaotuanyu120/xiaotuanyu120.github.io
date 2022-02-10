---
title: container 1.1.1 java encoding and container locale
date: 2020-05-15 14:29:00
categories: virtualization/container
tags: [container,docker,java]
---

### 1. 问题
使用debian:buster-slim为base的镜像，增加了oracle的jdk和spring boot的项目，启动后发现日志中中文是乱码

### 2. 解决办法
首先尝试了网上的各种办法，整理了一下，无非两种
- JVM参数
- 容器环境的locale（修改Dockerfile，增加ENV LANG=xxx）

locale知识背景
```
# debian系的系统
# 列出当前系统设定的locale
locale

# 列出当前系统可用的locale
locale -a
C
C.UTF-8
POSIX
```

因为容器环境中没有en_US和zh_CN，所以还尝试了下如何增加locale可用的地区，需要使用下面的locale-gen命令
```
    apt-get update && apt-get install -y locales && rm -rf /var/lib/apt/lists/* \
    echo "zh_CN.UTF-8 UTF-8" > /etc/locale.gen && locale-gen
```

但是后面仔细考虑一下，之所以中文有乱码，和地区其实关系不大，按理说只要是UTF8即可，所以使用下面的命令组合
```
ENV LANG=C.UTF-8

CMD "java -jar xxx.jar -Djavax.servlet.request.encoding=UTF-8 -Djavax.servlet.response.encoding=UTF-8 -Dfile.encoding=UTF-8 -Dsun.jnu.encoding=UTF-8 -Duser.language=zh -Duser.country=CN"
```
> - 网上大部分教程都是说只需要修改默认的encoding即可`-Dfile.encoding=UTF-8`，但是我测试不行
> - 