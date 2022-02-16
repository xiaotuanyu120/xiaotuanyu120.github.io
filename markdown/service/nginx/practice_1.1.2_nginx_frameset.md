---
title: 实践 1.1.2 使用frameset实现URL原地跳转
date: 2016-06-16 08:30:00
categories: service/nginx
tags: [nginx,frameset]
---

## 0. 需求
用户访问网站的完整功能时，即使页面发生跳转，浏览器地址栏中的URL不要发生变化。

## 1. 实现思路
很明显需要用HTML的frame这个tag来做，frame中的内容是加载的其他资源，它发生跳转的时候，并不会影响frame所在的静态资源界面的URL。
 
效果：
访问url完全不会随着你访问资源的变化而变化，只是作为一个frame访问
 
## 2. 实现
``` html
<html>
<head>
<meta http-equiv=Content-Type content="text/html;charset=GB2312" />
<title>outside.example.com</title>
</head>
 
<script LANGUAGE="JavaScript"> 
window.status='';
</script>
 
<frameset rows="0,*" framespacing="0" border="0" frameborder="0">
    <frame name="header" scrolling="no" noresize target="main" src="">
    <frame name="main" src="http://inside.example.com" scrolling="auto">
    <noframes>
    <body>
        <p></p>
    </body>
    </noframes>
</frameset>
</html>
```
 
```
server {
    listen 80;
    server_name outside.example.com;
    index index.html;
    location / {
        root /data/index;
    }
    access_log  logs/access.log access;
}
```