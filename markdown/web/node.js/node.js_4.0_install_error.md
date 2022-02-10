---
title: node.js: 4.0 npm install error
date: 2017-12-29 11:16:00
categories: web/node.js
tags: [node.js]
---

### 1. npm install Error one
``` bash
npm install
...
gyp WARN EACCES attempting to reinstall using temporary dev dir "/root/fabric-samples/fabcar/node_modules/pkcs11js/.node-gyp"
gyp WARN EACCES user "root" does not have permission to access the dev dir "/root/fabric-samples/fabcar/node_modules/pkcs11js/.node-gyp/6.12.2"
...
```

解决方法：
``` bash
npm install --unsafe-perm --verbose
```
> [github issue 链接](https://github.com/nodejs/node-gyp/issues/454)

### 2. npm install Error two
有时候我们会用普通用户来执行npm install，明明使用了sudo，还是会报
```
sudo PATH=/usr/java/jdk1.8.0_144/bin:/usr/java/jdk1.8.0_144/bin:/usr/local/bin:/usr/bin:/usr/java/jdk1.7.0_79/bin:/usr/java/jdk1.7.0_79/jre/bin:/usr/local/node-v10.15.3/bin:/usr/local/node-v10.15.3/bin /usr/local/node-v10.15.3/bin/npm install --unsafe-perm --allow-root
Unhandled rejection Error: Command failed: /usr/bin/git clone --depth=1 -q -b master git://github.com/mattermost/marked.git /root/.npm/_cacache/tmp/git-clone-353bdefa
fatal: could not create leading directories of '/root/.npm/_cacache/tmp/git-clone-353bdefa': Permission denied

    at ChildProcess.exithandler (child_process.js:294:12)
    at ChildProcess.emit (events.js:189:13)
    at maybeClose (internal/child_process.js:970:16)
    at Socket.stream.socket.on (internal/child_process.js:389:11)
    at Socket.emit (events.js:189:13)
    at Pipe._handle.close (net.js:597:12)
Unhandled rejection Error: Command failed: /usr/bin/git submodule update -q --init --recursive
fatal: Could not change back to '/root/.npm/_cacache/tmp/git-clone-ef63fcf9': Permission denied
...
```

解决办法：
``` bash
sudo sudo PATH=$PATH:/usr/local/node/bin npm install --unsafe-perm --allow-root
```
> `PATH=$PATH:/usr/local/node/bin`，这个是为了解决，有时候执行sudo，而本地env中的变量没有保持到sudo的用户中，从而报：node无法找到的错误


### 3. npm install pm2报错
使用npm4版本安装pm2`npm config set registry https://registry.npm.taobao.org && npm install pm2 -g`的时候报错
```
npm ERR! Verification failed shile extracting blessed@0.1.81
```

解决办法：升级npm到最新版本
```
npm install -g npm@latest
npm config set registry https://registry.npm.taobao.org && npm install pm2 -g
```