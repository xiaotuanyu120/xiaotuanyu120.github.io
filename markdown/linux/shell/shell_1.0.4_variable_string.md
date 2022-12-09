---
title: SHELL: 1.0.4 变量：字符串及字符串切片
date: 2022-12-09 21:16:00
categories: linux/shell
tags: [shell,variable]
---

## 0. shell中的字符串
``` bash
# 创建一个字符串变量
str01="a string"
```

## 1. 实际应用
### 1.1 获取字符串中的最后一位
``` bash
str01="abcd/"
echo "${str01: -1}" 
# 注意":"后面的" "，是为了在length为负数时避免和":-"混淆
```
> 参照[bash man docs](https://linux.die.net/man/1/bash)的`Parameter Expansion`中的`${parameter:offset:length}`