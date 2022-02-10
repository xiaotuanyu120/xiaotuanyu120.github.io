---
title: container 1.0.1 linux kernel - user namespaces
date: 2020-05-15 14:29:00
categories: virtualization/container
tags: [container,podman,docker,security]
---

### 1. 什么是user namespaces？
从[namespaces manual](http://man7.org/linux/man-pages/man7/namespaces.7.html)中可以看到，linux kernal带来的namespaces是用于隔离系统资源的，让处于一个namespace中的进程会认为自己是在一个独立的系统资源环境中。

namespaces提供了几种不同的flag，来用以创建不同类型的namespace，它们分别为：

Namespace | Flag              | Page                  | Isolates
--------- | ----------------- | --------------------- | ---------
Cgroup    | CLONE_NEWCGROUP   | cgroup_namespaces(7)  | Cgroup root directory
IPC       | CLONE_NEWIPC      | ipc_namespaces(7)     | System V IPC,POSIX message queues
Network   | CLONE_NEWNET      | network_namespaces(7) | Network devices,stacks, ports, etc.
Mount     | CLONE_NEWNS       | mount_namespaces(7)   | Mount points
PID       | CLONE_NEWPID      | pid_namespaces(7)     | Process IDs
Time      | CLONE_NEWTIME     | time_namespaces(7)    | Boot and monotonic clocks
User      | CLONE_NEWUSER     | user_namespaces(7)    | User and group IDs
UTS       | CLONE_NEWUTS      | uts_namespaces(7)     | Hostname and NIS domain name

user namespaces就是通过namespaces提供的一个clone()系统调用API，带上CLONE_NEWUSER这个flag类型来创建的一个独立的用户空间。

> - [RHEL linux 容器博客 - 应用程序公寓复杂例子类比](https://www.redhat.com/en/blog/application-apartment-complex-red-hat-enterprise-linux-linux-containers)
> - [user namespaces - manual](http://man7.org/linux/man-pages/man7/user_namespaces.7.html)

### 2. user namespaces有什么好处？
提到namespace，就不得不提到cgroup，这两个东西提供的系统资源的隔离性，是目前流行的容器技术所仰赖的最大的基石。而目前主流的容器应用中（最新的docker19.0.3和podman正在改进这个问题，这里不提），存在这样一个安全问题。有部分容器内部的进程必须以特权用户（root）运行，在没有user namespace的情况下，容器内的用户和宿主机的用户是一致的，也就是说，容器内的uid 0和容器外（宿主机）的uid 0是一致的。在特定的情况下，这种运行模式就存在着很大的安全风险。

但是如果使用了user namespaces，容器中运行的用户对应的宿主机上的用户就可以灵活的映射，举个例子，容器A中的uid 0，我们可以映射到宿主机的uid 20000，容器B中的uid 0，我们可以映射到宿主机的uid 25000。这样就能够大大增强了容器的安全性。

> - [RHEL linux 容器博客 - 容器接下来是什么？user namespaces](https://www.redhat.com/en/blog/whats-next-containers-user-namespaces)

### 3. 具体如何使用
我们需要配置的两个文件：
- `/etc/subuid`
- `/etc/subgid`
这两个文件格式基本一致`用户名:映射uid起点:映射uid长度`，举个例子`container:100000:65536`，意思就是container用户启动的容器，映射宿主机的100000-165535到容器的0-65535。也就是root用户的uid 0 映射到宿主机就是uid 100000。

当我们配置好以上两个文件之后，有两个执行文件会负责在容器启动的时候，创建用户命名空间并将配置好的uid和gid映射到容器中，这两个执行文件就是`newuidmap`,`newgidmap`(rhel系安装`shadow-utils`，debian系安装`uidmap`)。

> - [newuidmap - manual](http://man7.org/linux/man-pages/man1/newuidmap.1.html)