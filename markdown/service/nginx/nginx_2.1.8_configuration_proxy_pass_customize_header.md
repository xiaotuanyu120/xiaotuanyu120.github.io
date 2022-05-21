---
title: nginx: 配置 - nginx proxy的时候会撒谎吗？
date: 2021-11-08 19:30:00
categories: service/nginx
tags: [nginx, proxy]
---

### 0. nginx反向代理的时候会撒谎吗？
这个问题很标题党，这个问题换成nginx在作为反向代理服务器的时候，可以修改传向后端的http请求信息吗，会更贴切一点。

nginx作为一个代理服务器，所有的东西都是它中转给后端服务器的。比如说客户端的ip地址，客户访问的域名、端口等等。那么，nginx是否可以自由的修改这些变量呢？

下面我们就用客户访问的url来测试一下。

### 1. 准备环境
这里使用docker来模拟一个nginx，一个go的web服务器。nginx反向代理到go的web服务器，go的web服务器只是在页面上返回客户访问的域名信息。

**准备测试环境**
``` bash
mkdir -p ~/DevRoot/test-nginx-fake-url
cd ~/DevRoot/test-nginx-fake-url
sudo echo "127.0.0.1 example.com" >> /etc/hosts
```

**nginx配置文件 - nginx/example.conf**
```
  server {
    listen       80;
    server_name  example.com;
    access_log   /var/log/nginx/example.access.log  main;

    location / {
      proxy_pass      http://goserver:8080;
    }
  }
```

**golang: 程序文件 - goserver/main.go**
``` go
import (
    "fmt"
    "net/http"
)

func hello(w http.ResponseWriter, req *http.Request) {
    fmt.Fprintf(w, req.Host)
}

func headers(w http.ResponseWriter, req *http.Request) {

    for name, headers := range req.Header {
        for _, h := range headers {
            fmt.Fprintf(w, "%v: %v\n", name, h)
        }
    }
}

func main() {
    http.HandleFunc("/hello", hello)
    http.HandleFunc("/headers", headers)

    http.ListenAndServe(":8080", nil)
}
```

**golang: module文件 - goserver/go.mod**
``` go
module localhost.net

go 1.17
```

**docker文件 - goserver/Dockerfile**
``` dockerfile
FROM golang:alpine AS builder

WORKDIR /app
COPY . .
RUN go build -o /app/goserver


FROM golang:alpine

WORKDIR /app
COPY --from=builder /app/goserver .

EXPOSE 8080
CMD [ "/app/goserver" ]
```

**docker-compose文件： ./docker-compose.yaml**
``` yaml
version: "3.9"
services:
  web:
    image: nginx:stable
    container_name: nginx
    depends_on:
      - goserver
    ports:
      - "80:80"
    volumes:
      - "./nginx/example.conf:/etc/nginx/conf.d/example.conf"
  
  goserver:
    build: ./goserver
    container_name: goserver
```

**启动容器**
``` bash
docker-compose up -d
```

### 2. 修改代理配置看效果
**CASE 1. 最简单的proxy，啥也不配**
```
  server {
    listen       80;
    server_name  example.com;
    access_log   /var/log/nginx/example.access.log  main;

    location / {
      proxy_pass      http://goserver:8080;
    }
  }
```

**测试效果**
``` bash
curl example.com/hello
goserver:8080
```
> 你看，这里就假了，它用的是nginx自己upstream配置的url

**CASE 2. 线上经常使用的配置**
```
  server {
    listen       80;
    server_name  example.com;
    access_log   /var/log/nginx/example.access.log  main;

    location / {
      proxy_pass       http://goserver:8080;
      proxy_set_header Host       $http_host;
    }
  }
```

**测试效果**
``` bash
docker exec nginx nginx -s reload

curl example.com/hello
example.com
```
> $http_host的值就是header里面的Host的内容。
> 
> 相当于nginx把自己收到的Host的内容，proxy给后端的Host

**CASE 3. 玩点花的，欺骗goserver**
```
  server {
    listen       80;
    server_name  example.com;
    access_log   /var/log/nginx/example.access.log  main;

    location / {
      proxy_pass       http://goserver:8080;
      proxy_set_header Host       "fake-host";
    }
  }
```

**测试效果**
``` bash
docker exec nginx nginx -s reload

curl example.com/hello
fake-host
```
> 和case 2相同，只不过proxy给后端一个随意编写的Host内容


### 3. 总结
nginx是可以随意修改传给后端的内容的，只要nginx程序支持修改。

可用场景1：官网域名 > cdn > cdn域名 > 接入层nginx >修改Host为cdn域名> 后端（此时认为用户是通过官网域名访问过来的）
> - 为什么不用ip，而是用cdn域名？
> 用了https的域名，为了安全
> 
> - 为什么不用https的ip地址？
> 你的接入层nginx通常不会只监听一个域名，而是多个域名，此时用ip满足不了业务要求