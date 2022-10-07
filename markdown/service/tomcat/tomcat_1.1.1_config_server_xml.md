---
title: tomcat 1.1.1 配置 server.xml 和 context
date: 2017-02-16 10:20:00
categories: service/tomcat
tags: [tomcat,linux]
---
# 1. `server.xml`
## 1.1 结构说明
`$CATALINA_HOME/conf/server.xml`是tomcat的主要配置文件。

- `Server`，顶层元素
- `Service`，包含`Engine`和`Connector`
  - `Connector`，一个或者多个，用于接收请求
  - `Engine`
    - `Host`，一个或者多个，虚拟主机（_类似于nginx中的Server - 虚拟主机_）
      - `Context`， 一个或者多个，用于给虚拟主机指定不同web应用 （_类似于nginx中的location，针对不同的url，路由到不同的web应用来处理_）

tomcat 10.0.26中默认的`server.xml`
``` xml
<?xml version="1.0" encoding="UTF-8"?>
<!--
  Licensed to the Apache Software Foundation (ASF) under one or more
  contributor license agreements.  See the NOTICE file distributed with
  this work for additional information regarding copyright ownership.
  The ASF licenses this file to You under the Apache License, Version 2.0
  (the "License"); you may not use this file except in compliance with
  the License.  You may obtain a copy of the License at

      http://www.apache.org/licenses/LICENSE-2.0

  Unless required by applicable law or agreed to in writing, software
  distributed under the License is distributed on an "AS IS" BASIS,
  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
  See the License for the specific language governing permissions and
  limitations under the License.
-->
<!-- Note:  A "Server" is not itself a "Container", so you may not
     define subcomponents such as "Valves" at this level.
     Documentation at /docs/config/server.html
 -->
<Server port="8005" shutdown="SHUTDOWN">
  <Listener className="org.apache.catalina.startup.VersionLoggerListener" />
  <!-- Security listener. Documentation at /docs/config/listeners.html
  <Listener className="org.apache.catalina.security.SecurityListener" />
  -->
  <!-- APR library loader. Documentation at /docs/apr.html -->
  <Listener className="org.apache.catalina.core.AprLifecycleListener" SSLEngine="on" />
  <!-- Prevent memory leaks due to use of particular java/javax APIs-->
  <Listener className="org.apache.catalina.core.JreMemoryLeakPreventionListener" />
  <Listener className="org.apache.catalina.mbeans.GlobalResourcesLifecycleListener" />
  <Listener className="org.apache.catalina.core.ThreadLocalLeakPreventionListener" />

  <!-- Global JNDI resources
       Documentation at /docs/jndi-resources-howto.html
  -->
  <GlobalNamingResources>
    <!-- Editable user database that can also be used by
         UserDatabaseRealm to authenticate users
    -->
    <Resource name="UserDatabase" auth="Container"
              type="org.apache.catalina.UserDatabase"
              description="User database that can be updated and saved"
              factory="org.apache.catalina.users.MemoryUserDatabaseFactory"
              pathname="conf/tomcat-users.xml" />
  </GlobalNamingResources>

  <!-- A "Service" is a collection of one or more "Connectors" that share
       a single "Container" Note:  A "Service" is not itself a "Container",
       so you may not define subcomponents such as "Valves" at this level.
       Documentation at /docs/config/service.html
   -->
  <Service name="Catalina">

    <!--The connectors can use a shared executor, you can define one or more named thread pools-->
    <!--
    <Executor name="tomcatThreadPool" namePrefix="catalina-exec-"
        maxThreads="150" minSpareThreads="4"/>
    -->


    <!-- A "Connector" represents an endpoint by which requests are received
         and responses are returned. Documentation at :
         HTTP Connector: /docs/config/http.html
         AJP  Connector: /docs/config/ajp.html
         Define a non-SSL/TLS HTTP/1.1 Connector on port 8080
    -->
    <Connector port="8080" protocol="HTTP/1.1"
               connectionTimeout="20000"
               redirectPort="8443" />
    <!-- A "Connector" using the shared thread pool-->
    <!--
    <Connector executor="tomcatThreadPool"
               port="8080" protocol="HTTP/1.1"
               connectionTimeout="20000"
               redirectPort="8443" />
    -->
    <!-- Define an SSL/TLS HTTP/1.1 Connector on port 8443 with HTTP/2
         This connector uses the NIO implementation. The default
         SSLImplementation will depend on the presence of the APR/native
         library and the useOpenSSL attribute of the AprLifecycleListener.
         Either JSSE or OpenSSL style configuration may be used regardless of
         the SSLImplementation selected. JSSE style configuration is used below.
    -->
    <!--
    <Connector port="8443" protocol="org.apache.coyote.http11.Http11NioProtocol"
               maxThreads="150" SSLEnabled="true">
        <UpgradeProtocol className="org.apache.coyote.http2.Http2Protocol" />
        <SSLHostConfig>
            <Certificate certificateKeystoreFile="conf/localhost-rsa.jks"
                         type="RSA" />
        </SSLHostConfig>
    </Connector>
    -->

    <!-- Define an AJP 1.3 Connector on port 8009 -->
    <!--
    <Connector protocol="AJP/1.3"
               address="::1"
               port="8009"
               redirectPort="8443" />
    -->

    <!-- An Engine represents the entry point (within Catalina) that processes
         every request.  The Engine implementation for Tomcat stand alone
         analyzes the HTTP headers included with the request, and passes them
         on to the appropriate Host (virtual host).
         Documentation at /docs/config/engine.html -->

    <!-- You should set jvmRoute to support load-balancing via AJP ie :
    <Engine name="Catalina" defaultHost="localhost" jvmRoute="jvm1">
    -->
    <Engine name="Catalina" defaultHost="localhost">

      <!--For clustering, please take a look at documentation at:
          /docs/cluster-howto.html  (simple how to)
          /docs/config/cluster.html (reference documentation) -->
      <!--
      <Cluster className="org.apache.catalina.ha.tcp.SimpleTcpCluster"/>
      -->

      <!-- Use the LockOutRealm to prevent attempts to guess user passwords
           via a brute-force attack -->
      <Realm className="org.apache.catalina.realm.LockOutRealm">
        <!-- This Realm uses the UserDatabase configured in the global JNDI
             resources under the key "UserDatabase".  Any edits
             that are performed against this UserDatabase are immediately
             available for use by the Realm.  -->
        <Realm className="org.apache.catalina.realm.UserDatabaseRealm"
               resourceName="UserDatabase"/>
      </Realm>

      <Host name="localhost"  appBase="webapps"
            unpackWARs="true" autoDeploy="true">

        <!-- SingleSignOn valve, share authentication between web applications
             Documentation at: /docs/config/valve.html -->
        <!--
        <Valve className="org.apache.catalina.authenticator.SingleSignOn" />
        -->

        <!-- Access log processes all example.
             Documentation at: /docs/config/valve.html
             Note: The pattern used is equivalent to using pattern="common" -->
        <Valve className="org.apache.catalina.valves.AccessLogValve" directory="logs"
               prefix="localhost_access_log" suffix=".txt"
               pattern="%h %l %u %t &quot;%r&quot; %s %b" />

      </Host>
    </Engine>
  </Service>
</Server>
```

