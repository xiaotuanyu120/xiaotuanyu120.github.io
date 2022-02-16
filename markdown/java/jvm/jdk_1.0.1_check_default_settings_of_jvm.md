---
title: JDK 状态 - 查看默认参数
date: 2016-08-08 09:58:00
categories: java/jvm
tags: [java,jvm]
---

### 查看java设定的堆内存大小参数
```
java -XX:+PrintFlagsFinal -version | grep HeapSize
    uintx ErgoHeapSizeLimit                         = 0               {product}        
    uintx HeapSizePerGCThread                       = 87241520        {product}        
    uintx InitialHeapSize                          := 16070592        {product}        
    uintx LargePageHeapSizeThreshold                = 134217728       {product}        
    uintx MaxHeapSize                              := 257949696       {product}        
java version "1.7.0_80"
Java(TM) SE Runtime Environment (build 1.7.0_80-b15)
Java HotSpot(TM) 64-Bit Server VM (build 24.80-b11, mixed mode)
```
> InitialHeapSize：初始化堆大小
> MaxHeapSize：堆的最大内存大小
 
### 查看java设定的栈内存大小参数
```
java -XX:+PrintFlagsFinal -version | grep ThreadStackSize
     intx CompilerThreadStackSize                   = 0               {pd product}     
     intx ThreadStackSize                           = 1024            {pd product}     
     intx VMThreadStackSize                         = 1024            {pd product}     
java version "1.7.0_80"
Java(TM) SE Runtime Environment (build 1.7.0_80-b15)
Java HotSpot(TM) 64-Bit Server VM (build 24.80-b11, mixed mode)
```