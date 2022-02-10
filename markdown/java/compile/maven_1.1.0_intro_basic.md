---
title: maven 1.1.0 基础介绍
date: 2020-12-21 10:02:00
categories: java/compile
tags: [java,maven]
---

### 1.1 repository是什么？
maven的repository指的是保存artifact和依赖的仓库。分为本地和远程两种，本地仓库就是本地的一个目录，远程仓库分为公共仓库和私有仓库（本地网络中的一个服务，例如nexus）。

### 1.2 如何使用repository？
一般情况下，对于本地仓库，我们无需修改任何东西，除非需要清理磁盘空间。对于远程仓库，它可以实现上传（如果你有权限）和下载的功能。对于未存在于本地仓库中的依赖，maven会选择在远程仓库中下载那些依赖，默认情况下，会使用公共的central库，如果希望要修改，可以在maven的本地配置文件`settings.xml`中指定 [mirror](https://maven.apache.org/guides/mini/guide-mirror-settings.html) 来修改默认的公共central库为其他库的地址，但是，更常见的配置是在java project的`pom.xml`中 [自定义库地址](https://maven.apache.org/guides/mini/guide-multiple-repositories.html)  。

### 1.3 私有repository的用途
以前没有私有库的时候，本地的java project之间如果互相依赖，那么就需要手动拷贝jar包，或者干脆合并两个java project。如果遇到不同java project的不同版本release的依赖，则更加复杂，并且容易出错。

而使用私有库，就可以将一个复杂依赖的java project拆开，而只是在mvn中配置依赖和依赖版本，很大的增强了管理

### 1.4 repository配置示例
``` xml
<project>
  <repositories>
    <repository>
      <id>releases</id>
      <url>http://your-host:8081/repository/maven-releases/</url>
    </repository>
  </repositories>
</project>
```
> 这里是以自建的私有库为例，若私有库需要auth访问，那么需要在mvn的配置(settings.xml)中增加[私有仓库server的auth配置](/java/compile/maven_1.2.0_nexus.html)，需要重点注意的是`repository`里面的`id`必须和(settings.xml)中`server`的`id`一致。