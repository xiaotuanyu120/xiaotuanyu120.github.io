---
title: gitlab-ci: 1.3.0 编译docker镜像
date: 2020-01-21 18:16:00
categories: devops/git
tags: [devops,gitlab,git,ci,gitlab-runner]
---

### 0. 如何在gitlab-runner（exeutor：docker）中编译docker镜像
参考链接：
- [gitlab CI using_docker_build](https://docs.gitlab.com/ee/ci/docker/using_docker_build.html)
- [gitlab issue: 65511](https://gitlab.com/gitlab-org/gitlab-foss/issues/65511)
- [gitlab predefined variables](https://docs.gitlab.com/ee/ci/variables/predefined_variables.html)，这个文档不准确，用它里面介绍的变量都不存在，最后是[使用export命令debug出来可用的变量](https://docs.gitlab.com/ee/ci/variables/README.html)


### 1. 示例
config.toml
```
concurrent = 20
check_interval = 0

[session_server]
  session_timeout = 1800

[[runners]]
  environment = ["DOCKER_AUTH_CONFIG={\"auths\":{\"<your-private-registry>\":{\"auth\":\"<auth-string>\"}}}"]
  name = "docker-runner"
  url = "http://<your-git-url>"
  token = "<project-token>"
  executor = "docker"
  [runners.custom_build_dir]
  [runners.docker]
    tls_verify = false
    image = "alpine:latest"
    privileged = true 
    disable_entrypoint_overwrite = false
    oom_kill_disable = false
    disable_cache = false
    volumes = ["/var/run/docker.sock:/var/run/docker.sock"]
    shm_size = 0
    extra_hosts = ["sonarqube.example.net:192.168.86.60", "git.example.net:172.21.33.33", "reg.example.net:192.168.86.137"]
  [runners.cache]
    [runners.cache.s3]
    [runners.cache.gcs]

```
> 根据[gitlab CI using_docker_build](https://docs.gitlab.com/ee/ci/docker/using_docker_build.html)里面的说明，必须要使用privileged模式

``` yaml
image: <your-private-registry>/base-dind-build

stages:
  - build

variables:
  DOCKER_HOST: unix:///var/run/docker.sock
  DOCKER_DRIVER: overlay2

before_script:
  - docker login -u <user> -p <password> <your-private-registry>

build:
  stage: build
  script:
  - npm install
  - npm run build:prod
  - docker build --cache-from <your-private-registry>/vue:latest -t <your-private-registry>/vue:$CI_COMMIT_SHA -t <your-private-registry>/vue:latest .
  - docker push <your-private-registry>/luckyio-vue:$CI_COMMIT_SHA
  only:
  - master
  - manual
```
> [gitlab CI using_docker_build](https://docs.gitlab.com/ee/ci/docker/using_docker_build.html)，这个官方文档要仔细看，它写的指引里面，registry用的是gitlab自己的，所以如果我们使用的是其他的镜像库软件，然后参照它这里的流程是走不通的。

> dind，这个是docker官方出的，在docker里面运行docker的镜像。（根据上面的issue，使用最新的19.03.5版本有问题，要换成19.03.0）

> 重点是DOCKER_HOST，这个变量是docker命令和docker服务交互的接口，官方文档推荐用的是tcp://docker:2375，但是官方文档使用的registry是gitlab自己的，所以这里我换成了socket文件`/var/run/docker.sock`

> --cache-from，这个是用来使用之前的镜像缓存来加速docker镜像编译速度

> CI_COMMIT_SHA，关于这个变量，设想是想使用commit的唯一值来区分镜像版本。最开始按照[gitlab predefined variables](https://docs.gitlab.com/ee/ci/variables/predefined_variables.html)这里面的变量来使用，发现好多是空的。于是参照[这里](https://docs.gitlab.com/ee/ci/variables/README.html)，使用`- export`命令列出了所有可用的变量，才找到正确可用的变量。