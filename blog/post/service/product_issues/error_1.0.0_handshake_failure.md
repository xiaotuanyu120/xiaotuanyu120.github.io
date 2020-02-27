---
title: error 1.0.0 SSLHandshakeException handshake_failure
date: 2018-03-10 10:02:00
categories: service/product_issues
tags: [linux, java_env, ssl, handshake_failure]
---
### error 1.0.0 SSLHandshakeException handshake_failure

---

### 1. 错误信息
错误信息1：
``` java
[ERROR]_2018-03-08 16:31:10 990 : [http-apr-8580-exec-81] \
getHttpContentByBtParam 请求调用异常：
javax.net.ssl.SSLHandshakeException: Received fatal alert: handshake_failure
```

错误信息2
``` java
javax.net.ssl.SSLHandshakeException: sun.security.validator.ValidatorException: PKIX path building failed: sun.security.provider.certpath.SunCertPathBuilderException: unable to find valid certification path to requested target
```

### 2. 解决办法
#### 1) 解决方案一，增加证书到受信任列表中
问题的原因，是https使用的ssl证书没有加到信任列表里面，如果是直接用浏览器访问时，浏览器会提示我们不安全，但是依然会显示页面内容。但是因为是java程序连接，所以直接就提示创建连接失败了。  
这样的解决思路就来到了如何将需要连接的域名的ssl证书增加到受信任列表中，java程序是跑在jvm虚拟机里面，默认是用的是`<java-home>/lib/security/cacerts`。
给jvm增加ssl证书可以参照[microsoft java add certificate](https://docs.microsoft.com/en-us/azure/java-add-certificate-ca-store)
``` bash
# list all certificate
keytool -list -keystore cacerts

# example to add equifaxsecureca
keytool -keystore cacerts -importcert \
  -alias equifaxsecureca \
  -file Equifax_Secure_Certificate_Authority.cer
```
> 需要输入cacerts的密码，默认密码是changeit（如果你没有改动过jdk的密码的话）

> 如何通过浏览器获得证书（Equifax_Secure_Certificate_Authority.cer）
> - 通过浏览器访问接口url
> - 点击url框左边小绿锁
> - 点击“certificate”
> - 点击“详细信息”的tab
> - 点击“公钥”字段
> - 点击右下角“复制到文件”那个按钮
> - 弹出的窗口选择“下一步”
> - 弹出的窗口选择“Base64编码X.509(.CER)(S)”
> - 保存到本地即可，然后用笔记本打开，拷贝内容到服务器上

> 如果有多个jdk版本，注意要加到你想要增加证书的那个jdk版本上
``` bash
JAVA_HOME=/usr/local/jdk1.7.0_79

echo 'certification_file_content' > example.com.cer

${JAVA_HOME}/bin/keytool -keystore ${JAVA_HOME}/jre/lib/security/cacerts -importcert -alias example.com -file example.com.cer
```


#### 2) 解决方案二，关掉jdk的ssl证书白名单限制
**jdk7 - 替换无限制策略文件**
上面的方法之外，还有一种粗暴的解决办法，是直接下载oracle的一种无限制的策略文件到jdk中，来关闭ssl证书白名单限制。
[stackoverflow answer](https://stackoverflow.com/questions/38203971/javax-net-ssl-sslhandshakeexception-received-fatal-alert-handshake-failure)  

**jdk8 - 修改配置**
在[stackoverflow提问中](https://stackoverflow.com/questions/37741142/how-to-install-unlimited-strength-jce-for-java-8-in-os-x)，找到了jdk8的处理办法。
jdk8在update 151中加入了一个配置，用以打开和关闭无限制策略。而在update 161中，默认是启用了无限制策略。如果需要确认，可以查看以下配置
``` bash
vim $JAVA_HOME/jre/lib/security/java.security
******************************
crypto.policy=unlimited
******************************

# 1.  If the Security property "crypto.policy" has been defined,
#     then the following mechanism is used:
#
#     The policy files are stored as jar files in subdirectories of
# <java-home>/lib/security/policy.  Each directory contains a complete
# set of policy files.
#
#     The "crypto.policy" Security property controls the directory
#     selection, and thus the effective cryptographic policy.
#
# The default set of directories is:
#
#     limited | unlimited
#
# 2.  If the "crypto.policy" property is not set and the traditional
#     US_export_policy.jar and local_policy.jar files
#     (e.g. limited/unlimited) are found in the legacy
#     <java-home>/lib/security directory, then the rules embedded within
#     those jar files will be used. This helps preserve compatibility
# for users upgrading from an older installation.
#
# 3.  If the jar files are not present in the legacy location
#     and the "crypto.policy" Security property is not defined,
#     then the JDK will use the unlimited settings (equivalent to
#     crypto.policy=unlimited)
```
