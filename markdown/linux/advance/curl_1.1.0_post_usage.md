---
title: curl 1.1.0 POST usage
date: 2020-04-07 19:08:00
categories: linux/advance
tags: [linux,curl]
---

### 1. post 501 错误
``` bash
curl -X post -d "{}" https://something.com
HTTP Status 501 – Not Implemented
```
> 基于[mozilla 501 error docs](https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/501)，501错误是请求的方法不被服务器接受，定睛一看，`post`不应该是小写，换成`POST`就好了

### 2. post data 格式
``` bash
# form 格式
curl -d "param1=value1&param2=value2" -H "Content-Type: application/x-www-form-urlencoded" -X POST http://localhost:3000/data

# json格式
curl -d '{"key1":"value1", "key2":"value2"}' -H "Content-Type: application/json" -X POST http://localhost:3000/data
```
> [curl post docs](https://gist.github.com/subfuzion/08c5d85437d5d4f00e58)