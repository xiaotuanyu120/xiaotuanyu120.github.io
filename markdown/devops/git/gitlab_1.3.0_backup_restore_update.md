---
title: gitlab: 1.3.0 gitlab备份,恢复及升级
date: 2018-07-06 08:57:00
categories: devops/git
tags: [gitlab,backup,restore]
---

### 0. gitlab备份
#### 1) 依赖条件
- rsync安装

> [gitlab backup and restore official docs](https://docs.gitlab.com/ee/raketasks/backup_restore.html)

#### 2) 备份时间戳  
假设备份文件名称是 `1493107454_2018_04_25_10.6.4-ce_gitlab_backup.tar`(文件格式：`[TIMESTAMP]_gitlab_backup.tar`)，则备份时间戳是`1493107454_2018_04_25_10.6.4-ce`。  
备份的tar文件是在`backup_path`定义的目录中。

### 1. 创建gitlab备份
因为一直都是在用gitlab rpm安装，所以下面只讨论yum或rpm安装的gitlab的文件备份方式
#### 1) 手动备份
``` bash
gitlab-rake gitlab:backup:create

# 如果是docker版本的备份
docker exec -it <name of container> gitlab-backup create
# 如果gitlab是12.1和之前的版本
# docker exec -it <name of container> gitlab-rake gitlab:backup:create
```

#### 2) cron定时备份
``` bash
sudo su -
crontab -e
```

增加下面的内容到cron定时任务中
```
0 2 * * * /opt/gitlab/bin/gitlab-rake gitlab:backup:create CRON=1
```

在`/etc/gitlab/gitlab.rb`中可以配置定时产生的备份文件保留时间
```
# limit backup lifetime to 7 days - 604800 seconds
gitlab_rails['backup_keep_time'] = 604800
```

> 注意点：除了生成数据备份之外，认证文件也需要备份一下`/etc/gitlab/gitlab-secrets.json`

### 2. 恢复gitlab备份
``` bash
# 关闭访问数据库的服务
gitlab-ctl stop unicorn
gitlab-ctl stop sidekiq

# 恢复数据
gitlab-rake gitlab:backup:restore BACKUP=1493107454_2018_04_25_10.6.4-ce

# 如果是docker版本恢复
# docker容器中的git用户的uid和gid是998，可以通过下面命令查看
# docker exec -it <cotainer-name> id git
# 得到git用户的uid后，需要给备份tar文件修改属主属组，不然会有权限报错
chown 998.998 </path/to/your-git-backup-file>
docker exec -it <name of container> gitlab-backup restore BACKUP=1493107454_2018_04_25_10.6.4-ce
# 如果gitlab是12.1和之前的版本
# docker exec -it <cotainer-name> gitlab-rake gitlab:backup:restore BACKUP=1493107454_2018_04_25_10.6.4-ce
```
> 备份恢复必须要同样的gitlab版本

> BACKUP=timestamp_of_backup，不需要指定文件名称，只需要指定timestamp就可以


### 3. gitlab 升级
参考文档
- [官方升级推荐指南](https://docs.gitlab.com/ee/policy/maintenance.html#upgrade-recommendations)
- [官方docker升级指南](https://docs.gitlab.com/omnibus/docker/README.html#upgrade-gitlab-to-newer-version)
- [官方论坛问答](https://forum.gitlab.com/t/updating-gitlab-ce-9-1-2-ce-0-to-11-4-5-ce-0-on-debian-jessie/21117/2)

总结就是，
- 官方推荐先升级小版本到主版本的最新，例如你现在是9.4.5，你就升级到9版本的最新稳定版本(9.5.10)
- 然后升级到下一个大版本的第一个初始稳定版本，例如9.5.10升级到10.0.0；接着进行同样的循环，在升级到10版本里面的最新稳定版本

> 值得注意的是：gitlab每次升级完，第一次启动，会自动进行升级动作。所以只需要按照官方推荐的升级节奏，小版本升级 - 大版本升级，即可