---
title: 1.2.4 docker容器安装microsoft truetype 字体
date: 2019-09-26 13:08:00
categories: virtualization/docker
tags: [docker]
---

### 0. 问题背景
java工程运行某些情况需要微软的truetype字体支持，例如某些验证码的显示

### 1. 解决方案
```
# debian作为底层镜像时
RUN apt-get update; \
    apt-get install ttf-mscorefonts-installer

# alpine作为底层镜像时
RUN apk --no-cache add msttcorefonts-installer fontconfig && \
    update-ms-fonts && \
    fc-cache -f
```