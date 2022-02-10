---
title: linux: 系统资源限制 - 文件打开数 - ulimit、systemd
date: 2016-08-23 03:04:00
categories: linux/advance
tags: [linux,ulimit,fs-max,systemd]
---

### 0. linux系统资源限制简介
linux系统中对系统资源的限制使用[setrlimit](#setrlimit)这个系统调用，基于这个系统调用，常见的管理工具有ulimit和systemd（应用于不同场景）。

### 1. 文件打开数信息查看
``` bash
# 查看linux内核级别的文件描述符上限
cat /proc/sys/fs/file-max
97984

# 查看目前系统使用的文件描述符数量
cat /proc/sys/fs/file-nr
512 0 97984
# 512   -> 分配并使用的文件描述符数量
# 0     -> 分配却未使用的文件描述符数量
# 97984 -> 内核级别的最大文件描述符数量
```
> **file-max vs ulimit**  
`file-max`是linux内核级别的设定，影响的是linux内核最高可以打开的文件数限制；  
`ulimit`是进程级别的设定，影响的是指定用户启动进程最高可以打开的文件数限制；

> 参考文档:  
[ulimit设定的是每个进程的属性，而不是该用户所有进程的总限制](https://unix.stackexchange.com/questions/55319/are-limits-conf-values-applied-on-a-per-process-basis)  
[ulimit vs file-max](https://unix.stackexchange.com/questions/447583/ulimit-vs-file-max)  
[如何计算最大文件打开数应该设定多少](https://stackoverflow.com/questions/6180569/need-to-calculate-optimum-ulimit-and-fs-file-max-values-according-to-my-own-se)

### 1. ulimit工具使用说明
针对的是使用pam登录的用户的资源限制，老的init方式启动的进程也会被这个限制。/etc/security/limits.conf是pam_limits这个模块的配置文件，修改此配置文件之后，用户需要重新登录才会生效。

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

# 查看针对当前用户的软限制
ulimit -Sn
1024

# 查看针对当前用户的硬限制
ulimit -Hn
1024
```
其中open files对应的配置数目是最大打开文件数目，默认是1024，生产环境下，这个参数会影响到某些程序的并发数量，例如mysql。

**ulimit配置文件：limits.conf**
``` bash
# 修改/etc/security/limits.conf
********************
* soft nofile 32768
* hard nofile 65535
********************
## 重点需要注意 ##
# 后来发现编辑此文件并没有改变ulimit -a 中的open files值，原来是因为，当我们用'*'入口来配置时，会被/etc/security/limits.d/90-nproc.conf中的配置所覆盖，此时只需要去更改此默认值就可以了


# limits.conf实际是linux pam中的pam_limits.so的配置文件，针对于单个会话
# 编辑/etc/pam.d/login
********************
session    required     /lib64/security/pam_limits.so
********************
```

> limits.conf的详细说明
> - 格式：`<domain>        <type>  <item>  <value>`
>   - <domain> can be:
>     - a user name
>     - a group name, with @group syntax
>     - the wildcard *, for default entry
>     - the wildcard %, can be also used with %group syntax, for maxlogin limit
>   - <type> can have the two values:
>     - "soft" for enforcing the soft limits - 取值范围是0-该用户资源上限，普通用户可配置
>     - "hard" for enforcing hard limits - 设定了该用户资源上限，只有管理员可配置
>     - "-" for both enforcing hard and soft limits
>   - <item> can be one of the following:
>     - core - limits the core file size (KB)
>     - data - max data size (KB)
>     - fsize - maximum filesize (KB)
>     - memlock - max locked-in-memory address space (KB)
>     - nofile - max number of open file descriptors
>     - rss - max resident set size (KB)
>     - stack - max stack size (KB)
>     - cpu - max CPU time (MIN)
>     - nproc - max number of processes
>     - as - address space limit (KB)
>     - maxlogins - max number of logins for this user
>     - maxsyslogins - max number of logins on the system
>     - priority - the priority to run user process with
>     - locks - max number of file locks the user can hold
>     - sigpending - max number of pending signals
>     - msgqueue - max memory used by POSIX message queues (bytes)
>     - nice - max nice priority allowed to raise to values: [-20, 19]
>     - rtprio - max realtime priority

### 2. systemd
systemd默认会有一个资源分配值，例如文件打开数的默认值是4096。可以通过修改systemd默认资源分配值或者单个unit文件配置资源分配值这两种方式来修改systemd启动的service的资源限制数值。
- `/etc/systemd/system.conf`：系统进程的默认限制
- `/etc/systemd/user.conf`：用户进程的默认限制

#### 1) 修改systemd默认资源分配值
**systemd默认资源限制配置文件：`/etc/systemd/system.conf`**
```
#DefaultLimitCPU=
#DefaultLimitFSIZE=
#DefaultLimitDATA=
#DefaultLimitSTACK=
#DefaultLimitCORE=
#DefaultLimitRSS=
#DefaultLimitNOFILE=
#DefaultLimitAS=
#DefaultLimitNPROC=
#DefaultLimitMEMLOCK=
#DefaultLimitLOCKS=
#DefaultLimitSIGPENDING=
#DefaultLimitMSGQUEUE=
#DefaultLimitNICE=
#DefaultLimitRTPRIO=
#DefaultLimitRTTIME=
```

**system.conf重新加载命令**
``` bash
systemctl daemon-reexec
```

#### 2) 修改systemd unit文件资源分配值
配置以下项目到unit文件的service配置块中

| Directive        | ulimit equivalent | Unit                       |
| ---------------- | ----------------- | -------------------------- |
| LimitCPU=        | ulimit -t         | Seconds                    |
| LimitFSIZE=      | ulimit -f         | Bytes                      |
| LimitDATA=       | ulimit -d         | Bytes                      |
| LimitSTACK=      | ulimit -s         | Bytes                      |
| LimitCORE=       | ulimit -c         | Bytes                      |
| LimitRSS=        | ulimit -m         | Bytes                      |
| LimitNOFILE=     | ulimit -n         | Number of File Descriptors |
| LimitAS=         | ulimit -v         | Bytes                      |
| LimitNPROC=      | ulimit -u         | Number of Processes        |
| LimitMEMLOCK=    | ulimit -l         | Bytes                      |
| LimitLOCKS=      | ulimit -x         | Number of Locks            |
| LimitSIGPENDING= | ulimit -i         | Number of Queued Signals   |
| LimitMSGQUEUE=   | ulimit -q         | Bytes                      |
| LimitNICE=       | ulimit -e         | Nice Level                 |
| LimitRTPRIO=     | ulimit -r         | Realtime Priority          |
| LimitRTTIME=     | No equivalent     | Microseconds               |

> [manual for systemd.exec](https://www.freedesktop.org/software/systemd/man/systemd.exec.html#Process%20Properties)

### 3. podman（cgroup manager: systemd）
使用podman的rootless模式启动容器时，配置文件是`~/.config/containers/containers.conf`
```
[containers]
default_ulimits = [
 "nproc=65535:65535",
 "nofile=65535:65535",
]
``` 
> 这里设定的值，不可以高于运行容器普通用户的自身资源限定值

## 附录
### setrlimit
```
Name
getrlimit, setrlimit, prlimit - get/set resource limits

Synopsis
#include <sys/time.h>
#include <sys/resource.h>

int getrlimit(int resource, struct rlimit *rlim);
int setrlimit(int resource, const struct rlimit *rlim);

int prlimit(pid_t pid, int resource, const struct rlimit *new_limit,
struct rlimit *old_limit);

Feature Test Macro Requirements for glibc (see feature_test_macros(7)):

prlimit(): _GNU_SOURCE && _FILE_OFFSET_BITS == 64
Description
The getrlimit() and setrlimit() system calls get and set resource limits respectively. Each resource has an associated soft and hard limit, as defined by the rlimit structure:

struct rlimit {
    rlim_t rlim_cur;  /* Soft limit */
    rlim_t rlim_max;  /* Hard limit (ceiling for rlim_cur) */
};
The soft limit is the value that the kernel enforces for the corresponding resource. The hard limit acts as a ceiling for the soft limit: an unprivileged process may only set its soft limit to a value in the range from 0 up to the hard limit, and (irreversibly) lower its hard limit. A privileged process (under Linux: one with the CAP_SYS_RESOURCE capability) may make arbitrary changes to either limit value.
The value RLIM_INFINITY denotes no limit on a resource (both in the structure returned by getrlimit() and in the structure passed to setrlimit()).

The resource argument must be one of:

RLIMIT_AS
The maximum size of the process's virtual memory (address space) in bytes. This limit affects calls to brk(2), mmap(2) and mremap(2), which fail with the error ENOMEM upon exceeding this limit. Also automatic stack expansion will fail (and generate a SIGSEGV that kills the process if no alternate stack has been made available via sigaltstack(2)). Since the value is a long, on machines with a 32-bit long either this limit is at most 2 GiB, or this resource is unlimited.
RLIMIT_CORE
Maximum size of core file. When 0 no core dump files are created. When nonzero, larger dumps are truncated to this size.
RLIMIT_CPU
CPU time limit in seconds. When the process reaches the soft limit, it is sent a SIGXCPU signal. The default action for this signal is to terminate the process. However, the signal can be caught, and the handler can return control to the main program. If the process continues to consume CPU time, it will be sent SIGXCPU once per second until the hard limit is reached, at which time it is sent SIGKILL. (This latter point describes Linux behavior. Implementations vary in how they treat processes which continue to consume CPU time after reaching the soft limit. Portable applications that need to catch this signal should perform an orderly termination upon first receipt of SIGXCPU.)
RLIMIT_DATA
The maximum size of the process's data segment (initialized data, uninitialized data, and heap). This limit affects calls to brk(2) and sbrk(2), which fail with the error ENOMEM upon encountering the soft limit of this resource.
RLIMIT_FSIZE
The maximum size of files that the process may create. Attempts to extend a file beyond this limit result in delivery of a SIGXFSZ signal. By default, this signal terminates a process, but a process can catch this signal instead, in which case the relevant system call (e.g., write(2), truncate(2)) fails with the error EFBIG.
RLIMIT_LOCKS (Early Linux 2.4 only)
A limit on the combined number of flock(2) locks and fcntl(2) leases that this process may establish.
RLIMIT_MEMLOCK
The maximum number of bytes of memory that may be locked into RAM. In effect this limit is rounded down to the nearest multiple of the system page size. This limit affects mlock(2) and mlockall(2) and the mmap(2) MAP_LOCKED operation. Since Linux 2.6.9 it also affects the shmctl(2) SHM_LOCK operation, where it sets a maximum on the total bytes in shared memory segments (see shmget(2)) that may be locked by the real user ID of the calling process. The shmctl(2) SHM_LOCK locks are accounted for separately from the per-process memory locks established by mlock(2), mlockall(2), and mmap(2) MAP_LOCKED; a process can lock bytes up to this limit in each of these two categories. In Linux kernels before 2.6.9, this limit controlled the amount of memory that could be locked by a privileged process. Since Linux 2.6.9, no limits are placed on the amount of memory that a privileged process may lock, and this limit instead governs the amount of memory that an unprivileged process may lock.
RLIMIT_MSGQUEUE (Since Linux 2.6.8)
Specifies the limit on the number of bytes that can be allocated for POSIX message queues for the real user ID of the calling process. This limit is enforced for mq_open(3). Each message queue that the user creates counts (until it is removed) against this limit according to the formula:
bytes = attr.mq_maxmsg * sizeof(struct msg_msg *) +
        attr.mq_maxmsg * attr.mq_msgsize
where attr is the mq_attr structure specified as the fourth argument to mq_open(3).
The first addend in the formula, which includes sizeof(struct msg_msg *) (4 bytes on Linux/i386), ensures that the user cannot create an unlimited number of zero-length messages (such messages nevertheless each consume some system memory for bookkeeping overhead).

RLIMIT_NICE (since Linux 2.6.12, but see BUGS below)
Specifies a ceiling to which the process's nice value can be raised using setpriority(2) or nice(2). The actual ceiling for the nice value is calculated as 20 - rlim_cur. (This strangeness occurs because negative numbers cannot be specified as resource limit values, since they typically have special meanings. For example, RLIM_INFINITY typically is the same as -1.)
RLIMIT_NOFILE
Specifies a value one greater than the maximum file descriptor number that can be opened by this process. Attempts (open(2), pipe(2), dup(2), etc.) to exceed this limit yield the error EMFILE. (Historically, this limit was named RLIMIT_OFILE on BSD.)
RLIMIT_NPROC
The maximum number of processes (or, more precisely on Linux, threads) that can be created for the real user ID of the calling process. Upon encountering this limit, fork(2) fails with the error EAGAIN.
RLIMIT_RSS
Specifies the limit (in pages) of the process's resident set (the number of virtual pages resident in RAM). This limit only has effect in Linux 2.4.x, x < 30, and there only affects calls to madvise(2) specifying MADV_WILLNEED.
RLIMIT_RTPRIO (Since Linux 2.6.12, but see BUGS)
Specifies a ceiling on the real-time priority that may be set for this process using sched_setscheduler(2) and sched_setparam(2).
RLIMIT_RTTIME (Since Linux 2.6.25)
Specifies a limit (in microseconds) on the amount of CPU time that a process scheduled under a real-time scheduling policy may consume without making a blocking system call. For the purpose of this limit, each time a process makes a blocking system call, the count of its consumed CPU time is reset to zero. The CPU time count is not reset if the process continues trying to use the CPU but is preempted, its time slice expires, or it calls sched_yield(2).
Upon reaching the soft limit, the process is sent a SIGXCPU signal. If the process catches or ignores this signal and continues consuming CPU time, then SIGXCPU will be generated once each second until the hard limit is reached, at which point the process is sent a SIGKILL signal.

The intended use of this limit is to stop a runaway real-time process from locking up the system.

RLIMIT_SIGPENDING (Since Linux 2.6.8)
Specifies the limit on the number of signals that may be queued for the real user ID of the calling process. Both standard and real-time signals are counted for the purpose of checking this limit. However, the limit is only enforced for sigqueue(3); it is always possible to use kill(2) to queue one instance of any of the signals that are not already queued to the process.
RLIMIT_STACK
The maximum size of the process stack, in bytes. Upon reaching this limit, a SIGSEGV signal is generated. To handle this signal, a process must employ an alternate signal stack (sigaltstack(2)).
Since Linux 2.6.23, this limit also determines the amount of space used for the process's command-line arguments and environment variables; for details, see execve(2).

prlimit()

The Linux-specific prlimit() system call combines and extends the functionality of setrlimit() and getrlimit(). It can be used to both set and get the resource limits of an arbitrary process.
The resource argument has the same meaning as for setrlimit() and getrlimit().

If the new_limit argument is a not NULL, then the rlimit structure to which it points is used to set new values for the soft and hard limits for resource. If the old_limit argument is a not NULL, then a successful call to prlimit() places the previous soft and hard limits for resource in the rlimit structure pointed to by old_limit.

The pid argument specifies the ID of the process on which the call is to operate. If pid is 0, then the call applies to the calling process. To set or get the resources of a process other than itself, the caller must have the CAP_SYS_RESOURCE capability, or the real, effective, and saved set user IDs of the target process must match the real user ID of the caller and the real, effective, and saved set group IDs of the target process must match the real group ID of the caller.

Return Value
On success, these system calls return 0. On error, -1 is returned, and errno is set appropriately.

Errors
EFAULT
A pointer argument points to a location outside the accessible address space.

EINVAL

The value specified in resource is not valid; or, for setrlimit() or prlimit(): rlim->rlim_cur was greater than rlim->rlim_max.

EPERM

An unprivileged process tried to raise the hard limit; the CAP_SYS_RESOURCE capability is required to do this. Or, the caller tried to increase the hard RLIMIT_NOFILE limit above the current kernel maximum (NR_OPEN). Or, the calling process did not have permission to set limits for the process specified by pid.

ESRCH

Could not find a process with the ID specified in pid.

Versions
The prlimit() system call is available since Linux 2.6.36. Library support is available since glibc 2.13.

Conforming To
getrlimit(), setrlimit(): SVr4, 4.3BSD, POSIX.1-2001.
prlimit(): Linux-specific.

RLIMIT_MEMLOCK and RLIMIT_NPROC derive from BSD and are not specified in POSIX.1-2001; they are present on the BSDs and Linux, but on few other implementations. RLIMIT_RSS derives from BSD and is not specified in POSIX.1-2001; it is nevertheless present on most implementations. RLIMIT_MSGQUEUE, RLIMIT_NICE, RLIMIT_RTPRIO, RLIMIT_RTTIME, and RLIMIT_SIGPENDING are Linux-specific.

Notes
A child process created via fork(2) inherits its parent's resource limits. Resource limits are preserved across execve(2).

One can set the resource limits of the shell using the built-in ulimit command (limit in csh(1)). The shell's resource limits are inherited by the processes that it creates to execute commands.

Since Linux 2.6.24, the resource limits of any process can be inspected via /proc/[pid]/limits; see proc(5).

Ancient systems provided a vlimit() function with a similar purpose to setrlimit(). For backward compatibility, glibc also provides vlimit(). All new applications should be written using setrlimit().

Bugs
In older Linux kernels, the SIGXCPU and SIGKILL signals delivered when a process encountered the soft and hard RLIMIT_CPU limits were delivered one (CPU) second later than they should have been. This was fixed in kernel 2.6.8.

In 2.6.x kernels before 2.6.17, a RLIMIT_CPU limit of 0 is wrongly treated as "no limit" (like RLIM_INFINITY). Since Linux 2.6.17, setting a limit of 0 does have an effect, but is actually treated as a limit of 1 second.

A kernel bug means that RLIMIT_RTPRIO does not work in kernel 2.6.12; the problem is fixed in kernel 2.6.13.

In kernel 2.6.12, there was an off-by-one mismatch between the priority ranges returned by getpriority(2) and RLIMIT_NICE. This had the effect that the actual ceiling for the nice value was calculated as 19 - rlim_cur. This was fixed in kernel 2.6.13.

Since Linux 2.6.12, if a process reaches its soft RLIMIT_CPU limit and has a handler installed for SIGXCPU, then, in addition to invoking the signal handler, the kernel increases the soft limit by one second. This behavior repeats if the process continues to consume CPU time, until the hard limit is reached, at which point the process is killed. Other implementations do not change the RLIMIT_CPU soft limit in this manner, and the Linux behavior is probably not standards conformant; portable applications should avoid relying on this Linux-specific behavior. The Linux-specific RLIMIT_RTTIME limit exhibits the same behavior when the soft limit is encountered.

Kernels before 2.4.22 did not diagnose the error EINVAL for setrlimit() when rlim->rlim_cur was greater than rlim->rlim_max.

Example
The program below demonstrates the use of prlimit().

#define _GNU_SOURCE
#define _FILE_OFFSET_BITS 64
#include <stdio.h>
#include <time.h>
#include <stdlib.h>
#include <unistd.h>
#include <sys/resource.h>
#define errExit(msg)
do { perror(msg); exit(EXIT_FAILURE); \

} while (0)
int
main(int argc, char *argv[])
{
struct rlimit old, new;
struct rlimit *newp;
pid_t pid;

if (!(argc == 2 || argc == 4)) {
fprintf(stderr, "Usage: %s <pid> [<new-soft-limit> "
"<new-hard-limit>]\n", argv[0]);
exit(EXIT_FAILURE);
}

pid = atoi(argv[1]); /* PID of target process */

newp = NULL;
if (argc == 4) {
new.rlim_cur = atoi(argv[2]);
new.rlim_max = atoi(argv[3]);
newp = &new;
}

/* Set CPU time limit of target process; retrieve and display
previous limit */

if (prlimit(pid, RLIMIT_CPU, newp, &old) == -1)
errExit("prlimit-1");
printf("Previous limits: soft=%lld; hard=%lld\n",
(long long) old.rlim_cur, (long long) old.rlim_max);

/* Retrieve and display new CPU time limit */

if (prlimit(pid, RLIMIT_CPU, NULL, &old) == -1)
errExit("prlimit-2");
printf("New limits: soft=%lld; hard=%lld\n",
(long long) old.rlim_cur, (long long) old.rlim_max);

exit(EXIT_FAILURE);
}
```