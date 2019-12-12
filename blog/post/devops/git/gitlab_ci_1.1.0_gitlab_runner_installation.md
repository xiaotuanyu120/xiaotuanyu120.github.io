---
title: gitlab-ci: 1.1.0 gitlab-runner安装(docker)
date: 2019-12-12 09:26:00
categories: devops/git
tags: [devops,gitlab,git,ci,gitlab-runner]
---
### gitlab-ci: 1.1.0 gitlab-runner安装(docker)

---

### 0. gitlab-runner简介
Gitlab Runner是一个用于执行CI任务然后返回结果给gitlab的开源工程。Gitlab Runner用于和Gitlab CI连接（人话就是想执行gitlab ci里面的任务必须要使用gitlabrunner，gitlab本身的程序只提供ci的web界面，而不执行具体的任务）。

gitlab-runner是使用golang编写的，所以只是一个单个的可执行程序，不需要任何依赖。

#### gitlab-runner特性：
- 允许执行：
  - 并行多个任务
  - 给多个server使用多个token（或者给多个project使用多个token）
  - 根据token来限制任务并发数量限制
- 任务可以执行在：
  - 本地环境
  - 使用docker环境
  - 使用docker环境（通过ssh执行任务）
  - 使用docker环境（在云和虚拟化平台上自动扩展）
  - 使用通过ssh远程连接的server
- 支持bash、windows batch、windows powershell
- 支持GNU/LINUX、windows、macos（任何支持docker的系统）
- 支持自定义任务的运行环境
- 不用重启自动重载配置文件
- 开启docker缓存
- 内嵌Prometheus服务

#### 和gitlab版本的兼容性
gitlab-runner和gitlab版本应该一致，尽管较旧的Runner仍可以使用较新的GitLab版本，反之亦然，但在某些情况下，如果版本不同，则功能可能不可用或无法正常工作。向后不兼容仅适用于主要版本更新。


### 1. 按照gitlab-runner（docker）
gitlab-runner的官方镜像基于ubuntu或alpine，这个镜像只是一个gitlab-runner二进制命令的wrapper，就像在宿主机上直接执行gitlab-runner命令。
#### 启动gitlab-runner
``` bash
# 准备gitlab-runner配置目录
GITLAB_RUNNER_CONF_DIR=/data/docker/runtime/gitlab-runner/config
[[ -d ${GITLAB_RUNNER_CONF_DIR} ]] || mkdir -p ${GITLAB_RUNNER_CONF_DIR}

# 启动gitlab-runner
cat << EOF > docker-compose-gitlab-runner.yml
version: '2'
services:
  gitlab-runner:
    image: gitlab/gitlab-runner:latest
    container_name: gitlab-runner
    restart: always
    volumes:
       - ${GITLAB_RUNNER_CONF_DIR}:/etc/gitlab-runner
       - /var/run/docker.sock:/var/run/docker.sock
EOF

docker-compose -f docker-compose-gitlab-runner.yml up -d
```

