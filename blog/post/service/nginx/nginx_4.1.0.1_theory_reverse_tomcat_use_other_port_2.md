---
title: nginx: 4.1.0.1 nginx 监听https和http，然后使用http反向代理tomcat
date: 2020-02-18 14:29:00
categories: service/nginx
tags: [tomcat,nginx]
---
### nginx: 4.1.0.1 nginx 监听https和http，然后使用http反向代理tomcat

---

### 1. 需求背景 & 遇到的问题
#### 0) 背景
在之前的[文章](/service/nginx/nginx_4.1.0_theory_reverse_tomcat_use_other_port.html)中，我们使用非80端口的nginx，反向代理了tomcat。

但是问题在于，你需要根据http和https分别提供tomcat来提供nginx访问。http和https的tomcat区别如下：

- `http`：`$CATALINA_BASE/conf/server.xml`
```
<Connector port="6236" protocol="HTTP/1.1"
               proxyPort="6116"
               ...
               redirectPort="8443" useBodyEncodingForURI="true" URIEncoding="UTF-8" />
```
- `https`：`$CATALINA_BASE/conf/server.xml`
```
<Connector port="6236" protocol="HTTP/1.1"
               proxyPort="6116"
               sslProtocol='SSL'
               scheme='https'
               ...
               redirectPort="8443" useBodyEncodingForURI="true" URIEncoding="UTF-8" />
```
此处比http增加了`sslProtocol`,`scheme`  

#### 1) 需求：  
nginx监听非80端口的http和https，然后使用同一个tomcat来提供后端处理


### 2. 解决办法
首先，给nginx增加`proxy_set_header X-Forwarded-Proto $scheme;`

```
server {
    listen 6116;
    listen 443 ssl http2;
    server_name _;
    ssl_certificate     crt/example.crt;
    ssl_certificate_key crt/example.key;
    access_log  access.log main;
    location / {
        proxy_pass http://tomcat;
        proxy_redirect off;
        proxy_set_header Host $host;
        proxy_headers_hash_max_size 51200;
        proxy_headers_hash_bucket_size 6400;
        proxy_set_header X-Real-IP  $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

上面的原理就是proxy的时候，增加header`X-Forwarded-Proto`，设定它的值为你访问时候的scheme(https/http)

然后，tomcat那边增加如下配置
``` xml
<?xml version='1.0' encoding='utf-8'?>
<Server port="16210" shutdown="SHUTDOWN">

...

    <Engine name="Catalina" defaultHost="localhost">
      <Valve className="org.apache.catalina.valves.RemoteIpValve"
           internalProxies="127\.0\.[0-1]\.1"
           remoteIpHeader="x-forwarded-for"
           requestAttributesEnabled="true"
           httpServerPort="6116"
           protocolHeader="x-forwarded-proto"
           protocolHeaderHttpsValue="https"/>
    </Engine>

...

  </Service>
</Server>
```
里面改了如下配置：
- 设定只可以从127.0.0.1代理过来
- 设定remote ip的header是"x-forwarded-for"
- 设定http的port是6116，否则默认是80
- 设定protocol的header是"x-forwarded-proto"
- 设定protocol header中为何值时判断其为https请求，默认是https

> 原理就是设定https的header，然后根据header内容判断是不是https；然后因为http不是80，所以设定一下端口号

> [tomcat 7 offical docs](https://tomcat.apache.org/tomcat-7.0-doc/config/valve.html#Introduction)