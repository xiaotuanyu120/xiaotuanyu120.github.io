---
title: gitlab-ci: 1.1.1 gitlab-runner(docker)配置
date: 2020-05-01 13:42:00
categories: devops/git
tags: [devops,gitlab,git,ci,gitlab-runner]
---
### gitlab-ci: 1.1.1 gitlab-runner(docker)配置

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
  url = "http://extgit.easydevops.net"
  token = "P29W_M2onsxmJK2WFsXm"
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
    extra_hosts = ["extreg.easydevops.net:172.28.1.50"]
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
  [runners.docker]
    disable_cache = false
    cache_dir = "/data/docker/data/gitlab-runner/cache"
    volumes = ["/data/docker/data/gitlab-runner/cache"]
```
- cache_dir: 指定cache功能的本地缓存数据目录，如果是用docker-executor，那么同时要在volumes里面增加此目录

> 参考链接
> - [whats the cache_dir of the docker executor](https://forum.gitlab.com/t/what-is-the-cache-dir-of-the-docker-executor/4697)
> - [gitlab-runner advance configuration - runner-docker](https://docs.gitlab.com/runner/configuration/advanced-configuration.html#the-runnersdocker-section)