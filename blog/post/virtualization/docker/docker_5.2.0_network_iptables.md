---
title: 5.2.0 网络：docker中的iptables
date: 2019-11-12 13:47:00
categories: virtualization/docker
tags: [docker,iptables]
---
### 5.2.0 网络：docker中的iptables

---

### 0. 问题背景
启动了一个tomcat的docker容器，将其端口映射到宿主机的80端口上
``` bash
docker run -itd --rm -p 80:8080 --name tomcat tomcat:jdk8
```
然后按照我们的生产惯例，需要对80端口做防火墙限制，于是按照经验，增加了下面这条规则
```
iptables -A INPUT -s 172.16.0.0/24 -p tcp -m tcp --dport 80 -j ACCEPT
iptables -A INPUT -j REJECT --reject-with icmp-host-prohibited
```
> 允许172.16.0.0/24的来源ip访问80端口，禁止其他来源ip对任何ip的访问

结果奇怪的事情发生了，经过测试，刚才设想的规则竟然没有生效，任何来源ip都可以访问80端口。于是觉得自己应该详细研究一下iptables和docker之间到底发生了什么了。

### 1. docker and iptables
先来研究一下docker和iptables的关系，首先，在开始之前，请先阅读以下两个文档
- [iptables-manual](http://ipset.netfilter.org/iptables.man.html)
- [docker and iptables](https://docs.docker.com/network/iptables/)

iptables本身，最有价值的是一张图，关于这个图，大家可以搜索iptables关键字，然后查看图片，就会有很多，在这里不赘述。里面重点如下
1. iptables比较重要的几个表：raw，nat，filter，mangle
2. 每个表里面有很多链，有默认链，也可以增加自定义链
3. 一个tcp包到达后，并不是走完一个表的所有链然后再去走另外一个包里面的所有链，而是根据链的顺序来走，详细可以参照你查到的iptables图片

大概先说一下docker官方文档里面讲的iptables相关内容
1. docker会把iptables规则写到DOCKER链里面
2. 如果需要增加自己的规则，请写到DOCKER-USER链中
3. 默认docker是会自动管理iptables规则，我们可以选择关闭它，然后手动管理（如果你手动管理了，那真是脑子有问题了）


### 2. 实际分析
理论看完了，那么咱们来实际分析问题，既然docker官方推荐咱们使用DOCKER-USER链，那咱们试试写入如下规则
``` bash
# 咱们先drop所有的80的包看见效果
iptables -I DOCKER-USER -t tcp -m tcp --dport 80 -j DROP
```
结果让我大跌眼镜，WHAT？我竟然还可以访问？为啥子来？

冷静，冷静，首先先看看现在的iptables规则
``` bash
iptables-save
# 输出了两部分
# 第一部分，nat表，部分内容如下
*nat
:PREROUTING ACCEPT [0:0]
:INPUT ACCEPT [0:0]
:OUTPUT ACCEPT [4:296]
:POSTROUTING ACCEPT [4:296]
:DOCKER - [0:0]
-A PREROUTING -m addrtype --dst-type LOCAL -j DOCKER
-A OUTPUT ! -d 127.0.0.0/8 -m addrtype --dst-type LOCAL -j DOCKER
-A POSTROUTING -s 172.28.0.0/16 ! -o br-0be676646756 -j MASQUERADE
-A POSTROUTING -s 172.17.0.0/16 ! -o docker0 -j MASQUERADE
-A POSTROUTING -s 172.17.0.2/32 -d 172.17.0.2/32 -p tcp -m tcp --dport 8080 -j MASQUERADE
-A DOCKER -i br-0be676646756 -j RETURN
-A DOCKER -i docker0 -j RETURN
-A DOCKER ! -i docker0 -p tcp -m tcp --dport 80 -j DNAT --to-destination 172.17.0.2:8080
COMMIT
# Completed on Tue Nov 12 06:12:30 2019

# 第二部分，filter表，这部分内容不重要，可以忽略，只要关注上面的nat表内容即可
*filter
:INPUT ACCEPT [69:4048]
:FORWARD DROP [0:0]
:OUTPUT ACCEPT [37:2916]
:DOCKER - [0:0]
:DOCKER-ISOLATION-STAGE-1 - [0:0]
:DOCKER-ISOLATION-STAGE-2 - [0:0]
:DOCKER-USER - [0:0]
......
COMMIT
# Completed on Tue Nov 12 06:12:30 2019
```
发现问题了，WTF，原来在nat表里面的链PREROUTING，将所有LOCAL类型的都转给了nat中的DOCKER链
```
iptables -I DOCKER-USER -p tcp -m tcp --dport 80 -j DROP
```
然后在nat表的DOCKER链中，对来源ip进行了nat转换，变成了`容器ip:8080`
```
-A DOCKER ! -i docker0 -p tcp -m tcp --dport 80 -j DNAT --to-destination 172.17.0.2:8080
```
那么问题就好理解了，因为当包到达INPUT表中的DOCKER-USER链时，它已经不是访问80端口了，已经是8080了，我们对80做的限制，当然是无效的。

汗，既然找到了原因，那么再来分析一下我们的需求
- 开放程序给部分ip
- 禁止其他所有的来源ip对该程序的访问

这样的话，我们可以增加以下规则（提前先清除掉之前增加的所有自定义规则）
``` bash
iptables -I DOCKER-USER -p tcp -j DROP
iptables -I DOCKER-USER -s 172.16.0.0/24 -p tcp -m tcp --dport 8080 -j ACCEPT
```
然后事实再一次打脸，WTF，白名单内的我竟然无法访问了。汗，仔细看了以下，原来我这样的设置，是禁调了很多docker默认的容器间的、容器和宿主机网桥的网络规则。

如果要修复这个问题，我们可以配置好各个容器网卡之间的访问规则，然后再配置容器网卡和宿主机网桥之间的规则（事实上我们现在就是这样干的）。但是这样有个问题，容器网卡的名称，都是随机的啊亲，难道每一次创建虚拟网卡后都来改一遍规则吗？

那么我还有一个办法，我手动创建容器网络，给它们指定网段，到时候开通规则直接网段间允许所有不就可以啦，美滋滋。

但是冷静了5s之后，我还是觉得有点不对劲。再过了5s思考之后，我知道了不对劲的原因，这样一点都不完美啊，docker自动创建的规则和自定义的规则包括网络的设置交叉在一起，逻辑一点不清晰。难道就不能有更好的解决方案吗？

### 3. 最终方案
经过思考之后，发现，其实在input表里面的DOCKER-USER链中做规则限制，已经进入了容器的访问阶段了，既然在这个阶段设定规则如此复杂，那么如果在它的前一个阶段来配置自定义规则呢？

在nat表中，我们增加以下规则
``` bash
# 在表nat中创建新的链DOCKER-FILTER
iptables -t nat -N DOCKER-FILTER

# 禁止所有nat表中的访问，然后将所有LOCAL流量导到DOCKER-FILTER中
iptables -t nat -I PREROUTING -m addrtype --dst-type LOCAL -j RETURN # 当我们在一个内置的链中使用了RETURN，那么，默认的策略会应用到这个包上，PREROUTING默认的策略是ACCEPT，不过不用担心，因为只要它不去DOCKER链，依然是无法访问程序的
iptables -t nat -I PREROUTING -m addrtype --dst-type LOCAL -j DOCKER-FILTER
```
这样的话，nat表中的流量变成了PREROUTING -> DOCKER-FILTER -> 禁止

然后，我们再将自己允许的规则写入
``` bash
iptables -t nat -A DOCKER-FILTER -p tcp -m tcp --dport 80 -m state --state NEW,ESTABLISHED -j DOCKER
```
这样的话，nat表中的允许的流量变成了PREROUTING -> DOCKER-FILTER -> DOCKER，nat表中禁止的流量变成了PREROUTING -> DOCKER-FILTER -> 禁止。