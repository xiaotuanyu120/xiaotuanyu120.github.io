---
title: 1.2.5 dockerfile 示例
date: 2020-04-24 09:37:00
categories: virtualization/docker
tags: [docker,dockerfile]
---

### 0. 问题背景
积累实战中需要的dockerfile方案

### 1. dind - docker in docker
用于在docker容器中打docker镜像，并支持多种语言的编译，还包含了测试工具
```
FROM docker:19.03.0-dind
RUN apk update && apk upgrade && \
    apk add --no-cache bash git openssh openjdk8 openjdk7 maven nodejs npm curl && \
    echo "export JAVA_HOME=/usr/lib/jvm/default-jvm" >> /etc/profile
```

### 2. jenkins
```
FROM jenkins/jenkins:lts
ADD jdk-8u221-linux-x64.tar.gz /usr/local/
ADD jdk-7u80-linux-x64.tar.gz /usr/local/
ADD node-v8.16.1-linux-x64.tar.gz /usr/local/
COPY jenkins-profile.sh /etc/profile.d/
USER root
RUN apt-get update \
      && apt-get install -y git maven sudo libltdl7 rsync \
      && rm -rf /var/lib/apt/lists/*
ENV TZ=Asia/Shanghai
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone; \
      echo "jenkins ALL=NOPASSWD: ALL" >> /etc/sudoers; \
      source /etc/profile
USER jenkins
```
jenkins-profile.sh
```
export PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
```
> jdk和node包请自行下载

### 3. php-apache
``` bash
FROM php:5.6-apache
RUN apt-get update \
    # 增加图片系统库支持
    && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
    apt-utils libpng-dev libfreetype6-dev libjpeg62-turbo-dev \
    && rm -rf /var/lib/apt/lists/* \
    # 安装php扩展
    && docker-php-ext-configure gd --with-freetype-dir --with-jpeg-dir --with-png-dir \
    && docker-php-ext-install pdo_mysql mysqli mysql gd \
    # apache开启功能
    && a2enmod rewrite \
    && ln -s /etc/apache2/mods-available/ssl.conf /etc/apache2/mods-enabled/ssl.conf \
    && ln -s /etc/apache2/mods-available/ssl.load /etc/apache2/mods-enabled/ssl.load \
    && ln -s /etc/apache2/mods-available/socache_shmcb.load /etc/apache2/mods-enabled/socache_shmcb.load
COPY --chown=33:33 . /var/www/html/
```

### 4. install mvn 3.6.3 on centos7
```
FROM centos:7

COPY apache-maven-3.6.3-bin.tar.gz .
RUN tar -zxvf apache-maven-3.6.3-bin.tar.gz; \
    mv apache-maven-3.6.3 /usr/local; \
    ln -s /usr/local/apache-maven-3.6.3 /usr/local/apache-maven; \
    rm -rf apache-maven-3.6.3-bin.tar.gz

ENV PATH="$PATH:/usr/local/apache-maven/bin"
```