---
title: GO 1.3.0 原生工具
date: 2017-06-03 16:21:00
categories: go/go
tags: [godoc,gofmt,goimport]
---

### 1. goimport
``` bash
# 安装goimport
go install golang.org/x/tools/cmd/goimports@latest

# 然后将go的bin环境目录增加到PATH变量中
# 默认是“$HOME/go/bin”
```
> 用于自动添加使用的包和自动删除未使用的包

---

### 2. godoc
godoc是官方的生成go源码doc的工具

---

### 3. gofmt
很多编辑器和IDE使用此函数来格式化golang源码
