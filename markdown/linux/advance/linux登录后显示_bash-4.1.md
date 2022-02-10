---
title: linux登录后显示_bash-4.1
date: 2014-12-05 17:25:00
categories: linux/advance
tags: [linux,bash_profile,bashrc]
---

### 问题原因 
出现这种现象的原因是root目录下 .bash_profile   .bashrc
 
两个环境文件丢失。

### 解决方法
重新建立这两个文件
``` bash
vi /root/.bash_profile
************************************ 
# Get the aliases and functions
if [ -f ~/.bashrc ]; then
        . ~/.bashrc
fi
 
# User specific environment and startup programs
 
PATH=$PATH:$HOME/bin
 
export PATH
unset USERNAME
************************************
 
 
vi /root .bashrc
************************************
# User specific aliases and functions
 
alias rm='rm -i'
alias cp='cp -i'
alias mv='mv -i'
 
# Source global definitions
if [ -f /etc/bashrc ]; then
        . /etc/bashrc
fi
************************************