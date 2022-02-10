---
title: vsftp: 1.1.1 安装(centos6)
date: 2015-11-04 14:24:00
categories: service/ftp
tags: [ftp,vsftp]
---

### 0. 安装环境
OS：Centos 6 x64位
网段：172.168.2.x/24
 
### 1. 安装过程
``` bash
yum install -y vsftpd db4-utils
chkconfig --level 35 vsftpd on

# 增加vsftpd服务的用户
useradd vsftpd-u -s /sbin/nologin

# 准备虚拟用户账号密码文件
cat << EOF > /etc/vsftpd/vsftpd_userlist
ftp1
ftpuser01
ftp2
ftpuser02
ftp3
ftpuser03
ftp4
ftpuser04
EOF
# userlist语法：奇数行是username；偶数行是password
chmod 600 /etc/vsftpd/vsftpd_userlist
 
# 用db-utils加密userlist
db_load -T -t hash -f /etc/vsftpd/vsftpd_userlist /etc/vsftpd/vsftpd_userlist.db
# db_load 语法
# db_load [-nTV] [-c name=value] [-f file] 
# [-h home] [-P password] [-t btree | hash | recno | queue] db_file
# db_load -r lsn | fileid [-h home] [-P password] db_file
chmod 600 /etc/vsftpd/vsftpd_userlist.db
```

### 2. Configuration
``` bash
# 配置认证文件位置
vim /etc/pam.d/vsftpd
# 在最开头添加
# auth       sufficient   /lib64/security/pam_userdb.so db=/etc/vsftpd/vsftpd_userlist
# account    sufficient   /lib64/security/pam_userdb.so db=/etc/vsftpd/vsftpd_userlist
 
# 配置vsftpd全局配置
vim /etc/vsftpd/vsftpd.conf
## 修改以下几行
# anonymous_enable=NO
# anon_upload_enable=NO
# anon_mkdir_write_enable=NO
# chroot_local_user=YES
## 添加以下几行
# guest_enable=YES
# guest_username=vsftpd-u
# virtual_use_local_privs=YES
# user_config_dir=/etc/vsftpd/vsftpd_user_conf

mkdir /etc/vsftpd/vsftpd_user_conf
 
# 配置虚拟用户
vim /etc/vsftpd/vsftpd_user_conf/ftp1
# local_root=/home/vsftpd-u/ftp1
# anonymous_enable=NO
# write_enable=YES
# local_umask=022
# anon_upload_enable=NO
# anon_mkdir_write_enable=NO
# idle_session_timeout=600
# data_connection_timeout=120
# max_clients=10
# max_per_ip=5
# local_max_rate=50000

# 创建虚拟用户目录
mkdir /home/vsftpd-u/ftp1
chown -R vsftpd-u:vsftpd-u /home/vsftpd-u/ftp1
 
# 重启服务
service vsftpd restart
 
# selinux放行
setsebool -P allow_ftpd_full_access 1
# 如果未关闭selinux而且未设置ftp的访问权限，会报错500 oops cannot change directory
 
# iptables放行
# passive mode添加iptables规则的方法
# vsftpd配置被动模式的端口范围
vim /etc/vsftpd/vsftpd.conf
# listen_port=3721
# pasv_enable=YES
# pasv_min_port=3722
# pasv_max_port=3999
# port_enable=YES

# iptables根据配置放行端口
vim /etc/sysconfig/iptables
## 添加以下两行
# -A INPUT -p tcp -m state --state NEW -m tcp --dport 3721 -j ACCEPT
# -A INPUT -p tcp -m state --state NEW -m tcp --dport 3722:3999 -j ACCEPT

# 重启vsftpd和防火墙
service vsftpd restart
service iptables restart 
```