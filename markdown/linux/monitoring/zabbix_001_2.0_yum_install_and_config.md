---
title: zabbix: 安装 - yum(2.0)
date: 2015-11-27 20:15:00
categories: linux/monitoring
tags: [zabbix]
---

## 1. preparation
``` bash
# 准备工具
yum install -y vim wget epel-release

# 安装httpd、mysql、php
yum install -y httpd  mysql-server mysql mysql-libs php php-mysql php-bcmath php-gd php-mbstring
```
## 2. zabbix installation
``` bash
## 安装zabbix服务
# yum install -y zabbix20 zabbix20-agent zabbix20-server  zabbix20-server-mysql zabbix20-web zabbix20-web-mysql net-snmp-devel
```

## 3. service start & checking ports
``` bash
# 启动httpd、mysqld、zabbix服务
service mysqld start
service zabbix-server start
service zabbix-agent start
service httpd start

# 设置服务开机启动
chkconfig --add mysqld
chkconfig --add zabbix-server
chkconfig --add zabbix-agent 
chkconfig --add httpd

chkconfig mysqld on
chkconfig zabbix-server on
chkconfig zabbix-agent on
chkconfig httpd on
 
# 检查端口是否监听
netstat -lnpt |grep -E 'zabbix|mysqld|httpd'
tcp        0      0 0.0.0.0:10050               0.0.0.0:*                   LISTEN      2002/zabbix
tcp        0      0 0.0.0.0:3306                0.0.0.0:*                   LISTEN      1965/mysqld
tcp        0      0 :::10050                    :::*                        LISTEN      2002/zabbix
tcp        0      0 :::80                       :::*                        LISTEN      1767/httpd
```

## 4. MySQL preparation
``` bash
# set root password
mysqladmin -u root password 'new-password'

# create database & restore zabbix sql data
mysql -uroot -p --default-character-set=utf8 zabbix < /usr/share/zabbix-mysql/schema.sql
mysql -uroot -p --default-character-set=utf8 zabbix < /usr/share/zabbix-mysql/images.sql
mysql -uroot -p --default-character-set=utf8 zabbix < /usr/share/zabbix-mysql/data.sql

# create mysql user for zabbix
mysql -uroot -p -e "grant all on zabbix.* to 'zabbix'@'localhost' identified by 'sudozabbix'"
```

## 5. selinux & iptables
``` bash
# 暂时关闭iptables和selinux
service iptables stop
chkconfig iptables off
setenforce 0
vim /etc/selinux/config
*******************************
SELINUX=disabled
**********************************
```

## 6. 配置zabbix
### 1. 局域网内，用浏览器访问`http://zabbix-server-ip/zabbix`
按照错误提示修改timezone

```
date(): It is not safe to rely on the system's timezone settings. You are *required* to use the date.timezone setting or the date_default_timezone_set() function. In case you used any of those methods and you are still getting this warning, you most likely misspelled the timezone identifier. We selected 'Asia/Chongqing' for 'CST/8.0/no DST' instead [include/page_header.php:186]
```

``` bash
vim /etc/php.ini
***************************************
date.timezone = Asia/Chongqing
***************************************
service httpd restart
```
 
### 2. 刷新访问页面`http://zabbix-server-ip/zabbix`
点击next，进入check of pre-requisites页面，按照错误提示修改相应项

```
                                 Current value        Required
PHP option post_max_size                8M           16M                    Fail
PHP option max_execution_time           30           300             Fail
PHP option max_input_time               60           300             Fail
```

``` bash
vim /etc/php.ini
***************************************
post_max_size = 16M
max_execution_time = 300
max_input_time = 300
***************************************
service httpd restart
```

### 3. 刷新页面，当全部项显示ok状态的时候，点击next
输入user和password，记得最后test一下，查看是否返回ok，保证信息输入正确
![](/static/images/docs/linux/monitoring/zabbix_001-001.png)

host填写127.0.0.1
![](/static/images/docs/linux/monitoring/zabbix_001-002.png)
 
接下来是输入信息的汇总展示
![](/static/images/docs/linux/monitoring/zabbix_001-003.png)
 
最后是安装完成，并提示你安装过程的配置文件是在"/etc/zabbix/web/zabbix.conf.php"
![](/static/images/docs/linux/monitoring/zabbix_001-004.png)
 
登录界面，用默认的username:admin, password：zabbix登录
![](/static/images/docs/linux/monitoring/zabbix_001-005.png)
 
### 4. 登陆后界面显示zabbix服务运行状态是no
``` bash
vim /etc/zabbix/zabbix_server.conf
***********************************************************
DBHost=localhost
DBName=zabbix
DBUser=zabbix
DBPassword=your_password
***********************************************************

service zabbix-server restart
service zabbix-agent restart
```

![](/static/images/docs/linux/monitoring/zabbix_001-006.png)