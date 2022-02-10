---
title: kubernetes v1.17 2.1.0 CI/CD using gitlab and helm
date: 2020-01-30 09:20:00
categories: virtualization/container
tags: [container,docker,kubernetes,flannel]
---

## 本文档背景介绍

### 1. 思路背景
虽然gitlab提供了和kubernetes的integration，但是在我看来有几个缺点：
1. 太复杂，试图增加很多功能，但是我只需要ci/cd流里面的功能
2. gitlab社区版有很多功能限制
所以，这边研究一下如何自定义环境变量在gitlab-runner上来使用helm和k8s交互，以达到CI/CD的目的。

### 2. 提供kubernetes访问资源
#### 变量环境
``` bash
DEPLOY_DIR=/root/k8s
[[ -d ${DEPLOY_DIR}/pki/kubernetes ]] || mkdir -p ${DEPLOY_DIR}/pki/kubernetes
[[ -d ${DEPLOY_DIR}/kubeconfig ]] || mkdir -p ${DEPLOY_DIR}/kubeconfig
```

#### 生成gitlab-runner访问证书
``` bash
cd ${DEPLOY_DIR}/pki/kubernetes

# 指定用户和用户组
# CN: gitlab
# O: devops
# 名称可以随便写，后面授权的时候和此处设定的保持一致即可
cat > gitlab-csr.json << EOF
{
  "CN": "gitlab",
  "hosts": [
    "your-gitlab-runner-ip01",
    "your-gitlab-runner-ip02"
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
      "O": "devops",
      "OU": "System"
    }
  ]
}
EOF

# 使用k8s集群的ca给证书签名
cfssl gencert -ca=ca.pem -ca-key=ca-key.pem -config=ca-config.json -profile=client gitlab-csr.json | cfssljson -bare gitlab
# 生成证书使用的如下文件，需要自己去获得，如果不是你自己创建的集群，请找kubernetes管理员要以下信息
# ca.pem ca-key.pem 是kubernetes集群创建的时候生成的ca
# ca-config.json 是kubernetes集群创建的时候生成的签名用的配置文件，里面保存了各种profile（server,client等）
```

#### 生成kubeconfig
``` bash
export KUBE_APISERVER="https://<your-kubernetes-api-external-ip>:443"

cd ${DEPLOY_DIR}/kubeconfig

# step 1. 生成 kubeconfig
kubectl config set-cluster kubernetes \
  --certificate-authority=${DEPLOY_DIR}/pki/kubernetes/ca.pem \
  --embed-certs=true \
  --server=${KUBE_APISERVER} \
  --kubeconfig=gitlab.conf

# step 2. 设定认证信息
kubectl config set-credentials gitlab \
  --client-certificate=${DEPLOY_DIR}/pki/kubernetes/gitlab.pem \
  --embed-certs=true \
  --client-key=${DEPLOY_DIR}/pki/kubernetes/gitlab-key.pem \
  --kubeconfig=gitlab.conf

# step 3. 设定上下文（用户、集群）
kubectl config set-context kubernetes \
  --cluster=kubernetes \
  --user=gitlab \
  --kubeconfig=gitlab.conf

# step 4. 设定当前上下文
kubectl config use-context kubernetes --kubeconfig=gitlab.conf

# step 5. 将文件进行base64加密
cat gitlab.conf | base64
# 可以通过base64命令给解析出内容来
# cat gitlab.conf | base64|base64 -d
```

#### kubernetes集群给上面用户授权
这里以测试环境举例
``` bash
# 创建测试环境的namespace
kubectl create namespace env-test

# 授权kubernetes内置的edit角色给用户
cat << EOF | kubectl apply -f -
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: devops-edit
  namespace: env-test
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: ClusterRole
  name: edit
subjects:
- apiGroup: rbac.authorization.k8s.io
  kind: Group
  name: devops
EOF
# 之所以授权给组不是授权给用户，是因为有可能后面再增加其他用户
```

### 3. gitlab创建CI/CD文件
#### Dockerfile
``` bash
FROM my-tomcat:7-jdk8-openjdk
RUN rm -rf /usr/local/tomcat/webapps/*
ADD CODE.tar.gz /usr/local/tomcat/webapps
CMD ["catalina.sh", "start", "&&", "tail", "-f", "/usr/local/tomcat/logs/catalina.out"]
```
> CODE.tar.gz 是代码编译后的CODE目录（my-tomcat是自定义的镜像，server.xml中配置webapps/CODE为代码目录）

#### .gitlab-ci.yml
``` bash
stages:
  - build
  - analysis
  - publish_image

variables:
  DOCKER_HOST: unix:///var/run/docker.sock
  DOCKER_DRIVER: overlay2

build:
  stage: build
  image: reg.myplatform.net/sonarscanner:4.2
  script:
  - wget https://repo1.maven.org/maven2/org/apache/tomcat/tomcat-jsp-api/7.0.96/tomcat-jsp-api-7.0.96.jar -O ./WebRoot/WEB-INF/lib/jsp-api.jar
  - wget https://repo1.maven.org/maven2/org/apache/tomcat/tomcat-servlet-api/7.0.96/tomcat-servlet-api-7.0.96.jar -O ./WebRoot/WEB-INF/lib/servlet-api.jar
  - echo > javafile.txt
  - find src/ -name *.java >> javafile.txt
  - jarfiles=()
  - for jar in $(find WebRoot/WEB-INF/lib -name *.jar);do jarfiles=("${jarfiles[@]}" $jar);done
  - classfile=""
  - for cf in ${jarfiles[@]};do classfile="${classfile}:${cf}";done
  - /bin/mkdir -p WebRoot/WEB-INF/classes
  - /usr/lib/jvm/java-1.7-openjdk/bin/javac -d WebRoot/WEB-INF/classes -sourcepath src -cp $classfile @javafile.txt
  artifacts:
    paths:
    - WebRoot
    expire_in: 1 day
  only:
  - master

analysis:
  stage: analysis
  image: reg.myplatform.net/sonarscanner:4.2
  script:
  - /app/bin/sonar-scanner
    -Dsonar.host.url=http://sonarqube.myplatform.net:9000 
    -Dsonar.projectKey=web 
    -Dsonar.sources=./src 
    -Dsonar.sourceEncoding=UTF-8
    -Dsonar.java.binaries=./WebRoot/WEB-INF/classes
    -Dsonar.java.libraries=./WebRoot/WEB-INF/**/*.jar
  only:
  - master

publish_image:
  stage: publish_image
  image: reg.myplatform.net/base-dind-build
  before_script:
  - docker login -u admin -p Password reg.myplatform.net
  script:
  - ls WebRoot
  - mv WebRoot CODE
  - tar zcvf CODE.tar.gz CODE
  - docker build --cache-from reg.myplatform.net/web-test:latest
    -t reg.myplatform.net/web-test:${CI_COMMIT_SHA:0:6}
    -t reg.myplatform.net/web-test:latest .
  - docker push reg.myplatform.net/web-test:${CI_COMMIT_SHA:0:6}
  only:
  - master
```