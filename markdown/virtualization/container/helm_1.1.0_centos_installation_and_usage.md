---
title: helm 1.1.0 安装（centos 7）及使用
date: 2020-01-09 15:04:00
categories: virtualization/container
tags: [container,kubernetes]
---

### 0. 什么是helm？
helm是kubernetes的一个包管理工具，类似于yum之于rhel，apt之于debian。

三个主要概念：
- Chart，是helm的包。它包含了在Kubernetes集群中运行的应用程序、工具或服务所需的所有资源的定义。类似于rpm和dpkg
- Repository，用于保存和分享charts的仓库。
- Release，是在kubernetes集群中运行的charts的实例。一个charts可以被安装多次，每次都会生成一个新实例。当然，实例名称都是唯一的。

### 1. 安装helm
``` bash
curl -fsSL -o get_helm.sh https://raw.githubusercontent.com/helm/helm/master/scripts/get-helm-3
chmod 700 get_helm.sh
./get_helm.sh
```

### 2. 使用helm
搜索chart
``` bash
## SEARCH
# 在helm hub中搜索包，helm hub包含多个repo的包资源
helm search hub [package-name]

# 在本地repo（helm repo add）中搜索包
helm search repo [package-name]

# 注意点：
# - 不包含package-name时会列出所有可用的包
# - package-name可以是不完整的包名称
```

下载chart
``` bash
helm fetch repo-name/[package-name]
```

安装chart
``` bash
## INSTALL
# Usage:
#   helm install [NAME] [CHART] [flags]
helm install happy-panda stable/mariadb

# 如果不想指定release的名称，可以使用如下参数，会自动生成一个release名称
helm install stable/mariadb --generate-name

# 注意点：
# - Helm不会等到所有资源都运行后才退出

# 更多安装方式
# - 常规在repo里面安装，就是上面提到的
# - 从本地chart包安装，helm install foo foo-0.1.1.tgz
# - 从chart包解压缩出来的目录上安装，helm install foo path/to/foo
# - 从完整的chart包url上安装，helm install foo https://example.com/charts/foo-1.2.3.tgz
```

查看release状态和配置
``` bash
## STATUS
# 查看release的状态或重读它的配置
helm status happy-panda
```

在安装chart之前自定义参数
``` bash
# 输出可以自定义的选项
helm show values stable/mariadb
# ......
## Create a database user
## ref: https://github.com/bitnami/bitnami-docker-mariadb/blob/master/README.md#creating-a-database-user-on-first-run
##
# mariadbUser:
# mariadbPassword:
# ......

# 使用-f指定自定义内容
echo '{mariadbUser: user0, mariadbDatabase: user0db}' > config.yaml
helm install -f config.yaml stable/mariadb

# 使用--set在命令行指定自定义的变量
--set a=b,c=d
# a: b
# c: d

--set outer.inner=value
# outer:
#   inner: value

--set name={a, b, c}
# name:
#   - a
#   - b
#   - c

--set servers[0].port=80,servers[0].host=example
# servers:
#   port: 80
#   host: example

--set name=value1\,value2
# name: "value1,value2"

--set nodeSelector."kubernetes\.io/role"=master
# nodeSelector:
#   kubernetes.io/role: master
```

升级release  
当需要修改release配置，或者想要升级release使用的chart版本时，可以升级release  
由于Kubernetes chart可能很大且很复杂，因此Helm尝试执行侵入性最小的升级。它将仅更新自上一次release基础上变动的内容。
``` bash
helm upgrade -f panda.yaml happy-panda stable/mariadb

# 查看刚才做出的修改
helm get values happy-panda
```

回退release  
有升级就有回退
``` bash
# helm rollback [RELEASE] [REVISION]
helm rollback happy-panda 1

# 可以通过helm history [RELEASE]来查看历史
helm history happy-panda
```

删除release
``` bash
helm uninstall happy-panda

# 删除，但是存在保留历史
helm uninstall happy-panda --keep-history
```

查看release列表
``` bash
helm list

# 可以查看使用--keep-history删除的release
helm list --uninstalled

# 查看所有的release，包含--keep-history删除的release
helm list --all
```

repo相关命令
``` bash
helm repo list
helm repo add dev https://example.com/dev-charts
helm repo update
helm repo remove dev
```

### 3. 创建自己的chart
``` bash
# 创建自己的chart，会在当前目录生成一个和chart同名的目录
helm create deis-workflow

# 目录结构如下
tree deis-workflow/
deis-workflow/
├── charts
├── Chart.yaml
├── templates
│   ├── deployment.yaml
│   ├── _helpers.tpl
│   ├── ingress.yaml
│   ├── NOTES.txt
│   ├── serviceaccount.yaml
│   ├── service.yaml
│   └── tests
│       └── test-connection.yaml
└── values.yaml

# 可以自定义里面的值

# 自定义修改好之后，可以打包成为一个chart
helm package deis-workflow
# deis-workflow-0.1.0.tgz

# 可以这样安装自定义的包
helm install deis-workflow ./deis-workflow-0.1.0.tgz
```