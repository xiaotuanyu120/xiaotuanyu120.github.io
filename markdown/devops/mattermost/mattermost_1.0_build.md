---
title: mattermost: 1.0 build
date: 2020-03-10 13:51:00
categories: devops/mattermost
tags: [go,golang,mattermost,npm,nvm,react.js]
---

### 0. 环境准备
- golang环境
- node环境

mattermost 服务端用的是golang编写，然后服务端有提供前端web服务

- mattermost-server：服务端golang代码，另外也有前端代码
- mattermost-webapp：服务端前端代码，和server的代码放在同一个目录中，server里面make的时候会在`../mattermost-webapp/dist`拷贝编译好的前端代码

> - [官方开发编译指引](https://developers.mattermost.com/contribute/server/developer-workflow/)

### 1. 编译过程
``` bash
# step 1. 下载代码
cd ~/go/src
# 代码版本，自己去切换
git clone https://github.com/xiaotuanyu120/mattermost-webapp.git
git clone https://github.com/xiaotuanyu120/mattermost-server.git

# step 2. 编译前端
cd mattermost-webapp
npm install
# 以下操作见下面的注释里面的引用
cd node_modules/mattermost-redux/
npm install
npm run build
cd ../../
npm run build

# step 3. 编译后端
cd ../mattermost-server
make package
# 如果只是编译mattermost这个二进制命令，可以直接编译`go build cmd/mattermost/main.go`
```
> [编译时提示Module not found:的解决办法](https://github.com/mattermost/mattermost-redux/issues/814)