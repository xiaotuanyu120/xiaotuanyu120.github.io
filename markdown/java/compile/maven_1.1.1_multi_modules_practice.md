---
title: maven 1.1.1 多module工程的版本管理实践
date: 2020-12-27 18:02:00
categories: java/compile
tags: [java,maven]
---

### 1. 问题点
一个java的maven工程，里面有多个modules，然后各个modules之间还有相互依赖关系。在这样的情况下，如何对子模块的version标准管理呢？

### 2. 官方建议方法
要点：
- maven版本要在3.5.0以上
- 项目version使用变量`${revision}`、`${sha1}`和`${changelist}`（不可变更变量名称）来组合version名称
- 子module使用同样的变量组合方式来指定parent version，然后自身并不指定version（继承parent version）
- 子module互相之间的依赖，使用`${project.version}`来标准化，其实内容就是parent的version

**示例:parent-pom.xml**
``` xml
<project>
  <modelVersion>4.0.0</modelVersion>
  <parent>
    <groupId>org.apache</groupId>
    <artifactId>apache</artifactId>
    <version>18</version>
  </parent>
  <groupId>org.apache.maven.ci</groupId>
  <artifactId>ci-parent</artifactId>
  <name>First CI Friendly</name>
  <version>${revision}</version>
  ...
  <properties>
    <revision>1.0.0-SNAPSHOT</revision>
  </properties>
  <modules>
    <module>ci-child1</module>
    ..
  </modules>
</project>
```
**示例：child-pom.xml**
``` xml
<project>
  <modelVersion>4.0.0</modelVersion>
  <parent>
    <groupId>org.apache.maven.ci</groupId>
    <artifactId>ci-parent</artifactId>
    <version>${revision}</version>
  </parent>
  <groupId>org.apache.maven.ci</groupId>
  <artifactId>ci-child1</artifactId>
   ...
  <dependencies>
	<dependency>
      <groupId>org.apache.maven.ci</groupId>
      <artifactId>ci-child2</artifactId>
      <version>${project.version}</version>
    </dependency>
  </dependencies>
</project>
```

关于`INSTALL & DEPLOY`，官方的原话是
```
If you like to install or deploy artifacts by using the above setup you have to use the flatten-maven-plugin otherwise you will install/deploy artifacts in your repository which will not be consumable by Maven anymore. Such kind of setup will look like this:
```
``` xml
<project>
  <modelVersion>4.0.0</modelVersion>
  <parent>
    <groupId>org.apache</groupId>
    <artifactId>apache</artifactId>
    <version>18</version>
  </parent>
  <groupId>org.apache.maven.ci</groupId>
  <artifactId>ci-parent</artifactId>
  <name>First CI Friendly</name>
  <version>${revision}</version>
  ...
  <properties>
    <revision>1.0.0-SNAPSHOT</revision>
  </properties>
 
 <build>
  <plugins>
    <plugin>
      <groupId>org.codehaus.mojo</groupId>
      <artifactId>flatten-maven-plugin</artifactId>
      <version>1.1.0</version>
      <configuration>
        <updatePomFile>true</updatePomFile>
        <flattenMode>resolveCiFriendliesOnly</flattenMode>
      </configuration>
      <executions>
        <execution>
          <id>flatten</id>
          <phase>process-resources</phase>
          <goals>
            <goal>flatten</goal>
          </goals>
        </execution>
        <execution>
          <id>flatten.clean</id>
          <phase>clean</phase>
          <goals>
            <goal>clean</goal>
          </goals>
        </execution>
      </executions>
    </plugin>
  </plugins>
  </build>
  <modules>
    <module>child1</module>
    ..
  </modules>
</project>
```
> 大概的意思，我猜，是因为所有的version我们使用了变量，而不是固定的一个值，所以需要一个插件来特别处理，以保证其能在maven库中正确的被别人引用

**CI支持**
至于官方提供了这个方法，其实是为了更好的兼容CI，因为不可能每次编译都手动修改pom，那么在命令行里面来修改version变量的方法就是
```
mvn -Drevision=1.0.0-SNAPSHOT clean package
```
> 实际的CI流程中，肯定是使用变量来替代`1.0.0-SNAPSHOT`，例如日期字符串，或者commit串等，例如：`-Drevision=$(date +%Y%m%d.%H%M%S-${CI_COMMIT_SHA:0:6})`

> [apache官方CI友好文档 - 提及的多模块version管理](https://maven.apache.org/maven-ci-friendly.html#multi-module-setup)