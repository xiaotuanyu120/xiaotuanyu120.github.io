---
title: git error: 1.1.0 curl 18 error
date: 2019-11-07 16:56:00
categories: devops/git
tags: [git,error,curl]
---
### git error: 1.1.0 curl 18 error

---

### 0. 错误信息
```
error: RPC failed; curl 18 transfer closed with outstanding read data remaining
fatal: the remote end hung up unexpectedly
fatal: early EOF
fatal: index-pack failed
```

### 1. 解决方案
这些解决方案不是一套的，可以按照这个步骤一步一步排查下去，只要解决了，后面的就不用尝试了

#### step 1 查看自己的网络环境和git服务提供的网络环境
查看自己的网络到git服务网络之间，是否有什么代理，有没有什么限制。
如果有代理的话，最好是直连一下git服务，排除一下是不是代理的问题

#### step 2 git客户端增加buffer
``` bash
# 增加http的buffer为500m
git config --global http.postBuffer 524288000
```

#### step 3 尝试分步下载
``` bash
# 先下载深度1的文件
git clone http://your-repo-url/someproject.git --depth 1

# 然后全部下载一次
cd somproject
git fetch --unshallow
```