---
title: sql: 1.1.0 example
date: 2020-07-22 22:19:00
categories: database/sql
tags: [sql]
---
### sql: 1.1.0 example

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