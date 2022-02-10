---
title: linux内核: 1.2.0 system load or cpu load
date: 2021-10-18 09:13:00
categories: linux/advance
tags: [linux,kernel]
---

### 1. linux中的`cpu load`还是`system load`？
一般情况下，稍微有经验的linux管理员都会熟练知道，查看系统负载，使用`top`、`uptime`或`w`命令都会输出load average的信息，分别是1、5、15分钟内的“cpu load”（并不是cpu load）信息。相信今天之前的我也会这样说，但是最近在重温系统负载相关知识的时候，竟然发现在一篇文章里面有如下表述:
```
On Linux, the system load includes threads both in Runnable (R) and in Uninterruptible sleep (D) states (typically disk I/O, but not always)
```
> 出处：[High System Load with Low CPU Utilization on Linux?](https://tanelpoder.com/posts/high-system-load-low-cpu-utilization-on-linux/)

大意是，linux的系统负载计算时，不仅包括处于可运行状态的进程，还包含了处于睡眠状态的“不可中断睡眠进程”。这个就太出乎我意料了，因为我一直以为这个`load average`是说的`cpu load`，如果事实真的是包含后者，那么这里就应该是`system load`（因为处于"D"状态的进程并不消耗cpu资源）了。

### 2. linux中`load average`确实包含了`Uninteruptible sleep process`吗？
先说结果，是的，和unix系统不同，linux系统上的`load average`是包含`Uninteruptible sleep process`的。

首先，在load的wiki上可以看到如下表述：
```
Most UNIX systems count only processes in the running (on CPU) or runnable (waiting for CPU) states. However, Linux also includes processes in uninterruptible sleep states (usually waiting for disk activity), which can lead to markedly different results if many processes remain blocked in I/O due to a busy or stalled I/O system.
```
明确的说明了unix和linux的不同，unix更符合我们的直觉，即为`cpu load`，而linux却是属实的`system load`。

### 3. 为什么linux要这样设计呢？
为了探寻linux这样设计的原因，我搜索到了一篇文章，果然并不是我一个人对这个感到好奇。
> 主要参考：[Linux Load Averages: Solving the Mystery](https://brendangregg.com/blog/2017-08-08/linux-load-averages.html)
> 作者：Brendan Gregg
> 下面的叙述主要参考了这篇文章中的内容。

首先，linux在最开始的版本中，和unix的行为保持一致，`load average`表示的是`cpu load`。后面在某个版本中修改为了包含`Uninteruptible sleep process`，也就是说linux中的`load average`表达的不仅仅是cpu的负载，还包含了I/O的负载（硬盘或NFS等）。

那么，为什么呢？

于是文章的作者开始搜索linux内核的提交历史记录，终于在远古时期的邮件列表中，他找到了1993年的一个更动
```
From: Matthias Urlichs <urlichs@smurf.sub.org>
Subject: Load average broken ?
Date: Fri, 29 Oct 1993 11:37:23 +0200


The kernel only counts "runnable" processes when computing the load average.
I don't like that; the problem is that processes which are swapping or
waiting on "fast", i.e. noninterruptible, I/O, also consume resources.

It seems somewhat nonintuitive that the load average goes down when you
replace your fast swap disk with a slow swap disk...

Anyway, the following patch seems to make the load average much more
consistent WRT the subjective speed of the system. And, most important, the
load is still zero when nobody is doing anything. ;-)

--- kernel/sched.c.orig Fri Oct 29 10:31:11 1993
+++ kernel/sched.c  Fri Oct 29 10:32:51 1993
@@ -414,7 +414,9 @@
    unsigned long nr = 0;

    for(p = &LAST_TASK; p > &FIRST_TASK; --p)
-       if (*p && (*p)->state == TASK_RUNNING)
+       if (*p && ((*p)->state == TASK_RUNNING) ||
+                  (*p)->state == TASK_UNINTERRUPTIBLE) ||
+                  (*p)->state == TASK_SWAPPING))
            nr += FIXED_1;
    return nr;
 }
--
Matthias Urlichs        \ XLink-POP N|rnberg   | EMail: urlichs@smurf.sub.org
Schleiermacherstra_e 12  \  Unix+Linux+Mac     | Phone: ...please use email.
90491 N|rnberg (Germany)  \   Consulting+Networking+Programming+etc'ing      42
```
提交这个更动的作者说，当用慢速的swap磁盘替换快速的swap磁盘时，负载竟然下降了，这样反映系统负载非常不直观。

中间关于这个问题，大方向没变，但是有关细节多次变动。

然后文章作者又探讨了如今（2017年）4.12版本的这个机制，而且Matthias在twitter回复了文章作者的邮件说：
```
"The point of "load average" is to arrive at a number relating how busy the system is from a human point of view. TASK_UNINTERRUPTIBLE means (meant?) that the process is waiting for something like a disk read which contributes to system load. A heavily disk-bound system might be extremely sluggish but only have a TASK_RUNNING average of 0.1, which doesn't help anybody."
```
大意就是Matthias认为1993年的那个更动的思路在现在（2017）依然是对的。

然后作者认为，`Uninteruptible sleep process`现在已经不仅仅是代表了disk的负载，它包含了更多的东西，我们是否需要找寻另外一种方法，仅仅让`load average`包含`cpu load`和`disk load`。调度器的维护人员Peter Zijstra回应了他，Peter Zijstra表示可以用` task_struct->in_iowait`（进程的iowait）来替代`Uninteruptible sleep process`，这样更接近反映`cpu load`和`disk load`的真实情况（只是讨论，并未改动）。

### 4. 总结
linux为了反映`cpu load`和`disk load`的真实情况，所以将`load average`的计算包含了`Runable`和`Uninteruptible sleep`两种状态的进程。所以，之后如果看到linux系统的负载高，对于那些高I/O消耗的服务，有了另外一个排查的思路。