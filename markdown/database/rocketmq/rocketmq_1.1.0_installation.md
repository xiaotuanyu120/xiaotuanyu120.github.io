---
title: rocketmq 1.1.0 安装
date: 2020-12-22 12:03:00
categories: database/rocketmq
tags: [database,rocketmq]
---

### 1. rocketm容器安装
``` bash
# step 1. 本地编译镜像
git clone https://github.com/apache/rocketmq-docker.git
cd rocketmq-docker/image-build
# sh build-image.sh RMQ-VERSION BASE-IMAGE
# RMQ-VERSION: https://archive.apache.org/dist/rocketmq/
# BASE-IMAGE: centos,alpine
sh build-image.sh 4.7.1 alpine

# step 2. 准备docker-compose.yml文件
echo "version: '2'
services:
  namesrv:
    image: apacherocketmq/rocketmq:4.7.1-alpine
    container_name: rmqnamesrv
    ports:
      - 9876:9876
    volumes:
      - /data/docker/data/rocketmq/namesrv/logs:/home/rocketmq/logs
    command: sh mqnamesrv
  broker:
    image: apacherocketmq/rocketmq:4.7.1-alpine
    container_name: rmqbroker
    ports:
      - 10909:10909
      - 10911:10911
      - 10912:10912
    volumes:
      - /data/docker/data/rocketmq/broker/logs:/home/rocketmq/logs
      - /data/docker/data/rocketmq/broker/store:/home/rocketmq/store
      #- /data/docker/runtime/rocketmq/broker.conf:/home/rocketmq/rocketmq-4.7.1/conf/broker.conf
    command: sh -x mqbroker -n namesrv:9876 -c ../conf/broker.conf
    depends_on:
      - namesrv" > docker-compose.yml

# step 3. 修改文件权限
# issue: https://github.com/apache/rocketmq-externals/issues/267
chown -R 3000.3000 /data/docker/data/rocketmq/*
chown -R 3000.3000 /data/docker/runtime/rocketmq/*

# step 4. 启动rocketmq
docker-compose up -d
```

### 2. 如何手动配置jvm
```
environment:
  - MAX_HEAP_SIZE=8192
```
[broker customize scripts](https://github.com/apache/rocketmq-docker/blob/master/image-build/scripts/runbroker-customize.sh)