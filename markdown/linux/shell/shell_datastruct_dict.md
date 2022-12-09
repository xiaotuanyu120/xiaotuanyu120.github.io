---
title: 数据结构：字典
date: 2019-12-31 17:16:00
categories: linux/shell
tags: [shell,variable]
---

### 0. shell中的字典
``` bash
# 创建一个dict变量
declare -A animals
# 或者
# declare -A animals=( ["moo"]="cow" ["woof"]="dog")

# 给dict变量赋值
animals=( ["moo"]="cow" ["woof"]="dog")
# 或者
# animals=( [a]="2" [b]="4" )

# 或者
# animals=( \
# > [a]="2" \
# > [b]="4" \
# > )

# 轮询所有的值
for animal in "${animals[@]}"; do echo ${animal}; done
cow
dog

# 轮询所有的key
for animal in "${!animals[@]}"; do echo ${animal}; done
moo
woof

```