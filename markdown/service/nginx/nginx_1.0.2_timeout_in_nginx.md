---
title: nginx: 理论 - nginx中的timeout
date: 2019-07-15 16:00:00
categories: service/nginx
tags: [nginx,timeout]
---

### 1. keepalive_timeout
```
Syntax:	keepalive_timeout timeout [header_timeout];
Default: 
keepalive_timeout 75s;
Context:	http, server, location
```
> The first parameter sets a timeout during which a keep-alive client connection will stay open on the server side. The zero value disables keep-alive client connections. The optional second parameter sets a value in the “Keep-Alive: timeout=time” response header field. Two parameters may differ.
> 
> The “Keep-Alive: timeout=time” header field is recognized by Mozilla and Konqueror. MSIE closes keep-alive connections by itself in about 60 seconds.

设置的是客户端和nginx的连接超时时间


### 2. proxy_connect_timeout
```
Syntax:	proxy_connect_timeout time;
Default:	
proxy_connect_timeout 60s;
Context:	http, server, location
```
> Defines a timeout for establishing a connection with a proxied server. It should be noted that this timeout cannot usually exceed 75 seconds.

nginx和upstream的server连接的超时时间


### 3. proxy_read_timeout
```
Syntax:	proxy_read_timeout time;
Default:	
proxy_read_timeout 60s;
Context:	http, server, location
```
> Defines a timeout for reading a response from the proxied server. The timeout is set only between two successive read operations, not for the transmission of the whole response. If the proxied server does not transmit anything within this time, the connection is closed.

nginx对upstream的response的读操作之间的超时


### 4. proxy_send_timeout
```
Syntax:	proxy_send_timeout time;
Default:	
proxy_send_timeout 60s;
Context:	http, server, location
```
> Sets a timeout for transmitting a request to the proxied server. The timeout is set only between two successive write operations, not for the transmission of the whole request. If the proxied server does not receive anything within this time, the connection is closed.

nginx对upstream转发request的操作之间的超时