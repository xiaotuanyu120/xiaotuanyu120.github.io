Install and configure compute node
2016年6月28日
14:59
 
Install the components
===========================================
# yum install openstack-neutron-linuxbridge ebtables ipset -y 
Configure the common component
===========================================
# vim /etc/neutron/neutron.conf
*******************************************
[DEFAULT]
rpc_backend = rabbit
auth_strategy = keystone
 
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
 
[oslo_concurrency]
lock_path = /var/lib/neutron/tmp
 
******************************************* 
Configure the Linux bridge agent
=========================================
# vim /etc/neutron/plugins/ml2/linuxbridge_agent.ini
******************************************
[linux_bridge]
physical_interface_mappings = provider:eno16777736
 
[vxlan]
enable_vxlan = True
local_ip = 10.0.0.13
l2_population = True
 
[securitygroup]
enable_security_group = True
firewall_driver = neutron.agent.linux.iptables_firewall.IptablesFirewallDriver
 
****************************************** 
Configure Compute to use Networking
=======================================
# vim /etc/nova/nova.conf
******************************************
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
****************************************** 
Finalize installation
=======================================
# systemctl restart openstack-nova-compute.service
## 启动错误，记得关闭防火墙
 
# systemctl enable neutron-linuxbridge-agent.service
# systemctl start neutron-linuxbridge-agent.service
