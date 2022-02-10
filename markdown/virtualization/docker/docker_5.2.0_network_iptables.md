---
title: 5.2.0 网络：docker中的iptables
date: 2019-11-12 13:47:00
categories: virtualization/docker
tags: [docker,iptables]
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

# 将所有LOCAL流量导到nat表中的DOCKER-FILTER链中，未转发到nat表中DOCKER链的tcp包，执行nat表的默认策略：ACCEPT
# ！！！下面RETURN 这里是个坑，见后面的大坑说明！！！）
iptables -t nat -I PREROUTING -m addrtype --dst-type LOCAL -j RETURN # 当我们在一个内置的链中使用了RETURN，那么，默认的策略会应用到这个包上，PREROUTING默认的策略是ACCEPT，不过不用担心，因为只要它不去DOCKER链，依然是无法访问程序的（！！！这里是个坑，见后面的大坑说明！！！）
# ！！！上面RETURN 这里是个坑，见后面的大坑说明！！！）
iptables -t nat -I PREROUTING -m addrtype --dst-type LOCAL -j DOCKER-FILTER
```
这样的话，nat表中的流量变成了PREROUTING -> DOCKER-FILTER -> 执行nat表的默认策略：ACCEPT

然后，我们再将自己允许的规则写入
``` bash
iptables -t nat -A DOCKER-FILTER -p tcp -m tcp --dport 80 -m state --state NEW,ESTABLISHED -j DOCKER
```
这样的话，nat表中的允许的流量变成了PREROUTING -> DOCKER-FILTER -> DOCKER，nat表中禁止的流量变成了PREROUTING -> DOCKER-FILTER -> 执行nat表的默认策略：ACCEPT。

### 4. 最终方案补充 - 大坑说明
#### a. 遇到的大坑描述
后来在生产环境中实施上面3里面说到的最终方案，发现一个奇怪的问题，详细描述如下：

背景是启动了一个nginx容器，映射容器端口80到宿主机的80端口
``` bash
docker run -itd -p 80:80 --name nginx nginx:latest
```

首先，我按照3里面说到的最终方案，创建默认禁止全部的规则
``` bash
# 在表nat中创建新的链DOCKER-FILTER
iptables -t nat -N DOCKER-FILTER

# 将所有LOCAL流量导到nat表中的DOCKER-FILTER链中，未转发到nat表中DOCKER链的tcp包，执行nat表的默认策略：ACCEPT
iptables -t nat -I PREROUTING -m addrtype --dst-type LOCAL -j RETURN
iptables -t nat -I PREROUTING -m addrtype --dst-type LOCAL -j DOCKER-FILTER
```
然后我发现，在我增加允许访问80端口的白名单之前，我竟然可以不受任何限制的访问nginx镜像。蛤，按照3里面的说明，而且我在测试环境测试过，不应该发生这种情况啊？

#### b. 现状分析
首先合理的猜测，我3里面的理论，在理论上是没问题的，确实tcp包，在iptables里面的nat表是按照这个流程走的，PREROUTING -> DOCKER-FILTER -> 执行nat表的默认策略：ACCEPT。

**关键是后面，tcp包在nat表中的ACCEPT之后，去了哪里？**

按照iptables的知识，走完PREROUING链后，后面是路由判断去INPUT还是FORWARD，因为在经过nat表中的DOCKER链进行DNAT之前，就已经被ACCEPT，所以在路由判断的时候，tcp包的目的地没有改变，依然是宿主机的ip，所以应该进入的是filter表的INPUT链。

#### c. 理性分析后发现真相（其实是瞎几把猜，外加疯狂google）
理论分析到现在，遇到一个理论和实际冲突，因为按照我的理解，在我的规划中docker端口转发的逻辑应该是这样的：
- 客户对宿主机的端口发起请求 > iptables(nat:PREROUTING:DOCKER-FILTER -> nat:DOCKER-FILTER:DOCKER -> nat:DOCKER:DNAT -> filter:FORWARD:ACCEPT) > docker0(docker网桥设备) > vethxxxxx(容器网卡对中绑定在网桥上的虚拟网卡) > eth0(容器网卡对中在容器中的虚拟网卡)
> nat:PREROUTING:DOCKER-FILTER这个我自己瞎编的格式含义是，iptables表:表中的链:应用的target

**难道还有其他访问的逻辑？。。。。。。还真有，首先，我上面说明的那条逻辑没问题，在其基础上，实际情况下还有另外一条逻辑：**
- 客户对宿主机的端口发起请求 > iptables(nat:PREROUTING:DOCKER-FILTER -> nat:DOCKER-FILTER:ACCEPT -> filter:INPUT:ACCEPT) > docker-proxy(本地用户空间中的端口转发进程) > docker0(docker网桥设备) > vethxxxxx(容器网卡对中绑定在网桥上的虚拟网卡) > eth0(容器网卡对中在容器中的虚拟网卡)

**重点：docker目前依然使用--userland-proxy=true选项作为默认项，开启docker-proxy进程，来转发端口转发的流量，这就是我没有想到的另外一条逻辑**
``` bash
root      5619  0.0  1.3 218448 13208 ?        Sl   07:58   0:00 /usr/bin/docker-proxy -proto tcp -host-ip 0.0.0.0 -host-port 80 -container-ip 172.17.0.2 -container-port 80
```

先不追究docker这么设计的原因，先回归主题，按照之前的分析，tcp封包到了filter表中的INPUT链，这个链的默认策略是ACCEPT，也就是说，如果我没有设定任何INPUT的规则，那么即使我采用了3里面的规划，也是可以访问到容器服务的(而在3的测试环境中，在INPUT链中最后一条是禁止INPUT所有tcp包的流量的规则，所以我误以为3的方案是正确的，从而丧失了发现第二条逻辑的一个机会)。

#### d. 最终方案补充
**最终方案补充：在3的基础上，INPUT那边限制掉所有ip到容器端口转发中宿主机端口的流量。**

此时，我们的逻辑如下
- 允许的流量变成了nat:PREROUTING -> nat:DOCKER-FILTER -> nat:DOCKER:DNAT -> filter:FORWARD:ACCEPT
- 禁止的流量变成了nat:PREROUTING -> nat:DOCKER-FILTER -> nat:ACCEPT -> filter:INPUT:DROP

> docker-proxy浅谈
> 在[docker-proxy 默认禁用选项 --userland-proxy的issue: #14856](https://github.com/moby/moby/issues/14856)中，其实我感觉docker团队的目标是舍弃掉docker-proxy的，目前只是鉴于issue：14856引发的[issue: #5618 内核错误](https://github.com/moby/moby/issues/5618)，并且虽然[torvalds的fix](https://github.com/moby/moby/issues/5618#issuecomment-532623814)解决了内核问题，但是这个需要较高的版本（4.19.30），所以docker团队迄今为止并没有完成issue：14856的目标（在你阅读的时候，你可以去看一下issue：14856最新的进度）。

> 参考链接
> - [docker端口转发浅谈 - 这是我大量查询资料后，第一次接近真相的引子](https://learnku.com/articles/25018)
> - [docker-proxy 默认禁用选项 --userland-proxy的issue](https://github.com/moby/moby/issues/14856)
> - [理解docker-proxy存在现状及其意义的一篇英文博客](https://windsock.io/the-docker-proxy/)
> - [理解docker-proxy存在现状及其意义的另外一篇中文博客](https://www.jianshu.com/p/91002d316185)