---
title: php extensions: 编译时增加mysql驱动模块
date: 2016-12-19 15:37:00
categories: service/php
tags: [php,mysql]
---

### 1. 选择一个库
mysqli，PDO_MySQL和mysql PHP扩展是基于C客户端库之上的轻量级容器。扩展可以使用mysqlnd库或libmysqlclient库。必须在编译PHP时决定使用哪个库。

从5.3.0开始，mysqlnd库成为了PHP发行版的一部分。 它提供了诸如延迟连接、查询缓存等功能，还有部分libmysqlclient不提供的功能，因此强烈建议使用内置的mysqlnd库。 有关更多详细信息，请参阅mysqlnd文档，以及它提供的功能和功能的列表。

示例：Configure commands for using mysqlnd or libmysqlclient
``` bash
# 强烈推荐, 使用mysqlnd库来编译扩展
./configure --with-mysqli=mysqlnd --with-pdo-mysql=mysqlnd --with-mysql=mysqlnd

# 可选推荐, compiles with mysqlnd as of PHP 5.4
./configure --with-mysqli --with-pdo-mysql --with-mysql

# 不推荐, 使用libmysqlclient编译
./configure --with-mysqli=/path/to/mysql_config --with-pdo-mysql=/path/to/mysql_config --with-mysql=/path/to/mysql_config
```

特别推荐使用mysqlnd替代MySQL Client Server library (libmysqlclient)。支持所有的类，而且还在持续被提升。

[原文英文文档](http://php.net/manual/zh/mysqlinfo.library.choosing.php)

### 2. docker在php5.6和php7.4下面安装mysql扩展
```
# php 5.6
FROM php:5.6-apache
RUN docker-php-ext-config mysql --with-mysql=mysqlnd \
    && docker-php-ext-install mysqli pdo-mysql
```

```
# php 7.4
FROM php:7.4-apache
RUN ocker-php-ext-install mysqli pdo-mysql
```
> php7.4 默认就是mysqlnd的driver，所以不用额外配置

### 3. 检查mysql扩展信息
```
php -r 'print_r(phpinfo());' | grep mysql
php -m | grep mysql
```