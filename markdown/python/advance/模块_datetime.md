---
title: 模块: datetime
date: 2016-03-21 16:17:00
categories: python/advance
tags: [python]
---
### 模块导入
``` python
import datetime
```

### 获取当前时间
``` python
datetime.datetime.now()
datetime.datetime(2016, 3, 21, 4, 21, 45, 248352)
```

### 获取当前日期
``` python
datetime.date.today()
datetime.date(2016, 3, 21)
```

### 时间转换成字符串
``` python
datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
# '2016-03-21 04:26:48'
```

### 转换回来
``` python
datetime.datetime.strptime("2016-03-21 04:26:48", "%Y-%m-%d %H:%M:%S")
datetime.datetime(2016, 3, 21, 4, 26, 48)
```
