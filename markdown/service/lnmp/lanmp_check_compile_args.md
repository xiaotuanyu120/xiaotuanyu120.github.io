---
title: LANMP: 查看编译参数
date: 2015-12-12 09:07:00
categories: service/lnmp
tags: [apache,configuration]
---

``` bash
# apache编译参数获取
cat /path/to/apache/build/config.nice
 
# nginx编译参数
/path/to/sbin/nginx -v
 
# php编译参数
/path/to/bin/php -i | grep configure
 
# mysql编译参数
cat /path/to/mysql/bin/mysqlbug | grep configure
```