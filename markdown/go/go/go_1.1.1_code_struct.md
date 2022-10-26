---
title: GO 1.1.1 程序结构和编译
date: 2022-10-25 21:57:00
categories: go/go
tags: [go]
---

## 1. hello world
``` bash
# 在任意位置创建工程目录
mkdir -p $HOME/goproj/helloworld
cd $HOME/goproj/helloworld

# 创建第一个go文件main.go
touch main.go
```

`main.go`
``` go
// 包名称，整个go程序，只允许有一个main包
package main

// 引入标准库中的fmt目录下的所有包
// 这里的"fmt"指的是路径
import "fmt"

// main包中的main函数，这是整个程序的入口函数
func main() {
// 这里的"fmt"指的是包名称
    fmt.Println("hello, world")
}
```

编译执行
``` bash
# 编译
go build main.go

# 执行
./main
# 在开发环境中，可以直接执行go run main.go来调试
```

## 2. 复杂项目
正常的项目不止有一个go源文件，通常是多个包，每个包都有自己的第三方依赖。这种情况下编译过程如下
``` bash
# 1. 初始化mod
go mod init github.com/xiaotuanyu120/goproj01
# "github.com/xiaotuanyu120/goproj01" 代表的是"模块路径"
# 如果希望把project传到公网，就必须给一个可互联网访问的路径。
# 如果只是本地使用，可以用本地路径，比如"projectA"、"somthing/a/project"

# 最后一段为模块名称，".../mod_name"

# 2. 维护mod文件
go mod tidy
# 这个命令会自动分析第三方依赖，下载第三方依赖包和它的依赖包到本地的$GOMODCACHE目录中，默认值是$HOME/go/pkg/mod
# 并会维护当前模块的go.mod和go.sum文件

# 3. 编译项目
go build main.go
```