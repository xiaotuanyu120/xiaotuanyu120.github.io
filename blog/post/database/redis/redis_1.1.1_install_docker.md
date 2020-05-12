---
title: redis: 1.1.1 docker-redis
date: 2020-05-12 10:49:00
categories: database/redis
tags: [database,redis,docker]
---
### redis: 1.1.1 docker-redis

---

### 1. docker-compose yaml
``` yaml
version: '3'
services:
  redis:
    image: redis:3.2.12
    container_name: redis
    command: ["redis-server", "/usr/local/etc/redis/redis.conf"]
    volumes:
      - "/path/to/redis/data:/data"
      - "/path/to/redis/log:/var/log/redis"
      - "/path/to/reids/redis.conf:/usr/local/etc/redis/redis.conf"
```

### 2. 配置注意点
- `bind 0.0.0.0`，保证其他容器可以访问
- `logfile /var/log/redis/redis_6379.log`，日志路径和上面挂载的日志volumes`/var/log/redis`要统一
- `daemonize no`，不能后台daemon执行，docker需要`command: ["redis-server", "/usr/local/etc/redis/redis.conf"]`一直前台执行
- `dir /data`，需要和数据volumes`/data`保持一致
- `requirepass redispass`，redis官方容器默认是关闭了protechtion模式，所以推荐设定密码保证安全性