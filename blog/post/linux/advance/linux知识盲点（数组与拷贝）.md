---
title: linux知识盲点（数组与拷贝）
date: 2014年12月17日
categories: 下午 5:31
---
 
cp -r /good/. /bad/ 批量将good文件夹下的所有文件拷贝到bad文件夹下，而如果没有"."，则是将good文件夹整个移动到bad文件夹下
=========================================================================================
array=（$（字符串产生相关命令）），执行命令后把结果赋值给一个数组
数组网络上详细介绍
linux shell在编程方面比windows 批处理强大太多，无论是在循环、运算。已经数据类型方面都是不能比较的。 下面是个人在使用时候，对它在数组方面一些操作进行的总结。
 
1.数组定义
 
[chengmo@centos5 ~]$ a=(1 2 3 4 5)
[chengmo@centos5 ~]$ echo $a
1
 
一对括号表示是数组，数组元素用"空格"符号分割开。
 
2.数组读取与赋值
* 得到长度：
[chengmo@centos5 ~]$ echo ${#a[@]}
5
用${#数组名[@或*]} 可以得到数组长度
* 读取：
[chengmo@centos5 ~]$ echo ${a[2]} 
3
[chengmo@centos5 ~]$ echo ${a[*]} 
1 2 3 4 5   
用${数组名[下标]} 下标是从0开始  下标是：*或者@ 得到整个数组内容
* 赋值:
[chengmo@centos5 ~]$ a[1]=100
[chengmo@centos5 ~]$ echo ${a[*]} 
1 100 3 4 5
 
[chengmo@centos5 ~]$ a[5]=100     
[chengmo@centos5 ~]$ echo ${a[*]}
1 100 3 4 5 100
直接通过 数组名[下标] 就可以对其进行引用赋值，如果下标不存在，自动添加新一个数组元素
* 删除:
[chengmo@centos5 ~]$ a=(1 2 3 4 5)
[chengmo@centos5 ~]$ unset a
[chengmo@centos5 ~]$ echo ${a[*]}
[chengmo@centos5 ~]$ a=(1 2 3 4 5)
[chengmo@centos5 ~]$ unset a[1]   
[chengmo@centos5 ~]$ echo ${a[*]} 
1 3 4 5
[chengmo@centos5 ~]$ echo ${#a[*]}
4
直接通过：unset 数组[下标] 可以清除相应的元素，不带下标，清除整个数据。
 
 
3.特殊使用
* 分片:
[chengmo@centos5 ~]$ a=(1 2 3 4 5)
[chengmo@centos5 ~]$ echo ${a[@]:0:3}
1 2 3
[chengmo@centos5 ~]$ echo ${a[@]:1:4}
2 3 4 5
[chengmo@centos5 ~]$ c=(${a[@]:1:4})
[chengmo@centos5 ~]$ echo ${#c[@]}
4
[chengmo@centos5 ~]$ echo ${c[*]} 
2 3 4 5
直接通过 ${数组名[@或*]:起始位置:长度} 切片原先数组，返回是字符串，中间用"空格"分开，因此如果加上"()"，将得到切片数组，上面例子：c 就是一个新数据。
* 替换:
[chengmo@centos5 ~]$ a=(1 2 3 4 5)    
[chengmo@centos5 ~]$ echo ${a[@]/3/100}
1 2 100 4 5
[chengmo@centos5 ~]$ echo ${a[@]}
1 2 3 4 5
[chengmo@centos5 ~]$ a=(${a[@]/3/100}) 
[chengmo@centos5 ~]$ echo ${a[@]}     
1 2 100 4 5
调用方法是：${数组名[@或*]/查找字符/替换字符} 该操作不会改变原先数组内容，如果需要修改，可以看上面例子，重新定义数据。
 
从上面讲到的，大家可以发现linux shell 的数组已经很强大了，常见的操作已经绰绰有余了。
为数组赋值
a=(`echo {1..100}`)
b=(`echo {100..1}`)
[root@web01 ~]# a=(`echo  {1..50}`)
[root@web01 ~]# echo ${a[@]}
1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29 30 31 32 33 34 35 36 37 38 39 40 41 42 43 44 45 46 47 48 49 50
 
=============================================================================================
 
