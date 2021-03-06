openstack: 概览
2016年6月24日
19:06
 
什么是openstack？
openstack是一个开源的云计算平台，它通过一系列服务提供了IAAS解决方案。
 
openstack提供的服务及其简介：
ServiceProject nameDescriptionDashboardHorizonProvides a web-based self-service portal to interact with underlying OpenStack services, such as launching an instance, assigning IP addresses and configuring access controls.ComputeNovaManages the lifecycle of compute instances in an OpenStack environment. Responsibilities include spawning, scheduling and decommissioning of virtual machines on demand.NetworkingNeutronEnables Network-Connectivity-as-a-Service for other OpenStack services, such as OpenStack Compute. Provides an API for users to define networks and the attachments into them. Has a pluggable architecture that supports many popular networking vendors and technologies.Storage  Object StorageSwiftStores and retrieves arbitrary unstructured data objects via a RESTful, HTTP based API. It is highly fault tolerant with its data replication and scale-out architecture. Its implementation is not like a file server with mountable directories. In this case, it writes objects and files to multiple drives, ensuring the data is replicated across a server cluster.Block StorageCinderProvides persistent block storage to running instances. Its pluggable driver architecture facilitates the creation and management of block storage devices.Shared services  Identity serviceKeystoneProvides an authentication and authorization service for other OpenStack services. Provides a catalog of endpoints for all OpenStack services.Image serviceGlanceStores and retrieves virtual machine disk images. OpenStack Compute makes use of this during instance provisioning.TelemetryCeilometerMonitors and meters the OpenStack cloud for billing, benchmarking, scalability, and statistical purposes.Higher-level services  OrchestrationHeatOrchestrates multiple composite cloud applications by using either the native HOTtemplate format or the AWS CloudFormation template format, through both an OpenStack-native REST API and a CloudFormation-compatible Query API. 
示例架构
## 架构设计：http://docs.openstack.org/arch-design/
## 网络设计：http://docs.openstack.org/mitaka/networking-guide/
 
## 架构详解：
controller node
The controller node runs the Identity service, Image service, management portions of Compute, management portion of Networking, various Networking agents, and the dashboard. It also includes supporting services such as an SQL database, message queue, and NTP.
 
Optionally, the controller node runs portions of Block Storage, Object Storage, Orchestration, and Telemetry services.
 
The controller node requires a minimum of two network interfaces.
 
compute node
The compute node runs the hypervisor portion of Compute that operates instances. By default, Compute uses the KVM hypervisor. The compute node also runs a Networking service agent that connects instances to virtual networks and provides firewalling services to instances via security groups.
 
You can deploy more than one compute node. Each node requires a minimum of two network interfaces.
 
