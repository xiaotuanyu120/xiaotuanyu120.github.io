---
title: tomcat: 错误 - 启动问题
date: 2016-05-05 09:06:00
categories: service/tomcat
tags: [tomcat]
---

## 问题背景
线上服务器备份web目录、server.xml到本地测试环境报错

### 报错信息
``` bash
cat catalina.out |grep -E "Failed|not|Caused"
WARNING: [SetPropertiesRule]{Server/Service/Engine/Host/Context} Setting property 'debug' to '0' did not find a matching property.
INFO: The APR based Apache Tomcat Native library which allows optimal performance in production environments was not found on the java.library.path: /usr/java/packages/lib/amd64:/usr/lib64:/lib64:/lib:/usr/lib
SEVERE: Failed bind replication listener on address:auto
java.net.UnknownHostException: tomcat7: tomcat7: Name or service not known
Caused by: java.net.UnknownHostException: tomcat7: Name or service not known
SEVERE: Failed bind replication listener on address:auto
......
Caused by: java.net.UnknownHostException: auto: Name or service not known
```

### 问题分析
关键语句: `tomcat7: tomcat7: Name or service not known`

tomcat7 是我测试机器的hostname

检查server.xml和启动脚本，都没有发现tomcat7这个关键词

猜测，难道是无法解析测试机的主机名
 
### 解决方案
``` bash
vi /etc/hosts
****************************
127.0.0.1 tomcat7
****************************
# 问题成功解决
```

> 根因未挖出，但这是早期文章，测试环境已经没有了，暂不深究。