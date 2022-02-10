---
title: maven 1.1.3 jar和war中resources的区别
date: 2020-12-29 16:31:00
categories: java/compile
tags: [java,maven]
---

### 1. resources
发现maven工程中的`src/main/resources`中的文件会自动的拷贝到war包的`WEB-INF/classes`目录中，不知道这是不是一个默认的行为，所以想找一下官方文档验证。于是看到[how do I add resources to my jar](https://maven.apache.org/guides/getting-started/index.html#How_do_I_add_resources_to_my_JAR)，心想，jar应该和war差不多吧，但是看下去发现了不同，文档中说`src/main/resources`的文件会自动拷贝到jar的根目录下！？这就奇怪了，为啥和war里面的不同？

于是研究了一波[jar和war的区别](/java/compile/maven_1.1.2_jar_vs_war.html)，才知道原来jar的classes是放在根目录下的，而war的classes是放在`WEB-INF/classes`下面的（classpath不同？），所以就会出现这个差别了。

所以maven工程打包war包时，将`src/main/resources`中的文件拷贝到w`WEB-INF/classes`目录是默认行为