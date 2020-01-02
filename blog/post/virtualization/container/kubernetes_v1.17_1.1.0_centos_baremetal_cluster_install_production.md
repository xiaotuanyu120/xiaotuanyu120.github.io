
title: kubernetes v1.17 1.1.0 kubernetes集群安装(生产环境)
date: 2019-12-24 09:55:00
categories: virtualization/container
tags: [container,docker,kubernetes,flannel]
---
### kubernetes v1.17 1.1.0 kubernetes集群安装(生产环境)

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
| flannel    |            |

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
mkdir -p ${DEPLOY_DIR}/{node,master,etcd}/bin
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
```

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
```

---

## 生成k8s集群认证文件
k8s集群需要如下证书文件：
- Client certificates for the kubelet to authenticate to the API server
- Server certificate for the API server endpoint
- Client certificates for administrators of the cluster to authenticate to the API server
- Client certificates for the API server to talk to the kubelets
- Client certificate for the API server to talk to etcd
- Client certificate/kubeconfig for the controller manager to talk to the API server
- Client certificate/kubeconfig for the scheduler to talk to the API server.
- Client and server certificates for the front-proxy

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
      "O": "k8s",
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
            "O": "k8s",
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
            "O": "k8s",
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
      "O": "k8s",
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
            "O": "k8s",
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
      "O": "k8s",
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
      "O": "k8s",
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
      "O": "k8s",
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
  scp ${DEPLOY_DIR}/pki/kubernetes/kube-apiserver.pem ${master}:${K8S_PKI_DIR}/apiserver.pem
  scp ${DEPLOY_DIR}/pki/kubernetes/kube-apiserver-key.pem ${master}:${K8S_PKI_DIR}/apiserver-key.pem
  scp ${DEPLOY_DIR}/pki/kubernetes/kube-controller-manager.pem ${master}:${K8S_PKI_DIR}/api-kubelet-client.pem
  scp ${DEPLOY_DIR}/pki/kubernetes/kube-controller-manager-key.pem ${master}:${K8S_PKI_DIR}/api-kubelet-client-key.pem
  scp ${DEPLOY_DIR}/pki/etcd/ca.pem ${master}:${ETCD_PKI_DIR}
  scp ${DEPLOY_DIR}/pki/etcd/client.pem ${master}:${K8S_PKI_DIR}/apiserver-etcd-client.pem
  scp ${DEPLOY_DIR}/pki/etcd/client-key.pem ${master}:${K8S_PKI_DIR}/apiserver-etcd-client-key.pem
done

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
    --certificate-authority=${K8S_PKI_DIR}/ca.pem \
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
  --user=kube-proxy \
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
kubectl config set-cluster kubernetes \
  --certificate-authority=${DEPLOY_DIR}/pki/kubernetes/ca.pem \
  --embed-certs=true \
  --server=https://127.0.0.1:6443 \
  --kubeconfig=kube-controller-manager.conf

# 注意点： credential必须是system:kube-controller-manager
kubectl config set-credentials system:kube-controller-manager \
  --client-certificate=${DEPLOY_DIR}/pki/kubernetes/kube-controller-manager.pem \
  --client-key=${DEPLOY_DIR}/pki/kubernetes/kube-controller-manager-key.pem \
  --embed-certs=true \
  --kubeconfig=kube-controller-manager.conf

kubectl config set-context default \
  --cluster=kubernetes \
  --user=system:kube-controller-manager \
  --kubeconfig=kube-controller-manager.conf

kubectl config use-context default --kubeconfig=kube-controller-manager.conf
```

### 5. 创建 kube-scheduler kubeconfig 文件
``` bash
kubectl config set-cluster kubernetes \
  --certificate-authority=${DEPLOY_DIR}/pki/kubernetes/ca.pem \
  --embed-certs=true \
  --server=https://127.0.0.1:6443 \
  --kubeconfig=kube-scheduler.conf

# 注意点： credential必须是system:kube-scheduler
kubectl config set-credentials system:kube-scheduler \
  --client-certificate=${DEPLOY_DIR}/pki/kubernetes/kube-scheduler.pem \
  --client-key=${DEPLOY_DIR}/pki/kubernetes/kube-scheduler-key.pem \
  --embed-certs=true \
  --kubeconfig=kube-scheduler.conf

kubectl config set-context default \
  --cluster=kubernetes \
  --user=system:kube-scheduler \
  --kubeconfig=kube-scheduler.conf

