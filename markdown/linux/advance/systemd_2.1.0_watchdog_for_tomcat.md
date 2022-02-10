---
title: systemd 2.1.0 watchdog of systemd for tomcat
date: 2019-10-12 16:39:00
categories: linux/advance
tags: [systemd]
---

### 让我们先来启动一个简单的tomcat
只需要创建一个简单的unit file
``` bash
cat << EOF > /usr/lib/systemd/system/tomcat.service
[Unit]
Description=Apache Tomcat

[Service]
Type=forking
Environment=JAVA_HOME=/usr/local/jdk
ExecStart=/usr/local/tomcat/bin/startup.sh
ExecStop=/bin/kill -9 $MAINPID

[Install]
WantedBy=multi-user.target
EOF
```

然后启动tomcat
``` bash
systemctl daemon-reload
systemctl start tomcat
systemctl status tomcat
● tomcat.service - Apache Tomcat
   Loaded: loaded (/usr/lib/systemd/system/tomcat.service; disabled; vendor preset: disabled)
   Active: active (running) since Sat 2019-10-12 09:30:43 UTC; 6s ago
  Process: 20278 ExecStart=/usr/local/tomcat/bin/startup.sh (code=exited, status=0/SUCCESS)
 Main PID: 20286 (java)
    Tasks: 43
   Memory: 93.9M
   CGroup: /system.slice/tomcat.service
           └─20286 /usr/local/jdk/bin/java -Djava.util.logging.config.file=/u...

Oct 12 09:30:43 localhost.localdomain systemd[1]: Starting Apache Tomcat...
Oct 12 09:30:43 localhost.localdomain systemd[1]: Started Apache Tomcat.
Oct 12 09:30:43 localhost.localdomain startup.sh[20278]: Tomcat started.
```

### 如果tomcat进程死掉了怎么办？
上面我们启动了一个简单的tomcat，我们还可以在它的基础上改动一下，增加`Restart=always`到tomcat的unit文件中，这样tomcat进程如果因为任何原因停止掉，systemd会自动帮我们重新启动tomcat。

``` bash
cat << EOF > /usr/lib/systemd/system/tomcat.service
[Unit]
Description=Apache Tomcat

[Service]
Type=forking
Environment=JAVA_HOME=/usr/local/jdk
ExecStart=/usr/local/tomcat/bin/startup.sh
ExecStop=/bin/kill -9 $MAINPID
Restart=always

[Install]
WantedBy=multi-user.target
EOF
```
我们尝试用kill模拟tomcat进程死掉的情况
``` bash
systemctl status tomcat
● tomcat.service - Apache Tomcat
   Loaded: loaded (/usr/lib/systemd/system/tomcat.service; disabled; vendor preset: disabled)
   Active: active (running) since Sat 2019-10-12 09:38:32 UTC; 3s ago
  Process: 20361 ExecStart=/usr/local/tomcat/bin/startup.sh (code=exited, status=0/SUCCESS)
 Main PID: 20369 (java)
    Tasks: 43
   Memory: 61.7M
   CGroup: /system.slice/tomcat.service
           └─20369 /usr/local/jdk/bin/java -Djava.util.logging.config.file=/u...

Oct 12 09:38:32 localhost.localdomain systemd[1]: Starting Apache Tomcat...
Oct 12 09:38:32 localhost.localdomain systemd[1]: Started Apache Tomcat.
Oct 12 09:38:32 localhost.localdomain startup.sh[20361]: Tomcat started.


kill -9 20369

systemctl status tomcat
● tomcat.service - Apache Tomcat
   Loaded: loaded (/usr/lib/systemd/system/tomcat.service; disabled; vendor preset: disabled)
   Active: active (running) since Sat 2019-10-12 09:38:43 UTC; 2s ago
  Process: 20413 ExecStop=/bin/kill -9 (code=exited, status=1/FAILURE)
  Process: 20415 ExecStart=/usr/local/tomcat/bin/startup.sh (code=exited, status=0/SUCCESS)
 Main PID: 20423 (java)
    Tasks: 43
   Memory: 61.5M
   CGroup: /system.slice/tomcat.service
           └─20423 /usr/local/jdk/bin/java -Djava.util.logging.config.file=/u...

Oct 12 09:38:43 localhost.localdomain systemd[1]: tomcat.service holdoff time...
Oct 12 09:38:43 localhost.localdomain systemd[1]: Stopped Apache Tomcat.
Oct 12 09:38:43 localhost.localdomain systemd[1]: Starting Apache Tomcat...
Oct 12 09:38:43 localhost.localdomain systemd[1]: Started Apache Tomcat.
Oct 12 09:38:43 localhost.localdomain startup.sh[20415]: Tomcat started.
Hint: Some lines were ellipsized, use -l to show in full.
```

