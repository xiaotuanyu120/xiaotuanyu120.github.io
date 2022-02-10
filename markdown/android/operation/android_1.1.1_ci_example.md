---
title: android 1.1.1 android compile CI
date: 2020-04-06 16:46:00
categories: android/operation
tags: [android,sdk]
---


### 0. 问题背景
公司安卓项目需要上CI，于是需要研究android编译.


### 1. Dockerfile
```
FROM gradle:4.6-jdk8
USER root

# 准备android sdk环境
COPY --chown=1000:1000 commandlinetools-linux-6200805_latest /usr/local/android
ENV PATH=$PATH:/usr/local/android/tools/bin
ENV ANDROID_HOME=/usr/local/android
RUN yes|sdkmanager --sdk_root=/usr/local/android --licenses \
    && sdkmanager --sdk_root=/usr/local/android "build-tools;28.0.3"
```

### 2. .gitlab-ci.yml
``` yaml
image: your-reg.com/base-dind-build

stages:
  - build

variables:
  DOCKER_HOST: unix:///var/run/docker.sock
  DOCKER_DRIVER: overlay2

before_script:
  - docker login -u username -p password your-reg.com

build:
  stage: build
  script:
  - chmod +x commandlinetools-linux-6200805_latest/tools/bin/*
  - docker build
      --cache-from your-reg.com/android-build:latest
      -t your-reg.com/android-build:${CI_COMMIT_SHA:0:6}
      -t your-reg.com/android-build:latest .
  - docker push your-reg.com/android-build:${CI_COMMIT_SHA:0:6}
  environment:
    name: production
  only:
  - master
```