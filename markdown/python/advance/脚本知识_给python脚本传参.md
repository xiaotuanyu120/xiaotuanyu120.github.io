---
title: 脚本知识: 给python脚本传参
date: 2015-11-25 11:29:00
categories: python/advance
tags: [python]
---

## 模块：sys
- 参数个数：len(sys.argv)
- 参数0：     sys.argv[0](脚本本身)
- 参数1：     sys.argv[1]
- 参数2：     sys.argv[2]

``` bash
vi test.py
***************************
import sys

print "script name: ", sys.argv[0]
for i in range(1, len(sys.argv)):
    print "argument", i, sys.argv[i]
***************************

python test.py hello world
script name: test.py
argument 1 hello
argument 2 world
```
