Verify operation
2016年6月28日
16:07
 
## 在controller node上执行检查操作
 
# . admin-openrc
# neutron ext-list
+---------------------------+-----------------------------------------------+
| alias                     | name                                          |
+---------------------------+-----------------------------------------------+
| default-subnetpools       | Default Subnetpools                           |
| network-ip-availability   | Network IP Availability                       |
| network_availability_zone | Network Availability Zone                     |
| auto-allocated-topology   | Auto Allocated Topology Services              |
| ext-gw-mode               | Neutron L3 Configurable external gateway mode |
| binding                   | Port Binding                                  |
| agent                     | agent                                         |
| subnet_allocation         | Subnet Allocation                             |
| l3_agent_scheduler        | L3 Agent Scheduler                            |
| tag                       | Tag support                                   |
| external-net              | Neutron external network                      |
| net-mtu                   | Network MTU                                   |
| availability_zone         | Availability Zone                             |
| quotas                    | Quota management support                      |
| l3-ha                     | HA Router extension                           |
| provider                  | Provider Network                              |
| multi-provider            | Multi Provider Network                        |
| address-scope             | Address scope                                 |
| extraroute                | Neutron Extra Route                           |
| timestamp_core            | Time Stamp Fields addition for core resources |
| router                    | Neutron L3 Router                             |
| extra_dhcp_opt            | Neutron Extra DHCP opts                       |
| dns-integration           | DNS Integration                               |
| security-group            | security-group                                |
| dhcp_agent_scheduler      | DHCP Agent Scheduler                          |
| router_availability_zone  | Router Availability Zone                      |
| rbac-policies             | RBAC Policies                                 |
| standard-attr-description | standard-attr-description                     |
| port-security             | Port Security                                 |
| allowed-address-pairs     | Allowed Address Pairs                         |
| dvr                       | Distributed Virtual Router                    |
+---------------------------+-----------------------------------------------+
## 有报警
WARNING neutron.db.agentschedulers_db [req-88f8a44f-781d-4755-8b02-316d56d4ca05 - - - - -] No DHCP agents available, skipping rescheduling
 
# neutron agent-list
+--------------------------------------+--------------------+------------+-------------------+-------+----------------+---------------------------+
| id                                   | agent_type         | host       | availability_zone | alive | admin_state_up | binary                    |
+--------------------------------------+--------------------+------------+-------------------+-------+----------------+---------------------------+
| 19050fae-b667-48cd-abbc-14c29795d4a2 | Linux bridge agent | controller |                   | :-)   | True           | neutron-linuxbridge-agent |
| 3bed2a4f-1074-4706-ba8a-03ee4393f777 | Linux bridge agent | compute1   |                   | :-)   | True           | neutron-linuxbridge-agent |
| 901fcd7a-1369-42dc-983b-89aa1e980ced | L3 agent           | controller | nova              | :-)   | True           | neutron-l3-agent          |
| 9d629b67-a6d2-4c5a-9c6d-e55ff5637ace | Metadata agent     | controller |                   | :-)   | True           | neutron-metadata-agent    |
| f1146562-e9f5-4c47-9dbb-8d961a7636cb | DHCP agent         | controller | nova              | :-)   | True           | neutron-dhcp-agent        |
+--------------------------------------+--------------------+------------+-------------------+-------+----------------+---------------------------+

 
