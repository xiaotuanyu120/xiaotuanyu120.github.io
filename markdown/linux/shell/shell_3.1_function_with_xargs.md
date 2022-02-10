---
title: SHELL: 3.1 function with xargs
date: 2020-09-01 14:16:00
categories: linux/shell
tags: [shell,variable]
---

### 0. xargs后执行function
``` bash
#!/bin/bash

function echo_wrap {
    echo $1
}

ls /tmp | xargs -i echo_wrap {}
```
执行结果
``` bash
xargs: echo_wrap: No such file or directory
```

原来xargs之后识别不到function

那么我们来这样处理一下

``` bash
#!/bin/bash

function echo_wrap {
    echo $1
}

export -f echo_wrap

ls /tmp | xargs -i bash -c "echo_wrap {}"
```

再来执行，就没有问题了