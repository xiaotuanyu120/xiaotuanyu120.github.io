---
title: zabbix: 1.1.0 install by docker-compose
date: 2020-07-07 21:46:00
categories: service/zabbix
tags: [zabbix,monitor]
---

### 1. zabbix installation
安装策略:
- 选择官方latest版本，而不是根据本地目录local进行编译
- zabbix-proxy选择mysql做数据库
- zabbix-server选择mysql做数据库
- 选择zabbix-web-nginx-mysql做web interface

``` bash
git clone https://github.com/zabbix/zabbix-docker.git
mkdir zabbix

# 根据安装策略拷贝相应的env文件
cp zabbix-docker/.env_srv zabbix
cp zabbix-docker/.env_db_mysql zabbix
cp zabbix-docker/.env_db_mysql_proxy zabbix
cp zabbix-docker/.env_prx zabbix
cp zabbix-docker/.env_prx_mysql zabbix
cp zabbix-docker/.env_web zabbix
cp zabbix-docker/.env_agent zabbix
cp zabbix-docker/.env_java zabbix
cp zabbix-docker/.MYSQL_PASSWORD zabbix
cp zabbix-docker/.MYSQL_ROOT_PASSWORD zabbix
cp zabbix-docker/.MYSQL_USER zabbix

# 根据安装策略，拷贝官方latest镜像版本的yaml文件
cp zabbix-docker/docker-compose_v3_centos_mysql_latest.yaml zabbix/zabbix.yml

# 根据安装策略删除无用的service
sed -i '/zabbix-proxy-sqlite3:/,/^$/d' zabbix/zabbix.yml
sed -i '/zabbix-web-apache-mysql:/,/^$/d' zabbix/zabbix.yml

# 解决"mbind: Operation not permitted"错误
# add the content below to mysql-server
#   cap_add: [ SYS_NICE ]

cd zabbix
docker-compose -f zabbix.yml up -d
```
> 容器会在zabbix目录下自动创建zbx_env目录来挂载

> [how to solve "mbind: Operation not permitted" error](https://github.com/docker-library/mysql/issues/303#issuecomment-643154859)

### 2. Zabbix server的主机监控
安装完毕并启动后，可以通过`ip:8081`来访问zabbix，默认的账号密码是`Admin:zabbix`。

登录后，会发现有个提示，默认创建的Zabbix server主机监控未收集到数据。查看zabbix-agent的容器日志，发现如下错误
```
no active checks on server [zabbix-server:10051]: host [3148636f1f4e] not found
```
这个显然是主机的名称配置问题，去web界面上，将Zabbix server的主机连接地址，改为`zabbix-agent`（因为zabbix-agent的容器service名称，即代表了zabbix-server机器）即可。