---
title: auditd: linux 审计
date: 2021-02-01 16:26:00
categories: linux/advance
tags: [auditd]
---

### 1. 加载和管理审计规则
``` bash
cat >> /etc/audit/rules.d/audit.rules << EOF
# crontab
-w /etc/cron.d -p wa -k crontab_changes
-w /etc/cron.daily -p wa -k crontab_changes
-w /etc/cron.deny -p wa -k crontab_changes
-w /etc/cron.hourly -p wa -k crontab_changes
-w /etc/cron.monthly -p wa -k crontab_changes
-w /etc/crontab -p wa -k crontab_changes
-w /etc/cron.weekly -p wa -k crontab_changes
-w /var/spool/cron -p wa -k crontab_changes

# selinux
-w /etc/selinux/ -p wa -k selinux_changes

# kernel module
-w /sbin/insmod -p x -k module_insertion

# binary
-w /usr/bin/ -p wa -k binary_changes
-w /usr/sbin/ -p wa -k binary_changes

# ssh
-w /etc/ssh -p wa -k ssh_changes

# sudo
-w /usr/bin/sudo -p x -k sudo_executed
-w /etc/sudo.conf -p wa -k sudo_changes
-w /etc/sudoers -p wa -k sudo_changes
-w /etc/sudoers.d -p wa -k sudo_changes
-w /etc/sudo-ldap.conf -p wa -k sudo_changes

# su
-w /usr/bin/su -p x -k su_user
EOF

# 清除所有的现存规则
auditctl -D

# 加载审计规则
auditctl -R /etc/audit/rules.d/audit.rules

# 查看审计规则
auditctl -l

# 锁定audit配置，若想修改，必须重启服务器
# Make the configuration immutable -- reboot is required to change audit rules
auditctl -e 2
```

