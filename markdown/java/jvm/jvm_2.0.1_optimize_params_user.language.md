---
title: JVM: 2.0.1 调优：-Duser.language引起的oracle driver报错
date: 2019-09-05 09:06:00
categories: java/jvm
tags: [java,jvm,user.language,oracle]
---

### 0. 问题背景
有一个java程序使用了oracle driver连接oracle数据库，结果在tomcat启动的时候，有如下报错信息
```
2019-09-03 11:16:52,474 [Druid-ConnectionPool-Create-2015198630] ERROR [com.alibaba.druid.pool.DruidDataSource] - create connection error
java.sql.SQLException: Locale not recognized
        at oracle.jdbc.driver.T4CTTIoauthenticate.setSessionFields(T4CTTIoauthenticate.java:1006)
        at oracle.jdbc.driver.T4CTTIoauthenticate.<init>(T4CTTIoauthenticate.java:238)
        at oracle.jdbc.driver.T4CConnection.logon(T4CConnection.java:401)
        at oracle.jdbc.driver.PhysicalConnection.<init>(PhysicalConnection.java:553)
        at oracle.jdbc.driver.T4CConnection.<init>(T4CConnection.java:254)
        at oracle.jdbc.driver.T4CDriverExtension.getConnection(T4CDriverExtension.java:32)
        at oracle.jdbc.driver.OracleDriver.connect(OracleDriver.java:528)
        at com.alibaba.druid.pool.DruidAbstractDataSource.createPhysicalConnection(DruidAbstractDataSource.java:1375)
        at com.alibaba.druid.pool.DruidAbstractDataSource.createPhysicalConnection(DruidAbstractDataSource.java:1431)
        at com.alibaba.druid.pool.DruidDataSource$CreateConnectionThread.run(DruidDataSource.java:1844)
```


### 1. 问题原因
通过搜索报错，在stackoverflow上发现这样一个[回答](https://stackoverflow.com/questions/9685052/an-getting-this-error-when-i-run-my-project-java-sql-sqlexception-locale-not-r)，于是检查了tomcat配置，配置如下
```
JAVA_OPTS="$JAVA_OPTS -Djavax.servlet.request.encoding=UTF-8 -Djavax.servlet.response.encoding=UTF-8 -Dfile.encoding=UTF-8 -Duser.language=zh_CN -Dsun.jnu.encoding=UTF-8"
```
重点是`-Duser.language=zh_CN`，原来JVM里面是有两个system property来一起表示`zh_CN`，一个是`user.language`，一个是`user.country`。这里应该配置成`-Duser.language=zh -Duser.country=CN`。
> 这里有几点需要说明：
- 之所以有加这个参数，是因为线上有这个标准。而之所以这个标准以前存在了很久没有报错，**<个人猜测>**是因为mysql里面没有依赖JVM的Locale这个system property**<个人猜测>**。
- 其实如果没有手动增加`user.language`和`user.country`这两个system property，JVM会使用默认的`en`和`US`，也不会报错，这边是画蛇添足了。

参考资料：
- [oracle对jdk7中的Locale官方文档](https://docs.oracle.com/javase/7/docs/api/java/util/Locale.html)
- [iana对语言的缩写描述文档 - 关于zh和其他语言缩写标准](https://www.iana.org/assignments/language-subtag-registry/language-subtag-registry)