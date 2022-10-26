---
title: GO 1.1.2 目录结构
date: 2022-10-25 22:26:00
categories: go/go
tags: [go]
---

## 1. 几次目录结构的演进
### 1.1 Go 1.4 版本中，移除 pkg 和引入 internal
Go 1.4 版本中删除了 pkg 这一中间层目录，并引入了 internal 目录。

出于简化层次的目的，原本`src/pkg/xxx`改为`src/xxx`。

出于分类和清晰用途的目的，引入了 internal 目录，在 internal 下的包只能被本项目的包导入，而不能被外部的包导入。

### 1.2 Go 1.6 版本中，增加 vendor 目录
为了解决版本依赖问题，Go 允许源码不在 GOPATH 中寻找依赖包，而是在 vendor 目录下面寻找依赖包。这样开发者就可以在 vendor 中自己管理依赖包的版本，从而解决不同开发环境依赖包版本不一致的问题。

vendor 机制和目录的引入，让 Go 第一次拥有了可重现构建的能力

### 1.3 Go 1.13 版本中，增加了 go.sum 和 go.mod
依旧是为了解决版本依赖的问题，vendor 机制有很多缺点，例如，需要手工管理依赖包版本，另外会给代码审核带来干扰等。于是 go module 出现了，引入了 go.mod 来明确了第三方包及其版本，可以实现精准构建。

## 2. 典型结构布局
```
- exe-layout
  - cmd/
    - app1/
      - main.go
    - app2/
      - main.go
  - go.mod
  - go.sum
  - internal
    - pkga/
      - pkga.go
    - pkgb/
      - pkgb.go
  - pkg1/
    - pkg1.go
  - pkg2/
    - pkg2.go 
  - vendor/
```
> vendor 目录是可选的，在某些没有公网访问的场景可用，使用vendor模式构建：`go build -mod=vendor`

> Go 1.14 版本及其后续版本，当项目根目录存在 vendor 目录时，默认采用 vendor 模式来构建应用。可以使用 `go build -mod=mod` 来切换到 Go Module 模式。详细说明参见[Go 1.14 changelog](https://go.dev/doc/go1.14)

上面提到的例子有多个app构建，其实更建议使用下面app互相隔离的方式
```
- single-exe-layout
  - main.go
  - go.mod
  - go.sum
  - internal
    - pkga/
      - pkga.go
    - pkgb/
      - pkgb.go
  - pkg1/
    - pkg1.go
  - pkg2/
    - pkg2.go 
  - vendor/
```

**总结：虽然上面有提到了多种目录结构，但是 Go 官方并没有给出一个固定的目录结构范式。而且目前主流的开源项目的目录结构也都有着些许的差别，所以并不需要完全一对一的参照本文的模板来创建项目。**