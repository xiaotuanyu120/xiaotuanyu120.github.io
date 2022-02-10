---
title: jenkins: 2.3.0 修改slave节点的环境变量
date: 2019-04-24 09:49:00
categories: devops/jenkins
tags: [jenkins,java,linux]
---

### 1. 问题背景
jenkins创建了一个gitlab源码的job，因为gitlab使用的是https。于是遇到了以下错误：
``` bash
Peer's Certificate issuer is not recognized
```
在网上查到了很多相关资料，和解决办法，总的来讲是以下两种

1. 下载一个根域名证书（一般都是下载的mozilla的，网上很多），然后更新系统的证书认证服务
2. 全局或者单个repo禁用git的ssl认证

在master上，我通过方法2解决了这个问题，但是在slave上，设置了宿主机的环境变量，却一直无法生效，所以就怀疑，肯定是slave的环境变量配置有问题。

---

### 2. 如何设置slave上的环境变量?
原来在jenkins的`系统管理` **>** `节点管理` **>** `节点配置`（齿轮形状按钮）处，可以勾选环境变量选项，然后在里面输入变量名称和变量内容即可。
