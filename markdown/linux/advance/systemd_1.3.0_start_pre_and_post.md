---
title: systemd 1.3.0 exec pre and post
date: 2019-10-02 12:47:00
categories: linux/advance
tags: [systemd]
---

### 1. manual for systemd unit files
``` bash
man systemd.service
```

### 2. systemd exec pre and post
下面的内容来自于systemd.service的manual
```
       ExecStart=
           Commands with their arguments that are executed when this service is started. The value is split into zero or more command lines is according to the rules described below (see section
           "Command Lines" below).

           When Type is not oneshot, only one command may and must be given. When Type=oneshot is used, zero or more commands may be specified. This can be specified by providing multiple command lines
           in the same directive, or alternatively, this directive may be specified more than once with the same effect. If the empty string is assigned to this option, the list of commands to start is
           reset, prior assignments of this option will have no effect. If no ExecStart= is specified, then the service must have RemainAfterExit=yes set.

           For each of the specified commands, the first argument must be an absolute path to an executable. Optionally, if this file name is prefixed with "@", the second token will be passed as
           "argv[0]" to the executed process, followed by the further arguments specified. If the absolute filename is prefixed with "-", an exit code of the command normally considered a failure (i.e.
           non-zero exit status or abnormal exit due to signal) is ignored and considered success. If both "-" and "@" are used, they can appear in either order.

           If more than one command is specified, the commands are invoked sequentially in the order they appear in the unit file. If one of the commands fails (and is not prefixed with "-"), other
           lines are not executed, and the unit is considered failed.

           Unless Type=forking is set, the process started via this command line will be considered the main process of the daemon.

       ExecStartPre=, ExecStartPost=
           Additional commands that are executed before or after the command in ExecStart=, respectively. Syntax is the same as for ExecStart=, except that multiple command lines are allowed and the
           commands are executed one after the other, serially.

           If any of those commands (not prefixed with "-") fail, the rest are not executed and the unit is considered failed.

           Note that ExecStartPre= may not be used to start long-running processes. All processes forked off by processes invoked via ExecStartPre= will be killed before the next service process is
           run.

       ExecStopPost=
           Additional commands that are executed after the service was stopped. This includes cases where the commands configured in ExecStop= were used, where the service does not have any ExecStop=
           defined, or where the service exited unexpectedly. This argument takes multiple command lines, following the same scheme as described for ExecStart. Use of these settings is optional.
           Specifier and environment variable substitution is supported.
```
> 重点需要注意：
1. ExecStartPost里面的命令如果以`-`开头，代表执行成功与否，systemd都会当做它执行成功了。
2. ExecStartPost等命令，都可以配置多个，按照上下顺序执行
3. ExecStart系列的命令，先执行ExecStartPre，然后是ExecStart，然后是ExecStartPost，命令中没有以`-`起头的，一个失败，其他的就不会再执行，而且会导致service进入failed状态