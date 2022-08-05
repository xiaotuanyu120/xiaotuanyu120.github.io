---
title: 内存: 进程内存布局 - 堆栈
date: 2022-08-01 20:28:00
categories: linux/advance
tags: [linux, memory]
---

### 0. 进程的常见内存布局(c/c++)
进程是操作系统分配内存资源的最小单位，每个进程都有自己独立的内存布局（虚拟内存）。包含：
- stack: 保存function和local var
- memory mapping: 保存大块的从文件映射的内存空间，用于加载代码库文件、共享内存等
- heap: 程序动态使用的内存
- data: 全局变量，分为初始化的(data segment，实际分配内存)和非初始化的(bss segment，实际未分配内存)
- text: 保存运行的code

> memory mapping的内存会统计在top命令的SHR字段，所以，这个字段统计的内存并不全是共享内存，也包含其他被映射的文件，例如代码库文件

linux内核给每个进程一个独立的虚拟内存地址。这个虚拟内存的地址是连续的，虚拟内存又分为“用户空间”和“内核空间”。当进程在用户态的时候，只能访问“用户空间”，相反地，只有进程在内核态的时候，才能访问“内核空间”。虽然每个进程的内存空间都包含了“内核空间”，但其实它们是同一段物理内存，这样进程在进入内核态时，都能方便的访问内核态空间内存。

关于“用户空间”，它的结构，一般是从低地址开始依次为text、data、heap、memory mapping。然后stack是从高地址往下分配。
![](/static/images/docs/linux/advance/memory_layout.png)

> 通常情况下，频繁被执行的程序，其text一般是共享并且是只读的。例如gcc、shell、text editor等

> [stack and heap](https://courses.engr.illinois.edu/cs225/sp2022/resources/stack-heap/)


### 1. heap和stack的区别
- stack由编译器管理，而heap由程序员自己控制，使用方便，但是有泄漏风险。
- stack是由虚拟内存地址的高地址向下分配；而heap是由低地址向上分配。
- stack的容量由系统预先定义，一般比较小；而heap则是受限于操作系统中有效的虚拟内存，一般比较大。
- stack不会产生内存碎片，而heap会产生比较多的碎片。