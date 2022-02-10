---
title: openvpn: 1.0.0 openvpn安装(centos7)
date: 2020-03-04 13:53:00
categories: service/vpn
tags: [openvpn]
---

``` bash
## step 1. installation
# install openvpn
yum install -y epel-release
yum -y install openvpn easy-rsa iptables-services

mkdir /etc/openvpn/easy-rsa
cp -r /usr/share/easy-rsa/3/* /etc/openvpn/easy-rsa

## step 2. configuration
# config openvpn
cp /usr/share/doc/openvpn-*/sample/sample-config-files/server.conf /etc/openvpn

sed -i 's|^;push "redirect-gateway.*$|push "redirect-gateway def1 bypass-dhcp"|g' /etc/openvpn/server.conf
sed -i 's|^;push "dhcp-option DNS 208.67.222.222".*$|push "dhcp-option DNS 8.8.8.8"|g' /etc/openvpn/server.conf
sed -i 's|^;push "dhcp-option DNS 208.67.220.220".*$|push "dhcp-option DNS 8.8.4.4"|g' /etc/openvpn/server.conf
sed -i '/;compress lz4-v2/acompress lzo' /etc/openvpn/server.conf
sed -i 's|^;comp-lzo.*$|comp-lzo|g' /etc/openvpn/server.conf
sed -i 's|^;duplicate-cn.*$|duplicate-cn|g' /etc/openvpn/server.conf
# configuration example
################################################
# port 1194
# proto udp
# dev tun
# ca ca.crt
# cert server.crt
# dh dh2048.pem
# server 10.8.0.0 255.255.255.0
# ifconfig-pool-persist ipp.txt
# push "redirect-gateway def1 bypass-dhcp"
# push "dhcp-option DNS 8.8.8.8"
# push "dhcp-option DNS 8.8.4.4"
# duplicate-cn
# keepalive 10 120
# cipher AES-256-CBC
# compress lzo
# comp-lzo
# persist-key
# persist-tun
# status openvpn-status.log
# verb 3
# explicit-exit-notify 1
################################################


## step 3. security
# generate keys
cd /etc/openvpn/easy-rsa/
cat << EOF > vars
export KEY_COUNTRY="CN"
export KEY_PROVINCE="SH"
export KEY_CITY="SH"
export KEY_ORG="IT"
export KEY_EMAIL="example@gmail.com"
EOF
source ./vars
# 生成pki目录
./easyrsa init-pki
# 生成ca
./easyrsa build-ca nopass
# 生成server证书
./easyrsa build-server-full server nopass
# 生成Diffie-Hellman
./easyrsa gen-dh 2048
# 生成tls 认证
openvpn --genkey --secret /etc/openvpn/ta.key

cp /etc/openvpn/easy-rsa/pki/dh.pem /etc/openvpn/dh2048.pem
cp /etc/openvpn/easy-rsa/pki/ca.crt /etc/openvpn
cp /etc/openvpn/easy-rsa/pki/issued/server.crt /etc/openvpn
cp /etc/openvpn/easy-rsa/pki/private/server.key /etc/openvpn


## step 4. iptables rules
# iptables
yum install -y iptables-services
systemctl mask firewalld
systemctl enable iptables
systemctl stop firewalld
systemctl start iptables
iptables --flush

iptables -t nat -A POSTROUTING -s 10.8.0.0/24 -j MASQUERADE
iptables-save > /etc/sysconfig/iptables
echo 'net.ipv4.ip_forward = 1' >> /etc/sysctl.conf
sysctl -p

## step 5. start service
# start openvpn
systemctl enable openvpn@server.service
systemctl start openvpn@server.service
systemctl status openvpn@server.service

## step 6. prepare file for client
# generate key for client
USER=user01
cd /etc/openvpn/easy-rsa
./easyrsa build-client-full ${USER} nopass

# generate ovpn file
CA_CONTENT=`cat /etc/openvpn/ca.crt`
CLIENT_CRT_CONTENT=`cat /etc/openvpn/easy-rsa/pki/issued/${USER}.crt |sed -ne '/-BEGIN CERTIFICATE-/,/-END CERTIFICATE-/p'`
CLIENT_KEY_CONTENT=`cat /etc/openvpn/easy-rsa/pki/private/${USER}.key`
TLSAUTH_CONTENT=`cat /etc/openvpn/ta.key`
VPN_IP=`curl ip.sb`

cat << EOF > /etc/openvpn/client/${USER}.ovpn
client
proto udp
dev tun
remote 47.56.102.172 1194
tls-auth ta.key 1
remote-cert-tls server
persist-tun
persist-key
comp-lzo
verb 3
mute-replay-warnings
<ca>
${CA_CONTENT}
</ca>
<cert>
${CLIENT_CRT_CONTENT}
</cert>
<key>
${CLIENT_KEY_CONTENT}
</key>
<tls-auth>
${TLSAUTH_CONTENT}
</tls-auth>
EOF
```
> 关于ovpn文件的用法
> - windows: 下载openvpn程序，导入ovpn文件即可
> - macos: 使用tunnelblick应用程序，双击ovpn文件导入即可
> - linux: `sudo openvpn --config ~/path/to/client.ovpn`

> [参照文档： 棒棒的博客](https://qhh.me/2019/06/16/Cenos7-%E4%B8%8B%E6%90%AD%E5%BB%BA-OpenVPN-%E8%BF%87%E7%A8%8B%E8%AE%B0%E5%BD%95/)