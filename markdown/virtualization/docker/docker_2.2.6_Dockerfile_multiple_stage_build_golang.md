---
title: 2.2.7 Containerfile multiple stage build and run golang
date: 2021-02-06 16:28:00
categories: virtualization/docker
tags: [container,golang]
---

### 0.  multiple stage Containerfile
`Containerfile`
```
FROM golang:1.15.8-alpine3.13 AS builder

WORKDIR /go/src/app
COPY . .
RUN CGO_ENABLED=0 GOOS=linux go build -a -o app .

FROM alpine:3.13.1
RUN apk update && apk add ca-certificates && rm -rf /var/cache/apk/*
WORKDIR /opt
COPY --from=builder /go/src/app .
CMD ["./app"]
```