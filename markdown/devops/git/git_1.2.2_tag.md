---
title: git: 1.2.2 git tag
date: 2019-04-26 10:21:00
categories: devops/git
tags: [git]
---

### 1. 列出tag
``` bash
# list tags
git tag
tag1
tag2
...

# list tags filter by keywords
git tag -l "v1.8.5*"
v1.8.5
v1.8.5-rc0
v1.8.5-rc1
v1.8.5-rc2
v1.8.5-rc3
v1.8.5.1
v1.8.5.2
v1.8.5.3
v1.8.5.4
v1.8.5.5
```

### 2. 创建tag
tag分以下两种：
- lightweight(轻量级)，类似于一个无法修改的分支，只是指向一个commit
- annotated(注释性)，是一个git数据对象的完整对象，会包含tag创建者名称、email、日期、tag message、可以被GPG验证。

``` bash
# create annotated tag
git tag -a v1.4 -m "my version 1.4"

# create lightweight tag
git tag v1.4-lw
```
> 可以使用git show tag-name 查看tag信息，会发现这两种tag类型的区别

**指定commit来创建tag**
``` bash
git log --pretty=oneline
15027957951b64cf874c3557a0f3547bd83b3ff6 Merge branch 'experiment'
a6b4c97498bd301d84096da251c98a07c7723e65 beginning write support
0d52aaab4479697da7686c15f77a3d64d9165190 one more thing
6d52a271eda8725415634dd79daabbc4d9b6008e Merge branch 'experiment'
0b7434d86859cc7b8c3d5e1dddfed66ff742fcbc added a commit function
4682c3261057305bdd616e23b64b0857d832627b added a todo file
166ae0c4d3f420721acbb115cc33848dfcc2121a started write support
9fceb02d0ae598e95dc970b74767f19372d61af8 updated rakefile
964f16d36dfccde844893cac5b347e7b3d44abbc commit the todo
8a5cbc430f1a9c3d00faaeffd07798508422908a updated readme
```
假设你已经commit了很多，然后发现忘记给`updated rakefile`这个commit创建tag

``` bash
git tag -a v1.2 9fceb02
```

### 3. 分享tag
本地的tag，如果想分享给其他人，或者push到公共库
``` bash
# 语法：git push origin <tagname>

# 给origin分享v1.2
git push origin v1.2

# 给upstream分享所有的本地tag
git push upstream --tags
```

### 4. 删除tag
``` bash
# 删除本地tag
git tag -d v1.4-lw

# 删除公共库tag
git push origin --delete v1.4-lw
```

### 5. 切换到tag
``` bash
git checkout v1.2
```
此时你可以浏览该tag的代码目录，然后作出修改，创建新的commit，如果你希望丢弃他们，可以直接checkout离开。但是如果你希望保留你做的commit修改，你可以执行以下代码，创建一个新的分支来保留他们
``` bash
git checkout -b <new-branchname>
```