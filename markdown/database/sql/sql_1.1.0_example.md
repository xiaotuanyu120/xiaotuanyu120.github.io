---
title: sql: 1.1.0 example
date: 2020-07-22 22:19:00
categories: database/sql
tags: [sql]
---

### 1. 按照类型分类，对不同分类使用不同的条件筛选
``` sql
CREATE TABLE test (
    PRIMARY KEY (id),
    id    INT          NOT NULL AUTO_INCREMENT,
    type  VARCHAR(100) NOT NULL,
    score INT          NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

INSERT INTO test (type, score)
VALUES ('a', 90),
       ('b', 30),
       ('a', 60),
       ('b', 70),
       ('a', 75),
       ('b', 88);

SELECT id
  FROM test
 WHERE (type = 'a' AND score <= 80)
    OR (type = 'b' AND score <= 75);
```

### 2. 查看表信息
``` sql
-- 查看表容量
SELECT CONCAT(ROUND(SUM(DATA_LENGTH/1024/1024),2), 'MB') AS data
  FROM information_schema.TABLES
 WHERE table_schema='your_database_name'
   AND table_name='your_table_name';
```

### 3. 创建表
``` sql
-- 复制表的字段属性、数据来创建新表
CREATE TABLE IF NOT EXIST your_table_name_new [AS] SELECT * FROM your_table_name_old;

-- 复制表的备注、索引、主键外键、存储引擎等
CREATE TABLE IF NOT EXIST your_table_name_new (like your_table_name_old)
```

### 4. 表重命名
``` sql
ALTER TABLE your_table_name RENAME TO your_table_name_new;
```

### 5. 索引
``` sql
-- 查看索引
SHOW INDEX FROM your_table_name;
CREATE INDEX index_name on your_table_name (column1,column2);
```