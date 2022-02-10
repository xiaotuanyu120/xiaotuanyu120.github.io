---
title: docker-compose 2.2.0 resource limit without swarm
date: 2020-07-24 10:18:00
categories: virtualization/docker
tags: [docker,docker-compose]
---

### 0. docker运行容器时进行resource limit的注意点
1. 给容器做了resource limit，在容器内运行`free -h`和`top`显示的是宿主机的资源而不是容器的资源
2. 容器中的JVM不会意识到它在容器内运行，所以只能手动分配JVM内存或者自动化这个手动过程
3. `docker -m 100m`会分配100m内存和100m swap空间，所以一共给程序200m的内存空间（当然，你可以手动用`-memory-swap`指定swap空间大小）

为了解决上面提到的问题，无论用什么方式，其实都是集中在如何给JVM传入内存限制的参数，而不是采用JVM的默认值（不同jdk版本，不同策略）

> [redhat-developer-java-inside-docker](https://developers.redhat.com/blog/2017/03/14/java-inside-docker/)

### 1. docker compose里面的resource limit实现
version 3中使用resources替代了之前的[资源限制选项](https://docs.docker.com/compose/compose-file/compose-file-v2/#cpu-and-other-resources)。version 3对于resources limit的实现增加了几个限定条件，1. 只能在docker stack或者swarm模式启动；2. 只能限制cpu和mem这两项。如果想在docker-compose上使用resource limit，只能选择退回到version2.1或者使用`--compatibility`。
``` yaml
version: "3.8"
services:
  redis:
    image: redis:alpine
    deploy:
      resources:
        limits:
          cpus: '0.50'
          memory: 50M
        reservations:
          cpus: '0.25'
          memory: 20M
```

> [docker-compose - deploy - resources](https://docs.docker.com/compose/compose-file/#resources)

> [v3版本的`--compatibility` 解决非swarm模式的不生效问题](https://github.com/docker/compose/issues/4513)

> `reservations`意味着硬性的保留这些资源，专用于这个容器；`limits`意味着容器申请的资源，不能超过这个限制。