---
title: maven 1.2.0 私有仓库nexus
date: 2020-12-20 21:43:00
categories: java/compile
tags: [java,maven,nexus]
---

### 1. nexus（oss开源版本）是什么？
按照官方说法，nexus是一个支持通用格式的artifact储存仓库。实际上最广为流行的用途是作为maven（java的编译工具）的私有仓库（相对于maven的公共仓库）。

为何有了maven的公共仓库，还需要自己创建一个私有仓库呢：
- 节省流量，避免重复的公网流量浪费
- 加快速度，本地私有仓库请求速度肯定比公网快
- 部署第三方组件，指的是那些没有加入到公共仓库的组件（一般都是商业原因）
- 降低公共仓库压力（这个就是一个硬凑的理由）

### 2. 如何部署nexus？
首先，安装docker和docker-compose，然后准备下面这个`docker-compose.yml`
``` yaml
version: '3'
services:
  nexus:
    image: sonatype/nexus3:3.29.0
    container_name: nexus
    restart: always
    ports:
      - "8081:8081"
    volumes:
       - /data/docker/data/nexus/data:/nexus-data
```

启动nexus
``` bash
docker-compose up -d
```
> 访问http://ip:8081，会提示你admin的初始密码保存在`/nexus-data/admin.password`文件中。

### 3. 配置maven环境 - nexus的账号和密码
maven的settings.xml分为全局和用户两种配置文件，顾名思义，全局就是所有用户共同的配置，用户就是指定用户特定的配置（默认在`~/.m2/settings.xml`）。

这两种配置文件，可以分别使用下面的选项来手动指定
``` bash
mvn -s /path/to/user-settings.xml

mvn -gs /path/to/global-settings.xml
```

`settings.xml`的内容示例
``` xml
<?xml version="1.0" encoding="UTF-8"?>

<settings xmlns="http://maven.apache.org/SETTINGS/1.0.0"
          xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
          xsi:schemaLocation="http://maven.apache.org/SETTINGS/1.0.0 http://maven.apache.org/xsd/settings-1.0.0.xsd">
  <!-- servers
   | This is a list of authentication profiles, keyed by the server-id used within the system.
   | Authentication profiles can be used whenever maven must make a connection to a remote server.
   |-->
  <servers>
    <!-- server
     | Specifies the authentication information to use when connecting to a particular server, identified by
     | a unique name within the system (referred to by the 'id' attribute below).
     |
     | NOTE: You should either specify username/password OR privateKey/passphrase, since these pairings are
     |       used together.
    -->
    <server>
      <id>releases</id>
      <username>admin</username>
      <password>password-for-admin</password>
    </server>

    <server>
      <id>snapshots</id>
      <username>admin</username>
      <password>password-for-admin</password>
    </server>

    <repositories>
      <repository>
        <id>releases</id>
        <name>releases</name>
        <url>http://nexus.example.org/repository/maven-releases</url>
      </repository>
      <repository>
        <id>snapshots</id>
        <name>snapshots</name>
        <url>http://nexus.example.org/repository/maven-snapshots</url>
      </repository>
    </repositories>

    <!-- Another sample, using keys to authenticate.
    <server>
      <id>siteServer</id>
      <privateKey>/path/to/private/key</privateKey>
      <passphrase>optional; leave empty if not used.</passphrase>
    </server>
    -->
  </servers>

</settings>
```
> 重点关注每一个`server`的`id`，这个id必须非重复，且和后面执行的信息需要匹配

### 4.1 配置你的java project，并发布
在java工程的maven文件`pom.xml`里面加入如下配置，指定编译后包的发布地址
``` xml
<project ...>

  ...

  <distributionManagement>
    <snapshotRepository>
      <id>snapshots</id>
      <url>http://your-host:8081/repository/maven-snapshots/</url>
    </snapshotRepository>
    <repository>
      <id>releases</id>
      <url>http://your-host:8081/repository/maven-releases/</url>
    </repository>
  </distributionManagement>
</project>
```
> `repository`的`id`和前面maven配置文件`settings.xml`里面`server`的`id`必须要一致

> `repository/maven-releases/`代表了nexus界面里面browse功能里面展示的各个repository的名称

执行发布
``` bash
mvn deploy [-s /path/to/user-settings.xml]
```

### 4.2 手动发布
详情见[maven command basic](/java/compile/maven_1.1.4_command_basic.html)
> [apache guide of 3rd-party-jars-remote](https://maven.apache.org/guides/mini/guide-3rd-party-jars-remote.html)

### 5. 常见问题
**常见错误**
- 405, 有可能url写错了
- 400, 有可能是不允许重新发布，也有可能是账号密码写错了

**注意事项**
相应的代码修改之后，原则上要修改version，以保证每个release都是静态的，而不是用同一个version重复发布变更的代码。

将思路放在如何让maven强制更新同一个version重复发布的release是一个**错误的方向**，应该确保每次代码修改后，其version相应的做出改动，其他组件对其的依赖通过version来更新其版本，这样才是正确的思路