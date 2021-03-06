---
title: 版本: 1.0 python2.7:安装
date: 2016-09-23 16:01:00
categories: python/advance
tags: [python2.7,python]
---
### 版本: 1.0 python2.7:安装

---

### 1. 安装python2.7
#### 1) 安装环境
``` bash
yum install epel-release -y
yum groupinstall base "Development tools" -y
yum install gcc gcc-c++ zip zip-devel openssl openssl-devel sqlite-devel -y
```

#### 2) py2.7下载&解压缩
``` bash
wget https://www.python.org/ftp/python/2.7.11/Python-2.7.11.tgz
tar zxf Python-2.7.11.tgz
```

#### 3) py2.7编译安装
``` bash
cd Python-2.7.11
./configure --prefix=/usr/local/python27/
sed -i 's/#.*zlib zlibmodule.c/zlib zlibmodule.c/g' Modules/Setup
make
make install
```

#### 4) 配置PATH变量 & 修改命令alias
``` bash
echo 'export PATH=$PATH:/usr/local/python27/bin' >> /etc/profile
. /etc/profile
vim /root/.bashrc
************************
## 在alias列表下增加
alias python='python2.7'
************************
. /root/.bashrc
```

#### 5) 检查命令
``` bash
which python
python --version
```

#### 6) 问题
**问题描述:**
安装pip时提示
zipimport.ZipImportError: can't decompress data; zlib not available

**解决方法:**
重新编译
``` bash
cd Python-2.7.11
./configure --prefix=/usr/local/python27/
vim Modules/Setup
****************************
## 搜索zlib找到下面一行,去掉注释
zlib zlibmodule.c -I$(prefix)/include -L$(exec_prefix)/lib -lz
******************************
make
make install
```
