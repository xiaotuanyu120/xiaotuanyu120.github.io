---
title: vue: 0.1.0 部署vue项目到阿里云的OSS中
date: 2020-02-27 10:40:00
categories: web/vue.js
tags: [vue.js,oss]
---

## 1. 部署静态站点到OSS的标准步骤

- 购买oss，创建bucket
- 在bucket中上传静态站点需要的所有文件（如果要上传目录，可以使用[oss browser](https://help.aliyun.com/document_detail/61872.html)）
- 在`基础设置` - `静态页面` 中做以下设定
  - 默认首页
  - 404页面
  - 子目录首页：如果开通此选项，如果你访问`https://example.com/folder`且这个目录不存在时，会根据你所选择的选项进行对应的处理(详情见你设定的页面，有很详细解释，基本上就是返回404或者帮你重定向)
- 在`传输管理` - `域名管理` 中做以下设定
  - 绑定用户域名
  - 增加域名对应的证书
  - 将域名的dns解析到阿里云提供的cname上

## 2. vue相遇遇到的问题和解决方案
### 遇到的问题
发现我们的网站是分pc和mobile网站，访问首页的时候，会根据客户端来重定向到对应客户端平台的url，例如：`https://www.example.com/pc/home/index`和`https://www.example.com/mobile/home/index`。访问第一次的时候正常，但是每当刷新首页时，就会返回404页面。



### 解决过程

首先猜测访问过程，第一次访问可以刷新出页面的原因，可能是因为我们访问的是`https://www.example.com`，虽然由vue-router给跳转到了`https://www.example.com/pc/home/index`，但是我们发给oss的请求是`https://www.example.com`，oss显然意识到了我们的请求是正常的，且首页存在，于是成功返回。但是当我们二次手动刷新此页面时，请求的url变成了`https://www.example.com/pc/home/index`，这个路径在oss肯定是不存在的，404返回是正常行为。

因为在部署到oss之前，vue项目在服务器上是正常的，所以我重新读了一下nginx配置，其中关键是这部分
```
  location / {
    root   /app;
    index  index.html;
    try_files $uri $uri/ /index.html;
  }
```
其中的逻辑就是，如果`$uri`不存在，那么首先试一下`$uri/`，如果还是不存在，再试一下`/index.html`。

于是参照这个逻辑，又参照了下面参考链接中其他人的做法，我用以下配置解决了此问题
- `基础设置` - `镜像回源` - `创建规则`
  - 回源类型：重定向
  - 回源条件：http状态码=404
  - 回源地址：添加前后缀 - 实际是添加了后缀，就是给`$uri`加上后缀`/`
  - 重定向code：301

问题得到顺利解决

## 3. 问题思考

### 解决方式和子目录首页的逻辑很相似，为什么不用子目录首页？
因为子目录首页原理是访问子目录路径下的`index.html`，若在oss中子目录下并没有首页文件，依然会是返回404，那么会导致无限循环

### 给`$uri`后面增加`/`，在oss里面岂不是依然不存在这个路径，为什么就能解决这个问题
首先声明，下面解释只是个人猜测。
在说明这个问题之前，我们先看一下nginx的日志里面的逻辑，nginx常规情况下是使用location的匹配来对request进行路由的，但是因为vue有自己内置的路由逻辑，所以对于vue项目，nginx只需要无脑的把所有请求统统塞给vue即可，如果尝试`uri`不成功，则尝试一下给`uri`加上`/`。我个人猜测，这应该是vue自己的机制（未深入了解）。详细的原因，推荐阅读官方文档（偷个懒，上班太忙，实在没时间去深入了解前端知识）


> 参考链接
> [cnblog: 某用户的vue部署到oss的经验](https://www.cnblogs.com/xuejiangjun/p/9454221.html)