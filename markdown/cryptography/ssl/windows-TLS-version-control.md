---
title: SSL: windows tls version and ciphers control
date: 2021-11-11 11:00:00
categories: cryptography/ssl
tags: [ssl,windows]
---

### 0. 背景
强度不够的ssl版本和ssl加密算法，会影响服务器的安全性，所以需要禁用掉它们。这里专注在windows版本（windows server 2012 R2）。

### 1. 禁用windows服务器的SSL/TLS版本
需要禁掉`ssl 2.0,ssl 3.0,tls 1.0,tls 1.1`。

**Windows Server 2012 R2 对SSL/TLS的支持情况**

| Windows OS                         | TLS 1.0 Client | TLS 1.0 Server | TLS 1.1 Client | TLS 1.1 Server | TLS 1.2 Client | TLS 1.2 Server | TLS 1.3 Client | TLS 1.3 Server |
| ---------------------------------- | -------------- | -------------- | -------------- | -------------- | -------------- | -------------- | -------------- | -------------- |
| Windows 8.1/Windows Server 2012 R2 | Enabled        | Enabled        | Enabled        | Enabled        | Enabled        | Enabled        | Not supported  | Not supported  |
> [windows server 2012 R2 TLS version support list](https://docs.microsoft.com/en-us/windows/win32/secauthn/protocols-in-tls-ssl--schannel-ssp-)

**在注册表设定开启tls 1.2**

```
# windows server 2012 R2
# Registry path: HKLM SYSTEM\CurrentControlSet\Control\SecurityProviders\SCHANNEL
# disable ssl 2.0, ssl 3.0, tls 1.0 and tls 1.1
[SSL 2.0\Client] "Enabled"=dword:00000000
[SSL 2.0\Client] "DisabledByDefault"=dword:00000001
[SSL 2.0\Server] "Enabled"=dword:00000000
[SSL 2.0\Server] "DisabledByDefault"=dword:00000001
[SSL 3.0\Client] "Enabled"=dword:00000000
[SSL 3.0\Client] "DisabledByDefault"=dword:00000001
[SSL 3.0\Server] "Enabled"=dword:00000000
[SSL 3.0\Server] "DisabledByDefault"=dword:00000001
[TLS 1.0\Client] "Enabled"=dword:00000000
[TLS 1.0\Client] "DisabledByDefault"=dword:00000001
[TLS 1.0\Server] "Enabled"=dword:00000000
[TLS 1.0\Server] "DisabledByDefault"=dword:00000001
[TLS 1.1\Client] "Enabled"=dword:00000000
[TLS 1.1\Client] "DisabledByDefault"=dword:00000001
[TLS 1.1\Server] "Enabled"=dword:00000000
[TLS 1.1\Server] "DisabledByDefault"=dword:00000001

# enable tls 1.2
[TLS 1.2\Client] "Enabled"=dword:00000001
[TLS 1.2\Client] "DisabledByDefault"=dword:00000000
[TLS 1.2\Server] "Enabled"=dword:00000001
[TLS 1.2\Server] "DisabledByDefault"=dword:00000000
```
> 详情见：[windows server 2012 R2 SSL/TLS/DTLS registry setting](https://docs.microsoft.com/en-us/previous-versions/windows/it-pro/windows-server-2012-r2-and-2012/dn786418(v=ws.11))

### 2. 禁用windows服务器的SSL ciphers
#### 2.1 禁用RC4
**windows server 2012 R2 对ciphers的支持列表**

| Operating system version               | Protocol support | Cipher suite support |
| -------------------------------------- | ---------------- | -------------------- |
| Windows Server 2012 R2 and Windows 8.1 | TLS 1.2          | AES 128              |
|                                        | TLS 1.1          | AES 256              |
|                                        | TLS 1.0          | RC4 128/128          |
|                                        | SSL 3.0          | RC4 56/128           |
|                                        | SSL 2.0          | RC4 40/128           |
|                                        | DTLS 1.0         | Triple DES 168       |
|                                        |                  | DES 56               |

> [windows server 2012 R2 ssl ciphers support list](https://docs.microsoft.com/en-us/previous-versions/windows/it-pro/windows-server-2012-r2-and-2012/dn786419(v=ws.11)#cipher-suite-and-protocol-support)
>
> RC4的都是需要禁用的

**在注册表设定ciphers关闭RC4**

```
# windows server 2012 R2
# Registry path: HKLM SYSTEM\CurrentControlSet\Control\SecurityProviders\SCHANNEL\Ciphers
# disable RC4
[RC4 40/128] "Enabled"=dword:00000000
[RC4 56/128] "Enabled"=dword:00000000
[RC4 128/128] "Enabled"=dword:00000000
```
> 详情见：[windows server 2012 R2 ssl ciphers registry setting](https://docs.microsoft.com/en-us/previous-versions/windows/it-pro/windows-server-2012-r2-and-2012/dn786418(v=ws.11))


#### 2.2 禁用CBC

**windows server 2012 R2 默认启用的ciphersuites列表**

| Cipher suite string                             | Allowed by SCH_USE_STRONG_CRYPTO | TLS/SSL Protocol Versions |
| ----------------------------------------------- | -------------------------------- | ---------------------------------- |
| TLS_ECDHE_RSA_WITH_AES_256_CBC_SHA384_P256      | Yes                              | TLS 1.2                            |
| TLS_ECDHE_RSA_WITH_AES_256_CBC_SHA384_P384      | Yes                              | TLS 1.2                            |
| TLS_ECDHE_RSA_WITH_AES_128_CBC_SHA256_P256      | Yes                              | TLS 1.2                            |
| TLS_ECDHE_RSA_WITH_AES_128_CBC_SHA256_P384      | Yes                              | TLS 1.2                            |
| TLS_ECDHE_RSA_WITH_AES_256_CBC_SHA_P256         | Yes                              | TLS 1.2, TLS 1.1, TLS 1.0          |
| TLS_ECDHE_RSA_WITH_AES_256_CBC_SHA_P384         | Yes                              | TLS 1.2, TLS 1.1, TLS 1.0          |
| TLS_ECDHE_RSA_WITH_AES_128_CBC_SHA_P256         | Yes                              | TLS 1.2, TLS 1.1, TLS 1.0          |
| TLS_ECDHE_RSA_WITH_AES_128_CBC_SHA_P384         | Yes                              | TLS 1.2, TLS 1.1, TLS 1.0          |
| TLS_DHE_RSA_WITH_AES_256_GCM_SHA384             | Yes                              | TLS 1.2                            |
| TLS_DHE_RSA_WITH_AES_128_GCM_SHA256             | Yes                              | TLS 1.2                            |
| TLS_DHE_RSA_WITH_AES_256_CBC_SHA                | Yes                              | TLS 1.2, TLS 1.1, TLS 1.0          |
| TLS_DHE_RSA_WITH_AES_128_CBC_SHA                | Yes                              | TLS 1.2, TLS 1.1, TLS 1.0          |
| TLS_RSA_WITH_AES_256_GCM_SHA384                 | Yes                              | TLS 1.2                            |
| TLS_RSA_WITH_AES_128_GCM_SHA256                 | Yes                              | TLS 1.2                            |
| TLS_RSA_WITH_AES_256_CBC_SHA256                 | Yes                              | TLS 1.2                            |
| TLS_RSA_WITH_AES_128_CBC_SHA256                 | Yes                              | TLS 1.2                            |
| TLS_RSA_WITH_AES_256_CBC_SHA                    | Yes                              | TLS 1.2, TLS 1.1, TLS 1.0          |
| TLS_RSA_WITH_AES_128_CBC_SHA                    | Yes                              | TLS 1.2, TLS 1.1, TLS 1.0          |
| TLS_ECDHE_ECDSA_WITH_AES_256_GCM_SHA384_P384    | Yes                              | TLS 1.2                            |
| TLS_ECDHE_ECDSA_WITH_AES_128_GCM_SHA256_P256    | Yes                              | TLS 1.2                            |
| TLS_ECDHE_ECDSA_WITH_AES_128_GCM_SHA256_P384    | Yes                              | TLS 1.2                            |
| TLS_ECDHE_ECDSA_WITH_AES_256_CBC_SHA384_P384    | Yes                              | TLS 1.2                            |
| TLS_ECDHE_ECDSA_WITH_AES_128_CBC_SHA256_P256    | Yes                              | TLS 1.2                            |
| TLS_ECDHE_ECDSA_WITH_AES_128_CBC_SHA256_P384    | Yes                              | TLS 1.2                            |
| TLS_ECDHE_ECDSA_WITH_AES_256_CBC_SHA_P256       | Yes                              | TLS 1.2, TLS 1.1, TLS 1.0          |
| TLS_ECDHE_ECDSA_WITH_AES_256_CBC_SHA_P384       | Yes                              | TLS 1.2, TLS 1.1, TLS 1.0          |
| TLS_ECDHE_ECDSA_WITH_AES_128_CBC_SHA_P256       | Yes                              | TLS 1.2, TLS 1.1, TLS 1.0          |
| TLS_ECDHE_ECDSA_WITH_AES_128_CBC_SHA_P384       | Yes                              | TLS 1.2, TLS 1.1, TLS 1.0          |
| TLS_DHE_DSS_WITH_AES_256_CBC_SHA256             | Yes                              | TLS 1.2                            |
| TLS_DHE_DSS_WITH_AES_128_CBC_SHA256             | Yes                              | TLS 1.2                            |
| TLS_DHE_DSS_WITH_AES_256_CBC_SHA                | Yes                              | TLS 1.2, TLS 1.1, TLS 1.0          |
| TLS_DHE_DSS_WITH_AES_128_CBC_SHA                | Yes                              | TLS 1.2, TLS 1.1, TLS 1.0          |
| TLS_RSA_WITH_3DES_EDE_CBC_SHA                   | Yes                              | TLS 1.2, TLS 1.1, TLS 1.0          |
| TLS_DHE_DSS_WITH_3DES_EDE_CBC_SHA               | Yes                              | TLS 1.2, TLS 1.1, TLS 1.0, SSL 3.0 |
| TLS_RSA_WITH_RC4_128_SHA                        | No                               | TLS 1.2, TLS 1.1, TLS 1.0, SSL 3.0 |
| TLS_RSA_WITH_RC4_128_MD5                        | No                               | TLS 1.2, TLS 1.1, TLS 1.0, SSL 3.0 |
| TLS_RSA_WITH_NULL_SHA256                        | Yes                              | TLS 1.2                            |
| Only used when application explicitly requests. |                                  |  	                              |
| TLS_RSA_WITH_NULL_SHA                           | Yes                              | TLS 1.2, TLS 1.1, TLS 1.0, SSL 3.0 |
| Only used when application explicitly requests. |                                  |  	                              |
| SSL_CK_RC4_128_WITH_MD5                         | No                               | SSL 2.0                            |
| Only used when application explicitly requests. |                                  |  	                              |
| SSL_CK_DES_192_EDE3_CBC_WITH_MD5                | Yes                              | SSL 2.0                            |
| Only used when application explicitly requests. |                                  |  	                              |

> 详情见：[windows server 2012 R2 ssl ciphersuites supporet list](https://docs.microsoft.com/en-us/windows/win32/secauthn/tls-cipher-suites-in-windows-8-1)
>
> 可以单个ciphersuit来禁用，但是对CBC的禁用使用这个方法是不生效的，正确的方法见下面。

上面只是文档上的体现的ciphers算法列表，**实际环境中的ciphers列表，可以通过以下命令查看**
``` bash
nmap --script ssl-enum-ciphers -p 3389 ip_address
# 会输出对应IP:PORT下使用的ssl ciphers列表
```

**通过设定SSP cipher order来限制cipher - CBC**

- step 1. 运行中打开`gpedit.msc`
- step 2. `Local Computer Policy` > `Administrative Template` > `Network` > `SSL Configuration setting` > `SSL Cipher Suite Order`
- step 3. 在弹出的界面中
  - 选中Enable
  - 编辑tlsv1.2 支持的非CBC的ciphers，拷贝到文本编辑器中，使用","连接这些ciphers字符串
  > 可以按照这个来配置，只启用TLSv1.2的GCM相关的加密算法：
  > `TLS_DHE_RSA_WITH_AES_256_GCM_SHA384,TLS_DHE_RSA_WITH_AES_128_GCM_SHA256,TLS_RSA_WITH_AES_256_GCM_SHA384,TLS_RSA_WITH_AES_128_GCM_SHA256`
  
  - 删除原有的SSL Cipher Suites内容，将新的ciphers字符串拷贝进去，然后apply
  - 使用命令应用策略`gpupdate /force`
  - 重启服务器

> [how to disable cbc mode cipher encryption in windows server 2012](https://social.technet.microsoft.com/Forums/windowsserver/en-US/a51f9574-73b0-4808-ad5f-4db081d80e6f/disable-cbc-mode-cipher-encryption-and-enable-ctr-or-gcm-cipher-mode-encryption-amp-disable-md5?forum=winserversecurity)
>
> 同样适用于windows server 2012 R2：[windows server 2016+: Manage Transport Layer Security](https://docs.microsoft.com/en-us/windows-server/security/tls/manage-tls)

> **IMPORTANT**: 一定注意，不要根据`SSL Cipher Suite Order`打开的界面上的右下角提示框里面的内容作为根据来设定ciphers的列表，而需要使用前面提到的`nmap命令`来设定。它右下角的提示框里面的内容应该是没有更新的，所以内容不对。

### 3.  禁用掉ssl版本和ssl cipher（RC4,CBC）之后，RDP无法连接是什么原因？
本来禁用掉SSL弱版本和SSL cipher（RC4、CBC）之后，还有对应的GCM算法来支持RDP。但是有些情况下，在windows server 2012 R2中采取了上述限制措施之后，使用nmap查看发现3389端口的ciphers列表为空，实际rdp也无法连接到服务器。

这有可能是因为GCM算法缺失造成的，windows server 2012 R2通过KB2919355这个更新包来提供了GCM的支持。安装完KB2919355这个更新包之后，重启服务器再测试就可以看到GCM的算法支持了。

> - **微软关于增加GCM的官方声明**：
>   [microsoft support: update add GCM](https://support.microsoft.com/en-us/topic/update-adds-new-tls-cipher-suites-and-changes-cipher-suite-priorities-in-windows-8-1-and-windows-server-2012-r2-8e395e43-c8ef-27d8-b60c-0fc57d526d94)

> - **安装对应更新包的具体方法**：
>   在[kb2919355下载链接](https://www.microsoft.com/en-us/download/details.aspx?id=42334)下载更新包之后，需要按照这样的顺序来安装：clearcompressionflag.exe, KB2919355, KB2932046, KB2959977, KB2937592, KB2938439, and KB2934018。
>   - **安装对应更新包出问题的解决方法**：如果安装的时候遇到了"The update is not applicable to your computer"这个错误，有可能是因为部分依赖更新包没有安装导致的，请在安装KB2919355之前，提前安装KB2939087和KB2975061两个更新包。然后再尝试安装KB2919355更新包。[参考文档](https://www.lemonbits.com/kb2919355-update-not-applicable-computer/)