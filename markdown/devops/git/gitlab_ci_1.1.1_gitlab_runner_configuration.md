---
title: gitlab-ci: 1.1.1 gitlab-runner(docker)配置
date: 2020-05-01 13:42:00
categories: devops/git
tags: [devops,gitlab,git,ci,gitlab-runner]
---

### 0. gitlab-runner示例配置
`config.toml`
```
concurrent = 1
check_interval = 0

[session_server]
  session_timeout = 1800

[[runners]]
  name = "runner-01"
  url = "http://git.example.net"
  token = "your token here"
  executor = "docker"
  [runners.custom_build_dir]
  [runners.cache]
    [runners.cache.s3]
    [runners.cache.gcs]
  [runners.docker]
    tls_verify = false
    image = "alpine:latest"
    privileged = false
    disable_entrypoint_overwrite = false
    oom_kill_disable = false
    disable_cache = false
    cache_dir = "/data/docker/data/gitlab-runner/cache"
    volumes = ["/data/docker/data/gitlab-runner/cache", "/var/run/docker.sock:/var/run/docker.sock"]
    shm_size = 0
    extra_hosts = ["reg.example.net:172.28.1.50"]
    host = ""
    hostname = ""
    memory = "128m"
    memory_swap = "256m"
    memory_reservation = "64m"
    oom_kill_disable = false
    cpuset_cpus = "0,1"
    cpus = "2"
    dns = ["8.8.8.8"]
    dns_search = [""]
    userns_mode = "host"
    cap_add = ["NET_ADMIN"]
    cap_drop = ["DAC_OVERRIDE"]
    devices = ["/dev/net/tun"]
    wait_for_services_timeout = 30
    shm_size = 300000
    volumes_from = ["storage_container:ro"]
    links = ["mysql_container:mysql"]
    [runners.docker.sysctls]
      "net.ipv4.ip_forward" = "1"
```

### 1. 配置cache目录
```
[[runners]]
  cache_dir = "/mycache"
  [runners.docker]
    disable_cache = false
    cache_dir = "/data/docker/data/gitlab-runner/builds"
    volumes = ["/data/docker/data/gitlab-runner/cache:/mycache"]
```
- cache_dir([[runners]])：
指定的是执行job的容器中，缓存目录位置
- cache_dir([runners.docker]): 
指定的是缓存容器中/builds的本地目录
- volumes如上面的配置，是手动挂载本地目录到cache目录，如果只是写"/mycache"，docker会自动创建一个volume，然后挂载过去

``` bash
# 按照上面的配置，查看某个job的容器信息可以看到
docker inspect containerid
...
"Binds": [
                "/data/docker/data/gitlab-runner/cache:/mycache",
                "/data/docker/data/gitlab-runner/builds/runner-f6drxvp-project-150-concurrent-0/c33bcaa1fd2c77edfc3893b41966cea8:/builds"
            ]
...
# 其中挂载了两个目录
# 一个是我们显示指定的/mycache目录
# 另外一个是[runners.docker]中cache_dir的配置作为根目录，挂载了子目录到容器的/builds目录
```

> 参考链接
> - [whats the cache_dir of the docker executor](https://forum.gitlab.com/t/what-is-the-cache-dir-of-the-docker-executor/4697)
> - [gitlab-runner advance configuration - runner-docker](https://docs.gitlab.com/runner/configuration/advanced-configuration.html#the-runnersdocker-section)

> 关于`[[runners]] - cache_dir`和`[runners.docker] - cache_dir`，官方文档的说明如下
> **`[[runners]] - cache_dir`**
> ```
> Absolute path to a directory where build caches will be stored in context of selected executor (locally, Docker, SSH). If the docker executor is used, this directory needs to be included in its volumes parameter.
> ```
> **`[runners.docker] - cache_dir`**
> ```
> Specify where Docker caches should be stored (this can be absolute or relative to current working directory). See disable_cache for more information.
> ```
> **误区**
> 区别就在于前者是build cache，后者是docker cache，build cache是job的cache，docker cache是docker运行中使用的cache，其实就是job运行时的workdir(默认是/builds)，自己没仔细看人家文档，还以为人家瞎写文档乱配置，汗颜。不过这两个配置不明确是认真的。