---
title: zabbix 1.1.1 install with podman
date: 2021-03-12 11:16:00
categories: service/zabbix
tags: [zabbix,podman]
---

### 1. install zabbix with podman
#### create pod
``` bash
podman pod create -p "80:8080" -p "443:8443" -p "10051:10051" --name zabbix
```

#### create server side container
``` bash
# database
mkdir -p /data/container/data/mysql/data
mkdir -p /data/container/runtime/mysql/secrets
date +%s | sha256sum | base64 | head -c 32 > /data/container/runtime/mysql/secrets/MYSQL_PASSWORD
date +%s | md5sum | base64 | head -c 32 > /data/container/runtime/mysql/secrets/MYSQL_ROOT_PASSWORD
podman run -it -d --pod zabbix --name mysql \
  -v /data/container/data/mysql/data:/var/lib/mysql:rw,Z \
  -v /data/container/runtime/mysql/secrets:/run/secrets:ro,Z \
  -e TZ="Asia/Shanghai" \
  -e MYSQL_USER=/run/secrets/zabbix \
  -e MYSQL_PASSWORD_FILE=/run/secrets/MYSQL_PASSWORD \
  -e MYSQL_ROOT_PASSWORD_FILE=/run/secrets/MYSQL_ROOT_PASSWORD \
  -e MYSQL_ALLOW_EMPTY_PASSWORD=false \
  -e MYSQL_DATABASE=zabbix \
  mysql:8.0 \
  mysqld \
  --character-set-server=utf8 \
  --collation-server=utf8_bin \
  --default-authentication-plugin=mysql_native_password

# zabbix-server-mysql
mkdir -p /data/container/data/zabbix/usr/{alertscripts,externalscripts}
mkdir -p /data/container/data/zabbix/var/{export,modules,enc,ssh_keys,mibs}
podman unshare chown -R 1997:0 /data/container/data/zabbix/var
podman run -it -d --pod zabbix --name zabbix-server \
  -v /data/container/data/zabbix/usr/alertscripts:/usr/lib/zabbix/alertscripts:ro,Z \
  -v /data/container/data/zabbix/usr/externalscripts:/usr/lib/zabbix/externalscripts:ro,Z \
  -v /data/container/data/zabbix/var/export:/var/lib/zabbix/export:rw,Z \
  -v /data/container/data/zabbix/var/modules:/var/lib/zabbix/modules:ro,Z \
  -v /data/container/data/zabbix/var/enc:/var/lib/zabbix/enc:ro,Z \
  -v /data/container/data/zabbix/var/ssh_keys:/var/lib/zabbix/ssh_keys:ro,Z \
  -v /data/container/data/zabbix/var/mibs:/var/lib/zabbix/mibs:ro,Z \
  -v /data/container/runtime/mysql/secrets:/run/secrets:ro,Z \
  -e TZ="Asia/Shanghai" \
  -e DB_SERVER_HOST=127.0.0.1 \
  -e DB_SERVER_PORT=3306 \
  -e MYSQL_USER=zabbix \
  -e MYSQL_PASSWORD_FILE=/run/secrets/MYSQL_PASSWORD \
  -e MYSQL_ROOT_PASSWORD_FILE=/run/secrets/MYSQL_ROOT_PASSWORD \
  -e MYSQL_DATABASE=zabbix \
  zabbix/zabbix-server-mysql:alpine-5.2-latest

# zabbix-web-apache-mysql
wget https://www.xxshell.com/download/sh/zabbix/ttf/msyh.ttf -O /data/container/runtime/zabbix/msyh.ttf
podman run -it -d --pod zabbix --name zabbix-web-apache-mysql \
  -v /data/container/runtime/mysql/secrets:/run/secrets:ro,Z \
  -v /data/container/runtime/zabbix/msyh.ttf:/usr/share/zabbix/assets/fonts/DejaVuSans.ttf:ro,Z \
  -e TZ="Asia/Shanghai" \
  -e DB_SERVER_HOST=127.0.0.1 \
  -e DB_SERVER_PORT=3306 \
  -e MYSQL_USER=zabbix \
  -e MYSQL_PASSWORD_FILE=/run/secrets/MYSQL_PASSWORD \
  -e MYSQL_ROOT_PASSWORD_FILE=/run/secrets/MYSQL_ROOT_PASSWORD \
  -e MYSQL_DATABASE=zabbix \
  -e ZBX_SERVER_HOST=127.0.0.1 \
  -e ZBX_SERVER_PORT=10051 \
  -e PHP_TZ="Asia/Shanghai" \
  zabbix/zabbix-web-apache-mysql:alpine-5.2-latest
```
> 之所以要替换zabbix-web-apache-mysql的字体，是为了解决中文字体口口口的乱码问题

#### create client service
因需要监控宿主机指标，所以没用container
``` bash
rpm -Uvh https://repo.zabbix.com/zabbix/5.2/rhel/8/x86_64/zabbix-release-5.2-1.el8.noarch.rpm
dnf clean all
dnf install -y zabbix-agent

# 设定允许的zabbix server连入列表
sed -Ei 's/^Server=.*$/Server=127.0.0.1/g' /etc/zabbix/zabbix_agentd.conf
# 设定agent要连接的zabbix server和proxy
sed -Ei 's/^ServerActive=.*$/ServerActive=127.0.0.1:10051/g' /etc/zabbix/zabbix_agentd.conf
# 设定agent监控主机的名称，需要和zabbix web上设定的名称一致（区分大小写）
sed -Ei 's/^Hostname=.*$/Hostname=Zabbix server/g' /etc/zabbix/zabbix_agentd.conf

systemctl enable zabbix-agent
systemctl start zabbix-agent
```

### 2. 问题
#### 如果zabbix web上显示ZBX不是绿色，可以在zabbix server上执行这个来刷新
``` bash
zabbix_get -s 172.25.52.137 -p 10050 -k agent.version
```
> [zabbix_get docs](https://www.zabbix.com/documentation/current/manual/concepts/get)