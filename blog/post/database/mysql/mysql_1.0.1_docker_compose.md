---
title: mysql 1.0.1: docker-compose(单实例和主从)
date: 2020-04-21 09:08:00
categories: database/mysql
tags: [docker,docker-compose,mysql]
---
### mysql 1.0.1: docker-compose(单实例和主从)

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