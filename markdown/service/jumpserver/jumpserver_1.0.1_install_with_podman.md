---
title: jumpserver 1.0.1 install with podman
date: 2021-02-18 17:35:00
categories: service/jumpserver
tags: [jumpserver,podman]
---

### 0. jumpserver简介
jumpserver是一个开源堡垒机。

组件包含：
- core >> 核心组件
- koko >> 字符协议的connector
- ~~guacamole~~ >> 图形协议的connector（主要是win的vnc、rdp、ssh，此教程中取消安装这个组件）
- lina >> 前端界面
- ~~luna~~ >> web terminal（此教程中取消安装这个组件）
- task >> celery，执行批量任务的（代码和core是一套）

### 1. 安装jumpserver
需要说明的点：
- 使用podman rootless运行容器(普通用户container)
- 在selinux enforcing状态运行

使用root身份，准备启动环境
``` bash
# create podman running user
useradd -d /data/container container

# runtime var
VERSION=v2.7.1
JUMP_DATA_DIR=/data/container/data
JUMP_RUNTIME_DIR=/data/container/runtime
JUMP_SCRIPT_DIR=/data/container/jms_script
JUMP_CONF_FILE=${JUMP_RUNTIME_DIR}/config.txt

mkdir -p ${JUMP_RUNTIME_DIR}
mkdir -p ${JUMP_DATA_DIR}
mkdir -p ${JUMP_SCRIPT_DIR}

# jumpserver running var
secret_key=$(ip a|tail -10|base64|head -c 16)
bootstrap_token=$(ip a|tail -10|base64|head -c 46)
db_name=jumpserver
db_user=jumpserver
db_password=$(ip a|tail -11|base64|head -c 16)
db_root_password=$(ip a|tail -12|base64|head -c 16)
redis_password=$(ip a|tail -12|base64|head -c 32|tail -c 16)

# prepare var env for container user
cat << EOF > ${JUMP_SCRIPT_DIR}/env.sh
secret_key=${secret_key}
bootstrap_token=${bootstrap_token}
db_name=${db_name}
db_user=${db_user}
db_password=${db_password}
db_root_password=${db_root_password}
redis_password=${redis_password}
VERSION=${VERSION}
JUMP_DATA_DIR=${JUMP_DATA_DIR}
JUMP_RUNTIME_DIR=${JUMP_RUNTIME_DIR}
JUMP_SCRIPT_DIR=${JUMP_SCRIPT_DIR}
JUMP_CONF_FILE=${JUMP_CONF_FILE}
EOF
chmod 600 ${JUMP_SCRIPT_DIR}/env.sh

# prepare config file (for guacamole only) 
mkdir /opt
cd /opt
wget https://github.com/jumpserver/installer/releases/download/${VERSION}/jumpserver-installer-${VERSION}.tar.gz
tar -xf jumpserver-installer-${VERSION}.tar.gz
cd jumpserver-installer-${VERSION}
cp config-example.txt ${JUMP_CONF_FILE}

# last step: correct owner & group
chown -R container.container /data/container
```

#### 下面的操作都是用container用户执行（不要用su切换到container用户，那样env加载不全，podman执行会有问题）
加载启动环境变量文件
``` bash
source ~/jms_script/env.sh
```

准备POD创建和启动脚本
``` bash
cat << EOF > ${JUMP_SCRIPT_DIR}/jms_pod_create_run.sh
#!/usr/bin/env bash

podman pod stop jms
podman pod rm jms

podman pod create -p 80:80 -p 443:443 -p 6635:6635 --name jms
EOF
```
> - 80 > nginx
> - 443 > nginx
> - 6635 > koko-ssh


