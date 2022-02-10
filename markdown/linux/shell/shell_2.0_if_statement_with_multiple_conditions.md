---
title: SHELL: 2.0 多判断条件的 if 语句和简化写法的 if 语句
date: 2019-09-28 22:07:00
categories: linux/shell
tags: [shell,variable]
---

### 0. if语句，单纯只是多判断条件
``` bash
if [ condition1 ] && [ condition2 ] || [ condition3 ]
then
	#statements
elif [ condition ]
then
	#statements
else
	#statements
fi
```

### 1. if语句，嵌套多判断条件
``` bash
if ([ condition1 ] && [ condition2 ]) || ([ condition3 ] || [ condition4 ])
then
	#statements
elif [ condition ]
then
	#statements
else
	#statements
fi
```

### 2. if语句，简要写法和复杂判断条件
``` bash
# 如果没有elif和else，可以用下面的语句简化if语句
[[ condition1 ]] && statements

# 如果是多个判断条件和多个后续语句
([[ condition1 ]] && [[ condition2 ]]) || ([[ condition3 ]] || [[ condition4 ]]) && (
	statement1;
	statement2;
	statement3)
```