### 2. 查询审计事件
``` bash
# 查看用户变更日志
ausearch -m ADD_USER,ADD_GROUP,DEL_USER,DEL_GROUP,CHGRP_ID,CHUSER_ID -i

# 根据key查看信息
ausearch -k cutomized_key
```
``` bash
# 查看完整的message types
ausearch -m
Argument is required for -m
Valid message types are: ALL USER LOGIN USER_AUTH USER_ACCT USER_MGMT CRED_ACQ CRED_DISP USER_START USER_END USER_AVC USER_CHAUTHTOK USER_ERR CRED_REFR USYS_CONFIG USER_LOGIN USER_LOGOUT ADD_USER DEL_USER ADD_GROUP DEL_GROUP DAC_CHECK CHGRP_ID TEST TRUSTED_APP USER_SELINUX_ERR USER_CMD USER_TTY CHUSER_ID GRP_AUTH SYSTEM_BOOT SYSTEM_SHUTDOWN SYSTEM_RUNLEVEL SERVICE_START SERVICE_STOP GRP_MGMT GRP_CHAUTHTOK MAC_CHECK ACCT_LOCK ACCT_UNLOCK USER_DEVICE SOFTWARE_UPDATE DAEMON_START DAEMON_END DAEMON_ABORT DAEMON_CONFIG DAEMON_ROTATE DAEMON_RESUME DAEMON_ACCEPT DAEMON_CLOSE DAEMON_ERR SYSCALL PATH IPC SOCKETCALL CONFIG_CHANGE SOCKADDR CWD EXECVE IPC_SET_PERM MQ_OPEN MQ_SENDRECV MQ_NOTIFY MQ_GETSETATTR KERNEL_OTHER FD_PAIR OBJ_PID TTY EOE BPRM_FCAPS CAPSET MMAP NETFILTER_PKT NETFILTER_CFG SECCOMP PROCTITLE FEATURE_CHANGE KERN_MODULE FANOTIFY TIME_INJOFFSET TIME_ADJNTPVAL BPF AVC SELINUX_ERR AVC_PATH MAC_POLICY_LOAD MAC_STATUS MAC_CONFIG_CHANGE MAC_UNLBL_ALLOW MAC_CIPSOV4_ADD MAC_CIPSOV4_DEL MAC_MAP_ADD MAC_MAP_DEL MAC_IPSEC_ADDSA MAC_IPSEC_DELSA MAC_IPSEC_ADDSPD MAC_IPSEC_DELSPD MAC_IPSEC_EVENT MAC_UNLBL_STCADD MAC_UNLBL_STCDEL MAC_CALIPSO_ADD MAC_CALIPSO_DEL ANOM_PROMISCUOUS ANOM_ABEND ANOM_LINK INTEGRITY_DATA INTEGRITY_METADATA INTEGRITY_STATUS INTEGRITY_HASH INTEGRITY_PCR INTEGRITY_RULE INTEGRITY_EVM_XATTR KERNEL ANOM_LOGIN_FAILURES ANOM_LOGIN_TIME ANOM_LOGIN_SESSIONS ANOM_LOGIN_ACCT ANOM_LOGIN_LOCATION ANOM_MAX_DAC ANOM_MAX_MAC ANOM_AMTU_FAIL ANOM_RBAC_FAIL ANOM_RBAC_INTEGRITY_FAIL ANOM_CRYPTO_FAIL ANOM_ACCESS_FS ANOM_EXEC ANOM_MK_EXEC ANOM_ADD_ACCT ANOM_DEL_ACCT ANOM_MOD_ACCT ANOM_ROOT_TRANS ANOM_LOGIN_SERVICE RESP_ANOMALY RESP_ALERT RESP_KILL_PROC RESP_TERM_ACCESS RESP_ACCT_REMOTE RESP_ACCT_LOCK_TIMED RESP_ACCT_UNLOCK_TIMED RESP_ACCT_LOCK RESP_TERM_LOCK RESP_SEBOOL RESP_EXEC RESP_SINGLE RESP_HALT RESP_ORIGIN_BLOCK RESP_ORIGIN_BLOCK_TIMED USER_ROLE_CHANGE ROLE_ASSIGN ROLE_REMOVE LABEL_OVERRIDE LABEL_LEVEL_CHANGE USER_LABELED_EXPORT USER_UNLABELED_EXPORT DEV_ALLOC DEV_DEALLOC FS_RELABEL USER_MAC_POLICY_LOAD ROLE_MODIFY USER_MAC_CONFIG_CHANGE CRYPTO_TEST_USER CRYPTO_PARAM_CHANGE_USER CRYPTO_LOGIN CRYPTO_LOGOUT CRYPTO_KEY_USER CRYPTO_FAILURE_USER CRYPTO_REPLAY_USER CRYPTO_SESSION CRYPTO_IKE_SA CRYPTO_IPSEC_SA VIRT_CONTROL VIRT_RESOURCE VIRT_MACHINE_ID VIRT_INTEGRITY_CHECK VIRT_CREATE VIRT_DESTROY VIRT_MIGRATE_IN VIRT_MIGRATE_OUT 
```
> [message types(record types) list and info](https://access.redhat.com/documentation/en-us/red_hat_enterprise_linux/6/html/security_guide/sec-audit_record_types)


### 3. 实践
线上某个服务的日志文件会被定期清除，经过排查发现了两个清理脚本，不是触发条件对应不上，就是触发时间对应不上。于是使用auditd来排查

``` bash
# 启动auditd服务
systemctl start auditd

# 增加audit规则，审计one.log的write和attribute的变动
auditctl -w /path/to/one.log -p wa -k FindLogCleanProblem

# 过了一段时间，在日志文件又一次被清理之后，搜索审计日志
ausearch -i -k FindLogCleanProblem
```

> 限于环境因素，在这里不列出审计日志具体内容

通过审计日志的comm和exec，发现了是一个python脚本清理了这个文件。通过这个进一步排查，发现定时任务中有一个不易发现的python清理脚本，于是找到了问题的具体原因。

### 4. 问题
使用`systemctl`关闭auditd提示不允许手动关闭，可以用下面的命令代替
``` bash
service auditd stop
```