---
title: 实践: 1.1.0 使用nginx提供mp4串流服务
date: 2020-11-09 16:50:00
categories: service/nginx
tags: [nginx,ffmpeg]
---

### 0. 前言
电脑上下载了电影，想在手机上看

### 1. 部署
`docker-compose.yml`
```
version: '3'
services:
  nginx:
    image: nginx:stable
    container_name: nginx
    ports:
      - 80:80
    volumes:
      - "./default.conf:/etc/nginx/conf.d/default.conf"
      - "/Users/opsuser/Movies/nginx-movie-data:/var/www/html/movie"
```

`default.conf`
```
server {
    listen 80;
    server_name _;
    location / {
        autoindex on;
        root /var/www/html/movie;
        charset utf-8;
    }

    location ~ \.mp4$ {
        mp4;
        root /var/www/html/movie;
    }
}
```
> - `autoindex`，可以自动列出目录下的文件内容
> - `charset utf-8`，支持中文字符的正常显示
> - `mp4`，加载mp4模块后，可以提供mp4文件的浏览器播放支持

> 下载的mp4文件是h265，需要转换成h264，才能在浏览器正常播放，转换方式请查看[ffmpeg convert h265 to h264](/linux/advance/ffmpeg_1.1.0_convert_h265_to_h264.html)