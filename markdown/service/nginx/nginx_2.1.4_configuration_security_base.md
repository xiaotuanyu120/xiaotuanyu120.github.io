---
title: nginx: 2.1.4 安全 - 基础安全
date: 2021-11-10 19:49:00
categories: service/nginx
tags: [lnmp,nginx]
---

### 0. nginx本身的安全性需要注意的点
这里仅就nginx本身的安全配置做个小的总结，实际生产环境中，安全还会有其他的诸如代码、网络、主机等方方面面，这里就不涉及到了。

业务逻辑方面的安全配置，请参照[安全 - 业务配置安全](/servie/nginx/nginx_2.1.4_configuration_security_config.html)

仅就nginx本身的安全性而言，有如下几点需要注意
- 隐藏nginx版本信息
- 禁用不安全的SSL版本
- 禁用不安全的SSL ciphers
- 配置安全header
- 隐藏nginx服务类型

### 1. 隐藏nginx版本信息
关闭nginx版本信息，降低被黑客针对性扫描入侵。

```
server_tokens off;
```

> [nginx core docs: server_tokens](http://nginx.org/en/docs/http/ngx_http_core_module.html#server_tokens)

### 2. 禁用不安全的SSL版本
SSLv2、SSLv3、TLSv1和TLSv1.1，已经被主流浏览器停止支持，目前的主流是TLSv1.2，最新版本是TLSv1.3。

```
ssl_protocols TLSv1.2 TLSv1.3;
```

> 配置SSL版本的时候，注意openssl的版本依赖，详情见[nginx http_ssl docs: ssl_protocols](http://nginx.org/en/docs/http/ngx_http_ssl_module.html#ssl_protocols)
>
> 安全设定也要参考实际业务的兼容性，有些业务场景必须要支持到很老的操作系统和浏览器，那么就需要综合性评估一下。

### 3. 禁用不安全的SSL ciphers

```
# 告诉客户端，使用服务端的算法
ssl_prefer_server_ciphers on;

# 使用高等级算法，带感叹号的是需要在HIGH这个算法组中排除掉的强度不够的算法子组
ssl_ciphers HIGH:!aNULL:!MD5:!AES128:!SHA1:!SHA256:!SHA384;
```

> 详细的算法列表，可以查看[openssl ciphers string](https://www.openssl.org/docs/man1.0.2/man1/ciphers)
>
> 也可以用这个命令`openssl ciphers -v '这里是配置的算法串'`看实际配置算法的列表内容

### 4. 配置安全的header
有一些安全的header还是需要额外增加一下的。

> [nginx docs: add_header](http://nginx.org/en/docs/http/ngx_http_headers_module.html#add_header)
>
> `always`，意思是无论响应代码如何，都会加上这个header

#### 1) Strict-Transport-Security
HTTP Strict-Transport-Security缩写是HSTS，这个响应标头用以告诉浏览器此站点只接受https连接。

```
add_header Strict-Transport-Security "" always;
```

> [MDN WEB DOCS: Strict-Transport-Security](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Strict-Transport-Security)

#### 2) X-Content-Type-Options
X-Content-Type-Options，这个响应标头用于告诉浏览器应遵循 Content-Type 标头中通告的 MIME 类型，不可以更改它。用以避免MIME 类型嗅探。

```
add_header X-Content-Type-Options nosniff always;
# 严格要求了以下两种MIME类型
# - 请求“style”类型，但MIME类型不是“text/css”
# - 请求“script”类型，但MIME类型不是JavaScript MIME type
#   - application/ecmascript
#   - application/javascript
#   - application/x-ecmascript
#   - application/x-javascript
#   - text/ecmascript
#   - text/javascript
#   - text/javascript1.0
#   - text/javascript1.1
#   - text/javascript1.2
#   - text/javascript1.3
#   - text/javascript1.4
#   - text/javascript1.5
#   - text/jscript
#   - text/livescript
#   - text/x-ecmascript
#   - text/x-javascript
```

> 确保配置之前，先去看看 [MDN WEB DOCS: X-Content-Type-Options](https://developer.mozilla.org/zh-CN/docs/Web/HTTP/Headers/X-Content-Type-Options) 来了解如何具体配置，避免影响业务。

#### 3) Content-Security-Policy
Content-Security-Policy，这个响应标头用以控制允许user agent为给定页面加载的资源。除了少数例外情况，设置的政策主要涉及指定服务器的源和脚本结束点。用以避免跨站脚本攻击。

可做的限制举几个例子：

- javascript可以加载的源地址
- font可以加载的源地址
- 可以通过脚本加载的URL
- 图片加载的源地址
- 多媒体资源加载的源地址
- 样式文件加载的源地址
等等

```
# 设定所有来源都是本站
add_header Content-Security-Policy  "default-src 'self';" always;
```

> [MDN WEB DOCS: Content-Security-Policy](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Content-Security-Policy)

### 5. 隐藏nginx服务类型(nginx 1.20.x)
在上面虽然隐藏了nginx的服务器版本，但是依然可以被探测是nginx服务器。

若想隐藏这个内容：

- 一个是购买nginx的商业发行版，通过`server_tokens "your string or variable here or empty to disable Server header"`来实现；
- 另外一个安装nginx-extras，但是这个是依赖外部模块，引入了不必要的风险，和我们的目标不一致;
- 还有一个就是通过修改源码

```
# 路径：src/http/ngx_http_header_filter_module.c
static u_char ngx_http_server_string[] = "Server: nginx" CRLF;

# 路径：src/core/nginx.h
#define NGINX_VER          "nginx/" NGINX_VERSION
```

### 6. 总结
通过减少服务器信息外漏，增强ssl连接安全和限制请求规范（https、mime不许修改和限制源地址）的多重手段，增强nginx的安全性