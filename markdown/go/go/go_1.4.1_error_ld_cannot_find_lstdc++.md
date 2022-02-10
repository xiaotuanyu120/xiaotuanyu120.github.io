---
title: GO 1.4.1 error 编译错误 - ld: cannot find -lstdc++
date: 2020-08-09 22:12:00
categories: go/go
tags: [go,sql]
---

### 0. 问题描述
在centos7 x64中编译一个[开源项目](https://github.com/gobitfly/eth2-beaconchain-explorer)，遇到如下问题
```
/usr/bin/ld: cannot find -lstdc++
collect2: error: ld returned 1 exit status
```

### 1. 解决方案
排查过程
#### 1) 缺少依赖库？
肯定是缺少库了，google搜索到的结果，逐个安装一波`yum install libstdc++.x86_64 libstdc++-devel.x86_64 libstdc++-static.x86_64`，结果发现错误依旧

#### 2) 库文件位置不对？
按照网上说的debug一波
``` bash
ld -lstdc++ --verbose

......

attempt to open //usr/x86_64-redhat-linux/lib64/libstdc++.so failed
attempt to open //usr/x86_64-redhat-linux/lib64/libstdc++.a failed
attempt to open //usr/lib64/libstdc++.so failed
attempt to open //usr/lib64/libstdc++.a failed
attempt to open //usr/local/lib64/libstdc++.so failed
attempt to open //usr/local/lib64/libstdc++.a failed
attempt to open //lib64/libstdc++.so failed
attempt to open //lib64/libstdc++.a failed
attempt to open //usr/x86_64-redhat-linux/lib/libstdc++.so failed
attempt to open //usr/x86_64-redhat-linux/lib/libstdc++.a failed
attempt to open //usr/local/lib/libstdc++.so failed
attempt to open //usr/local/lib/libstdc++.a failed
attempt to open //lib/libstdc++.so failed
attempt to open //lib/libstdc++.a failed
attempt to open //usr/lib/libstdc++.so failed
attempt to open //usr/lib/libstdc++.a failed
ld: cannot find -lstdc++
```
发现是找不到libstdc++.so和libstdc++.a，于是搜索了一波系统文件，发现了几个不同目录下的libstdc++.so.6，于是逐个做软连接到`/usr/lib/libstdc++.so`，重新执行上面的debug命令
``` bash
ld -lstdc++ --verbose

......

attempt to open //usr/x86_64-redhat-linux/lib64/libstdc++.so failed
attempt to open //usr/x86_64-redhat-linux/lib64/libstdc++.a failed
attempt to open //usr/lib64/libstdc++.so failed
attempt to open //usr/lib64/libstdc++.a failed
attempt to open //usr/local/lib64/libstdc++.so failed
attempt to open //usr/local/lib64/libstdc++.a failed
attempt to open //lib64/libstdc++.so failed
attempt to open //lib64/libstdc++.a failed
attempt to open //usr/x86_64-redhat-linux/lib/libstdc++.so failed
attempt to open //usr/x86_64-redhat-linux/lib/libstdc++.a failed
attempt to open //usr/local/lib/libstdc++.so failed
attempt to open //usr/local/lib/libstdc++.a failed
attempt to open //lib/libstdc++.so succeeded
ld: skipping incompatible //lib/libstdc++.so when searching for -lstdc++
attempt to open //lib/libstdc++.a failed
attempt to open //usr/lib/libstdc++.so succeeded
ld: skipping incompatible //usr/lib/libstdc++.so when searching for -lstdc++
attempt to open //usr/lib/libstdc++.a failed
ld: cannot find -lstdc++
```
提示不兼容，那么就两种可能：
- 版本不兼容
- 位数不兼容（32位程序？排除，因为安装了i386的库发现还是不行）

那么问题有可能是版本不兼容，后来通过下面两个方式验证，果然是版本不兼容
- 将centos7 换成fedora 31（libc++ 9.3.0版本）
- 使用开源项目中的dockerfile，查看libc++版本（9.3.0）

获得一个教训，开发还是要用ubuntu或者fedora等环境啊，centos和redhat还是只适合服务器和运维个人的测试环境了。