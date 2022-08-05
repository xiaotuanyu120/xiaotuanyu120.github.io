---
title: PEP8: flake8
date: 2016-01-29 10:13:00
categories: python/advance
tags: [python]
---

### 工具简介
flake8是对下面相关工具的包装
- PyFlakes
- pep8
- Ned Batchelder's McCabe script

### 安装方法
`pip install flake8`

### 使用方法
``` bash
flake8 website_speed_test.py
website_speed_test.py:6:1: F401 'sys' imported but unused
website_speed_test.py:10:1: E302 expected 2 blank lines, found 1
website_speed_test.py:17:1: E302 expected 2 blank lines, found 1
```