MYSQL 环境准备
``` bash
mkdir -p ${JUMP_DATA_DIR}/mysql/data
mkdir -p ${JUMP_RUNTIME_DIR}/mysql/{pass,conf.d}
echo ${db_root_password} > ${JUMP_RUNTIME_DIR}/mysql/pass/root.pass
echo ${db_password} > ${JUMP_RUNTIME_DIR}/mysql/pass/jumpserver.pass
chmod 600 ${JUMP_RUNTIME_DIR}/mysql/pass/*
echo '[mysqld]
basedir    		= /usr/
datadir    		= /var/lib/mysql
pid-file  		= /var/run/mysqld/mysqld.pid
socket     		= /var/run/mysqld/mysqld.sock
port       		= 3306
user       		= mysql

log_error              	= /var/lib/mysql/mysql-error.log
slow-query-log-file    	= /var/lib/mysql/mysql-slow.log
log_bin                	= /var/lib/mysql/mysql-bin.log
relay-log              	= /var/lib/mysql/mysql-relay-bin

server-id              	= 1
#read_only 		= 1
innodb_buffer_pool_size = 1024M
innodb_log_buffer_size  = 16M
#key_buffer_size         = 64M
key_buffer_size         = 128M
query_cache_size        = 256M
tmp_table_size          = 128M

#lower_case_table_names = 1
binlog_format          = mixed
#binlog_format          	= statement
skip-external-locking
skip-name-resolve
character-set-server 	= utf8
collation-server 	= utf8_bin
#collation-server 	= utf8_general_ci
max_allowed_packet      = 16M
thread_cache_size       = 256
table_open_cache 	= 4096
back_log                = 1024
max_connect_errors      = 100000
#wait_timeout            = 864000

interactive_timeout  =  1800
wait_timeout  = 1800

max_connections         = 2048
sort_buffer_size        = 16M
join_buffer_size        = 4M
read_buffer_size        = 4M
#read_rnd_buffer_size    = 8M
read_rnd_buffer_size    = 16M
binlog_cache_size       = 2M
thread_stack            = 192K

max_heap_table_size     = 128M
myisam_sort_buffer_size = 128M
bulk_insert_buffer_size = 256M
open_files_limit        = 65535
query_cache_limit       = 2M
slow-query-log
long_query_time        	= 2

expire_logs_days	= 3
max_binlog_size        	= 1000M
slave_parallel_workers 	= 4
log-slave-updates
#slave-skip-errors	=1062,1053,1146,1032

binlog_ignore_db       	= mysql
replicate_wild_ignore_table = mysql.%
sync_binlog = 1

innodb_file_per_table 	= 1
innodb_flush_method 	= O_DIRECT
innodb_buffer_pool_instances = 4
innodb_log_file_size    = 512M
innodb_log_files_in_group = 3
innodb_open_files 	= 4000
innodb_read_io_threads 	= 8
innodb_write_io_threads = 8
innodb_thread_concurrency = 8
innodb_io_capacity 	= 2000
innodb_io_capacity_max	= 6000
innodb_lru_scan_depth	= 2000
innodb_max_dirty_pages_pct = 85
innodb_flush_log_at_trx_commit = 2
sql_mode=NO_ENGINE_SUBSTITUTION,STRICT_TRANS_TABLES


[mysqldump]
quick
quote-names
max_allowed_packet      = 16M

[client]
default-character-set 	= utf8
[mysql]
default-character-set 	= utf8

[isamchk]
key_buffer       	= 128M
sort_buffer_size 	= 4M
read_buffer      	= 2M
write_buffer     	= 2M

[myisamchk]
key_buffer       	= 128M
sort_buffer_size 	= 4M
read_buffer      	= 2M
write_buffer     	= 2M' > ${JUMP_RUNTIME_DIR}/mysql/conf.d/my.cnf

cat << EOF > ${JUMP_SCRIPT_DIR}/mysql_create_run.sh
#!/usr/bin/env bash

podman stop mysql
podman rm mysql

podman unshare chown -R 999.999 ${JUMP_DATA_DIR}/mysql
podman unshare chown -R 999.999 ${JUMP_RUNTIME_DIR}/mysql

podman run -it -d --pod jms --restart=always --name mysql \\
  -v ${JUMP_RUNTIME_DIR}/mysql/conf.d:/etc/mysql/conf.d:Z \\
  -v ${JUMP_DATA_DIR}/mysql/data:/var/lib/mysql:Z \\
  -v ${JUMP_RUNTIME_DIR}/mysql/pass/root.pass:/etc/mysql/pass/root.pass:Z \\
  -v ${JUMP_RUNTIME_DIR}/mysql/pass/jumpserver.pass:/etc/mysql/pass/jumpserver.pass:Z \\
  -e MYSQL_ROOT_PASSWORD_FILE=/etc/mysql/pass/root.pass \\
  -e MYSQL_DATABASE=${db_name} \\
  -e MYSQL_USER=${db_user} \\
  -e MYSQL_PASSWORD_FILE=/etc/mysql/pass/jumpserver.pass \\
  -e TZ=Asia/Shanghai \\
  --health-cmd="mysql -uroot -h127.0.0.1 -p\$\$MYSQL_ROOT_PASSWORD -e 'SHOW DATABASES;'" \\
  --health-interval=10s \\
  --health-timeout=5s \\
  --health-retries=10 \\
  mysql:5.7.33 \\
  --character-set-server=utf8 --collation-server=utf8_bin 
EOF
```

