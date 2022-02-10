---
title: openssl 1.3.0 获取证书
date: 2020-06-01 11:05:00
categories: cryptography/basic
tags: [cryptography,openssl]
---

### 1. 获取域名证书

#### openssl获取
``` bash
# 获取域名证书
domain=www.example.com
echo|openssl s_client -servername ${domain} -connect ${domain}:443|\
    sed -ne '/-BEGIN CERTIFICATE-/,/-END CERTIFICATE-/p' > ${domain}.crt
```
> `-servername`，web服务器有可能同时托管多个ssl网站，所以需要指定servername，来在tls握手阶段判断获取哪个servername证书，[详情参照SNI说明](/linux/advance/what_is_sni.html)

#### 浏览器（chrome）获取
如何通过浏览器获得证书
- 通过浏览器访问接口url
- 点击url框左边小绿锁
- 点击“certificate”
- 点击“详细信息”的tab
- 点击“公钥”字段
- 点击右下角“复制到文件”那个按钮
- 弹出的窗口选择“下一步”
- 弹出的窗口选择“Base64编码X.509(.CER)(S)”
- 保存到本地即可，然后用笔记本打开，拷贝内容到服务器上