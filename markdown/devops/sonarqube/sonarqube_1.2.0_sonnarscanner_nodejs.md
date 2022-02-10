---
title: sonarqube: 1.2.0 sonarscanner扫描js代码
date: 2019-12-16 14:56:00
categories: devops/sonarqube
tags: [devops,sonarqube,java]
---

### 1. sonnarscanner扫描js代码示例
``` bash
# 例子
sonar-scanner \
  -Dsonar.host.url=http://sonarqube-domain:9000 \
  -Dsonar.projectKey=project-name \
  -Dsonar.sources=./src \
  -Dsonar.sourceEncoding=UTF-8
```

### 2. 在docker中运行sonnarscanner
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
# 安装nodejs编译js代码
cat << EOF > Dockerfile
FROM alpine:latest
WORKDIR /app
ADD sonar-scanner-4.2.0.1873-linux.tar.gz /app
RUN apk update && apk upgrade && \
    apk add --no-cache bash git openssh openjdk8-jre nodejs
EOF
```