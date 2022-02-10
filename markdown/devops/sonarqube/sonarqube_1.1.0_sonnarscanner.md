---
title: sonarqube: 1.1.0 sonarscanner扫描java代码
date: 2019-12-12 14:05:00
categories: devops/sonarqube
tags: [devops,sonarqube,java]
---

### 1. sonarscanner简介
参考链接：[sonarscanner官方文档](https://docs.sonarqube.org/latest/analysis/scan/sonarscanner/)

其实sonarscanner只是sonarqube的一种代码扫描的方式，比较通用的方式。如果你用的是maven、gradle啥的，可以用对应的工具。恰好我就遇到了这样的project。所以只能使用最通用的方式，sonarscanner。

sonarscanner就是你没有特定的scanner时，使用的一个代码的scanner。

### 2. sonnarscanner使用
``` bash
# 例子
sonar-scanner \
  -Dsonar.host.url=http://sonarqube-domain:9000 \
  -Dsonar.projectKey=project-name \
  -Dsonar.sources=./src \
  -Dsonar.sourceEncoding=UTF-8 \
  -Dsonar.java.binaries=./path/to/classes \
  -Dsonar.java.libraries=./path/to/**/*.jar
```
> 重点：
> - java代码必须编译过后，使用sonar.java.binaries指向编译后的classes目录，然后sonar.sources指向源码目录，才可以正常检测
> - 有些教程让我们指定sonar.languages，这个选项已经废弃了，sonar会自己检测源码是什么类型

### 3. `ERROR: Error during SonarQube Scanner execution java.lang.IllegalStateException: No files nor directories matching`
这个错误。。。其实就是因为没有提前编译java代码，所以classes目录不存在，导致报错。提前编译好java代码即可


### 4. 在docker中运行sonnarscanner
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
    apk add --no-cache bash git openssh openjdk8 openjdk7 maven && \
    echo "export JAVA_HOME=/usr/lib/jvm/default-jvm" >> /etc/profile
ADD settings.xml /usr/share/java/maven-3/conf/settings.xml
EOF

# 准备Dockerfile所需要的文件
cat << EOF > settings.xml
<settings>
    <pluginGroups>
        <pluginGroup>org.sonarsource.scanner.maven</pluginGroup>
    </pluginGroups>
    <profiles>
        <profile>
            <id>sonar</id>
            <activation>
                <activeByDefault>true</activeByDefault>
            </activation>
            <properties>
                <sonar.host.url>
                  http://sonarqube.example.net:9000
                </sonar.host.url>
            </properties>
        </profile>
     </profiles>
</settings>
EOF
```