---
title: php 1.2.1: PHP配置 - 安全配置
date: 2015-01-12 05:47:00
categories: service/php
tags: [php]
---
### php 1.2.1: PHP配置 - 安全配置

---

### 1. 配置disable_function
``` bash
## php.ini,配置disable_function禁用一些php模块
disable_functions = func1,func2...

## 常用func
eval,assert,popen,passthru,escapeshellarg,escapeshellcmd,passthru,exec,system,chroot,scandir,chgrp,chown,escapeshellcmd,escapeshellarg,shell_exec,proc_get_status,ini_alter,ini_restore,dl,pfsockopen,openlog,syslog,readlink,symlink,leak,popepassthru,stream_socket_server,popen,proc_open,proc_close

## safe模式是否开启对此配置无影响
## 链接：http://www.php.net/manual/en/ini.sect.safe-mode.php#ini.disable-functions
```

### 2. 配置open_basedir
```
## 不推荐全局配置(php.ini)
open_basedir = /dir1/:/dir2

## 推荐在apache的各虚拟主机配置文件中配置(例如httpd-vhost.conf)
## 语法：php_admin_value name value
php_admin_value open_basedir "/dir1/:/dir2/"
```

> `open_basedir`解释说明
> a. 将 PHP 所能打开的文件限制在指定的目录树，包括文件本身。本指令不受安全模式打开或者关闭的影响。
> b. 当一个脚本试图用例如 fopen() 或者 gzopen() 打开一个文件时，该文件的位置将被检查。当文件在指定的目录树之外时 PHP 将拒绝打开它。所有的符号连接都会被解析，所以不可能通过符号连接来避开此限制。
> c. 特殊值"."指明脚本的工作目录将被作为基准目录。但这有些危险，因为脚本的工作目录可以轻易被 chdir() 而改变。
> d. 在 httpd.conf 文件中中，open_basedir 可以像其它任何配置选项一样用"php_admin_value open_basedir none"的方法关闭（例如某些虚拟主机中）。
> e. 在Windows中，用";"分隔目录。在任何其它系统中用":"分隔目录。
> f. 作为 Apache 模块时，父目录中的 open_basedir 路径自动被继承。
> g. 用open_basedir指定的限制实际上是前缀，不是目录名。也就是说"open_basedir = /dir/incl"也会允许访问"/dir/include"和"/dir/incls"。如果要将访问限制在仅为指定的目录，用斜线结束路径名。例如："open_basedir = /dir/incl/"。

> [参考链接](http://php.net/manual/zh/ini.core.php#ini.open-basedir)