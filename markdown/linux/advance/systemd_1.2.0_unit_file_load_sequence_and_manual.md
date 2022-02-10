---
title: systemd 1.2.0 unit file load sequence and manual
date: 2018-10-17 09:31:00
categories: linux/advance
tags: [systemd,manual]
---

### 1. manual for systemd unit files
``` bash
man systemd.unit
```

### 2. systemd unit file load sequence
下面的内容来自于systemd.unit的manual
```
UNIT LOAD PATH
       Unit files are loaded from a set of paths determined during compilation, described in the two tables below. Unit files found in directories listed earlier
       override files with the same name in directories lower in the list.

       Table 1.  Load path when running in system mode (--system).
       ┌────────────────────────┬─────────────────────────────┐
       │Path                    │ Description                 │
       ├────────────────────────┼─────────────────────────────┤
       │/etc/systemd/system     │ Local configuration         │
       ├────────────────────────┼─────────────────────────────┤
       │/run/systemd/system     │ Runtime units               │
       ├────────────────────────┼─────────────────────────────┤
       │/usr/lib/systemd/system │ Units of installed packages │
       └────────────────────────┴─────────────────────────────┘

       Additional units might be loaded into systemd ("linked") from directories not on the unit load path. See the link command for systemctl(1). Also, some units
       are dynamically created via a systemd.generator(7).
```
> 重点需要注意：
1. unit files配置在三个目录中
2. unit files和iptables的规则差不多，是从（表中）上到下，遇到的第一个unit file生效。
3. unit files可以是一个其他非表中目录的文件的链接（链接文件必须在表中的目录中）

### 3. unit files覆盖配置
可以在上面三个unit files目录中(推荐/etc/systemd/system)创建`<unitfile_name>.d/*.conf`，里面写上包含覆盖或增加内容的conf文件。daemon-reload后，使用`systemctl cat <service_name>`来查看
``` bash
systemctl cat docker.service
# /usr/lib/systemd/system/docker.service
[Unit]
Description=Docker Application Container Engine
Documentation=https://docs.docker.com
BindsTo=containerd.service
After=network-online.target firewalld.service
Wants=network-online.target
Requires=docker.socket

[Service]
Type=notify
# the default is not to use systemd for cgroups because the delegate issues still
# exists and systemd currently does not support the cgroup feature set required
# for containers run by docker
ExecStart=/usr/bin/dockerd -H fd://
ExecReload=/bin/kill -s HUP $MAINPID
TimeoutSec=0
RestartSec=2
Restart=always

# Note that StartLimit* options were moved from "Service" to "Unit" in systemd 229.
# Both the old, and new location are accepted by systemd 229 and up, so using the old location
# to make them work for either version of systemd.
StartLimitBurst=3

# Note that StartLimitInterval was renamed to StartLimitIntervalSec in systemd 230.
# Both the old, and new name are accepted by systemd 230 and up, so using the old name to make
# this option work for either version of systemd.
StartLimitInterval=60s

# Having non-zero Limit*s causes performance problems due to accounting overhead
# in the kernel. We recommend using cgroups to do container-local accounting.
LimitNOFILE=infinity
LimitNPROC=infinity
LimitCORE=infinity

# Comment TasksMax if your systemd version does not supports it.
# Only systemd 226 and above support this option.
TasksMax=infinity

# set delegate yes so that systemd does not reset the cgroups of docker containers
Delegate=yes

# kill only the docker process, not all processes in the cgroup
KillMode=process

[Install]
WantedBy=multi-user.target

# /etc/systemd/system/docker.service.d/network.conf
[Service]
ExecStartPost=-/usr/bin/docker network create --driver=bridge --subnet=172.30.1.0/24 --ip-range=172.30.1.0/24 --gateway=172.30.1.254 net1
ExecStartPost=-/usr/bin/docker network create --driver=bridge --subnet=172.30.2.0/24 --ip-range=172.30.2.0/24 --gateway=172.30.2.254 net2
```
> 扩展命令
> - `systemctl cat <service_name>`，查看配置文件内容
> - `systemctl show <service_name>`，查看实际生效的内容