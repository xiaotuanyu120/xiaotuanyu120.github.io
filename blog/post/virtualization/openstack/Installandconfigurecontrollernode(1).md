Install and configure controller node
2016年6月26日
13:10
 
Prerequisites
==========================================
## 数据库准备
# mysql -u root -p
CREATE DATABASE neutron;
GRANT ALL PRIVILEGES ON neutron.* TO 'neutron'@'localhost' IDENTIFIED BY 'neutron.passwd';
GRANT ALL PRIVILEGES ON neutron.* TO 'neutron'@'%' IDENTIFIED BY 'neutron.passwd';
flush privileges;
 
# . admin-openrc
 
## 创建neutron user和添加entity
# openstack user create --domain default --password-prompt neutron
User Password:
Repeat User Password:
+-----------+----------------------------------+
| Field     | Value                            |
+-----------+----------------------------------+
| domain_id | 6c4295d7e7ba49c3b59118a3ced5328a |
| enabled   | True                             |
| id        | daf8821f14e244c1b866ad9d6a91ad24 |
| name      | neutron                          |
+-----------+----------------------------------+
## 密码是neutron.keystone
 
# openstack role add --project service --user neutron admin
 
# openstack service create --name neutron --description "OpenStack Networking" network
+-------------+----------------------------------+
| Field       | Value                            |
+-------------+----------------------------------+
| description | OpenStack Networking             |
| enabled     | True                             |
| id          | 264b32525964444a8e674ca94be6d891 |
| name        | neutron                          |
| type        | network                          |
+-------------+----------------------------------+
 
## Create the Networking service API endpoints:
# openstack endpoint create --region RegionOne network public http://controller:9696
+--------------+----------------------------------+
| Field        | Value                            |
+--------------+----------------------------------+
| enabled      | True                             |
| id           | bebaf9415baf469a9bcc4d5a88966bcd |
| interface    | public                           |
| region       | RegionOne                        |
| region_id    | RegionOne                        |
| service_id   | 264b32525964444a8e674ca94be6d891 |
| service_name | neutron                          |
| service_type | network                          |
| url          | http://controller:9696           |
+--------------+----------------------------------+
 
# openstack endpoint create --region RegionOne network internal http://controller:9696
+--------------+----------------------------------+
| Field        | Value                            |
+--------------+----------------------------------+
| enabled      | True                             |
| id           | b5d61568665d46079c8967b2c3bb73ee |
| interface    | internal                         |
| region       | RegionOne                        |
| region_id    | RegionOne                        |
| service_id   | 264b32525964444a8e674ca94be6d891 |
| service_name | neutron                          |
| service_type | network                          |
| url          | http://controller:9696           |
+--------------+----------------------------------+
 
# openstack endpoint create --region RegionOne network admin http://controller:9696
+--------------+----------------------------------+
| Field        | Value                            |
+--------------+----------------------------------+
| enabled      | True                             |
| id           | a2e914b157a445b8a017d5b0f43e1809 |
| interface    | admin                            |
| region       | RegionOne                        |
| region_id    | RegionOne                        |
| service_id   | 264b32525964444a8e674ca94be6d891 |
| service_name | neutron                          |
| service_type | network                          |
| url          | http://controller:9696           |
+--------------+----------------------------------+
  
Configure networking options
==========================================
## 这里有两种选择，一种是简单的只是提供网络接入，另外一种可以提供众多网络自定义功能，后者复杂，但功能强，这里选择后者。
 
Install the components
# yum install openstack-neutron openstack-neutron-ml2 openstack-neutron-linuxbridge ebtables -y
 
## Configure the server component
# vim /etc/neutron/neutron.conf
****************************************
[database]
connection = mysql+pymysql://neutron:neutron.passwd@controller/neutron
 
[DEFAULT]
core_plugin = ml2
service_plugins = router
allow_overlapping_ips = True
rpc_backend = rabbit
auth_strategy = keystone
notify_nova_on_port_status_changes = True
notify_nova_on_port_data_changes = True
 