redis 环境准备
``` bash
mkdir -p ${JUMP_DATA_DIR}/redis/{data,log}
mkdir -p ${JUMP_RUNTIME_DIR}/redis
cat << EOF > ${JUMP_RUNTIME_DIR}/redis/redis.conf
daemonize no
#bind 127.0.0.1
port 6379
timeout 300
loglevel notice
logfile /var/log/redis/redis_6379.log
databases 16
save 900 1
save 300 10
save 60 10000
dbfilename dump.rdb
rdbcompression yes
dir /data
# slaveof <masterip> <masterport>
# masterauth <master-password>
maxclients 20480
maxmemory 2g
maxmemory-policy allkeys-lru
appendonly no
#appendfilename
# appendfsync always
# appendfsync everysec
appendfsync no
requirepass ${redis_password}
EOF

cat << EOF > ${JUMP_SCRIPT_DIR}/redis_create_run.sh
#!/usr/bin/env bash

podman stop redis
podman rm redis

podman unshare chown -R 999.1000 ${JUMP_DATA_DIR}/redis
podman unshare chown -R 999.1000 ${JUMP_RUNTIME_DIR}/redis

podman run -it -d --pod jms --restart=always --name redis \\
  -v ${JUMP_RUNTIME_DIR}/redis/redis.conf:/usr/local/etc/redis/redis.conf:Z \\
  -v ${JUMP_DATA_DIR}/redis/data:/data:Z \\
  -v ${JUMP_DATA_DIR}/redis/log:/var/log/redis:Z \\
  -e TZ=Asia/Shanghai \\
  redis:6.0.10-alpine \\
  redis-server /usr/local/etc/redis/redis.conf
EOF
```

core 环境准备
``` bash
mkdir -p ${JUMP_DATA_DIR}/core/{data,logs}
mkdir -p ${JUMP_RUNTIME_DIR}/core
cat << EOF > ${JUMP_RUNTIME_DIR}/core/config.yml
SECRET_KEY: ${secret_key}
BOOTSTRAP_TOKEN: ${bootstrap_token}
# Mysql连接配置
DB_ENGINE: mysql
DB_HOST: 127.0.0.1
DB_PORT: 3306
DB_USER: ${db_user}
DB_PASSWORD: ${db_password}
DB_NAME: ${db_name}
# 运行时绑定端口
HTTP_BIND_HOST: 0.0.0.0
HTTP_LISTEN_PORT: 8080
WS_LISTEN_PORT: 8070
# redis连接
REDIS_HOST: 127.0.0.1
REDIS_PORT: 6379
REDIS_PASSWORD: ${redis_password}
EOF


cat << EOF > ${JUMP_SCRIPT_DIR}/core_create_run.sh
#!/usr/bin/env bash

podman stop core
podman rm core

podman run -it -d --pod jms --restart=always --name core \\
  -v ${JUMP_RUNTIME_DIR}/core/config.yml:/opt/jumpserver/config.yml:Z \\
  -v ${JUMP_DATA_DIR}/core/data:/opt/jumpserver/data:Z \\
  -v ${JUMP_DATA_DIR}/core/logs:/opt/jumpserver/logs:Z \\
  --health-cmd="curl -f http://localhost:8080/api/health/" \\
  --health-interval=10s \\
  --health-timeout=5s \\
  --health-retries=10 \\
  jumpserver/core:${VERSION} \\
  start web
EOF
```

koko是ssh/wss(web terminal)的转发器

koko 环境准备

``` bash
mkdir -p ${JUMP_DATA_DIR}/koko/data
mkdir -p ${JUMP_RUNTIME_DIR}/koko
cat << EOF > ${JUMP_RUNTIME_DIR}/koko/config.yml
CORE_HOST: http://127.0.0.1:8080
BOOTSTRAP_TOKEN: ${bootstrap_token}
SSHD_PORT: 2222
HTTPD_PORT: 5000
REDIS_HOST: 127.0.0.1
REDIS_PORT: 6379
REDIS_PASSWORD: ${redis_password}
EOF

cat << EOF > ${JUMP_SCRIPT_DIR}/koko_create_run.sh
#!/usr/bin/env bash

podman stop koko
podman rm koko

podman run -it -d --pod jms --restart=always --name koko \\
  -v ${JUMP_RUNTIME_DIR}/koko/config.yml:/opt/koko/config.yml:Z \\
  -v ${JUMP_DATA_DIR}/koko/data:/opt/koko/data:Z \\
  -e CORE_HOST=http://127.0.0.1:8080 \\
  --health-cmd="ps axu | grep 'koko'" \\
  --health-interval=10s \\
  --health-timeout=5s \\
  --health-retries=3 \\
  jumpserver/koko:${VERSION}
EOF
```

