---
title: nginx: 配置 - 日志
date: 2022-05-16 16:59:00
categories: service/nginx
tags: [nginx]
---

## 1. 常用的log_format
### 1.1 记录post data
简单说明就是，在proxy_pass,fastcgi_pass,uwsgi_pass和scgi_pass配置块中，可以使用`reqeust_body`这个内置变量来获取POST请求的post数据。
```
log_format logpost "$request_body";
```

> 其他限制见官方文档：[built in var: request_body](https://nginx.org/en/docs/http/ngx_http_core_module.html#var_request_body)

> 注意：当nginx作为web tunnel，客户端使用CONNECT来访问时，使用这个配置无法获取预期值。

### 1.2 记录upstream的响应请求的server地址
```
log_format logupstream "$upstream_addr";
```
> [module ngx_http_upstream_module var: upstream_addr](https://nginx.org/en/docs/http/ngx_http_upstream_module.html#var_upstream_addr)

> 注意：当nginx作为web tunnel，客户端使用CONNECT来访问时，使用这个配置无法获取预期值。

## 2. 问题
### 2.1 内置的log_format格式
在nginx.conf中添加如下配置

```
log_format  combined  '$remote_addr - $remote_user [$time_local] '
                       '"$request" $status $body_bytes_sent '
                       '"$http_referer" "$http_user_agent"';
```

**报错信息**

``` bash
nginx -t
2008/05/26 18:45:16 [emerg] 19875#0: "log_format" directive duplicate "log_format" name in /usr/local/nginx/conf/nginx.conf:26
```
大意是，我们重复定义了combined日志格式，但是我仔细检查了整个nginx.conf，以及所有include的配置文件，都没有找到其他的combined这个log_format配置项。

**原因解析**
[nginx邮件列表关于此问题的参考链接](http://mailman.nginx.org/pipermail/nginx/2008-May/005214.html)  
原来"combined" log_format 是在nginx的源码中已经定义过的，我重新去再次定义，实属画蛇添足，当然软件会提示我重复定义了。