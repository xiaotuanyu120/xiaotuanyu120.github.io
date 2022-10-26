---
title: GO 1.1.3 构建应用
date: 2022-10-26 21:45:00
categories: go/go
tags: [go]
---

## 1. 构建应用演进历史
Go 语言的构建模式历经了三个迭代和演化过程，分别是最早期的GOPATH、1.5版本的 Vendor 机制，以及现在的 Go Module。

### 1.1 GOPATH
GOPATH 构建模式下，Go 语言通过环境变量 GOPATH 配置的路径下，搜寻第三方依赖包来构建应用。

在 GOPATH 构建模式下，解决依赖不存在的命令是 `go get ...`。不过这样只能获取执行命令当下时间依赖包的最新主线版本，而依赖包可能是不断演进的，因此，这种构建模式无法保证应用的可重现构建。


### 1.2 Vendor
Go 1.5 版本中引入了 Vendor 机制。本质就是在一个指定的 Vendor 目录中，将依赖包的特定版本拷贝进来。Go 编译器在编译时，优先查找 Vendor 目录中的依赖包，而不是直接去 GOPATH中寻找。

使用 Vendor 构建模式的最佳实践就是，将 Vendor 目录一起提交到应用代码库中。这样别人 clone 你的项目代码后，就可以实现可重现构建。

> 需要注意的是，若希望使用 Vendor 模式，需要将 Go 项目置于 GOPATH 路径中的 src 目录中。否则 Go 编译器不会理会 Go 项目目录下的 Vendor 目录的。

### 1.3 Go Module
Go 1.11 版本引入了 Go Module 机制，一个 Go Module 是一个 Go 包的集合，它是有版本的。

在 Go Module 机制下，通常一个 git 库就是一个 Go Module。每个 Go Module 项目根目录下会存在一个 go.mod 文件，Go Module 和 go.mod 是一一对应的关系。go.mod 文件所在的目录为 Go Module 的根目录，根目录和它的子目录的所有 Go 包都属于这个 Go Module。
> 同时还有另外一个文件 go.sum，这个文件记录的是 Go Module 当前版本内容的哈希值。这是 Go Module 的一个安全机制，当下载一个 Go Module 后，go 会使用 go.sum 和下载内容的哈希值对比，通过验证其一致性来保证下载的内容不被恶意篡改。

## 2. 了解 Go Module
### 2.1 创建 Go Module 的步骤
``` bash
# step 1. create Go Module
# syntax: "go mod init [path/to/module]"
go mod init github.com/someuser/somemodule
# OR "go mod init myproject/service/module01"

# step 2. auto anylysis dependencies
# syntax: "go mod tidy"
go mod tidy
# this command would auto download denpendency packages AND update go.mod
# default download dir is "$GOPATH/pkg/mod", but it can been customized by modifying GOMODCACHE env var.

# step 3. build app
# syntax: "go build"
go build
```

### 2.2 深入 Go Module 机制
#### **2.2.1 Go Module 的语义导入版本机制**
在 Go Module 构建模式下，一个符合 Go Module 要求的版本号，需满足语义版本规范的格式
```
v[major].[minor].[patch]
```
借助于语义版本规范格式，可以区分不同版本的先后顺序，以及它们的兼容性。

按照语义版本规范，主版本号不同的版本，是互不兼容的。而在主版本号相同的情况下，次版本号大都兼容之前的此版本号。补丁版本号不影响兼容性。

而且，Go Module 规定，如果一个包的新旧版本是兼容的，那么它们的包导入路径应该是相同的。

例如： v1.7.8 和 v1.8.1 的主版本号相同，那么它们的导入路径也相同；而 v1.8.1 和 v2.0.0 的主版本号不同，那么导入路径就可以按照如下处理
``` go
import (
    "github.com/someuser/somemodule"
    smv2 "github.com/someuser/somemodule/v2"
)
```

> 因为v0.y.z一般情况下是在初期开发阶段的不稳定阶段，Go Module 将 v0.y.z 和 v1.y.z 做同等对待，它们具有同样的导入路径。

#### **2.2.2 Go Module 的最小版本选择原则**
一般情况下，Go Module 只会依赖同一个版本的第三方包。但也存在 Go Module 下不同的包对同一个第三方包的不同版本存在依赖的情况，例如
```
main.go
go.mod
go.sum
internal
pkg1 // 依赖 3rd-module v1.1.0 [3rd-module latest version is v1.6.0]
pkg2 // 依赖 3rd-module v1.3.0
```
这种情况下，Go 会选择哪个版本的 `3rd-module` 来编译应用呢？

答案是 `v1.3.0` ，当前存在的许多主流编程语言，会通常会选择最新的版本，即上例中的 `v1.6.0`，依据是最新的版本通常情况下被认为更稳定和更安全。而 Go 的设计者认为，在考虑稳定和安全的基础上，也要尊重各个 Module 的诉求，`pkg1` 明确的要求依赖 `v1.1.0`，而 `pkg2` 明确的要求依赖 `v1.3.0`。**Go 会在该项目依赖项的所有版本中，选择符合项目要求的“最小版本”**。

拿前面的例子举例，符合项目要求的 `3rd-module` 的版本范围是 `v1.3.0 - v1.6.0`，所以最终 Go 的选择是 `v1.3.0`。

## 3. Go Module 的常见操作
### 3.1 为当前 Go Module 增加一个依赖项
``` bash
# step 1. add dependency to your code

# step 2. add dependency to go.mod
# method one
go get github.com/someuser/somemodule
# method two
go mod tidy
```

### 3.2 为已存在的依赖项升降级
``` bash
# How to check module's version list?
go list -m github.com/someuser/somemodule

# How to downgrade from v1.8.0 to v1.7.0?
# update your code first !!!
# method one
go get github.com/someuser/somemodule@v1.7.0
# method two
go mod edit -require=github.com/someuser/somemodule@v1.7.0
go mod tidy

# How to upgrade from v1.8.0 to v2.0.0?
# update your code first !!!
# method one
go get github.com/someuser/somemodule/v2
```

### 3.3 移除一个依赖
``` bash
# Update your code first !!!
# delete "import github.com/someuser/somemodule/v2"

# Is it gone already? Check all modules
go list -m all
...
github.com/someuser/somemodule/v2
...
# its still there

# How to remove a dependency?
go mod tidy
```

### 3.4 特殊情况：如何使用 Vendor？
在某些特殊场景，例如无法访问互联网的环境，或者一些内部的CI/CD中，可能会用到 Vendor 模式

``` bash
# How to Generate Vendor?
go mod vendor
# This command would
# - copy dependencies to vendor directory
# - maintain a file modules.txt in vendor directory

# How to Build in vendor mode?
go build -mod=vendor
```
> Go 1.14 及其以后的版本中，若 Go 项目中存在 vendor 目录，则会优先使用 vendor 模式来构建。除非使用 `go build -mod=mod`来指定 Go Module 构建模式。