task环境准备
``` bash
cat << EOF > ${JUMP_SCRIPT_DIR}/task_create_run.sh
#!/usr/bin/env bash

podman stop task
podman rm task

podman run -it -d --pod jms --restart=always --name task \\
  -v ${JUMP_RUNTIME_DIR}/core/config.yml:/opt/jumpserver/config.yml:Z \\
  -v ${JUMP_DATA_DIR}/core/data:/opt/jumpserver/data:Z \\
  -v ${JUMP_DATA_DIR}/core/logs:/opt/jumpserver/logs:Z \\
  -t \\
  -e SERVER_HOSTNAME=${HOSTNAME} \\
  --health-cmd="cd /opt/jumpserver/apps && python manage.py check_celery" \\
  --health-interval=30s \\
  --health-timeout=20s \\
  --health-retries=3 \\
  jumpserver/core:${VERSION} \\
  start task
EOF
```

~~guacamole环境准备（本教程不启用，图形用到的情况少）~~
``` bash
############################################################################
# windows vpn和rdp的服务，可以不启动
############################################################################
# 全局配置（官方提供的，将所有容器的变量放在同一个变量文件中）
#sed -i "s|^CORE_HOST=.*$|CORE_HOST=127.0.0.1|g" ${JUMP_CONF_FILE}
#sed -i "s|^JUMPSERVER_SERVER=.*$|JUMPSERVER_SERVER=http://127.0.0.1:8080|g" ${JUMP_CONF_FILE}
#
#sed -i "s|^SECRET_KEY=.*$|SECRET_KEY=$secret_key|g" ${JUMP_CONF_FILE}
#sed -i "s|^BOOTSTRAP_TOKEN=.*$|BOOTSTRAP_TOKEN=$bootstrap_token|g" ${JUMP_CONF_FILE}
#sed -i "s|^DB_ENGINE=.*$|DB_ENGINE=mysql|g" ${JUMP_CONF_FILE}
#sed -i "s|^DB_HOST=.*$|DB_HOST=127.0.0.1|g" ${JUMP_CONF_FILE}
#sed -i "s|^DB_PORT=.*$|DB_PORT=3306|g" ${JUMP_CONF_FILE}
#sed -i "s|^DB_USER=.*$|DB_USER=$db_user|g" ${JUMP_CONF_FILE}
#sed -i "s|^DB_PASSWORD=.*$|DB_PASSWORD=$db_password|g" ${JUMP_CONF_FILE}
#sed -i "s|^DB_NAME=.*$|DB_NAME=$db_name|g" ${JUMP_CONF_FILE}
#
#sed -i "s|^REDIS_HOST=.*$|REDIS_HOST=127.0.0.1|g" ${JUMP_CONF_FILE}
#sed -i "s|^REDIS_PORT=.*$|REDIS_PORT=6379|g" ${JUMP_CONF_FILE}
#sed -i "s|^REDIS_PASSWORD=.*$|REDIS_PASSWORD=$redis_password|g" ${JUMP_CONF_FILE}
#
#podman run -it -d --pod jms --restart=always --name guacamole \
#  --env-file ${JUMP_CONF_FILE} \
#  --health-cmd="curl http://localhost:8080" \
#  --health-interval=10s \
#  --health-timeout=5s \
#  --health-retries=3 \
#  jumpserver/guacamole:${VERSION}
```

前端环境准备(包含nginx、lina、luna)
``` bash
mkdir -p ${JUMP_DATA_DIR}/nginx/logs
mkdir -p ${JUMP_RUNTIME_DIR}/nginx/{conf.d,stream.d}
```

~~luna环境准备（本教程不启用，用不到web terminal）~~
``` bash
############################################################################
# web terminal 项目，如不需要可以不用（同时将nginx里面的luna配置注释掉）
############################################################################
cat << EOF > ${JUMP_SCRIPT_DIR}/luna_deploy.sh
#!/usr/bin/env bash

rm -rf ${JUMP_DATA_DIR}/nginx/luna
podman run -it --rm --name luna \\
  -v ${JUMP_DATA_DIR}/nginx:/opt/luna_dest:Z \\
  jumpserver/luna:${VERSION} \\
  cp -r /opt/luna /opt/luna_dest
EOF
#只作为更新luna前端代码脚本使用
```

