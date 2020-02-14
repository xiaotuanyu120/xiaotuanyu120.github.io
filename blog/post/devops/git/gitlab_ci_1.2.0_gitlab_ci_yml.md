---
title: gitlab-ci: 1.2.0 .gitlab-ci.yml
date: 2019-12-12 11:50:00
categories: devops/git
tags: [devops,gitlab,git,ci,gitlab-runner]
---
### gitlab-ci: 1.2.0 .gitlab-ci.yml example

---

### 0. .gitlab-ci.yml说明
参考链接：[.gitlab-ci.yml 官方文档](https://docs.gitlab.com/ee/ci/yaml/)
.gitlab-ci.yml是用于配置gitlab的pipeline，里面定义了
- gitlab-runner执行的内容
- 特定条件触发后任务的执行走向

``` yaml
image: <your-docker-image-repo>/sonarscanner:4.2

stages:
  - analysis

analysis:
  stage: analysis
  script:
  - wget https://repo1.maven.org/maven2/org/apache/tomcat/tomcat-jsp-api/7.0.96/tomcat-jsp-api-7.0.96.jar -O ./WebRoot/WEB-INF/lib/jsp-api.jar
  - wget https://repo1.maven.org/maven2/org/apache/tomcat/tomcat-servlet-api/7.0.96/tomcat-servlet-api-7.0.96.jar -O ./WebRoot/WEB-INF/lib/servlet-api.jar
  - echo > javafile.txt
  - find src/ -name *.java >> javafile.txt
  - jarfiles=()
  - for jar in $(find path/to/lib -name *.jar);do jarfiles=("${jarfiles[@]}" $jar);done
  - classfile=""
  - for cf in ${jarfiles[@]};do classfile="${classfile}:${cf}";done
  - /bin/mkdir -p path/to/classes
  - /usr/lib/jvm/java-1.7-openjdk/bin/javac -d path/to/classes -sourcepath src -cp $classfile @javafile.txt
  - /app/bin/sonar-scanner
    -Dsonar.host.url=http://sonarqube-domain:9000 
    -Dsonar.projectKey=project-name 
    -Dsonar.sources=./src 
    -Dsonar.sourceEncoding=UTF-8
    -Dsonar.java.binaries=./path/to/classes
    -Dsonar.java.libraries=./path/to/**/*.jar
  only:
  - master
```
> 注意点：
> - 只有一个stage里面的所有job都执行完毕了，才会去执行下一个stage
> - 同一个stage里面的job是同时被执行的
> - only限定了只有master分支commit后才会触发pipeline的执行


### 1. [cache](https://docs.gitlab.com/ee/ci/yaml/README.html#cache) vs [artifacts](https://docs.gitlab.com/ee/user/project/pipelines/job_artifacts.html#introduction-to-job-artifacts)
官方文档[cache vs artifacts](https://docs.gitlab.com/ee/ci/caching/#cache-vs-artifacts)里面说：
- cache：用于储存工程依赖文件
- artifacts：用于储存在stage之间需要传递的文件

#### cache
``` yaml
cache:
  key:
    files:
      - Gemfile.lock
      - package.json
  paths:
    - vendor/ruby
    - node_modules
```
> 如果没有用到共享缓存，只是用本地缓存，必须保证runner对project的唯一性

> - key: 是决定是否更新新缓存的条件，一旦此条件发生变化，就创建新的缓存（一旦Gemfile.lock或package.json变化，会重新创建cache）
> - paths: 是相对于`${CI_PROJECT_DIR}`下面的相对路径，是被缓存的目标

> gitlab版本需要更新到12.5+

#### artifacts
``` yaml
deploy:
  ...
  artifacts:
    paths:
    - target
    expire_in: 1 day
```
> erro: `ERROR: Uploading artifacts to coordinator... too large archive`
> [解决方法](https://gitlab.com/gitlab-org/gitlab-foss/issues/14841)
> 1. gitlab启动参数增加nginx的`client_max_body_size`
> 2. gitlab的admin的CICD设置中，调大artifacts的上限大小