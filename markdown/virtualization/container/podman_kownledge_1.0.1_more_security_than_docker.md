---
title: podman knowledge 1.0.1 为何podman比docker安全
date: 2020-05-15 10:00:00
categories: virtualization/container
tags: [container,podman,docker,security]
---

### 0. 参考文档
[why podman is more secured than docker](https://cloudnweb.dev/2019/10/heres-why-podman-is-more-secured-than-docker-devsecops/)

### 1. audit and loginuid
宿主机上，audit 监控文件
``` bash
sudo auditctl -w /etc/shadow
sudo touch /etc/shadow
sudo ausearch -f /etc/shadow -i -ts recent
----
type=PROCTITLE msg=audit(05/15/20 01:56:36.088:897) : proctitle=touch /etc/shadow 
type=PATH msg=audit(05/15/20 01:56:36.088:897) : item=1 name=/etc/shadow inode=35153145 dev=fd:00 mode=file,000 ouid=root ogid=root rdev=00:00 objtype=NORMAL cap_fp=none cap_fi=none cap_fe=0 cap_fver=0 
type=PATH msg=audit(05/15/20 01:56:36.088:897) : item=0 name=/etc/ inode=33554497 dev=fd:00 mode=dir,755 ouid=root ogid=root rdev=00:00 objtype=PARENT cap_fp=none cap_fi=none cap_fe=0 cap_fver=0 
type=CWD msg=audit(05/15/20 01:56:36.088:897) :  cwd=/home/vagrant 
type=SYSCALL msg=audit(05/15/20 01:56:36.088:897) : arch=x86_64 syscall=open success=yes exit=3 a0=0x7ffcb6d257aa a1=O_WRONLY|O_CREAT|O_NOCTTY|O_NONBLOCK a2=0666 a3=0x7ffcb6d24620 items=2 ppid=4304 pid=4324 auid=vagrant uid=root gid=root euid=root suid=root fsuid=root egid=root sgid=root fsgid=root tty=pts0 ses=7 comm=touch exe=/usr/bin/touch key=(null) 
```
> 可以看出auid准确的识别了，我的普通用户vagrant

每次登陆系统，都会存在loginuid，而且这个值是不会变的
``` bash
# 查看用户的loginuid
id vagrant
uid=1000(vagrant) gid=1000(vagrant) groups=1000(vagrant)

cat /proc/self/loginuid 
1000

# 即使你su切换了用户，loginuid也不会变
sudo su

id
uid=0(root) gid=0(root) groups=0(root)

cat /proc/self/loginuid 
1000
```

### 2. docker的表现
``` bash
# 使用docker容器来测试audit
sudo docker run --rm --privileged -v /:/host fedora touch /host/etc/shadow

sudo ausearch -f /etc/shadow -i
----
type=PROCTITLE msg=audit(05/15/20 02:11:37.642:936) : proctitle=touch /host/etc/shadow 
type=PATH msg=audit(05/15/20 02:11:37.642:936) : item=1 name=/host/etc/shadow inode=35153145 dev=fd:00 mode=file,000 ouid=root ogid=root rdev=00:00 objtype=NORMAL cap_fp=none cap_fi=none cap_fe=0 cap_fver=0 
type=PATH msg=audit(05/15/20 02:11:37.642:936) : item=0 name=/host/etc/ inode=33554497 dev=fd:00 mode=dir,755 ouid=root ogid=root rdev=00:00 objtype=PARENT cap_fp=none cap_fi=none cap_fe=0 cap_fver=0 
type=CWD msg=audit(05/15/20 02:11:37.642:936) :  cwd=/ 
type=SYSCALL msg=audit(05/15/20 02:11:37.642:936) : arch=x86_64 syscall=openat success=yes exit=3 a0=0xffffff9c a1=0x7fff21dacf50 a2=O_WRONLY|O_CREAT|O_NOCTTY|O_NONBLOCK a3=0x1b6 items=2 ppid=4435 pid=4452 auid=unset uid=root gid=root euid=root suid=root fsuid=root egid=root sgid=root fsgid=root tty=(none) ses=unset comm=touch exe=/usr/bin/touch key=(null) 

# 使用docker容器来查看loginuid
sudo docker run --rm fedora cat /proc/self/loginuid
4294967295
```
> 原因其实就是因为fork和exec，docker cli通过和docker server通信，由docker server来创建的container。所以container没有继承执行docker cli的用户的信息

### 3. podman的表现
``` bash
# 使用podman容器来测试audit
sudo ausearch -f /etc/shadow -i
----
type=PROCTITLE msg=audit(05/15/20 02:22:10.404:987) : proctitle=touch /host/etc/shadow 
type=PATH msg=audit(05/15/20 02:22:10.404:987) : item=1 name=/host/etc/shadow inode=35153145 dev=fd:00 mode=file,000 ouid=root ogid=root rdev=00:00 objtype=NORMAL cap_fp=none cap_fi=none cap_fe=0 cap_fver=0 
type=PATH msg=audit(05/15/20 02:22:10.404:987) : item=0 name=/host/etc/ inode=33554497 dev=fd:00 mode=dir,755 ouid=root ogid=root rdev=00:00 objtype=PARENT cap_fp=none cap_fi=none cap_fe=0 cap_fver=0 
type=CWD msg=audit(05/15/20 02:22:10.404:987) :  cwd=/ 
type=SYSCALL msg=audit(05/15/20 02:22:10.404:987) : arch=x86_64 syscall=openat success=yes exit=3 a0=0xffffff9c a1=0x7ffd333d1f3f a2=O_WRONLY|O_CREAT|O_NOCTTY|O_NONBLOCK a3=0x1b6 items=2 ppid=4859 pid=4871 auid=vagrant uid=root gid=root euid=root suid=root fsuid=root egid=root sgid=root fsgid=root tty=(none) ses=7 comm=touch exe=/usr/bin/touch key=(null)

# 使用podman容器来测试loginuid
sudo podman run --rm fedora cat /proc/self/loginuid
1000
```
> podman 是直接由运行podman命令的用户fork出的container，这个container是其子进程，所以能继承父进程的用户信息


### 4. 总结
podman因为没有docker那种cli和server的关系，所以创建的容器和podman命令之间是父子进程关系。这样的设计让容器更接近我们以前认知中的进程，可以更好的使用以前的方式来运维容器进程。