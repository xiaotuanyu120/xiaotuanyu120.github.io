---
title: php extensions: zip
date: 2020-12-09 14:57:00
categories: service/php
tags: [php,gd,ext]
---

### 1. docker在php5.6和php7.4下面安装扩展zip
```
# php 5.6
FROM php:5.6-apache
RUN apt-get update \
    && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends zlib1g-dev libzip-dev \
    && rm -rf /var/lib/apt/lists/* \
    && docker-php-ext-configure zip --with-libzip \
    && docker-php-ext-install zip
```

```
# php 7.4
FROM php:7.4-apache
RUN apt-get update \
    && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends zlib1g-dev libzip-dev \
    && rm -rf /var/lib/apt/lists/* \
    && docker-php-ext-install zip
```

### 3. 检查插件状态
```
# 检查模块
php -m
```