---
title: what is SNI?
date: 2020-06-01 10:47:00
categories: linux/advance
tags: [linux,sni]
---

### 1. what is SNI?
SNI，server name indication。

很多web服务器，会同时托管多个网站，这多个网站共享同一个服务器ip，而且每个网站拥有独立的ssl证书。此时，只是使用单一的服务器ip，并不足以判别用户希望连接哪个网站。就像是寄信到一个机关大院，并未署名收信人，而大院内同时住着十户人家，当然信件无法正常被送达。因为ssl的握手过程，是早于客户与网站的http连接的，所以，此时就会报错。

SNI是设计用来修补这个错误的，它是TLS的一个扩展，在https中使用。在tls/ssl的握手过程中，被用于确认客户端需要获取正确的网站证书（从多个网站证书中正确识别出来）。这个扩展，在http连接之前实现了hostname和domain name的识别，相当于实现在tls/ssl握手阶段，而不是在http建立连接的阶段。

> [参考连接：cloudflare docs](https://www.cloudflare.com/learning/ssl/what-is-sni/)