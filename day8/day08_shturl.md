\# Day8 学习日志：MySQL 8.0 安装与 SQL 实战



\## 一、今日完成



\-  安装 MySQL 8.0 和 DBeaver 可视化工具

\-  创建数据库 `ai\_dataset\_db`，设置字符集 utf8mb4

\-  设计三张贴合 AI 标注业务的数据表：`user`、`project`、`dataset`

\-  建立外键关联：`project.manager\_id` → `user.id`，`dataset.project\_id` → `project.id`

\-  执行完整 DDL（建库建表）、DML（增删改查）、聚合统计（GROUP BY）、多表联查（JOIN）

\-  将所有 SQL 语句保存到 `sql\_demo.sql`

\-  理解 SQL 逻辑执行顺序与 WHERE/HAVING 的区别



\## 二、核心概念



\### 1. 数据库与表

\-  \*\*数据库\*\*：仓库，包含多张表

\-  \*\*表\*\*：货架，每张表存一类数据，由行（记录）和列（字段）组成



\### 2. SQL 语句分类



| 分类 | 作用 | 关键词 |

|------|------|--------|

| DDL（数据定义语言） | 定义数据库结构 | CREATE, ALTER, DROP |

| DML（数据操作语言） | 操作数据 | INSERT, SELECT, UPDATE, DELETE |

| 聚合查询 | 统计分析 | COUNT, SUM, AVG, GROUP BY |

| 联表查询 | 跨表关联 | JOIN, LEFT JOIN |



\### 3. 关键字段约束



| 约束 | 含义 | 示例 |

|------|------|------|

| PRIMARY KEY | 主键，唯一且非空 | id INT AUTO\_INCREMENT PRIMARY KEY |

| AUTO\_INCREMENT | 自增，数据库自动分配 ID | 同上 |

| NOT NULL | 字段不允许为空 | username VARCHAR(50) NOT NULL |

| UNIQUE | 字段值全表唯一 | username VARCHAR(50) UNIQUE |

| DEFAULT | 插入时不指定则使用默认值 | role DEFAULT 'annotator' |

| ENUM | 限制字段只能取预设值 | ENUM('annotator', 'admin') |



\### 4. 外键与级联策略

\-  `FOREIGN KEY (本表字段) REFERENCES 外表(外表字段)`：确保引用完整性

\-  `ON DELETE RESTRICT`：被引用时禁止删除父行

\-  `ON DELETE CASCADE`：父行删除时自动删除所有子行



\### 5. 字符集 utf8mb4

\-  MySQL 中真正完整的 UTF-8 编码

\-  支持所有 Unicode 字符（包括 emoji）

\-  区别于早期阉割版 `utf8`（只支持 3 字节）



\### 6. SQL 逻辑执行顺序



```

FROM → JOIN → WHERE → GROUP BY → HAVING → SELECT → ORDER BY → LIMIT

```



\-  \*\*书写顺序\*\*：SELECT → FROM → WHERE → GROUP BY → HAVING → ORDER BY → LIMIT

\-  \*\*执行顺序和书写顺序不同\*\*，这是理解 SQL 的关键



\### 7. WHERE vs HAVING



| 特性 | WHERE | HAVING |

|------|-------|--------|

| 执行时机 | 分组\*\*之前\*\* | 分组\*\*之后\*\* |

| 筛选对象 | 原始行 | 分组聚合结果 |

| 能否用聚合函数 | ❌ 不能 | ✅ 可以 |

| 能否用列别名 | ❌ 不能 | ✅ 可以（MySQL） |

| 口诀 | \*\*WHERE 管行\*\* | \*\*HAVING 管组\*\* |



\### 8. JOIN 连接类型

\-  `JOIN`（内连接）：只返回两表都有匹配的行

\-  `LEFT JOIN`（左连接）：保留左表所有行，右表无匹配则填充 NULL

\-  `ON`：指定连接条件



\## 三、踩坑记录



1\.  \*\*表名与保留字冲突\*\*：`user` 是 MySQL 保留字，必须用反引号包裹（`` `user` ``），否则语法报错。

2\.  \*\*外键约束导致删除失败\*\*：尝试删除被项目引用的用户时，因 `ON DELETE RESTRICT` 被拦截，这正是数据完整性保护的体现。

3\.  \*\*字符集设置遗漏\*\*：如果建库时忘记指定 utf8mb4，后续插入中文可能乱码。建库时统一设置是最佳实践。

4\.  \*\*UPDATE/DELETE 忘记加 WHERE\*\*：不加条件的 UPDATE/DELETE 会修改/删除整张表的所有数据，这是灾难性的操作。

5\.  \*\*WHERE 中误用聚合函数\*\*：`WHERE SUM(total\_samples) > 10000` 会报错，因为聚合发生在分组之后，WHERE 执行时聚合结果还不存在。



\## 四、三张表关联逻辑总结



```

user (标注员)

&#x20; │

&#x20; │ 1:N

&#x20; ▼

project (标注项目) ──────────┐

&#x20; │                          │ 外键: manager\_id → user.id

&#x20; │ 1:N                      │ 策略: ON DELETE RESTRICT

&#x20; ▼                          │ （负责人被引用时不可删除）

dataset (数据集) ────────────┘

&#x20; │

&#x20; │ 外键: project\_id → project.id

&#x20; │ 策略: ON DELETE CASCADE

&#x20; │ （项目删除时自动删除其数据集）

```



\## 五、今日收获



1\.  掌握了从建库到联表查询的完整 SQL 流程

2\.  理解了外键约束与级联策略对数据完整性的保障

3\.  能用聚合函数 + GROUP BY 完成项目标注完成率等统计分析

4\.  搞懂了 SQL 执行顺序，能解释 WHERE 中为何不能用聚合函数和别名

5\.  数据库是后端开发的核心基础设施，所有业务数据最终都落库

6\.  贴合 AI 标注业务设计表结构，让学习与工作实际紧密关联

```

