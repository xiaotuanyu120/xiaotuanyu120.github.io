---
title: GO 1.1.0 安装
date: 2017-03-28 13:40:00
categories: go/go
tags: [go]
---

### 1. 下载并安装go语言
> 环境：linux平台
``` bash
# 1. 下载go语言源码包
wget https://go.dev/dl/go1.19.2.linux-amd64.tar.gz

# 2. 解压源码包
tar -C /usr/local -xzf go1.19.2.linux-amd64.tar.gz

# 3. 配置环境变量
vim /etc/profile
****************************************
export PATH=$PATH:/usr/local/go/bin
****************************************
```

### 2. 查看go语言版本
``` bash
go version
```
> [如何安装多个go版本](https://go.dev/doc/manage-install#installing-multiple)

### 3. go环境配置
- `GOROOT`，go语言的根目录，一般情况无需自定义，除非是想在多个本地版本中切换
- `GOPATH`，`go path`包管理机制中的包管理根目录，目前包管理机制已经默认为`go module`。默认值是`$HOME/go`。
- `GO111MODULE`，控制使用`go path`模式，还是`go module`模式。设定项为`on`、`off`和`auto`
- `GOMODCACHE`，go模块下载目录，默认为`$HOME/go/pkg/mod`
> [go environment](https://pkg.go.dev/cmd/go#hdr-Environment_variables)