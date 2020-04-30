---
title: jira 1.0.0: 安装及破解
date: 2016-02-25 10:44:00
categories: service/jira
tags: [jira]
---

### 1. 安装JDK
``` bash
# 下载解压，下载jdk8需要登录oracle官网，所以下面的命令仅供参考
wget -O jdk-8u74-linux-x64.tar.gz http://download.oracle.com/otn-pub/java/jdk/8u74-b02/jdk-8u74-linux-x64.tar.gz?AuthParam=1456382948_f9226abf85a83c6abc301550abf1aef2
tar zxvf jdk-8u74-linux-x64.tar.gz -C /usr/local/
 
# 配置JAVA环境变量
cat << EOF > /etc/profile.d/java-env.sh
JAVA_HOME=/usr/local/jdk1.8.0_74/
JRE_HOME=/usr/local/jdk1.8.0_74/jre
PATH=$PATH:$JAVA_HOME/bin:$JRE_HOME/bin
CLASSPATH=$JAVA_HOMNE/lib:$JRE_HOME/lib
EOF
source /etc/profile.d/java-env.sh
 
# 检查JAVA环境
java -version
java version "1.8.0_74"
Java(TM) SE Runtime Environment (build 1.8.0_74-b02)
Java HotSpot(TM) 64-Bit Server VM (build 25.74-b02, mixed mode)
```

### 2. 安装JIRA & 配置jira.home
``` bash
# 下载jira
# 下载地址https://www.atlassian.com/software/jira/download-archives
wget https://downloads.atlassian.com/software/jira/downloads/atlassian-jira-6.3.6.tar.gz

tar zxvf atlassian-jira-6.3.6.tar.gz -C /usr/local
ln -s /usr/local/atlassian-jira-6.3.6-standalone/ /usr/local/jira

# 设定jira.home
# （The JIRA Home Directory contains key data that help define how JIRA works. You must have a JIRA home directory pecified for your JIRA instance before you can start it. This document describes how to specify the location of he JIRA home directory for your JIRA instance.）
mkdir /var/db/jira
vi /usr/local/jira/conf/server.xml
# <Context ...>
# ...
#     <Parameter name="jira.home" value="/var/db/jira"/>
# ...
# </Context>
```

### 3. 配置数据库
``` bash
mysql -u root -p
mysql> create database jiradb charset=utf8;
mysql> grant all privileges on jiradb.* to 'jira'@'%' identified by 'urpass';
mysql> flush privileges;
 
# 拷贝mysql连接驱动到jira的库中（文件可以百度下载）
cp /root/jira/mysql-connector-java-5.1.35-bin.jar /usr/local/jira/atlassian-jira/WEB-INF/lib/
 
# 汉化（文件百度下载）
cp /root/jira/JIRA-6.3.3-language-pack-zh_CN.jar /usr/local/jira/atlassian-jira/WEB-INF/lib/
```

### 4. 启动jira
``` bash
/usr/local/jira/bin/startup.sh
```
- 用浏览器访问http://serverip:8080
- 配置数据库连接
- 配置标题和url
- 选择产品组合
- 选择"我没有一个账户"，系统会出现界面让你注册，完毕后生成你的临时授权码
- 配置管理员账号
- smtp配置，先跳过
 
### 5. 破解
``` bash
/usr/local/jira/bin/stop-jira.sh
cp atlassian-extras-2.2.2.jar /usr/local/jira/atlassian-jira/WEB-INF/lib/
cp atlassian-universal-plugin-manager-plugin-2.17.13.jar /usr/local/jira/atlassian-jira/WEB-INF/atlassian-bundled-plugins/
/usr/local/jira/bin/startup.sh
```

登陆后去到license处，在下面更新license框中填写以下信息
```
Description=JIRA: Commercial,
CreationDate=2014-09-20,
jira.LicenseEdition=ENTERPRISE,
Evaluation=false,
jira.LicenseTypeName=COMMERCIAL,
jira.active=true,
licenseVersion=2,
MaintenanceExpiryDate=2099-12-31,
Organisation=ig,
SEN=SEN-L4572887,
ServerID=BPT3-4QRK-FCRR-HEP3,
jira.NumberOfUsers=-1,
LicenseID=AAABBw0ODAoPeNptkFtLxDAQhd/zKwI+R9Kwy66FPKxthGhvtF0p4kuso0a6sUwvuP/edissyj4MD
HPOfHOYqzu0tICWeoJy4a+FzzkNwpIK7q1ICF2Ntu3tl5P3Ot89+1SNphnMPCEBwqkJTQ9y9jN+w
zxBPi2a68jW4DpQr/a0rZJS5VmuC0XOBNnjAH/s5bGFxBxABmkcqzzQu2jRTd3bEZaFZvE+AnYzR
JDYWNeDM64G9d1aPJ4TeXxOlOK7cbZbjrbNgkyGwwtg+rbvJpBkHikAR0Adytt0XzFV7R5Y+qQzV
kWZIoVK5FQsWq03YrvdkN/Ekz3S4SXlcpRswPrDdPD/aT+P1nzDMC0CFQCM9+0LlHVNnZQnSTwuR
O3eK+2gVgIUCteTs4Q3khIgrnsY64hxYB/d8bM=X02dh,
LicenseExpiryDate=2099-12-31,
PurchaseDate=2014-09-20
```
看到license过期时间变成2099年，就成功了

> 参考链接
> - http://blog.itpub.net/26230597/viewspace-1275597 
> - http://blog.163.com/super_lpc/blog/static/6777789201544426429/ 
> - 各种汉化包地址：https://translations.atlassian.com/dashboard/download?lang=zh_CN#/JIRA/6.4.9