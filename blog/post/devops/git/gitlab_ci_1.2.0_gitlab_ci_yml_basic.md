---
title: gitlab-ci: 1.2.0 .gitlab-ci.yml 基础
date: 2019-12-12 11:50:00
categories: devops/git
tags: [devops,gitlab,git,ci,gitlab-runner]
---
### gitlab-ci: 1.2.0 .gitlab-ci.yml 基础

---

### 0. `.gitlab-ci.yml`说明
参考链接：[.gitlab-ci.yml 官方文档](https://docs.gitlab.com/ee/ci/yaml/)
.gitlab-ci.yml是用于配置gitlab的pipeline，里面定义了
- gitlab-runner执行的内容
- 特定条件触发后任务的执行走向

``` yaml
image: dind

stages:
  - build
  - docker-build

variables:
  DOCKER_HOST: unix:///var/run/docker.sock
  DOCKER_DRIVER: overlay2
  MAVEN_OPTS: -Dmaven.repo.local=${CI_PROJECT_DIR}/.m2

before_script:
  - docker login -u user -p password private.docker-registry.net

build:
  stage: build
  script:
    - mvn clean install ${MAVEN_OPTS}
  cache:
    paths:
      - ${CI_PROJECT_DIR}/.m2
  artifacts:
    paths:
      - target
    expire_in: 1 day

docker-build:
  stage: docker-build
  script:
    - docker build --cache-from private.docker-registry.net/web:latest
        -t private.docker-registry.net/web:${CI_COMMIT_SHA:0:6}
        -t private.docker-registry.net/web:latest .
    - docker push private.docker-registry.net/web:${CI_COMMIT_SHA:0:6}
  only:
    - master
```
> 注意点：
> - 只有一个stage里面的所有job都执行完毕了，才会去执行下一个stage
> - 同一个stage里面的job是同时被执行的
> - only限定了只有master分支commit后才会触发pipeline的执行


### 1. 常用的gitlab ci内置变量
- `CI_BUILDS_DIR`，执行build的根目录，默认是`/builds`
- `CI_PROJECT_DIR`，当前project的被clone到的目录，也就是默认你所有script执行命令运行的目录
- `CI_COMMIT_SHA`，commit的sha值


### 2. 关于curl的用法
``` yaml
  script: >-
    curl -X post -H "Content-Type:application/json" -H "Authorization: 认证字符串" -d "{\"extra_vars\": {\"role\": \"test_role\",\"project\": {\"version\": \"${CI_COMMIT_SHA:0:6}\",\"name\": \"project_name\"},\"host\": \"project_host\"}}" http://awx_domain/api/v2/job_templates/deploy_test/launch/
```
> 别问我为啥，我是尝试了很多形式才成功的，最终这样成功了
> [gitlab issues](https://gitlab.com/gitlab-org/gitlab-foss/issues/59726)
> [stackoverflow](https://stackoverflow.com/questions/43223992/escape-curl-command-in-yaml-which-contains-quotes-and-apostrophes/43224973)

### 3. 关于for循环中多行代码的写法
``` yaml
  script:
    - echo ${rsyncpass} > ./rsyncpass && chmod 600 ./rsyncpass
    - for ip in ${rsync_dest_all};
        do
          rsync -auvz --progress --no-o --no-g --no-p --delete
            --password-file=./rsyncpass
            --exclude="properties" --exclude="config.properties"
            --exclude="ftp.properties" --exclude="log4j.properties"
            ./dc-api/dc-api-preferential/target/dc-api-preferential/* leo@${ip}::${RSYNC_DEST_MOD_PREF};
        done
```
> 失败的尝试是在rsync的多行命令末尾增加`\`