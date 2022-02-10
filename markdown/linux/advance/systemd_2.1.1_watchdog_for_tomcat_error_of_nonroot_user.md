---
title: systemd 2.1.1 watchdog of systemd for tomcat continue: nonroot user problem
date: 2019-10-17 16:58:00
categories: linux/advance
tags: [systemd]
---

### 美好被打破
在[上一篇文章里面](./systemd_2.1.0_watchdog_for_tomcat.html)我们介绍了如何创建一个脚本，来和tomcat在同一个cgroup中启动，然后通过systemd-notify来进行tomcat运行状态监控。然后目前这个看起来很美好的画面被一个现实打破了。

上面讲的一切正常的前提是，我们的systemd里面是使用root身份来执行进行，当我们换成了非root身份，比如普通用户tomcat，发现systemd-notify的逻辑貌似失效了一样。

通过各种调试，尝试过试用root启动systemd unit程序，然后里面使用su和sudo去切换用户执行命令什么的，皆以失败而告终。

后面网上搜索了一下，发现systemd-notify这个sd_notify的wraper使用起来很有限制，而sd_notify本身的原理就是和`$NOTIFY_SOCKET`变量指向的socket(systemd)通讯发送各种信号而已。而且网上也有评论推荐自己使用语言来实现整个watchdog的逻辑，而不是使用systemd-notify。于是就有了下面这个go语言的watchdog版本

### 为什么是go而不是py
其实py开发这种运维脚本是最方便的，一是基本上有点开发能力的运维大概率对py熟悉，另外一个是它简单。但是go语言也很容易上手，而且关键是，跨平台特性比py好，不需要注意不同版本系统的py环境。

### 实现的思路
其实思路很简单，和[上一篇文章里面](./systemd_2.1.0_watchdog_for_tomcat.html)逻辑一样，只不过在以下几个问题上，略有不同

#### 不同1：获取jvm的pid
bash脚本里面，我是使用ss命令得到了监听端口关联的pid。在go里面，一番了解后，发现本身os.exec.command是可以返回执行命令的pid的，于是尝试了以下，发现tomcat可以正常启动，其他逻辑也正常，但是有一个问题，MAINPID不是JVM的pid，而是catalina.sh这个脚本的pid。相当于我们需要获取脚本fork的子进程的pid。

经过一番搜索，在执行command的时候，可以让系统附加执行setgpid，这样可以让catalina.sh和jvm进程之间属于同一个group pid，而通过使用ps和grep命令，通过列出的pgid列筛选出实际的jvm的pid，来配置了正确的MAINPID。

### [源码地址](https://github.com/xiaotuanyu120/systemd-watchdog-tomcat)

### 扩展阅读
- [关于nonroot用户运行systemd的issue](https://github.com/systemd/systemd/issues/2739)