---
title: git: 1.9.0 使用rebase合并多个commit
date: 2020-03-04 09:07:00
categories: devops/git
tags: [devops,git,rebase]
---

### 0. 需求背景
有时候会开bug或者特性分支来解决一个bug或者完成一个新的特性，我们可能需要数个commit才能完成这项工作，在合并到master或production分支时，我们更希望自己的commit合并为一次。此时可以采用如下操作

### 1. rebase合并多个commit
``` bash
# step 1 查看需要合并的commit
git log
# 查看列出的所有commit，找到自己希望合并的所有commit之前的一个commit号

# step 2 合并commit
git rebase -i commit_NO.
# 这个commit号并不参与合并，它之后的所有分支参与合并

# step 3 选择合并信息
# 执行完rebase命令后，会在交互界面出现以下内容
# *****************************************************************************
# pick b71f0c6 Some commit message

# pick 5431438 Other commit message

# # Rebase a46a543..23c6558 onto a46a543 (1 command)
# #
# # Commands:
# # p, pick <commit> = use commit
# # r, reword <commit> = use commit, but edit the commit message
# # e, edit <commit> = use commit, but stop for amending
# # s, squash <commit> = use commit, but meld into previous commit
# # f, fixup <commit> = like "squash", but discard this commit's log message
# # x, exec <command> = run command (the rest of the line) using shell
# # b, break = stop here (continue rebase later with 'git rebase --continue')
# # d, drop <commit> = remove commit
# # l, label <label> = label current HEAD with a name
# # t, reset <label> = reset HEAD to a label
# # m, merge [-C <commit> | -c <commit>] <label> [# <oneline>]
# # .       create a merge commit using the original merge commit's
# # .       message (or the oneline, if no original merge commit was
# # .       specified). Use -c <commit> to reword the commit message.
# #
# # These lines can be re-ordered; they are executed from top to bottom.
# #
# *****************************************************************************
# 此时可以按照提示，pick一个commit，然后其他的commit将pick修改为squash
# 然后保存退出

# step 3.a 如果没有冲突，界面会出现合并后的commit信息，wq保存退出即可
# 此时可以使用git log查看合并后的commit

# step 3.b 如果有冲突
# step 3.b.i 如果希望rebase继续，需要手动修改冲突，然后执行下面命令
git add .
git rebase --continue

# step 3.b.ii 如果希望取消此次rebase
git rebase --abort 
```