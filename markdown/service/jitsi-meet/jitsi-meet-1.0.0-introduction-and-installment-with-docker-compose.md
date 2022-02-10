---
title: jitsi meet: 1.0.0 introduction and installation with docker compose
date: 2021-04-09 10:25:00
categories: service/jitsi-meet
tags: [xmpp]
---

## 1. 介绍
jitsi 是一套开源代码的合集，用于提供视频会议，类似于zoom。

### 1.1 组件介绍
- jitsi meet：是一个WebRTC兼容的JavaScript前端程序，使用Jitsi Videobridge提供高质量、可扩展的视频会议。
- jitsi videobridge（JVB）：WebRTC兼容服务器，旨在在会议参与者之间路由视频流。
- jitsi conference focus（jicofo）：Jitsi Meet会议中使用的服务端focus组件，用于管理媒体会话，并充当每个参与者和video bridge之间的负载平衡器。
- jitsi gateway to SIP（jigasi）：服务器端应用程序，允许常规SIP客户端加入Jitsi Meet会议
- Jitsi Broadcasting Infrastructure (jibri) ：用于录制或者steam jitsi meet会议的一组工具，通过启动在虚拟帧缓冲区中渲染的Chrome实例，并使用ffmpeg捕获和编码输出。
- 外部组件
  - prosody：xmpp服务器

### 1.2 架构图
![](/static/images/docs/service/jitsi-meet/jitsiMeetArchitectureDiagram.png)

## 2. docker-compose启动jitsi meet
### 2.1 [下载jitsi meet](https://github.com/jitsi/docker-jitsi-meet/releases)
``` bash
wget https://github.com/jitsi/docker-jitsi-meet/archive/refs/tags/stable-5390-3.tar.gz
tar zxf stable-5390-3.tar.gz
cd docker-jitsi-meet-stable-5390-3
```

### 2.2 创建并调整`.env`配置文件
``` bash
cp env.example .env


## 修改密码配置
./gen-passwords.sh
# 运行密码生成脚本，会生成四个密码，并替换.env文件中的密码配置
#- JICOFO_COMPONENT_SECRET=${JICOFO_COMPONENT_SECRET}
#- JICOFO_AUTH_PASSWORD=${JICOFO_AUTH_PASSWORD
#- JVB_AUTH_PASSWORD=${JVB_AUTH_PASSWORD}
#- JIGASI_XMPP_PASSWORD=${JIGASI_XMPP_PASSWORD}
#- JIBRI_RECORDER_PASSWORD=${JIBRI_RECORDER_PASSWORD}
#- JIBRI_XMPP_PASSWORD=${JIBRI_XMPP_PASSWORD}


## 修改生成的配置文件储存目录
# Directory where all configuration will be stored
# 组件的配置文件生成目录配置：CONFIG=~/.jitsi-meet-cfg
mkdir -p ~/.jitsi-meet-cfg/{web/letsencrypt,transcripts,prosody/config,prosody/prosody-plugins-custom,jicofo,jvb,jigasi,jibri}


## 修改常规配置
# Exposed HTTP port
HTTP_PORT=8000

# Exposed HTTPS port
HTTPS_PORT=8443

# System time zone
TZ=Aisa/Shanghai

# Public URL for the web service (required)
PUBLIC_URL=https://meet.example.com:8443

# IP address of the Docker host
# See the "Running behind NAT or on a LAN environment" section in the Handbook:
# https://jitsi.github.io/handbook/docs/devops-guide/devops-guide-docker#running-behind-nat-or-on-a-lan-environment
DOCKER_HOST_ADDRESS=192.168.1.1
```

### 2.3 启动程序
``` bash
docker-compose up -d
```

### 2.4 开放以下端口的防火墙
- 8000/tcp for Web UI HTTP (really just to redirect, after uncommenting ENABLE_HTTP_REDIRECT=1 in .env)
- 8443/tcp for Web UI HTTPS
- 4443/tcp for RTP media over TCP
- 10000/udp for RTP media over UDP

### 2.5 访问
https://meet.example.com:8443


> [参考安装文档](https://jitsi.github.io/handbook/docs/devops-guide/devops-guide-docker)