---
title: nginx: 2.1.6 configuration proxy_pass for xmpp
date: 2021-01-21 22:01:00
categories: service/nginx
tags: [nginx,xmpp,stream]
---

### 0. what is xmpp?
细节请看[官方文档](https://xmpp.org/about/technology-overview.html)。我个人接触到的就是，使用xmpp可以开发IM应用。

### 1. 使用nginx反向代理xmpp
```
stream {
	# webserver
	upstream httpserver {
		server localhost:8443;
	}

	# xmppserver
	upstream xmppserver {
		server localhost:5666;
	}

	map $ssl_preread_alpn_protocols $upstream {
		default httpserver;
		"xmpp-client" xmppserver;
	}

	server {
		listen 5666;
		ssl_preread on;
		proxy_pass $upstream
	}
}
```