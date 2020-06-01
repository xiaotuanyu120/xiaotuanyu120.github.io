---
title: keytool 1.1.0 命令使用说明
date: 2020-06-01 13:28:00
categories: java/security
tags: [keytool]
---
### keytool 1.1.0 命令使用说明

---

### 0. 什么是keytool？
keytool是管理keystore数据文件的工具，keystore文件可储存私钥、x509证书链和受信任的证书列表

其中储存私钥和x509证书链的keystore文件，称为keystore，主要用于服务端，接收ssl请求；

其中储存根证书和受信任的自建证书的keystore文件，称为truststore，主要用于客户端，发起ssl请求；

### 1. 创建一个只有一个entry的truststore
``` bash
java -version
java version "1.8.0_251"
Java(TM) SE Runtime Environment (build 1.8.0_251-b08)
Java HotSpot(TM) 64-Bit Server VM (build 25.251-b08, mixed mode)

echo | openssl s_client -servername www.google.com -connect www.google.com:443 -showcerts|sed -ne '/-BEGIN CERTIFICATE-/,/-END CERTIFICATE-/p' > www.google.com.cer

keytool -importcert \
  -noprompt \
  -keystore googleonly.jks \
  -trustcacerts \
  -storepass randompass \
  -alias www.google.com-ca \
  -file www.google.com.cer

keytool -list -keystore googleonly.jks -storepass randompass
Keystore type: jks
Keystore provider: SUN

Your keystore contains 1 entry

www.google.com-ca, Jun 1, 2020, trustedCertEntry, 
Certificate fingerprint (SHA1): 95:E2:82:36:E0:41:A6:FA:8E:53:8C:18:85:F6:F3:B2:2D:C7:A2:C9
```

### 2. 导入证书到keystore中
``` bash
# 获取域名证书
domain=www.example.com
echo|openssl s_client -servername ${domain} -connect ${domain}:443|\
    sed -ne '/-BEGIN CERTIFICATE-/,/-END CERTIFICATE-/p' > ${domain}.crt

# example to add equifaxsecureca
keytool -keystore cacerts -importcert \
  -storepass changeit \
  -noprompt \
  -trustcacerts \
  -alias ${domain} \
  -file ${domain}.crt
```
> cacerts的密码，默认密码是changeit（如果你没有改动过jdk的密码的话）

> 浏览器获取证书的方法，请查看[获取证书方法](/cryptography/basic/openssl_1.3.0_retrieve_certificate_info.html)

#### 如果有多个jdk版本，注意要加到你想要增加证书的那个jdk版本上

``` bash
JAVA_HOME=/usr/local/jdk1.7.0_79
# 获取域名证书
domain=www.example.com
echo|openssl s_client -servername ${domain} -connect ${domain}:443|\
  sed -ne '/-BEGIN CERTIFICATE-/,/-END CERTIFICATE-/p' > ${domain}.crt

${JAVA_HOME}/bin/keytool -keystore ${JAVA_HOME}/jre/lib/security/cacerts -importcert \
  -storepass changeit \
  -noprompt \
  -trustcacerts \
  -alias ${domain} \
  -file ${domain}.crt
```

> 给jdk增加ssl证书可以参照[microsoft java add certificate](https://docs.microsoft.com/en-us/azure/java-add-certificate-ca-store)

### 3. 查看keystore信息
``` bash
keytool -list -keystore cacerts
```