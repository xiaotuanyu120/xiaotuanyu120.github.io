---
title: android 1.1.0 安装 android SDK（命令行工具）
date: 2020-04-06 16:34:00
categories: android/operation
tags: [android,sdk]
---

### 0. 问题背景
公司安卓项目需要上CI，于是需要研究android编译，而其编译依赖sdk。


### 1. 安装命令行版本的sdk
在[android ide官网](https://developer.android.com/studio)上，有一个studio的工具，那个是IDE开发工具，但是我们需要的仅仅是命令行的编译工具，所以我们只需要下载下面的`Command line tools only`(下载的是sdk管理工具，还需要使用它来下载sdk)即可
``` bash
# 下载
wget https://dl.google.com/android/repository/commandlinetools-linux-6200805_latest.zip
unzip commandlinetools-linux-6200805_latest.zip

# 列出可用的sdk和其他工具
sdkmanager --sdk_root=/usr/local/android --list

# 安装
sdkmanager --sdk_root=/usr/local/android "platform-tools" "platforms;android-28"
```
> [sdkmanager 使用方法](https://developer.android.com/studio/command-line/sdkmanager)

> 错误1： [Warning: Could not create settings java.lang.IllegalArgumentException](https://stackoverflow.com/questions/60440509/android-command-line-tools-sdkmanager-always-shows-warning-could-not-create-se)


### 2. 自动接受license
``` bash
yes|sdkmanager --sdk_root=/usr/local/android --licenses
```