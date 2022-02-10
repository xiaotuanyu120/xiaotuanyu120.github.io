---
title: SHELL: 1.0.1 变量：内置变量
date: 2019-10-10 13:46:00
categories: linux/shell
tags: [shell,variable]
---

### 0. 内置变量简介
#### 1) 变量$?
``` bash
# $? 上个命令的执行结果
# 执行成功返回0值
rm -rf test.sh

echo $?
0

# 执行失败返回非0值
ls test.sh
ls: test.sh: No such file or directory

echo $?
1

ll
-bash: ll: command not found
echo $?
127
```

#### 2) 变量$$
``` bash
cat << EOF > /tmp/test.sh
#!/bin/bash

echo $$

while :; do
    echo test
    sleep 60
done
EOF

sh test.sh 
13920
test
^Z
[1]+  Stopped                 sh test.sh
ps aux |grep test.sh|grep -v grep
user             13920   0.0  0.0  4268636   1156 s000  T     1:52PM   0:00.00 sh test.sh
```