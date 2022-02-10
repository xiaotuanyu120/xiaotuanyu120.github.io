---
title: 4.0.2 docker 本地registry push时一直retrying
date: 2020-04-02 16:40:00
categories: virtualization/docker
tags: [docker,registry]
---

### 0. 问题背景
搭建了一个本地registry，因为80端口被占用，所以用了81端口。当程序正常运行后，push镜像时遇到了下面的问题
```
The push refers to repository [reg.blablabla.com:81/base-dind-build]
a0009f5c5ca2: Pushing [==================================================>]  317.3MB
bebe768ef6e0: Pushing [==================================================>]   7.68kB
0ae97136c06b: Pushing [==================================================>]  4.608kB
d91ebd273e7f: Pushing [==================================================>]  13.82kB
c5cdaed0fa41: Pushing [==================================================>]  14.24MB
763b860aaaad: Pushing [==================================================>]  4.608kB
08a26357a53e: Pushing [==================================================>]  4.096kB
7648c0c6495d: Retrying in 6 seconds 
e0a42524f665: Pushing [==================================================>]   2.56kB
05540d8bb3fd: Retrying in 1 second 
1bfeebd65323: Retrying in 2 seconds 
blob upload unknown
```

### 1. 解决方法
增加一个环境变量`REGISTRY_HTTP_HOST=http://extreg.blablabla.com:81`
``` yaml
  reg:
    image: 'registry:2'
    container_name: reg
    restart: always
    environment:
      - REGISTRY_HTTP_HOST=http://extreg.blablabla.com:81
    volumes:
      - '/data/docker/data/reg:/var/lib/registry'
```
- [github issues answer](https://github.com/docker/distribution/issues/2042#issuecomment-606753339)