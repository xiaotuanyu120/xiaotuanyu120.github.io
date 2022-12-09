---
title: GO 1.1.4 入口函数和包初始化
date: 2022-10-27 20:49:00
categories: go/go
tags: [go]
---

## 1. 背景
一个 Go 项目中有多个包，一个包有多个文件，同时每个包中又有多个常量、变量、各种函数和方法，那 Go 代码是使用什么顺序加载它们，又是从哪里开始执行的呢？

## 2. `main.main` 函数：Go 应用的入口函数
Go 语言中有一个特殊的函数 `main.main`，它是所有 Go 可执行应用的用户层执行逻辑的入口函数。

`main.main` 函数没有参数，也没有返回值
``` go
func main() {
    fmt.Println("Hello world")
}
```

Go 语言要求，可执行程序的main包，必须要包含main函数，否则 Go 编译器会报错
``` bash
go build main.go 
# command-line-arguments
runtime.main_main·f: function main is undeclared in the main package
```

另外值得注意的是，其他的包也可以拥有自己的main函数，但是不同包中的main函数只能在自己的包内部使用。
``` go
// main.go
package main

import (
	"fmt"
	"github.com/fakeuser/mod/pkg1"
)

func main() {
	fmt.Println("Hello world")
	pkg1.Main()
}
```
``` go
// pkg1/pkg1.go
package pkg1

import "fmt"

func Main() {
	main()
}

func main() {
	fmt.Println("main from pkg1")
}
```
`pkg1` 包中的 `main` 函数，只能在 `pkg1` 包内部使用，这个例子就是在 `pkg1.Main` 这个函数中执行了它
``` bash
# What is the output?
go run main.go
Hello world
main from pkg1
```

## 3.  `init()` 函数：包初始化函数
`main.main` 虽然是用户层执行逻辑的入口函数，但是它并不是用户层被执行的第一个函数，`init` 函数才是。如果 `main` 包依赖的包中有 `init` 函数，或者 `main` 包自身有包含 `init` 函数，那么 Go 在这个程序初始化的时候，会自动调用它的 `init` 函数，因此，这些 `init` 函数的执行会在 `main.main` 函数之前。

`init` 函数也是一个无参数无返回值的函数
``` go
func init() {
	fmt.Println("print from init")
}

func main() {
	fmt.Println("Hello world")
}
```

用户无法显式的调用 `init` 函数
``` go
func main() {
	init()
}
```
执行后会发生编译错误
``` bash
go run main.go  
# command-line-arguments
./main.go:14:2: undefined: init
```

实际上，每一个 Go 包，或者每一个 Go 包中的源文件，都可以声明多个 `init` 函数。Go 编译器会特别对待 `init` 函数，因此不会发生函数名称重复的报错。

在初始化时，Go 会按照一定的次序，顺序并逐一的执行每个 `init` 函数。一般情况下，先传递给 Go 编译器的源文件中的 `init` 函数会被先执行；同一个源文件中的不同 `init` 函数，会根据声明的先后顺序依次执行。

## 4. Go 包的初始化次序
从程序逻辑结构角度来看，Go 包是程序逻辑封装的基本单元，每个包都可以理解为一个“自治”的、封装良好的、对外暴露有限接口的基本单元。一个 Go 程序就是一组包组成的，程序的初始化就是这些包的初始化。每个 Go 包还会有自己的依赖包、常量、变量、init函数等。

Go 包的初始化次序流程图
![](/static/images/docs/go/go_1.1.4_01.jpg)

初始化次序注意点：
- 每一个 Go 包的初始化内容都遵循 “常量 -> 变量 -> init 函数”的顺序
- Go 包的初始化会采用“深度优先”原则
- 包内多个 `init()` 函数按照声明顺序初始化

### 4.1 Go 包初始化次序示例
包之间的依赖关系如下
``` bash
# 依赖关系
main > pkg1 > pkg3
     > pkg2 > pkg3
```

`main.go`
``` go
package main

import (
	"fmt"
	_ "github.com/fakeuser/mod/pkg1"
	_ "github.com/fakeuser/mod/pkg2"
)

const c int = 1

var (
	_        = constInit()
	s string = varInit()
)

func init() {
	fmt.Println("main init()")
}

func main() {
	fmt.Println("Hello world")
}

func varInit() string {
	fmt.Println("main var init")
	return ""
}

func constInit() string {
	fmt.Println("main const init")
	return ""
}
```

`pkg1/pkg1.go`
``` go
package pkg1

import (
	"fmt"
	_ "github.com/fakeuser/mod/pkg3"
)

const c int = 1

var (
	_        = constInit()
	s string = varInit()
)

func init() {
	fmt.Println("pkg1 init()")
}

func varInit() string {
	fmt.Println("pkg1 var init")
	return ""
}

func constInit() string {
	fmt.Println("pkg1 const init")
	return ""
}
```

`pkg2/pkg2.go`
``` go
package pkg2

import (
	"fmt"
	_ "github.com/fakeuser/mod/pkg3"
)

const c int = 1

var (
	_        = constInit()
	s string = varInit()
)

func init() {
	fmt.Println("pkg2 init()")
}

func varInit() string {
	fmt.Println("pkg2 var init")
	return ""
}

func constInit() string {
	fmt.Println("pkg2 const init")
	return ""
}
```

`pkg3/pkg3.go`
``` go
package pkg3

import "fmt"

const c int = 1

var (
	_        = constInit()
	s string = varInit()
)

func init() {
	fmt.Println("pkg3 init()")
}

func varInit() string {
	fmt.Println("pkg3 var init")
	return ""
}

func constInit() string {
	fmt.Println("pkg3 const init")
	return ""
}
```

执行查看各个包的初始化顺序
``` bash
go run main.go
pkg3 const init
pkg3 var init
pkg3 init()
pkg1 const init
pkg1 var init
pkg1 init()
pkg2 const init
pkg2 var init
pkg2 init()
main const init
main var init
main init()
Hello world
```

## 5. init() 函数的用途

### 5.1 重置包级变量值
### 5.2 实现对包级变量的复杂初始化
### 5.3 在 init() 函数中实现注册模式