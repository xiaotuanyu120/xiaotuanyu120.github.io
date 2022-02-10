---
title: kubernetes v1.17 1.1.0 kubernetes集群安装(生产环境)
date: 2019-12-24 09:55:00
categories: virtualization/container
tags: [container,docker,kubernetes,flannel]
---

## 本文档背景介绍

### 1. 参照文档
kubernetes的官方文档，目前官方维护的最老的1.13的版本里面，也已经无法找到当时我在1.9里面参照的`Creating a Custom Cluster from Scratch`那篇文档了，基本上能看出来趋势是希望采用kubeadm这个工具来初始化集群。但是其实二进制模式的安装还是可行，而且个人意见：二进制安装能增强维护人员对k8s集群的细节了解程度，并且能在解决安装时遇到各种问题的情况下增加对k8s管理知识的了解。

关于文档，主体流程和重点部分可以参照 [kubeadm 实施流程文档](https://kubernetes.io/docs/reference/setup-tools/kubeadm/implementation-details/)

### 2. 软件版本

| items      | version    |
| ---------- | ---------- |
| OS         | centos7    |
| kubernetes | 1.17       |
| docker     | 19.03.5-ce |
| etcd       | v3.3.18    |

### 3. 节点规划

| 角色            | ip address    | 服务                                                              | comment             |
| --------------- | ------------- | ----------------------------------------------------------------- | ------------------- |
| master01,etcd01 | 192.168.33.101| kube-apiserver,kube-controller-manager,kube-scheduler,etcd,docker | 主节点01,etcd节点01 |
| master02,etcd02 | 192.168.33.102| kube-apiserver,kube-controller-manager,kube-scheduler,etcd,docker | 主节点02,etcd节点02 |
| master03,etcd03 | 192.168.33.103| kube-apiserver,kube-controller-manager,kube-scheduler,etcd,docker | 主节点03,etcd节点03 |
| node01          | 192.168.33.104| kubelet,kube-proxy,docker                                         | node节点01          |
| node02          | 192.168.33.105| kubelet,kube-proxy,docker                                         | node节点02          |
| node03          | 192.168.33.106| kubelet,kube-proxy,docker                                         | node节点03          |

### 4. 网络规划

| 名称    | 网段范围        |
| ------- | --------------- |
| pod     | 10.5.0.0/16     |
| service | 10.254.0.0/16   |
| 宿主机  | 192.168.33.0/24 |

---

## 宿主机环境准备(所有节点)

### 1. 准备系统环境
``` bash
# 安装必要的工具包
yum install -y wget vim

# 确保mac地址和product_uuid不重复
# 查看mac地址
ip link
# 查看uuid
cat /sys/class/dmi/id/product_uuid

# nftables驱动的防火墙管理工具和kube-proxy不兼容，所以需要换回老版本的iptables
systemctl stop firewalld
systemctl disable firewalld
systemctl mask firewalld
yum install -y iptables iptables-services
systemctl disable iptables
systemctl stop iptables
# 安装期间临时关闭防火墙，正式运行需开放api等服务的端口

# 关闭selinux  
sed -i "s/SELINUX=enforcing/SELINUX=disabled/g" /etc/selinux/config
setenforce 0

# 设定hostname到hosts文件中
cat << EOF >> /etc/hosts
192.168.33.101 master01
192.168.33.102 master02
192.168.33.103 master03
192.168.33.101 etcd01
192.168.33.102 etcd02
192.168.33.103 etcd03
192.168.33.104 node01
192.168.33.105 node02
192.168.33.106 node03
EOF

# 关闭系统swap  
swapoff -a
# 注释swap的开机挂载项，修改/etc/fstab
sed -ri "s|(^ ?+\/.*swap.*$)|#\1|g" /etc/fstab
# 关闭系统swap，是为了严格的按照cpu和内存的限制，这样scheduler在规划pod的时候就不会把pod放进swap中了，这是为了性能考虑。

# 加载内核模块br_netfilter
lsmod | grep br_netfilter
[ $? -eq 0 ] || modprobe br_netfilter

# 优化系统内核
cat << EOF >  /etc/sysctl.d/k8s.conf
net.bridge.bridge-nf-call-ip6tables = 1
net.bridge.bridge-nf-call-iptables = 1
EOF
sysctl --system
```

---

## 安装runtime(所有节点)
参照 [docker installation on centos 7](/virtualization/docker/docker_1.1.0_installation_centos7.html) 这篇文档来安装

> 重点关注：
> - 使用overlay2存储驱动
> - 使用systemd替代cgroupfs作为cgroup管理器

---

## 准备环境变量
``` bash
# 各角色ip变量
declare -A IP_LIST
IP_LIST=(
[master01]="192.168.33.101" \
[master02]="192.168.33.102" \
[master03]="192.168.33.103" \
[etcd01]="192.168.33.101" \
[etcd02]="192.168.33.102" \
[etcd03]="192.168.33.103" \
[node01]="192.168.33.104" \
[node02]="192.168.33.105" \
[node03]="192.168.33.106")
KUBE_API_PROXY_IP=192.168.33.101

# 安装环境变量
DEPLOY_DIR=/root/k8s
K8S_VER=v1.17.0
ETCD_VER=v3.3.18

# 证书环境变量
K8S_PKI_DIR=/etc/kubernetes/pki
ETCD_PKI_DIR=/etc/etcd/pki
ADMIN_KUBECONFIG_DIR=/root/.kube
KUBECONFIG_DIR=/etc/kubernetes/kubeconfig

# IP配置变量
SERVICE_CLUSTER_IP_RANGE=10.254.0.0/16
SERVICE_NODE_PORT_RANGE=30000-32767
POD_CLUSTER_IP_RANGE=10.5.0.0/16
```
---

## 给kube-apiserver创建一个负载均衡
这里我选择了master01机器上来部署高可用服务，当然你可以选择任意你希望部署的一台机器。
``` bash
DOCKER_YML_DIR=/data/docker/yml
DOCKER_RUNTIME_DIR=/data/docker/runtime

mkdir -p ${DOCKER_YML_DIR}
cat << EOF > ${DOCKER_YML_DIR}/docker-compose-haproxy.yml
version: '3'
services:
  haproxy:
    container_name: haproxy-kube-apiserver
    image: haproxy
    ports:
      - 443:6443
    volumes:
      - /data/docker/runtime/haproxy/etc/haproxy.cfg:/usr/local/etc/haproxy/haproxy.cfg
EOF

mkdir -p ${DOCKER_RUNTIME_DIR}/haproxy/etc
cat << EOF > ${DOCKER_RUNTIME_DIR}/haproxy/etc/haproxy.cfg
frontend k8s-api
  bind 0.0.0.0:6443
  mode tcp
  option tcplog
  timeout client 1h
  default_backend k8s-api

backend k8s-api
  mode tcp
  timeout server 1h
  option tcplog
  option tcp-check
  balance roundrobin
  default-server inter 10s downinter 5s rise 2 fall 2 slowstart 60s maxconn 250 maxqueue 256 weight 100
  server k8s-api-1 ${IP_LIST["master01"]}:6443 check
  server k8s-api-2 ${IP_LIST["master02"]}:6443 check
  server k8s-api-3 ${IP_LIST["master03"]}:6443 check
EOF

docker-compose -f /data/docker/yml/docker-compose-haproxy.yml up -d
```

---

## 准备 k8s、etcd二进制文件
master01上准备二进制文件，统一下发给所有其他机器，所以提前做好ssh信任
### 0. 准备各节点二进制文件目录
``` bash
mkdir -p ${DEPLOY_DIR}/{node,master,etcd,cni}/bin
```

### 1. 下载二进制文件
``` bash
cd ${DEPLOY_DIR}
# 下载kubernetes
wget https://dl.k8s.io/${K8S_VER}/kubernetes-server-linux-amd64.tar.gz -O ${DEPLOY_DIR}/kubernetes-server-linux-amd64.tar.gz
tar zxvf kubernetes-server-linux-amd64.tar.gz
cp ${DEPLOY_DIR}/kubernetes/server/bin/{kube-apiserver,kube-scheduler,kube-controller-manager,kubectl} ${DEPLOY_DIR}/master/bin
cp ${DEPLOY_DIR}/kubernetes/server/bin/{kubelet,kube-proxy} ${DEPLOY_DIR}/node/bin

# 下载etcd
curl -L https://github.com/coreos/etcd/releases/download/${ETCD_VER}/etcd-${ETCD_VER}-linux-amd64.tar.gz \
  -o etcd-${ETCD_VER}-linux-amd64.tar.gz
tar xzvf etcd-${ETCD_VER}-linux-amd64.tar.gz
cp etcd-${ETCD_VER}-linux-amd64/{etcd,etcdctl} ${DEPLOY_DIR}/etcd/bin/

# 下载cni
wget https://github.com/containernetworking/plugins/releases/download/v0.8.4/cni-plugins-linux-amd64-v0.8.4.tgz
tar zxvf cni-plugins-linux-amd64-v0.8.4.tgz -C ${DEPLOY_DIR}/cni/bin/
```
> [flannel cni issue: 890 about cni binary not found error](https://github.com/coreos/flannel/issues/890)

### 2. 分发二进制文件
``` bash
chmod +x ${DEPLOY_DIR}/etcd/bin/*
chmod +x ${DEPLOY_DIR}/node/bin/*
chmod +x ${DEPLOY_DIR}/master/bin/*

# 下发master二进制文件
for master in {master01,master02,master03};do
  rsync -av ${DEPLOY_DIR}/master/bin/* ${master}:/usr/local/bin/
done

# 下发node二进制文件
for node in {node01,node02,node03};do
  rsync -av ${DEPLOY_DIR}/node/bin/* ${node}:/usr/local/bin/
done

# 下发etcd二进制文件
for etcd in {etcd01,etcd02,etcd03};do
  rsync -av ${DEPLOY_DIR}/etcd/bin/* ${etcd}:/usr/local/bin/
done

# 下发cni二进制文件
for node in {node01,node02,node03};do
  ssh root@${node} "mkdir -p /opt/cni/bin"
  rsync -av ${DEPLOY_DIR}/cni/bin/* ${node}:/opt/cni/bin
done
```

---

## 生成k8s集群认证文件
### 0. 生成k8s集群中的证书之前
创建认证文件之前，墙裂推荐阅读[apiserver authentication documentation](https://kubernetes.io/docs/reference/access-authn-authz/authentication/#x509-client-certs)。

里面重点提到了：
- 证书中的CN(common name)，被用作request的用户名
- 从k8s 1.4开始，证书中的organization被用作用户组（可多个）

这里是一个证书CSR的示例，可以通过CSR来设定CN和O
``` json
{
  "CN": "kubernetes",
  "key": {
    "algo": "rsa",
    "size": 2048
  },
  "names":[{
    "C": "<country>",
    "ST": "<state>",
    "L": "<city>",
    "O": "<organization>",
    "OU": "<organization unit>"
  }]
}
```

### 1. 安装cfssl
``` bash
curl -s -L -o /usr/local/bin/cfssl https://github.com/cloudflare/cfssl/releases/download/v1.4.1/cfssl_1.4.1_linux_amd64
curl -s -L -o /usr/local/bin/cfssljson https://github.com/cloudflare/cfssl/releases/download/v1.4.1/cfssljson_1.4.1_linux_amd64
curl -s -L -o /usr/local/bin/cfssl-certinfo https://github.com/cloudflare/cfssl/releases/download/v1.4.1/cfssl-certinfo_1.4.1_linux_amd64
chmod +x /usr/local/bin/*
export PATH=$PATH:/usr/local/bin

# 创建k8s-ssl目录
mkdir -p ${DEPLOY_DIR}/pki/{etcd,kubernetes}
# 此目录只是临时存放ca生成文件，可随意更换位置
```
> 因为[issues 717: 错误提示hosts缺失问题](https://github.com/cloudflare/cfssl/issues/717)，这里和官方文档不一样，从1.2升级到了1.4.1

### 2. 创建 etcd 认证文件
#### 1) 准备配置文件
``` bash
cd ${DEPLOY_DIR}/pki/etcd

# step 1. 创建根CA
# 创建 ETCD CA 证书签名请求文件
cat > ca-csr.json << EOF
{
  "CN": "etcd.local",
  "key": {
    "algo": "rsa",
    "size": 4096
  },
  "names": [
    {
      "C": "CN",
      "ST": "BeiJing",
      "L": "BeiJing",
      "O": "kubernetes",
      "OU": "System"
    }
  ]
}
EOF

# step 2. 签名证书
# 创建CA签名配置文件
# [issue]: 因为etcd开启--client-cert-auth选项，导致需要给serverde profile (client auth) 权限
# [issue-url]: https://github.com/etcd-io/etcd/issues/9785
cat > ca-config.json <<EOF
{
  "signing": {
    "default": {
      "expiry": "87600h"
    },
    "profiles": {
      "server": {
        "usages": [
            "signing",
            "key encipherment",
            "server auth",
            "client auth"
        ],
        "expiry": "87600h"
      },
      "client": {
        "usages": [
            "signing",
            "key encipherment",
            "client auth"
        ],
        "expiry": "87600h"
      },
      "peer": {
        "usages": [
            "signing",
            "key encipherment",
            "server auth",
            "client auth"
        ],
        "expiry": "87600h"
      }
    }
  }
}
EOF

# step 3. 创建"证书签名请求"文件
# server限定etcd所有节点监听ip
cat > server-csr.json << EOF
{
    "CN": "server",
    "hosts": [
      "127.0.0.1",
      "${IP_LIST['etcd01']}",
      "${IP_LIST['etcd02']}",
      "${IP_LIST['etcd03']}"
    ],
    "key": {
        "algo": "rsa",
        "size": 2048
    },
    "names": [
        {
            "C": "CN",
            "ST": "BeiJing",
            "L": "BeiJing",
            "O": "kubernetes",
            "OU": "System"
        }
    ]
}
EOF

# client不限定签名ip
cat > client-csr.json << EOF
{
    "CN": "client",
    "hosts": [""],
    "key": {
        "algo": "rsa",
        "size": 2048
    },
    "names": [
        {
            "C": "CN",
            "ST": "BeiJing",
            "L": "BeiJing",
            "O": "system:masters",
            "OU": "System"
        }
    ]
}
EOF

# peer限定签名etcd所有节点的通信ip
cat > peer-csr.json << EOF
{
    "CN": "peer",
    "hosts": [
      "${IP_LIST['etcd01']}",
      "${IP_LIST['etcd02']}",
      "${IP_LIST['etcd03']}"
    ],
    "key": {
        "algo": "rsa",
        "size": 2048
    },
    "names": [
        {
            "C": "CN",
            "ST": "BeiJing",
            "L": "BeiJing",
            "O": "kubernetes",
            "OU": "System"
        }
    ]
}
EOF
```

#### 2) 生成证书
``` bash
# step 1. 生成 CA 证书和私钥
cfssl gencert -initca ca-csr.json | cfssljson -bare ca
# 生成文件：ca-key.pem ca.csr ca.pem

# step 2. 生成应CSR文件请求，使用CA签名过的证书
cfssl gencert -ca=ca.pem -ca-key=ca-key.pem -config=ca-config.json -profile=server server-csr.json | cfssljson -bare server
# 生成文件：server-key.pem server.csr server.pem

cfssl gencert -ca=ca.pem -ca-key=ca-key.pem -config=ca-config.json -profile=client client-csr.json | cfssljson -bare client
# 生成文件：client-key.pem client.csr client.pem

cfssl gencert -ca=ca.pem -ca-key=ca-key.pem -config=ca-config.json -profile=peer peer-csr.json | cfssljson -bare peer
# 生成文件：peer-key.pem peer.csr peer.pem
```


### 3. 创建 k8s master节点 认证文件
#### 1) 准备配置文件
``` bash
cd ${DEPLOY_DIR}/pki/kubernetes

# step 1. 创建根CA
# 创建 K8S CA 证书签名请求文件
cat > ${DEPLOY_DIR}/pki/kubernetes/ca-csr.json << EOF
{
  "CN": "kubernetes",
  "key": {
    "algo": "rsa",
    "size": 4096
  },
  "names": [
    {
      "C": "CN",
      "ST": "BeiJing",
      "L": "BeiJing",
      "O": "kubernetes",
      "OU": "System"
    }
  ]
}
EOF

# step 2. 签名证书
# 创建CA签名配置文件
cat > ${DEPLOY_DIR}/pki/kubernetes/ca-config.json <<EOF
{
  "signing": {
    "default": {
      "expiry": "87600h"
    },
    "profiles": {
      "server": {
        "usages": [
            "signing",
            "key encipherment",
            "server auth",
            "client auth"
        ],
        "expiry": "87600h"
      },
      "client": {
        "usages": [
            "signing",
            "key encipherment",
            "client auth"
        ],
        "expiry": "87600h"
      }
    }
  }
}
EOF

# step 3. 创建"证书签名请求"文件

# kube-apiserver
# hosts内容：
#   - HA所有监听ip、vip
#   - --apiserver-advertise-address指定的ip
#   - service网段第一个ip
#   - k8s DNS域名
#   - master节点名称
cat > ${DEPLOY_DIR}/pki/kubernetes/kube-apiserver-csr.json << EOF
{
    "CN": "kubernetes",
    "hosts": [
      "127.0.0.1",
      "${IP_LIST['master01']}",
      "${IP_LIST['master02']}",
      "${IP_LIST['master03']}",
      "${SERVICE_CLUSTER_IP_RANGE%.*}.1",
      "kubernetes",
      "kubernetes.default",
      "kubernetes.default.svc",
      "kubernetes.default.svc.cluster",
      "kubernetes.default.svc.cluster.local"
    ],
    "key": {
        "algo": "rsa",
        "size": 2048
    },
    "names": [
        {
            "C": "CN",
            "ST": "BeiJing",
            "L": "BeiJing",
            "O": "kubernetes",
            "OU": "System"
        }
    ]
}
EOF

# api-kubelet-client
cat > ${DEPLOY_DIR}/pki/kubernetes/api-kubelet-client.json << EOF
{
  "CN": "system:kubelet-api-admin",
  "hosts": [
    "127.0.0.1",
    "node01",
    "node02",
    "node03",
    "${IP_LIST['master01']}",
    "${IP_LIST['master02']}",
    "${IP_LIST['master03']}",
    "${IP_LIST['node01']}",
    "${IP_LIST['node02']}",
    "${IP_LIST['node03']}"
  ],
  "key": {
    "algo": "rsa",
    "size": 2048
  },
  "names": [
    {
      "C": "CN",
      "ST": "BeiJing",
      "L": "BeiJing",
      "O": "system:kubelet-api-admin",
      "OU": "System"
    }
  ]
}
EOF

# kube-controller-manager
# 注意点：
# - CN名称必须是： system:kube-controller-manager
cat > ${DEPLOY_DIR}/pki/kubernetes/kube-controller-manager-csr.json << EOF
{
  "CN": "system:kube-controller-manager",
  "hosts": [
    "127.0.0.1",
    "${IP_LIST['master01']}",
    "${IP_LIST['master02']}",
    "${IP_LIST['master03']}"
  ],
  "key": {
    "algo": "rsa",
    "size": 2048
  },
  "names": [
    {
      "C": "CN",
      "ST": "BeiJing",
      "L": "BeiJing",
      "O": "system:kube-controller-manager",
      "OU": "System"
    }
  ]
}
EOF

# kube-scheduler
cat > ${DEPLOY_DIR}/pki/kubernetes/kube-scheduler-csr.json << EOF
{
  "CN": "system:kube-scheduler",
  "hosts": [
    "127.0.0.1",
    "${IP_LIST['master01']}",
    "${IP_LIST['master02']}",
    "${IP_LIST['master03']}"
  ],
  "key": {
    "algo": "rsa",
    "size": 2048
  },
  "names": [
    {
      "C": "CN",
      "ST": "BeiJing",
      "L": "BeiJing",
      "O": "system:kube-scheduler",
      "OU": "System"
    }
  ]
}
EOF

# kube-proxy
cat > ${DEPLOY_DIR}/pki/kubernetes/kube-proxy-csr.json << EOF
{
  "CN": "system:kube-proxy",
  "hosts": [""],
  "key": {
    "algo": "rsa",
    "size": 2048
  },
  "names": [
    {
      "C": "CN",
      "ST": "BeiJing",
      "L": "BeiJing",
      "O": "system:node-proxier",
      "OU": "System"
    }
  ]
}
EOF
```
> [注：详情可以参照k8s证书官方文档](https://kubernetes.io/docs/concepts/cluster-administration/certificates/)  

#### 2) 生成证书
``` bash
# step 1. 生成 CA 证书和私钥
cfssl gencert -initca ca-csr.json | cfssljson -bare ca
# 生成文件： ca-key.pem ca.csr ca.pem

# step 2. 生成应CSR文件请求，使用CA签名过的证书
cfssl gencert -ca=ca.pem -ca-key=ca-key.pem -config=ca-config.json -profile=server kube-apiserver-csr.json | cfssljson -bare kube-apiserver
# 生成文件： kube-apiserver-key.pem kube-apiserver.csr kube-apiserver.pem

cfssl gencert -ca=ca.pem -ca-key=ca-key.pem -config=ca-config.json -profile=server api-kubelet-client.json | cfssljson -bare api-kubelet-client
# 生成文件： api-kubelet-client-key.pem api-kubelet-client.csr api-kubelet-client.pem

cfssl gencert -ca=ca.pem -ca-key=ca-key.pem -config=ca-config.json -profile=client kube-controller-manager-csr.json | cfssljson -bare kube-controller-manager
# 生成文件： kube-controller-manager-key.pem kube-controller-manager.csr kube-controller-manager.pem

cfssl gencert -ca=ca.pem -ca-key=ca-key.pem -config=ca-config.json -profile=client kube-scheduler-csr.json | cfssljson -bare kube-scheduler
# 生成文件： kube-scheduler-key.pem kube-scheduler.csr kube-scheduler.pem

cfssl gencert -ca=ca.pem -ca-key=ca-key.pem -config=ca-config.json -profile=client  kube-proxy-csr.json | cfssljson -bare kube-proxy
# 生成文件：kube-proxy-key.pem kube-proxy.csr kube-proxy.pem
```

### 4. 创建 admin 认证文件
``` bash
cd ${DEPLOY_DIR}/pki/kubernetes

# step 1. 创建"证书签名请求"文件
cat > admin-csr.json << EOF
{
  "CN": "admin",
  "hosts": [""],
  "key": {
    "algo": "rsa",
    "size": 2048
  },
  "names": [
    {
      "C": "CN",
      "ST": "BeiJing",
      "L": "BeiJing",
      "O": "system:masters",
      "OU": "System"
    }
  ]
}
EOF

# step 2. 生成应CSR文件请求，使用CA签名过的证书
cfssl gencert -ca=ca.pem -ca-key=ca-key.pem -config=ca-config.json -profile=client admin-csr.json | cfssljson -bare admin
# 生成文件：admin-key.pem admin.csr admin.pem
```

### 5. 校验证书方法
``` bash
cfssl-certinfo -cert server.pem
```

### 6. 分发证书
``` bash
# 下发证书到master
# 证书对象
# - 根证书
# - 管理员证书
# - apiserver证书
# - apiserver-etcd-client证书
for master in {master01,master02,master03};do
  ssh root@${master} "mkdir -p ${K8S_PKI_DIR}"
  ssh root@${master} "mkdir -p ${ETCD_PKI_DIR}"
  scp ${DEPLOY_DIR}/pki/kubernetes/{ca.pem,ca-key.pem,admin.pem,admin-key.pem} ${master}:${K8S_PKI_DIR}
  scp ${DEPLOY_DIR}/pki/kubernetes/kube-apiserver.pem ${master}:${K8S_PKI_DIR}/kube-apiserver.pem
  scp ${DEPLOY_DIR}/pki/kubernetes/kube-apiserver-key.pem ${master}:${K8S_PKI_DIR}/kube-apiserver-key.pem
  scp ${DEPLOY_DIR}/pki/kubernetes/api-kubelet-client.pem ${master}:${K8S_PKI_DIR}/api-kubelet-client.pem
  scp ${DEPLOY_DIR}/pki/kubernetes/api-kubelet-client-key.pem ${master}:${K8S_PKI_DIR}/api-kubelet-client-key.pem
  scp ${DEPLOY_DIR}/pki/etcd/ca.pem ${master}:${ETCD_PKI_DIR}
  scp ${DEPLOY_DIR}/pki/etcd/client.pem ${master}:${K8S_PKI_DIR}/apiserver-etcd-client.pem
  scp ${DEPLOY_DIR}/pki/etcd/client-key.pem ${master}:${K8S_PKI_DIR}/apiserver-etcd-client-key.pem
done

# 下发证书到node
for node in {node01,node02,node03};do
  ssh root@${node} "mkdir -p ${K8S_PKI_DIR}"
  scp ${DEPLOY_DIR}/pki/kubernetes/{ca.pem,api-kubelet-client.pem,api-kubelet-client-key.pem} ${node}:${K8S_PKI_DIR}
done
# 用于加密master和node通信，kubelet中需要提供ca.pem来认证，主要用于kubectl logs/exec

# 下发证书到etcd
for etcd in {etcd01,etcd02,etcd03};do
  ssh root@${etcd} "mkdir -p ${ETCD_PKI_DIR}"
  scp ${DEPLOY_DIR}/pki/etcd/{ca.pem,server.pem,server-key.pem,peer.pem,peer-key.pem} ${etcd}:${ETCD_PKI_DIR}
done
```

---

## 生成kubeconfig
参照文档： [kubernetes in hard way about kubeconfig](https://github.com/kelseyhightower/kubernetes-the-hard-way/blob/master/docs/05-kubernetes-configuration-files.md)
``` bash
# 创建k8s-config目录
mkdir -p ${DEPLOY_DIR}/kubeconfig
```

### 1. 创建 kubelet kubeconfig 文件
``` bash
cd ${DEPLOY_DIR}/kubeconfig
export KUBE_APISERVER="https://${KUBE_API_PROXY_IP}:443"

# step 1. 创建 bootstrap token file
# Token 可以是任意的包涵128 bit的字符串，可以使用安全的随机数发生器生成。
export BOOTSTRAP_TOKEN=$(head -c 16 /dev/urandom | od -An -t x | tr -d ' ')
cat > ${DEPLOY_DIR}/kubeconfig/token.csv <<EOF
${BOOTSTRAP_TOKEN},kubelet-bootstrap,10001,"system:bootstrappers"
EOF
# 注意： 在进行后续操作前请检查 token.csv 文件，确认其中的 ${BOOTSTRAP_TOKEN} 环境变量已经被真实的值替换。
cat ${DEPLOY_DIR}/kubeconfig/token.csv 
# 输出类似这种值： 31c5af9c14a8f8ddbed6564234b2644f,kubelet-bootstrap,10001,"system:bootstrappers"

# step 2. 生成 kubeconfig 和 设置 current context
# 注意点： credential必须是，用户组system:node和hostname小写化后的拼接
for node in {node01,node02,node03};do
  kubectl config set-cluster kubernetes \
    --certificate-authority=${DEPLOY_DIR}/pki/kubernetes/ca.pem \
    --embed-certs=true \
    --server=${KUBE_APISERVER} \
    --kubeconfig=bootstrap-kubelet-${node}.conf

  kubectl config set-credentials system:node:${node} \
    --token=${BOOTSTRAP_TOKEN} \
    --kubeconfig=bootstrap-kubelet-${node}.conf

  kubectl config set-context default \
    --cluster=kubernetes \
    --user=system:node:${node} \
    --kubeconfig=bootstrap-kubelet-${node}.conf

  kubectl config use-context default --kubeconfig=bootstrap-kubelet-${node}.conf
done
# 依次执行了以下步骤：
# 生成文件： bootstrap-kubelet-${node}.conf，内容为集群信息（证书、apiserver地址、集群名称）
# 修改文件： bootstrap-kubelet-${node}.conf，增加token等认证信息
# 修改文件： bootstrap-kubelet-${node}.conf，增加context信息
# 修改文件： bootstrap-kubelet-${node}.conf，设定当前context为default
```

### 2. 创建 kube-proxy kubeconfig 文件
``` bash
export KUBE_APISERVER="https://${KUBE_API_PROXY_IP}:443"

# step 1. 生成 kubeconfig
kubectl config set-cluster kubernetes \
  --certificate-authority=${DEPLOY_DIR}/pki/kubernetes/ca.pem \
  --embed-certs=true \
  --server=${KUBE_APISERVER} \
  --kubeconfig=kube-proxy.conf
# 生成文件： kube-proxy.conf，内容为集群信息（证书、apiserver地址、集群名称）

kubectl config set-credentials system:kube-proxy \
  --client-certificate=${DEPLOY_DIR}/pki/kubernetes/kube-proxy.pem \
  --client-key=${DEPLOY_DIR}/pki/kubernetes/kube-proxy-key.pem \
  --embed-certs=true \
  --kubeconfig=kube-proxy.conf
# 修改文件： kube-proxy.conf，增加认证用户和认证信息

kubectl config set-context default \
  --cluster=kubernetes \
  --user=system:kube-proxy \
  --kubeconfig=kube-proxy.conf
# 修改文件： kube-proxy.conf，增加context信息

# 设置 current context
kubectl config use-context default --kubeconfig=kube-proxy.conf
# 修改文件： kube-proxy.conf，设定当前context为default
```

### 3. 创建 admin kubeconfig 文件
``` bash
# step 1. 生成 kubeconfig
kubectl config set-cluster kubernetes \
  --certificate-authority=${DEPLOY_DIR}/pki/kubernetes/ca.pem \
  --embed-certs=true \
  --server=${KUBE_APISERVER} \
  --kubeconfig=admin.conf
# 生成文件： admin.conf，内容为集群信息（证书、apiserver地址、集群名称）

kubectl config set-credentials admin \
  --client-certificate=${DEPLOY_DIR}/pki/kubernetes/admin.pem \
  --embed-certs=true \
  --client-key=${DEPLOY_DIR}/pki/kubernetes/admin-key.pem \
  --kubeconfig=admin.conf
# 修改文件： admin.conf，增加认证用户和认证信息

kubectl config set-context kubernetes \
  --cluster=kubernetes \
  --user=admin \
  --kubeconfig=admin.conf
# 修改文件： admin.conf，增加context信息

# 设定上下文
kubectl config use-context kubernetes --kubeconfig=admin.conf
# 修改文件： admin.conf，设定当前context为kubernetes
```

### 4. 创建 kube-controller-manager kubeconfig 文件
``` bash
for master in {master01,master02,master03};do
kubectl config set-cluster kubernetes \
  --certificate-authority=${DEPLOY_DIR}/pki/kubernetes/ca.pem \
  --embed-certs=true \
  --server=https://${IP_LIST[${master}]}:6443 \
  --kubeconfig=kube-controller-manager-${master}.conf

# 注意点： credential必须是system:kube-controller-manager
kubectl config set-credentials system:kube-controller-manager \
  --client-certificate=${DEPLOY_DIR}/pki/kubernetes/kube-controller-manager.pem \
  --client-key=${DEPLOY_DIR}/pki/kubernetes/kube-controller-manager-key.pem \
  --embed-certs=true \
  --kubeconfig=kube-controller-manager-${master}.conf

kubectl config set-context default \
  --cluster=kubernetes \
  --user=system:kube-controller-manager \
  --kubeconfig=kube-controller-manager-${master}.conf

kubectl config use-context default --kubeconfig=kube-controller-manager-${master}.conf
done
```
> 注意点： 
> - 此处指定了--server，必须是自己所在节点的kube-apiserver，不然选举会卡住失败，参照[issue: 49000](https://github.com/kubernetes/kubernetes/issues/49000#issuecomment-316015834)
> - 另外，systemd unit文件中，--master是用来覆盖此处配置，可以省略

### 5. 创建 kube-scheduler kubeconfig 文件
``` bash
for master in {master01,master02,master03};do
kubectl config set-cluster kubernetes \
  --certificate-authority=${DEPLOY_DIR}/pki/kubernetes/ca.pem \
  --embed-certs=true \
  --server=https://${IP_LIST[${master}]}:6443 \
  --kubeconfig=kube-scheduler-${master}.conf

# 注意点： credential必须是system:kube-scheduler
kubectl config set-credentials system:kube-scheduler \
  --client-certificate=${DEPLOY_DIR}/pki/kubernetes/kube-scheduler.pem \
  --client-key=${DEPLOY_DIR}/pki/kubernetes/kube-scheduler-key.pem \
  --embed-certs=true \
  --kubeconfig=kube-scheduler-${master}.conf

kubectl config set-context default \
  --cluster=kubernetes \
  --user=system:kube-scheduler \
  --kubeconfig=kube-scheduler-${master}.conf

kubectl config use-context default --kubeconfig=kube-scheduler-${master}.conf
done
```
> 注意点： 
> - 此处指定了--server，必须是自己所在节点的kube-apiserver，不然选举会卡住失败，参照[issue: 49000](https://github.com/kubernetes/kubernetes/issues/49000#issuecomment-316015834)
> - 另外，systemd unit文件中，--master是用来覆盖此处配置，可以省略

### 6. 分发kubeconfig文件和admin上下文环境文件
``` bash
cd ${DEPLOY_DIR}/kubeconfig
# 将bootstrap.kubelet.<node-hostname>.conf和kube-proxy.conf分发到node节点
for node in {node01,node02,node03};do
  ssh root@${node} "mkdir -p ${KUBECONFIG_DIR}"
  scp ${DEPLOY_DIR}/kubeconfig/bootstrap-kubelet-${node}.conf ${node}:${KUBECONFIG_DIR}/bootstrap-kubelet.conf
  scp ${DEPLOY_DIR}/kubeconfig/kube-proxy.conf ${node}:${KUBECONFIG_DIR}
done

# 将master节点的 kubeconfig 分发到所有master上
for master in {master01,master02,master03};do
  ssh root@${master} "mkdir -p ${ADMIN_KUBECONFIG_DIR}"
  ssh root@${master} "mkdir -p ${KUBECONFIG_DIR}"
  scp ${DEPLOY_DIR}/kubeconfig/admin.conf $master:${ADMIN_KUBECONFIG_DIR}/config
  scp ${DEPLOY_DIR}/kubeconfig/token.csv $master:${KUBECONFIG_DIR}
  scp ${DEPLOY_DIR}/kubeconfig/kube-controller-manager-${master}.conf $master:${KUBECONFIG_DIR}/kube-controller-manager.conf
  scp ${DEPLOY_DIR}/kubeconfig/kube-scheduler-${master}.conf $master:${KUBECONFIG_DIR}/kube-scheduler.conf
done
```

---

## 准备master、node、etcd - systemd unit文件
### 0. 创建各节点unit文件目录
``` bash
mkdir -p ${DEPLOY_DIR}/{node,master,etcd}/systemd-unit-files
```

### 1. 创建master所需unit文件
需要各master节点根据自身调整ip地址
``` bash
# kube-apiserver.service
for master in {master01,master02,master03};do
cat << EOF > ${DEPLOY_DIR}/master/systemd-unit-files/kube-apiserver-${master}.service
[Unit]
Description=Kubernetes API Server
Documentation=https://github.com/kubernetes/kubernetes
After=network.target

[Service]
ExecStart=/usr/local/bin/kube-apiserver \\
  --advertise-address=${IP_LIST[${master}]} \\
  --bind-address=${IP_LIST[${master}]} \\
  --secure-port=6443 \\
  --insecure-port=0 \\
  --authorization-mode=Node,RBAC \\
  --enable-admission-plugins=NodeRestriction \\
  --enable-bootstrap-token-auth=true \\
  --token-auth-file=${KUBECONFIG_DIR}/token.csv \\
  --service-cluster-ip-range=${SERVICE_CLUSTER_IP_RANGE} \\
  --service-node-port-range=${SERVICE_NODE_PORT_RANGE} \\
  --client-ca-file=${K8S_PKI_DIR}/ca.pem \\
  --tls-cert-file=${K8S_PKI_DIR}/kube-apiserver.pem \\
  --tls-private-key-file=${K8S_PKI_DIR}/kube-apiserver-key.pem \\
  --service-account-key-file=${K8S_PKI_DIR}/ca-key.pem \\
  --etcd-cafile=${ETCD_PKI_DIR}/ca.pem \\
  --etcd-certfile=${K8S_PKI_DIR}/apiserver-etcd-client.pem \\
  --etcd-keyfile=${K8S_PKI_DIR}/apiserver-etcd-client-key.pem \\
  --etcd-servers=https://${IP_LIST["etcd01"]}:2379,https://${IP_LIST["etcd02"]}:2379,https://${IP_LIST["etcd03"]}:2379 \\
  --kubelet-certificate-authority=${K8S_PKI_DIR}/ca.pem \\
  --kubelet-client-certificate=${K8S_PKI_DIR}/api-kubelet-client.pem \\
  --kubelet-client-key=${K8S_PKI_DIR}/api-kubelet-client-key.pem \\
  --allow-privileged=true \\
  --apiserver-count=3 \\
  --audit-log-maxage=30 \\
  --audit-log-maxbackup=3 \\
  --audit-log-maxsize=100 \\
  --audit-log-path=/var/lib/audit.log \\
  --event-ttl=1h \\
  --v=2
Restart=on-failure
RestartSec=5
Type=notify
LimitNOFILE=65536

[Install]
WantedBy=multi-user.target
EOF
done
# --admission-control: 1.10之后默认启用admission-control
#   默认设定的值: "NamespaceLifecycle, LimitRanger, ServiceAccount, TaintNodesByCondition, Priority, 
#   DefaultTolerationSeconds, DefaultStorageClass, StorageObjectInUseProtection, PersistentVolumeClaimResize,
#   MutatingAdmissionWebhook, ValidatingAdmissionWebhook, RuntimeClass, ResourceQuota"
# 若需要额外配置其他admission，请参照kubernetes admission controller官方文档

# --enable-bootstrap-token-auth: 启用bootstrap-token认证，详情请参照[官方文档](https://kubernetes.io/docs/reference/command-line-tools-reference/kubelet-tls-bootstrapping/)

# 根据下面这个issue和pr内容，以下三个配置是用来加密master和node通信的，主要是kubectl logs/exec。
# [issue: 14700](https://github.com/kubernetes/kubernetes/pull/14700)
# [PR: 31562](https://github.com/kubernetes/kubernetes/pull/31562)
# [kubelet-authentication-authorization]
#   (https://kubernetes.io/docs/reference/command-line-tools-reference/kubelet-authentication-authorization/)
#  --kubelet-certificate-authority
#  --kubelet-client-certificate
#  --kubelet-client-key

# kube-controller-manager.service
for master in {master01,master02,master03};do
cat << EOF > ${DEPLOY_DIR}/master/systemd-unit-files/kube-controller-manager-${master}.service
[Unit]
Description=Kubernetes Controller Manager
Documentation=https://github.com/kubernetes/kubernetes

[Service]
ExecStart=/usr/local/bin/kube-controller-manager \\
  --bind-address=127.0.0.1 \\
  --controllers=*,bootstrapsigner,tokencleaner \\
  --allocate-node-cidrs=true \\
  --service-cluster-ip-range=${SERVICE_CLUSTER_IP_RANGE} \\
  --cluster-cidr=${POD_CLUSTER_IP_RANGE} \\
  --cluster-name=kubernetes \\
  --kubeconfig=${KUBECONFIG_DIR}/kube-controller-manager.conf \\
  --root-ca-file=${K8S_PKI_DIR}/ca.pem \\
  --cluster-signing-cert-file=${K8S_PKI_DIR}/ca.pem \\
  --cluster-signing-key-file=${K8S_PKI_DIR}/ca-key.pem \\
  --use-service-account-credentials=true \\
  --service-account-private-key-file=${K8S_PKI_DIR}/ca-key.pem \\
  --leader-elect=true \\
  --v=2
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF
done

# kube-scheduler.service
for master in {master01,master02,master03};do
cat << EOF > ${DEPLOY_DIR}/master/systemd-unit-files/kube-scheduler-${master}.service
[Unit]
Description=Kubernetes Scheduler
Documentation=https://github.com/kubernetes/kubernetes

[Service]
ExecStart=/usr/local/bin/kube-scheduler \\
  --bind-address=127.0.0.1 \\
  --kubeconfig=${KUBECONFIG_DIR}/kube-scheduler.conf \\
  --leader-elect=true \\
  --v=2
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF
done
```
> 如果中途修改过`--service-cluster-ip-range`(kube-apiserver,kube-controller-manager)，有可能会遇到下面的错误
> - `"message": "Cluster IP *.*.*.* is not within the service CIDR *.*.*.*/**; please recreate service"`
> 解决方案：
> `kubectl get services --all-namespaces`获得系统的最初创建的集群的service后，删除它`kubectl delete service kubernets`
> 然后系统会自动创建它，但是！！！不推荐生产环境已经存在应用service后这样搞！！！

### 2. 创建etcd所需unit文件
``` bash
for etcd in {etcd01,etcd02,etcd03};do
cat << EOF > ${DEPLOY_DIR}/etcd/systemd-unit-files/etcd-${etcd}.service
[Unit]
Description=Etcd Server
After=network.target
After=network-online.target
Wants=network-online.target
Documentation=https://github.com/coreos

[Service]
Type=notify
WorkingDirectory=/var/lib/etcd/
EnvironmentFile=-/etc/etcd/etcd.conf
ExecStart=/usr/local/bin/etcd \\
  --name=${etcd} \\
  --client-cert-auth=true \\
  --trusted-ca-file=${ETCD_PKI_DIR}/ca.pem \\
  --cert-file=${ETCD_PKI_DIR}/server.pem \\
  --key-file=${ETCD_PKI_DIR}/server-key.pem \\
  --peer-client-cert-auth=true \\
  --peer-trusted-ca-file=${ETCD_PKI_DIR}/ca.pem \\
  --peer-cert-file=${ETCD_PKI_DIR}/peer.pem \\
  --peer-key-file=${ETCD_PKI_DIR}/peer-key.pem \\
  --initial-advertise-peer-urls=https://${IP_LIST[${etcd}]}:2380 \\
  --listen-peer-urls=https://${IP_LIST[${etcd}]}:2380 \\
  --listen-client-urls=https://${IP_LIST[${etcd}]}:2379,https://127.0.0.1:2379 \\
  --advertise-client-urls=https://${IP_LIST[${etcd}]}:2379 \\
  --initial-cluster-token=etcd-cluster-0 \\
  --initial-cluster=etcd01=https://${IP_LIST["etcd01"]}:2380,etcd02=https://${IP_LIST["etcd02"]}:2380,etcd03=https://${IP_LIST["etcd03"]}:2380 \\
  --initial-cluster-state=new \\
  --data-dir=/var/lib/etcd
Restart=on-failure
RestartSec=5
LimitNOFILE=65536

[Install]
WantedBy=multi-user.target
EOF
done
```

### 3. 创建node所需unit文件
``` bash
# kubelet.service
for node in {node01,node02,node03};do
cat << EOF > ${DEPLOY_DIR}/node/systemd-unit-files/kubelet-${node}.service
[Unit]
Description=Kubernetes Kubelet
Documentation=https://github.com/kubernetes/kubernetes
After=docker.service
Requires=docker.service

[Service]
WorkingDirectory=/var/lib/kubelet
ExecStart=/usr/local/bin/kubelet \\
  --address=${IP_LIST[${node}]} \\
  --hostname-override=${node} \\
  --network-plugin=cni \\
  --pod-infra-container-image=k8s.gcr.io/pause-amd64:3.0 \\
  --bootstrap-kubeconfig=${KUBECONFIG_DIR}/bootstrap-kubelet.conf \\
  --kubeconfig=${KUBECONFIG_DIR}/kubelet.conf \\
  --client-ca-file=${K8S_PKI_DIR}/ca.pem \\
  --cert-dir=${K8S_PKI_DIR} \\
  --tls-cert-file=${K8S_PKI_DIR}/api-kubelet-client.pem \\
  --tls-private-key-file=${K8S_PKI_DIR}/api-kubelet-client-key.pem \\
  --anonymous-auth=false \\
  --hairpin-mode promiscuous-bridge \\
  --serialize-image-pulls=false \\
  --cgroup-driver=systemd \\
  --cluster-dns=${SERVICE_CLUSTER_IP_RANGE%.*}.2 \\
  --cluster-domain=cluster.local \\
  --v=2
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF
done
# cgroup-driver和docker一致，皆为systemd
# --cert-dir指定kubelet从master那边获取的签名证书存放目录

# 根据下面这个issue和pr内容，以下配置是用来加密master和node通信的，主要是kubectl logs/exec。
# [issue: 14700](https://github.com/kubernetes/kubernetes/pull/14700)
# [PR: 31562](https://github.com/kubernetes/kubernetes/pull/31562)
# [kubelet-authentication-authorization]
#   (https://kubernetes.io/docs/reference/command-line-tools-reference/kubelet-authentication-authorization/)
# --client-ca-file

# 根据[issue: 63164](https://github.com/kubernetes/kubernetes/issues/63164)
# tls bootsraping里面自动在--cert-dir下面生成的key，只是用于kubelet -> apiserver
# 而如果需要apiserver -> kubelet的认证，需要手动指定以下参数，如果不指定，kubelet会自动生成一个ca
# --tls-cert-file
# --tls-private-key-file

for node in {node01,node02,node03};do
cat << EOF > ${DEPLOY_DIR}/node/systemd-unit-files/kube-proxy-${node}.service
[Unit]
Description=Kubernetes Kube-Proxy Server
Documentation=https://github.com/GoogleCloudPlatform/kubernetes
After=network.target

[Service]
ExecStart=/usr/local/bin/kube-proxy \\
  --logtostderr=true \\
  --v=0 \\
  --master=https://${KUBE_API_PROXY_IP}:443 \\
  --bind-address=${IP_LIST[${node}]} \\
  --hostname-override=${node} \\
  --kubeconfig=${KUBECONFIG_DIR}/kube-proxy.conf \\
  --cluster-cidr=${POD_CLUSTER_IP_RANGE}
Restart=on-failure
LimitNOFILE=65536

[Install]
WantedBy=multi-user.target
EOF
done
```

### 4. 分发systemd unit文件
``` bash
# 下发master unit文件
for master in {master01,master02,master03};do
  rsync -av ${DEPLOY_DIR}/master/systemd-unit-files/kube-apiserver-${master}.service \
    ${master}:/usr/lib/systemd/system/kube-apiserver.service         
  rsync -av ${DEPLOY_DIR}/master/systemd-unit-files/kube-controller-manager-${master}.service \
    ${master}:/usr/lib/systemd/system/kube-controller-manager.service
  rsync -av ${DEPLOY_DIR}/master/systemd-unit-files/kube-scheduler-${master}.service \
    ${master}:/usr/lib/systemd/system/kube-scheduler.service  
done

# 下发node unit文件
for node in {node01,node02,node03};do
  rsync -av ${DEPLOY_DIR}/node/systemd-unit-files/kubelet-${node}.service \
    ${node}:/usr/lib/systemd/system/kubelet.service
  rsync -av ${DEPLOY_DIR}/node/systemd-unit-files/kube-proxy-${node}.service \
    ${node}:/usr/lib/systemd/system/kube-proxy.service
done

# 下发etcd unit文件
for etcd in {etcd01,etcd02,etcd03};do
  rsync -av ${DEPLOY_DIR}/etcd/systemd-unit-files/etcd-${etcd}.service ${etcd}:/usr/lib/systemd/system/etcd.service
done
```

---

## 启动服务
### 1. etcd节点
``` bash
for etcd in {etcd01,etcd02,etcd03};do
  ssh root@${etcd} "mkdir -p /var/lib/etcd"
  ssh root@${etcd} "systemctl daemon-reload"
  ssh root@${etcd} "systemctl enable etcd"
done

# 手动去etcd机器上启动etcd，必须同时启动，集群才能启动成功
systemctl start etcd

etcdctl \
  --endpoints https://${IP_LIST["etcd01"]}:2379,https://${IP_LIST["etcd02"]}:2379,https://${IP_LIST["etcd03"]}:2379 \
  --ca-file=${DEPLOY_DIR}/pki/etcd/ca.pem \
  --cert-file=${DEPLOY_DIR}/pki/etcd/peer.pem \
  --key-file=${DEPLOY_DIR}/pki/etcd/peer-key.pem \
  cluster-health
```

### 2. master节点
``` bash
for master in {master01,master02,master03};do
  ssh root@${master} "systemctl daemon-reload"
  ssh root@${master} "systemctl start kube-apiserver kube-controller-manager kube-scheduler"
  ssh root@${master} "systemctl enable kube-apiserver kube-controller-manager kube-scheduler"
done
```

### 3. kubelet tls bootstrap
下面执行的内容牵扯到kubelet-tls-bootstrap的内容，可以参考[官方文档](https://kubernetes.io/docs/reference/command-line-tools-reference/kubelet-tls-bootstrapping/)

创建ClusterRoleBinding允许kubelet创建CSR(certificate signing requests)
``` bash
# enable bootstrapping nodes to create CSR
cat << EOF | kubectl apply -f -
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  name: create-csrs-for-bootstrapping
subjects:
- kind: Group
  name: system:bootstrappers
  apiGroup: rbac.authorization.k8s.io
roleRef:
  kind: ClusterRole
  name: system:node-bootstrapper
  apiGroup: rbac.authorization.k8s.io
EOF
```

创建ClusterRoleBinding允许kubelet请求和接收证书
``` bash
# Approve all CSRs for the group "system:bootstrappers"
cat << EOF | kubectl apply -f -
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  name: auto-approve-csrs-for-group
subjects:
- kind: Group
  name: system:bootstrappers
  apiGroup: rbac.authorization.k8s.io
roleRef:
  kind: ClusterRole
  name: system:certificates.k8s.io:certificatesigningrequests:nodeclient
  apiGroup: rbac.authorization.k8s.io
EOF
```

创建ClusterRoleBinding允许kubelet重签证书
``` bash
# Approve renewal CSRs for the group "system:nodes"
cat << EOF | kubectl apply -f -
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  name: auto-approve-renewals-for-nodes
subjects:
- kind: Group
  name: system:nodes
  apiGroup: rbac.authorization.k8s.io
roleRef:
  kind: ClusterRole
  name: system:certificates.k8s.io:certificatesigningrequests:selfnodeclient
  apiGroup: rbac.authorization.k8s.io
EOF
```

### 4. node节点
``` bash
for node in {node01,node02,node03};do
  ssh root@${node} "mkdir -p /var/lib/kubelet"
  ssh root@${node} "systemctl daemon-reload && systemctl start kubelet kube-proxy && systemctl enable kubelet kube-proxy"
done
```

### 5. 查看node节点的tls认证请求
``` bash
# 查看csr请求
kubectl get csr
# 如果自动认证签证证书失败，有需要人工批准的请求，可以执行approve csr请求
# kubectl get csr | awk '/Pending/ {print $1}' | xargs kubectl certificate approve
```

### 6. 查看集群状态
``` bash
kubectl get componentstatuses
NAME                 STATUS    MESSAGE             ERROR
scheduler            Healthy   ok                  
controller-manager   Healthy   ok                  
etcd-0               Healthy   {"health":"true"}   
etcd-2               Healthy   {"health":"true"}   
etcd-1               Healthy   {"health":"true"}

kubectl get nodes
NAME      STATUS    ROLES     AGE       VERSION
node01    Ready     <none>    40m       v1.9.1
node02    Ready     <none>    3m        v1.9.1
node03    Ready     <none>    3m        v1.9.1
```

---

## 安装Pod网络附加组件
关于CNI网络组件的选择，可以自行搜索文档，此处选择使用flannel。

### 1. flannel需要的环境
- bridge-nf-call-iptables内核优化开启，前面已经优化过，此处不需要再处理
- 确保防火墙规则允许参与overlay网络的所有主机的UDP端口8285和8472通信，参照文档：[coreos关于防火墙的说明](https://coreos.com/flannel/docs/latest/troubleshooting.html#firewalls)

### 2. 启动flannel
官方kubeadm引导k8s集群的文档中，使用了这个yaml文件： https://raw.githubusercontent.com/coreos/flannel/2140ac876ef134e0ed5af15c65e414cf26827915/Documentation/kube-flannel.yml 上面这个文件中默认使用了10.244.0.0/16作为pod的网络，如果希望自定义，需要在kubeadm init时增加--pod-network-cidr选项

但是因为我们是二进制安装，此处我们下载上面的yaml文件，并手动修改pod网络的参数，并仅保留amd64硬件的daemonset，其他硬件平台的删除
``` bash
mkdir -p ${DEPLOY_DIR}/kube-addon

# customize kube-flannel.yml
# ！！！！！！！！！！！！！！！！
# ！！！ 有时候下面这个命令，会导致文件里面有乱码，为啥子我也没弄清楚，最后执行完检查下
# ！！！ 如果有问题，手动粘贴以下内容，记得把变量${POD_CLUSTER_IP_RANGE}替换为它的值
# ！！！！！！！！！！！！！！！！
cat << EOF > ${DEPLOY_DIR}/kube-addon/kube-flannel.yml
---
apiVersion: policy/v1beta1
kind: PodSecurityPolicy
metadata:
  name: psp.flannel.unprivileged
  annotations:
    seccomp.security.alpha.kubernetes.io/allowedProfileNames: docker/default
    seccomp.security.alpha.kubernetes.io/defaultProfileName: docker/default
    apparmor.security.beta.kubernetes.io/allowedProfileNames: runtime/default
    apparmor.security.beta.kubernetes.io/defaultProfileName: runtime/default
spec:
  privileged: false
  volumes:
    - configMap
    - secret
    - emptyDir
    - hostPath
  allowedHostPaths:
    - pathPrefix: "/etc/cni/net.d"
    - pathPrefix: "/etc/kube-flannel"
    - pathPrefix: "/run/flannel"
  readOnlyRootFilesystem: false
  # Users and groups
  runAsUser:
    rule: RunAsAny
  supplementalGroups:
    rule: RunAsAny
  fsGroup:
    rule: RunAsAny
  # Privilege Escalation
  allowPrivilegeEscalation: false
  defaultAllowPrivilegeEscalation: false
  # Capabilities
  allowedCapabilities: ['NET_ADMIN']
  defaultAddCapabilities: []
  requiredDropCapabilities: []
  # Host namespaces
  hostPID: false
  hostIPC: false
  hostNetwork: true
  hostPorts:
  - min: 0
    max: 65535
  # SELinux
  seLinux:
    # SELinux is unsed in CaaSP
    rule: 'RunAsAny'
---
kind: ClusterRole
apiVersion: rbac.authorization.k8s.io/v1beta1
metadata:
  name: flannel
rules:
  - apiGroups: ['extensions']
    resources: ['podsecuritypolicies']
    verbs: ['use']
    resourceNames: ['psp.flannel.unprivileged']
  - apiGroups:
      - ""
    resources:
      - pods
    verbs:
      - get
  - apiGroups:
      - ""
    resources:
      - nodes
    verbs:
      - list
      - watch
  - apiGroups:
      - ""
    resources:
      - nodes/status
    verbs:
      - patch
---
kind: ClusterRoleBinding
apiVersion: rbac.authorization.k8s.io/v1beta1
metadata:
  name: flannel
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: ClusterRole
  name: flannel
subjects:
- kind: ServiceAccount
  name: flannel
  namespace: kube-system
---
apiVersion: v1
kind: ServiceAccount
metadata:
  name: flannel
  namespace: kube-system
---
kind: ConfigMap
apiVersion: v1
metadata:
  name: kube-flannel-cfg
  namespace: kube-system
  labels:
    tier: node
    app: flannel
data:
  cni-conf.json: |
    {
      "cniVersion": "0.2.0",
      "name": "cbr0",
      "plugins": [
        {
          "type": "flannel",
          "delegate": {
            "hairpinMode": true,
            "isDefaultGateway": true
          }
        },
        {
          "type": "portmap",
          "capabilities": {
            "portMappings": true
          }
        }
      ]
    }
  net-conf.json: |
    {
      "Network": "${POD_CLUSTER_IP_RANGE}",
      "Backend": {
        "Type": "vxlan"
      }
    }
---
apiVersion: apps/v1
kind: DaemonSet
metadata:
  name: kube-flannel-ds-amd64
  namespace: kube-system
  labels:
    tier: node
    app: flannel
spec:
  selector:
    matchLabels:
      app: flannel
  template:
    metadata:
      labels:
        tier: node
        app: flannel
    spec:
      affinity:
        nodeAffinity:
          requiredDuringSchedulingIgnoredDuringExecution:
            nodeSelectorTerms:
              - matchExpressions:
                  - key: beta.kubernetes.io/os
                    operator: In
                    values:
                      - linux
                  - key: beta.kubernetes.io/arch
                    operator: In
                    values:
                      - amd64
      hostNetwork: true
      tolerations:
      - operator: Exists
        effect: NoSchedule
      serviceAccountName: flannel
      initContainers:
      - name: install-cni
        image: quay.io/coreos/flannel:v0.11.0-amd64
        command:
        - cp
        args:
        - -f
        - /etc/kube-flannel/cni-conf.json
        - /etc/cni/net.d/10-flannel.conflist
        volumeMounts:
        - name: cni
          mountPath: /etc/cni/net.d
        - name: flannel-cfg
          mountPath: /etc/kube-flannel/
      containers:
      - name: kube-flannel
        image: quay.io/coreos/flannel:v0.11.0-amd64
        command:
        - /opt/bin/flanneld
        args:
        - --ip-masq
        - --kube-subnet-mgr
        resources:
          requests:
            cpu: "100m"
            memory: "50Mi"
          limits:
            cpu: "100m"
            memory: "50Mi"
        securityContext:
          privileged: false
          capabilities:
             add: ["NET_ADMIN"]
        env:
        - name: POD_NAME
          valueFrom:
            fieldRef:
              fieldPath: metadata.name
        - name: POD_NAMESPACE
          valueFrom:
            fieldRef:
              fieldPath: metadata.namespace
        volumeMounts:
        - name: run
          mountPath: /run/flannel
        - name: flannel-cfg
          mountPath: /etc/kube-flannel/
      volumes:
        - name: run
          hostPath:
            path: /run/flannel
        - name: cni
          hostPath:
            path: /etc/cni/net.d
        - name: flannel-cfg
          configMap:
            name: kube-flannel-cfg
EOF
# 包含以下资源
# - PodSecurityPolicy
# - ClusterRole
# - ClusterRoleBinding
# - ServiceAccount
# - ConfigMap
# - DaemonSet(for amd64 platform)

# apply cni addon: flannel
kubectl apply -f ${DEPLOY_DIR}/kube-addon/kube-flannel.yml
```
> `--kube-subnet-mgr`，使用了这个选项，flannel不会去etcd中获取网络配置信息，而是通过`/etc/kube-flannel/net-conf.json`来获取网络配置

### 3. 查看flannel运行状态
``` bash
kubectl get pods --namespace kube-system
NAME                          READY   STATUS    RESTARTS   AGE
kube-flannel-ds-amd64-g2snw   1/1     Running   0          62s
kube-flannel-ds-amd64-pzmf5   1/1     Running   0          62s
kube-flannel-ds-amd64-sxtdz   1/1     Running   0          62s
```

---

## 安装DNS
高版本里面基本都推荐使用CoreDNS替代，参考文档[K8S-COREDNS](https://kubernetes.io/docs/tasks/administer-cluster/coredns/#installing-coredns) & [COREDNS-GITHUB](https://github.com/coredns/deployment/tree/master/kubernetes)

创建coredns部署脚本
``` bash
# coredns脚本安装需要jq命令支持
yum install epel-release -y
yum install jq -y

# 下载部署coredns需要的文件
wget https://raw.githubusercontent.com/coredns/deployment/master/kubernetes/deploy.sh -O ${DEPLOY_DIR}/kube-addon/deploy.sh
wget https://raw.githubusercontent.com/coredns/deployment/master/kubernetes/coredns.yaml.sed -O ${DEPLOY_DIR}/kube-addon/coredns.yaml.sed

# 官方脚本里面的function名称不符合bash的标准，你敢信？
sed -i "s/translate-kube-dns-configmap/translate_kube_dns_configmap/g" ${DEPLOY_DIR}/kube-addon/deploy.sh
sed -i "s/kube-dns-federation-to-coredns/kube_dns_federation_to_coredns/g" ${DEPLOY_DIR}/kube-addon/deploy.sh
sed -i "s/kube-dns-upstreamnameserver-to-coredns/kube_dns_upstreamnameserver_to_coredns/g" ${DEPLOY_DIR}/kube-addon/deploy.sh
sed -i "s/kube-dns-stubdomains-to-coredns/kube_dns_stubdomains_to_coredns/g" ${DEPLOY_DIR}/kube-addon/deploy.sh

# 部署coredns
# -i 指定dns ip
sh ${DEPLOY_DIR}/kube-addon/deploy.sh -i ${SERVICE_CLUSTER_IP_RANGE%.*}.2| kubectl apply -f -
```

---

## 安装持久化存储方案（此处选择glusterfs）
- [k8s persistent volume docs](https://kubernetes.io/docs/concepts/storage/persistent-volumes/)
- [部署glusterfs之前需求](https://github.com/gluster/gluster-kubernetes/blob/master/docs/setup-guide.md)
- [部署glusterfs文档](https://github.com/gluster/gluster-kubernetes)

### 0. 浅谈选择glusterfs的理由
看了k8s的pv文档后，因为前面安装k8s的环境是bare metal，所以无法使用云提供的方案，最终只能从glusterfs和ceph里面选择一个。经过网络上简单的搜索之后，发现glusterfs性能上比ceph稍高一点，另外它支持一个heketi，可以用restful的方式管理glusterfs的volume。虽然我没有实际部署对比过，但是倾向于glusterfs。

另外，之前不知道使用k8s持久化存储之前需要先安装持久化存储，汗，走了一点弯路。

### 1. k8s集群要求
- 至少三个节点
- 每个节点必须至少连接一个raw disk（例如EBS卷或本地磁盘），以供heketi使用。这些设备上不得包含任何数据，因为它们将由heketi格式化和分区。
- 每个节点上必须保留以下端口供glusterfs使用：
  - 2222 - GlusterFS pod's sshd
  - 24007 - GlusterFS Daemon
  - 24008 - GlusterFS Management
  - 49152 to 49251 - Each brick for every volume on the host requires its own port. For every new brick, one new port will be used starting at 49152. We recommend a default range of 49152-49251 on each host, though you can adjust this to fit your needs.
- 每个节点需要加载的内核模块
  - dm_snapshot
  - dm_mirror
  - dm_thin_pool
- 每个节点需要拥有`mount.glusterfs`命令
- glusterfs客户端版本和server版本越接近越好

#### 在节点上执行
``` bash
# 检查raw disk环境
fdisk -l
# 查看结果中是否有未被使用的磁盘

# 检查和加载内核模块
lsmod | grep dm_snapshot || modprobe dm_snapshot
lsmod | grep dm_mirror || modprobe dm_mirror
lsmod | grep dm_thin_pool || modprobe dm_thin_pool
# 检查加载是否成功
lsmod | egrep '^(dm_snapshot|dm_mirror|dm_thin_pool)'
# 输出内容
# dm_thin_pool           66358  0 
# dm_snapshot            39103  0 
# dm_mirror              22289  0 

# 安装mount.glusterfs命令
yum install -y https://buildlogs.centos.org/centos/7/storage/x86_64/gluster-7/glusterfs-libs-7.1-1.el7.x86_64.rpm
yum install -y https://buildlogs.centos.org/centos/7/storage/x86_64/gluster-7/glusterfs-7.1-1.el7.x86_64.rpm
yum install -y https://buildlogs.centos.org/centos/7/storage/x86_64/gluster-7/glusterfs-client-xlators-7.1-1.el7.x86_64.rpm
yum install -y https://buildlogs.centos.org/centos/7/storage/x86_64/gluster-7/glusterfs-fuse-7.1-1.el7.x86_64.rpm
# 默认安装的是glusterfs 3.12，为了和下面gk-deploy脚本里面安装的版本一致，手动安装7.1版本

# 查看glusterfs版本
glusterfs --version
glusterfs 7.1

mount.glusterfs -V
glusterfs 7.1
```

### 2. 部署glusterfs(master01上操作)
``` bash
# step 1. 下载安装文件
# 以下测试使用的，最新commit是：
#   Latest commit
#   7246eb4
#   on Jul 19, 2019
# 这个时候的版本和kubenetes 1.17不兼容，有很多需要修改的东西
# 我个人做了很多修改和debug，后面应该会修复，所以下面的内容
# 请酌情来判断是否需要执行
git clone https://github.com/gluster/gluster-kubernetes.git
cd gluster-kubernetes/deploy

# step 2. 准备topology文件
# ***************************
# 重点关注
# - hostsnames.manage里面填写节点的hostname
# - hostnames.storage里面填写节点的ip
# - devices里面填写磁盘的名称
# ***************************
cat << EOF > topology.json
{
  "clusters": [
    {
      "nodes": [
        {
          "node": {
            "hostnames": {
              "manage": [
                "node01"
              ],
              "storage": [
                "${IP_LIST['node01']}"
              ]
            },
            "zone": 1
          },
          "devices": [
            "/dev/sdb"
          ]
        },
        {
          "node": {
            "hostnames": {
              "manage": [
                "node02"
              ],
              "storage": [
                "${IP_LIST['node02']}"
              ]
            },
            "zone": 1
          },
          "devices": [
            "/dev/sdb"
          ]
        },
        {
          "node": {
            "hostnames": {
              "manage": [
                "node03"
              ],
              "storage": [
                "${IP_LIST['node03']}"
              ]
            },
            "zone": 1
          },
          "devices": [
            "/dev/sdb"
          ]
        }
      ]
    }
  ]
}
EOF

# 安装前确认节点都ready状态
kubectl get nodes

# step 3. ISSUCE解决(在官方的git中已经有看到解决的pr，但我当前使用的时间点还需要自己来修改)
# 1) k8s 1.17换了api版本
sed -ir "s|apiVersion: extensions/v1beta1|apiVersion: apps/v1|g" kube-templates/deploy-heketi-deployment.yaml
sed -ir "s|apiVersion: extensions/v1beta1|apiVersion: apps/v1|g" kube-templates/gluster-s3-template.yaml
sed -ir "s|apiVersion: extensions/v1beta1|apiVersion: apps/v1|g" kube-templates/glusterfs-daemonset.yaml
sed -ir "s|apiVersion: extensions/v1beta1|apiVersion: apps/v1|g" kube-templates/heketi-deployment.yaml
sed -ir "s|apiVersion: extensions/v1beta1|apiVersion: apps/v1|g" ocp-templates/glusterfs-template.yaml

# 2) error: error validating "STDIN": error validating data: ValidationError(DaemonSet.spec): missing required
# field "selector" in io.k8s.api.apps.v1.DaemonSetSpec; if you choose to ignore these errors, turn validation off with --validate=false
# k8s 1.17需要指定pod selector
# 确认以下内容，如果不存在，请手动增加
vim kube-templates/glusterfs-daemonset.yaml
spec:
  selector:
    matchLabels:
      name: glusterfs
  template:
    metadata:
      labels:
        name: glusterfs

vim kube-templates/deploy-heketi-deployment.yaml
spec:
  selector:
    matchLabels:
      name: deploy-heketi
  template:
    metadata:
      labels:
        name: deploy-heketi

vim kube-templates/gluster-s3-template.yaml
- kind: Deployment
  spec:
    selector:
      matchLabels:
        name: gluster-s3
    template:
      metadata:
        labels:
          name: gluster-s3

vim kube-templates/heketi-deployment.yaml
spec:
  selector:
    matchLabels:
      name: heketi
  template:
    metadata:
      labels:
        name: heketi

# 3) Determining heketi service URL ... Error: unknown flag: --show-all
# See 'kubectl get --help' for usage.
# Failed to communicate with heketi service.
# kubectl v1.17 没有--show-all这个选项
vim gk-deploy
# 将下面的内容
# heketi_pod=$(${CLI} get pod --no-headers --show-all --selector="heketi" | awk '{print $1}')
# 修改为
# heketi_pod=$(${CLI} get pod --no-headers --selector="heketi" | awk '{print $1}')

# step 4. 部署heketi and GlusterFS
ADMIN_KEY=adminkey
USER_KEY=userkey
./gk-deploy -g -y -v --admin-key ${ADMIN_KEY} --user-key ${USER_KEY}
# 如果第一次没安装成功，需要二次安装，使用下面命令清除之前的安装资源
# 删除资源和服务
# ./gk-deploy -g --abort --admin-key adminkey --user-key userkey
# 查看lv名称
# lvs
# 删除lv
# lvremove /dev/vg
# 清除磁盘(在节点机器上执行)
# wipefs -a /dev/sdc

# step 5. 检查heketi和glusterfs运行情况
export HEKETI_CLI_SERVER=$(kubectl get svc/heketi --template 'http://{{.spec.clusterIP}}:{{(index .spec.ports 0).port}}')
echo $HEKETI_CLI_SERVER
curl $HEKETI_CLI_SERVER/hello
# Hello from Heketi
# 如果timeout的话，看看是不是master没搞成node节点，没加入kube-proxy
# 可以获取到地址之后，到node节点上执行curl操作


# step 6. 创建storageclass，来自动为pvc创建pv
SECRET_KEY=`echo -n "${ADMIN_KEY}" | base64`

cat << EOF | kubectl apply -f -
apiVersion: v1
kind: Secret
metadata:
  name: heketi-secret
  namespace: default
data:
  # base64 encoded password. E.g.: echo -n "mypassword" | base64
  key: ${SECRET_KEY}
type: kubernetes.io/glusterfs
EOF

cat << EOF | kubectl apply -f -
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: glusterfs-storage
provisioner: kubernetes.io/glusterfs
parameters:
  resturl: "${HEKETI_CLI_SERVER}"
  restuser: "admin"
  secretNamespace: "default"
  secretName: "heketi-secret"
  volumetype: "replicate:3"
EOF
# 注意生成pvc资源时，需要指定storageclass为上面配置的"glusterfs-storage"


kubectl get nodes,pods
NAME          STATUS   ROLES    AGE    VERSION
node/node01   Ready    <none>   5d3h   v1.17.0
node/node02   Ready    <none>   5d3h   v1.17.0
node/node03   Ready    <none>   5d3h   v1.17.0

NAME                          READY   STATUS    RESTARTS   AGE
pod/glusterfs-bhprz           1/1     Running   0          45m
pod/glusterfs-jt64n           1/1     Running   0          45m
pod/glusterfs-vkfp5           1/1     Running   0          45m
pod/heketi-779bc95979-272qk   1/1     Running   0          38m
```