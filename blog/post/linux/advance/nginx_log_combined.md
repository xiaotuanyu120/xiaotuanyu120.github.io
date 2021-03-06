---
title: nginx: log_format combined?
date: 2016-10-14 09:46:00
categories: linux/advance
tags: [nginx,log]
---
### nginx: log_format combined?

---

### 0. 背景
新安装nginx，发现配置文件没有log_format配置项，于是在nginx.conf中添加如下配置
```
log_format  combined  '$remote_addr - $remote_user [$time_local] '
                       '"$request" $status $body_bytes_sent '
                       '"$http_referer" "$http_user_agent"';
```
#### 1) 报错信息
执行nginx配置语法检查时报错
``` bash
nginx -t
2008/05/26 18:45:16 [emerg] 19875#0: "log_format" directive duplicate "log_format" name in /usr/local/nginx/conf/nginx.conf:26
```
大意是，我们重复定义了combined日志格式，但是我仔细检查了整个nginx.conf，以及所有include的配置文件，都没有找到combined这个log_format配置项。

#### 2) 原因解析
[nginx邮件列表关于此问题的参考链接](http://mailman.nginx.org/pipermail/nginx/2008-May/005214.html)  
原来"combined" log_format 是在nginx的源码中已经定义过的，我重新去再次定义，实属画蛇添足，当然软件会提示我重复定义了。
