---
title: php 1.1.0: 查看环境信息
date: 2015-01-12 05:47:00
categories: service/php
tags: [php]
---

### 1. php版本查看
``` bash
php -v
```

### 2. 配置文件php.ini路径查看
命令行方式查看phpinfo
``` bash
# 方式1
php -i | grep "Configuration File"

# 方式2
php -r "phpinfo();" | grep "Configuration File"
```

另一种方式查看phpinfo
``` bash
cat << EOF > second.php
<?php
phpinfo()
?>
EOF
```
通过浏览器访问这个文件（前提你必须在web服务器上做好php解析）  
![](/static/images/docs/service/php/phpinfo.png)

> PS: 关于apache使用php.ini的位置查看说明，可以参照[apache配置基础中的第五部分](/service/apache/1.1.0_apache_config_basic.html)

#### 3) 模块查看
``` bash
php -m
[PHP Modules]
bz2
calendar
Core
ctype
curl
date
ereg
exif
fileinfo
filter
ftp
gettext
gmp
hash
iconv
json
libxml
openssl
pcntl
pcre
Phar
readline
Reflection
session
shmop
SimpleXML
sockets
SPL
standard
tokenizer
xml
zip
zlib

[Zend Modules]
```