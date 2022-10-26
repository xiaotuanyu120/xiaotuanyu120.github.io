---
title: GO 1.0.0 go语言
date: 2022-10-25 20:33:00
categories: go/go
tags: [go]
---

## 0. go语言的诞生
计算机领域中的任何事物的诞生，都是要解决一些老旧的无法忍受的问题而产生的。go语言也不例外，谷歌的三位大佬在等待C++数以小时计的编译期间做了一场普通的讨论。大白话就是，C和C++虽然性能够强，但是编译速度太慢、过于复杂、对并发支持度不高，python等动态语言虽然易于上手，但是性能太弱。于是他们想搞一个新语言，这就是go。
> 三位谷歌大佬
> - 图灵奖获得者、C 语法联合发明人、Unix 之父肯·汤普森（Ken Thompson）
> - Plan 9 操作系统领导者、UTF-8 编码的最初设计者罗伯·派克（Rob Pike）
> -  Java 的 HotSpot 虚拟机和 Chrome 浏览器的 JavaScript V8 引擎的设计者之一罗伯特·格瑞史莫（Robert Griesemer）

之后，他们使用一封邮件开始正式讨论这个设想
```
Date: Sun, 23 Sep 2007 23:33:41 -0700
From: "Robert Griesemer" <gri@google.com>
To: "Rob 'Commander' Pike" <r@google.com>, ken@google.com
Subject: prog lang discussion
...
*** General:
Starting point: C, fix some obvious flaws, remove crud, add a few missing features
  - no includes, instead: import
  - no macros (do we need something instead?)
  - ideally only one file instead of a .h and .c file, module interface
should be extracted automatically
  - statements: like in C, though should fix 'switch' statement
  - expressions: like in C, though with caveats (do we need ',' expressions?)
  - essentially strongly typed, but probably w/ support for runtime types
  - want arrays with bounds checking on always (except perhaps in 'unsafe mode'-see section on GC)
  - mechanism to hook up GC (I think that most code can live w/ GC, but for a true systems
    programming language there should be mode w/ full control over memory allocation)
  - support for interfaces (differentiate between concrete, or implementation types, and abstract,
    or interface types)
  - support for nested and anonymous functions/closures (don't pay if not used)
  - a simple compiler should be able to generate decent code
  - the various language mechanisms should result in predictable code
```

> 几个事实：
> - go语言的名字，就是go，不是Golang。Golang只是go官方网站的名称，因为go.com已经被使用了。
> - go语言虽然在谷歌内部始于2007年9月20日，但是公布于众是在2009年10月30日，10天后的2009年11月10日，谷歌官宣Go语言项目开源，这一天被官方确定为Go语言的诞生日。
> - go语言使用gopher（地鼠）代指go语言开发者。

## 1. go语言的发展
2012 年 3 月 28 日，Go 1.0 版本正式发布，同时 Go 官方发布了“Go 1 兼容性”承诺：**只要符合 Go 1 语言规范的源代码，Go 编译器将保证向后兼容（backwards compatible），也就是说我们使用新版编译器也可以正确编译用老版本语法编写的代码。**

### **go语言的杀手级项目**
`Docker`, `Kubernetes`, `Prometheus`, `Ethereum`, `Istio`, `CockroachDB`, `InfluxDB`, `Terraform`, `Etcd`, `Consul` 等

### **go语言大事记**
- 2012：Go 1.0 发布，同时承诺“Go 1 兼容性”
- 2014：Go 1.4 发布，最后一个由C语言实现编译器和运行时的版本
- 2015：Go 1.5 发布，实现自举，大幅降低GC延迟
- 2018：Go 1.11 发布，引入新的Go包管理机制 go module
- 2021：Go 1.16 发布，Go module成为默认包管理机制
- 2022：Go 1.18 发布，支持泛型

## 2. go语言的设计哲学
现代的编程语言有很多，每个语言都根据自己的设计哲学做了不同的取舍。

而go语言的设计哲学，可以做以下归类
- 简单，不做特性缝合怪，致力于做减法，保持简单
- 显式，明确优于模糊
- 组合，没有选择面向对象（落笔之初对这里理解不深，留白，不误导他人）
- 并发，使用用户空间的goroutine来取代cpu中的线程调度，以达到轻量级调度，面向多核cpu的大规模并发的效果。并且增加了channel和select的辅助并发的原语。
- 面向工程，提供完善的工程支持工具，来解决程序构建慢、依赖管理失控、代码难于理解、跨语言构建难等问题