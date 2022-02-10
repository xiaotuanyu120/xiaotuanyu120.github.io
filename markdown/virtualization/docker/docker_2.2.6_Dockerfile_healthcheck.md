---
title: 2.2.6 Dockerfile healthcheck
date: 2020-10-08 13:17:00
categories: virtualization/docker
tags: [docker,healthcheck]
---

### 0. Dockerfile healthcheck
根据docker关于[healthcheck的官方文档](https://docs.docker.com/engine/reference/builder/#healthcheck)。

healthcheck有两种格式：
1. `HEALTHCHECK [OPTIONS] CMD command`，command就是执行健康监测的具体的命令
2. `HEALTHCHECK NONE`, 禁止继承底层镜像的任何健康监测

关于`[OPTIONS]`，有如下选项
- `--interval=DURATION` (default: 30s)
- `--timeout=DURATION` (default: 30s)
- `--start-period=DURATION` (default: 0s)
- `--retries=N` (default: 3)

> `OPTIONS`说明
> - 超过timeout时间的监测，被认为是`failed`
> - 容器启动后，经过interval时间后，执行第一次健康监测，后面的健康监测，都是在上一次健康监测执行完毕后的interval时间后执行
> - start-period给容器启动设定了一个启动时间，在这个时间内，健康监测`failed`并不会计算到retries次数内。但一旦健康监测`success`，则容器被认为启动成功，然后后面的健康监测`failed`就会记录到retries设定的最大失败次数内。

> 健康监测的状态转移：
> - 初始化状态是`starting`
> - 无论之前的状态如何，只要有一次健康监测成功，状态转为`healthy`
> - 当指定次数的健康监测连续失败后，状态转为`unhealthy`

关于CMD之后的command，有两种格式，一种是直接shell格式，`HEALTHCHECK CMD /bin/check-running`，第二种是和`ENTRYPOINT`类似的那种exec数组格式，`HEALTHCHECK CMD ["executable", "param1", "param2"]`
> command执行的三种exit状态
> - 0, success
> - 1, unhealthy
> - 2, reserved - 不要用这个exitcode
> eg: `HEALTHCHECK --interval=5m --timeout=3s CMD curl -f http://localhost/ || exit 1`

### 1. 为什么要用docker-compose的healthcheck？
一句话，不用修改image，无需因为healthcheck给镜像安装额外的工具包，更灵活的修改

示例：
``` yaml
version: "3"
services:
  web:
    image: nginx:latest
    ports:
      - "80:80"
    restart: always
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost/api/nonexist", "||", "exit", "1"]
      interval: 1m30s
      timeout: 3s
      retries: 3
      start_period: 20s
```
> docker-compose的healthcheck更多信息，查看[官方文档](https://docs.docker.com/compose/compose-file/#healthcheck)

### 2. 拥有检查docker的容器是否healthy的接口，然后呢？
目前docker只是提供了检查容器是否healthy的接口，但是并没有给出后续的action。所以目前需要配合各种编排工具来使用。如果是standlone的容器，可能需要自己写脚本来监测容器状态，从而进行后续的动作。

当然，也可以用下面这个镜像，这是开源出来的一个监测容器运行状态，然后根据状态来重启容器的一个公共镜像
```
docker run -d --name autoheal \
  --restart=always \
  -e AUTOHEAL_CONTAINER_LABEL=all \
  -v /var/run/docker.sock:/var/run/docker.sock \
  willfarrell/autoheal
```
> 详细说明和配置见：[docker-hub: willfarrell/autoheal](https://hub.docker.com/r/willfarrell/autoheal/)