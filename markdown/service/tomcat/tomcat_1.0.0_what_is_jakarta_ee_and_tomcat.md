---
title: tomcat 1.0.0 Jakarta EE 和 Tomcat
date: 2022-10-05 10:44:00
categories: service/tomcat
tags: [tomcat,linux]
---

## 0. 什么是Jakarta EE？
Jakarta EE是用于开发云原生 Java 应用程序的开源框架。

其历史发展为，sun公司的JAVA EE（Enterprise Edition），到oracle收购sun，然后捐JAVA EE给eclipse。eclipse将JAVA EE更名为EE4J（Eclipse Enterprise for Java）。因eclipse在javax和java商标上无法与oracle达成一致，oracle将JAVA EE更名为Jakarta EE。

## 1. 什么是Tomcat？
Apache Tomcat 是 Jakarta Servlet、Jakarta Server Pages、Jakarta Expression Language、Jakarta WebSocket、Jakarta Annotations 和 Jakarta Authentication 规范的开源实现。

Jakarta EE平台由JAVA EE进化而来。Tomcat 10和之后的版本实现的Jakarta EE。而Tomcat 9和之前的版本实现的是JAVA EE。

> - Jakarta Servlet: 虽然Servlet可以响应多种请求，但最常见的用途是作为Web容器，用以托管web应用。
> - Jakarta Server Pages: JSP，是帮助软件开发人员根据HTML、XML、SOAP或其他文档类型创建动态生成网页的技术集合。
> - Jakarta Expression Language: 是一种特殊目的编程语言，主要用于在Jakarta EE Web应用程序的网页中嵌入和评估表达式。
> - Jakarta WebSocket: 顾名思义，是web socket。
> - Jakarta Annotations: 顾名思义，是java 注解。
> - Jakarta Authentication: 顾名思义，是java 授权。


## 2. Tomcat版本
不同的tomcat版本支持的JAVA语言和Jakarta EE组件的版本不同。

> [选择tomcat版本](https://tomcat.apache.org/whichversion.html)