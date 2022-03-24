
---
title: haproxy: 使用docker-compose启动haproxy
date: 2022-03-24 10:45:00
categories: service/haproxy
tags: [haproxy]
---

## 1. 使用docker-compose启动haproxy
``` bash
DOCKER_YML_DIR=/data/docker/yml
DOCKER_RUNTIME_DIR=/data/docker/runtime

mkdir -p ${DOCKER_YML_DIR}
cat << EOF > ${DOCKER_YML_DIR}/docker-compose-haproxy.yml
version: '3'
services:
  haproxy:
    container_name: haproxy
    image: haproxy
    ports:
      - 443:6443
    volumes:
      - /data/docker/runtime/haproxy/etc/haproxy.cfg:/usr/local/etc/haproxy/haproxy.cfg
EOF

mkdir -p ${DOCKER_RUNTIME_DIR}/haproxy/etc
cat << EOF > ${DOCKER_RUNTIME_DIR}/haproxy/etc/haproxy.cfg
frontend front
  bind 0.0.0.0:6443
  mode tcp
  option tcplog
  timeout client 1h
  default_backend back

backend back
  mode tcp
  timeout server 1h
  option tcplog
  option tcp-check
  balance roundrobin
  default-server inter 10s downinter 5s rise 2 fall 2 slowstart 60s maxconn 250 maxqueue 256 weight 100
  server RS1 <IP>:<PORT> check
  server RS2 <IP>:<PORT> check
  server RS3 <IP>:<PORT> check
EOF

docker-compose -f /data/docker/yml/docker-compose-haproxy.yml up -d
```