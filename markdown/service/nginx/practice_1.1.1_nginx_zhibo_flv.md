---
title: 实践: 1.1.1 使用nginx提供直播服务
date: 2021-01-29 11:15:00
categories: service/nginx
tags: [nginx,http-flv,rtmp]
---

### 0. 前言
想试试用nginx搞直播

### 1. 直播用的协议
- rtmp：tcp流，flv视频格式，延时低，adobe推出的标准，现在主要用于推流，播放需要flash插件
- http-flv：http流，flv视频格式，延时低，通过flv.js支持html5播放
- hls：http流，ts文件格式，延时高，苹果推出的标准，目前安卓也支持，通过hls.js支持html5播放
- dash：http流，mp4 3gp webm视频格式，延时高，支持html5直接播放

现在一般用rtmp推流，用http-flv或者hls播放

### 2. nginx部分
``` bash
set -e

yum install gcc gcc-c++ cmake -y

groupadd nginx
useradd -g nginx nginx

yum install pcre-devel openssl openssl-devel zlib-devel -y

git clone https://github.com/winshining/nginx-http-flv-module.git
# 下载nginx
# cd 到nginx源码目录
./configure --user=nginx --group=nginx \
  --prefix=/usr/local/nginx \
  --with-http_ssl_module \
  --with-pcre \
  --with-http_realip_module \
  --with-http_v2_module \
  --add-module=/usr/local/src/nginx-http-flv-module
make
make install
```

nginx.conf
```
# 要单核
worker_processes 1;

http {
  ...
  server {
    listen 80;

    location /hls {
      types {
        application/vnd.apple.mpegurl m3u8;
        video/mp2t ts;
      }

      root /data/nginx/stream;
      add_header 'Cache-Control' 'no-cache';
    }
  }
}

rtmp {
  server {
    listen 1985;
    chunk_size 4000;

    application myapp {
      live on;
      hls on;
      hls_path /data/nginx/stream/hls;
    }
  }
}
```

### 3. 推流部分
- 推流软件用开源推流软件obs
- rtmp推流路径，重点就是两个，一个是application名称，上例中的myapp，一个是stream名称，这个随便取（后面观看的时候用得到）
- 查看的时候用flv，路径就是http://domain.com/myapp/steam-name.m3u8

> 参考文件：去查rtmp和flv的github，那边说明很详细