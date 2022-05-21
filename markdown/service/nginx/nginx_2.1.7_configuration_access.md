---
title: nginx: 配置 - access limit
date: 2021-02-09 10:18:00
categories: service/nginx
tags: [nginx]
---

### 1. 常规的access限制
```
location / {
    deny  192.168.1.1;
    allow 192.168.1.0/24;
    allow 10.1.1.0/16;
    allow 2001:0db8::/32;
    deny  all;
}
```
但是这样是根据remote_address来限制的，所以说，如果用户和nginx服务器之间有代理的话，就不行了
>[nginx docs: access](http://nginx.org/en/docs/http/ngx_http_access_module.html)

### 2. 中间有代理的access限制方法
```
set $allow 0;
if ($http_x_forwarded_for ~ "^(192.168.0.1|172.16.0.1)") {
  set $allow "$allow1";
}
if ($allow != 01) {
  return 403;
}
```
这样的话，是使用了xff变量[http_x_forwarded_for]来匹配来源ip做限制