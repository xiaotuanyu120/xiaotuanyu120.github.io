---
title: jce 1.1.0 无限制策略
date: 2020-06-01 14:54:00
categories: java/security
tags: [jce]
---
### jce 1.1.0 无限制策略

---

### 0. 什么是jce？
jca，Java Cryptography Architecture，顾名思义，是用来提供加密的基础架构。

而jce，Java Cryptography Extension，很明显，是jca的一个部分。

JCE 提供了一个关于加密、密钥生成、密钥同意和Message Authentication Code (MAC) 算法的框架和实现。


### 1. unlimited policy有啥用？
因为如果使用limited policy，官方限制了加密的强度。看文档是针对不同加密方法限制了位数最高是64和128不等。

> [oracle官方说明文档 - 请查看limited 和 unlimited部分](https://docs.oracle.com/javase/8/docs/technotes/guides/security/crypto/CryptoSpec.html)

### 2. 取消limited限制，启用unlimited
#### 各版本关于jce unlimited policy的说明
- jdk9及以后版本，默认启用unlimited
- jdk8u161、7u171和6u16之前版本的，需要单独下载unlimited policy文件
- jdk8u161、7u171和6u16及以后版本的，unlimited policy文件已经在jdk中包含，但是默认未启用

> [jce unlimited policy file download page](https://www.oracle.com/java/technologies/javase-jce-all-downloads.html)

#### 启用unlimited
JDK 8u161、7u171和6u181及之后版本，都会在<java_home>/jre/lib/security/下面包含一个policy目录，里面包含limited和unlimited两个目录，这两个目录中分别包含了各自的policy文件（可以看到，其实就是相当于把unlimited的policy文件下载下来，帮我们放在了policy/unlimited目录中）

关于jdk采用哪个policy的策略，配置和说明如下：

```
The JDK determines the policy configuration to use as follows:

If the crypto.policy Security Property is defined, then the JDK uses the policy configuration specified by this Security Property.
If the crypto.policy Security Property is not set, and the traditional US_export_policy.jar and local_policy.jar files (which correspond to strong but limited cryptographic strength and unlimited cryptographic strength, respectively) are found in the legacy <java_home>/lib/security directory, then the JDK uses the policy configuration specified in these JAR files. This helps preserve compatibility for users upgrading from an older version of the JDK.
If the crypto.policy Security Property is not set, and the US_export_policy.jar and local_policy.jar files don't exist in the <java_home>/lib/security directory, then the JDK uses unlimited cryptographic strength, which is equivalent to cryto.policy=unlimited.
```

所以，综上所述
- 如果是用新版本的jdk，直接在<java_home>/jre/lib/security/java.security中配置cryto.policy=unlimited即可
- 如果是老版本的jdk，直接下载对应版本的unlimited policy文件，然后解压到<java_home>/jre/lib/security即可

> [oracle官方说明文档 - 请查看启用unlimited部分](https://docs.oracle.com/javase/8/docs/technotes/guides/security/crypto/CryptoSpec.html)