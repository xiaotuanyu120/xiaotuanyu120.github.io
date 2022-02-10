---
title: selinux 1.0.1 enable selinux from disabled status
date: 2021-01-31 17:28:00
categories: linux/advance
tags: [selinux]
---

### 1. enable selinux on systems that previously had it disabled
#### step 1 change it to permissive
``` bash
sed -i "s/^SELINUX=disabled.*$/SELINUX=permissive/g" /etc/selinux/config

reboot
```

#### step 2 check selinux denial message
详情看下面的参考链接，基本上如果机器是新安装的，用以下三个命令检查出来没有denied信息，就可以继续下一步了
```
ausearch -m AVC,USER_AVC,SELINUX_ERR,USER_SELINUX_ERR -ts recent
journalctl -t setroubleshoot
dmesg | grep -i -e type=1300 -e type=1400
```
> [redhat access: identify selinux denials troubleshooting problem](https://access.redhat.com/documentation/en-us/red_hat_enterprise_linux/8/html/using_selinux/troubleshooting-problems-related-to-selinux_using-selinux#identifying-selinux-denials_troubleshooting-problems-related-to-selinux)

#### step 3 change it to enforcing
``` bash
sed -i "s/^SELINUX=permissive.*$/SELINUX=permissive/g" /etc/selinux/config

reboot
```

> [redhat access: enable selinux on systems that previously had it disabled](https://access.redhat.com/documentation/en-us/red_hat_enterprise_linux/8/html/using_selinux/changing-selinux-states-and-modes_using-selinux#enabling-selinux-on-systems-that-previously-had-it-disabled_changing-selinux-states-and-modes)