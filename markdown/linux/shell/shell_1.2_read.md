---
title: SHELL: 1.2 read
date: 2022-09-21 22:05:00
categories: linux/shell
tags: [shell]
---

### 0. read简介
read是将标准输入中读取逻辑行，然后将其转换成一个或多个变量的工具。一般是从文件中读取内容，然后赋值给shell脚本的变量。

### 1. read变量和选项
变量：
- `IFS`: 逻辑行中用于分隔不同field的分隔符

> 其他变量参见 [read manual](https://man7.org/linux/man-pages/man1/read.1p.html)

选项：
- `-r`: 把转义符`\`当做普通字符。

### 2. 实例：读取配置文件
配置文件内容：`var.conf`
``` bash
cat << EOF > var.conf
id=01
type=apple
EOF
```

读取配置的shell脚本：`load_var.sh`
``` bash
#!/bin/bash

# read content from conf file and transfer it to var value pair in shell script
#
# EXAMPLE:
#
# var.conf's content
# ==================================
# id=01
# type=apple
# ==================================
#
# this script will read one line each time,
# for example the first line "id=01", and
# separate it by "=", load the two part to
# var key and value: 
#     key=id; value=01
# then transfer it to new var pair in script
#     id=01

set -e

while IFS='=' read -r key value
do
    # ensure key and value is not empty
    if [[ -z ${key} ]] || [[ -z ${value} ]]; then
        continue
    fi

    # assign the content of var value to var which name is the content of var key 
    # EXAMPLE:
    #     orinal vars: key=foo; value=bar
    #     new var:     foo=bar
    if [[ ${key} == "id" ]] || [[ ${key} == "type" ]]; then
        eval "$key=$value"
    fi
done < ./var.conf

printf "  id = %s\ntype = %s\n" ${id} ${type}
```

执行后的输出演示
``` bash
sh load_var.sh
  id = 01
type = apple
```