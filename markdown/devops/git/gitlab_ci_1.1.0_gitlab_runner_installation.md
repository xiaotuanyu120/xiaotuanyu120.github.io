---
title: gitlab-ci: 1.1.0 gitlab-runner安装(docker)
date: 2019-12-12 09:26:00
categories: devops/git
tags: [devops,gitlab,git,ci,gitlab-runner]
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
  - 使用docker环境（通过ssh执行任务） - 不推荐，后续会废弃掉
  - 使用docker环境（在云和虚拟化平台上自动扩展） - 不推荐，后续会废弃掉
  - 使用通过ssh远程连接的server
- 支持bash、windows batch、windows powershell
- 支持GNU/LINUX、windows、macos（任何支持docker的系统）
- 支持自定义任务的运行环境
- 不用重启自动重载配置文件
- 开启docker缓存
- 内嵌Prometheus服务

#### 和gitlab版本的兼容性
gitlab-runner和gitlab版本应该一致，尽管较旧的Runner仍可以使用较新的GitLab版本，反之亦然，但在某些情况下，如果版本不同，则功能可能不可用或无法正常工作。向后不兼容仅适用于主要版本更新。

#### gitlab-runner(docker)原理
这里我们需要介绍几个角色（job-runner是我自己分类的，并非官方说法）：
- gitlab-runner
- job-runner
- gitlab

其中，gitlab-runner是一个中介的角色，它首先在gitlab处通过token注册中介身份。然后定时去询问是否有"工作机会"（job），如果有"工作机会"，则创建一个job-runner的容器来完成工作。


### 1. 安装gitlab-runner（docker）
gitlab-runner的官方镜像基于ubuntu或alpine，这个镜像只是一个gitlab-runner二进制命令的wrapper，就像在宿主机上直接执行gitlab-runner命令。

#### step 1. 注册gitlab-runner到gitlab - 生成配置文件
在注册gitlab-runner到gitlab之前，gitlab-runner不会执行任何任务。更多信息查看：[register官方文档链接](https://docs.gitlab.com/runner/register/index.html#docker)
``` bash
GITLAB_RUNNER_CONF_DIR=/data/docker/runtime/gitlab-runner/config
[[ -d ${GITLAB_RUNNER_CONF_DIR} ]] || mkdir -p ${GITLAB_RUNNER_CONF_DIR}

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

上面的操作，会在`/data/docker/runtime/gitlab-runner/config`，这个目录中生成`config.toml`配置文件。

#### step 2. gitlab-runner和job-runner（个人创造的说法，非官方）的内部解析配置
如果我们有一个内部系统，希望job执行的时候去调用，但是该内部系统我们用的是内部解析的域名，需要修改配置

假设这个系统是sonarqube，我们需要在job-runner的容器环境中增加本地解析，因为job-runner是用gitlab-runner自动启动的docker环境，所以需要修改config.toml中的`runners.docker`部分的`extra_hosts`配置
> 参考链接：[gitlab-runner executor 配置extra_hosts](https://docs.gitlab.com/runner/configuration/advanced-configuration.html)

下面列出以下runner的额外docker的配置：
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

假设这个系统是docker registry，job-runner和gitlab-runner使用的镜像都是用的docker registry中的镜像，那么除了在`config.toml`的`runners.docker`部分中的`extra_hosts`修改之外，还需要在gitlab-runner的docker-compose文件中配置`extra_hosts`
如果sonarqube server使用的是一个内网域名，没有外网解析，执行job时报sonarqube域名无法解析，咋整？


#### step 3. job-runner（个人创造的说法，非官方）中编译docker镜像配置
如果启动的job的容器里面需要执行docker编译，请挂载socket文件进去，例如`volumes = ["/var/run/docker.sock:/var/run/docker.sock","/cache"]`


#### step 4. 如果执行任务的容器镜像使用的是私有仓库，auth问题这样解决
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
> 参考链接：[配置私有docker仓库的auth认证](https://docs.gitlab.com/ee/ci/docker/using_docker_images.html#using-statically-defined-credentials)

### 2. 启动gitlab-runner
``` bash
# 准备gitlab-runner配置目录
GITLAB_RUNNER_CONF_DIR=/data/docker/runtime/gitlab-runner/config

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

### 3. gitlab-runner register 报错
在亚马逊云上申请了一台机器，部署gitlab-runner，register时报错
```
Runtime platform                                    arch=amd64 os=linux pid=6 revision=c5874a4b version=12.10.2
Running in system-mode.                            
                                                              
ERROR: Registering runner... forbidden (check registration token)  runner=<mytoken>
PANIC: Failed to register this runner. Perhaps you are having network problems
```

检查和排除过的可能问题所在
- 确认自建gitlab的域名解析正确；
- 确认自建gitlab域名的http协议正确(http还是https不能搞错，若是https，还要解决证书问题)；
- 确认token输入正确(gitlab网页端，在project页面点击setting - CI/CD - RUNNER);
- 确认经过curl和telnet两个工具测试，gitlab-runner所在服务器可以通过域名调用gitlab服务;
- 确认gitlab-runner版本和gitlab版本一致;

然而我网上搜索错误的关键字，大部分说的都是上面的原因。于是经过一番“大海捞针”，终于找到了一个解决办法:“将docker运行的register容器，网络模式改为host”
``` bash
# 增加了--network host
docker run --rm --network host -v ${GITLAB_RUNNER_CONF_DIR}:/etc/gitlab-runner gitlab/gitlab-runner register \
...
```
> 参考链接：[gitlab org issues](https://gitlab.com/gitlab-org/gitlab-runner/-/issues/4082)


### 4. delete unused gitlab runner
第一步是在gitlab各个project上，disable不用的runner

第二步是执行下面命令
``` bash
curl -S --header "PRIVATE-TOKEN:<user's token>" "http://gitlab.com/api/v4/runners/all" | jq '.[] | select(.status == "paused") | .id' | xargs -I runner_id curl -S --request DELETE --header "PRIVATE-TOKEN:<user's token>" "http://gitlab.com/api/v4/runners/runner_id"
```
> 原理就是筛选出处于paused状态的runner的id，然后删掉它们。