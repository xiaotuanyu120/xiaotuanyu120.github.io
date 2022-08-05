---
title: cnyunwei: 安装和配置
date: 2015-12-28 19:57:00
categories: linux/monitoring
tags: [linux,monitoring]
---

## 1. cnyunwei下载及系统安装
ISO文件下载连接：http://pan.baidu.com/s/1eRcnfYa 提取密码：nz5v
 
### 1.1 安装过程
- 引导
- 选择安装版本（我选的cati+nagios+nconf-x64中文版本）
- 重启

## 2. 安装后配置
### 2.1 修改密码

修改root密码（默认root：www.cnyunwei.com）

``` bash
passwd root
```

修改cati密码（默认admin：www.cnyunwei.com）

- 访问http://system_ip/
- 输入默认帐号密码登录
- console >user management >点击admin >修改密码
> 访问的时候提示连接不上mysql，去机器上启动一下mysql就可以了

修改nagios密码（默认nagiosadmin：www.cnyunwei.com）

``` bash
/usr/bin/htpasswd -c /usr/local/nagios/etc/htpasswd.users nagiosadmin
```

修改nconf密码（默认admin：www.cnyunwei.com）

``` bash
vi /var/www/nconf/config/.file_accounts.php 
**********************************
admin::your_password::admin::Administrator::
**********************************
```

mysql的帐号密码（root：www.cnyunwei.com）

``` bash
mysql> select host,user from mysql.user;
+-----------------------+-----------+
| host                  | user      |
+-----------------------+-----------+
| 127.0.0.1             | root      |
| localhost             |           |
| localhost             | cactiuser |
| localhost             | nconfuser |
| localhost             | root      |
| localhost.localdomain |           |
| localhost.localdomain | root      |
+-----------------------+-----------+
## cacti和nconf都有自己的数据库帐号
```

### 2.2 配置selinux
``` bash
setenforce 0
vi /etc/selinux/config
************************************
## 修改下行为
SELINUX=disabled
************************************
```

## 3. CACTI配置及使用
### 监控服务端SNMP配置
### **snmp配置**
``` bash
vim /etc/snmp/snmpd.conf
**********************************
## 修改下面一行为新的内容
##view    systemview    included   .1.3.6.1.2.1.1
view    systemview    included   .1.3.6.1.2.1
## 修改下面一行为新的内容
## com2sec notConfigUser  127.0.0.1        public
com2sec notConfigUser 58.64.214.61        public
**********************************
```

#### **测试一下snmp的连接**
``` bash
snmpnetstat -v 2c -c public -Ca -Cp tcp localhost
Active Internet (tcp) Connections (including servers)
Proto Local Address          Remote Address         (state)
tcp   *.ssh                  *.*                   LISTEN
tcp   *.mysql                *.*                   LISTEN
tcp   *.5668                 *.*                   LISTEN
tcp   58.64.214.61.ssh       61.14.162.11.60403    ESTABLISHED
tcp   localhost.smtp         *.*                   LISTEN
tcp   localhost.smux         *.*                   LISTEN
tcp   localhost.5668         localhost.45809       ESTABLISHED
tcp   localhost.45809        localhost.5668        ESTABLISHED
```

#### **验证收集数据的php**
``` bash
php /var/www/html/poller.php 
OK u:0.01 s:0.00 r:2.06
OK u:0.01 s:0.00 r:2.06
OK u:0.01 s:0.00 r:2.06
OK u:0.01 s:0.00 r:2.06
OK u:0.01 s:0.00 r:2.06
OK u:0.01 s:0.00 r:2.06
OK u:0.01 s:0.00 r:2.06
OK u:0.01 s:0.00 r:2.06
OK u:0.01 s:0.00 r:2.06
OK u:0.01 s:0.00 r:2.06
OK u:0.01 s:0.00 r:2.06
。。。。。。
```
poller.php是主要的信息收集程序

## 4. 添加监控

### 4.1 监控本机
console > device > localhost(或127.0.0.1)

点击后保证下面几个设置

snmp version： version2

如果希望添加监控的图形，可以点击右上角的"为这个主机添加图形"

然后把图形添加进图形树
 
### 4.2 监控远程主机（被监控端配置）
#### **安装snmp**
``` bash
yum install -y net-snmp net-snmp-utils net-snmp-libs
```
#### **修改配置文件**
``` bash
vim /etc/snmp/snmpd.conf 
******************************************
## 修改下面两行
com2sec notConfigUser 58.64.214.61        public
view    systemview    included   .1.3.6.1.2.1
******************************************
```

#### **启动snmp服务**
``` bash
chkconfig snmpd on
service snmpd start
Starting snmpd:                                            [  OK  ]
```
#### **开放防火墙端口**
``` bash
vim /etc/sysconfig/iptables
****************************************
## 注意是udp
-A INPUT -p udp -m udp --dport 161 -j ACCEPT
****************************************

service iptables restart
```

### 4.3 监控服务端测试
``` bash
snmpnetstat -v 2c -c public -Can -Cp tcp 59.188.30.50
Active Internet (tcp) Connections (including servers)
Proto Local Address          Remote Address         (state)
tcp   *.22                   *.*                   LISTEN
tcp   *.80                   *.*                   LISTEN
tcp   *.3306                 *.*                   LISTEN
tcp   59.188.30.50.22        61.14.162.7.61106     ESTABLISHED
tcp   59.188.30.50.22        61.14.162.11.51034    ESTABLISHED
tcp   127.0.0.1.25           *.*                   LISTEN
tcp   127.0.0.1.199          *.*                   LISTEN
tcp   127.0.0.1.9000         *.*                   LISTEN
You have new mail in /var/spool/mail/root
```

### 4.4 web页面设定
#### **添加主机**
console > device > add

#### **填写以下字段**
- description： 主机名称
- hostname： ip地址
- host template： 主机模版
- 是否监控：勾选
- 然后保存，成功以后你会发现下面会出现snmp采集数据正在进行
- 添加图形
- 添加阀值
- 把主机添加到图形树

## 5. 邮件报警配置
### 5.1 修改主机名
将主机名修改为cnyunwei.com，修改/etc/sysconfig/network
### 5.2 安装sendmail，关闭postfix
``` bash
service postfix stop
chkconfig postfix off
yum install sendmail -y
service sendmail start
chkconfig sendmail on
```
### 5.3 cacti 管理界面修改
在设置-邮件/域名解析选项卡中，如图
![](/static/images/docs/linux/monitoring/cnyunwei-01.png)

> 备注：
> - 测试邮件：相当于收件人，就是写一个邮件地址，将邮件发送到此邮箱，建议使用163邮箱，其他邮箱可能会被屏蔽掉，
> - 邮件服务 : 需要选smtp，不知道为什么sendmail 会报错，但是我们真正发邮件还是走的sendmail，只不过这里选择smtp
> - 发件人地址：一般就是root@主机名,我们上边设置的主机名是cnyunwei.com，所以这里写root@cnyunwei.com
> - smtp 服务器主机名：127.0.0.1 端口 25 dns 8.8.8.8 202.106.0.20 
> - 最后发送一封测试邮件，以确保邮件配置正确。

### 5.4 报警/阀值的设置,如图所示
![](/static/images/docs/linux/monitoring/cnyunwei-02.png)

### 5.5 设置完毕后只是宕机可以收到短信，但是图形报警还是不可以，需要为图形添加阀值
阀值的话可以通过阀值模板统一部署，也可以自己一条一条定义，这里就不在介绍

> 注意：监控端口流量图形可以用基线监控，硬盘分区可以用百分比数值来监控