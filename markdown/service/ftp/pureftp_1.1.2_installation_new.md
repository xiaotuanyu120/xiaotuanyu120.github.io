---
title: pureftpd: 1.1.2 安装(2020新版) - 1.0.49
date: 2015-01-22 02:54:00
categories: service/ftp
tags: [ftp]
---

### 1. 准备工作
``` bash
# env var
PURE_FTPD_UID=1000
PURE_FTPD_GID=1000
PURE_FTPD_USER=pureftpd
PURE_FTPD_GROUP=pureftpd
PURE_FTPD_HOMEDIR=/var/www/html

PURE_FTPD_VER=1.0.49
PURE_FTPD_DIR=/usr/local/pure-ftpd-${PURE_FTPD_VER}

# install base packages
yum install gcc make wget openssl-devel -y

# prepare pure-ftpd's process running user
mkdir -p ${PURE_FTPD_HOMEDIR%/*}
groupadd -g ${PURE_FTPD_GID} ${PURE_FTPD_GROUP}
useradd -g ${PURE_FTPD_GROUP} -u ${PURE_FTPD_UID} -d ${PURE_FTPD_HOMEDIR} -s /sbin/nologin ${PURE_FTPD_USER}
```

### 2. 编译安装
``` bash
# download, compile and install
wget https://download.pureftpd.org/pub/pure-ftpd/releases/pure-ftpd-${PURE_FTPD_VER}.tar.gz
tar zxf pure-ftpd-${PURE_FTPD_VER}.tar.gz
cd pure-ftpd-${PURE_FTPD_VER}
./configure --prefix=${PURE_FTPD_DIR} \
  --with-tls --with-puredb \
  --with-certfile=${PURE_FTPD_DIR}/etc/ssl/private/pure-ftpd.pem \
  --with-keyfile=${PURE_FTPD_DIR}/etc/ssl/private/pure-ftpd.pem
make install-strip

# prepare runtime env
ln -s ${PURE_FTPD_DIR} ${PURE_FTPD_DIR%/*}/pure-ftpd
export PATH=$PATH:${PURE_FTPD_DIR}/bin:${PURE_FTPD_DIR}/sbin
```

### 3. 一般配置
``` bash
# env vars
MAX_CLIENT_NUM=50
MAX_CLIENT_PER_IP=10

# 禁止匿名用户访问
sed -i -r "s|^NoAnonymous +no ?+$|NoAnonymous yes|g" ${PURE_FTPD_DIR}/etc/pure-ftpd.conf
# 启用虚拟用户配置
sed -i -r "s|^# ?+PureDB +/etc/pureftpd.pdb ?+$|PureDB ${PURE_FTPD_DIR}/etc/pureftpd.pdb|g" ${PURE_FTPD_DIR}/etc/pure-ftpd.conf
# 关闭pam认证
sed -i -r "s|^# ?+PAMAuthentication +yes ?+$|# PAMAuthentication yes|g" ${PURE_FTPD_DIR}/etc/pure-ftpd.conf
# 设定最大用户数
sed -i -r "s|^#?+ ?+MaxClientsNumber +[[:digit:]]+ ?+$|MaxClientsNumber ${MAX_CLIENT_NUM}|g" ${PURE_FTPD_DIR}/etc/pure-ftpd.conf
# 设定每个ip最大用户数
sed -i -r "s|^#?+ ?+MaxClientsPerIP +[[:digit:]]+ ?+$|MaxClientsPerIP ${MAX_CLIENT_PER_IP}|g" ${PURE_FTPD_DIR}/etc/pure-ftpd.conf
```

### 4. ssl key生成和配置
``` bash
# ssl key generate
mkdir -p ${PURE_FTPD_DIR}/etc/ssl/private
openssl dhparam -out ${PURE_FTPD_DIR}/etc/ssl/private/pure-ftpd-dhparams.pem 2048
openssl req -x509 -nodes -newkey rsa:2048 -sha256 \
  -keyout ${PURE_FTPD_DIR}/etc/ssl/private/pure-ftpd.pem \
  -out ${PURE_FTPD_DIR}/etc/ssl/private/pure-ftpd.pem
# -----
# You are about to be asked to enter information that will be incorporated
# into your certificate request.
# What you are about to enter is what is called a Distinguished Name or a DN.
# There are quite a few fields but you can leave some blank
# For some fields there will be a default value,
# If you enter '.', the field will be left blank.
# -----
# Country Name (2 letter code) [XX]:CN
# State or Province Name (full name) []:ShangHai
# Locality Name (eg, city) [Default City]:Shanghai      
# Organization Name (eg, company) [Default Company Ltd]:test
# Organizational Unit Name (eg, section) []:IT
# Common Name (eg, your name or your server's hostname) []:localhost
# Email Address []:test@localhost.com

chmod 600 ${PURE_FTPD_DIR}/etc/ssl/private/*.pem

# ssl configuration
sed -i -r "s|^# ?+TLS +[[:digit:]] ?+$|TLS 1|g" ${PURE_FTPD_DIR}/etc/pure-ftpd.conf
sed -i -r "s|^# ?+TLSCipherSuite +HIGH ?+$|TLSCipherSuite HIGH:MEDIUM:+TLSv1:\!SSLv2:\!SSLv3|g" ${PURE_FTPD_DIR}/etc/pure-ftpd.conf
sed -i -r "s|^# ?+CertFile +/etc/ssl/private/pure-ftpd.pem ?+$|CertFile ${PURE_FTPD_DIR}/etc/ssl/private/pure-ftpd.pem|g" ${PURE_FTPD_DIR}/etc/pure-ftpd.conf
```

### 5. 配置虚拟用户
``` bash
PURE_FTPD_LOGIN=ftpuser01
PURE_FTPD_LOGIN_PASS=123456
PURE_FTPD_PASSFILE=${PURE_FTPD_DIR}/etc/pureftpd.passwd
PURE_FTPD_DB=${PURE_FTPD_DIR}/etc/pureftpd.pdb

mkdir -p ${PURE_FTPD_HOMEDIR}/${PURE_FTPD_LOGIN}
chown -R ${PURE_FTPD_UID}.${PURE_FTPD_GID} ${PURE_FTPD_HOMEDIR}/${PURE_FTPD_LOGIN}

TMP_PASSFILE=$(mktemp)
echo -e "${PURE_FTPD_LOGIN_PASS}\n${PURE_FTPD_LOGIN_PASS}" > ${TMP_PASSFILE}
pure-pw useradd ${PURE_FTPD_LOGIN} -f ${PURE_FTPD_PASSFILE} -u ${PURE_FTPD_UID} -g ${PURE_FTPD_GID} -d ${PURE_FTPD_HOMEDIR}/${PURE_FTPD_LOGIN} < ${TMP_PASSFILE}

pure-pw mkdb ${PURE_FTPD_DB} -f ${PURE_FTPD_PASSFILE}
```

### 6. 启动pure-ftpd
``` bash
# prepare systemd unit file 
cat << EOF > /usr/lib/systemd/system/pure-ftpd.service
# pure-ftpd binary startup for DirectAdmin servers
# To reload systemd daemon after changes to this file:
# systemctl --system daemon-reload
[Unit]
Description=Pure-FTPd FTP server
After=syslog.target network.target

[Service]
Type=forking
ExecStart=${PURE_FTPD_DIR}/sbin/pure-ftpd ${PURE_FTPD_DIR}/etc/pure-ftpd.conf

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl restart pure-ftpd
```