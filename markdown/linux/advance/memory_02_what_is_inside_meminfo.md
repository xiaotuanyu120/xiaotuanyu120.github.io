---
title: /proc/meminfo里面有什么？
date: 2022-02-17 20:36:00
categories: linux/advance
tags: [linux, memory, /proc/meminfo]
---

### 0. 文章背景
想要做好linux的性能调优，光知道工具如何使用还不够，最重要的是要理解指标。很多内存工具（例如free）提供的指标都是从`/proc/meminfo`这里面获取的数据。

### 1. `/proc/meminfo`是什么？
它是`/proc/`目录中最常用的一个文件，因为它提供了大量的系统内存用量的有价值的信息。它提供了linux内核使用的空闲的和使用的内存（包含物理内存和交换分区）容量以及共享内存和缓冲区内存。

### 2. `/proc/meminfo`里面有什么？
- `MemTotal`，可用的内存的总量（计算：物理内存 - 保留bits - 内核二进制代码容量）。
- `MemFree`，（计算：`LowFree` + `HighFree`）。
- `MemAvailable` (since Linux 3.14)，用于启动新应用的可用内存的估计值，不包含交换分区。
- `Buffers`，原始磁盘块的临时存储（包括读写），不应该特别大（20MB左右）。
- `Cached`，磁盘中文件读写时在内存中的缓存，不包括`SwapCached`。
- `SwapCached`，交换出的内存交换回内存后，交换分区对应的交换文件依旧保留。在内存压力高时，不需要再次从内存中交换到交换分区，因为这些数据在交换分区文件中仍然存在，这减轻了I/O压力。
- `Active`，最近使用过的内存，除非特别需要，否则通常不会回收。
- `Inactive`，最近较少使用的内存，会优先被回收用于其他目的。
- `Active(anon)` (since Linux 2.6.28)
- `Inactive(anon)` (since Linux 2.6.28)
- `Active(file)` (since Linux 2.6.28)
- `Inactive(file)` (since Linux 2.6.28)
- `Unevictable` (since Linux 2.6.28)
- `Mlocked` (since Linux 2.6.28)
- `HighTotal` (Starting with Linux 2.6.19, CONFIG_HIGHMEM is required.)，高内存的总量。高内存是所有高于约860MB的物理内存。高内存是用于分配给用户空间程序或页缓存使用的。内核必须使用技巧来访问此内存，使其访问速度比低内存慢。
- `HighFree` (Starting with Linux 2.6.19, CONFIG_HIGHMEM is required.)，高内存的空闲容量。
- `LowTotal` (Starting with Linux 2.6.19, CONFIG_HIGHMEM is required.)，低内存的总量。低内存的用途包含所有高内存的用途，但它也可用于内核用于自己的数据结构。在许多其他事情中，`Slab`所有的内容都会在这里分配。当低内存耗尽时，会产生严重的后果。
- `LowFree` (Starting with Linux 2.6.19, CONFIG_HIGHMEM is required.)，低内存的空闲总量。
- `MmapCopy` (since Linux 2.6.29)
- `SwapTotal`，交换分区总量。
- `SwapFree`，未使用的交换分区总量。
- `Dirty`，等待写回到磁盘中的内存。
- `Writeback`，正在主动写回磁盘的内存。
- `AnonPages` (since Linux 2.6.18)，未关联文件并映射到用户空间页表的内存页。
- `Mapped`[，映射进内存（使用[`mmap`](https://man7.org/linux/man-pages/man2/mmap.2.html)）的文件占用的内存，例如库文件。
- `Shmem` (since Linux 2.6.32)，[`tmpfs`](https://man7.org/linux/man-pages/man5/tmpfs.5.html)文件系统占用的内存。
- `KReclaimable` (since Linux 4.20)，内核在内存压力下会尝试回收的分配给内核的内存。包含`SReclaimable`和其他带有shirinker的直接分配的内存。
- `Slab`，内核数据结构缓存。（见[slabinfo](https://man7.org/linux/man-pages/man5/slabinfo.5.html)）
- `SReclaimable` (since Linux 2.6.19)，`Slab`中的一部分，可能会被回收，例如缓存。
- `SUnreclaim` (since Linux 2.6.19)，`Slab`中的一部分，不会在内存压力下回收。
- `KernelStack` (since Linux 2.6.32)，分配给内核栈的内存。
- `PageTables` (since Linux 2.6.18)，专用于最低页表级别的内存。
- `Quicklists` (since Linux 2.6.27)
- `NFS_Unstable` (since Linux 2.6.18)，发给了服务器，但是尚未提交到稳定存储中的NFS页面。
- `Bounce` (since Linux 2.6.18)，用于块设备“反弹缓冲区”的内存。
- `WritebackTmp` (since Linux 2.6.26)，FUSE 用于临时回写缓冲区的内存。
- `CommitLimit` (since Linux 2.6.10)，当前系统可以分配的内存。仅当严格的overcommit accounting启用时（`/proc/sys/vm/overcommit_memory`为mode 2）此指标才有效。
- `Committed_AS`，系统上当前分配的内存总量。是分配给所有进程的内存量的总和，即使仅仅是分配给进程却并未被使用的。举例，一个进程分配了1G内存，使用了其中300M，这1G内存是这个进程随时可使用的内存。严格过度使用模式下(/proc/sys/vm/overcommit_memory中的mode 2)，超过CommitLimit的分配不会被准许。这有利于保证进程不会因为内存已分配，却因为内存不足的情况导致的错误。
- `VmallocTotal`，vmalloc内存区域的总量。
- `VmallocUsed`，vmalloc内存区域的使用量。从Linux4.4之后，这个值不再被计算，硬编码为0（详情见/proc/vmallocinfo）
- `VmallocChunk`，vmalloc区域的最大连续空闲连续块。从Linux4.4之后，这个值不再被计算，硬编码为0（详情见/proc/vmallocinfo）
- `HardwareCorrupted` (since Linux 2.6.32)(CONFIG_MEMORY_FAILURE is required.)
- `LazyFree` (since Linux 4.12)，显示[madvise(2)](https://man7.org/linux/man-pages/man2/madvise.2.html)标记的内存量。
- `AnonHugePages` (since Linux 2.6.38)(CONFIG_TRANSPARENT_HUGEPAGE is required.)，无文件映射的映射到用户空间页表的大页。
- `ShmemHugePages` (since Linux 4.8)(CONFIG_TRANSPARENT_HUGEPAGE is required.)，共享内存(shmem)和[tmpfs(5)](https://man7.org/linux/man-pages/man5/tmpfs.5.html)使用的分配大页的内存。
- `ShmemPmdMapped` (since Linux 4.8)(CONFIG_TRANSPARENT_HUGEPAGE is required.)，映射到有大页的用户空间的共享内存。
- `CmaTotal` (since Linux 3.1)(CONFIG_CMA is required.)，CMA(Contiguous Memory Allocator)页面总量。
- `CmaFree` (CONFIG_CMA is required.)，CMA(Contiguous Memory Allocator)页面空闲量。
- `HugePages_Total` (CONFIG_HUGETLB_PAGE is required.)，大页面池的总量。
- `HugePages_Free` (CONFIG_HUGETLB_PAGE is required.)，大页面池中未被分配的大页量。
- `HugePages_Rsvd` (since Linux 2.6.17)(CONFIG_HUGETLB_PAGE is required.)，指从大页面池中承诺分配的，但并未实际分配的大页量。这些预留的大页量保证了一个应用可以在故障时间从大页面池中分配到大页。
- `HugePages_Surp` (since Linux 2.6.24)(CONFIG_HUGETLB_PAGE is required.)，这是大页面池中高于`/proc/sys/vm/nr_hugepages`的大页数量。其最大值被`/proc/sys/vm/nr_overcommit_hugepages`所设定。
- `HugePagesize` (CONFIG_HUGETLB_PAGE is required.) ，大页的size。32位架构，单处理器的默认值是4096KB。SMP巨量内存内核和AMD64，默认值是2048KB。Itanium架构，默认值是262144KB。此统计信息仅出现在 x86、Itanium 和 AMD64 架构上。
- `DirectMap4k` (since Linux 2.6.27)，内核中线性映射的4KB页的字节数量。
- `DirectMap4M` (since Linux 2.6.27)，内核中线性映射的4MB页的字节数量。(x86 with CONFIG_X86_64 or CONFIG_X86_PAE enabled.)
- `DirectMap2M` (since Linux 2.6.27)，内核中线性映射的2MB页的字节数量。(x86 with CONFIG_X86_64 or CONFIG_X86_PAE enabled.)
- `DirectMap1G` (since Linux 2.6.27)，(x86 with CONFIG_X86_64 or CONFIG_X86_PAE enabled.)