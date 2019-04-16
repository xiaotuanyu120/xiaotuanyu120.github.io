## branch of \*\*markdown_build_static_html\*\*
#### 和原版的区别：
原版是使用flask做的web服务器，此版本为了使用gitpages，特地改成了完全html静态文件的版本。此版本去掉了flask相关文件和功能，仅保留了markdown文件转换成静态文件的功能

### 使用说明
#### step 1. 安装程序
在linux环境中按照如下操作
``` bash
git clone https://github.com/xiaotuanyu120/xiaotuanyu120.github.io.git
cd xiaotuanyu120.github.io
pip install lib/requirement.txt
```

#### step 2. 修改配置
修改conf目录中的blog.ini
```
[blog]
base_dir=/vagrant/newsite/blog
md_dir=/vagrant/newsite/blog/post
html_dir=/vagrant/newsite/blog/html
template_dir=/vagrant/newsite/blog/template
topics_file=/vagrant/newsite/blog/topics.py
topics_json=/vagrant/newsite/blog/topics.json
index_json_file=/vagrant/newsite/blog/index.json
extend_file=base/sub_categories_base.html
```

配置说明（此处没有说明的配置，在此版本中无用）：
- md_dir, 存放markdown文件的根目录
- html_dir, 生成的html存放的目录
- template_dir, 相关模板的路径，请配置成下载的此git目录中的/path/to/xiaotuanyu120.github.io/blog/template


#### step 3. 编写markdown文件
编写的markdown文件需要满足一定规则，每篇文章的最开头必须包含以下内容，不然不会转换改文件
```
---
title: 1.0.0 silent模式安装oracle 11G R2 之 环境准备
date: 2016-12-20 11:53:00
categories: database/oracle
tags: [database,oracle]
---
```

- 必须包含title,date,catagories,tags这四项header
- catagories必须是`分类1/分类2`这种结构，使用`/`间隔分类1和分类2
- tags必须是一个list格式, `[keyword1, keyword2, ...]`
- 文章开头必须是`---`
- 文件保存在`md_dir`中，目录结构是`md_dir/分类1/分类2`


#### step 4. 转换markdown文件去html
```
python /path/to/xiaotuanyu120.github.io/blog/generate.py
```