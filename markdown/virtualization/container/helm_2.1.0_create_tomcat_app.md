---
title: helm 2.1.0 从零开始创建tomcat的charts
date: 2020-01-30 18:00:00
categories: virtualization/container
tags: [container,kubernetes,helm,chartmuseum]
---

### 0. 问题背景
为什么不用stable中的tomcat？呵呵，看不懂，不可控。

个人思路是使用tomcat官方docker镜像先提前配置好，然后只需要给helm传参（image），其他的helm参数可以先提前写好模板。

### 1. 从零开始helm创建tomcat的charts
#### 背景
假设我们有一个前后端分离项目，前端项目web-frontend已经存在，后端项目我们称其为web

#### 开始创建
创建charts模板web
``` bash
helm create web
```

修改service.yaml
`vim web/templates/service.yaml`
``` yaml
apiVersion: v1
kind: Service
spec:
  type: {{ .Values.service.type }}
  ports:
    - port: {{ .Values.service.port }}
      targetPort: {{ .Values.template.containerPort }}
```

修改deployment.yml
`vim web/templates/deployment.yaml`
``` yaml
apiVersion: apps/v1
kind: Deployment
spec:
  template:
    spec:
      containers:
          image: {{ .Values.image.repository }}
          ports:
            - name: http
              containerPort: {{ .Values.template.containerPort }}
              protocol: TCP
```

修改values.yaml
`vim web/values.yaml`
``` yaml
imagePullSecrets:
  - name: myregistrykey
serviceAccount:
  create: false
securityContext:
  runAsNonRoot: true
  runAsUser: 999
  runAsGroup: 999
template:
  containerPort: 8080
service:
  type: ClusterIP
  port: 80
ingress:
  enabled: true
  hosts:
    - host: chart-example.local
      paths:
      - path:
          - /
```
> imagePullSecrets，是用来指定从私有镜像仓库下载镜像的auth信息，详情可以参照:
> [pull_image_from_private_registry](/virtualization/container/kubernetes_v1.17_1.1.1_pull_image_from_private_registry.html)

#### 测试启动
``` bash
helm upgrade --install my-release ./web --set image.repository=<image>
```