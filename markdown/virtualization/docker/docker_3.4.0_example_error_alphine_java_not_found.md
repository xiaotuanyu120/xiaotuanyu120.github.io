---
title: 3.4.0 alpine oracle java no such file or directory error
date: 2020-04-14 14:02:00
categories: virtualization/docker
tags: [docker,alpine,java]
---

### 0. 背景
使用dind，然后想要编译java工程，结果导入进去oracle的jdk竟然提示no such file or directory

WHAT?

结果搜到了这个[stackoverflow answer](https://stackoverflow.com/questions/45147371/docker-alpine-oracle-java-cannot-find-java/45147882)

### 1. 实际解决办法
照抄，那是肯定失败的，预计经过改造如下
``` yaml
RUN apk --no-cache add ca-certificates && \
    wget -q -O /etc/apk/keys/sgerrand.rsa.pub https://raw.githubusercontent.com/sgerrand/alpine-pkg-node-bower/master/sgerrand.rsa.pub && \
    wget https://github.com/sgerrand/alpine-pkg-glibc/releases/download/2.25-r0/glibc-2.25-r0.apk && \
    apk add glibc-2.25-r0.apk
```