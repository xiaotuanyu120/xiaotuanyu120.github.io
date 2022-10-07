---
title: web
date: 2015-09-23 09:15:00
categories: python/basic
tags: [python]
---

## 1. web访问流程
从用户输入url之后的详细流程
- dns
- cdn 静态/ 动态
- http server nginx/apache/xxx
- web server django

gunicorn: (wsgi) django:
1. authorize
2. url dispatch: url = {('/n/(\d+)/', news_handler)}
3. middleware  session, csrf, cookie, post argument, get argument
4. handle(def, class)
5. form
6. model queryset --> table (orm)
7. return
8. middelware, response
9. proxy --> http server

## 2. web访问流程问题
### 2.1 DNS解析是什么？
人们习惯记忆域名，但机器间互相只认ip，域名和ip可以是多对一的关系，他们之间的转换工作称为域名解析，域名解析需要有专门的域名解析服务器来完成。举例说明：

在浏览器中输入域名 www.xxx.com ， 操作系统会向检查自己本地的hosts是否有这个网址映射，如果有就直接调用这个ip地址，完成域名解析。如果没有就查找本地DNS解析器缓存，是否有这个网址映射关系，如果有直接返回，完成域名解析。如果没有相应的网址映射关系，则会查找本地DNS服务器，如果要查询的域名包含在本地配置区域资源中，则返回结果给客户机，完成域名解析。如果未找到，本地DNS就会把请求发至根DNS，根DNS收到请求后会判断这个域名并返回负责该域名服务器的ip，最后会返回到本地DNS服务器，由DNS服务器在返回给客户机。

### 2.2 简述如何与服务器建立TCP连接
在TCP/IP协议体系结构中的TCP协议使用三次握手机制来建立传输连接，具体步骤如下：

1. 首先是服务器初始化的过程，从CLOSED（关闭）状态开始通过顺序调用SOCKET、BIND、LISTEN和ACCEPT原语创建Socket套接字，进入LISTEN（监听）状态，等待客户端的TCP传输连接请求。

2. 客户端最开始也是从CLOSED状态开始调用SOCKET原语创建新的Socket套接字，然后在需要在调用CONNECT原语，向服务器发送一个将SYN字段置1（表示为同步数据段）的数据段，主动打开端口，进入到SYN SENT（已发送连接请求，等待对方确认）状态。

3. 服务器在收到来自客户端的SUN数据段后，发回一个SYN字段置1（表示此为同步数据段），ACK字段置1（表示此为确认数据段），ACK（确认号）=i+1的应答数据段（假设初始序号为j），被动打开端口，进入到SYN RCVD（已收到一个连接请求，但未进行确认）状态。这里要注意的是确认号是i+1,而不是i，表示服务器希望接收的下一个数据段序号为i+1.

4. 客户端在收到来自服务器的SYN+ACK数据段后，向服务器发送一个ACK=1（表示此为确认数据段），序号为i+1,ack=J+1的确认数据段，同时进去ESTABLISHED（连接建立）状态，建立单向连接。要注意的是，此时序号为i+1,确认号为j+1,表示客户端希望收到服务器的下一个数据段的序号为j+1.

服务端在收到客户端的ACK数据段后，进入ESTABLISHED状态，完成双向连接的建立。

一旦连接建立，数据就可以双向对等的流动，没有所谓的主从关系。

### 2.3 简述客户端与服务端传送数据
在建立连接最后一次"握手"时，客户端发送的数据稍带着http请求报文，服务器在给客户端的http响应报文中稍带着要浏览的数据。

### 2.4 http协议与tcp协议之间的关系
TCP协议是传输层协议，主要解决数据如何在网络中传输。而HTTP是应用层协议，主要解决如何包装数据。HTTP建立在TCP的基础上。

### 2.5 简述Http get请求过程，并举例
get请求用于从服务器上获取资源，是默认的请求方法。当客户端向服务器发送http请求是可以稍带上要请求的数据，服务器在响应http请求是可以向客户端返回要访问的数据。

例如使用get方法读取路径为/usr/bin/image的图像。请求行给出了方法GET，URL，与HTTP协议版本号。报文头部有2行，给出了浏览器可以接收GIF与JPEG格式的图像。请求报文中没有正文.应答报文包括状态码和4行的报头。报头表示了日期，服务器，MIME版本号和文档长度：

请求
```
GET/usr/bin/image1  HTTP/1.1

         Accept:  image/gif
     
         Accept:  image/jpeg
```
应答
```
 HTTP/1.1  200  ok

        Date: San,1-Feb-09  8:30:10  GMT
     
        Server:  xxx
     
        MIME-version:  1.0
     
        Content-length: 2048
     
             (文档内容)
```

### 2.6 简述Http post请求过程，并举例
post与get基本一致，post请求是客户端向服务器发送http请求是稍带上要上传到服务器处理的数据。

请求
```
POST/cgi-bin/doc.pl  HTTP/1.1

        Accept: */*
     
        Accept: image/gif
     
        Accept: image/jpeg
     
        Content-length:64
```
应答
```
HTTP/1.1  200 OK(状态行)

Last-Modified(应答首部) : Mon,20 Dec 2001 23 :26 :42 GMT

Date:Tue,11 Jan 2002 20:53:12 GMT

Status:200

Content-Type: Text/html

Servlet-Engine:

Content-Length:59

<html>(应答主体)

......

</html>
```

### 2.7 nginx是什么
Nginx是一个跨平台的Web服务器，可运行在Linux、FreeBSD、Solaris、AIX、Mac OS、Windows等操作系统上。相比Apache等，占有内存少，并发能力强，安装简单，bugs少。

Nginx由内核和模块组成，其中，内核的设计非常微小和简洁，完成的工作也非常简单，仅仅通过查找配置文件将客户端请求映射到一个location block（location是Nginx配置中的一个指令，用于URL匹配），而在这个location中所配置的每个指令将会启动不同的模块去完成相应的工作。

Nginx的模块从结构上分为核心模块、基础模块和第三方模块。用户根据自己的需要开发的模块都属于第三方模块。

### 2.8 简述nginx的工作流程
当它接收到一个HTTP请求是，它仅仅是通过查找配置文件将此次请求映射到一个location block，而此location中所配置的各个指令则会启动不同的模块去完成工作，因此模块可以看作是nginx的真正劳动工作者。通常一个location中的指令会涉及一个handler模块和多个fiflter模块（多个location可以复用同一个模块）。handler模块负责处理请求，完成响应内容的生成，而filter模块对影响内容进行处理。

### 2.9 nginx工作原理

Nginx的模块从功能上分为如下三类:

- Handlers（处理器模块）。此类模块直接处理请求，并进行输出内容和修改headers信息等操作。Handlers处理器模块一般只能有一个。

- Filters （过滤器模块）。此类模块主要对其他处理器模块输出的内容进行修改操作，最后由Nginx输出。

- Proxies （代理类模块）。此类模块是Nginx的HTTP Upstream之类的模块，这些模块主要与后端一些服务比如FastCGI等进行交互，实现服务代理和负载均衡等功能。

> nginx工作原理参考：http://wuzhengfei.iteye.com/blog/2026998