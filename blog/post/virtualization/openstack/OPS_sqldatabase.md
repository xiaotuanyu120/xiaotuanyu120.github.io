OPS: sql database
2016年4月7日
14:14
 
http://docs.openstack.org/mitaka/install-guide-rdo/keystone-install.html 
 
SQL DATABASE(controller节点)
======================================================
# yum install mariadb mariadb-server MySQL-python
# vim /etc/my.cnf.d/mariadb_openstack.cnf
*************************************
[mysqld]
bind-address = 10.10.222.3
default-storage-engine = innodb
innodb_file_per_table
collation-server = utf8_general_ci
init-connect = 'SET NAMES utf8'
character-set-server = utf8
*************************************
# systemctl enable mariadb.service
# systemctl start mariadb.service
# mysql_secure_installation
