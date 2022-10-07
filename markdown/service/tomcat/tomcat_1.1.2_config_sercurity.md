---
title: tomcat: 安全 - 隐藏版本号
date: 2016-06-03 14:45:00
categories: service/tomcat
tags: [tomcat,security]
---

### 背景 
出于安全，一般会隐藏掉服务器信息和对应的版本,避免攻击者通过当前版本的服务器软件的漏洞进行攻击

### 隐藏TOMCAT信息及版本号
``` bash
cd apache-tomcat-7.0.59/lib
mkdir test
cd test

jar xf ../catalina.jar
vi org/apache/catalina/util/ServerInfo.properties
server.info=Tomcat
server.number=6
server.built=Jan 18 2013 14:51:10 UTC

jar cf ../catalina.jar ./*
rm -rf test
```