---
title: maven 1.1.2 jar和war的区别
date: 2020-12-29 16:10:00
categories: java/compile
tags: [java,maven]
---

### 0. 参考链接
- [stackoverflow: jar vs war](https://stackoverflow.com/questions/5871053/difference-between-jar-and-war-in-java)
- [sun: jar basic](https://web.archive.org/web/20120626012843/http://java.sun.com/developer/Books/javaprogramming/JAR/basics)
- [sun: war docs](https://web.archive.org/web/20120626020019/http://java.sun.com/j2ee/tutorial/1_3-fcs/doc/WCC3.html)
- [腾讯云问答：war和jar区别](https://cloud.tencent.com/developer/ask/37456)

### 1. jar
**个人理解**

jar是一个类的相关文件存档，包含并不限于以下文件：
- classes：com/example/www/...
- META-INF
  - MANIFEST.MF
  - 其他信息文件，例如maven

主要用途：一个单独运行的应用程序，或者其他工程依赖的一个单独的模块

### 2. war
**个人理解**

war是一个web应用文件的存档，包含并不限于以下文件：
- META-INF
  - MANIFEST.MF
  - 其他信息文件，例如maven
- WEB-INF
  - classes：com/example/www/...
  - lib: *.jar
  - web.xml

主要用途：完整的web应用，包含各种java的classes文件，依赖的jar包，各种静态文件等