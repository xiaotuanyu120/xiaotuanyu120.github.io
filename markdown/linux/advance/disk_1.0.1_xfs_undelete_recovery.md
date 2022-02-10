---
title: disk: 1.0.1 xfs 硬盘数据恢复
date: 2021-02-23 15:54:00
categories: linux/advance
tags: [xfs]
---

### 0. 背景
能搜到这个文章的人，懂得都懂。误删了线上文件，只能想办法恢复了

### 1. 解决过程
- 停掉误删文件相关的服务
- 卸载误删文件磁盘
- 尝试不能用的工具
  - extundelete, 文件恢复工具。不能用的原因，centos7默认的磁盘格式是xfs，而这个工具只能恢复ext3和ext4
  - testdisk, 磁盘工具，主要是分区的功能，不能用的原因，文件恢复的功能只支持FAT,NTFS及ext2/ext3/ext4

### 2. xfs官方网站怎么说？
[xfs.org: ](https://xfs.org/index.php/XFS_FAQ#Q:_Does_the_filesystem_have_an_undelete_capability.3F)

There is no undelete in XFS.
However, if an inode is unlinked but neither it nor its associated data blocks get immediately re-used and overwritten, there is some small chance to recover the file from the disk.
photorec, xfs_irecover or xfsr are some tools which attempt to do this, with varying success.
There are also commercial data recovery services and closed source software like Raise Data Recovery for XFS which claims to recover data, although this has not been tested by the XFS developers.
As always, the best advice is to keep good backups.

大意就是，删除的文件有很小的机会来找回，工具就是photorec、xfs_irecover和xfsr。

但是我研究了半天，没发现这些工具如何安装。

### 3. 解决过程
根据上面的一顿搜索，我目前的选择无非是
- 继续找开源工具来尝试恢复
- 找商业支持

因为是公司的数据，所以直接找商业支持了，比较快速，在这方面我咨询了一些同行，大部分人都是血淋淋的被骗历史。所以我比较审慎，接洽过几个团队，最终一个反应最冷淡的，我觉得最靠谱，对方不像其他团队，跟你问情况，然后漫天要价。而是直接发了他们官网，上面有各个软件版本的下载试用和license的价格，明码标价，关键是价格不高。

于是我买了一个gui的linux版本，把之前卸载的硬盘快照之后，挂载到gui的linux上面，用这个试用版本的工具来尝试扫描。

最终我通过试用版本的软件扫描出来我需要的文件，当恢复的时候，试用版本的只能恢复部分文件，大部分的是需要买license来解锁的，不过还好，license很便宜，我买的单节点的版本才33澳币左右。果断购入解决，虽然恢复的文件路径没有了，但是文件名称还是对的，方便后期恢复。

[非广告，只为自己记录，下次方便直接找](https://www.ufsexplorer.com)