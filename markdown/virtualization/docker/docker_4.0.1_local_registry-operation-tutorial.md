---
title: 4.0.1 docker 本地registry 使用说明
date: 2017-07-07 16:51:00
categories: virtualization/docker
tags: [docker,registry]
---

### 1. 从docker HUB上拷贝镜像到本地registry
#### 1) 从docker HUB上下载镜像
``` bash
docker pull ubuntu:16.04
```

#### 2) 给下载的镜像打新tag
``` bash
docker tag ubuntu:16.04 <your-domain>/my-ubuntu
docker images
REPOSITORY                 TAG                 IMAGE ID            CREATED             SIZE
registry                   2                   c2a449c9f834        8 days ago          33.2MB
ubuntu                     16.04               d355ed3537e9        2 weeks ago         119MB
localhost:5000/my-ubuntu   latest              d355ed3537e9        2 weeks ago         119MB
```
> `<your-domain>`替换成你自己的docker-registry的域名

#### 3) 上传镜像到本地registry中
``` bash
docker push <your-domain>/my-ubuntu
```

#### 4) 移除本地镜像
``` bash
docker image remove ubuntu:16.04
docker image remove <your-domain>/my-ubuntu
```

#### 5) 从本地registry中下载镜像
``` bash
docker pull <your-domain>/my-ubuntu
```

### 2. registry服务配置
#### 1) 自动启动registry
``` bash
docker run -d \
  -p 5000:5000 \
  --restart=always \
  --name registry \
  registry:2
```
> docker使用`--restart=always`来重新启动无论因为任何原因退出的容器，当然，不包括手动执行`docker stop`命令。加上此参数开启的容器，可以尝试kill掉它的进程，会发现它会自动启动。

#### 2) 自定义端口
如果5000端口已经被使用，使用`-p 5001:5000`来指定5001端口
``` bash
docker run -d \
  -p 5001:5000 \
  --name registry-test \
  registry:2
```
但如果希望改变容器内部的运行端口， 使用`-e REGISTRY_HTTP_ADDR=0.0.0.0:5001`
``` bash
docker run -d \
  -e REGISTRY_HTTP_ADDR=0.0.0.0:5001 \
  -p 5001:5001 \
  --name registry-test \
  registry:2
```

#### 3) 挂载外部目录储存数据
``` bash
docker run -d \
  -p 5000:5000 \
  --restart=always \
  --name registry \
  -v /mnt/registry:/var/lib/registry \
  registry:2
```

#### 4) 清理tag和未被引用数据
``` bash
# step 1. 系统环境准备
sudo mkdir cleanup; sudo sh -c "chown -R username.username reg-cleanup"; cd reg-cleanup
wget https://bootstrap.pypa.io/get-pip.py; python get-pip.py
pip install virtualenv

# step 2. 清理脚本环境准备
# 下载清理脚本
wget https://raw.githubusercontent.com/andrey-pohilko/registry-cli/master/registry.py
# 创建python环境，安装清理脚本需要的依赖库
virtualenv venv; source venv/bin/activate
pip install requests
pip install www_authenticate
pip install datautil

# step 3. 执行清理
# 两个命令，第一个是清理最近10个tag之外的tag，第二个是清除未被引用的垃圾数据
echo '# 清理tag
python /data/docker/yml/reg-cleanup/registry.py -l reg_user01:VOtern93 -r http://reg.example.net --delete --num 10
# 执行garbage-collect
sudo docker exec reg registry garbage-collect /etc/docker/registry/config.yml' > cleanup.sh
sh cleanup.sh
```