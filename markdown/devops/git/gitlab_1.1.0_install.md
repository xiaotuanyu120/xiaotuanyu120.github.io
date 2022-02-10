---
title: gitlab: 1.1.0 安装(centos6)
date: 2016-08-26 15:19:00
categories: devops/git
tags: [devops,gitlab,git]
---

### 0. 文档
[gitlab centos6 installation guide](https://about.gitlab.com/downloads/#centos6)  
在上面的的文档中，你可以选择不同的linux版本切换文档

### 1. 安装gitlab
#### 1) Install and configure the necessary dependencies
``` bash
yum install curl openssh-server openssh-clients postfix cronie
service postfix start
chkconfig postfix on
lokkit -s http -s ssh
```
> lokkit 会修改防火墙规则，如果是线上已经使用中的机器，记得备份iptables规则

#### 2) Add the GitLab package server and install the package
``` bash
curl -sS https://packages.gitlab.com/install/repositories/gitlab/gitlab-ce/script.rpm.sh | sudo bash
yum install gitlab-ce
# 下载中断的话，可重新执行yum命令继续下载

gitlab-ctl reconfigure
```

---

### 2. docker-compose安装
``` bash
cat << EOF > docker-compose-gitlab.yml
version: '3'
services:
  web:
    container_name: gitlab
    image: gitlab/gitlab-ce:11.11.8-ce.0
    restart: always
    hostname: 'git.example.net'
    environment:
      GITLAB_OMNIBUS_CONFIG: |
        external_url 'http://<your domain here>'
        nginx['client_max_body_size'] = '2048m'
        nginx['proxy_max_temp_file_size'] = '2048m'
        gitlab_rails['rack_attack_git_basic_auth'] = {
           'enabled' => true,
           'ip_whitelist' => ["127.0.0.1","<your auth ip here>"],
           'maxretry' => 10,
           'findtime' => 60,
           'bantime' => 3600
        }
    ports:
      - '80:80'
      - '443:443'
    volumes:
      - '/data/docker/runtime/gitlab/config:/etc/gitlab'
      - '/data/docker/data/gitlab/logs:/var/log/gitlab'
      - '/data/docker/data/gitlab/data:/var/opt/gitlab'
EOF

docker-compose -f docker-compose-gitlab.yml up -d
```
> 更多environment配置见：[Omnibus GitLab template](https://gitlab.com/gitlab-org/omnibus-gitlab/blob/master/files/gitlab-config-template/gitlab.rb.template)