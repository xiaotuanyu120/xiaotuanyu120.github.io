---
title: mysql 1.0.0: 安装教程
date: 2015-01-07 05:32:00
categories: database/mysql
tags: [lamp,mysql]
---
### mysql 1.0.0: 安装教程

---

### 0. 脚本源码及安装包
github源码链接：https://github.com/xiaotuanyu120/install-lnmp

---

### 1. MySQL 5.1.72/5.1.73安装脚本
``` bash
cat installmysql5172.sh
*********************************************************
#!/bin/bash

## env setting
BASEDIR=/usr/local/mysql
DATADIR=/data/mysql
PASSWORD=adminmysql
PIDFILE=/usr/local/mysql/mysql.pid

## mysql base env install
yum install gcc gcc-c++ cmake ncurses-devel -y
yum groupinstall base "Development Tools" -y

## create user
groupadd mysql
useradd -r -g mysql mysql

## source package unzip
[[ -d mysql ]] || mkdir mysql && rm -rf mysql && mkdir mysql
tar zxvf mysql-5.1.72.tar.gz -C mysql
mv ./mysql/mysql-5.1.72/* ./mysql/
cd mysql

## mysql install
./configure --prefix=$BASEDIR --datadir=$DATADIR \
--with-mysqld-user=mysql --with-charset=utf8 --with-extra-charsets=all
make
make install

mkdir -p $DATADIR
chown -R mysql:mysql $BASEDIR
chown -R mysql:mysql $DATADIR

## mysql initial
./scripts/mysql_install_db --datadir=$DATADIR --user=mysql
cp ./support-files/mysql.server /etc/init.d/mysqld
rm -f /etc/my.cnf
cp support-files/my-large.cnf /etc/my.cnf
chmod 755 /etc/init.d/mysqld

sed -inr "s#^basedir=#basedir=$BASEDIR#g" /etc/init.d/mysqld
sed -inr "s#^datadir=#datadir=$DATADIR#g" /etc/init.d/mysqld
sed -inr "s#^pid_file=#pid_file=$PIDFILE#g" /etc/init.d/mysqld

sed -i "/\[mysqld\]/abasedir=$BASEDIR" /etc/my.cnf
sed -i "/\[mysqld\]/adatadir=$DATADIR" /etc/my.cnf
sed -i "/\[mysqld\]/apid_file=$PIDFILE" /etc/my.cnf

## service start and enanble
chkconfig mysqld on
/etc/init.d/mysqld start
$BASEDIR/bin/mysqladmin -u root password "$PASSWORD"
*********************************************************
```

---

### 2. MySQL 5.5.49/5.6.30安装脚本
``` bash
# 不同之处只是版本号和配置文件，其他都一样
cat installmysql5630.sh
*********************************************************
#!/bin/bash

## env setting
BASEDIR=/usr/local/mysql
DATADIR=/data/mysql
PASSWORD=adminmysql
PIDFILE=/usr/local/mysql/mysql.pid

## mysql base packages installation
yum install cmake gcc gcc-c++ ncurses-devel -y
yum groupinstall base "Development Tools" -y

## create user
groupadd mysql
useradd -r -g mysql mysql

## unzip source package
[[ -d mysql ]] || mkdir mysql && rm -rf ./mysql && mkdir mysql
tar zxvf mysql-5.6.30.tar.gz -C mysql
mv ./mysql/mysql-5.6.30/* ./mysql/
cd mysql

## mysql install
cmake -DCMAKE_INSTALL_PREFIX=/usr/local/mysql \
-DMYSQL_DATADIR=/data/mysql -DMYSQL_USER=mysql -DMYSQL_TCP_PORT=3306 \
-DWITH_MYISAM_STORAGE_ENGINE=1 -DWITH_INNOBASE_STORAGE_ENGINE=1 \
-DWITH_MEMORY_STORAGE_ENGINE=1 -DWITH_READLINE=1 \
-DENABLED_LOCAL_INFILE=1 -DWITH_EXTRA_CHARSETS=all \
-DDEFAULT_CHARSET=utf8 -DDEFAULT_COLLATION=utf8_general_ci
make
make install

mkdir -p $DATADIR
chown -R mysql:mysql $BASEDIR
chown -R mysql:mysql $DATADIR

## initialize database
cd $BASEDIR
./scripts/mysql_install_db --datadir=$DATADIR --user=mysql
cp ./support-files/mysql.server /etc/init.d/mysqld
rm -f /etc/my.cnf

## 5.6.30是my-default.cnf，不同于5.5.49
cp ./support-files/my-large.cnf /etc/my.cnf
chmod 755 /etc/init.d/mysqld

sed -inr "s#^basedir=#basedir=$BASEDIR#g" /etc/init.d/mysqld
sed -inr "s#^datadir=#datadir=$DATADIR#g" /etc/init.d/mysqld
sed -inr "s#^pid_file=#pid_file=$PIDFILE#g" /etc/init.d/mysqld

sed -i "/\[mysqld\]/abasedir=$BASEDIR" /etc/my.cnf
sed -i "/\[mysqld\]/adatadir=$DATADIR" /etc/my.cnf
sed -i "/\[mysqld\]/apid_file=$PIDFILE" /etc/my.cnf

## service start and enable
chkconfig mysqld on
service mysqld start
$BASEDIR/bin/mysqladmin -u root password "$PASSWORD"
*********************************************************
```

---

### 3. 脚本中MySQL配置说明
``` bash
## 脚本中配置项及其说明
## 启动脚本/etc/init.d/mysqld配置
basedir - 指定mysql目录
datadir - 指定mysql的数据目录
pid_file - 指定mysql的pid文件路径

## 配置文件/etc/my.cnf配置
basedir - 指定mysql目录
datadir - 指定mysql的数据目录
pid_file - 指定mysql的pid文件路径
```

---

### 4. mysql服务版本查看
``` bash
/usr/local/mysql/bin/mysql -V
/usr/local/mysql/bin/mysql  Ver 14.14 Distrib 5.5.49, for Linux (x86_64) using readline 5.1
```
