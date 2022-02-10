---
title: mysql 4.0.1：auto_increment引起的问题
date: 2021-11-19 00:04:00
categories: database/mysql
tags: [database,mysql,auto_increment]
---

### 0. 背景
数据库中的一个字段，业务开发计划将其改为自增，由DBA执行后，发现原本字段中为NULL的记录，全都按照自增规则给重新赋了值。这不符合初衷啊，是为什么呢？

### 1. 重现场景
#### 1) 准备环境
``` bash
docker run -it -d --name mysql -e MYSQL_EMPTY_PASSWORD=true mysql:5.7
```

#### 2) 模拟线上场景
**创建测试表test2**
``` sql
CREATE TABLE test2 (
    id    INT NOT NULL,
    score INT NULL,
    PRIMARY KEY (id),
    INDEX (score)
);
```

> score字段，允许为NULL，用来测试；之所以给score增加索引，是因为这是增加AUTO_INCREMENT的前提。

**准备测试数据**
``` sql
INSERT INTO test2 VALUES
    (1, NULL),
    (2, 200),
    (3, NULL),
    (4, 0),
    (5, -2);
```

> 测试数据涵盖范围：
> - 正数
> - NULL
> - 0
> - 负数

**查看当前的现存记录**
``` sql
SELECT *
  FROM test2 ORDER BY id;
```

> 输出：
> ```
> +----+-------+
> | id | score |
> +----+-------+
> |  1 |  NULL |
> |  2 |   200 |
> |  3 |  NULL |
> |  4 |     0 |
> |  5 |    -2 |
> +----+-------+
> 5 rows in set (0.01 sec)
> ```

**在有现存数据的基础上，设定score字段自增**
``` sql
 ALTER TABLE test2 
MODIFY COLUMN score INT AUTO_INCREMENT;
```

**查看修改为自增之后的结果**
``` sql
SELECT *
  FROM test2 ORDER BY id;
```

输出：
```
+----+-------+
| id | score |
+----+-------+
|  1 |     1 |
|  2 |   200 |
|  3 |   201 |
|  4 |   202 |
|  5 |    -2 |
+----+-------+
5 rows in set (0.01 sec)
```

#### 3) 总结
- 给字段设定为自增后，现存记录中的`NULL`和`0`值都会按照自增规则被重新赋值
- 自增赋值时，会按照之前记录的最大值加1
- 负数和正数不会被重新赋值，会保持原记录

### 2. 文档解读
- 参考文档：[mysql 5.7 docs: InnoDB引擎下的AUTO_INCREMENT](https://dev.mysql.com/doc/refman/5.7/en/innodb-auto-increment-handling.html)

#### 1) 下面这个文档原文，证实了前面实践出的结论，给字段设定为自增后，现存记录中的`NULL`和`0`值都会按照自增规则被重新赋值
```
Specifying NULL or 0 for the AUTO_INCREMENT column

In all lock modes (0, 1, and 2), if a user specifies NULL or 0 for the AUTO_INCREMENT column in an INSERT, InnoDB treats the row as if the value was not specified and generates a new value for it.
```

#### 2) innodb_autoinc_lock_mode
文档中着重介绍了变量`innodb_autoinc_lock_mode`，这个变量表示了处理AUTO_INCREMENT时的锁的模式，有可能会影响主备情况下并发事务的自增逻辑，牵扯到表锁和行锁，详细信息还是看上面的参考文档链接。
``` sql
SHOW VARIABLES LIKE "innodb_autoinc_lock_mode";
```

输出：
```
+--------------------------+-------+
| Variable_name            | Value |
+--------------------------+-------+
| innodb_autoinc_lock_mode | 1     |
+--------------------------+-------+
1 row in set (0.04 sec)
```

#### 3) 其他变量
- auto_increment_increment，代表自增的数值，默认为1
- auto_increment_offset，代表目前自增数字的偏移量，默认为1，取值范围时1-65535

### 3. 总结
表创建好之后，增加自增逻辑，一定要慎重。如果是业务方面的需求，最好是用代码来解决自增问题，而不是依赖数据库的能力。