---
title: SHELL: 1.0.2 变量：计算
date: 2019-10-10 13:56:00
categories: linux/shell
tags: [shell,variable]
---

### 0. shell中的计算
``` bash
cat << EOF > /tmp/test.sh
#!/bin/bash

a=1
b=2
echo $((${a}+${b}))

i=0
while [ $i -lt 10 ] ;do
	echo $i
	((i++))
done
EOF

sh test.sh 
3
0
1
2
3
4
5
6
7
8
9
```