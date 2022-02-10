---
title: MYSQL-配置：配置字符集为utf8
date: 2020-10-21 23:32:00
categories: database/mysql
tags: [database,mysql]
---

### 1. mysql配置字符集为utf8
``` bash
[client]
default-character-set=utf8

[mysql]
default-character-set=utf8

[mysqld]
# 禁止客户端和服务端协商字符集格式
character-set-client-handshake=false
character-set-server=utf8
collation-server=utf8_general_ci

default-storage-engine=INNODB
```

### 2. 将已经创建的库或表转换为utf8
``` sql
-- 将数据库转换字符集设定
ALTER DATABASE databasename CHARACTER SET utf8 COLLATE utf8_general_ci

-- 将数据库表转换字符集设定
ALTER TABLE tablename CONVERT TO CHARACTER SET utf8 COLLATE utf8_general_ci
```

### 3. 检查字符集设定
``` sql
SHOW VARIABLES LIKE 'character%';
SHOW VARIABLES LIKE 'collation%';
```