---
title: pureftpd: 1.1.1 安装 - 1.0.36
date: 2015-01-22 02:54:00
categories: service/ftp
tags: [ftp]
---
### pureftpd: 1.1.1 安装 - 1.0.36

---

### 1. 编译安装pure-ftpd
``` bash
cd /usr/local/src
wget http://download.pureftpd.org/pub/pure-ftpd/releases/pure-ftpd-1.0.36.tar.gz
tar -zxvf pure-ftpd-1.0.36.tar.gz
cd pure-ftpd-1.0.36
./configure \
    --prefix=/usr/local/pureftpd --without-inetd \
    --with-altlog --with-puredb --with-throttling \
    --with-peruserlimits --with-tls
make
make install
```

---

### 2. 准备配置文件与启动命令脚本
``` bash
cd configuration-file
cp pure-ftpd.conf /usr/local/pureftpd/etc/pure-ftpd.conf
cp pure-config.pl /usr/local/pureftpd/sbin/pure-config.pl
chmod 755 /usr/local/pureftpd/sbin/pure-config.pl
```

---

### 3. 编辑配置文件
``` bash
vim /usr/local/pureftpd/etc/pure-ftpd.conf
============================================================================
ChrootEveryone              yes
BrokenClientsCompatibility  no
MaxClientsNumber            50
Daemonize                   yes
MaxClientsPerIP             8
VerboseLog                  no
DisplayDotFiles             yes
AnonymousOnly               no
NoAnonymous                 no
SyslogFacility              ftp
DontResolve                 yes
MaxIdleTime                 15
PureDB                        /usr/local/pureftpd/etc/pureftpd.pdb
# 这个就是pure-pw mkdb生成的文件
LimitRecursion              3136 8
AnonymousCanCreateDirs      no
MaxLoad                     4
AntiWarez                   yes
Umask                       133:022
MinUID                      100
AllowUserFXP                no
AllowAnonymousFXP           no
ProhibitDotFilesWrite       no
ProhibitDotFilesRead        no
AutoRename                  no
AnonymousCantUpload         no
PIDFile                     /usr/local/pureftpd/var/run/pure-ftpd.pid
MaxDiskUsage               99
CustomerProof              yes
============================================================================
```

---

### 4. 系统环境准备

``` bash
# 创建ftp目录
mkdir /data/ftp

# ftp依赖的系统用户
useradd pureftp -s /sbin/nologin

# ftp的虚拟登录用户及其密码数据库
/usr/local/pureftpd/bin/pure-pw useradd ftp01 -u pureftp -d /data/ftp
Password:
Enter it again:
# 此命令生成的文件在/usr/local/pureftpd/etc/pureftpd.passwd

# 生成密码库文件
/usr/local/pureftpd/bin/pure-pw mkdb
/usr/local/pureftpd/bin/pure-pw list
ftp01               /data/ftp/./

# 删除用户
/usr/local/pureftpd/bin/pure-pw userdel ftp02
```

---

### 5. 启动pure-ftpd
``` bash
/usr/local/pureftpd/sbin/pure-config.pl /usr/local/pureftpd/etc/pure-ftpd.conf
Running: /usr/local/pureftpd/sbin/pure-ftpd -A -c50 -B -C8 -D -fftp -H -I15 -lpuredb:/usr/local/pureftpd/etc/pureftpd.pdb -L3136:8 -m4 -s -U133:022 -u100 -g/usr/local/pureftpd/var/run/pure-ftpd.pid -k99 -Z
```