okay, 现在看起来很好，systemd帮我们启动死掉的tomcat，而不至于等我们收到报警再来手动启动它，但是这还不够完美。

### 如果tomcat不是死掉，只是卡住在那里了，怎么办？
这是一个经常遇到的问题，从运维的角度，我们不能只把原因归咎于开发者，而选择指责并袖手旁观，运维应该能够处理程序不同的异常状况的发生。那么，现在的问题是，上面我们在进程级别监控了tomcat程序，但是，怎样从服务可用性级别来监控并处理呢？

此时，如果能有一个脚本，跟随tomcat这个程序的启动而启动，通过对tomcat进行health check，如果health check失败，则帮助我们重启卡住的tomcat最好不过了。这个时候，我们需要来了解一下systemd的watchdog功能。

### 了解一下(systemd的watchdog)[http://0pointer.de/blog/projects/watchdog.html]
首先，watchdog有硬件和软件两种，我们在这里主要讨论软件这一种。另外，关于watchdog的应用对象，大概可以分为三类，嵌入式设备、桌面和服务器，这里我们主要集中探讨服务器。

首先，在讨论watchdog之前，我们要先了解一下(sd_notify)[https://www.freedesktop.org/software/systemd/man/sd_notify.html] ，sd_notify是一个c语言的程序，可以被service调用来通知service manager(例如：systemd)来更新自己的服务状态。例如，程序在自己启动完毕后，通过sd_notify来发送`READY=1`来告诉service manager自己已经启动成功，同时，还可以发送以下多个信号，**多个信号应该是一个以换行符间隔的状态列表**
```
READY=1
Tells the service manager that service startup is finished, or the service finished loading its configuration. This is only used by systemd if the service definition file has Type=notify set. Since there is little value in signaling non-readiness, the only value services should send is "READY=1" (i.e. "READY=0" is not defined).

RELOADING=1
Tells the service manager that the service is reloading its configuration. This is useful to allow the service manager to track the service's internal state, and present it to the user. Note that a service that sends this notification must also send a "READY=1" notification when it completed reloading its configuration. Reloads are propagated in the same way as they are when initiated by the user.

STOPPING=1
Tells the service manager that the service is beginning its shutdown. This is useful to allow the service manager to track the service's internal state, and present it to the user.

STATUS=…
Passes a single-line UTF-8 status string back to the service manager that describes the service state. This is free-form and can be used for various purposes: general state feedback, fsck-like programs could pass completion percentages and failing programs could pass a human-readable error message. Example: "STATUS=Completed 66% of file system check…"

ERRNO=…
If a service fails, the errno-style error code, formatted as string. Example: "ERRNO=2" for ENOENT.

BUSERROR=…
If a service fails, the D-Bus error-style error code. Example: "BUSERROR=org.freedesktop.DBus.Error.TimedOut"

MAINPID=…
The main process ID (PID) of the service, in case the service manager did not fork off the process itself. Example: "MAINPID=4711"

WATCHDOG=1
Tells the service manager to update the watchdog timestamp. This is the keep-alive ping that services need to issue in regular intervals if WatchdogSec= is enabled for it. See systemd.service(5) for information how to enable this functionality and sd_watchdog_enabled(3) for the details of how the service can check whether the watchdog is enabled.

WATCHDOG=trigger
Tells the service manager that the service detected an internal error that should be handled by the configured watchdog options. This will trigger the same behaviour as if WatchdogSec= is enabled and the service did not send "WATCHDOG=1" in time. Note that WatchdogSec= does not need to be enabled for "WATCHDOG=trigger" to trigger the watchdog action. See systemd.service(5) for information about the watchdog behavior.

WATCHDOG_USEC=…
Reset watchdog_usec value during runtime. Notice that this is not available when using sd_event_set_watchdog() or sd_watchdog_enabled(). Example : "WATCHDOG_USEC=20000000"
```
在上面的信号列表里面(信号列表不止上面列举的这些，可以是任意变量和变量内容)，我们发现了例如重载、停止、watchdog信号等内容，这为我们手动来控制服务的状态提供了扩展的可能。

当然，实现sd_notify来控制服务运行状态监护逻辑最好方式，是直接在自己的程序里面集成sd_notify。像go和python都已经有了基于sd_notify的实现，如果自己使用的语言没有这方面的实现，自己也可以去实现一下，因为编程语言基本上都有socket通信的功能的，获取系统的变量`NOTIFY_SOCKET`，然后基于内容创建socket连接，给这个socket连接发送和sd_notify一致的状态即可实现和sd_notify一样的功能。
```
$NOTIFY_SOCKET
Set by the service manager for supervised processes for status and start-up completion notification. This environment variable specifies the socket sd_notify() talks to. See above for details.
```

另外，除了以上在服务的代码层面集成服务的运行状态监护逻辑之外，我们总会遇到一些，程序无法修改，或者开发对这个不感兴趣等情况，有没有一种可以不侵入代码，就能够实现服务运行状态监控逻辑的方法呢？

### 使用一个脚本或者程序容器来实现watchdog的功能吧！
当然是有方法的，这就是将watchdog(脚本或者程序)和服务一起启动，在watchdog里面实现服务运行状态的监控逻辑。

在本文的场景下，我们集中讨论一下tomcat这个程序，所以下面都是以tomcat当做通用的服务来举例。

首先，我们需要在systemd中运行两个程序，一个是tomcat，一个是watchdog，而且这两个程序都是长时间运行的。systemd里面可以执行启动程序的参数有以下几个
- ExecStartPre
- ExecStartPost
- ExecStart

因为只有ExecStart参数执行的程序才是可以长时间运行的，其他两个参数执行的服务不可以长时间执行，否则程序的启动会卡住。所以我们只能将服务和watchdog的启动逻辑合并在一起，在一个“容器”脚本或者程序里面顺序启动tomcat和watchdog。

如果要使用脚本，那么就要提到systemd-notify，这个二进制工具，是systemd提供的一个对sd_notify的wraper，是便于脚本编写的一个工具，使用方法很简单: 
``` bash
systemd-notify -h
systemd-notify [OPTIONS...] [VARIABLE=VALUE...]

Notify the init system about service status updates.

  -h --help            Show this help
     --version         Show package version
     --ready           Inform the init system about service start-up completion
     --pid[=PID]       Set main pid of daemon
     --status=TEXT     Set status text
     --booted          Check if the system was booted up with systemd
     --readahead=ACTION Controls read-ahead operations
```

基于systemd-notify所以就有了下面这个脚本的实现
``` bash
#!/bin/bash
#set -e -x

CURL_TMP_RESULT=/tmp/curl_result.txt

WATCHED_IP=127.0.0.1
WATCHED_PORT=8080
WATCHED_NET=$WATCHED_IP:$WATCHED_PORT
CATALINA_BASE=/usr/local/tomcat

trap "rm -f ${CURL_TMP_RESULT}" EXIT

getPidByPort() {
    pid_raw=`ss -lnpt|grep ":$WATCHED_PORT "|awk '{print $6}'|awk -F "pid=" '{print $2}'|awk -F "," '{print $1}'`

    [[ -n $pid_raw ]] && {
        space_regex=".* .*"
        if [[ $pid_raw =~ $space_regex ]] ; then
            pid=`echo $pid_raw|awk '{print $1}'`
        else
            pid=$pid_raw
        fi
    }
}

healthCheck() {
    # limit whole check time in 8 seconds and connect time in 2 seconds
    curl -s --connect-timeout 2 --max-time 8 -o $CURL_TMP_RESULT $WATCHED_NET && HEALTH_STATUS="success" || HEALTH_STATUS="fail"
}

watchdogTomcat() {
    # INITIAL OF WATCHDOG
    # go to watchdog logic when conditions down satisfied
    #   - pid exist
    #   - first health check status success
    while : ; do
        [[ -n $pid ]] && {
            healthCheck
            [[ $HEALTH_STATUS -eq "success" ]] && {
                echo "healthCheck >>> notify systemd READY=1" # debug
                systemd-notify --pid=$pid --ready
                break
            }
        } || {
            getPidByPort
            #echo "getPidByPort >>> PID_RAW=$pid_raw PID:$pid"             # debug
        }
    done

    # WATCHDOG START
    while : ; do
        interval=$(($WATCHDOG_USEC / $((2 * 1000000))))

        healthCheck

        if [[ $HEALTH_STATUS -eq "success" ]] ; then
            #echo "watchdog detect success" # debug
            systemd-notify --pid=$pid WATCHDOG=1
            sleep ${interval}
        else
            #echo "watchdog detect failed" # debug
            sleep 1
        fi
    done
}


${CATALINA_BASE}/bin/catalina.sh start
watchdogTomcat &
```

``` bash
echo '[Unit]
Description=watchdog test
 
[Service]
Type=forking
Environment=JAVA_HOME=/usr/local/jdk
#Environment=CATALINA_PID=/usr/local/tomcat/bin/catalina.pid
#PIDFile=/usr/local/tomcat/bin/catalina.pid
ExecStart=/usr/local/bin/watchdog-tomcat
ExecStop=/bin/kill -9 $MAINPID
WatchdogSec=30
NotifyAccess=all
Restart=always
RestartSec=5s
TimeoutStartSec=2min
 
[Install]
WantedBy=multi-user.target' > /usr/lib/systemd/system/watchdog-tomcat.service
```

> 源码见: https://github.com/xiaotuanyu120/systemd-watchdog-tomcat