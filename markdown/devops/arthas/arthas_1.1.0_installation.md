---
title: arthas: 1.1.0 安装使用
date: 2019-12-09 15:25:00
categories: devops/arthas
tags: [devops,arthas,jvm]
---

### 0. 理论
Arthas 是Alibaba开源的Java诊断工具，深受开发者喜爱。

当你遇到以下类似问题而束手无策时，Arthas可以帮助你解决：
- 这个类从哪个 jar 包加载的？为什么会报各种类相关的 Exception？
- 我改的代码为什么没有执行到？难道是我没 commit？分支搞错了？
- 遇到问题无法在线上 debug，难道只能通过加日志再重新发布吗？
- 线上遇到某个用户的数据处理有问题，但线上同样无法 debug，线下无法重现！
- 是否有一个全局视角来查看系统的运行状况？
- 有什么办法可以监控到JVM的实时运行状态？
- 怎么快速定位应用的热点，生成火焰图？

arthas支持web console，但是那个web页面只能一次访问单台机器，为了方便管理，最好是使用arthas tunnel server。

arthas tunnel server的工作原理是：
```
browser <-> arthas tunnel server <-> arthas tunnel client <-> arthas agent
```
PS: 这样我们就可以通过一个固定的web界面，通过输入不同的agent id，然后来排查不同服务器上的jvm了。

### 1. 启动arthas tunnel server
``` bash
ARTHAS_TUNNEL_SERVER_DIR=/usr/local/arthas-tunnel-server

[[ -d ${ARTHAS_TUNNEL_SERVER_DIR} ]] || mkdir -p ${ARTHAS_TUNNEL_SERVER_DIR}

# download arthas-tunnel-server
wget https://github.com/alibaba/arthas/releases/download/arthas-all-3.1.7/arthas-tunnel-server-3.1.7.jar \
  -o ${ARTHAS_TUNNEL_SERVER_DIR}/arthas-tunnel-server.jar

cat << EOF > ${ARTHAS_TUNNEL_SERVER_DIR}/asts.sh
nohup java -jar ${ARTHAS_TUNNEL_SERVER_DIR}//arthas-tunnel-server.jar &
EOF

cd ${ARTHAS_TUNNEL_SERVER_DIR} && sh ${ARTHAS_TUNNEL_SERVER_DIR}/asts.sh
```

### 2. 启动arthas agent
``` bash
JAVA_HOME=/usr/java/jdk1.7.0_79
ARTHAS_AGENT_DIR=/usr/local/arthas-agent
ARTHAS_TUNNEL_SERVER=127.0.0.1

[[ -d ${ARTHAS_AGENT_DIR} ]] || mkdir -p ${ARTHAS_AGENT_DIR}
cd ${ARTHAS_AGENT_DIR} && wget https://alibaba.github.io/arthas/arthas-boot.jar

# start agent
cat << EOF > ${ARTHAS_AGENT_DIR}/startup.sh
sudo -u tomcat -EH ${JAVA_HOME}/bin/java -jar ${ARTHAS_AGENT_DIR}/arthas-boot.jar --tunnel-server 'ws://${ARTHAS_TUNNEL_SERVER}:7777/ws'
EOF

sh ${ARTHAS_AGENT_DIR}/startup.sh
```