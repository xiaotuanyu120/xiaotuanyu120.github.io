---
title: kubernetes v1.17 1.1.1 pull image from private registry
date: 2020-01-31 11:35:00
categories: virtualization/container
tags: [container,docker,kubernetes,registry]
---

### 1. 从私有镜像仓库拉取镜像
``` bash
# 获取auth信息
docker login --username <username> --password <password> <your-private-registry-domain>
DOCKERCONFIGJSON=`cat ~/.docker/config.json | base64 -w 0`
echo ${DOCKERCONFIGJSON}

# 创建secret
cat << EOF | kubectl apply -f -
apiVersion: v1
kind: Secret
metadata:
  name: myregistrykey
  namespace: default
data:
  .dockerconfigjson: ${DOCKERCONFIGJSON}
type: kubernetes.io/dockerconfigjson
EOF

# 配置pods使用secret
apiVersion: apps/v1
kind: Deployment
spec:
  template:
    spec:
      imagePullSecrets:
      - name: myregistrykey
```
> 参考文档：[pull-image-private-registry](https://kubernetes.io/docs/tasks/configure-pod-container/pull-image-private-registry/)