---
title: 内核调优: 1.1.1 优化nf_conntrack表来解决tcp包被drop的问题
date: 2019-02-22 13:38:00
categories: linux/advance
tags: [linux,nf_conntrack,kernel]
---

### 1. 问题背景?
机房某台服务器上的redis突然无法被访问，机房switch的监控检查该服务器有流量，但是zabbix上显示该服务器流量全部断掉，服务排查了正常。检查`/var/log/message`日志发现有大量的报错如下：
```
kernel: nf_conntrack: table full, dropping packet.
``` 

通过排查错误才知道，原来是linux会维护一个连接跟踪的表，上面的报错是因为内核默认的值无法满足目前redis的访问能力。

[参考文档资料](https://www.kernel.org/doc/Documentation/networking/nf_conntrack-sysctl.txt)

---

### 2. TCP优化
``` bash
vim /etc/sysctl.conf
***************************************
# 调整nf_conntrack表最大上限
net.netfilter.nf_conntrack_max=1048576
***************************************

# 使配置立即生效
sysctl -p
```

**其他nf_conntrack参数**
``` bash
sysctl -a|grep nf_conntrack

net.netfilter.nf_conntrack_acct = 0
net.netfilter.nf_conntrack_buckets = 16384
net.netfilter.nf_conntrack_checksum = 1
net.netfilter.nf_conntrack_count = 1
net.netfilter.nf_conntrack_dccp_loose = 1
net.netfilter.nf_conntrack_dccp_timeout_closereq = 64
net.netfilter.nf_conntrack_dccp_timeout_closing = 64
net.netfilter.nf_conntrack_dccp_timeout_open = 43200
net.netfilter.nf_conntrack_dccp_timeout_partopen = 480
net.netfilter.nf_conntrack_dccp_timeout_request = 240
net.netfilter.nf_conntrack_dccp_timeout_respond = 480
net.netfilter.nf_conntrack_dccp_timeout_timewait = 240
net.netfilter.nf_conntrack_events = 1
net.netfilter.nf_conntrack_expect_max = 256
net.netfilter.nf_conntrack_frag6_high_thresh = 4194304
net.netfilter.nf_conntrack_frag6_low_thresh = 3145728
net.netfilter.nf_conntrack_frag6_timeout = 60
net.netfilter.nf_conntrack_generic_timeout = 600
net.netfilter.nf_conntrack_helper = 0
net.netfilter.nf_conntrack_icmp_timeout = 30
net.netfilter.nf_conntrack_icmpv6_timeout = 30
net.netfilter.nf_conntrack_log_invalid = 0
net.netfilter.nf_conntrack_max = 65536
net.netfilter.nf_conntrack_sctp_timeout_closed = 10
net.netfilter.nf_conntrack_sctp_timeout_cookie_echoed = 3
net.netfilter.nf_conntrack_sctp_timeout_cookie_wait = 3
net.netfilter.nf_conntrack_sctp_timeout_established = 432000
net.netfilter.nf_conntrack_sctp_timeout_heartbeat_acked = 210
net.netfilter.nf_conntrack_sctp_timeout_heartbeat_sent = 30
net.netfilter.nf_conntrack_sctp_timeout_shutdown_ack_sent = 3
net.netfilter.nf_conntrack_sctp_timeout_shutdown_recd = 0
net.netfilter.nf_conntrack_sctp_timeout_shutdown_sent = 0
net.netfilter.nf_conntrack_tcp_be_liberal = 0
net.netfilter.nf_conntrack_tcp_loose = 1
net.netfilter.nf_conntrack_tcp_max_retrans = 3
net.netfilter.nf_conntrack_tcp_timeout_close = 10
net.netfilter.nf_conntrack_tcp_timeout_close_wait = 60
net.netfilter.nf_conntrack_tcp_timeout_established = 432000
net.netfilter.nf_conntrack_tcp_timeout_fin_wait = 120
net.netfilter.nf_conntrack_tcp_timeout_last_ack = 30
net.netfilter.nf_conntrack_tcp_timeout_max_retrans = 300
net.netfilter.nf_conntrack_tcp_timeout_syn_recv = 60
net.netfilter.nf_conntrack_tcp_timeout_syn_sent = 120
net.netfilter.nf_conntrack_tcp_timeout_time_wait = 120
net.netfilter.nf_conntrack_tcp_timeout_unacknowledged = 300
net.netfilter.nf_conntrack_timestamp = 0
net.netfilter.nf_conntrack_udp_timeout = 30
net.netfilter.nf_conntrack_udp_timeout_stream = 180
net.netfilter.nf_conntrack_udplite_timeout = 30
net.netfilter.nf_conntrack_udplite_timeout_stream = 180
```

### 3. 后续问题
后面又再次出现这个问题，就深入研究了一下。iptables是基于netfilter的，所以原因是因为启用了iptables，开启了tcp包的追踪。追踪文件是在/proc/net/nf_conntrack，里面会跟踪每个tcp连接的状态。

解决这个问题有几个方案
1. 提高netfilter跟踪tcp表的max值
2. 优化程序，降低短连接的数量
3. iptables里面使用`-j notrace`关闭tcp包的追踪

详情见[这篇博客](http://www.10tiao.com/html/488/201701/2247484116/1.html)或者深入搜索netfilter里面的nf_conntrack这个东西的原理，目前我们是通过第三个方案，禁用tcp追踪来解决的。