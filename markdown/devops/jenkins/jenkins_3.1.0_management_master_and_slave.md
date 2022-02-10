---
title: jenkins: 3.1.0 管理slave节点
date: 2019-10-08 10:56:00
categories: devops/jenkins
tags: [docker,jenkins]
---

### 1. 管理slave节点
#### step 0. 和slave节点通信有几种方式
- SSH
- windows administrative account
- Java Web Start (JNLP)

你可以选择最适合你环境的，我们这里使用SSH的方式


#### step 1. 生成ssh文件
在jenkins-master上执行
``` bash
# 使用jenkins用户执行下面命令

# DOCKER
# 如果使用的是docker启动的jenkins，可以执行
mkdir jenkins
chmod 777 jenkins
docker run --rm -it -v `pwd`/jenkins:/var/jenkins_home jenkins:lts ssh-keygen
chmod 755 jenkins
# 在./jenkins/.ssh目录得到id_rsa和id_rsa.pub两个文件

# 非DOCKER
su - jenkins
ssh-keygen
# 在/home/jenkins/.ssh目录得到id_rsa和id_rsa.pub两个文件
```

#### step 2. 在jenkins上配置凭证
- 选择credentials
- 点击global域链接
- 选择增加credentials
- 填写信息
  - Kind: SSH Username with private key
  - Scope: Global
  - Username: jenkins
  - Private key: Enter directly and paste the 'id_rsa' private key of Jenkins user from the master server.

#### step 3. 启动docker-slave
``` bash
cat << EOF > docker-compose-jenkins-slave.yml
version: '3'
services:
  jenkins-slave:
    image: 'jenkins/ssh-slave'
    container_name: jenkins-slave
    restart: always
    volumes:
      - /data/jenkins_home:/var/jenkins_home
      - /var/run/docker.sock:/var/run/docker.sock
      - /usr/bin/docker:/usr/bin/docker
    environment:
      - JAVA_ARGS=-Dorg.apache.commons.jelly.tags.fmt.timeZone=Asia/Shanghai
    entrypoint:
      - setup-sshd
      - "<id_rsa.pub>"
EOF

docker-compose -f docker-compose-jenkins-slave.yml up -d
```

#### step 4. jenkins web端配置上新的slave
- Manage Jenkins
- Manage Nodes
- New Node
- 输入node名称，选择permanent agent，点击OK
- 输入node节点详细信息
  - Description: slave01 node agent server
  - Remote root directory: /home/jenkins
  - Labels: slave01
  - Launch method: Launch slave agent via SSH, type the host ip address '10.0.15.21', choose the authentication using 'Jenkins' credential.


- Manage Jenkins
- Configure System
- 配置slave