---
title: php-fpm error: 1.1.0 容器中开启慢日志后的permission dennied错误
date: 2020-04-29 11:28:00
categories: service/php
tags: [php,error,php-fpm,capability]
---

### 0. 问题背景
使用容器启动了php-fpm，开启了慢日志

慢日志配置 - php-fpm.conf
```
slowlog = /var/log/php-fpm/$pool.log.slow
request_slowlog_timeout = 3
```

此时出现了报错

error报错信息
```
[29-Apr-2020 01:36:20] NOTICE: about to trace 8
[29-Apr-2020 01:36:20] ERROR: failed to open /proc/8/mem: Permission denied (13)
[29-Apr-2020 01:36:20] NOTICE: finished trace of 8	
```

查到了[这篇github issuce](https://github.com/docker-library/php/issues/498)，里面大概意思讲说，php-fpm是通过trace其他进程来支持某些功能（例如慢日志，获取其他进程响应request信息）
``` c
int fpm_trace_ready(pid_t pid) /* {{{ */
{
	char buf[128];

	sprintf(buf, "/proc/%d/" PROC_MEM_FILE, (int) pid);
	mem_file = open(buf, O_RDONLY);
	if (0 > mem_file) {
		zlog(ZLOG_SYSERROR, "failed to open %s", buf);
		return -1;
	}
	return 0;
}
/* }}} */
```

但是docker为了安全性，默认是未开启所有的[linux capability](http://man7.org/linux/man-pages/man7/capabilities.7.html)。比如说，php-fpm的trace依赖的`CAP_SYS_PTRACE`就不在[docker默认开启的CAP名单](https://docs.docker.com/engine/reference/run/#runtime-privilege-and-linux-capabilities)中。

此时我们要解决这个问题，就需要额外开启`CAP_SYS_PTRACE`

docker run方法： `--cap-add SYS_PTRACE`

docker-compose方法：
``` yaml
    cap_add:
      - SYS_PTRACE
```