ftp一键安装
2016年8月1日
16:43
 
yum install -y vsftpd
>/etc/vsftpd/vsftpd.conf
echo anonymous_enable=NO>>/etc/vsftpd/vsftpd.conf
echo local_enable=YES>>/etc/vsftpd/vsftpd.conf
echo local_umask=022>>/etc/vsftpd/vsftpd.conf
echo write_enable=YES>>/etc/vsftpd/vsftpd.conf
echo dirmessage_enable=YES>>/etc/vsftpd/vsftpd.conf
echo xferlog_enable=YES>>/etc/vsftpd/vsftpd.conf
echo connect_from_port_20=YES>>/etc/vsftpd/vsftpd.conf
echo xferlog_std_format=YES>>/etc/vsftpd/vsftpd.conf
echo listen=YES>>/etc/vsftpd/vsftpd.conf
echo pam_service_name=vsftpd>>/etc/vsftpd/vsftpd.conf
echo userlist_enable=YES>>/etc/vsftpd/vsftpd.conf
echo tcp_wrappers=YES>>/etc/vsftpd/vsftpd.conf
useradd -d /ftpuser -s /sbin/nologin ftpuser
echo 123456 | passwd ftpuser --stdin
sed -i 's/SELINUX=enforcing/SELINUX=disabled/g' /etc/selinux/config 
service iptables stop
chkconfig iptables off
service vsftpd reload
chkconfig vsftpd on
