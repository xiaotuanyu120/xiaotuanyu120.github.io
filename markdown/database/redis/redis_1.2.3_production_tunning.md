---
title: redis: 1.2.3 性能优化
date: 2019-12-23 17:08:00
categories: database/redis
tags: [database,redis]
---

### 访问限制
``` bash
# 禁用keys，严重拖慢性能
rename-command KEYS "u0utIN%t3"

# 禁用flush，防止误删数据
rename-command FLUSHDB "8yJ6rPyp-"
rename-command FLUSHALL "8yJ6rPyp-"

# 禁用config命令，提升安全性
rename-command CONFIG ""

# 禁用select
# - 切换database很容易发生问题
# - 集群中不支持多个database
rename-command SELECT ""
```
> 禁用select命令容易造成`Unknown command 'SELECT' reading the append only file`错误，原因是，aof机制中使用了select命令，但是我们给禁用了，所以它无法加载aof文件来启动redis