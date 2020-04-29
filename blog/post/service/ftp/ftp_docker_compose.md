---
title: ftp: docker-compose with nginx
date: 2020-04-24 09:22:00
categories: service/ftp
tags: [docker,docker-compose,ftp]
---
### ftp: docker-compose with nginx

---

### 1. ftp
``` yaml
version: '3.1'
services:
  ftp:
    image: stilliard/pure-ftpd:latest
    container_name: ftp
    environment:
      PUBLICHOST: 0.0.0.0
      FTP_USER_NAME: "ftpuser"
      FTP_USER_PASS: "ftppass"
      FTP_USER_HOME: "/var/www/html"
      FTP_USER_UID: 33
      FTP_USER_GID: 33
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

### 2. ftp+nginx
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
      FTP_USER_UID: 33
      FTP_USER_GID: 33
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