#### 注册gitlab-runner到gitlab（会生成配置文件）
在注册gitlab-runner到gitlab之前，gitlab-runner不会执行任何任务。更多信息查看：[register官方文档链接](https://docs.gitlab.com/runner/register/index.html#docker)
``` bash
docker run --rm -v ${GITLAB_RUNNER_CONF_DIR}:/etc/gitlab-runner gitlab/gitlab-runner register \
  --non-interactive \
  --executor "docker" \
  --docker-image alpine:latest \
  --url "http://your-gitlab-domain" \
  --registration-token "your-gitlab-token" \
  --description "your-runner-description" \
  --tag-list "tag1,tag2" \
  --run-untagged="true" \
  --locked="false" \
  --access-level="not_protected"
```
> 主要选项介绍：
> - executor，指定runner名称
> - docker-image，指定任务执行默认的镜像（runner会控制docker，在宿主机启动独立的容器来执行任务，这里说的镜像就是这个容器的镜像。）
> - url，指定gitlab的url
> - registration-token，指定注册的runner的token，这个可以在gitlab的ci设定里面找到

#### 如果sonarqube server使用的是一个内网域名，没有外网解析，执行job时报sonarqube域名无法解析，咋整？
参考链接：[gitlab-runner executor 配置extra_hosts](https://docs.gitlab.com/runner/configuration/advanced-configuration.html)

sonarqube server使用的是内网ip，然后自以为在gitlab-runner的容器启动时增加了`--add-host=mysonarqube-server-domain:ip-address`，应该就可以顺利解析了，结果事与愿违，竟然执行job时报解析不了sonarqube server域名的错误。

苦思冥想了一段时间，才发现，原来gitlab-runner那个容器并不实际执行job。当runner接收到任务的时候，它会额外启动其他的容器来执行job，这就导致了，我在runner上配置的extra_hosts压根没起作用。下面列出以下runner的额外docker的配置：
```
[runners.docker]
  host = ""
  hostname = ""
  tls_cert_path = "/Users/ayufan/.boot2docker/certs"
  image = "ruby:2.1"
  memory = "128m"
  memory_swap = "256m"
  memory_reservation = "64m"
  oom_kill_disable = false
  cpuset_cpus = "0,1"
  cpus = "2"
  dns = ["8.8.8.8"]
  dns_search = [""]
  privileged = false
  userns_mode = "host"
  cap_add = ["NET_ADMIN"]
  cap_drop = ["DAC_OVERRIDE"]
  devices = ["/dev/net/tun"]
  disable_cache = false
  wait_for_services_timeout = 30
  cache_dir = ""
  volumes = ["/data", "/home/project/cache"]
  extra_hosts = ["other-host:127.0.0.1"]
  shm_size = 300000
  volumes_from = ["storage_container:ro"]
  links = ["mysql_container:mysql"]
  services = ["mysql", "redis:2.8", "postgres:9"]
  allowed_images = ["ruby:*", "python:*", "php:*"]
  allowed_services = ["postgres:9.4", "postgres:latest"]
  [runners.docker.sysctls]
    "net.ipv4.ip_forward" = "1"
```
> 关于额外配置hosts解析的内容，只需要关注extra_hosts

#### 如果执行任务的容器镜像使用的是私有仓库，auth问题这样解决
参考链接：[配置私有docker仓库的auth认证](https://docs.gitlab.com/ee/ci/docker/using_docker_images.html#using-statically-defined-credentials)
``` bash
# 手动登录你的私有仓库
docker login --username <username> --password <password> <your-docker-repo-domain>

# 查看docker在本地生成的auth信息
cat ~/.docker/config.json 
{
	"auths": {
		"<your-docker-repo-domain>": {
			"auth": "auth-string"
		}
	},
	"HttpHeaders": {
		"User-Agent": "Docker-Client/18.09.9 (linux)"
	}
}

# 打开gitlab-runner的持久化配置文件
vi ${GITLAB_RUNNER_CONF_DIR}/config.toml
# 将docker镜像仓库的auth信息填写进去
[[runners]]
  environment = ["DOCKER_AUTH_CONFIG={\"auths\":{\"your-docker-repo-domain\":{\"auth\":\"auth-string\"}}}"]
```

#### 如果执行任务的容器使用的镜像是基于alpine，那么如果任务运行时会遇到找不到java命令的错误
参考链接：
- [alpine镜像里面java找不到的报错解决方案](https://community.sonarsource.com/t/installing-sonar-scanner-in-alpine-linux-docker/7010/2)
- [修改sonarscanner文件，配置使用系统的java环境](https://www.javatt.com/p/66709)

``` bash
# 下载sonarscanner，解压目录，然后编辑sonarscanner，配置程序使用宿主机的java，而不是自己内嵌的java
sed -ir 's/^use_embedded_jre=.*$/use_embedded_jre=false/g' bin/sonar-scanner
# 然后将修改好的sonar-scanner目录打包成sonar-scanner-4.2.0.1873-linux.tar.gz
tar zcvf sonar-scanner-4.2.0.1873-linux.tar.gz bin conf jre lib

# 准备Dockerfile
# 安装jre8运行sonnarscanner
# 安装jdk7用于编译java工程（这个要依据你的java工程使用的jdk来定）
cat << EOF > Dockerfile
FROM alpine:latest
WORKDIR /app
ADD sonar-scanner-4.2.0.1873-linux.tar.gz /app
RUN apk update && apk upgrade && \
    apk add --no-cache bash git openssh openjdk8-jre openjdk7
EOF
```