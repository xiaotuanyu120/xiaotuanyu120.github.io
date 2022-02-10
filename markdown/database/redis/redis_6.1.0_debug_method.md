---
title: redis: 6.1.0 DEBUG方法
date: 2019-05-13 09:33:00
categories: database/redis
tags: [redis,debug]
---

### 0. 需要DEBUG的情况
基本上都是一些未完全了解redis而导致的异常性能问题；  
举例说：
1. redis定时会流量增高
2. redis不定时流量增高

像我们就遇到了redis定时流量增高的问题。在业务代码方面排查感觉无处下手的时候，在redis这边使用工具查看当时的可疑拖慢性能的操作，是一个好方法

### 1. 参考链接
- [redis-cli的monitor命令](https://redis.io/commands/monitor)，用来记录详细的客户端操作命令，；需要注意的是，一些特殊的管理员命令，由于安全问题，是无法监控到的，例如说CONFIG命令。
- [rdbtools](https://github.com/sripathikrishnan/redis-rdb-tools)，一个开源python工具，可以把rdb文件转换成json格式，还能把内存里面的数据统计成csv格式的文件；特别方便来查找大容量的key

### 2. monitor命令用法
``` bash
# 1. 使用redis-cli
redis-cli -a 'password' monitor > result.out
# -a 是指定redis授权密码，如果无密码，可省略
# 想结束monitor过程，直接使用CTRL+C

# 2. 使用telnet
telnet localhost 6379
Trying 127.0.0.1...
Connected to localhost.
Escape character is '^]'.
MONITOR
+OK
+1339518083.107412 [0 127.0.0.1:60866] "keys" "*"
+1339518087.877697 [0 127.0.0.1:60866] "dbsize"
+1339518090.420270 [0 127.0.0.1:60866] "set" "x" "6"
+1339518096.506257 [0 127.0.0.1:60866] "get" "x"
+1339518099.363765 [0 127.0.0.1:60866] "del" "x"
+1339518100.544926 [0 127.0.0.1:60866] "get" "x"
QUIT
+OK
Connection closed by foreign host.
# 使用QUIT退出这个过程
```
> monitor只可以用来debug信息，长期开放会显著降低redis性能

### 3. rdbtools用法
#### 1) 安装rdbtools
``` bash
pip install rdbtools
```

#### 2) 转换rdb文件为json格式
``` bash
rdb -c json /var/redis/6379/dump.rdb > dump.json
# -c 等同于 --command
```

#### 3) 生成内存数据报告
``` bash
rdb -c memory /var/redis/6379/dump.rdb --bytes 128 -f memory.csv
# 生成内容是以下格式
# Database Number, Data Type, Key, Memory Used in bytes and RDB Encoding type.
```
> Memory usage includes the key, the value and any other overheads. 注意这个内存占用量是个近似值，实际使用会比这个大一点。

#### 4) 查看指定key的内存占用情况
``` bash
redis-memory-for-key -s localhost -p 6379 -a mypassword person:1
Key 			person:1
Bytes				111
Type				hash
Encoding			ziplist
Number of Elements		2
Length of Largest Element	8
```