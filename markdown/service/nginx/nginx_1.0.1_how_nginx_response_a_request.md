---
title: nginx 1.0.1: how nginx response a request
date: 2015-12-03 14:39:00
categories: service/nginx
tags: [lnmp,nginx]
---

### 1. NGXIN在request到达后，如何来返回响应
1. request is coming

2. 判断listen ip_address:port
- 若port未指定，则用默认值80；
- 若ip_address未指定，则监听所有ip；
- 若listen 这个配置在server{}中不存在，标准port是80/tcp（superuser启动），或者port是8000/tcp（非superuser启动）；
- 若多个server的listen指定了同一个ip:port，转去查看server_name；

> [nginx doc: listen](http://nginx.org/en/docs/http/ngx_http_core_module.html#listen)

3. 判断server_name
- 类型包括  
  - 准确名称；  
  - wildcard（带星号的）；
  - 正则匹配； 
- 匹配先后顺序：
    - 准确名称（www.example.org）
    - 最长的开头带asterisk的wildcard（\*.example.org）
    - 最长的末尾带asterisk的wildcard（mail.example.\*）
    - 第一个匹配的正则表达
- 如果以上全不匹配，nginx把请求转去默认server(由listen的上下顺序来确定，从上往下第一个listen为默认server)；
> `_`和`listen 80 default`搭配使用是一种catch_all的写法[详细见此文档](/service/nginx/nginx_2.1.2_configuration__catch_all.html)，但`_`本身只是千万种无效域名中的一种[见此文档](http://nginx.org/en/docs/http/server_names.html)。不可以理解单独使用`_`即为default server的想法，这是`listen`的功能。

4. 判断location
- 类型包括
  - prefix名称(包含带`^~`修饰符和`=`的)
  - 正则表达式(`~`大小写敏感; `~*`大小写不敏感)
- 匹配顺序
  - prefix名称
    - `=`的准确prefix location匹配到，终止匹配
    - 最长的prefix location匹配到，会被记住，并继续匹配正则表达式location（但是，若最长的prefix location有`^~`修饰符，则不再匹配正则表达式location）
  - 第一个匹配到的正则表达式location(`~`大小写敏感; `~*`大小写不敏感)，在正则没有匹配到的情况下，使用之前记住的最长的prefix location
> [nginx doc: location](http://nginx.org/en/docs/http/ngx_http_core_module.html#location)