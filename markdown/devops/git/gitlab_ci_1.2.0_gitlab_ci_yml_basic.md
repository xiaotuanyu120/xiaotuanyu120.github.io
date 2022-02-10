---
title: gitlab-ci: 1.2.0 .gitlab-ci.yml 基础
date: 2019-12-12 11:50:00
categories: devops/git
tags: [devops,gitlab,git,ci,gitlab-runner]
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
    curl -X POST -H "Content-Type:application/json" -H "Authorization: 认证字符串" -d "{\"extra_vars\": {\"role\": \"test_role\",\"project\": {\"version\": \"${CI_COMMIT_SHA:0:6}\",\"name\": \"project_name\"},\"host\": \"project_host\"}}" http://awx_domain/api/v2/job_templates/deploy_test/launch/
```
> 别问我为啥，我是尝试了很多形式才成功的，最终这样成功了
> [gitlab issues](https://gitlab.com/gitlab-org/gitlab-foss/issues/59726)
> [stackoverflow](https://stackoverflow.com/questions/43223992/escape-curl-command-in-yaml-which-contains-quotes-and-apostrophes/43224973)

另外一种简单方法
``` yaml
  script:
    - msg='{"extra_vars": {"role": "test_role","project": {"version": "'${CI_COMMIT_SHA:0:6}'","name": "project_name"},"host":"project_host"}}'
    - >
      curl -X POST -H "Content-Type:application/json" -H "Authorization: 认证字符串" -d ${msg} http://awx_domain/api/v2/job_templates/deploy_test/launch/
```
> 注意msg变量不能用空格，curl命令的json格式里面都不要有空格

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
            ./demo/target/demo/* rsync@<ip>::<RSYNC_DEST_MOD_PREF>;
        done
```
> 失败的尝试是在rsync的多行命令末尾增加`\`

### 4. git strategy
通过设定GIT_STRATEGY，我们可以来给job设定不同的git策略
- clone，最慢的选项，会重新下载代码，保证本地代码总是最原始状态
- fetch，会使用本地的代码为基础，然后拉取最新的commit，来加速拉取代码的速度
- none，会直接使用本地的代码
> [gitlab docs about git strategy](https://docs.gitlab.com/ee/ci/yaml/#git-strategy)

### 5. anchors
如果遇到需要复用的部分，可以使用anchors
``` yaml
.job_template: &java-project
  cache:
    paths:
      - ${PROJECT_CACHE}
  artifacts:
    paths:
      - ${PROJECT_ARTIFACTS}

javaproject01:
  <<: *java-project
  varibles:
    PROJECT_CACHE: .m2
    PROJECT_ARTIFACTS: ./target
  script:
    - test1 project

javaproject02:
  <<: *java-project
  varibles:
    PROJECT_CACHE: .m2
    PROJECT_ARTIFACTS: ./target
  script:
    - test2 project
```
> [gitlab ci yaml anchors](https://docs.gitlab.com/ee/ci/yaml/#anchors)

### 6. include
如果遇到多个project复用的部分逻辑，可以使用include
``` yaml
# 多个project都需要同样的before_script
# put it in https://gitlab.com/awesome-project/raw/master/.before-script-template.yml
before_script:
  - apt-get update -qq && apt-get install -y -qq sqlite3 libsqlite3-dev nodejs
  - gem install bundler --no-document
  - bundle install --jobs $(nproc)  "${FLAGS[@]}"

# 在另外一个.gitlab-ci.yml中
include:
  - 'https://gitlab.com/awesome-project/raw/master/.before-script-template.yml'
  - '/templates/.after-script-template.yml'
  - template: Auto-DevOps.gitlab-ci.yml
  - project: 'my-group/my-project'
    ref: master
    file: '/templates/.gitlab-ci-template.yml'
```
> [gitlab ci yaml include](https://docs.gitlab.com/ee/ci/yaml/includes.html)