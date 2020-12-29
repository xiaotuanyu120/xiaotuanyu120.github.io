---
title: maven 1.4.0 命令行基础
date: 2020-12-29 20:36:00
categories: java/compile
tags: [java,maven]
---
### maven 1.4.0 命令行基础

### 1.1 编译子模块
```
mvn clean install -pl child-module -am -amd
```
> - pl: 模块名称
> - am: 编译指定子模块依赖的模块
> - amd: 编译依赖指定子模块的模块 