---
title: helm 1.1.1 chartmuseum
date: 2020-01-23 14:39:00
categories: virtualization/container
tags: [container,kubernetes,helm,chartmuseum]
---

### 0. 什么是chartmuseum?
[chartmuseum](https://github.com/helm/chartmuseum)是一个开源的helm chart本地仓库

### 1. [安装chartmuseum](https://github.com/helm/charts/tree/master/stable/chartmuseum)？
``` bash
helm repo add stable https://kubernetes-charts.storage.googleapis.com
helm repo update
helm fetch stable/chartmuseum
tar zxvf chartmuseum-2.7.0.tgz
cd chartmuseum
```

### 2. 自定义chartmuseum
``` yaml
env:
  open:
    # 启用api调用，不然会限制所有/api的访问
    DISABLE_API: false
    # 允许重复上传chart包
    ALLOW_OVERWRITE: true
  secret:
    # Redis requirepass server configuration
    CACHE_REDIS_PASSWORD: redisp@ssw0rd
# 因为要用pv，这里设定一个有pv硬盘提供的节点
nodeSelector:
  storagenode: glusterfs
persistence:
  enabled: true
  # 指定storageclass
  storageClass: "glusterfs-storage"
# 用ingress会比较方便，记住域名就可以了
ingress:
  enabled: true
  hosts:
      # 指定访问域名
    - name: chartmuseum.domain1.com
      path: /
      tls: false
```

### 3. 使用chartmuseum
``` bash
# 查看ingress-controller service的nodeport端口，这里是31253
kubectl get svc -n ingress-nginx
NAME            TYPE       CLUSTER-IP       EXTERNAL-IP   PORT(S)                      AGE
ingress-nginx   NodePort   10.244.137.221   <none>        80:31253/TCP,443:32111/TCP   7d1h

# 把刚才指定的域名指定解析
kubectl get nodes -o wide
# 获得节点的ip
echo "node-ip chartmuseum.domain1.com" >> /etc/hosts

# 把刚才的chartmuseum打包，先将version: 2.7.0，增加一个patch版本，改成2.7.1
helm package .
# 会生成chartmuseum-2.7.0.tgz
# 上传到自己的chartmuseum
curl --data-binary "@chartmuseum-2.7.0.tgz" http://chartmuseum.domain1.com:31253/api/charts
```

### 4. 使用helm-push插件
``` bash
# step 1. install helm-push
helm plugin install https://github.com/chartmuseum/helm-push

# step 2. add chartmuseum repo
helm repo add chartmuseum http://chartmuseum.domain1.com:31253

# step 3.a push directory
cd .. && cat chartmuseum/Chart.yaml|grep version

helm push chartmuseum/ chartmuseum
# 可以手动指定version
# helm push chartmuseum/ --version="version-string" chartmuseum

# step 3.b push tar file
cd chartmuseum
helm push chartmuseum-2.7.0.tgz chartmuseum
```