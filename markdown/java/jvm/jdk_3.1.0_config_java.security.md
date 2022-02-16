---
title: JDK 配置 - java security
date: 2022-02-16 22:28:00
categories: java/jvm
tags: [java,jvm,jdk,security,dns,tls,ssl]
---

### 1. JDK8: 为JVM中的DNS名称解析设定超时时间
JVM会缓存DNS结果。当JVM成功解析hostname为IP后，它会将解析结果缓存一定时间，这个时间即为TTL（time-to-live）。

这个设定的默认值在不同的JVM中各不相同，许多JVM会设定这个值为少于60s的时间，这个设定是合理的，因为目前在云环境中，很多hostname会动态的变化，假如超时时间设定的过久，那么就会导致hostname解析会延时生效，会引发一系列连锁效应。

> 有些特殊场景，有些管理员会将JVM的这个设定设置为永久缓存，这样的话，JVM运行期间，第一次成功获取的hostname解析的IP会永久储存在缓存中，直到JVM重启才会刷新。这样的话，在hostname会频繁改动的情况下问题就会更加严重。

**如何设定JVM的DNS TTL**

全局设定，可以编辑`$JRE_HOME/lib/security/java.security`中的`networkaddress.cache.ttl`
```
network.address.cache.ttl=60
```
> 设定为永久的值为`-1`，但是不推荐这样设定，因为这代表第一次成功解析到的记录会储存在缓存中永不失效，在hostname变更解析时必须要重启JVM才能使解析的变更生效。

程序里面设定
``` java
java.security.Security.setProperty("networkaddress.cache.ttl" , "60");
```

### 2. JDK8: 禁用SSLv3等不安全的ssl/tls版本
目前`ssl 2.0, ssl 3.0, tls 1.0, tls 1.1`并不安全，建议使用`tls 1.2`
> ssl版本禁用相关，也可以参照[windows ssl安全](/cryptography/ssl/windows-TLS-version-control.html)查看理论知识。

JVM全局设定，可以编辑`$JRE_HOME/lib/security/java.security`中的`jdk.tls.disabledAlgorithms`，这个选项配置的内容即为被禁用的ssl版本和加密算法
```
jdk.tls.disabledAlgorithms=SSLv3, TLSv1, TLSv1.1, RC4, DES, MD5withRSA, \
    DH keySize < 1024, EC keySize < 224, 3DES_EDE_CBC, anon, NULL, \
    include jdk.disabled.namedCurves
```
> `DH keySize < 1024`类似的格式，即为【某种算法】小于【xx】位的被禁用