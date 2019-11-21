---
title: sonarqube: 1.0.0 installation - docker
date: 2019-11-21 10:00:00
categories: devops/sonarqube
tags: [devops,sonarqube,java]
---
### sonarqube: 1.0.0 installation - docker

---

### 1. 参考链接
- [sonarqube - dockerhub docs](https://hub.docker.com/_/sonarqube/)
- [elasticsearch - system requirement](https://www.elastic.co/guide/en/elasticsearch/reference/current/docker.html#docker-prod-prerequisites)

### 2. docker宿主机系统环境配置要求
``` bash
# STEP: sysctl config
# set sysctl config permanently
sed -i '/vm.max_map_count=.*$/ d' /etc/sysctl.conf
sed -i 'fs.file-max=.*$/ d' /etc/sysctl.conf
echo "vm.max_map_count=262144" >> /etc/sysctl.conf
echo "fs.file-max=65536" >> /etc/sysctl.conf

# set vm.max_map_count on a live system
sysctl -w vm.max_map_count=262144
sysctl -w fs.file-max=65536

# STEP: disable swap
# disable swap on a live system
swapoff -a
# disable swap permanantly
sed -ri 's/^#?(.*)(swap.*swap)(.*$)/#\1\2\3/g' /etc/fstab


# STEP: increase limit
# increase limit on a live system
ulimit -n 65536
ulimit -u 4096
# increase limit permanantly
sed -i '/^\*.*soft.*nofile/ d' /etc/security/limits.conf
sed -i '/^\*.*hard.*nofile/ d' /etc/security/limits.conf
sed -i '/^\*.*soft.*nproc/ d' /etc/security/limits.conf
sed -i '/^\*.*hard.*nproc/ d' /etc/security/limits.conf
echo "
*               soft    nofile           65536
*               hard    nofile           65536
*               soft    nproc            4096
*               hard    nproc            4096" >> /etc/security/limits.conf

sed -ri 's/^#?(DefaultLimitNOFILE)=(.*)$/\1=65536/g' /etc/systemd/system.conf
sed -ri 's/^#?(DefaultLimitNPROC)=(.*)$/\1=4096/g' /etc/systemd/system.conf
systemctl daemon-reexec
```

### 3. sonarqube启动
#### 1) 初始化sonarqube
使用下面的命令启动sonarqube。这将初始化所有sonarqube数据(复制默认插件，创建Elasticsearch数据文件夹，
创建sonar.properties配置文件)。查看日志，一旦容器正确启动，就可以强制退出(ctrl+c)并继续进行下一步。
``` bash
# create folder
DOCKER_DATA_DIR=/data/docker
SONARQUBE_DIR=${DOCKER_DATA_DIR}/data/sonarqube
SONARQUBE_CONF_DIR=${SONARQUBE_DIR}/conf
SONARQUBE_LOG_DIR=${SONARQUBE_DIR}/logs
SONARQUBE_EXT_DIR=${SONARQUBE_DIR}/extensions
SONARQUBE_DATA_DIR=${SONARQUBE_DIR}/data
SONARQUBE_YML_DIR=${SONARQUBE_DIR}/yml

mkdir -p ${DOCKER_DATA_DIR}
mkdir -p ${SONARQUBE_DIR}
mkdir -p ${SONARQUBE_CONF_DIR}
mkdir -p ${SONARQUBE_LOG_DIR}
mkdir -p ${SONARQUBE_EXT_DIR}
mkdir -p ${SONARQUBE_DATA_DIR}
mkdir -p ${SONARQUBE_YML_DIR}

# 一次性运行sonarqube，初始化数据
docker run --rm \
  -p 9000:9000 \
  -v ${SONARQUBE_CONF_DIR}:/opt/sonarqube/conf \
  -v ${SONARQUBE_EXT_DIR}:/opt/sonarqube/extensions \
  -v ${SONARQUBE_LOG_DIR}:/opt/sonarqube/logs \
  -v ${SONARQUBE_DATA_DIR}:/opt/sonarqube/data \
  sonarqube
```

#### 2) 配置sonarqube
修改`sonar.properties`修改数据库连接url。配置文件中有各个支持数据库的配置模板，删除想要的数据库的配置模板配置的注释即可。
```
#Example for PostgreSQL
#也可以不在这里配置，在下面的docker-compose.yml文件中传入环境变量来配置
sonar.jdbc.url=jdbc:postgresql://localhost/sonarqube
```
> 根据[SONAR-12501](https://jira.sonarsource.com/browse/SONAR-12501),不要在`sonar.properties`中配置`sonar.jdbc.username`和`sonar.jdbc.password`。要使用环境变量替代，在version 8中，这个bug被修复

#### 3) 启动sonarqube
``` bash
cat << EOF > docker > ${SONARQUBE_YML_DIR}/docker-compose.yml
version: '2.2'
services:
  sonarqube:
    image: sonarqube:7.9-community
    container_name: sonarqube
    environment:
      - sonar.jdbc.username=sonar
      - sonar.jdbc.password=sonar
      - sonar.jdbc.url=jdbc:postgresql://localhost/sonar
    ulimits:
      memlock:
        soft: -1
        hard: -1
      nproc: 4096
      nofile:
        soft: 65536
        hard: 65536
    volumes:
      - ${SONARQUBE_CONF_DIR}:/opt/sonarqube/conf
      - ${SONARQUBE_EXT_DIR}:/opt/sonarqube/extensions
      - ${SONARQUBE_LOG_DIR}:/opt/sonarqube/logs
      - ${SONARQUBE_DATA_DIR}:/opt/sonarqube/data
    ports:
      - 9000:9000
EOF

cd ${SONARQUBE_YML_DIR}
docker-compose up -d
```
> 启动后，默认的用户名和密码是`admin:admin`