---
title: ftp: 1.1.0 客户端lftp
date: 2015-01-22 02:54:00
categories: service/ftp
tags:
---
### ftp: 1.1.0 客户端lftp

### 1. lftp客户端使用
``` bash
# 安装lftp
yum install lftp -y
# 登录ftp server
lftp ftp01@192.168.0.26
Password:

# 查看、创建、上传、下载
# 显示帮助信息
lftp ftp01@192.168.0.26:~> help
# 上传当前目录文件
lftp ftp01@192.168.0.26:~> put 1.log
24 bytes transferred
# 上传其他目录的文件
lftp ftp01@192.168.0.26:/> put ./fugai/pass
1531 bytes transferred  
# 创建目录
lftp ftp01@192.168.0.26:/> mkdir ftptest
mkdir ok, 'ftptest' created
# 移动和重命名
lftp ftp01@192.168.0.26:/> mv 1.log ./ftptest/111.log
rename successful
# 下载，默认是下载到本目录
lftp ftp01@192.168.0.26:/> get ./ftptest/111.log
24 bytes transferred
# 下载到指定目录
lftp ftp01@192.168.0.26:/> get ./pass -o ./aa
1531 bytes transferred
```
