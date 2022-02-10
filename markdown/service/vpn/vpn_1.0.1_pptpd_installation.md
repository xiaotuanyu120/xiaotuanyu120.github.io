---
title: pptpd: 1.0.1 openvpn安装(centos7)
date: 2020-03-05 09:06:00
categories: service/vpn
tags: [openvpn]
---

``` bash
## step 0. preparation
# check env

# 检查内核是否支持pptp vpn
modprobe ppp-compress-18 && echo success
# 输出success

# 检查是否开启tun/tap
cat /dev/net/tun
# 输出cat: /dev/net/tun: File descriptor in bad state

# 检查是否开启ppp
cat /dev/ppp
# 输出cat: /dev/ppp: No such device or address

## step 1. installment
yum install epel-release -y
yum install ppp pptpd net-tools iptables-services -y

## step 2. configuration

sed -i 's|^#localip 192.168.0.1.*$|localip 10.0.10.1|g' /etc/pptpd.conf
sed -i 's|^#remoteip 192.168.0.234-238,192.168.0.245.*$|remoteip 10.0.10.2-254|g' /etc/pptpd.conf

sed -i 's|^#ms-dns 10.0.0.1.*$|ms-dns 8.8.8.8|g' /etc/ppp/options.pptpd
sed -i 's|^#ms-dns 10.0.0.2.*$|ms-dns 8.8.4.4|g' /etc/ppp/options.pptpd

echo "user_test1       pptpd   123456             *" >> /etc/ppp/chap-secrets

## step 3. kernel optimize
echo net.ipv4.ip_forward = 1 >> /etc/sysctl.conf
sysctl -p

## step 4. iptables
systemctl stop firewalld
systemctl disable firewalld
systemctl enable iptables
iptables -F
iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE
iptables-save > /etc/sysconfig/iptables

## step 5. vpn start
systemctl start pptpd
systemctl enalbe pptpd
```

> [参照文档： 腾讯云文章](https://cloud.tencent.com/developer/article/1446826)