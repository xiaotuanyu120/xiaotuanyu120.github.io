---
title: tomcat 7.1.1 使用非root用户用daemon运行tomcat - (systemd) - 推荐
date: 2018-05-30 21:41:00
categories: service/tomcat
tags: [linux,tomcat]
---

### 0. 背景
之前讨论了tomcat官方推荐的jsvc模式启动tomcat的方式，但是这种方式有点问题
1. jsvc和常规的startup.sh启动方式相比，虽然jsvc更准确的获得了进程的完全启动时间，但是反馈确实不如脚本方式快速
2. jsvc模式，启动一个jvm，有两个进程

所以这里来讨论如何使用systemd调用脚本，来代替jsvc的模式

### 1. 最简单的单个tomcat
systemd-unit-file: `/usr/lib/systemd/system/tomcat.service`
```
[Unit]
Description=tomcat
After=network.target

[Service]
Type=forking  
User=tomcat
Group=tomcat
Environment=JAVA_HOME=/usr/local/java
Environment=CATALINA_HOME=/usr/local/tomcat03
ExecStart=/usr/local/tomcat03/bin/startup.sh
ExecStop=/usr/local/tomcat03/bin/shutdown.sh
Restart=always

[Install]
WantedBy=multi-user.target
```

### 2. 单机tomcat伪集群
#### 1) 子tomcat的systemd文件
system-unit-file: `/usr/lib/systemd/system/tomcat01.service`
```
[Unit]
Description=tomcat worker s1
After=network.target
PartOf=tomcat-cluster.target

[Service]
Type=forking  
User=tomcat
Group=tomcat
Environment=JAVA_HOME=/usr/local/java
Environment=CATALINA_HOME=/usr/local/tomcat01
ExecStart=/usr/local/tomcat01/bin/startup.sh
ExecStop=/usr/local/tomcat01/bin/shutdown.sh
Restart=always
```
> 直接归属到tomcat-cluster.target中，最后面就不需要install在multi-user.target中了
> 上面是tomcat01.service，其他的只需要修改部分内容，其他copy即可

#### 2) 子tomcat的汇总target文件
target-file: `/etc/systemd/system/tomcat-cluster.target`
```
[Unit]
Description=main tomat cluster service
# Requires=tomcat01.service tomcat02.service tomcat03.service
# or
Wants=tomcat01.service tomcat02.service tomcat03.service

[Install]
WantedBy=multi-user.target
```
> tomcat-cluster.target配置为multi-user.target的子target  
> 如果使用Requires方式，tomcat-cluster.target会强依赖子tomcat的状态，其中任意一个子tomcat被关闭或启动失败，将会导致整个tomcat-cluster.target中的所有tomcat都处于failed状态。  
> 如果使用Wants方式，tomcat-cluster.target会弱依赖子tomcat的状态，任意一个子tomcat被关闭或者启动失败，不会影响整个tomcat-cluster.target中的其他tomcat的正常启动和运行状态。

#### 3) 管理方式
``` bash
# 启动、关闭、重启那些和普通的service没什么区别，但是不可以省略target后缀
sudo systemctl start tomcat-cluster.target
sudo systemctl stop tomcat-cluster.target
sudo systemctl restart tomcat-cluster.target

# 可以通过target来查看所有子tomcat的状态，但是看不到详细的进程信息
sudo systemctl status tomcat-cluster.target

# 可以单独查看子tomcat的状态
sudo systemctl status tomcat03
```
> 需要注意的点：
1. 无法通过kill的方式杀掉tomcat01的进程，因为我们配置了Restart=always