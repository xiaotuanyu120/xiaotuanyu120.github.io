---
title: SHELL: 2.1 带有正则语句判断条件的 if 语句
date: 2019-09-28 22:07:00
categories: linux/shell
tags: [shell,variable]
---

### 0. if语句，带有正则判断
``` bash
# 1. 基本语法
# [[ "str_origin" =~ regex_rules ]]，代表匹配的话，结果为true
# [[ ！ "str_origin" =~ regex_rules ]]，代表匹配的话，结果为false
# 右侧正则规则，不可以使用双引号括起来

# 2. 关于正则字符串的转义
# [[ "str_origin" =~ regex_rules ]]判断中，需要对各种特殊字符进行转义操作，例如#,$, ,%等
# 也可以正则规则字符串单独写成一个变量，这样就不需要转义了
regex_rules="^(develop$|release//*)"
[[ "str_origin" =~ $regex_rules ]] && echo yes
# 同样，正则规则字符串变量也不可以使用双引号括起来

# 3. 实际使用例子
VERSION=18.09.3
IS_1809=18.09.*
[[ "${VERSION}" =~ ${IS_1809} ]] && echo "yes its 18.09"
```
> 参考链接：https://stackoverflow.com/questions/18709962/regex-matching-in-a-bash-if-statement