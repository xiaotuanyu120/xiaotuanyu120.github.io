---
title: 2.2.3 Dockerfile entrypoint with script
date: 2018-12-09 14:19:00
categories: virtualization/docker
tags: [docker, entrypoint]
---

### 0. 问题背景
某天有其他项目组来问我，`docker run`启动没问题，但是换成`docker-compose`启动后，一直是显示restarting状态咋办。

因为我一直有以下的docker运行个人习惯：
- 使用offical原生镜像
- 每个镜像里面只运行一个服务

所以一直没遇到过这个怪问题。后来经过一段时间的面向google运维找到了问题的答案。

参考文档：
- [stackoverflow - 关于在docker entrypoint脚本中使用exec的回答](https://stackoverflow.com/questions/32255814/what-purpose-does-using-exec-in-docker-entrypoint-scripts-serve)
- [docker docs - 关于docker entrypoint脚本的详细说明](https://docs.docker.com/develop/develop-images/dockerfile_best-practices/#entrypoint)
- [bash - exec的详细文档](http://wiki.bash-hackers.org/commands/builtin/exec)

### 1. entrypoint使用脚本的时候，用docker-compose启动一直处在restarting的状态？
通常用`docker run `命令启动容器时，为了同时启动多个服务或者执行多个操作，会设定entrypoint为一个脚本。

而使用脚本启动会遇到一个问题，那就是脚本执行完毕后，容器会进入exit状态。此时有人可能会采用下面的方法来解决
```
#!/bin/bash

set -e

# 其他逻辑信息，此处忽略

/usr/local/apache-tomcat-8.5.35/bin/catalina.sh start
/bin/bash
```
这样使用最后一句`/bin/bash`，相当于把这个脚本hold住，让它不停止，则这个容器就会一直处于一个运行状态。然而这样真的完美吗？答案是否定的。
> 无语，竟然有人想到用sleep 30000d来解决，只能说世界之大，无奇不有啊

实际测试了一下，结果竟然真的复现了上面说到的情况，使用`docker run`启动没问题，但是换成`docker-compose`启动后，一直是显示restarting状态。

而查看`docker-compose`启动后的容器日志，是一直循环在输出程序启动的日志，于是问题肯定出现在，这个脚本最后的`/bin/bash`并没有起到把这个脚本hold住的效果。

原来，docker官方已经给这个问题提出过解决方案，详细内容可以参考[docker docs - 关于docker entrypoint脚本的详细说明](https://docs.docker.com/develop/develop-images/dockerfile_best-practices/#entrypoint)。以下是个人总结的entrypoint使用脚本时的几个要点：
- 通过在脚本中使用`exec <cmd>`取代直接执行`<cmd>`的方式，让`<cmd>`来取代被执行的脚本，而不是另外生成一个新的进程。
- 这个`<cmd>`不能是后台执行的语句，只能是前台执行的语句，才能保证容器持续运行

下面这个要点看情况使用，并不是必须的
- 脚本最后添加`exec "$@"`语句来重定向脚本执行的参数到脚本内部，其实就是把`<entrypoint> <cmd>`中的`<cmd>`传递到`<entrypoint>`脚本中。

根据entrypoint使用脚本时的要点，上面的脚本存在几个问题：
- 使用`catalina.sh start`，这样启动是后台启动。需要变更成`catalina.sh run`这样前台启动的方式
- `/bin/bash`去掉，通过给`catalina.sh run`前面增加`exec`的方式来让`catalina.sh run`成为真正控制docker容器生命周期的命令。
> 为了增强entrypoint的灵活性（entrypoint就是因为能接收参数的灵活性，才在已经有cmd的情况下还有生存空间），可以将run赋值给entrypoint的默认参数`cmd`

同上修正上面的问题，得到正确的entrypoint脚本：
```
#!/bin/bash

set -e

# 其他逻辑信息，此处忽略

exec /usr/local/apache-tomcat-8.5.35/bin/catalina.sh "$@"

exec "$@"
```

而Dockerfile内容为：
```
...其他内容省略...

ENTRYPOINT ["/bin/entrypoint.sh"]
CMD ["run"]
```
> 通过将`run` 传递到`/bin/entrypoint.sh`中，得到真正决定docker生命周期的命令为`/usr/local/apache-tomcat-8.5.35/bin/catalina.sh run`