[oslo_messaging_rabbit]
rabbit_host = controller
rabbit_userid = openstack
rabbit_password = rabbitmq.passwd
 
[keystone_authtoken]
auth_uri = http://controller:5000
auth_url = http://controller:35357
memcached_servers = controller:11211
auth_type = password
project_domain_name = default
user_domain_name = default
project_name = service
username = neutron
password = neutron.keystone
 
[nova]
auth_url = http://controller:35357
auth_type = password
project_domain_name = default
user_domain_name = default
region_name = RegionOne
project_name = service
username = nova
password = nova.keystone
 
[oslo_concurrency]
lock_path = /var/lib/neutron/tmp
****************************************
 
## Configure the Modular Layer 2 (ML2) plug-in
# vim /etc/neutron/plugins/ml2/ml2_conf.ini
****************************************
[ml2]
type_drivers = flat,vlan,vxlan
tenant_network_types = vxlan
mechanism_drivers = linuxbridge,l2population
extension_drivers = port_security
 
[ml2_type_flat]
flat_networks = provider
 
[ml2_type_vxlan]
vni_ranges = 1:1000
 
[securitygroup]
enable_ipset = True
****************************************
 
## Configure the Linux bridge agent
# vim /etc/neutron/plugins/ml2/linuxbridge_agent.ini
****************************************
## 这里配置你希望用哪个网卡做桥接
[linux_bridge]
physical_interface_mappings = provider:eno16777736
 
[vxlan]
enable_vxlan = True
local_ip = 10.0.0.12
l2_population = True
 
[securitygroup]
enable_security_group = True
firewall_driver = neutron.agent.linux.iptables_firewall.IptablesFirewallDriver
****************************************
 
## Configure the layer-3 agent
# vim /etc/neutron/l3_agent.ini
****************************************
[DEFAULT]
interface_driver = neutron.agent.linux.interface.BridgeInterfaceDriver
external_network_bridge =
****************************************
 
## Configure the DHCP agent
# vim /etc/neutron/dhcp_agent.ini
****************************************
[DEFAULT]
interface_driver = neutron.agent.linux.interface.BridgeInterfaceDriver
dhcp_driver = neutron.agent.linux.dhcp.Dnsmasq
enable_isolated_metadata = True
**************************************** 
Configure the metadata agent
==========================================
# vim /etc/neutron/metadata_agent.ini
**************************************
[DEFAULT]
nova_metadata_ip = controller
metadata_proxy_shared_secret = metadata.secret
************************************** 
Configure Compute to use Networking
==========================================
# vim /etc/nova/nova.conf
**************************************
[neutron]
url = http://controller:9696
auth_url = http://controller:35357
auth_type = password
project_domain_name = default
user_domain_name = default
region_name = RegionOne
project_name = service
username = neutron
password = neutron.keystone
 
service_metadata_proxy = True
metadata_proxy_shared_secret = metadata.secret
************************************** 
 
Finalize installation
==========================================
## The Networking service initialization scripts expect a symbolic link /etc/neutron/plugin.ini pointing to the ML2 plug-in configuration file, /etc/neutron/plugins/ml2/ml2_conf.ini. If this symbolic link does not exist, create it using the following command:
# ln -s /etc/neutron/plugins/ml2/ml2_conf.ini /etc/neutron/plugin.ini
 
## Populate the database:
# su -s /bin/sh -c "neutron-db-manage --config-file /etc/neutron/neutron.conf  --config-file /etc/neutron/plugins/ml2/ml2_conf.ini upgrade head" neutron
 
## Restart the Compute API service:
# systemctl restart openstack-nova-api.service
 
## Start the Networking services and configure them to start when the system boots.For both networking options:
# systemctl enable neutron-server.service   neutron-linuxbridge-agent.service neutron-dhcp-agent.service   neutron-metadata-agent.service
 
# systemctl start neutron-server.service \
  neutron-linuxbridge-agent.service neutron-dhcp-agent.service \
  neutron-metadata-agent.service
 
# systemctl enable neutron-l3-agent.service
# systemctl start neutron-l3-agent.service
 
 
 
