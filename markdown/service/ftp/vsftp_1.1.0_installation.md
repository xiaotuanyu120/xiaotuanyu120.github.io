---
title: vsftp 1.1.0: vsftp 安装
date: 2015-01-22 02:54:00
categories: service/ftp
tags: [ftp,vsftp]
---

### 1. 安装vsftp
``` bash
yum install -y vsftpd db4-utils
```

### 2. 准备vsftp使用的用户及密码文件
``` bash
useradd vsftpd-u -s /sbin/nologin

cat << EOF > /etc/vsftpd/vsftpd_login
ftpa1                     #奇数行为用户名
*passwd1*                 #偶数行为密码
ftpa2
*passwd2*
EOF

#保证安全性，设为只有root可读写
chmod 600 /etc/vsftpd/vsftpd_login
```

### 3. db_load命令来创建密码库文件
``` bash
db_load -T -t hash -f /etc/vsftpd/vsftpd_login /etc/vsftpd/vsftpd_login.db
# db_load工具是由db4-utils提供的
# -T参数，让db_load将文本文件转换为db文件
# -t参数，指定db库文件类型，此处指定为hash（哈希）
# -f参数，指定input文件
# 语法：db_load -T -t <库类型> -f <input file> <output file>

rm -rf /etc/vsftpd/vsftpd_login
# 保证安全性，设为只有root可读写
chmod 600 /etc/vsftpd/vsftpd_login.db
```

### 4. 配置/etc/pam.d/vsftpd和/etc/vsftpd/vsftpd.conf（全局设定）
``` bash
vi /etc/pam.d/vsftpd
## 将下面两行添加到最开头
## 64系统是lib64，32位系统是lib
# auth sufficient /lib64/security/pam_userdb.so db=/etc/vsftpd/vsftpd_login
# account sufficient /lib64/security/pam_userdb.so db=/etc/vsftpd/vsftpd_login
# ......

vi /etc/vsftpd/vsftpd.conf
## 修改原内容
# anonymous_enable=NO
# anon_upload_enable=NO
# anon_mkdir_write_enable=NO
## 增加新内容
# chroot_local_user=YES
# guest_enable=YES
# guest_username=vsftpd-u
# virtual_use_local_privs=YES
# user_config_dir=/etc/vsftpd/vsftpd_user_conf
```

### 5. 建立虚拟账户目录及独立配置文件（独立设定）
``` bash
mkdir /etc/vsftpd/vsftpd_user_conf
cd /etc/vsftpd/vsftpd_user_conf/
cat << EOF > ftpa1
local_root=/home/vsftpd-u/ftpa1
anonymous_enable=NO
write_enable=YES
local_umask=022
anon_upload_enable=NO
anon_mkdir_write_enable=NO
idle_session_timeout=600
data_connection_timeout=120
max_clients=10
max_per_ip=5
local_max_rate=50000
EOF

chown -R vsftpd-u:vsftpd-u /home/vsftpd-u
```

### 6. Selinux 和 防火墙
selinux
``` bash
setsebool -P allow_ftpd_full_access 1
# 如果未关闭selinux而且未设置ftp的访问权限，会报错500 oops cannot change directory
```

Iptables
- passive mode添加iptables规则的方法
- vsftpd配置被动模式的端口范围
`/etc/vsftpd/vsftpd.conf`
```
listen_port=3721
pasv_enable=YES
pasv_min_port=3722
pasv_max_port=3999
port_enable=YES
```

# iptables根据配置放行端口
``` bash
-A INPUT -p tcp -m state --state NEW -m tcp --dport 3721 -j ACCEPT
-A INPUT -p tcp -m state --state NEW -m tcp --dport 3722:3999 -j ACCEPT
```

### 7. 启动vsftpd服务
``` bash
service vsftpd start
```
