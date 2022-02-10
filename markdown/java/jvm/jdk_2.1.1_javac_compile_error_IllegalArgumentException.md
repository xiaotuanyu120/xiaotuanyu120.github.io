---
title: jdk: 2.1.1 javac error IllegalArgumentException
date: 2020-08-09 21:59:00
categories: java/jvm
tags: [jdk,javac,production_issue]
---

### 0. 报错信息
换了编译环境，然后线上原来运行正常的代码报错如下
``` java
java.lang.IllegalArgumentException: Name for argument type [java.lang.String]  
not available, and parameter name information not found in class file either. 
```

### 1. 解决方案

**排查过程**
- jdk版本不一致？，排除，开发和运行均为jdk7
- 代码问题？，排除，没有新的相关commit

因为这是由于更换了编译环境后出现的，所以使用老的编译环境编译上线测试，发现使用老的编译环境编译过的代码是对的。于是定位为编译问题，仔细检查了编译环境的区别，发现少了一个使用javac编译的时候，少了一个`-g`参数。据某博主和某些答主总结（见下面链接），是因为javac没有`-g`参数的时候会忽略某些spring中的参数，我暂时没有深入研究。留待以后祥查官方文档

> - [cnblog博客](https://www.cnblogs.com/mrcharles/p/11879810.html)
> - [stackoverflow answer](https://stackoverflow.com/questions/7484659/usage-of-requestparam-throws-error-in-spring-3)