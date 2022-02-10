---
title: SHELL: 2.2 判断用户是否存在
date: 2019-09-28 23:09:00
categories: linux/shell
tags: [shell,variable]
---

### 1. 比较优雅的实现方式
``` bash
PHPFPM_USER=www
id ${PHPFPM_USER} >/dev/null 2>&1 || useradd -r -s /sbin/nologin ${PHPFPM_USER} && echo "${PHPFPM_USER} already exist!!"
```