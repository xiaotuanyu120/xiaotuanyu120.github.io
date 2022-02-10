---
title: docker-compose 2.1.0 network
date: 2019-09-30 13:00:00
categories: virtualization/docker
tags: [docker,docker-compose]
---

### 0. docker-compose 默认网络
在没有指定加入网络的情况下，docker-compose会默认创建一个网络，重点概括如下：
- yaml文件所在的目录`<folder_name>`是一个project
- docker-compose创建的默认网络是`<folder_name>_default`
- 在同一个网络中的容器，网络可以互通，互相使用`service_name`当做对方的`hostname`
- 在同一个网络中的容器，可以互相访问对方的`容器端口`，而不必要去使用对方的`主机端口`

### 1. docker-compose 指定网络
可以使用`networks`这个顶级key来创建网络，然后在各个service里面使用`networks`来指定service加入的网络。当然，也可以不使用`networks`顶级key创建网络，直接在service里面指定要加入的非docker-compose创建的网络。

下面这个例子中，proxy因为不需要访问db，所以只和app在同一个网络中，而app则同时处于proxy和db所在的网络中
``` yaml
version: "3"
services:

  proxy:
    build: ./proxy
    networks:
      - frontend
  app:
    build: ./app
    networks:
      frontend:
        aliases:
          - upstream
          - alias2
      backend:
        aliases:
          - db-client
  db:
    image: postgres
    networks:
      backend:
      db_net:
        ipv4_address: 172.16.238.10
        ipv6_address: 2001:3984:3989::10

networks:
  frontend:
    # Use a custom driver
    driver: custom-driver-1
  backend:
    # Use a custom driver which takes special options
    driver: custom-driver-2
    driver_opts:
      foo: "1"
      bar: "2"
  db_net:
    driver: bridge
    enable_ipv6: true
    ipam:
      driver: default
      config:
      - subnet: 172.16.238.0/24
        gateway: 172.16.238.1
      - subnet: 2001:3984:3989::/64
        gateway: 2001:3984:3989::1
```
> 注意以下两项配置：
> - aliases: 在不同网络中，给每个service设定多个hostname
> - ipv4&ipv6的地址配置和地址指定

### 2. docker-compose 自定义默认网络
如果你的project还是全部在同一个网络中，你只是想改动默认网络的部分配置，可以按照下面的方式
``` yaml
version: "3.5"
services:

  web:
    build: .
    ports:
      - "8000:8000"
  db:
    image: postgres

networks:
  default:
    # Use a custom driver
    name: default_network
    driver: custom-driver-1
```

如果想把外部网络拿来当成默认网络，可以这样使用
``` yaml
networks:
  default:
    external:
      name: my-pre-existing-network
```