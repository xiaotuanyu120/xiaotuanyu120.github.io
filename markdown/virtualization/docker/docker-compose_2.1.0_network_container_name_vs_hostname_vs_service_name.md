---
title: docker-compose 2.1.1 network: container_name vs hostname vs service name
date: 2020-09-18 15:51:00
categories: virtualization/docker
tags: [docker,docker-compose]
---

### 0. docker-compose 默认网络
- container_name: 仅用于替代默认生成的容器名称
- hostname： 仅用于改变容器内部的hostname，并不影响容器外的使用。在使用`hostname`和`bash`命令时可以看得出效果，另外有些软件的集群是依赖hostname的，例如rabbitmq。
- service name: 用于在bridge网络中，充当互相调用的name（感觉就是docker run --name这个选项）

> 正常情况下，service name 和`docker run --name`中[命名规则](https://docs.docker.com/engine/reference/run/#name---name)一致，就是`字母`加上`下划线`，但是如果是在spring的容器中，可能`下划线`会导致容器的相互调用出问题，详情见[这个例子](https://stackoverflow.com/questions/51632753/spring-boot-rest-app-returns-400-when-requested-from-other-docker-compose-servic)


参考文档：
- [docker network](https://docs.docker.com/network/)
- [docker --links](https://docs.docker.com/network/links/)
- [Differences between user-defined bridges and the default bridge](https://docs.docker.com/network/bridge/#differences-between-user-defined-bridges-and-the-default-bridge)
- [docker compose network](https://docs.docker.com/compose/networking/)
- [docker run --name](https://docs.docker.com/engine/reference/run/#name---name)