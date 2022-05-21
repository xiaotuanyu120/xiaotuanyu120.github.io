---
title: word2markdown
date: 2016-06-30 21:31:00
categories: linux/desktop
tags: [word,markdown]
---

## convert work 2 markdown
``` bash
yum install epel-release -y
yum install unoconv pandoc -y
yum install libreoffice-core libreoffice-headless libreoffice-sdk libreoffice-writer2latex breoffice-writer2xhtml libreoffice-pyuno -y
unoconv --listener &
unoconv -f html -o 2.2-yum-repo-conf.html 2.2-yum-repo-conf.docx
pandoc -f html -t markdown -o 2.2-yum-repo-conf.md 2.2-yum-repo-conf.html
```

## 问题
### 错误信息
``` bash
unoconv -f html -o 2.2-yum-repo-conf.html 2.2-yum-repo-conf.docx
/usr/lib64/libreoffice/program/soffice.bin X11 error: Can\'t open display:
   Set DISPLAY environment variable, use -display option
   or check permissions of your X-Server
   (See "man X" resp. "man xhost" for details)
Error: Unable to connect or start own listener. Aborting.
```

### 解决方案：
``` bash
# 杀掉目前的office和unoconv的进程，然后执行下面两条命令
yum install libreoffice-core libreoffice-headless libreoffice-sdk libreoffice-writer2latex libreoffice-writer2xhtml libreoffice-pyuno -y
unoconv --listener &
```