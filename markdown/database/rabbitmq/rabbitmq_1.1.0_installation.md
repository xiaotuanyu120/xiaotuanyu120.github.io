---
title: rabbitmq 1.1.0 安装
date: 2021-01-30 20:23:00
categories: database/rabbitmq
tags: [database,rabbitmq]
---

### 1. rabbitmq容器安装
``` bash
# step 1. 修改文件权限
# root 运行模式
chown -R 100.101 /path/to/dir/on/host/should/mounted/to/container
# rootless 运行模式
podman unshare chown -R 100.101 /path/to/dir/on/host/should/mounted/to/container

# step 2. 启动rocketmq
podman run -it -d --hostname rabbitmq --name rabbitmq \
  -p 5672:5672 \
  -p 15672:15672 \
  -e RABBITMQ_DEFAULT_USER_FILE=/etc/rabbitmq/pass/username \
  -e RABBITMQ_DEFAULT_PASS_FILE=/etc/rabbitmq/pass/password \
  -e RABBITMQ_DEFAULT_VHOST=vhost01 \
  -v /path/to/pass:/etc/rabbitmq/pass:ro \
  -v /path/to/data:/var/lib/rabbitmq \
  rabbitmq:3.7.28-management-alpine
```
> - `hostname`，rabbitmq根据nodename来保存数据，默认的nodename就是hostname
> - `RABBITMQ_DEFAULT_USER_FILE`和`RABBITMQ_DEFAULT_PASS_FILE`指定的是默认的用户和密码保存的文件路径
> - `RABBITMQ_DEFAULT_VHOST`，默认的vhost是`/`，可以通过这个值修改，上例中默认的vhost即为`/vhost01`