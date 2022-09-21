---
title: SHELL: 1.1 trap
date: 2019-10-10 13:22:00
categories: linux/shell
tags: [shell,command]
---

### 0. trap简介
trap是类unix操作系统上内置的一个shell命令，用来响应硬件信号或者其他事件的命令

语法：`trap [-lp] [[ARG] SIGNAL_SPEC...]`，意思是当收到`SIGNAL_SPEC`后，执行`ARG`指定的命令或者动作

### 1. 信号含义
`trap -l`会列出所有的信号
``` bash
trap -l
 1) SIGHUP	 2) SIGINT	 3) SIGQUIT	 4) SIGILL
 5) SIGTRAP	 6) SIGABRT	 7) SIGEMT	 8) SIGFPE
 9) SIGKILL	10) SIGBUS	11) SIGSEGV	12) SIGSYS
13) SIGPIPE	14) SIGALRM	15) SIGTERM	16) SIGURG
17) SIGSTOP	18) SIGTSTP	19) SIGCONT	20) SIGCHLD
21) SIGTTIN	22) SIGTTOU	23) SIGIO	24) SIGXCPU
25) SIGXFSZ	26) SIGVTALRM	27) SIGPROF	28) SIGWINCH
29) SIGINFO	30) SIGUSR1	31) SIGUSR2	
```

### 2. 实际应用
#### 1) 删除临时文件：
``` bash
cat << EOF > /tmp/test.sh
#!/bin/bash

trap "rm -rf /tmp/test" EXIT

touch /tmp/test
echo "good" > /tmp/test
ls -l /tmp/test
cat /tmp/test
EOF

sh /tmp/test.sh 
-rw-r--r--  1 user  wheel  5 Oct 11 13:38 /tmp/test
good

# 在上面脚本进入EXIT信号，即执行完毕退出时，会执行删除"/tmp/test"文件的action
ls -l /tmp/test
ls: cannot access /tmp/test: No such file or directory
```

#### 2) 禁止用户ctrl+c
``` bash
cat << EOF > /tmp/test.sh
#!/bin/bash

trap "echo \"don't ctrl+c\"" SIGINT

while true
do
    echo Sleeping
    sleep 10
done
EOF


sh test.sh 
Sleeping
^Cdon't ctrl+c
Sleeping
^Cdon't ctrl+c
Sleeping
^Cdon't ctrl+c
Sleeping
```