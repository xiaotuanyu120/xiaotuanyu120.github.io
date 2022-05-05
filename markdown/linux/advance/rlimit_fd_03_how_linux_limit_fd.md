---
title: rlimit fd: linux中如何管理fd
date: 2022-04-30 21:05:00
categories: linux/advance
tags: [fd, rlimit]
---

## 0. 总览
上一篇[文件描述符简明介绍](/linux/advance/rlimit_fd_01_file_descriptor_brief_introduction.html)中有介绍fd是什么，那么linux中是如何管理它的呢？

根据上篇文章，我们可知，fd的实际使用是绑定到每个进程上的。

因为linux上创建进程，其实是通过拷贝的方式来实现的，区别只是在于PID、PPID、某些资源和统计量（例如挂起的信号量），大部分的task_struct(fd表所在的数据结构)中的数据没有变化，相当于是直接继承了，**所以fd的限制理论上，是直接继承的父进程的fd的限制**。

但是也会有其他的管理工具或者方法可以让子进程改变继承的fd限制。总结来讲有以下几种方式：

1. login-shell通过ulimit来设定登录用户或登录用户组的fd限制（或non-login-shell通过在启动脚本中显式调用ulimit命令）
2. container通过container management来设定fd限制
3. systemd管理的service通过systemd的配置来设定fd限制
4. 程序本身调用系统调用来修改fd限制

除了默认的从父进程继承的形式之外，其他所有改变fd限制的方式底层都是通过相关的几个系统调用（后面细讲）来实现的。
> 只有root才可以调高hard limit，其他的用户只可以调整soft limit（不可以超过hard limit）

```
┌────────────┐ ┌────────┐ ┌─────┐     ┌────┐ ┌─────┐ ┌─────┐     ┌─────────┐
│init/systemd│ │services│ │shell│     │sshd│ │crond│ │login│     │container│
└────────┬───┘ └────┬───┘ └───┬─┘     └──┬─┘ └──┬──┘ └───┬─┘     └────┬────┘
         │          │    (opti│onal)     └──────┴────────┤            │ 
         │          │         └─────────────┐            │            │
         │          │                       │           PAM           │
         │          ├─sysvinit scripts──────┤            │            │
         │          │   (optional)          │            │            │
         │          │                       │            │            │
         │          ├─systemd units─┐       │            │            │
         │          │               │       │            │            │
         │       ┌──▼───┐   ┌───────▼─┐ ┌───▼──┐ ┌───────▼──────┐ ┌───▼────────┐
         │       │ hard │   │ systemd │ │ulimit│ │ limits.conf  │ │ container  │
         └──────►│ code │   │         │ │(cmd) │ │ pam_limit.so │ │ management │
                 └──┬───┘   └────┬────┘ └───┬──┘ └───────┬──────┘ └──────┬─────┘
                    │            │          │            │               │
                    └────────────┴──────────┴───┬────────┴───────────────┘
                                          SYSTEM│CALL
            DEFAULT                             │
   ┌─────────────────────────┬──────────────────▼──────┐
   │                         │                         │
   │     inherit from        │    getrlimit prlimit    │
   │     parent process      │    setrlimit rlimit     │
   │                         │                         │
   ├─────────────────────────┴─────────────────────────┤
   │                                                   │
   │                      KERNEL                       │
   │                                                   │
   └───────────────────────────────────────────────────┘
```


## 1. 资源限制(rlimit)的系统调用：getrlimit, setrlimit, prlimit
- 和资源限制（包含fd）系统调用相关的数据结构：`rlimit`（resource limit）

- 和资源限制（包含fd）相关的系统调用

``` c
// 获取rlimit
int getrlimit(int resource, struct rlimit *rlim);

// 设定rlimit
int setrlimit(int resource, const struct rlimit *rlim);

// 设定其他进程的rlimit
int prlimit(pid_t pid, int resource, const struct rlimit *new_limit,
                   struct rlimit *old_limit);
```


## 2. 子进程继承父进程的fd限制
### 2.1 简单fork进程，继承测试和hard code硬编程fd限制测试
准备一个简单的测试c程序`limit.c`，为排除ulimit的影响，修改父进程的rlimit值为和ulimit不同的值，看子进程是否继承

``` c
#include <stdio.h>
#include <unistd.h>
#include <sys/resource.h>
#include <errno.h>
#include<sys/wait.h>

int main() {
    pid_t c_pid;
    struct rlimit p_rlim, c_rlim;

    if (fork()==0)
        printf("fork done\n");
    else
        c_pid = wait(NULL);

    if (c_pid != 0) {
        // change parent pid's rlimit
        p_rlim.rlim_cur = 512;
        p_rlim.rlim_max = 512;
        if(setrlimit(RLIMIT_NOFILE, &p_rlim) == -1)
            fprintf(stderr, "%s\n", strerror(errno));

        if( getrlimit(RLIMIT_NOFILE, &p_rlim) == 0) {
            printf("Parent limits -> soft limit= %ld \t hard limit= %ld \n",
                p_rlim.rlim_cur, 
                p_rlim.rlim_max);
            printf("Parent pid = %d\n", getpid());
        } else {
            fprintf(stderr, "%s\n", strerror(errno));
        }
    } else {
        if( getrlimit(RLIMIT_NOFILE, &c_rlim) == 0) {
            printf("Child limits -> soft limit= %ld \t hard limit= %ld \n",
                c_rlim.rlim_cur, 
                c_rlim.rlim_max);
            printf("Child pid = %d\n", getpid());
        } else {
            fprintf(stderr, "%s\n", strerror(errno));
        }
    }

    return 0;
}
```

``` bash
# 为排除ulimit的影响，我们先设定ulimit的限制为和父进程的rlimit不同的值
ulimit -n 1024

# compile测试程序并运行
gcc limit.c -o limit

./limit
fork done
Child limits -> soft limit= 1024    hard limit= 1024 
Child pid = 246
Parent limits -> soft limit= 512    hard limit= 512 
Parent pid = 245
```
可以看出，limit（子）的fd限制继承自limit（父），然后limit（父）可以通过hard code把fd限制手动修改

> **注意：**程序设定的值不可以超过父进程bash的值，也就是ulimit命令设定的hard limit的值，否则会有如下报错
``` bash
strace ./limit

......

setrlimit(RLIMIT_NOFILE, {rlim_cur=1025, rlim_max=1025}) = -1 EPERM (Operation not permitted)
--- SIGSEGV {si_signo=SIGSEGV, si_code=SEGV_MAPERR, si_addr=0x80cde390} ---
+++ killed by SIGSEGV +++
Segmentation fault
```

## 3. 通过其他管理工具或者系统调用来修改fd限制
### 3.1 ulimit
详细内容见：[ulimit工具简明介绍：2.3](/linux/advance/rlimit_ulimit_01_introduce.html)
- sysvinit script是否受ulimit中的配置限制；答案：（未验证，猜测是否）
- 手动创建子shell(login shell 和 non-login shell)，是配置文件生效，还是继承的父进程的值？答案：继承父进程的值
- crontab中的任务是否受ulimit中的配置限制；答案：收到`/etc/security/limits.conf`中的配置限制，前提是在pam中针对crond配置了pam_limits.so模块的对应配置

### 3.2 systemd
详细内容见：[systemd 系统资源限制](/linux/advance/systemd_00_00_rlimit_settings.html)

### 3.3 container management
#### 3.3.1 docker
#### 3.3.2 podman
详细配置见[podman config: 系统资源限制](/virtualization/container/podman_config_00_rlimit.html)