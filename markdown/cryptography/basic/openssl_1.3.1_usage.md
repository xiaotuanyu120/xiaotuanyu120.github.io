---
title: openssl 1.3.1 SSL DEBUG: s_client
date: 2022-09-09 20:51:00
categories: cryptography/basic
tags: [openssl]
---

## 1. s_client
简介：SSL/TLS 客户端程序，用于调试和SSL服务器的连接。
```
openssl s_client [-connect host:port] [-servername name] [-verify depth] [-verify_return_error] [-cert filename] [-certform DER|PEM] [-key filename] [-keyform DER|PEM] [-pass arg] [-CApath directory] [-CAfile filename] [-no_alt_chains] [-reconnect] [-pause] [-showcerts] [-debug] [-msg] [-nbio_test] [-state] [-nbio] [-crlf] [-ign_eof] [-no_ign_eof] [-quiet] [-ssl2] [-ssl3] [-tls1] [-no_ssl2] [-no_ssl3] [-no_tls1] [-no_tls1_1] [-no_tls1_2] [-fallback_scsv] [-bugs] [-sigalgs sigalglist] [-curves curvelist] [-cipher cipherlist] [-serverpref] [-starttls protocol] [-engine id] [-tlsextdebug] [-no_ticket] [-sess_out filename] [-sess_in filename] [-rand file(s)] [-serverinfo types] [-status] [-alpn protocols] [-nextprotoneg protocols]
```

**选项介绍：**
- `-connect host:port`: 指定连接主机和端口
- `-servername name`: TLS SNI (Server Name Indication)
- `-cert certname`: 客户端证书（如果使用双向认证的话）
- `-certform format`: 客户端证书格式，`DER,PEM`，默认值`PEM`
- `-key keyfile`: 客户端私钥（如果使用双向认证的话）
- `-keyform format`: 客户端私钥格式，`DER,PEM`，默认值`PEM`
- `-pass arg`: 客户端私钥密码
- `-tls1,-tls1_1,-tls1_2,-no_ssl2,-no_ssl3,-no_tls1,-no_tls1_1,-no_tls1_2`: 指定`ssl protocol`
- `-cipher cipherlist`: 指定ssl连接的加密算法

> 加密算法详情见：[ciphers](https://www.openssl.org/docs/man1.0.2/man1/ciphers.html)

> openssl ssl debug工具详细用法：[openssl s_client](https://www.openssl.org/docs/man1.0.2/man1/openssl-s_client.html)

## 2. s_client示例
``` bash
openssl s_client -cert client.crt -key client.key -tls1_2 -connect 127.0.0.1:80 -servername www.test.com
```
常见的使用场景：
- debug服务器是否开启了ssl的特定版本；
- debug特定的ssl加密算法；