## 1.2 不同配置介绍
### 1.2.1 Connector
#### **SSL配置**
> 一般情况下，在公网请求的处理方面，在请求到达java应用程序之前，已经在接入层做了SSL卸载的动作；而对内部的java组件之间的交互，一般是将它们部署在同一个内网，网络边界有防火墙防护；对于第三方java api组件，则有可能需要启用ssl加密。
> 
> 基于上面的应用范围分析，目的是要说明，一般情况下，并不需要在tomcat上配置SSL。

**tomcat6和7在ssl的配置上大同小异，后面使用tomcat同时代指这两个版本进行说明。**

在HOWTO文档中可得到信息，tomcat对ssl有两种实现方式：
- the JSSE implementation provided as part of the Java runtime (since 1.4)
- the APR implementation, which uses the OpenSSL engine by default.

由于APR提供了更好的IO性能，生产环境一般启用APR，所以这里仅对apr对ssl的配置进行说明

在Connector配置中启用APR
``` xml
<!-- Define a HTTP/1.1 Connector on port 8443, APR implementation -->
<Connector protocol="org.apache.coyote.http11.Http11AprProtocol"
           port="8443" .../>
```
如果不手动制定apr的protocol，tomcat会自动在两种实现方式中选择，但推荐明确的指定apr的protocol。 

在APR模式下，需要使用`SSLCertificateFile`和`SSLCertificateKeyFile`
``` xml
<!-- Define a SSL Coyote HTTP/1.1 Connector on port 8443 -->
<Connector
           protocol="org.apache.coyote.http11.Http11AprProtocol"
           port="8443" maxThreads="200"
           scheme="https" secure="true" SSLEnabled="true"
           SSLCertificateFile="/usr/local/ssl/server.crt"
           SSLCertificateKeyFile="/usr/local/ssl/server.pem"
           SSLVerifyClient="optional" SSLProtocol="TLSv1+TLSv1.1+TLSv1.2"/>
```
> **JSSE SSL配置选项**
> 
> 对于证书文件，如果使用JSSE，需要使用keystoreFile和keystorPass，感兴趣的可以查看howto连接

