---
title: bash: login shell vs non-login shell
date: 2022-05-02 14:02:00
categories: linux/advance
tags: [bash, linux]
---

### 1. login shell和non-login shell是什么？
login shell是`参数0`以`"-"`开头，或者使用`--login(-l)`选项启动的shell。

non-login shell是除了login shell之外的shell。

> - [gnome pages](https://help.gnome.org/users/gnome-terminal/stable/pref-login-shell.html.en)
> - [bash manual docs](https://linux.die.net/man/1/bash) 查看Invocation部分

### 2. 如何区分login shell和non-login shell？
根据login shell的介绍说明可知，我们可以查看login shell的`参数0`或根据启动选项中是否包含`login`来判断

``` bash
# METHOD 1，根据参数0是否以"-"开头来判断
echo $0
-bash

# METHOD 2，使用SHELLOPT来判断（这个一定准确，推荐）
shopt login_shell
login_shell       on

shopt -q login_shell && echo 'Login shell' || echo 'Not login shell'
Login shell
```
> 方法1中，参数0不以"-"开头时，也不一定不是login shell，是因为还有部分是通过"--login"选项来启动的。所以推荐用方法2。

### 3. 如何创建login shell和non-login shell？
**创建login shell**
- 通过本地或者远程的连接，使用用户名和密码登录获得的第一个shell
- 通过`bash`或`sh`加上`--login(-l)`参数启动shell
- 使用`sudo -i`或`su -`

**创建non-login shell**
- 未使用账号密码登录，直接使用`bash`或`sh`命令，无`--login(-l)`参数启动shell
- crond中创建任务，默认是non-login shell，但是可以通过显式使用`bash`或`sh`命令加上`--login(-l)`参数，例如`bash(or sh) -l -c "command"`来创建login-shell。

> 这里暂时不讨论图形界面

### 4. 为什么需要有login shell和non-login shell？
没有找到确切的原因，但是根据网上的讨论，一个相对靠谱的说法是，因为login shell和non-login shell加载的start up文件不同（详细的看man文档），有些登录时需要执行的任务，如果在每次执行其他子shell的时候都执行一遍，这样任务太重。所以才创建了这种non-login shell，避免每次创建子shell环境都会执行一遍那些任务。

> [stackexchange answer](https://unix.stackexchange.com/questions/324359/why-a-login-shell-over-a-non-login-shell)