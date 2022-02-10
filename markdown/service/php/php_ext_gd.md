---
title: php extensions: GD - graphic draw
date: 2020-12-09 14:31:00
categories: service/php
tags: [php,gd,ext]
---

### 1. GD是啥？
php不仅可以输出html信息，还可以创建不同格式（png、jpeg、gif等）的图片输出。

> [php - gd官方文档](https://www.php.net/manual/en/intro.image.php)

### 2. docker在php5.6和php7.4下面安装扩展
```
# php 5.6
FROM php:5.6-apache
RUN apt-get update \
    && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
    libpng-dev libfreetype6-dev libjpeg62-turbo-dev \
    && rm -rf /var/lib/apt/lists/* \
    && docker-php-ext-configure gd --with-freetype-dir --with-jpeg-dir --with-png-dir \
    && docker-php-ext-install gd
```

```
# php 7.4
FROM php:7.4-apache
RUN apt-get update \
    && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
    libpng-dev libfreetype6-dev libjpeg62-turbo-dev \
    && rm -rf /var/lib/apt/lists/* \
    && docker-php-ext-configure gd --with-freetype --with-jpeg \
    && docker-php-ext-install gd
```
> php7.4 默认有png的enable，所以不需要再使用--with-png-dir

### 3. 检查插件状态
```
# 检查模块
php -m

# 查看gd信息
php -r 'print_r(gd_info());'
```