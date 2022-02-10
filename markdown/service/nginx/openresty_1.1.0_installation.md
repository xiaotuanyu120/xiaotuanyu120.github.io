---
title: openresty: 1.1.0 在location里面匹配parameters
date: 2019-03-06 10:05:00
categories: service/nginx
tags: [nginx,openresty]
---

### 0. 前言
openresty是一个nginx的bundle，主要是集成了nginx、luaJIT、lua库，还有很多第三方nginx模块，如果要使用lua的话，使用openresty是一个比较好的选择。

### 1. 安装
``` bash
yum install -y pcre-devel openssl-devel gcc curl

VERSION=1.13.6.2
wget https://openresty.org/download/openresty-${VERSION}.tar.gz
tar -xvf openresty-${VERSION}.tar.gz
cd openresty-${VERSION}/
./configure --prefix=/usr/local/openresty \
            --user=www \
            --group=www \
            --with-pcre \
            --with-pcre-jit \
            --with-http_gzip_static_module \
            --with-http_v2_module \
            -j2
make -j2
make install
```

### 2. 启动管理
``` bash
# 环境变量
echo 'export PATH=$PATH:/usr/local/openresty/bin:/usr/local/openresty/nginx/sbin' > /etc/profile.d/openresty.sh
sh /etc/profile.d/openresty.sh

# 启动文件
echo "[Unit]
Description=full-fledged web platform
After=network.target

[Service]
Type=forking
PIDFile=/usr/local/openresty/nginx/logs/nginx.pid
ExecStartPre=/usr/local/openresty/nginx/sbin/nginx -t -q -g 'daemon on; master_process on;'
ExecStart=/usr/local/openresty/nginx/sbin/nginx -g 'daemon on; master_process on;'
ExecReload=/usr/local/openresty/nginx/sbin/nginx -g 'daemon on; master_process on;' -s reload
ExecStop=-/sbin/start-stop-daemon --quiet --stop --retry QUIT/5 --pidfile /usr/local/openresty/nginx/logs/nginx.pid
TimeoutStopSec=5
KillMode=mixed

[Install]
WantedBy=multi-user.target" > /usr/lib/systemd/system/nginx.service

systemctl daemon-reload
systemctl enable nginx
systemctl start nginx
```