---
title: maven 1.4.0 命令行基础
date: 2020-12-29 20:36:00
categories: java/compile
tags: [java,maven]
---

### 1.1 编译子模块
``` bash
mvn clean install -pl child-module -am -amd
```
> - pl: 模块名称
> - am: 编译指定子模块依赖的模块
> - amd: 编译依赖指定子模块的模块 

### 1.2 删除本地库中的依赖
``` bash
mvn dependency:purge-local-repository -DreResolve=false -DmanualInclude="com.xxx"
```

### 2.1 deploy artifact to local repository
``` bash
mvn install:install-file -Dfile=test-1.0.jar -DgroupId=org.example -DartifactId=test -Dversion=1.0 -Dpackaging=jar
```

### 2.2 deploy artifact to remote repository
``` bash
# mvn deploy:deploy-file -DgroupId=<group-id> \
#   -DartifactId=<artifact-id> \
#   -Dversion=<version> \
#   -Dpackaging=<type-of-packaging> \
#   -Dfile=<path-to-file> \
#   -DrepositoryId=<id-to-map-on-server-section-of-settings.xml> \
#   -Durl=<url-of-the-repository-to-deploy>

mvn deploy:deploy-file -DgroupId=org.example -DartifactId=test -Dversion=1.0-SNAPSHOT -Dfile=test-1.0-SNAPSHOT.jar -Durl=http://nexus.example.org/repository/maven-snapshots/ -DrepositoryId=snapshots
```