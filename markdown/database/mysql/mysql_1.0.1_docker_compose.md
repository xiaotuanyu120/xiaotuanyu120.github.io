---
title: mysql 1.0.1: docker-compose(单实例和主从)
date: 2020-04-21 09:08:00
categories: database/mysql
tags: [docker,docker-compose,mysql]
---

### 1. mysql
``` yaml
version: '3'
services:
  db:
    image: mysql:5.7.29
    container_name: db
    command: --default-authentication-plugin=mysql_native_password
    restart: always
    environment:
      MYSQL_ROOT_PASSWORD: "root_password"
      MYSQL_DATABASE: database_name
      MYSQL_USER: database_user
      MYSQL_PASSWORD: "database_password"
    volumes:
      - '/data/docker/data/db/mysql:/var/lib/mysql'

# networks:
#   default:
#     external:
#       name: production
```

### 2. mysql-replication
``` yaml
version: '3'
services:
  db-master:
    image: bergerx/mysql-replication:5.7
    container_name: db-master
    restart: always
    environment:
      MYSQL_ALLOW_EMPTY_PASSWORD: 1
      REPLICATION_USER: database-user
      REPLICATION_PASSWORD: "database-password"
    ports:
      - '33063:3306'
    volumes:
      - '/data/docker/data/db/mysql/master:/var/lib/mysql'
  db-slave:
    depends_on:
      - db-master
    image: bergerx/mysql-replication:5.7
    container_name: db-slave
    restart: always
    environment:
      MYSQL_ALLOW_EMPTY_PASSWORD: 1
      MASTER_HOST: db-master
      MASTER_PORT: 3306 
      REPLICATION_USER: database-user
      REPLICATION_PASSWORD: "database-password"
    ports:
      - '33073:3306'
    volumes:
      - '/data/docker/data/db/mysql/slave:/var/lib/mysql'

# networks:
#   default:
#     external:
#       name: production
```
> - 这个镜像是基于mysql官方镜像搞的
> - 配置MASTER_HOST的是slave。
> - 配置MYSQL_ALLOW_EMPTY_PASSWORD是因为启动的脚本里面没有用密码执行了一部分操作，如果设定密码会导致出问题
> - [github source code](https://github.com/bergerx/docker-mysql-replication)、

``` bash
# 查看slave状态
docker exec -it db-slave bash
mysql -u root
mysql > show slave status\G
``` 

### 3. 使用自定义的配置文件
``` bash
# 主配文件位置：my.cnf
#     其中包含了两个目录:
#         - /etc/mysql/conf.d/
#         - /etc/mysql/mysql.conf.d/
docker exec mysql-container cat /etc/mysql/my.cnf
...
!includedir /etc/mysql/conf.d/
!includedir /etc/mysql/mysql.conf.d/

# 配置子目录中已经存在部分文件
docker exec mysql-container ls /etc/mysql/conf.d
docker.cnf mysql.cnf mysqldump.cnf

docker exec mysql-container ls /etc/mysql.conf.d
mysqld.cnf
```

可以将自定义的配置文件挂载进去
``` yaml
    volumes:
      - '/data/docker/runtime/db/mysql/custom.cnf:/etc/mysql/conf.d/custom.cnf'
```