## 错误
错误描述：
当启动neutron-server的时候，
/var/log/neutron/server.log报错
2016-06-28 09:56:56.537 9547 ERROR oslo.messaging._drivers.impl_rabbit [req-0b607df4-1d12-4feb-95a7-47d07edcd854 - - - - -] AMQP server controller:5672 closed the connection. Check login credentials: Socket closed
2016-06-28 09:57:00.534 9547 ERROR oslo.messaging._drivers.impl_rabbit [req-0b607df4-1d12-4feb-95a7-47d07edcd854 - - - - -] AMQP server controller:5672 closed the connection. Check login credentials: Socket closed
2016-06-28 09:57:05.518 9547 ERROR oslo.messaging._drivers.impl_rabbit [req-0b607df4-1d12-4feb-95a7-47d07edcd854 - - - - -] AMQP server controller:5672 closed the connection. Check login credentials: Socket closed
2016-06-28 09:57:12.512 9547 ERROR oslo.messaging._drivers.impl_rabbit [req-0b607df4-1d12-4feb-95a7-47d07edcd854 - - - - -] AMQP server controller:5672 closed the connection. Check login credentials: Socket closed
2016-06-28 09:57:21.500 9547 ERROR oslo.messaging._drivers.impl_rabbit [req-0b607df4-1d12-4feb-95a7-47d07edcd854 - - - - -] AMQP server controller:5672 closed the connection. Check login credentials: Socket closed
2016-06-28 09:57:32.492 9547 ERROR oslo.messaging._drivers.impl_rabbit [req-0b607df4-1d12-4feb-95a7-47d07edcd854 - - - - -] AMQP server controller:5672 closed the connection. Check login credentials: Socket closed
2016-06-28 09:57:38.866 9547 WARNING neutron.db.agentschedulers_db [req-6c6f9bc5-2be6-4c71-8c6b-c5fabf5051bf - - - - -] No DHCP agents available, skipping rescheduling
 
/var/log/rabbitmq/rabbit@controller.log报错
=INFO REPORT==== 28-Jun-2016::10:06:16 ===
accepting AMQP connection <0.761.0> (10.0.0.12:39484 -> 10.0.0.12:5672)
 
=INFO REPORT==== 28-Jun-2016::10:06:16 ===
accepting AMQP connection <0.764.0> (10.0.0.12:39486 -> 10.0.0.12:5672)
 
=ERROR REPORT==== 28-Jun-2016::10:06:16 ===
Error on AMQP connection <0.761.0> (10.0.0.12:39484 -> 10.0.0.12:5672, state: starting):
AMQPLAIN login refused: user 'openstack' - invalid credentials
 
=ERROR REPORT==== 28-Jun-2016::10:06:16 ===
Error on AMQP connection <0.764.0> (10.0.0.12:39486 -> 10.0.0.12:5672, state: starting):
AMQPLAIN login refused: user 'openstack' - invalid credentials
 
 
/var/log/messages报错
Jun 28 10:02:43 controller neutron-server: Guru mediation now registers SIGUSR1 and SIGUSR2 by default for backward compatibility. SIGUSR1 will no longer be registered in a future release, so please use SIGUSR2 to generate reports.
Jun 28 10:02:46 controller neutron-server: Option "verbose" from group "DEFAULT" is deprecated for removal.  Its value may be silently ignored in the future.
Jun 28 10:02:47 controller neutron-server: Option "notification_driver" from group "DEFAULT" is deprecated. Use option "driver" from group "oslo_messaging_notifications".
Jun 28 10:04:11 controller systemd: neutron-server.service start operation timed out. Terminating.
Jun 28 10:04:11 controller systemd: Failed to start OpenStack Neutron Server.
Jun 28 10:04:11 controller systemd: Unit neutron-server.service entered failed state.
Jun 28 10:04:11 controller systemd: neutron-server.service failed.
 
## 从报错上看，是neutron启动的时候通过slo.messaging._drivers.impl_rabbit去连接rabbitmq的时候报错，字面上看是用户或密码错误
 
解决方案：
hostname检查
rabbitmqctl list_users
增加用户，赋值权限 