前端界面lina环境准备
``` bash
cat << EOF > ${JUMP_SCRIPT_DIR}/lina_deploy.sh
#!/usr/bin/env bash

rm -rf ${JUMP_DATA_DIR}/nginx/lina
podman run -it --rm --name lina \\
  -v ${JUMP_DATA_DIR}/nginx:/opt/lina_dest:Z \\
  jumpserver/lina:${VERSION} \\
  cp -r /opt/lina /opt/lina_dest
EOF
#只作为更新lina前端代码脚本使用
```

nginx环境准备(用作前端转发各种请求)
``` bash
cat << EOF > ${JUMP_RUNTIME_DIR}/nginx/nginx.conf
user  nginx;
worker_processes auto;

error_log  /var/log/nginx/error.log warn;
pid        /var/run/nginx.pid;


events {
    use epoll;
    worker_connections  4096;
}


http {
    include       /etc/nginx/mime.types;
    default_type  application/octet-stream;
    log_format  main  '\$remote_addr - \$remote_user [\$time_local] "\$request" '
                      '\$status \$body_bytes_sent "\$http_referer" '
                      '"\$http_user_agent" "\$http_x_forwarded_for"';
    access_log  /var/log/nginx/access.log  main;
    sendfile        on;
    keepalive_timeout  65;
    gzip  on;
    include /etc/nginx/conf.d/*.conf;
}


stream {
    include /etc/nginx/stream.d/*.conf;
}
EOF

cat << EOF > ${JUMP_RUNTIME_DIR}/nginx/conf.d/http_server.conf
server {
  listen 80;
  #listen 443 ssl;
  server_tokens off;
  #ssl_certificate cert/server.crt;
  #ssl_certificate_key cert/server.key;
  #ssl_protocols TLSv1 TLSv1.1 TLSv1.2;
  #
  #ssl_ciphers ECDHE-RSA-AES128-GCM-SHA256:ECDHE:ECDH:AES:HIGH:!NULL:!aNULL:!MD5:!ADH:!RC4:!DH:!DHE;
  #add_header Strict-Transport-Security "max-age=31536000";

  client_max_body_size 5000m;

  #若luna（web terminal）不需要使用，则保持注释状态
  ## Luna 配置
  #location /luna/ {
  #  try_files $uri / /index.html;
  #  alias /opt/luna/;
  #}

  # 挂载在本地的配置
  location /media/replay/ {
    add_header Content-Encoding gzip;
    root /data/;
  }

  location /media/ {
    root /data/;
  }

  location /static/ {
    root /data/;
  }

  # 这里使用的是koko的默认wss端口5000
  # Koko 配置
  location /koko/ {
    proxy_pass       http://127.0.0.1:5000;
    proxy_set_header X-Real-IP \$remote_addr;
    proxy_set_header Host \$host;
    proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;

    proxy_http_version 1.1;
    proxy_buffering off;
    proxy_set_header Upgrade \$http_upgrade;
    proxy_set_header Connection "upgrade";
  }
  
  #若guacamole（vnc、rdp for windows）不需要使用，则保持注释状态
  ## Guacamole 配置
  #location /guacamole/ {
  #  proxy_pass http://guacamole:8080/;

  #  proxy_buffering off;
  #  proxy_http_version 1.1;
  #  proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
  #  proxy_set_header Upgrade \$http_upgrade;
  #  proxy_set_header Connection \$http_connection;

  #  proxy_ignore_client_abort on;
  #  proxy_connect_timeout 600;
  #  proxy_send_timeout 600;
  #  proxy_read_timeout 600;
  #  send_timeout 6000;
  #}

  ## OmniDB 配置
  #location /omnidb/ws {
  #  resolver 127.0.0.11 valid=30s;
  #  set $upstream http://omnidb:8071;
  #  proxy_pass       \$upstream\$request_uri;
  #  proxy_http_version 1.1;
  #  proxy_buffering off;
  #  proxy_set_header Upgrade \$http_upgrade;
  #  proxy_set_header Connection "upgrade";
  #  proxy_set_header X-Real-IP \$remote_addr;
  #  proxy_set_header Host \$host;
  #  proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
  #  access_log off;
  #}

  #location /omnidb/ {
  #  resolver 127.0.0.11 valid=30s;
  #  set $upstream http://omnidb:8082;
  #  proxy_pass       \$upstream\$request_uri;
  #  proxy_buffering off;
  #  proxy_http_version 1.1;
  #  proxy_set_header Upgrade \$http_upgrade;
  #  proxy_set_header Connection \$http_connection;
  #  proxy_set_header X-Real-IP \$remote_addr;
  #  proxy_set_header Host \$host;
  #  proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
  #  access_log off;
  #}

  # Core 配置
  location /ws/ {
    proxy_set_header X-Real-IP \$remote_addr;
    proxy_set_header Host \$host;
    proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
    proxy_pass http://127.0.0.1:8070;

    proxy_http_version 1.1;
    proxy_buffering off;
    proxy_set_header Upgrade \$http_upgrade;
    proxy_set_header Connection "upgrade";
  }

  location /api/ {
    proxy_set_header X-Real-IP \$remote_addr;
    proxy_set_header Host \$host;
    proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
    proxy_pass http://127.0.0.1:8080;
  }

  location /core/ {
    proxy_set_header X-Real-IP \$remote_addr;
    proxy_set_header Host \$host;
    proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
    proxy_pass http://127.0.0.1:8080;
  }

  # 前端 Lina
  location /ui/ {
    try_files \$uri / /ui/index.html;
    alias /opt/lina/;
  }

  location / {
    rewrite ^/(.*)\$ /ui/\$1 last;
  }
}
EOF

cat << EOF > ${JUMP_RUNTIME_DIR}/nginx/stream.d/kokossh.conf
log_format  proxy  '\$remote_addr [\$time_local] '
                   '\$protocol \$status \$bytes_sent \$bytes_received '
                   '\$session_time "\$upstream_addr" '
                   '"\$upstream_bytes_sent" "\$upstream_bytes_received" "\$upstream_connect_time"';

access_log /var/log/nginx/kokossh-tcp-access.log proxy;
open_log_file_cache off;

upstream kokossh {
    server 127.0.0.1:2222;
    least_conn;
}

server {
    listen 6635;
    proxy_pass kokossh;
    proxy_protocol on;
    proxy_connect_timeout 1s;
}
EOF


cat << EOF > ${JUMP_SCRIPT_DIR}/nginx_create_run.sh
#!/usr/bin/env bash

podman stop nginx
podman rm nginx

podman unshare chown -R 101.101 ${JUMP_DATA_DIR}/nginx
podman unshare chown -R 101.101 ${JUMP_RUNTIME_DIR}/nginx

podman run -it -d --pod jms --restart=always --name nginx \\
  -v ${JUMP_RUNTIME_DIR}/nginx/nginx.conf:/etc/nginx/nginx.conf:Z \\
  -v ${JUMP_RUNTIME_DIR}/nginx/conf.d:/etc/nginx/conf.d:Z \\
  -v ${JUMP_RUNTIME_DIR}/nginx/stream.d:/etc/nginx/stream.d:Z \\
  -v ${JUMP_DATA_DIR}/core/data:/data:Z \\
  -v ${JUMP_DATA_DIR}/nginx/lina:/opt/lina:Z \\
  -v ${JUMP_DATA_DIR}/nginx/logs:/var/log/nginx:Z \\
  -e TZ=Asia/Shanghai \\
  --health-cmd="test -f /var/run/nginx.pid" \\
  --health-interval=10s \\
  --health-timeout=5s \\
  --health-retries=2 \\
  nginx:1.18.0-alpine
EOF
```
>如果希望用到luna(web terminal)，增加下面的内容
> - `-v ${JUMP_DATA_DIR}/nginx/luna:/opt/luna:Z \\`

启动jumpserver
``` bash
chmod a+x ${JUMP_SCRIPT_DIR}/*.sh

# 先创建pod，映射端口
${JUMP_SCRIPT_DIR}/jms_pod_create_run.sh

# 启动数据层
${JUMP_SCRIPT_DIR}/mysql_create_run.sh
${JUMP_SCRIPT_DIR}/redis_create_run.sh

# 启动核心组件
${JUMP_SCRIPT_DIR}/core_create_run.sh
${JUMP_SCRIPT_DIR}/koko_create_run.sh
${JUMP_SCRIPT_DIR}/task_create_run.sh

# 准备前端代码
${JUMP_SCRIPT_DIR}/lina_deploy.sh
#若luna（web terminal）不需要使用，则保持注释状态
#${JUMP_SCRIPT_DIR}/luna_deploy.sh

# 启动前端nginx
${JUMP_SCRIPT_DIR}/nginx_create_run.sh
```