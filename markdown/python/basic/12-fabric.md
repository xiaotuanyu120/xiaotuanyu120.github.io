---
title: fabric
date: 2015-09-14 13:35:00
categories: python/basic
tags: [python]
---
## 1. fabric
Fabric is a Python (2.5-2.7) library and command-line tool for streamlining the use of SSH for application deployment or systems administration tasks.

### 1.1 安装方法
``` bash
yum install python-devel -y
pip install fabric
```

## 2. Example
创建fabfile文件`fab.py`
``` python
from fabric.api import run

def os_version():
    run('uname -r')
```

fabric默认使用文件名称为fabfile.py
``` bash
fab -l

Fatal error: Couldn't find any fabfiles!

Remember that -f can be used to specify fabfile path, and use -h for help.

Aborting.

mv fab.py fabfile.py
fab -l
Available commands:

    os_version
```

fab tools
``` bash
fab -H root@localhost os_version
 Executing task 'os_version'
 run: uname -r
 out: 3.10.0-123.el7.x86_64
 out:


Done.
Disconnecting from localhost... done.
# -H 指定host
# fab -H user@hostname command
```

可以自己传要执行哪些命令吗?
`fabfile2.py`
``` python
from fabric.api import run


def command(cmd):
    run(cmd)
```
``` bash
fab -f fabfile2.py -l
Available commands:

    command

fab -f fabfile2.py -H root@localhost command:pwd
 Executing task 'command'
 run: pwd
 out: /root
 out:


Done.
Disconnecting from localhost... done.
```

## 3. roles&hosts

### 3.1 HOSTS
`fabfile.py`
``` python
from fabric.api import run, env, roles, hosts


@hosts('root@192.168.0.96')
def host_type():
    run('uname -s')
```
``` bash
fab -l
Available commands:

    host_type

fab host_type
[root@192.168.0.96] Executing task 'host_type'
[root@192.168.0.96] run: uname -s
[root@192.168.0.96] out: Linux
[root@192.168.0.96] out:


Done.
Disconnecting from 192.168.0.96... done.
```

### 3.2 ROLE
`fabfile.py`
``` python
from fabric.api import run, env, roles, hosts

env.roledefs = {
    'selfdefine':[
        'root@192.168.0.96'
    ]
}


@roles('selfdefine')
def host_type():
    run('uname -r')
```
``` bash
fab -l
Available commands:

    host_type

fab host_type
[root@192.168.0.96] Executing task 'host_type'
[root@192.168.0.96] run: uname -r
[root@192.168.0.96] out: 3.10.0-123.el7.x86_64
[root@192.168.0.96] out:


Done.
Disconnecting from 192.168.0.96... done.
```

## 4. local
在远程机器上执行命令，主要用到的函数`run`，如果涉及到本地命令，可使用`local`
`fabfile.py`
``` python
from fabric.api import local


def localhost_type():
    local('uname -r')
```
``` bash
fab -l
Available commands:

    localhost_type

fab localhost_type
[localhost] local: uname -r
3.10.0-123.el7.x86_64

Done.
```

## 5. 看下常用的函数
``` python
from fabric.colors import red, green

fabric.contrib.files.exists

with cd('/path/to/app'):

with prefix('workon myvenv'):

fabric.operations.get
# 下载文件
# http://docs.fabfile.org/en/latest/api/core/operations.html

fabric.operations.put
```

## 6.  实战一下
来看一个需求：写一个部署程序，流程是先把本地代码文件打成tar包，然后批量上传到多台服务器上解压缩并执行。

> fabric官网：
> - http://docs.fabfile.org/en/latest/tutorial.html
> - http://fabric-chs.readthedocs.org/zh_CN/chs/

ansible使用，自学即可：
- http://www.the5fire.com/ansible-guide-cn.html 入门指南
- http://www.the5fire.com/explore-the-ansible.html  执行原理

## 7. 作业
1. 写一个fabfile实现可批量在任意多台已配置ssh key的机器上完成ipython的安装，要求检测是否已经安装，如果没有则安装。