kubectl config use-context default --kubeconfig=kube-scheduler.conf
```

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
  scp ${DEPLOY_DIR}/kubeconfig/kube-controller-manager.conf $master:${KUBECONFIG_DIR}
  scp ${DEPLOY_DIR}/kubeconfig/kube-scheduler.conf $master:${KUBECONFIG_DIR}
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
  --tls-cert-file=${K8S_PKI_DIR}/apiserver.pem \\
  --tls-private-key-file=${K8S_PKI_DIR}/apiserver-key.pem \\
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

# --enable-bootstrap-token-auth: 启用bootstrap-token认证，详情请参照官方文档

# kube-controller-manager.service
for master in {master01,master02,master03};do
cat << EOF > ${DEPLOY_DIR}/master/systemd-unit-files/kube-controller-manager-${master}.service
[Unit]
Description=Kubernetes Controller Manager
Documentation=https://github.com/kubernetes/kubernetes

[Service]
ExecStart=/usr/local/bin/kube-controller-manager \\
  --bind-address=127.0.0.1 \\
  --master=https://${KUBE_API_PROXY_IP}:443 \\
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
  --master=https://${KUBE_API_PROXY_IP}:443 \\
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
  --pod-infra-container-image=k8s.gcr.io/pause-amd64:3.0 \\
  --bootstrap-kubeconfig=${KUBECONFIG_DIR}/bootstrap-kubelet.conf \\
  --kubeconfig=${KUBECONFIG_DIR}/kubelet.conf \\
  --cert-dir=${K8S_PKI_DIR} \\
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

for node in {node01,node02,node03};do
cat << EOF > ${DEPLOY_DIR}/node/systemd-unit-files/kube-proxy-${node}.service
[Unit]
Description=Kubernetes Kube-Proxy Server
Documentation=https://github.com/GoogleCloudPlatform/kubernetes
After=network.target

[Service]
ExecStart=/usr/local/bin/kube-proxy \
  --logtostderr=true \
  --v=0 \
  --master=https://${KUBE_API_PROXY_IP}:443 \
  --bind-address=${IP_LIST[${node}]} \
  --hostname-override=${node} \
  --kubeconfig=${K8S_PKI_DIR}/kube-proxy.conf \
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
# 不知道为啥，这样老是启动失败，每次都是自己手动上去重启一下etcd，集群就成功了
for etcd in {etcd01,etcd02,etcd03};do
  ssh root@${etcd} "mkdir -p /var/lib/etcd"
  ssh root@${etcd} "systemctl daemon-reload"
  ssh root@${etcd} "systemctl enable etcd"
  ssh root@${etcd} "systemctl restart etcd"
done
# 应该是etcd必须是同时启动，才能成功，个人猜测

etcdctl \
  --endpoints https://${IP_LIST["etcd01"]}:2379,https://${IP_LIST["etcd02"]}:2379,https://${IP_LIST["etcd03"]}:2379 \
  --ca-file=${DEPLOY_DIR}/pki/etcd/ca.pem \
  --cert-file=${DEPLOY_DIR}/pki/etcd/peer.pem \
  --key-file=${DEPLOY_DIR}/pki/etcd/peer-key.pem \
  cluster-health

etcdctl \
  --endpoints https://${IP_LIST["etcd01"]}:2379,https://${IP_LIST["etcd02"]}:2379,https://${IP_LIST["etcd03"]}:2379 \
  --ca-file=${DEPLOY_DIR}/pki/etcd/ca.pem \
  --cert-file=${DEPLOY_DIR}/pki/etcd/peer.pem \
  --key-file=${DEPLOY_DIR}/pki/etcd/peer-key.pem \
  set /kubernetes/network/config "{ 'Network': ${POD_CLUSTER_IP_RANGE}, 'Backend': {'Type': 'vxlan'}}"
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
``` bash
mkdir -p ${DEPLOY_DIR}/kubelet-tls-bootstrap
```

创建ClusterRoleBinding允许kubelet创建CSR(certificate signing requests)
``` bash
# enable bootstrapping nodes to create CSR
cat << EOF > ${DEPLOY_DIR}/kubelet-tls-bootstrap/csr-create-rbac.yaml
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

kubectl apply -f ${DEPLOY_DIR}/kubelet-tls-bootstrap/csr-create-rbac.yaml
```

创建ClusterRoleBinding允许kubelet请求和接收证书
``` bash
# Approve all CSRs for the group "system:bootstrappers"
cat << EOF > ${DEPLOY_DIR}/kubelet-tls-bootstrap/csr-approve-rbac.yaml
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

kubectl apply -f ${DEPLOY_DIR}/kubelet-tls-bootstrap/csr-approve-rbac.yaml
```

创建ClusterRoleBinding允许kubelet重签证书
``` bash
# Approve renewal CSRs for the group "system:nodes"
cat << EOF > ${DEPLOY_DIR}/kubelet-tls-bootstrap/cert-renew-rbac.yaml
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

kubectl apply -f ${DEPLOY_DIR}/kubelet-tls-bootstrap/cert-renew-rbac.yaml
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

### 6. 查看集群节点状态
``` bash
kubectl get nodes
NAME      STATUS    ROLES     AGE       VERSION
node01    Ready     <none>    40m       v1.9.1
node02    Ready     <none>    3m        v1.9.1
node03    Ready     <none>    3m        v1.9.1
```