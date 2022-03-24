
---
title: haproxy: 配置和日志
date: 2022-03-24 10:53:00
categories: service/haproxy
tags: [haproxy]
---

## 1. haproxy配置

### 1) 常见的终止标志
- PR，The proxy blocked the client's request, either because of an invalid HTTP syntax, in which case it returned an HTTP 400 error to the client, or because a deny filter matched, in which case it returned an HTTP 403 error.

> 其他的见参考文档：[haproxy 8.5 部分配置](https://www.haproxy.org/download/1.4/doc/configuration.txt)，这里只列出我遇到过的

### 2) ACL配置
大概的配置流程就是

1. 需要先定义一个测试标准
2. 然后再根据上面的测试标准来做对应的动作


格式：`acl <aclname> <criterion> [flags] [operator] <value> ...`
> 含义是创建了一个新的aclname(或者替代旧的)，然后可以根据这个aclname来执行对应的action


**例如根据ip来源的配置**
```
acl in_src_ip_list src ip1 ip2 ip3 ...
tcp-request content accept if in_src_ip_list
tcp-request content reject
```

> 其他详情见参考文档：[haproxy 7. 部分配置](https://www.haproxy.org/download/1.4/doc/configuration.txt)