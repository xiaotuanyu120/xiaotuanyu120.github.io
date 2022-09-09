---
title: curl: 使用教程
date: 2020-04-07 19:08:00
categories: linux/tools
tags: [linux,curl]
---

# curl
## 0. 什么是curl？
官方介绍：“Curl is a command-line tool for transferring data specified with URL syntax”。其实就是一个用来发送URL请求的命令行工具。

> 参考文档：
> - [curl github](https://github.com/curl/curl)
> - [curl man](https://curl.se/docs/manpage.html)

## 1. curl基本介绍
### 1.1 options
- `-I, --head`: 只获取响应的header
- `-H`: 发送请求时额外的header，例如：`-H "Host: example.com"`
- `-X`: 指定连接HTTP服务器时的HTTP请求方法，默认是`GET`。通常情况下，不需要使用这个选项，因为常见的`GET,HEAD,POST,PUT`等请求有专门的option来调用。这个选项只是更改了HTTP请求中actual word，并没有改变curl的行为，例如，`-X HEAD`并不能代替`-I, --head`的功能。
- `--post301`, `--port302`, `--port303`: 让curl遵循`RFC 7231/6.4.2`规范，在进行`301`, `302`, `303`跳转时，依然不会把`POST`转换成`GET`。这个选项必须要和`-L, --location`选项同时使用。
- `-L, --location`: 如果连接的HTTP服务器返回了3XX的重定向返回码，这个选项会让curl在重定向的地址上重新发起请求。如果同时使用了`-I, --head`，会返回路径上所有的header信息。
- `-d, --data <data>`: 将指定的数据在POST请求中发送给HTTP服务器，就像用户在浏览器中填写表单，然后点下发送按钮之后浏览器执行的行为一样。这样的请求使用的`content-type`是`application/x-www-form-urlencoded`。和`-I, --head`, `-F, --form`, `-T, --upload-file`这些选项互斥。
- `-E, --cert <certificate[:password]>`: 告诉curl在建立TLS连接时，使用什么客户端证书（如果应用程序有使用双向证书认证的话）。
- `--key <key>`: 告诉curl在建立TLS连接时，使用什么客户端私钥（如果应用程序有使用双向证书认证的话）。
- `--ciphers <list of ciphers>`: 设定在连接中使用什么加密算法。
  
  > [--ciphers中可以使用的加密算法参考](https://www.openssl.org/docs/man1.1.1/man1/ciphers.html)

- `-w, --write-out <format>`: 按照指定的格式和变量内容，在curl完成请求后输出。
  
  > 详细变量说明，见[curl.se](https://curl.se/docs/manpage.html#-w)

## 2. curl用法示例
### 2.1 post用法
#### 2.1.1 post 501 错误
``` bash
curl -X post -d "{}" https://something.com
HTTP Status 501 – Not Implemented
```
> 基于[mozilla 501 error docs](https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/501)，501错误是请求的方法不被服务器接受，定睛一看，`post`不应该是小写，换成`POST`就好了

#### 2.1.2 post data 格式
``` bash
# form 格式
curl -d "param1=value1&param2=value2" -H "Content-Type: application/x-www-form-urlencoded" -X POST http://localhost:3000/data

# json格式
curl -d '{"key1":"value1", "key2":"value2"}' -H "Content-Type: application/json" -X POST http://localhost:3000/data
```
> [curl post docs](https://gist.github.com/subfuzion/08c5d85437d5d4f00e58)

### 2.2 `-w`用法
使用`-w`来排查连接的各种时间
``` bash
curl -o /dev/null -s -w 'time_namelookup: %{time_namelookup}\ntime_connect: %{time_connect}\ntime_starttransfer: %{time_starttransfer}\ntime_total: %{time_total}\n' https://www.baidu.com
time_namelookup: 0.010346
time_connect: 0.051382
time_starttransfer: 0.251428
time_total: 0.251855
```