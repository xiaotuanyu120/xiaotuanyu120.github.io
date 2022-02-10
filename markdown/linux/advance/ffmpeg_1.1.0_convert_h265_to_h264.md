---
title: ffmpeg: 1.1.0 转换h265为h264
date: 2020-11-09 16:58:00
categories: linux/advance
tags: [linux,ffmpeg]
---

### 0. 背景
h264的视频，使用nginx提供托管后，无法浏览器正常播放

### 1. 转换
``` bash
ffmpeg -i path/to/h265-source.mp4 -c copy -c:v libx264 -crf 23 -preset medium path/to/h264-destination.mp4
```
> - `-c:v libx264`，video指定转化为h264
> - `-crf 23 -preset medium`，和视频质量相关，可选

### 2. 转换rmvb为mp4
```
ffmpeg -i path/to/source.rmvb -c:a aac -c:v libx264 -crf 23 -preset medium path/to/destination.mp4
```
> - `-c:a acc`，audio指定转换为acc
> - `-c:v libx264`，video指定转化为h264
> - `-crf 23 -preset medium`，和视频质量相关，可选