---
title: php error: 不间断502问题
date: 2015-12-08 14:37:00
categories: service/php
tags: [php,error]
---

### 1. 问题描述
访问网站动态页面的时候不间断出502错误(服务器内部错误)
 
### 2. 问题排查过程(年轻时)
``` bash
netstat -c 2 -i
# 看流量正常

ps -aux |grep php
# 发现结果中大部分php进程是在R状态(running状态),而且一直持续
```
> PS: 以前考虑的太不全面了，而且追问题没追到根因。
> 首先，查看流量，这个无可厚非，虽然我现在绝对不会首要查看这个方向。因为502代表的是服务器内部错误，意思是请求已经被服务器接收。个人理解是nginx接收了，在转发给php时，发生以下几种可能的情况：
> - php没有进程来处理这个请求
> - php接收了这个请求，但是没有正常的处理，报错了
> 然后，如果查看大部分进程在R状态的话，那其实有可能是请求处理速度过慢，此时我们可以打开慢日志或者错误日志，来根据日志分析
> 另外，其实应该看一下系统环境、nginx、php优化配置，看是不是优化未到位，或者优化参数匹配的有问题导致的，详细可以参考[php+nginx高并发调优](/service/php/php_1.4.0_configuration_concurrent_connection_tunning_with_nginx.html)

### 3. 解决方案(年轻时)
``` bash
crontab -e
# * * * * * /usr/local/php/sbin/php-fpm reload

# 相当于每分钟平滑重启一遍php，把处在R状态的php进程，重置为S状态（stop状态，随时待命）
# 另外发现php进程有点多，于是去配置文件中修改最大进程数和最大处理请求数
vi /usr/local/php/etc/php-fpm.conf
# pm.max_children = 50
# pm.max_requests = 500
```
> PS: 我只能说当时的解决方式太粗暴了。。。