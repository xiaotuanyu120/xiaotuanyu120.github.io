---
title: MYSQL-配置：常用基本配置
date: 2015-01-12 05:47:00
categories: database/mysql
tags: [database,mysql]
---
### MYSQL-配置：常用基本配置

---

### 1. mysql配置
``` bash
=====================================
[mysqld]


#################
## 服务基础配置
#################
## pid路径配置
pid_file=/usr/local/mysql/mysql.pid

## 程序目录和数据目录
datadir=/data/mysql
basedir=/usr/local/mysql

## 为MySQL client与server之间的本地通信指定一个套接字文件                      
socket = /tmp/mysql.sock

## 指定MsSQL侦听的端口     
port             = 3306       


#################
## 慢日志查询
#################
# 慢查询日志的超时时间
long_query_time = 1
# 慢查询日志路径，必须配合上面的参数一同使用  
log_slow_queries = /path/to/slow_queries  


# back_log参数的值指的是MySQL暂时停止响应新的请求之前，短时间内的多少个请求可以被存在堆栈中。不同操作系统上在这个队列上有自己的限制，对于linux系统而言，推荐设置为小于512的整数
back_log = 384


#################
## buffer和cache配置
#################
# key_buffer是用于索引块的缓冲区大小，增加它可得到更好处理的索引(对所有读和多重写)。索引被所有的线程共享，key_buffer的大小视内存大小而定。
key_buffer_size   = 384M      

# 为所有线程打开表的数量。增加该值能增加mysqld要求的文件描述符的数量。可以避免频繁的打开数据表产生的开销。可以查看数据库运行峰值时间的状态值Open_tables和Opened_tables,用以判断是否需要增加table_cache的值，即如果Open_tables接近table_cache的时候，并且Opened_tables这个值在逐步增加，就要考虑增大table_cache的值了。
table_cache      = 614K       

# 每个需要进行排序的线程分配该大小的一个缓冲区。增加这值加速ORDER BY或GROUP BY操作。
sort_buffer_size = 6M       
# 注意：该参数对应的分配内存是每连接独占！如果有100个连接，那么实际分配的总共排序缓冲区大小为100×6=600MB

# 联合查询操作所能使用的缓冲区大小，和sort_buffer_size一样，该参数对应的分配内存也是每个连接独享
join_buffer_size = 8M

# 读查询操作所能使用的缓冲区大小。和sort_buffer_size一样，该参数对应的分配内存也是每连接独享。
read_buffer_size = 2M        

# 指定MySQL查询结果缓冲区的大小，如果Qcache_hits的值非常大，则表明查询缓冲使用的非常频繁。
query_cache_size = 32M       
# 如果Qcache_lowmem_prunes的值非常大，则表明缓冲不够用
# 如果Qcache_free_blocks的值很大，则表明缓冲区中碎片很多

# 改参数在使用行指针排序之后，随机读用的。
read_rnd_buffer_size    = 8M

# MyISAM表发生变化时重新排序所需的缓冲
myisam_sort_buffer_size =64M


#################
## 线程配置
#################
# 最大并发线程数，取值为服务器逻辑CPU数量×2，如果CPU支持H.T超线程，再×2
thread_concurrency      = 8

# 缓存可重用的线程数，指定数目的线程可重用。一般每1G内存分配8
thread_cache_size        = 8

# 每个线程的堆栈大小，默认值192K基本是足够用了
thread_stack = 256K


#################
## 连接数与包容量上限
#################
# 设定在网络传输中一次消息传输量的最大值，最小1M，最大1G，必须设定为1024字节的倍数，新版MySQL中默认是4M
max_allowed_packet = 4M

# 设置每个主机的连接请求异常终端的最大次数，当超过该次数，MySQL服务器将禁止host的连接请求，知道MySQL服务器重启或通过flush host命令清空此host的相关信息。
max_connect_errors = 1000

# 指定MySQL允许的最大连接进程数。如果访问论坛经常出现Too Many Connections的错误提示，就要增大该值
max_connections = 768


# 设定内存临时表最大值，如果超过该值，则会将临时表写入磁盘。
tmp_table_size = 256M

# 避免MySQL的外部锁定，减少出错几率增强稳定性。
skip-locking                 

# 禁止MySQL对外部连接进行DNS解析，使用这一选项可以消除MySQL进行DNS解析的时间，如果开启该选项，则所有远程主机连接授权都要使用IP地址方式。
skip-name-resolve     

# 表示空闲的连接超时时间，默认是28800s，这个参数是和interactive_timeout一起使用的，也就是说要想让wait_timeout 生效，必须同时设置interactive_timeout
wait_timeout  = 8
interactive_timeout = 8
```
