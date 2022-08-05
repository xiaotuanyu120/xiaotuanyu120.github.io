---
title: django
date: 2015-09-25 09:16:00
categories: python/basic
tags: [python]
---
## 1.  PythonWeb开发介绍
- 静态资源：HTML Javascript  CSS （ Bootstrap搞定）
- http server： nginx
- PythonWeb框架：
  - Django（大而全，CMS）
  - flask(自己造轮子，+n*插件）
  - Tornado（epoll， 异步，单线程）
  - web.py
  - bottle（单文件）
    

框架跟http交互方式两种方式：
- 端口（反向代理）
- 协议（PEP333 wsgi，fastcgi）
  

框架解决的问题：
- http 协议的封装（http request， http response）
- 重复的web数据流程
- 通用的数据库访问操作（关于数据库访问的ORM：Django自带ORM，SQLAlchemy，Peewee，等）

session & cookie
```
jsp?sessionid=xxsd12sdfsfds
asp?sessionid=112321
```
> http://www.the5fire.com/session-cookie.html


## 2. Django快速一览
``` bash
pip install Django
mkdir AutoOps
cd AutoOps
django-admin startproject autoops
```

我们先运行它
``` bash
python manage.py runserver
```

根据提示创建app
``` bash
python manage startapp asset
```

完成第一个页面：
``` python
# 先配置settings
INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'asset',
)
```
编写views.py, vim asset/views.py:
``` python
# coding:utf-8
from django.http import HttpResponse

def index(request):
    return HttpResponse('hello world')
```

配置urls.py vim autoops/urls.py:
``` python
from django.conf.urls import include, url
from django.contrib import admin

urlpatterns = [
    url(r'^$', 'asset.views.index'),
    url(r'^admin/', include(admin.site.urls)),
]
```
启动：python manage.py runserver 0.0.0.0:8000

so easy！

再来看下Model和Admin的使用：

`asset/models.py`
``` python
# coding:utf-8

from django.db import models

class Host(models.Model):
    STATUS_ITEMS = (
        (1, "空闲"),
        (2, "使用中"),
        (3, "报废"),
    )
    ip = models.GenericIPAddressField(verbose_name="主机IP")
    open_port = models.CharField(max_length=1000, verbose_name="开放端口")
    status = models.IntegerField(choices=STATUS_ITEMS, verbose_name="主机状态")

    created_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    update_time = models.DateTimeField(auto_now=True, verbose_name="更新时间")
     
    class Meta:
        verbose_name_plural = "主机"
```

`asset/admin.py`
``` python
# coding:utf-8
from django.contrib import admin

from .models import Host
# or from asset.models import Host

admin.site.register(Host)
```
启动：`python manage.py runserver`, 注意提示：
```
You have unapplied migrations; your app may not work properly until they are applied.
Run 'python manage.py migrate' to apply them.
```

运行: `python manage.py migrate`

访问:`http://localhost:8000/admin`

然后创建用户:
```
python manage.py createsuperuser

admin
admin
```

登录一下看看，一个完整的cms系统有了

## 3. Django介绍
为快速开发Web应用而生

### 3.1 Model驱动
Django中的重点是Model，围绕Model有很多成熟可用的功能

### 3.2 view
配置url dispatch
     
接受request，处理业务，返回response
     
两种方式：def  vs  class，初期使用def即可，middleware使用
     
### 3.3 模板
类似于字符串的模板，使用Django内置的语法
     
### 3.4 form
处理页面表单
     
### 3.5 admin
根据model直接生成对应界面

## 4. 数据流程

## 5. 详细介绍代码每一个模块

## 6. ORM大体思路
把对象映射成表
``` python
class Student(models.Model):
     name = char(20)
     age = int()

student = Student()
student.name = 'huyang'
student.age = 10
student.save() -> insert into Student(name, age) values('huyang', 10);

Student.objects.all() ->  select * from Student;
```
> 文档：https://docs.djangoproject.com/en/1.8/topics/db/models/

## 7. views和url
https://docs.djangoproject.com/en/1.8/#the-view-layer

## 8. templates
https://docs.djangoproject.com/en/1.8/ref/templates/language/

## 9. 作业
根据Django1.8的入门文档，以及本课件实现一个简单管理系统：内容包括：主机管理，机房管理，服务管理。