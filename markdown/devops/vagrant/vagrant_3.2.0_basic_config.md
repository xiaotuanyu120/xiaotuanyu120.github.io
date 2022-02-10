---
title: vagrant: 3.2.0 基本配置
date: 2016-09-30 15:40:00
categories: devops/vagrant
tags: [devops,vagrant]
---

### 1. 基本配置

#### 1) hostname配置
``` ruby
config.vm.hostname = "hostname"
```

#### 2) 网络配置
``` ruby
config.vm.network "private_network", ip: "11.11.11.11"
config.vm.network "public_network", ip: "192.168.0.11"

# 不需要自动配置
config.vm.network "private_network", ip: "11.11.11.11", auto_config: false

# 自动配置宿主机的dns到虚拟机的配置
config.vm.provider :virtualbox do |vb|
  vb.customize ["modifyvm", :id, "--natdnshostresolver1", "on"]
  vb.customize ["modifyvm", :id, "--natdnsproxy1", "on"]
end
```

#### 3) 内存、CPU、视频显示配置
``` ruby
config.vm.provider "virtualbox" do |vb|
  # Display the VirtualBox GUI when booting the machine
  vb.gui = true

  vb.memory = 2048
  vb.cpus = 2
end
```
> 此配置在多主机配置中，可以作为主机配置的子配置项
``` ruby
config.vm.define "clouderaN2" do |clouderaN2|
  clouderaN2.vm.hostname = "cloudera-n2"
  clouderaN2.vm.network "private_network", ip: "192.168.33.62"
  config.vm.provider "virtualbox" do |vb|
    vb.memory = "2048"
  end
end
```

#### 4) 同步目录
``` ruby
# 默认把host机器的Vagrantfile所在目录和虚机的/vagrant自动同步
  config.vm.synced_folder "d:/local/dir", "/vm/dir/"
# 也可以用nfs，听说会比较快
  config.vm.synced_folder "D:/go/src/mattermost-server", "/root/go/src/mattermost-server", type: "nfs"
  config.vm.synced_folder "D:/go/src/mattermost-webapp", "/root/go/src/mattermost-webapp", type: "nfs"
```

#### 5) 增加新硬盘
首先检测自己box支持的存储控制器类型
```
VBoxManage showvminfo <vmname> | findstr "Storage Controller"
Storage Controller Name (0):            IDE
Storage Controller Type (0):            PIIX4
Storage Controller Instance Number (0): 0
Storage Controller Max Port Count (0):  2
Storage Controller Port Count (0):      2
Storage Controller Bootable (0):        on
Audio:                       enabled (Driver: DSOUND, Controller: AC97, Codec: STAC9700)
```

在Vagrantfile增加以下内容
```
  config.vm.provider "virtualbox" do |vb|
    
    file_to_disk = 'disk2.vdi'
    unless File.exist?(file_to_disk)
      # 50 GB
      vb.customize ['createhd', '--filename', file_to_disk, '--size', 50 * 1024]
    end
    vb.customize ['storageattach', :id, '--storagectl', 'IDE', '--port', 1, '--device', 0, '--type', 'hdd', '--medium', file_to_disk]
  end
```
> 注意在`--storagectl`参数上增加上面检查出来对应的存储控制器名称

> 然后就会发现，在vagrant目录出现硬盘文件