---
title: ssl error 1.1.0 handshake_failure and unable to find valid certification path
date: 2018-03-10 10:02:00
categories: java/security
tags: [ssl, handshake_failure]
---
### ssl error 1.1.0 handshake_failure and unable to find valid certification path

---

### 1. handshake_failure
#### 错误信息
``` bash
[ERROR]_2018-03-08 16:31:10 990 : [http-apr-8580-exec-81] \
getHttpContentByBtParam 请求调用异常：
javax.net.ssl.SSLHandshakeException: Received fatal alert: handshake_failure
```
#### 解决办法：应用JCE的unlimited policy文件
原因：据参照文档中的文档所述，这个错误是因为代码的加密方法使用的是256位，而jdk默认的limited policy限制是128位。

解决思路：参照[JCE unlimited policy应用文档](/java/security/jce_1.1.0_unlimited_policy.html)应用对应版本的方法即可。

> 参照文档：[stackoverflow answer](https://stackoverflow.com/questions/38203971/javax-net-ssl-sslhandshakeexception-received-fatal-alert-handshake-failure) 


### 2. unable to find valid certification path to requested target
#### 错误信息
```
javax.net.ssl.SSLHandshakeException: sun.security.validator.ValidatorException: PKIX path building failed: sun.security.provider.certpath.SunCertPathBuilderException: unable to find valid certification path to requested target
```

#### 解决办法：增加证书到受信任列表中
原因：是https使用的ssl证书没有加到信任列表里面，如果是直接用浏览器访问时，浏览器会提示我们不安全，但是依然会显示页面内容。但是因为是java程序连接，所以直接就提示创建连接失败了。  

解决思路: 按照[keytool使用方法](/java/security/keytool_1.1.0_usage.html)中介绍的方法，将需要连接的域名的ssl证书增加到受信任列表中即可

> jdk默认的truststore(也是keystore格式，专做信任证书用途)路径是`<java-home>/jre/lib/security/cacerts`。


### 3. timestamp check failed
### 错误信息
```
Exception: javax.net.ssl.SSLHandshakeException: sun.security.validator.ValidatorException: PKIX path validation failed: java.security.cert.CertPathValidatorException: timestamp check failed
```
生产环境很多接口用的域名，突然一起报错。域名可以在浏览器中访问。

#### 解决办法：【增加证书到受信任列表中】 或者 【重新申请新证书】
原因：原来是[sectigo根证书过期](https://www.racent.com/blog/about-sectigo-addtrust-root-expiration)，如果域名是浏览器访问，因为浏览器内置的根证书肯定是更新过，而我们java程序使用的truststore文件中的根证书并没有及时更新，所以才造成了这个问题

解决思路：因为根证书失效，所以根证书来认证域名证书失效；所以我们最好是手动将域名证书加到我们jdk的truststore中，或者干脆给域名申请一个新的证书。