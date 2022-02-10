---
title: openssh 1.0.1 sshd 密钥认证错误原因排查
date: 2021-02-16 22:47:00
categories: linux/advance
tags: [openssh,sshd,selinux]
---

### 1. `StrictsModes Yes`影响的原因
[`StrictsModes`](https://www.freebsd.org/cgi/man.cgi?sshd_config%285%29)默认为启用，用来控制sshd是否在处理用户登入之前来检查相关文件和家目录的权限。

详细规则：
- 家目录 > 只能用户自己拥有写权限（属主属组是用户，权限是700、755、750等）
- .ssh目录 > 只能用户自己拥有读写执行权限（属主属组是用户，权限是700）
- authorized_keys > 只能用户自己拥有读写权限（属主属组是用户，权限是600）

所以基本上检查权限就检查以上三个即可。并不推荐将`StrictsModes`修改为`No`，因为将自己的公钥文件设定为全局可写，是很危险的事情。

### 2. `selinux`影响的原因
selinux默认给sshd有一个policy，关于文件方面，都是有固定的位置给授权了lable，一般情况下，不会影响密钥认证的过程。

但是以下情况会影响：
- 修改了authorized_keys的位置
- 用户家目录不在/home下

此时因为修改了sshd密钥认证文件的位置，所以默认的sshd的selinux policy就无法正确的给文件正确的lable，所以此时需要我们手动来修正，具体的修正过程，见[selinux sshd public key lable](/linux/advance/selinux_1.0.2_sshd_public_key_lable.html)