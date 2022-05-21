---
title: nginx: 配置 - CRLF注入漏洞（nginx）Demo
date: 2021-02-11 17:24:00
categories: service/nginx
tags: [nginx,rewrite,CRLF]
---

### 0. `CRLF`注入漏洞
`CRLF`的含义是”回车符+换行符“(`\r\n`)，其十六进制的assii码`CR`和`LF`分别对应`0x0d`和`0x0a`。浏览器会对URL中不安全的ascii码字符进行编码，编码规则就是将字符替换为`%`后面跟上其十六进制末尾两位，也就是说CRLF在URL中的编码是`%0d%0a`。

在HTTP协议中，HTTP报文分为三个部分，请求行、首部、空行和请求数据组成，其中首部各个header之间是通过CRLF分隔，浏览器就是根据CRLF来格式化提取HTTP报文的各个组成部分。所以，一旦客户端可以任意注入CRLF到http请求中，那么就可以伪造cookie、session等任意内容到http请求中。

CRLF注入攻击，就是利用浏览器对不安全字符（\r\n）的编码和HTTP报文使用CRLF（\r\n）区隔不同部分，绕过服务端，将特定内容注入到服务器的响应报文中的过程。

什么情况下，服务端会把URL中的内容添加到响应报文里面呢？答案就是重定向，服务端接收到请求，如果触发了重定向的条件，服务端会把请求处理后发回给浏览器，在此过程中，攻击者就把需要注入的内容从客户端发起的请求中，注入到了服务端的响应报文里面。

### 1. 使用nginx模拟CRLF漏洞
使用如下nginx配置，重点关注**重定向配置**和`$uri`变量

```
server {
    listen 80;
    server_name test.local.net;

    location / {
        return 302 http://$host/hello$request_uri;
    }

    location /hello {
        add_header Content-Type text/plain;
        return 200 hello;
    }
}
```

> 上面配置的含义就是，直接访问`test.local.net/hello`，会直接在浏览器返回hello字符串；而访问`test.local.net`域名的任意其他uri，都会被重定向到`test.local.net/hello`上。

接下来，我们在浏览器中访问`http://test.local.net/%0d%0aSet-Cookie:session%3dblabla`

![](/static/images/docs/service/nginx/CRLF-demo-on-nginx.01.png)

从上图你会发现请求的响应标头里面多了一些奇怪的东西，`Set-Cookie: session=blabla`

然后，再查看重定向`/hello`的请求

![](/static/images/docs/service/nginx/CRLF-demo-on-nginx.02.png)

从上图你会发现重定向到`/hello`的请求中，增加了`Cookie: session=blabla`的内容。

### 2. 如何解决这个问题呢？
很简单，把`$uri`换成`$request_uri`。nginx在重定向前，对`$uri`中的字符，会把`%0d%0a`识别为URL编码，经过解码后转换成了CRLF的编码，然后将其发给了浏览器。而对于`$request_uri`，nginx不会进行这个编码识别过程，没有解码的话，发回浏览器还是`%0d%0a`，浏览器识别不到CRLF，于是注入就不成功了。