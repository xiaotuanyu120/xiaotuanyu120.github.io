---
title: SHELL 基础: 与或逻辑操作符
date: 2014-12-08 20:01:00
categories: linux/shell
tags: [linux,shell]
---

### 1. 逻辑操作符
操作符：`;`、`&&`和`||`  

含义：
- cmd1是否执行成功都会执行cmd2
`cmd1 ; cmd2 `

- 只有cmd1执行成功才会执行cmd2
`command1 && command2`

- 只有cm1执行失败才会执行cmd2
`command1 || command2  `