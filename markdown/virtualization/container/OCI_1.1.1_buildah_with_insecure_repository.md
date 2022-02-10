---
title: OCI 1.1.1 buildah 推送镜像到非https的repository
date: 2020-09-08 20:24:00
categories: virtualization/container
tags: [container,podman,docker,buildah,fuse-overlayfs]
---

### 0. builah 和 非https的repository
虽然非常特别不推荐repository使用http，但是在测试环境可能会遇到这种情况。此时就需要使用如下选项
```
buildah bud --tls-verify=false ...
buildah push --tls-verify=false ...
buildah pull --tls-verify=false ...
```