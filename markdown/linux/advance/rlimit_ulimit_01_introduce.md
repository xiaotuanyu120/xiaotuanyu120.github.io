---
title: rlimit ulimit: 简明介绍
date: 2016-08-23 03:04:00
categories: linux/advance
tags: [linux,ulimit,fs-max]
---

### 0. linux系统资源限制简介
单台计算机的资源不可能是无限的，所以linux系统需要对资源进行限制。linux系统中对系统资源的限制设定，提供了三个系统调用
- setrlimit，设定当前进程的rlimit
- getrlimit，设定当前进程的rlimit
- prlimit，update指定pid的进程的rlimit

> 资源限制分为soft limit和hard limit。只有root可以调高hard limit，其他用户可以调整soft limit和hard limit，但无法将其设定为超过hard limit的数值。

ulimit就是shell内置的基于上面的系统调用研发的，应用对象为用户或用户组的系统级别的rlimit管理工具。

**ulimit命令使用范围，特别注意 ！！**
ulimit命令只能对当前登录的shell环境生效，一旦用户登出当前shell，之前所做的设定修改则失效；

**ulimit配置文件使用范围和生效方式，特别注意！！**
ulimit的主要配置文件为`/etc/security/limits.conf`，而`/etc/security/limits.d/*.conf`以c中的字符排序进行加载，重复的规则会以后加载的顺序覆盖前者。上述配置修改过后，只对通过[PAM（Pluggable Authentication Modules）](https://en.wikipedia.org/wiki/Linux_PAM)登录的用户环境生效（已经登录过的需要重新登录shell）。

鉴于以上使用限制，ulimit只能应用于未经过其他rlimit管理工具管理的，且通过**PAM登录**过的login shell中fork出的进程。
> “通过PAM登录”，这里是针对shell环境来说的，其实并不一定是需要登录这个动作，而是只要经过PAM授权，调用了PAM的pam_limits.so这个模块，这个模块就会加载`/etc/security/limits.conf`，从而给进程修改了limit。（可见下面的crontab，就是未经过ulimit的一个例子）

> [login shell vs non-login shell](/linux/advance/bash_02_00_login_shell_vs_non_login_shell.html)

> `/etc/security/limits.conf`中的注释说明
This file sets the resource limits for the users logged in via PAM.
It does not affect resource limits of the system services.

### 1. ulimit工具使用说明
**ulimit命令使用说明**

``` bash
# 查看所有信息
ulimit -a
core file size          (blocks, -c) 0
data seg size           (kbytes, -d) unlimited
scheduling priority             (-e) 0
file size               (blocks, -f) unlimited
pending signals                 (-i) 3876
max locked memory       (kbytes, -l) 64
max memory size         (kbytes, -m) unlimited
open files                      (-n) 1024
pipe size            (512 bytes, -p) 8
POSIX message queues     (bytes, -q) 819200
real-time priority              (-r) 0
stack size              (kbytes, -s) 10240
cpu time               (seconds, -t) unlimited
max user processes              (-u) 3876
virtual memory          (kbytes, -v) unlimited
file locks                      (-x) unlimited

# 查看针对当前用户的最大文件打开数软限制
ulimit -Sn
1024

# 查看针对当前用户的最大文件打开数硬限制
ulimit -Hn
1024
```

**ulimit配置文件：limits.conf**

```
1. 修改/etc/security/limits.conf，增加或修改以下值
* soft nofile 32768
* hard nofile 65535

!!重点需要注意!!
后来发现编辑此文件并没有改变ulimit -a 中的open files值，原来是因为，
当我们用'*'入口来配置时，会被/etc/security/limits.d/90-nproc.conf中的配置所覆盖，
所以需要注意配置文件的覆盖顺序（前面有提及）


2. limits.conf实际是linux pam中的pam_limits.so的配置文件，针对于单个会话
编辑/etc/pam.d/login
session    required     /lib64/security/pam_limits.so
```

> **!!重点注意!!**
> `/etc/pam.d/login`中有`session    include      system-auth`这条记录，意味着`/etc/pam.d/system-auth`这个文件的记录都会包含到`/etc/pam.d/login`中。
> 在`/etc/pam.d/system-auth`中有配置`session    required     /lib64/security/pam_limits.so`

> PS: /etc/pam.d中文件的名称就是service，对应不同的application，例如login、sshd


**`limits.conf`的详细说明**
```
格式：<domain>        <type>  <item>  <value>

<domain> can be:
- a user name
- a group name, with @group syntax
- the wildcard *, for default entry
- the wildcard %, can be also used with %group syntax, for maxlogin limit

<type> can have the two values:
- "soft" for enforcing the soft limits - 取值范围是0-该用户资源上限，普通用户可配置
- "hard" for enforcing hard limits - 设定了该用户资源上限，只有管理员可配置
- "-" for both enforcing hard and soft limits

<item> can be one of the following:
- core - limits the core file size (KB)
- data - max data size (KB)
- fsize - maximum filesize (KB)
- memlock - max locked-in-memory address space (KB)
- nofile - max number of open file descriptors
- rss - max resident set size (KB)
- stack - max stack size (KB)
- cpu - max CPU time (MIN)
- nproc - max number of processes
- as - address space limit (KB)
- maxlogins - max number of logins for this user
- maxsyslogins - max number of logins on the system
- priority - the priority to run user process with
- locks - max number of file locks the user can hold
- sigpending - max number of pending signals
- msgqueue - max memory used by POSIX message queues (bytes)
- nice - max nice priority allowed to raise to values: [-20, 19]
- rtprio - max realtime priority
```

### 2. ulimit应用范围示例
#### 2.1 sysvinit script是否受ulimit中的配置限制

#### 2.2 关于ulimit，手动创建子shell(login shell 和 non-login shell)，是配置文件生效，还是继承的父进程的值？
``` bash
# ulimit配置文件
cat /etc/security/limits.conf | grep nofile
root soft nofile 65535 
root hard nofile 65535

# ulimit内存配置值
ulimit -Hn
2048

ulimit -Sn
2048

# 无论是login shell还是non-login shell，都是继承内存中的值
bash -l -c "shopt login_shell; cat /proc/$$/limits|grep files"
login_shell       on
Max open files            2048                 2048                 files     

bash -c "shopt login_shell; cat /proc/$$/limits|grep files"
login_shell       off
Max open files            2048                 2048                 files
```
> 在login shell和non-login shell中进行上述测试，结果一致

**原因分析**

并不是login shell都调用了PAM，未经过PAM调用的login shell也不会受到ulimit配置文件的影响，而是继承了父进程（当前bash进程）的limit值。

#### 2.3 关于ulimit，crontab中的任务，是配置文件生效，还是当前内存值生效
**首先，crontab中的任务的父进程是谁？**

``` bash
crontab -l
* * * * * sleep 50

# 查看crond的进程数
pstree -p 3849
crond(3849)---crond(7836)---sleep(7838)

# ulimit配置文件
cat /etc/security/limits.conf | grep nofile
root soft nofile 2048 
root hard nofile 65535

# ulimit内存配置值
ulimit -Hn
1025

ulimit -Sn
1025

# 查看进程的limit
cat /proc/3849/limits | grep files
Max open files            1024                 262144               files 

cat /proc/7838/limits|grep files
Max open files            2048                 65535                files     

cat /proc/7836/limits|grep files
Max open files            2048                 65535                files
```

从上面可以验证两个事情：
1. cron jobs是由crond fork出的子进程
2. cron jobs虽然是由crond fork出来，但是并未继承crond的limit值，而是继承了`/etc/security/limits.conf`中设定的值。

**其次，当ulimit配置文件中更新值后，cron job获取的limit设定会实时变动吗？**

``` bash
crontab -l
* * * * * sh -l -c "shopt login_shell >> /tmp/result-login; cat /proc/$$/limits | grep files >> /tmp/result-login"
* * * * * shopt login_shell >> /tmp/result-non-login; cat /proc/$$/limits | grep files >> /tmp/result-non-login

# 中间将ulimit配置文件'/etc/security/limits.conf'中的值从1025改为65535
cat /tmp/result-login
login_shell     on
Max open files            1025                 1025                 files     
login_shell     on
Max open files            65535                65535                files 

cat /tmp/result-non-login
login_shell     off
Max open files            1025                 1025                 files     
login_shell     off
Max open files            65535                65535                files 
```

对于cron job，如果`/etc/securit/limits.conf`中的值中途修改过，那么最新的cron job获取的是配置中的最新值。

**原因分析**

不是说只有经过PAM登录的login shell才会加载这个配置吗？为什么crontab中无论启动login shell还是non-login shell都会加载这个配置？原因是因为`/etc/security/limits.conf`其实本质上是PAM中pam_limit.so的配置文件，前面的介绍中提到这个配置文件都在说ulimit的配置文件，是因为前面的语境都是在shell环境中。ulimit是shell内置的一个limit配置管理工具，而跳出shell语境下后，只要某个进程的授权经过了PAM，并且在PAM中针对性的配置了对应这个application的pam_limits.so的require，那么它就和前面提到的经过PAM登录的login shell一样，会将`/etc/security/limits.conf`中的资源限制在子进程上生效。

果不其然，在/etc/pam.d中发现了crond这个配置，在下面是它的内容。

``` bash
cat /etc/pam.d/crond 
#
# The PAM configuration file for the cron daemon
#
#
# Although no PAM authentication is called, auth modules
# are used for credential setting
auth       include    password-auth
account    required   pam_access.so
account    include    password-auth
session    required   pam_loginuid.so
session    include    password-auth

cat /etc/pam.d/password-auth | grep pam_limits.so
session     required                                     pam_limits.so
```
> crond中session 部分 include了password-auth。而password-auth中包含了pam_limits.so。

这样我们前面的猜测就得到了验证，crond是通过调用PAM([crond 的man文档中有说明](https://man7.org/linux/man-pages/man8/cron.8.html))来应用了资源的限制。