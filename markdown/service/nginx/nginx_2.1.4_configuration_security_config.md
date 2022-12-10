---
title: nginx: 配置 - 业务配置安全
date: 2017-03-09 14:04:00
categories: service/nginx
tags: [nginx,rewrite]
---

### 0. nginx业务配置方面的安全注意点
关于业务无关的nginx本身的安全注意点，详见[安全 - 基础安全](/service/nginx/nginx_2.1.4_configuration_security_base.html)。

这里更关注一些业务相关的配置中的安全因素，比如说：

- 禁止IP直接访问服务器
- 如何安全的重定向

### 1. 禁止IP直接访问服务器
生产环境下，服务之间，一般都是使用指定的公网域名或者内部局域网域名来跨主机交互。基于此，禁止使用服务器IP访问nginx服务器的安全限制就成为了可能。

```
server {
    listen      80 default_server;
    server_name _;
    return      444;
}
```

### 2. 如何安全的重定向
这里有几个要点：

- 301和302，换成307和308。目的是禁止某些浏览器在重定向时，将post请求换成get请求
- 使用`$request_uri`而不是`$uri`。目的是避免CRLF注入漏洞，因为`$uri`在跳转前会识别URL编码，而`$request_uri`不会。详情见[nginx上演示CRLF注入漏洞](service/nginx/nginx_2.1.4_security_CRLF_demo_on_nginx.html)

``` bash
server {
    listen 80 default_server;
    server_name _;
    return 307 https://$host$request_uri;
}
```

简要解释

- [$host变量说明](http://nginx.org/en/docs/http/ngx_http_core_module.html#var_host)
- [$request_uri变量说明](http://nginx.org/en/docs/http/ngx_http_core_module.html#var_request_uri)

> 不要混淆`$server_name`和`$host`，server_name就是我们配置的该server块的变量

### 3. 严格要求HTTP请求方法
仅允许常用的`GET, POST`
``` bash
add_header Allow "GET, POST" always;
if ( $request_method !~ ^(GET|POST)$ ) {
	return 405;
}
```