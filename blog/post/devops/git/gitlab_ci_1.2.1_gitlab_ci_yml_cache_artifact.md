---
title: gitlab-ci: 1.2.1 .gitlab-ci.yml - cache and artifact
date: 2019-12-12 11:50:00
categories: devops/git
tags: [devops,gitlab,git,ci,gitlab-runner]
---
### gitlab-ci: 1.2.1 .gitlab-ci.yml - cache and artifact

---

### 0. [cache](https://docs.gitlab.com/ee/ci/yaml/README.html#cache) vs [artifacts](https://docs.gitlab.com/ee/user/project/pipelines/job_artifacts.html#introduction-to-job-artifacts)
官方文档[cache vs artifacts](https://docs.gitlab.com/ee/ci/caching/#cache-vs-artifacts)里面说：
- cache：用于储存工程依赖文件
- artifacts：用于储存在stage之间需要传递的文件

### 1. cache
**BASIC**
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
> 如果没有用到共享缓存，只是用本地缓存，必须保证runner对project的唯一性(人话就是，必须保证project在同一个gitlab-runner上执行)

> - key: 是决定是否更新新缓存的条件，一旦此条件发生变化，就创建新的缓存（一旦Gemfile.lock或package.json变化，会重新创建cache）
> - paths: 是相对于`${CI_PROJECT_DIR}`下面的相对路径，是被缓存的目标

> gitlab版本需要更新到12.5+

> **`not supported: outside build directory`**，cache不支持在build目录之外的目录

> cache 本地目录配置参照[gitlab runner 配置文档](/devops/git/gitlab_ci_1.1.1_gitlab_runner_configuration.html)

**EXAMPLE: CACHE MAVEN LOCAL REPOSITORY**
- 然后在.gitlab-ci.yml中配置
``` yaml
variables:
  MAVEN_OPTS: -Dmaven.repo.local=${CI_PROJECT_DIR}/.m2

cache:
  paths:
    - ${CI_PROJECT_DIR}/.m2

  script:
    - mvn clean install -Dmaven.test.skip=true ${MAVEN_OPTS}
```

> [stackoverflow: change local m2 dir](https://stackoverflow.com/questions/16591080/maven-alternative-m2-directory)

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