> **SSLCertificateKeyFile的文件后缀名**
> 
> 虽然在HOWTO文档中，我们看到key文件使用的是pem后缀，但是参照apr文档中对于https配置的介绍，我们也可以使用server.key。

> **参考链接**
> 
> - [tomcat6 ssl howto文档](https://tomcat.apache.org/tomcat-6.0-doc/ssl-howto.html)
> - [tomcat7 ssl howto文档](https://tomcat.apache.org/tomcat-7.0-doc/ssl-howto.html)
> - [tomcat7 apr文档](http://tomcat.apache.org/tomcat-7.0-doc/apr.html)

#### SSL生产样例
综合上述文档，实际使用格式如下
``` xml
<Connector port="443" protocol="org.apache.coyote.http11.Http11AprProtocol"
     maxThreads="32000" SSLEnabled="true" scheme="https" secure="true"
     SSLCertificateFile="${catalina.base}/conf/server.crt"
     SSLCertificateKeyFile="${catalina.base}/conf/server.key" />
```
> 对于crt，key，pem，jks等证书格式，HOWTO文档中均有介绍，详细生成和获得方式也可以google出很多教程，这里不再涉及

### 1.2.2 Host
- `appBase`，指定部署app的base目录，默认是webapps。
- `deployOnStart`，设定为true时，在tomcat启动时去启动appBase目录下的app，默认是true。
- `autoDeploy`，设定为true时，会定期检查app中文件是否被更新过或有新文件，若有更新和新增，则部署它们。用于热部署，默认是true。
- `deployXML`，设定为true时，会加载应用中的/META-INF/context.xml文件。为了安全，推荐设定为false。当设定为false时，tomcat会去xmlBase下加载独立在app之外的上下文xml文件。默认为true
- `xmlBase`，上下文xml文件所在目录，默认为conf/<engine_name>/<host_name>。
- `deployIgnore`，`appBase`中忽略启动的app，支持正则匹配。

``` xml
<Host deployIgnore=".*ROOT.*|.*host.*|.*manager.*|.*docs.*|.*example.*" />
```

> **推荐配置 - 禁用全部热部署或禁用部分热部署**
> - 常规情况下，我们可以将`autoDeploy`、`deployXML`、`deployOnStart`全部设置为false，然后通过配置单独的`context`文件来手动指定我们需要启动的app路径。
> - 也可以开启`deployOnStart=true`，然后用`deployIgnore`排除掉我们不希望启动的app


# 2. context
线上的工程，一直在server.xml里面配置context来指定工程目录，不是特别清楚里面配置的含义，结果就系统性的查询了一下，结果真就发现，直接在server.xml里面配置context是不推荐的(`<Context path="" docBase="/root/webfile/web" debug=“0” reloadable="false"/>`)，当然，也不是不可以这样，详细请查看后面说明。  
> 主要参考了[tomcat 7.0.90的context说明文档](https://tomcat.apache.org/tomcat-7.0-doc/config/context.html)

## 2.1 context
### 2.1.1 配置说明
context元素表示在特定虚拟主机中运行的Web应用程序。每个Web应用程序都基于Web应用程序归档（WAR）文件或包含相应解压缩内容的相应目录。web应用程序通过http请求的URI与context path变量的最长匹配来处理http请求。当context被匹配中后，它会通过`WEB-INF/web.xml`中配置的servlet来处理http请求。

context元素可以配置多个，每个context的名称必须是唯一的。context path不需要唯一，见[多版本并行部署](https://tomcat.apache.org/tomcat-7.0-doc/config/context.html#Parallel_deployment)。每个虚拟主机中至少要配置一个context path为空的context，这个context作为默认的web应用程序，会处理所有匹配不到其他context的http请求。

### 2.1.2 名称
当虚拟主机执行`autoDeploy`或`deployOnStartup`操作时，Web应用程序的context name和context path是从定义Web应用程序的文件的名称派生的。因此，context path可能未在应用程序中嵌入的`META-INF/context.xml`中定义，并且context name，context path，context version和base filename（名称减去任何.war或.xml扩展名）之间存在密切关系。 

如果没有version指定的话，context name和context path是一致的。如果context path是空（默认context），则context name是ROOT，否则，base filename就是context path去掉开头的`/`然后替换其他的`/`为`#`。 

如果指定了version，context path不变，context name和base filename会在结尾增加`##version`

Context Path|Context Version|Context Name|Base File Name|Example File Names (.xml, .war & directory)
---|---|---|---|---
/foo|None|/foo|foo|foo.xml, foo.war, foo
/foo/bar|None|/foo/bar|foo#bar|foo#bar.xml, foo#bar.war, foo#bar
Empty String|None|Empty String|ROOT|ROOT.xml, ROOT.war, ROOT
/foo|42|/foo##42|foo##42|foo##42.xml, foo##42.war, foo##42
/foo/bar|42|/foo/bar##42|foo#bar##42|foo#bar##42.xml, foo#bar##42.war, foo#bar##42
Empty String|42|##42|ROOT##42|ROOT##42.xml, ROOT##42.war, ROOT##42

> version是一个字符串，没有version指定的时候是空字符串，tomcat根据字符串排序来判定不同的version的先后顺序，"001"比"002"早，空字符串比"11"早。

虽然有上面的规则将context path和base filename关联在了一起，但是，我们还是有办法让base filename不再根据context path派生。 

下面说明两种方法：
- disable `autoDeploy`和`deployOnStartup`，然后将所有context在server.xml中配置。
- 将war包或者工程目录放在appBase定义的目录之外，然后配置一个context.xml，在里面定义docBase

### 2.1.3 定义context
不建议将`Context`直接配置在`server.xml`中，一个原因是`server.xml`不重启是无法重新被加载的；另一个原因是，`server.xml`中的`Context`配置会被默认`Context`覆盖掉。

可以按照如下方式定义context：
- 在web应用程序`META-INF/context.xml`中配置。可选，若host配置了copyXML（此属性仅在deployXML为true时生效），则会拷贝此context文件到$CATALINA_BASE/conf/[enginename]/[hostname]/中，并重命名为应用程序的base filename加上.xml后缀。
- 在$CATALINA_BASE/conf/[enginename]/[hostname]/目录中，根据base filename派生出context path和version。这个文件也会取代`META-INF/context.xml`的优先权。
- 在server.xml的HOST元素中配置context

默认的context配置会多个web应用程序应用。web应用程序单独配置的context会覆盖任意的默认配置的context。
- $CATALINA_BASE/conf/context.xml中，context配置会被所有的web应用程序加载
- $CATALINA_BASE/conf/[enginename]/[hostname]/context.xml.default中，会被指定的hostname的host中的所有web应用程序加载

### 2.1.4 属性
有很多context种的具体属性，可参照[tomcat 7.0.90 context文档 - atrributes](https://tomcat.apache.org/tomcat-7.0-doc/config/context.html#Attributes)

> 其他更多详细信息，可以查看[tomcat 7.0.90 官方context文档](https://tomcat.apache.org/tomcat-7.0-doc/config/context.html)

## 2.2 context 配置实践
### 2.2.1 理论推荐实践
目的：
- webapps下面的默认程序不自动启动
- 不在server.xml中配置context，实现独立文件配置context

`$CATALINA_HOME/conf/server.xml`
``` xml
      <Host name="localhost"  appBase=""
            unpackWARs="true" autoDeploy="false">
```
1. 修改`appBase`的值为空，或者其他目录。目的是避免加载tomcat默认的应用程序。
2. 修改`autoDeploy`为`false`，避免热加载

`$CATALINA_BASE/conf/Catalina/localhost/ROOT.xml`
``` xml
<Context path="" docBase="/root/webfile/web" debug="0" reloadable="false"/>
```
1. `path`为空，代表是默认的context。
2. `docBase`指向需要的工程路径。
3. `debug`为0，按需开启
4. `reloadable`默认即为false，代表修改工程目录中文件时，不去自动重载context，仅在重启tomcat时生效。有需要的话，可以配置为true

### 2.2.2 管理方便的实践
当然，还有另外一种官方不推荐，但是相当简便的方法，就是直接在server.xml中配置context
- host中将autoDeploy、deployOnStartup、deployXML配置为false
- context中path为空，docBase设置为真正的war包或者目录路径
> 代价仅仅为不可以热更新而已，对某些不在乎服务重启导致的中断的项目可以这样配置，便于管理

## 2.3 context 配置 sessionCookieName
### 2.3.1 sessionCookieName
The name to be used for all session cookies created for this context. If set, this overrides any name set by the web application. If not set, the value specified by the web application, if any, will be used, or the name JSESSIONID if the web application does not explicitly set one.

大意就是这个参数的设定会影响cookie的名称

### 2. 3.2 配置示例
`$CATALINA_BASE/conf/server.xml`
``` xml
<Context path="" docBase="/path/to/yourprojectfolder" debug="0" reloadable="false" sessionCookieName="yourcookieName" />
```
> 这样当你在客户端访问时，cookie的名称就会你设定的名称