---
title: 4.0.0 docker 本地registry
date: 2017-07-07 16:51:00
categories: virtualization/docker
tags: [docker,registry]
---

### 0. 安装docker
安装本地的registry之前，我们需要首先安装docker。然后使用docker启动一个registry的镜像就启动了registry服务。
> docker安装参照[docker官方安装文档](https://docs.docker.com/engine/installation/#server)和[docker中文安装文档(centos7)](/virtualization/docker/docker_1.1.0_installation_centos7.html)

---

### 1. 准备文件
#### 0) 变量设定
``` bash
# docker路径变量
DOCKER_DIR=/data/docker
DOCKER_YAML_DIR=${DOCKER_DIR}/yml
DOCKER_BUILD_DIR=${DOCKER_DIR}/build
DOCKER_RUNTIME_DIR=${DOCKER_DIR}/runtime
DOCKER_DATA_DIR=${DOCKER_DIR}/data

# nginx路径变量
NGINX_BUILD_DIR=${DOCKER_BUILD_DIR}/nginx
NGINX_DATA_DIR=${DOCKER_DATA_DIR}/nginx
NGINX_LOG_DIR=${NGINX_DATA_DIR}/logs

# registry路径变量
REG_RUNTIME_DIR=${DOCKER_RUNTIME_DIR}/registry
REG_DATA_DIR=${DOCKER_DATA_DIR}/registry
```

#### 1） 准备文件目录结构
``` bash
# 创建docker相关路径
mkdir -p ${DOCKER_YAML_DIR}
mkdir -p ${DOCKER_BUILD_DIR}
mkdir -p ${DOCKER_RUNTIME_DIR}
mkdir -p ${DOCKER_DATA_DIR}

# 创建nginx相关路径
mkdir -p ${NGINX_BUILD_DIR}
mkdir -p ${NGINX_DATA_DIR}
mkdir -p ${NGINX_LOG_DIR}

# 创建registry数据目录
mkdir -p ${REG_RUNTIME_DIR}
mkdir -p ${REG_DATA_DIR}

# yml和编译目录保持在同一个目录下
ln -s ${NGINX_BUILD_DIR} ${DOCKER_YAML_DIR}/nginx
```

#### 2） nginx编译文件准备
- **nginx主配文件**

``` bash
echo 'user  nginx;
worker_processes  auto;

error_log  /var/log/nginx/error.log warn;
pid        /var/run/nginx.pid;


events {
    use epoll;
    worker_connections 51200;
    multi_accept on;
}


http {
    include       /etc/nginx/mime.types;
    default_type  application/octet-stream;

    log_format  main  "$http_x_forwarded_for - $remote_user [$time_local] $request "
                      "$status $body_bytes_sent $http_referer "
                      "$http_user_agent $remote_addr "
                      "$upstream_addr $upstream_response_time $request_time $host $proxy_add_x_forwarded_for";

    access_log  off;

    sendfile        on;
    #tcp_nopush     on;

    keepalive_timeout  65;

    #gzip  on;

    include /etc/nginx/conf.d/*.conf;
}' > ${NGINX_BUILD_DIR}/nginx.conf
```

- **registry虚拟主机文件**

``` bash
# 选择1：HTTP版本
echo '# Configuration for the server
server {
    charset utf-8;
    listen 80;
    server_name <your-domain.com>;
    client_max_body_size 1000M;
    access_log /var/log/nginx/docker-registry.access.log main;
    location / {
        proxy_pass       http://reg:5000;
        proxy_redirect   off;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Host $server_name;
        }
    }' > ${NGINX_BUILD_DIR}/docker-registry.conf

# 选择2：HTTPS版本
echo '# Configuration for the server
server {
    charset utf-8;
    listen 80;
    listen 443 ssl;
    server_name <your-domain.com>;
    ssl_certificate     conf.d/domain.crt;
    ssl_certificate_key conf.d/domain.key;
    client_max_body_size 1000M;
    access_log /var/log/nginx/docker-registry.access.log main;
    location / {
        proxy_pass       https://reg:443;
        proxy_redirect   off;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Host $server_name;
        }
    }' > ${NGINX_BUILD_DIR}/docker-registry.conf
```
> `client_max_body_size 1000M`; 是为了防止上传时的413错误，这个错误提示客户端上传数据容量超过限制；
> 把`<your-domain.com>`改成自己的域名

- **如果启用了SSL，准备证书文件**

``` bash
# 准备证书给nginx
cat << EOF > ${NGINX_BUILD_DIR}/domain.crt
<your crt content>
EOF

cat << EOF > ${NGINX_BUILD_DIR}/domain.key
<your crt content>
EOF

# 将证书给registry一份
cp ${NGINX_BUILD_DIR}/{domain.crt,domain.key} ${REG_RUNTIME_DIR}
```

- **nginx镜像Dockerfile文件**

``` bash
# 选择1：HTTP版本
cat << EOF > ${NGINX_BUILD_DIR}/Dockerfile
FROM nginx:stable
RUN rm /etc/nginx/conf.d/default.conf
ADD docker-registry.conf /etc/nginx/conf.d/
EOF

# 选择2：HTTPS版本
cat << EOF > ${NGINX_BUILD_DIR}/Dockerfile
FROM nginx:stable
RUN rm /etc/nginx/conf.d/default.conf
ADD docker-registry.conf /etc/nginx/conf.d/
ADD domain.crt /etc/nginx/conf.d/
ADD domain.key /etc/nginx/conf.d/
EOF
```

#### 3) registry和nginx的docker-compose文件准备

``` bash
# 选择1：HTTP版本
cat << EOF > ${DOCKER_YAML_DIR}/docker-compose-registry.yaml
version: '2'
services:
  nginx:
    container_name: nginx
    build: nginx
    restart: always
    ports:
      - '80:80'
    volumes:
      - '${NGINX_LOG_DIR}:/var/log/nginx'
    links:
      - reg
  reg:
    image: 'registry:2'
    container_name: reg
    restart: always
    volumes:
      - '${REG_DATA_DIR}:/var/lib/registry'
EOF

# 选择2：HTTPS版本
cat << EOF > ${DOCKER_YAML_DIR}/docker-compose-registry.yaml
version: '2'
services:
  nginx:
    container_name: nginx
    build: nginx
    restart: always
    ports:
      - '80:80'
      - '443:443'
    volumes:
      - '${NGINX_LOG_DIR}:/var/log/nginx'
    links:
      - reg
  reg:
    environment:
      - REGISTRY_HTTP_ADDR=0.0.0.0:443
      - REGISTRY_HTTP_TLS_CERTIFICATE=/certs/domain.crt
      - REGISTRY_HTTP_TLS_KEY=/certs/domain.key
    image: 'registry:2'
    container_name: reg
    restart: always
    volumes:
      - '${REG_DATA_DIR}:/var/lib/registry'
      - '${REG_RUNTIME_DIR}:/certs'
EOF
```

### 2. 本地基础认证(可选)
``` bash
# 基础变量设置
REG_AUTH_LOCAL_DIR=${REG_RUNTIME_DIR}/auth
REG_AUTH_MOUNT_DIR=/auth
REG_USER=<your-username>
REG_PASSWD=<your-password>

# 准备本地auth目录和文件
mkdir ${REG_AUTH_LOCAL_DIR}
docker run \
  --entrypoint htpasswd \
  registry:2 -Bbn ${REG_USER} ${REG_PASSWD} > ${REG_AUTH_LOCAL_DIR}/htpasswd

# 更新docker-compose文件
# 选择1：HTTP版本
cat << EOF > ${DOCKER_YAML_DIR}/docker-compose-registry.yaml
version: '2'
services:
  nginx:
    container_name: nginx
    build: nginx
    restart: always
    ports:
      - '80:80'
    volumes:
      - '${NGINX_LOG_DIR}:/var/log/nginx'
    links:
      - reg
  reg:
    environment:
      - REGISTRY_AUTH=htpasswd
      - REGISTRY_AUTH_HTPASSWD_REALM=Registry Realm
      - REGISTRY_AUTH_HTPASSWD_PATH=/auth/htpasswd
    image: 'registry:2'
    container_name: reg
    restart: always
    volumes:
      - '${REG_DATA_DIR}:/var/lib/registry'
      - '${REG_AUTH_LOCAL_DIR}:${REG_AUTH_MOUNT_DIR}'
EOF

# 选择2：HTTPS版本
cat << EOF > ${DOCKER_YAML_DIR}/docker-compose-registry.yaml
version: '2'
services:
  nginx:
    container_name: nginx
    build: nginx
    restart: always
    ports:
      - '80:80'
      - '443:443'
    volumes:
      - '${NGINX_LOG_DIR}:/var/log/nginx'
    links:
      - reg
  reg:
    environment:
      - REGISTRY_HTTP_ADDR=0.0.0.0:443
      - REGISTRY_HTTP_TLS_CERTIFICATE=/certs/domain.crt
      - REGISTRY_HTTP_TLS_KEY=/certs/domain.key
      - REGISTRY_AUTH=htpasswd
      - REGISTRY_AUTH_HTPASSWD_REALM=Registry Realm
      - REGISTRY_AUTH_HTPASSWD_PATH=/auth/htpasswd
    image: 'registry:2'
    container_name: reg
    restart: always
    volumes:
      - '${REG_DATA_DIR}:/var/lib/registry'
      - '${REG_RUNTIME_DIR}:/certs'
      - '${REG_AUTH_LOCAL_DIR}:${REG_AUTH_MOUNT_DIR}'
EOF
```

### 3. 运行registry
``` bash
# 使用docker-compose启动registry
docker-compose -f ${DOCKER_YAML_DIR}/docker-compose-registry.yaml up -d

# 使用之前先认证
docker login --username ${REG_USER} --password ${REG_PASSWD} reg.example.net
```

### 4. 非https协议下的registry使用，docker需要修改的配置
`/etc/docker/daemon.json`
``` json
{
  "insecure-registries" : ["myregistrydomain.com:5000"]
}
```
> [deploy a plain http registry](https://docs.docker.com/registry/insecure/#deploy-a-plain-http-registry)