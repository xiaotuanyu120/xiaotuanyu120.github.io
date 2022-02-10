---
title: zabbix 1.2.0 usage
date: 2021-03-17 10:25:00
categories: service/zabbix
tags: [zabbix]
---

### 0. 前言
zabbix选项卡里面，最重要的是以下两个
- 监控：查看监控内容
- 配置：配置监控，所有的主机组、模板、主机、监控项等等都在这里

### 1. 配置 - 主机组
主机组故名思义，就是主机组，没有额外配置，就是一个group主机的选项

### 2. 配置 - 模板
模板的创建需要挂在一个主机组下，创建时只需要
- 模板名称
- 主机组

以下资源都是绑定在模板上的：
- 应用集：监控项的group
- 监控项：具体的监控的item
- 触发器：针对监控项的数值触发器，用以问题分级
- 图形：基于监控项创建的图表
- 仪表盘
- 自动发现规则：自动发现并创建监控项的规则

#### 模板增加资源的方式
1. 链接其他模板
2. 在其他模板细节界面，拷贝监控项、图形等资源，拷贝到新模板
3. 自己根据zabbix agent的关键词来创建规则
> [zabbix agent rules](https://www.zabbix.com/documentation/current/manual/config/items/itemtypes/zabbix_agent)

### 2.1 配置模板示例
#### 网卡流量
- 监控项
  - 键值
    - net.if.in[eth0,bytes]
    - net.if.out[eth0,bytes]
    - net.if.total[eth0,bytes]
  - 进程
    1. 每秒更改
    2. 自定义倍数：8

### 3. 配置 - 主机
创建主机的时候，需要配置
- 主机组归属
- 应用的模板
- 收集数据的方式，一般都是zabbix agent（zabbix agent要提前创建和启动好)