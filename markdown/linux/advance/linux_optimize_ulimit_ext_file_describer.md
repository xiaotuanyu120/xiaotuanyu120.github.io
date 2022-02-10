---
title: linux: ulimit优化 - 扩展文件句柄vs文件描述符
date: 2019-03-28 13:27:00
categories: linux/advance
tags: [linux,ulimit,file handler,file describer]
---

### 0. 延伸背景
之前看了文件打开数的优化，讲到了ulimit和file-max的区别。后面发现`/proc/sys/fs/file-nr`这个文件的内容和`lsof|wc -l`相差巨大。于是就搜索了一波。

### 1. 原因
file-nr记录的是linux内核里面的文件打开数，而lsof列出的其实是各进程的文件描述符。

### 2. 文件打开 vs 文件描述符
- 文件打开，意味着打开一个目录、文件、块文件、执行文件、库文件、网络文件；  
- 文件描述符，是进程操作文件所使用的一个数据结构。

### 3. 文件打开数 vs 文件描述符数量
当前打开文件的数量与当前文件描述符/句柄的数量存在差异。 即使文件是打开的，它也可能没有与之关联的文件描述符，例如当前工作目录，内存映射文件和可执行文本文件。

[文件打开vs文件描述符](https://www.thegeekdiary.com/linux-interview-questions-open-files-open-file-descriptors/)
[文件描述符含义](https://stackoverflow.com/questions/25140730/what-does-the-fd-column-of-pipes-listed-by-lsof-mean)
[file-nr vs lsof](https://unix.stackexchange.com/questions/176967/why-file-nr-and-lsof-count-on-open-files-differs)