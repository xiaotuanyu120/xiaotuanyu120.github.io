---
title: ethereum 1.0.1 client geth installation
date: 2021-02-18 17:58:00
categories: blockchain/ethereum
tags: [container,podman,blockchain,ethereum]
---

### 0. geth简介
Official Go implementation of the Ethereum protocol

geth提供了很多镜像
- ethereum/client-go:latest 最新开发版本
- ethereum/client-go:stable 最新稳定版本
- ethereum/client-go:{version} 指定的稳定版本
- ethereum/client-go:release-{version} 指定的最新稳定版本
[geth 镜像版本说明](https://geth.ethereum.org/docs/install-and-build/installing-geth#run-inside-docker-container)

geth提供了以下端口
- 8545 TCP, used by the HTTP based JSON RPC API（需要使用--http启用）
- 8546 TCP, used by the WebSocket based JSON RPC API（需要使用--ws启用）
- 8547 TCP, used by the GraphQL API（需要使用--graphql启用）
- 30303 TCP and UDP, used by the P2P protocol running the network
> [geth 命令行选项文档](https://geth.ethereum.org/docs/interface/command-line-options)

geth镜像，默认储存数据文件在`/root/.ethereum`
- `--datadir`, 可以使用这个选项来指定另外的数据目录

### 1. 用systemd + podman运行geth
geth systemd文件
```
[Unit]
Description=Podman in Systemd

[Service]
Restart=on-failure
ExecStartPre=/usr/bin/rm -f /%t/%n-pid /%t/%n-cid
ExecStart=/usr/bin/podman run --conmon-pidfile  /%t/%n-pid  --cidfile /%t/%n-cid -d \
                              -it --name eth \
                              -p 8545:8545 -p 30303:30303 \
                              -v /data/container/data/eth/data:/data/eth:Z \
                              ethereum/client-go:stable \
                              --http \
                              --http.addr 127.0.0.1 \
                              --allow-insecure-unlock \
                              --http.api personal,eth,net,web3 \
                              --cache=12288 \
                              --maxpeers 80 \
                              --maxpendpeers 80 \
                              --nousb \
                              --datadir /data/eth
ExecStop=/usr/bin/sh -c "/usr/bin/podman rm -f `cat /%t/%n-cid`"
KillMode=none
Type=forking
PIDFile=/%t/%n-pid

[Install]
WantedBy=multi-user.target
```
> [http.api 列表获取方法](https://ethereum.stackexchange.com/questions/49487/is-there-a-complete-list-of-available-values-for-the-rpcapi-command-line-opt) ，其实也可以乱写，启动的时候会在日志里面提示你，有效的api是哪些。

> [geth日志需要怎么获取？](https://ethereum.stackexchange.com/questions/3229/geth-what-happened-to-logfile/3230) ，虽然按照他们的提示，用了输出重定向，但是和容器的兼容有点问题，还需要再研究，但是可以确认的是，官方移除了早期的`--logfile`选项。

### 2. 遇到的error
**报错信息：**检测不到usb设备: `Failed to enumerate USB devices hub=ledger vendor=11415 failcount=3 err="failed to initialize libusb: libusb: unknown error [code -99]"`

**解决方法：**[增加--nousb选项](https://ethereum.stackexchange.com/questions/72750/geth-account-creation-failed-to-enumerate-usb-devices)
