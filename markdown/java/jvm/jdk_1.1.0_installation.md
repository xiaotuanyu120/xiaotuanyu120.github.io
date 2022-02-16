---
title: JDK 安装 - jre1.6 和 jre1.8
date: 2016-09-27 11:42:00
categories: java/jvm
tags: [java,jre]
---

### 1.1 安装JAVA环境 - jre1.6
``` bash
chmod u+x jre-6u45-linux-x64.bin
sh jre-6u45-linux-x64.bin
mv jre1.6.0_45 /usr/local/
ln -s /usr/local/jre1.6.0_45/ /usr/local/jdk
```


### 1.2 安装JAVA环境 - jre1.8
``` bash
tar zxvf server-jdk-8u66-linux-x64.tar.gz
mv jdk1.8.0_66/ /usr/local/
ln -s /usr/local/jdk1.8.0_102 /usr/local/jdk
```

### 2 配置java环境变量
``` bash
vim /etc/profile.d/java-env.sh
*******************************
JAVA_HOME=/usr/local/jdk
JRE_HOME=${JAVA_HOME}/jre
PATH=$PATH:${JAVA_HOME}/bin:${JRE_HOME}/bin
CLASSPATH=${JAVA_HOME}/lib:${JRE_HOME}/lib
*******************************
source /etc/profile.d/java-env.sh
```
