---
title: pure-ftpd: 1.1.0 docker-compose with nginx
date: 2020-04-24 09:22:00
categories: service/ftp
tags: [docker,docker-compose,ftp]
---

### 1. docker-compose of pure-ftpd
``` yaml
version: '3.1'

services:
  nginx:
    image: nginx:1.16.1
    container_name: nginx
    volumes:
      - /data/docker/data/ftp/html:/var/www/html
      - /data/docker/runtime/nginx/conf.d:/etc/nginx/conf.d
      - /data/docker/runtime/nginx/ssl:/etc/nginx/ssl
      - /data/docker/data/nginx/logs:/etc/nginx/logs
    ports:
      - "80:80"
      - "443:443"

  ftp:
    image: stilliard/pure-ftpd:latest
    container_name: ftp
    environment:
      PUBLICHOST: 0.0.0.0
      FTP_USER_NAME: "ftpuser"
      FTP_USER_PASS: "ftppass"
      FTP_USER_HOME: "/var/www/html"
      FTP_PASSIVE_PORTS: "30000:30050"
      FTP_MAX_CONNECTIONS: "20"
      FTP_MAC_CLIENTS: "10"
    volumes:
      - /data/docker/data/ftp/html:/var/www/html
      - /data/docker/runtime/ftp/userdata:/etc/pure-ftpd/passwd
    ports:
      - "21:21"
      - "30000-30050:30000-30050"

# networks:
#   default:
#     external:
#       name: production
```
> 此镜像的环境变量说明(详细的请查看[源码](https://github.com/stilliard/docker-pure-ftpd))
> - `PUBLICHOST`: 对应的是`-P`，可配置ip或者域名，含义是在回应客户端`PASV/EPSV/SPSV`命令时返回哪个ip。如果是nat环境，可以设定为nat环境的公网出口ip。
> - `FTP_USER_UID`: 对应的是`pure-pw`里面的`-u`，如果不指定，默认的就是ftpuser（镜像作者设定的），uid是1000
> - `FTP_USER_GID`: 对应的是`pure-pw`里面的`-g`，如果不指定，默认的就是ftpgroup，gid是1000
> - `FTP_USER_NAME`,`FTP_USER_PASS`,`FTP_USER_HOME`，包括上面的`FTP_USER_UID`和`FTP_USER_GID`，其实对应的都是`pure-pw`创建虚拟用户时用到的信息。
> - `FTP_MAX_CONNECTIONS`: 对应的是`-C`，含义是每个ip的最大连接的客户端数目
> - `FTP_MAX_CLIENTS`: 对应的是`-c`，含义是最大连接的客户端数目(所以说，端口数目设定为和这个数字一样多就好了)

> docker镜像里面的环境变量选项是镜像作者自定义的，详细的说明还是要参照[pure-ftpd选项说明](https://download.pureftpd.org/pub/pure-ftpd/doc/README)

> 挂载的ftp数据目录，需要设定uid和gid为`FTP_USER_UID`和`FTP_USER_GID`，默认是`ftpuser`和`ftpgroup`的`1000`和`1000`

### 2. enable tls
首先我们要明确，我们要搞得是ftps(tls+ftp)，而不是sftp(过ssh通道)

pure-ftpd开启tls有几个条件
- 编译时有`--with-tls`选项，其实就是把openssl的库编译进去
- 自生成或者买一个pem的秘钥（crt和key内容可分开为两个文件，也可合并为一个文件，一般选择合并在一起的pem。我们的例子也选用合并在一起的pem）
- pure-ftpd启动时增加`--tls 1/2`的选项（1是mixed安全和非安全两种模式，2是强制全部是安全模式）

此处的镜像是用这样的逻辑来开启tls的
- 如果你映射了pem证书到容器`/etc/ssl/private/pure-ftpd.pem`，它会自动给你添加`--tls 1`选项
- 如果你指定了`--tls 1/2`选项，且`/etc/ssl/private/pure-ftpd.pem`不存在，它会自动生成一个证书文件

我个人倾向于自己生成，然后挂载进去
``` bash
# ssl key generate
mkdir -p /path/to/private
openssl dhparam -out /path/to/private/pure-ftpd-dhparams.pem 2048
openssl req -x509 -nodes -newkey rsa:2048 -sha256 \
  -keyout /path/to/private/pure-ftpd.pem \
  -out /path/to/private/pure-ftpd.pem
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

chmod 600 /path/to/private/*.pem
```
> 所有选项不要空着，不然有可能遇到docker的252 exit code错误
> 手动去容器里面排查了一下，提示的是“421 证书文件不存在啥的”，但是查看了pure-ftpd的源码，发现不是文件不存在，而是openssl的库解析证书的时候报错了。猜测是因为生成证书的时候，有的选项空着没填内容有关，而且国家那里必须是两位字母。
``` c
static void tls_load_cert_file(const char * const cert_file,
                               const char * const key_file)
{
    if (SSL_CTX_use_certificate_chain_file(tls_ctx, cert_file) != 1) {
        die(421, LOG_ERR,
            MSG_FILE_DOESNT_EXIST ": [%s]", cert_file);
    }
    if (SSL_CTX_use_PrivateKey_file(tls_ctx, key_file,
                                    SSL_FILETYPE_PEM) != 1) {
        die(421, LOG_ERR,
            MSG_FILE_DOESNT_EXIST ": [%s]", key_file);
    }
    if (SSL_CTX_check_private_key(tls_ctx) != 1) {
        tls_error(LINE, 0);
    }
}
```

docker-compose的yaml文件需要增加内容
``` yaml
    volumes:
      - /path/to/private:/etc/ssl/private
```