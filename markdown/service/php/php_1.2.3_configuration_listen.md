---
title: php 1.2.3: PHP配置 - listen
date: 2016-01-14 14:34:00
categories: service/php
tags: [php]
---

### 1. 配置背景
以前都是把php和nginx放在同一个服务器上，所以php监听127.0.0.1没问题
如果要把php服务器单独起来的话，就需要做如下配置

---

### 2. 配置内容
1.把监听127.0.0.1改成对外IP
2.允许的client变成任意，默认配置是127.0.0.1

修改`php-fpm.conf`
```
# listen = 127.0.0.1:9000
listen = 0.0.0.0:9000
# listen.allowed_clients = 127.0.0.1
listen.allowed_clients = any
# or
listen.allowed_clients = 0.0.0.0
# or
listen.allowed_clients = 192.168.0.0/16,172.16.1.2,172.18.1.3
```
