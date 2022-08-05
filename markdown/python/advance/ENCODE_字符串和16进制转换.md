---
title: ENCODE: 字符串和16进制转换
date: 2016-03-01 17:33:00
categories: python/advance
tags: [python,encode]
---

``` python
In [7]: str = "我--日* "

In [8]: print str.encode('hex')
e68891e28094e28094e697a52a20

In [9]: print str.encode('hex').decode('hex')
我--日*
```
